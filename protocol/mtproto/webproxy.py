# webproxy.py
# ══════════════════════════════════════════════════════════════════════════════
# «Telegram Web Proxy» (tg://webproxy) — نوع جدید پروکسی تلگرام که به TCP Proxy
# و پورت اختصاصی نیاز نداره: کلاینت تلگرام ترافیک MTProto رو داخل درخواست‌های
# HTTPS معمولی روی همون دامنه‌ی پنل (پورت ۴۴۳) می‌فرسته.
#
# معماری:
#   - telemt اجازه نمی‌ده دو vhost یک host داشته باشن؛ برای همین هر کانفیگ یک
#     پروسه‌ی سبک telemt مستقل داره (listener از نوع transport="web" روی
#     127.0.0.1 با پورت تصادفی)، با یک vhost، یک base_path (= توکن کانفیگ) و یک
#     کاربر. (همون الگوی «یک پروسه به‌ازای هر لینک» که برای MTProto هم داریم.)
#   - خودِ پنل (FastAPI) درخواست‌های /<token>/... رو به پورت همون پروسه فوروارد
#     می‌کنه (TLS رو پلتفرم مثل Railway/Render/Fly انجام میده). چون ترافیک هر
#     کانفیگ از مسیر جدا عبور می‌کنه، حجم/انقضا/غیرفعال‌سازی/سقف IP دقیقاً داخل
#     پنل اعمال میشه.
#   - تبلیغ (ad_tag) از طریق use_middle_proxy + [access.user_ad_tags] تنظیم میشه.
#   - لاگ اتصال ذخیره یا چاپ نمی‌شه (فقط خروجی ۱۰ ثانیه‌ی اول اجرا برای تشخیص
#     خطای راه‌اندازی نگه داشته میشه).
# ══════════════════════════════════════════════════════════════════════════════

import asyncio
import base64
import hashlib
import ipaddress
import os
import re
import socket
import secrets
import time
from typing import Callable, Dict, List, Optional
from urllib.parse import quote

import httpx
from fastapi import Request
from fastapi.responses import Response, StreamingResponse

from protocol.mtproto import telemt

WEB_DIR = telemt.TELEMT_DIR
DECOY_DIR = WEB_DIR / "web-decoy"

# token -> {"proc", "port", "sig", "boot"}
_procs: Dict[str, dict] = {}
_lock = asyncio.Lock()
_http: Optional[httpx.AsyncClient] = None
_last_error: Optional[str] = None
# سطح سرعت کانفیگ؛ اگر telemt نسخه‌ی سرور یک سطح را نپذیرد، یک سطح پایین‌تر امتحان می‌شود:
#   2 = WebSocket-lanes + WebSocket + https-lanes + https (سریع‌ترین)
#   1 = WebSocket + https
#   0 = فقط https (قدیمی/ساده)
_level = 2


# ── کمکی‌ها ──────────────────────────────────────────────────────────────────
def new_token() -> str:
    return secrets.token_hex(6)


def base_path(token: str) -> str:
    # یک بخش ساده (۱۲ کاراکتر هگز) — دقیقاً مثل لینک‌های کارکن
    return token


def generate_secret() -> str:
    return secrets.token_hex(16)


def build_links(host: str, token: str, raw_secret: str) -> dict:
    """لینک اشتراک: server = «دامنه/مسیر» (percent-encoded) و secret = base64url
    ِ (0x70 || 0xdd || سکرت ۱۶ بایتی). بایت 0x70 نشانه‌ی «لینک دارای مسیر» است و
    0xdd همان حالت secret_mode="dd"؛ با دیکد کردن یک لینک کارکن تأیید شد."""
    try:
        sec = base64.urlsafe_b64encode(bytes([0x70, 0xDD]) + bytes.fromhex(raw_secret)).decode().rstrip("=")
    except Exception:
        sec = ""
    qs = f"server={quote(f'{host}/{base_path(token)}', safe='')}&secret={sec}"
    return {"tme": f"https://t.me/webproxy?{qs}", "tg": f"tg://webproxy?{qs}"}


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def valid_host(h: str) -> bool:
    """telemt فقط FQDN غیر-IP (با حداقل یک نقطه) و بدون پورت می‌پذیرد."""
    h = (h or "").strip().lower()
    if not h or "." not in h or ":" in h or h.endswith(".") or h == "localhost":
        return False
    try:
        ipaddress.ip_address(h)
        return False
    except ValueError:
        return True


async def _resolve_ip(host: str) -> str:
    try:
        loop = asyncio.get_running_loop()
        infos = await loop.getaddrinfo(host, 443, family=socket.AF_INET, type=socket.SOCK_STREAM)
        if infos:
            return infos[0][4][0]
    except Exception:
        pass
    return "127.0.0.1"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _write_decoy():
    DECOY_DIR.mkdir(parents=True, exist_ok=True)
    idx = DECOY_DIR / "index.html"
    if not idx.exists():
        idx.write_text("<!doctype html><html><head><meta charset=\"utf-8\"><title>OK</title></head>"
                       "<body>OK</body></html>", encoding="utf-8")


def _build_config(token: str, secret: str, ad_tag: Optional[str], hosts: List[str],
                  public_ip: str, port: int, level: int) -> str:
    user = "u" + token
    L = [
        "[general]",
        f"use_middle_proxy = {'true' if ad_tag else 'false'}",
        'log_level = "silent"',
        "",
        "[general.modes]",
        "classic = false",
        "secure = false",
        "tls = true",
        "",
        "[censorship]",
        f'tls_domain = "{_esc(telemt.DEFAULT_TLS_DOMAIN)}"',
        "mask = true",
        "",
        # API مدیریتی telemt به‌صورت پیش‌فرض روی 0.0.0.0:9091 فعاله؛ با چند پروسه‌ی
        # هم‌زمان پورت تکراری میشه (پروسه‌ی دوم بالا نمیاد) و ضمناً بی‌دلیل در معرضه.
        "[server.api]",
        "enabled = false",
        "",
        "[[server.listeners]]",
        'ip = "127.0.0.1"',
        f"port = {port}",
        'transport = "web"',
        "proxy_protocol = false",
        "reuse_allow = false",
        'web_client_ip_source = "x_forwarded_for"',
        'web_trusted_proxy_cidrs = ["127.0.0.1/32"]',
        "",
        "[web]",
        "enabled = true",
        'carrier = "https"',   # carrier نهایی/fallback (مثلاً iOS فقط https دارد)
    ]
    if level >= 1:
        # WebSocket یک اتصال پایدار است و بسیار سریع‌تر از https (که هر تکه‌ی داده یک
        # POST جدا می‌خواهد). سطح ۲ حامل‌های -lanes را هم اضافه می‌کند: هر استریم مسیر
        # مستقل دارد و دانلود سنگین جلوی پیام‌های کوچک را نمی‌گیرد.
        carriers = ('"websocket-lanes", "websocket", "https-lanes", "https"' if level >= 2
                    else '"websocket", "https"')
        L += [
            f"carriers = [{carriers}]",
            'carrier_negotiation_aggressiveness = "aggressive"',
            "",
            "[web.retry_jitter]",
            "enabled = false",
        ]
    hosts_toml = ", ".join(f'"{_esc(h)}"' for h in hosts)
    L += [
        "",
        "[[web.vhosts]]",
        f"hosts = [{hosts_toml}]",
        f'base_path = "{_esc(base_path(token))}"',
        f'public_addr = "{public_ip}:443"',
        "",
        "[web.vhosts.decoy]",
        'mode = "static_directory"',
        f'directory = "{_esc(str(DECOY_DIR))}"',
        'index = "index.html"',
        "",
        "[[web.vhosts.profiles]]",
        f'user = "{user}"',
        'secret_mode = "dd"',
        "max_sessions = 8",
        "max_streams = 512",
        "max_streams_per_session = 64",
        "",
        "[access.users]",
        f'"{user}" = "{secret}"',
    ]
    if ad_tag:
        L += ["", "[access.user_ad_tags]", f'"{user}" = "{ad_tag}"']
    return "\n".join(L) + "\n"


# ── مدیریت پروسه‌ها ──────────────────────────────────────────────────────────
def is_running(token: Optional[str] = None) -> bool:
    if token is not None:
        e = _procs.get(token)
        return bool(e and e["proc"].returncode is None)
    return any(e["proc"].returncode is None for e in _procs.values())


async def _drain(entry: dict):
    """خروجی پروسه خوانده می‌شود تا pipe پر نشود. فقط ۱۰ ثانیه‌ی اول (برای تشخیص
    خطای راه‌اندازی) نگه داشته می‌شود؛ بعد از آن هیچ لاگی ذخیره یا چاپ نمی‌شود."""
    proc = entry["proc"]
    t0 = time.monotonic()
    try:
        assert proc.stdout is not None
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            if time.monotonic() - t0 < 10 and len(entry["boot"]) < 40:
                txt = line.decode("utf-8", errors="ignore").rstrip()
                txt = re.sub(chr(27) + r"\[[0-9;]*m", "", txt)
                if txt:
                    entry["boot"].append(txt)
    except Exception:
        pass


async def _kill(entry: dict):
    proc = entry["proc"]
    if proc.returncode is not None:
        return
    try:
        proc.terminate()
        await asyncio.wait_for(proc.wait(), timeout=5.0)
    except (asyncio.TimeoutError, ProcessLookupError):
        try:
            proc.kill()
            await proc.wait()
        except ProcessLookupError:
            pass


async def _start_one(token: str, secret: str, ad_tag: Optional[str], hosts: List[str],
                     public_ip: str, level: int) -> dict:
    if not await telemt.ensure_binary():
        raise RuntimeError("باینری telemt در دسترس نیست")
    port = _free_port()
    # هر پروسه پوشه‌ی کاری مستقل دارد؛ فایل‌های حالت/کش telemt (proxy-secret, cache/,
    # telemt.limit.json, ...) نسبی‌اند و با پوشه‌ی مشترک بین پروسه‌ها قاطی می‌شدند.
    run_dir = (WEB_DIR / "run" / token).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = run_dir / "config.toml"
    cfg_path.write_text(_build_config(token, secret, ad_tag, hosts, public_ip, port, level), encoding="utf-8")
    proc = await asyncio.create_subprocess_exec(
        str(telemt.TELEMT_BIN), "run", str(cfg_path),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        env=os.environ.copy(), cwd=str(run_dir),
    )
    entry = {"proc": proc, "port": port, "boot": [], "sig": None}
    asyncio.create_task(_drain(entry))
    await asyncio.sleep(1.2)
    if proc.returncode is not None:
        await asyncio.sleep(0.4)
        out = " | ".join(entry["boot"][-10:])[:700] or "(بدون خروجی)"
        raise RuntimeError(f"telemt (حالت WEB) بلافاصله متوقف شد (کد {proc.returncode}). خروجی telemt: {out}")
    return entry


async def stop():
    async with _lock:
        for e in list(_procs.values()):
            await _kill(e)
        _procs.clear()
    global _http
    if _http is not None:
        await _http.aclose()
        _http = None


async def sync(items: Dict[str, dict], hosts: List[str]) -> None:
    """items: token -> {"secret": str, "ad_tag": Optional[str]}.
    برای هر توکن یک پروسه‌ی telemt بالا میاره/به‌روز می‌کنه، پروسه‌ی توکن‌های حذف‌شده
    رو می‌بنده. فقط پروسه‌ای که کانفیگش عوض شده ری‌استارت میشه (بقیه دست نمی‌خورن)."""
    global _last_error, _level
    async with _lock:
        hosts = [h.strip().lower() for h in dict.fromkeys(hosts) if valid_host(h)]
        # حذف پروسه‌های بی‌صاحب یا مرده
        for tok in [t for t in _procs if t not in items]:
            await _kill(_procs.pop(tok))
        for tok, e in list(_procs.items()):
            if e["proc"].returncode is not None:
                _procs.pop(tok, None)
        if not items:
            _last_error = None
            return
        if not hosts:
            _last_error = "هیچ دامنه‌ی معتبری پیدا نشد"
            raise RuntimeError("دامنه‌ی عمومی پنل (مثلاً xxx.fly.dev) پیدا نشد؛ telemt فقط دامنه‌ی واقعی می‌پذیرد، نه localhost یا IP")
        _write_decoy()
        public_ip = await _resolve_ip(hosts[0])
        try:
            for tok, it in items.items():
                sig = hashlib.sha1(
                    f"{it['secret']}|{it.get('ad_tag') or ''}|{','.join(hosts)}|{_level}".encode()
                ).hexdigest()
                cur = _procs.get(tok)
                if cur and cur["sig"] == sig and cur["proc"].returncode is None:
                    continue
                if cur:
                    await _kill(cur)
                    _procs.pop(tok, None)
                errors = []
                entry = None
                while entry is None:
                    try:
                        entry = await _start_one(tok, it["secret"], it.get("ad_tag"), hosts, public_ip, _level)
                    except Exception as exc:
                        errors.append(f"سطح {_level}: {exc}")
                        if _level == 0:
                            raise RuntimeError("  ||  ".join(errors))
                        # این نسخه‌ی telemt کانفیگ این سطح را قبول نکرد → یک سطح ساده‌تر
                        _level -= 1
                sig = hashlib.sha1(
                    f"{it['secret']}|{it.get('ad_tag') or ''}|{','.join(hosts)}|{_level}".encode()
                ).hexdigest()
                entry["sig"] = sig
                _procs[tok] = entry
            _last_error = None
        except Exception as exc:
            _last_error = str(exc)
            raise


def get_status() -> dict:
    return {"running": is_running(), "processes": len(_procs), "speed_level": _level, "error": _last_error}


# ── فوروارد درخواست‌ها به telemt ─────────────────────────────────────────────
_HOP = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te",
        "trailers", "transfer-encoding", "upgrade"}
_DROP_REQ = _HOP | {"host", "content-length", "accept-encoding", "x-forwarded-for",
                    "x-forwarded-host", "x-forwarded-proto", "x-forwarded-port",
                    "x-real-ip", "forwarded", "cf-connecting-ip", "true-client-ip"}


def _get_http() -> httpx.AsyncClient:
    global _http
    if _http is None:
        _http = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=5.0, read=70.0, write=30.0, pool=10.0),
            limits=httpx.Limits(max_connections=400, max_keepalive_connections=50),
        )
    return _http


async def forward(request: Request, token: str, rest: str, host: str, client_ip: str,
                  on_bytes: Callable[[int], None]) -> Response:
    entry = _procs.get(token)
    if not entry or entry["proc"].returncode is not None:
        return Response(status_code=503)
    url = f"http://127.0.0.1:{entry['port']}/{token}/{rest}"
    if request.url.query:
        url += "?" + request.url.query
    headers = {k: v for k, v in request.headers.items() if k.lower() not in _DROP_REQ}
    headers["Host"] = host
    headers["X-Forwarded-For"] = client_ip or "0.0.0.0"
    body = await request.body()
    if body:
        on_bytes(len(body))
    client = _get_http()
    try:
        req = client.build_request(request.method, url, headers=headers, content=body)
        resp = await client.send(req, stream=True)
    except Exception:
        return Response(status_code=502)

    async def gen():
        try:
            async for chunk in resp.aiter_raw():
                on_bytes(len(chunk))
                yield chunk
        finally:
            await resp.aclose()

    out_headers = {k: v for k, v in resp.headers.items()
                   if k.lower() not in _HOP and k.lower() != "content-length"}
    return StreamingResponse(gen(), status_code=resp.status_code, headers=out_headers)


# ── فوروارد WebSocket (carrier = websocket) ──────────────────────────────────
async def ws_proxy(websocket, token: str, host: str, ip: str,
                   on_bytes: Callable[[int], None], touch: Callable[[], None],
                   is_allowed: Callable[[], bool]) -> None:
    """WebSocket کلاینت را به /<token>/api/v1/ws در telemt وصل می‌کند و دوطرفه پمپ می‌کند.
    از sock آماده استفاده می‌کنیم تا هدر Host همان دامنه‌ی vhost بماند ولی اتصال به 127.0.0.1 برود."""
    import websockets
    entry = _procs.get(token)
    if not entry or entry["proc"].returncode is not None:
        await websocket.close(code=1013)
        return
    loop = asyncio.get_running_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    try:
        await asyncio.wait_for(loop.sock_connect(sock, ("127.0.0.1", entry["port"])), 5)
        protos = list(websocket.scope.get("subprotocols") or [])
        try:
            major = int(websockets.version.version.split(".")[0])
        except Exception:
            major = 12
        hdr_key = "additional_headers" if major >= 13 else "extra_headers"
        up = await websockets.connect(
            f"ws://{host}/{token}/api/v1/ws",
            sock=sock, subprotocols=protos or None, compression=None,
            max_size=None, ping_interval=None,
            **{hdr_key: {"X-Forwarded-For": ip or "0.0.0.0"}},
        )
    except Exception:
        try:
            sock.close()
        except Exception:
            pass
        await websocket.close(code=1011)
        return

    await websocket.accept(subprotocol=up.subprotocol)

    async def c2u():
        while True:
            m = await websocket.receive()
            if m["type"] == "websocket.disconnect":
                return
            data = m.get("bytes") if m.get("bytes") is not None else m.get("text")
            if data is None:
                continue
            on_bytes(len(data))
            if not is_allowed():
                return
            await up.send(data)

    async def u2c():
        async for m in up:
            on_bytes(len(m))
            if not is_allowed():
                return
            if isinstance(m, (bytes, bytearray)):
                await websocket.send_bytes(bytes(m))
            else:
                await websocket.send_text(m)

    async def keep():
        while True:
            await asyncio.sleep(15)
            touch()

    tasks = [asyncio.create_task(c()) for c in (c2u, u2c, keep)]
    try:
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    finally:
        for t in tasks:
            t.cancel()
        try:
            await up.close()
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass
