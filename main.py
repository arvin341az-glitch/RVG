import subprocess
import sys

_PACKAGES = [
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "uvloop>=0.19.0",
    "httptools>=0.6.0",
    "httpx[http2]==0.25.1",
    "websockets==12.0",
    "aiofiles>=23.2.1",
    "cryptography>=39.0.0",
]

def _install_packages():
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", *_PACKAGES],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        print(f"[STARTUP] خطا در نصب پکیج‌ها:\n{e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)

# _install_packages()  # deps preinstalled for local test

import asyncio
import json
import os
import hashlib
import secrets
import sys
import time
import traceback
import central
import aiofiles
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import quote
from collections import deque, defaultdict
from pathlib import Path
import bottokentcpproxy
from protocol.mtproto import mtproto_native as mtproto
from typing import Optional
import base64
import botgeneratedomin
import bottokentcpproxy
import zeussocks5
from protocol.mtproto import mtproto_native as mtproto
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import Response, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RVG-Gateway")

IRAN_TZ = ZoneInfo("Asia/Tehran")

app = FastAPI(title="RVG Gateway - codebox", docs_url=None, redoc_url=None)

# وقتی مستقیم با `python main.py` اجرا میشه، این ماژول با نام "__main__" ثبت
# میشه نه "main". چون protocol/vless/vless.py و protocol/trojan/trojan.py با
# `from main import (...)` به این فایل رفرنس می‌دن، بدون این خط پایتون مجبور
# میشه کل main.py رو یک‌بار دیگه از صفر به‌عنوان ماژول جداگانه‌ی "main" اجرا کنه
# که باعث circular import و کرش میشه. با alias کردن sys.modules، هر دو اسم
# به همین نمونه‌ی در حال اجرا اشاره می‌کنن.
sys.modules.setdefault("main", sys.modules[__name__])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Persistence ───────────────────────────────────────────────────────────────
DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
DATA_FILE = DATA_DIR / "rvg_state.json"
SECRET_FILE = DATA_DIR / ".rvg_secret"
SAVE_LOCK = asyncio.Lock()


def _get_or_create_secret() -> str:
    env_secret = os.environ.get("SECRET_KEY")
    if env_secret:
        return env_secret
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if SECRET_FILE.exists():
            val = SECRET_FILE.read_text(encoding="utf-8").strip()
            if val:
                return val
        new_secret = secrets.token_urlsafe(32)
        SECRET_FILE.write_text(new_secret, encoding="utf-8")
        logger.info("SECRET_KEY جدید ساخته و در دیسک ذخیره شد (پایدار بین ری‌استارت‌ها).")
        return new_secret
    except Exception as e:
        logger.warning(f"عدم امکان ذخیره‌ی SECRET_KEY روی دیسک: {e} — از مقدار موقت استفاده می‌شود.")
        return secrets.token_urlsafe(32)


CONFIG = {
    "port": int(os.environ.get("PORT", 8000)),
    "secret": _get_or_create_secret(),
    "host": os.environ.get("RAILWAY_PUBLIC_DOMAIN", "localhost"),
    "disable_logging": False,
}


def apply_logging_state():
    """logging.disable سطح‌بندی سراسریه (روی کل ماژول logging اثر می‌ذاره)، پس
    یک‌جا همه‌ی logger های پروژه (RVG-Gateway، uvicorn.access، uvicorn.error،
    mtproto و ...) رو خاموش/روشن می‌کنه. چک داخلیش خیلی ارزونه، پس این خودش
    باعث می‌شه سربار I/O و فرمت‌کردن استرینگ لاگ‌ها کاملاً حذف بشه."""
    if CONFIG.get("disable_logging"):
        logging.disable(logging.CRITICAL)
    else:
        logging.disable(logging.NOTSET)


async def load_state():
    global LINKS, AUTH, SUBS
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if DATA_FILE.exists():
            async with aiofiles.open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = await f.read()
            data = json.loads(raw)
            LINKS.update(data.get("links", {}))
            SUBS.update(data.get("subs", {}))
            NODE_KEYS.update(data.get("node_keys", {}))
            for nid, n in (data.get("nodes") or {}).items():
                NODES[nid] = _normalize_node(n)
            if "password_hash" in data:
                AUTH["password_hash"] = data["password_hash"]
            CONFIG["disable_logging"] = bool(data.get("disable_logging", False))
            apply_logging_state()
            logger.info(
                f"State loaded: {len(LINKS)} links, {len(SUBS)} subs, "
                f"{len(NODES)} nodes, {len(NODE_KEYS)} node keys"
            )
    except Exception as e:
        logger.warning(f"Could not load state: {e}")

async def save_state():
    async with SAVE_LOCK:
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            data = {
                "links": dict(LINKS),
                "subs": dict(SUBS),
                "node_keys": dict(NODE_KEYS),
                "nodes": dict(NODES),
                "password_hash": AUTH["password_hash"],
                "disable_logging": CONFIG.get("disable_logging", False),
                "saved_at": datetime.now().isoformat(),
            }
            tmp = DATA_FILE.with_suffix(".tmp")
            async with aiofiles.open(tmp, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            tmp.replace(DATA_FILE)
        except Exception as e:
            logger.warning(f"Could not save state: {e}")


# ── Debounced save ─────────────────────────────────────────────────────────────
# هر بار که یک کانکشن (trojan/vless/shadowsocks/xhttp) بسته میشه، schedule_save()
# صدا زده میشه به‌جای save_state() مستقیم. اگه صدها کانکشن در ثانیه باز و بسته بشن
# (که برای WebSocket-based transportها عادیه)، save_state() قبلی باعث میشد به همون
# تعداد، کل state سریالایز و روی دیسک نوشته بشه و event loop تک‌هسته‌ای رو مسدود کنه.
# اینجا چندین درخواست ذخیره‌سازی که در بازه‌ی SAVE_DEBOUNCE_SECONDS اتفاق بیفتن،
# در یک نوشتن واحد روی دیسک ادغام میشن.
SAVE_DEBOUNCE_SECONDS = 2.0
_save_pending = False
_save_dirty_again = False


async def schedule_save():
    """نسخه‌ی debounce شده‌ی save_state — برای صدا زدن مکرر و پرتعداد (هر بسته شدن کانکشن) امن است."""
    global _save_pending, _save_dirty_again
    if _save_pending:
        _save_dirty_again = True
        return
    _save_pending = True
    try:
        while True:
            _save_dirty_again = False
            await asyncio.sleep(SAVE_DEBOUNCE_SECONDS)
            await save_state()
            if not _save_dirty_again:
                break
    finally:
        _save_pending = False

# ── In-memory state ───────────────────────────────────────────────────────────
connections: dict = {}
stats = {
    "total_bytes": 0,
    "total_requests": 0,
    "total_errors": 0,
    "start_time": time.time(),
}
class _ErrorLogDeque(deque):
    """deque معمولی، با این تفاوت که وقتی توقف لاگ‌گیری فعال باشه append() هیچ کاری
    نمی‌کنه. با این روش همه‌ی error_logs.append(...) های پخش‌شده توی پروژه
    (websocket.py ها، xhttp_core.py ها و ...) بدون نیاز به تغییر خودشون از این
    فلگ پیروی می‌کنن."""
    def append(self, item):
        if CONFIG.get("disable_logging"):
            return
        super().append(item)


error_logs: deque = _ErrorLogDeque(maxlen=50)
activity_logs: deque = deque(maxlen=200)
hourly_traffic: dict = defaultdict(int)
http_client: httpx.AsyncClient | None = None
LINKS: dict = {}
LINKS_LOCK = asyncio.Lock()
SUBS: dict = {}
SUBS_LOCK = asyncio.Lock()

# ── MTProto (mtproto_native / باینری رسمی تلگرام) — هر لینک = یک پروسه‌ی جدا،
# روی پورت خودش، با ad_tag مستقل خودش (per-instance، دقیقاً مثل mtg قدیم) ──

# ── Node linking (اتصال چند پنل به هم) ────────────────────────────────────────
# NODE_KEYS: کلیدهایی که *این* پنل صادر کرده. هر کلید به یک پنل دیگه اجازه میده
#            دیتای این پنل رو بخونه و روی کانفیگ‌هاش بنویسه (سمت inbound).
# NODES:     پنل‌هایی که *این* پنل بهشون وصل شده و دیتاشون رو ادغام می‌کنه (سمت outbound).
NODE_KEYS: dict = {}
NODE_KEYS_LOCK = asyncio.Lock()
NODES: dict = {}
NODES_LOCK = asyncio.Lock()
_NODE_CACHE: dict = {}          # node_id -> {"at": float, "data": dict}
NODE_CACHE_TTL = 8.0
NODE_KEY_PREFIX = "rvg-"
NODE_KEY_HEADER = "X-RVG-Node-Key"
NODE_SHARE_PARTS = ("usage", "links", "subs", "requests", "logs")

PROTOCOLS = (
    "vless-ws", "xhttp-packet-up", "xhttp-stream-up",
    "trojan-ws", "trojan-xhttp-packet-up", "trojan-xhttp-stream-up",
    "mtproto", "shadowsocks",
)
DEFAULT_PROTOCOL = "vless-ws"

def log_activity(kind: str, message: str, level: str = "info"):
    activity_logs.append({
        "kind": kind,
        "level": level,
        "message": message,
        "time": datetime.now().isoformat(),
    })


# ── Auth ──────────────────────────────────────────────────────────────────────
SESSION_COOKIE = "rvg_session"
SESSION_TTL = 60 * 60 * 24 * 7

def hash_password(pw: str) -> str:
    return hashlib.sha256(f"{pw}{CONFIG['secret']}".encode()).hexdigest()

AUTH = {"password_hash": hash_password(os.environ.get("ADMIN_PASSWORD", "123456"))}
SESSIONS: dict = {}
SESSIONS_LOCK = asyncio.Lock()

async def create_session() -> str:
    token = secrets.token_urlsafe(32)
    async with SESSIONS_LOCK:
        SESSIONS[token] = time.time() + SESSION_TTL
    return token

async def is_valid_session(token: str | None) -> bool:
    if not token:
        return False
    async with SESSIONS_LOCK:
        exp = SESSIONS.get(token)
        if exp is None:
            return False
        if exp < time.time():
            SESSIONS.pop(token, None)
            return False
        return True

async def destroy_session(token: str | None):
    if not token:
        return
    async with SESSIONS_LOCK:
        SESSIONS.pop(token, None)

async def require_auth(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if not await is_valid_session(token):
        raise HTTPException(status_code=401, detail="unauthorized")
    return token

# ── Startup / Shutdown ────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    asyncio.create_task(central.heartbeat_loop())
    global http_client
    limits = httpx.Limits(max_connections=500, max_keepalive_connections=100)
    timeout = httpx.Timeout(30.0, connect=10.0)
    http_client = httpx.AsyncClient(
        limits=limits, timeout=timeout, follow_redirects=True,
    )
    await load_state()
    await _restart_mtproto_instances()
    log_activity("system", "سرور راه‌اندازی شد", "ok")
    logger.info(f"RVG Gateway v9.2 started on port {CONFIG['port']}")

async def _restart_mtproto_instances():
    """بعد از بالا اومدن پنل، به‌ازای هر لینک MTProto فعال یک پروسه‌ی جدای
    mtproto_native (باینری رسمی تلگرام) روی پورت خودش بالا می‌آره."""
    async with LINKS_LOCK:
        targets = [
            (uid, d) for uid, d in LINKS.items()
            if d.get("protocol") == "mtproto" and d.get("active", True)
        ]
    if targets and not bottokentcpproxy.has_saved_token():
        logger.error(
            f"⚠️ {len(targets)} لینک MTProto وجود دارد ولی توکن Railway ذخیره نشده — "
            f"هیچ TCP Proxy عمومی ساخته/بازسازی نمی‌شود و این لینک‌ها از بیرون کار نمی‌کنند. "
            f"(اگر قبلاً توکن را وارد کرده بودید، یعنی دایرکتوری DATA_DIR بین دیپلوی‌ها "
            f"پاک می‌شود و باید یک Volume پایدار روی Railway بهش وصل کنید.)"
        )
    for uid, d in targets:
        try:
            inst = await mtproto.start_instance(
                uid,
                secret=d.get("mtproto_secret"),
                domain=d.get("mtproto_domain", mtproto.DEFAULT_FAKE_TLS_DOMAIN),
                preferred_port=d.get("mtproto_port"),
                force_port=d.get("mtproto_manual_port", False),
                ad_tag=d.get("ad_tag"),
            )
        except Exception as exc:
            logger.error(f"MTProto[{uid[:8]}]: راه‌اندازی ناموفق بود: {exc}\n{traceback.format_exc()}")
            continue

        old_port = d.get("mtproto_port")
        async with LINKS_LOCK:
            if uid in LINKS:
                LINKS[uid]["mtproto_port"] = inst["port"]
                LINKS[uid]["mtproto_secret"] = inst["secret"]

        if (d.get("mtproto_proxy_id") and inst["port"] != old_port
                and not d.get("mtproto_manual_port", False)):
            asyncio.create_task(_reattach_mtproto_public_proxy(
                uid, inst["port"], d.get("mtproto_proxy_id"), d.get("label", "")
            ))
        elif not d.get("mtproto_proxy_id") and bottokentcpproxy.has_saved_token():
            # لینکی که هنوز هیچ TCP Proxy عمومی نداره (مثلاً چون با نسخه‌ی قدیمی
            # ساخته شده) — بدون این، لینکش مرده می‌مونه.
            asyncio.create_task(_attach_mtproto_public_proxy(
                uid, inst["port"], d.get("label", "")
            ))


async def _mtproto_usage_callback(uuid: str, n_bytes: int) -> bool:
    async with LINKS_LOCK:
        link = LINKS.get(uuid)
        if link is None:
            return False
        if not is_link_allowed(link):
            return False
        link["used_bytes"] += n_bytes
        stats["total_bytes"] += n_bytes
        hourly_traffic[now_ir().strftime("%H:00")] += n_bytes
    return True

mtproto.set_usage_callback(_mtproto_usage_callback)


async def _attach_mtproto_public_proxy(uid: str, application_port: int, label: str):
    """TCP Proxy عمومی روی Railway برای پورت این instance خاص می‌سازه (هر لینک
    پورت جدای خودش رو داره، پس هرکدوم TCP Proxy جدای خودش رو لازم داره)."""
    try:
        pub = await bottokentcpproxy.create_public_proxy_for_port(application_port)
    except Exception as exc:
        logger.warning(f"TCP Proxy عمومی برای {uid[:8]} ناموفق بود: {exc}")
        log_activity("link", f"ساخت TCP Proxy عمومی برای «{label}» ناموفق بود: {exc}", "err")
        return
    async with LINKS_LOCK:
        if uid in LINKS:
            LINKS[uid]["mtproto_public_host"] = pub["domain"]
            LINKS[uid]["mtproto_public_port"] = pub["port"]
            LINKS[uid]["mtproto_proxy_id"] = pub["id"]
            LINKS[uid]["mtproto_public_pending"] = False
    asyncio.create_task(save_state())
    log_activity("link", f"TCP Proxy عمومی «{label}» آماده شد ({pub['domain']}:{pub['port']})", "ok")


async def _reattach_mtproto_public_proxy(uid: str, new_port: int, old_proxy_id: Optional[str], label: str):
    if old_proxy_id:
        await bottokentcpproxy.delete_public_proxy(old_proxy_id)
    await _attach_mtproto_public_proxy(uid, new_port, label)


async def _update_mtproto_ad_tag(uuid: str, ad_tag: str):
    """پروسه‌ی این کاربر رو stop/start می‌کنه تا ad_tag جدید (که -P هست، سطح
    process، نه runtime-API) اعمال بشه. force_port=True چون تازه stop شده و
    پورت قدیمی باید آزاد باشه؛ اگه بازم آزاد نشد، پورت جدید می‌گیره و TCP Proxy
    عمومی رو دوباره به پورت جدید وصل می‌کنیم."""
    try:
        async with LINKS_LOCK:
            link = LINKS.get(uuid)
            if not link:
                return
            label = link.get("label", "")
            secret = link.get("mtproto_secret")
            domain = link.get("mtproto_domain", mtproto.DEFAULT_FAKE_TLS_DOMAIN)
            old_port = link.get("mtproto_port")
            old_proxy_id = link.get("mtproto_proxy_id")
            manual_port = link.get("mtproto_manual_port", False)
            if not secret:
                logger.error(f"MTProto[{uuid[:8]}]: سکرت پیدا نشد")
                return

        await mtproto.stop_instance(uuid)
        try:
            inst = await mtproto.start_instance(
                uuid,
                secret=secret,
                domain=domain,
                preferred_port=old_port,
                force_port=True,
                ad_tag=ad_tag,
            )
        except RuntimeError as exc:
            logger.warning(f"ad_tag ناموفق بود ({exc})، تلاش با پورت جدید...")
            inst = await mtproto.start_instance(
                uuid,
                secret=secret,
                domain=domain,
                preferred_port=None,
                force_port=False,
                ad_tag=ad_tag,
            )

        async with LINKS_LOCK:
            link = LINKS.get(uuid)
            if not link:
                asyncio.create_task(mtproto.stop_instance(uuid))
                return
            link["mtproto_port"] = inst["port"]
            link["mtproto_secret"] = inst["secret"]
            link["mtproto_domain"] = inst["domain"]
            link["ad_tag"] = ad_tag
            link["ad_tag_status"] = "done"
            link["ad_tag_link"] = generate_share_link(
                uuid, get_host(), remark=f"RVG-{link.get('label','')}", protocol="mtproto"
            )

        if inst["port"] != old_port and old_proxy_id and not manual_port:
            asyncio.create_task(_reattach_mtproto_public_proxy(
                uuid, inst["port"], old_proxy_id, label
            ))

        asyncio.create_task(save_state())
        logger.info(
            f"MTProto[{uuid[:8]}]: ad_tag به‌روز شد، instance ری‌استارت شد "
            f"(پورت: {old_port} -> {inst['port']})"
        )
        log_activity("link", f"تبلیغ کانال برای «{label}» با موفقیت اعمال شد", "ok")

    except Exception as exc:
        logger.error(f"خطا در به‌روزرسانی ad_tag برای {uuid[:8]}: {exc}")
        async with LINKS_LOCK:
            if uuid in LINKS:
                LINKS[uuid]["ad_tag_status"] = "error"
        log_activity("link", f"به‌روزرسانی ad_tag برای «{LINKS.get(uuid,{}).get('label','')}» ناموفق بود", "err")
        asyncio.create_task(save_state())


@app.on_event("shutdown")
async def shutdown():
    await save_state()
    await mtproto.stop_all()
    if http_client:
        await http_client.aclose()

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_host() -> str:
    return os.environ.get("RAILWAY_PUBLIC_DOMAIN", CONFIG["host"])

def generate_uuid() -> str:
    h = secrets.token_hex(16)
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"

def now_ir() -> datetime:
    return datetime.now(IRAN_TZ)

def generate_share_link(uuid: str, host: str, remark: str = "RVG", protocol: str = DEFAULT_PROTOCOL) -> str:
    link = LINKS.get(uuid) or {}
    alpn = link.get("alpn", "h2")
    fp = link.get("fingerprint", "chrome")

    if protocol == "mtproto":
        secret = link.get("mtproto_secret")
        if not secret:
            return f"tg://proxy?server={host}&port=0&secret=not_ready#{quote(remark)}"
        # مهم: برای MTProto هیچ‌وقت به دامنه‌ی پنل fallback نمی‌کنیم. دامنه‌ی اصلی
        # Railway فقط HTTP/443 رو سرو می‌کنه و پورت داخلی (مثلاً 8477) از بیرون
        # اصلاً باز نیست — چنین لینکی کاملاً مرده‌ست (نه پینگ می‌ده نه وصل می‌شه).
        # تنها آدرس معتبر، دامنه/پورتی هست که Railway موقع ساخت TCP Proxy می‌ده.
        pub_host = link.get("mtproto_public_host")
        pub_port = link.get("mtproto_public_port")
        if not pub_host or not pub_port:
            return f"tg://proxy?server={host}&port=0&secret=not_ready#{quote(remark)}"
        return mtproto.generate_mtproto_link(
            pub_host, pub_port, secret,
            mtproto.sanitize_domain(link.get("mtproto_domain"))
        )

    if protocol == "shadowsocks":
        cipher = link.get("ss_cipher", DEFAULT_CIPHER)
        password = link.get("ss_password", "")
        return generate_ss_link(host, 443, cipher, password, remark)

    if protocol == "trojan-ws":
        params = {
            "security": "tls", "type": "ws", "host": host,
            "path": "/trojan-ws", "sni": host, "fp": fp, "alpn": alpn,
        }
        query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
        return f"trojan://{uuid}@{host}:443?{query}#{quote(remark)}"

    if protocol.startswith("trojan-xhttp-"):
        mode = protocol.replace("trojan-xhttp-", "")
        path = f"/txhttp-siz10/{mode}/{uuid}"
        params = {
            "security": "tls", "type": "xhttp", "mode": mode, "host": host,
            "path": path, "sni": host, "fp": fp, "alpn": alpn,
        }
        query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
        return f"trojan://{uuid}@{host}:443?{query}#{quote(remark)}"

    if protocol == "vless-ws":
        path = f"/ws/{uuid}"
        params = {
            "encryption": "none",
            "security": "tls",
            "type": "ws",
            "host": host,
            "path": path,
            "sni": host,
            "fp": fp,
            "alpn": alpn,
        }
    else:
        mode = protocol.replace("xhttp-", "")
        path = f"/xhttp-siz10/{mode}/{uuid}"
        params = {
            "encryption": "none",
            "security": "tls",
            "type": "xhttp",
            "mode": mode,
            "host": host,
            "path": path,
            "sni": host,
            "fp": fp,
            "alpn": alpn,
        }
    query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
    return f"vless://{uuid}@{host}:443?{query}#{quote(remark)}"

def uptime() -> str:
    secs = int(time.time() - stats["start_time"])
    h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def parse_size_to_bytes(value: float, unit: str) -> int:
    unit = unit.upper()
    if unit == "GB": return int(value * 1024 ** 3)
    if unit == "MB": return int(value * 1024 ** 2)
    if unit == "KB": return int(value * 1024)
    return int(value)

def is_link_expired(link: dict) -> bool:
    exp = link.get("expires_at")
    if not exp:
        return False
    try:
        return datetime.now() > datetime.fromisoformat(exp)
    except Exception:
        return False

def is_link_allowed(link: dict | None) -> bool:
    if link is None:
        return False
    if not link.get("active", True):
        return False
    if is_link_expired(link):
        return False
    lb = link.get("limit_bytes", 0)
    if lb > 0 and link.get("used_bytes", 0) >= lb:
        return False
    return True

def fmt_bytes(b: int) -> str:
    if b < 1024: return f"{b} B"
    if b < 1024**2: return f"{b/1024:.1f} KB"
    if b < 1024**3: return f"{b/1024**2:.2f} MB"
    return f"{b/1024**3:.2f} GB"

def build_sub_headers(label: str, used_bytes: int, limit_bytes: int, expires_at: str | None, support_url: str = "https://t.me/CodeBoxo") -> dict:
    total = limit_bytes if limit_bytes > 0 else 0
    expire_ts = 0
    if expires_at:
        try:
            expire_ts = int(datetime.fromisoformat(expires_at).timestamp())
        except Exception:
            expire_ts = 0
    userinfo = f"upload=0; download={used_bytes}; total={total}; expire={expire_ts}"
    title_b64 = base64.b64encode(label.encode("utf-8")).decode()
    return {
        "profile-title": f"base64:{title_b64}",
        "subscription-userinfo": userinfo,
        "profile-update-interval": "6",
        "support-url": support_url,
    }

def client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "نامشخص"

# ── Node linking helpers ──────────────────────────────────────────────────────
def _b64u_encode(s: str) -> str:
    return base64.urlsafe_b64encode(s.encode("utf-8")).decode().rstrip("=")


def _b64u_decode(s: str) -> str:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad).decode("utf-8")


def build_node_key(host: str, secret: str) -> str:
    """کلید خودکفا: دامنه‌ی این پنل داخل خودِ کلید کدگذاری میشه."""
    return f"{NODE_KEY_PREFIX}{_b64u_encode(host)}.{secret}"


def parse_node_key(key: str) -> tuple[str, str]:
    """برمی‌گرداند (host, secret). در صورت نامعتبر بودن ValueError می‌دهد."""
    key = (key or "").strip()
    if not key.startswith(NODE_KEY_PREFIX):
        raise ValueError("کلید باید با rvg- شروع شود")
    body = key[len(NODE_KEY_PREFIX):]
    if "." not in body:
        raise ValueError("ساختار کلید نامعتبر است")
    host_part, secret = body.split(".", 1)
    if not secret:
        raise ValueError("بخش سکرت کلید خالی است")
    try:
        host = _b64u_decode(host_part).strip()
    except Exception:
        raise ValueError("دامنه‌ی داخل کلید قابل خواندن نیست")
    if not host or "/" in host or " " in host:
        raise ValueError("دامنه‌ی داخل کلید نامعتبر است")
    return host, secret


def _node_scheme(host: str) -> str:
    # فقط برای تست محلی http مجاز است؛ در بقیه‌ی موارد اجباراً https
    return "http" if host.startswith(("localhost", "127.0.0.1")) else "https"


def _normalize_node(n: dict) -> dict:
    share = n.get("share") or {}
    return {
        "label": str(n.get("label") or n.get("host") or "نود")[:60],
        "host": str(n.get("host") or ""),
        "key": str(n.get("key") or ""),
        "enabled": bool(n.get("enabled", True)),
        "merge_dashboard": bool(n.get("merge_dashboard", True)),
        "share": {p: bool(share.get(p, p != "logs")) for p in NODE_SHARE_PARTS},
        "created_at": n.get("created_at") or datetime.now().isoformat(),
        "last_sync_at": n.get("last_sync_at"),
        "last_error": n.get("last_error"),
        "peer_version": n.get("peer_version"),
    }


def _node_public(node_id: str, n: dict) -> dict:
    """نسخه‌ی امن برای فرانت‌اند — کلید خام بیرون نمی‌رود."""
    out = {k: v for k, v in n.items() if k != "key"}
    out["node_id"] = node_id
    out["key_preview"] = (n.get("key") or "")[:14] + "…"
    return out


async def _node_request(node: dict, method: str, path: str, *,
                        params: dict | None = None,
                        json_body: dict | None = None,
                        timeout: float = 10.0) -> httpx.Response:
    host = node["host"]
    url = f"{_node_scheme(host)}://{host}{path}"
    client = http_client or httpx.AsyncClient()
    return await client.request(
        method, url,
        params=params, json=json_body,
        headers={NODE_KEY_HEADER: node["key"]},
        timeout=timeout, follow_redirects=False,
    )


async def require_node_key(request: Request) -> str:
    """احراز هویت پنل مقابل با هدر X-RVG-Node-Key (بدون کوکی سشن)."""
    raw = (request.headers.get(NODE_KEY_HEADER) or "").strip()
    if not raw:
        raise HTTPException(status_code=401, detail="node key missing")
    try:
        _, secret = parse_node_key(raw)
    except ValueError:
        raise HTTPException(status_code=401, detail="invalid node key")
    matched = None
    async with NODE_KEYS_LOCK:
        for key_id, entry in NODE_KEYS.items():
            if entry.get("revoked"):
                continue
            if secrets.compare_digest(str(entry.get("secret", "")), secret):
                matched = key_id
                break
        if matched is None:
            raise HTTPException(status_code=401, detail="unknown or revoked node key")
        entry = NODE_KEYS[matched]
        entry["last_used_at"] = datetime.now().isoformat()
        entry["use_count"] = int(entry.get("use_count", 0)) + 1
    asyncio.create_task(schedule_save())
    return matched

# ── Default link ──────────────────────────────────────────────────────────────
_default_link_created = False

async def ensure_default_link():
    global _default_link_created
    if _default_link_created:
        return
    async with LINKS_LOCK:
        if not any(l.get("is_default") for l in LINKS.values()):
            uid = hashlib.sha256(f"default{CONFIG['secret']}".encode()).hexdigest()
            uid = f"{uid[:8]}-{uid[8:12]}-{uid[12:16]}-{uid[16:20]}-{uid[20:32]}"
            if uid not in LINKS:
                LINKS[uid] = {
                    "label": "لینک پیش‌فرض",
                    "limit_bytes": 0,
                    "used_bytes": 0,
                    "created_at": datetime.now().isoformat(),
                    "active": True,
                    "expires_at": None,
                    "note": "",
                    "is_default": True,
                    "sub_id": None,
                    "protocol": DEFAULT_PROTOCOL,
                }
                asyncio.create_task(save_state())
        _default_link_created = True

# ── Basic endpoints ───────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"service": "RVG Gateway", "version": "9.2", "status": "active", "channel": "https://t.me/CodeBoxo"}

@app.get("/health")
async def health():
    return {"status": "ok", "connections": len(connections), "uptime": uptime()}

# ── Subscription (single link) ────────────────────────────────────────────────
@app.get("/sub/{uuid}")
async def subscription_single(uuid: str):
    async with LINKS_LOCK:
        link = LINKS.get(uuid)
    if not link or not is_link_allowed(link):
        raise HTTPException(status_code=404, detail="not found or inactive")
    host = get_host()
    proto = link.get("protocol", DEFAULT_PROTOCOL)
    vless = generate_share_link(uuid, host, remark=f"RVG-{link['label']}", protocol=proto)
    content = base64.b64encode(vless.encode()).decode()
    headers = build_sub_headers(link["label"], link.get("used_bytes", 0), link.get("limit_bytes", 0), link.get("expires_at"))
    return Response(content=content, media_type="text/plain", headers=headers)

@app.get("/sub-all")
async def subscription_all(_=Depends(require_auth)):
    host = get_host()
    async with LINKS_LOCK:
        allowed = [d for d in LINKS.values() if is_link_allowed(d)]
        lines = [
            generate_share_link(uid, host, remark=f"RVG-{d['label']}", protocol=d.get("protocol", DEFAULT_PROTOCOL))
            for uid, d in LINKS.items()
            if is_link_allowed(d)
        ]
        total_used = sum(d.get("used_bytes", 0) for d in allowed)
        total_limit = sum(d.get("limit_bytes", 0) for d in allowed)
        expiries = [d["expires_at"] for d in allowed if d.get("expires_at")]
    nearest_exp = min(expiries) if expiries else None
    content = base64.b64encode("\n".join(lines).encode()).decode()
    headers = build_sub_headers("RVG-All", total_used, total_limit, nearest_exp)
    return Response(content=content, media_type="text/plain", headers=headers)

# ══════════════════════════════════════════════════════════════════════════════
# SUB GROUP endpoints (بدون تغییر)
# ══════════════════════════════════════════════════════════════════════════════

async def _create_sub_core(body: dict) -> dict:
    name = (body.get("name") or "گروه جدید").strip()[:60]
    desc = (body.get("desc") or "").strip()[:200]
    password = (body.get("password") or "").strip()
    sub_id = generate_uuid()
    uuid_key = secrets.token_urlsafe(16)
    async with SUBS_LOCK:
        SUBS[sub_id] = {
            "name": name,
            "desc": desc,
            "password_hash": hash_password(password) if password else None,
            "uuid_key": uuid_key,
            "created_at": datetime.now().isoformat(),
            "link_ids": [],
            "node_link_ids": [],
        }
    asyncio.create_task(save_state())
    log_activity("sub", f"گروه «{name}» ساخته شد", "ok")
    host = get_host()
    return {
        "sub_id": sub_id,
        **SUBS[sub_id],
        "public_url": f"https://{host}/p/{uuid_key}",
        "sub_url": f"https://{host}/sub-group/{uuid_key}",
    }

@app.post("/api/subs")
async def create_sub(request: Request, _=Depends(require_auth)):
    body = await request.json()
    return await _create_sub_core(body)

@app.post("/api/node/subs")
async def node_create_sub(request: Request, key_id: str = Depends(require_node_key)):
    await _require_node_manage(key_id)
    body = await request.json()
    return await _create_sub_core(body)

@app.get("/api/subs")
async def list_subs(_=Depends(require_auth)):
    host = get_host()
    async with SUBS_LOCK:
        snap_subs = dict(SUBS)
    async with LINKS_LOCK:
        snap_links = dict(LINKS)
    result = []
    for sid, s in snap_subs.items():
        link_ids = s.get("link_ids", [])
        node_link_ids = s.get("node_link_ids", [])
        foreign_links = s.get("foreign_links", [])
        active_count = sum(1 for lid in link_ids if is_link_allowed(snap_links.get(lid)))
        total_used = sum(snap_links[lid].get("used_bytes", 0) for lid in link_ids if lid in snap_links)
        total_used += sum(int(fl.get("used_bytes") or 0) for fl in foreign_links)
        result.append({
            "sub_id": sid,
            **s,
            "node_link_ids": node_link_ids,
            "foreign_links": foreign_links,
            "password_hash": None,
            "has_password": s.get("password_hash") is not None,
            "links_count": len(link_ids) + len(node_link_ids) + len(foreign_links),
            "active_count": active_count + len(foreign_links),
            "total_used_bytes": total_used,
            "total_used_fmt": fmt_bytes(total_used),
            "public_url": f"https://{host}/p/{s['uuid_key']}",
            "sub_url": f"https://{host}/sub-group/{s['uuid_key']}",
        })
    result.sort(key=lambda x: x["created_at"], reverse=True)
    return {"subs": result}

@app.patch("/api/subs/{sub_id}")
async def update_sub(sub_id: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    async with SUBS_LOCK:
        if sub_id not in SUBS:
            raise HTTPException(status_code=404, detail="sub not found")
        s = SUBS[sub_id]
        if "name" in body:
            s["name"] = str(body["name"])[:60]
        if "desc" in body:
            s["desc"] = str(body["desc"])[:200]
        if "password" in body:
            pw = str(body["password"]).strip()
            s["password_hash"] = hash_password(pw) if pw else None
        if "link_ids" in body:
            s["link_ids"] = list(body["link_ids"])
        if "node_link_ids" in body:
            s["node_link_ids"] = [str(x) for x in body["node_link_ids"] if "::" in str(x)]
        if "foreign_links" in body:
            fl = body["foreign_links"] if isinstance(body["foreign_links"], list) else []
            clean = []
            for it in fl:
                if not isinstance(it, dict) or not it.get("vless_link"):
                    continue
                clean.append({
                    "key": str(it.get("key") or "")[:120],
                    "label": str(it.get("label") or "کانفیگ")[:60],
                    "vless_link": str(it.get("vless_link"))[:2000],
                    "used_bytes": int(it.get("used_bytes") or 0),
                    "source": str(it.get("source") or "")[:60],
                })
            s["foreign_links"] = clean
    asyncio.create_task(save_state())
    return {"ok": True}

@app.delete("/api/subs/{sub_id}")
async def delete_sub(sub_id: str, _=Depends(require_auth)):
    async with SUBS_LOCK:
        if sub_id not in SUBS:
            raise HTTPException(status_code=404, detail="sub not found")
        name = SUBS[sub_id].get("name", sub_id)
        del SUBS[sub_id]
    async with LINKS_LOCK:
        for link in LINKS.values():
            if link.get("sub_id") == sub_id:
                link["sub_id"] = None
    asyncio.create_task(save_state())
    log_activity("sub", f"گروه «{name}» حذف شد", "warn")
    return {"ok": True, "deleted": sub_id}

@app.post("/api/subs/{sub_id}/links")
async def assign_link_to_sub(sub_id: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    link_id = str(body.get("link_id", ""))
    action = str(body.get("action", "add"))
    async with SUBS_LOCK:
        if sub_id not in SUBS:
            raise HTTPException(status_code=404, detail="sub not found")
        s = SUBS[sub_id]
        ids = s.setdefault("link_ids", [])
        if action == "add":
            if link_id not in ids:
                ids.append(link_id)
        else:
            if link_id in ids:
                ids.remove(link_id)
    async with LINKS_LOCK:
        if link_id in LINKS:
            LINKS[link_id]["sub_id"] = sub_id if action == "add" else None
    asyncio.create_task(save_state())
    return {"ok": True}

# ── مدیریت گروه از راه دور (توسط پنل مرکزی روی این نود) ──────────────────────
@app.patch("/api/node/subs/{sub_id}")
async def node_update_sub(sub_id: str, request: Request, key_id: str = Depends(require_node_key)):
    peer = await _require_node_manage(key_id)
    result = await update_sub(sub_id, request, None)
    log_activity("node", f"گروه {sub_id[:8]} از راه دور توسط «{peer}» ویرایش شد", "warn")
    return result

@app.delete("/api/node/subs/{sub_id}")
async def node_delete_sub(sub_id: str, key_id: str = Depends(require_node_key)):
    peer = await _require_node_manage(key_id)
    result = await delete_sub(sub_id, None)
    log_activity("node", f"گروه {sub_id[:8]} از راه دور توسط «{peer}» حذف شد", "err")
    return result

@app.post("/api/node/subs/{sub_id}/links")
async def node_assign_link_to_sub(sub_id: str, request: Request, key_id: str = Depends(require_node_key)):
    await _require_node_manage(key_id)
    return await assign_link_to_sub(sub_id, request, None)

# ── Public sub-group subscription file ───────────────────────────────────────
@app.get("/sub-group/{uuid_key}")
async def sub_group_subscription(uuid_key: str, request: Request):
    async with SUBS_LOCK:
        sub = next((s for s in SUBS.values() if s.get("uuid_key") == uuid_key), None)
    if not sub:
        raise HTTPException(status_code=404, detail="not found")
    if sub.get("password_hash"):
        pw = request.query_params.get("pw", "")
        if hash_password(pw) != sub["password_hash"]:
            raise HTTPException(status_code=403, detail="wrong password")
    host = get_host()
    link_ids = sub.get("link_ids", [])
    node_link_ids = sub.get("node_link_ids", [])
    async with LINKS_LOCK:
        lines = []
        allowed_links = []
        for lid in link_ids:
            link = LINKS.get(lid)
            if link and is_link_allowed(link):
                lines.append(generate_share_link(lid, host, remark=f"RVG-{link['label']}", protocol=link.get("protocol", DEFAULT_PROTOCOL)))
                allowed_links.append(link)
        total_used = sum(l.get("used_bytes", 0) for l in allowed_links)
        total_limit = sum(l.get("limit_bytes", 0) for l in allowed_links)
        expiries = [l["expires_at"] for l in allowed_links if l.get("expires_at")]
    if node_link_ids:
        async with NODES_LOCK:
            nodes_snap = {nid: dict(n) for nid, n in NODES.items()}
        needed_nodes = list({ref.split("::", 1)[0] for ref in node_link_ids if "::" in ref})
        needed_nodes = [nid for nid in needed_nodes if nid in nodes_snap]
        snapshots = await asyncio.gather(
            *(_fetch_node_snapshot(nid, nodes_snap[nid], fresh=True) for nid in needed_nodes),
            return_exceptions=True,
        )
        snap_by_node = dict(zip(needed_nodes, snapshots))
        for ref in node_link_ids:
            if "::" not in ref:
                continue
            nid, uid = ref.split("::", 1)
            snap = snap_by_node.get(nid)
            if not snap or isinstance(snap, Exception):
                continue
            node_link = next((l for l in (snap.get("links") or []) if l.get("uuid") == uid), None)
            if not node_link or not node_link.get("vless_link"):
                continue
            if not node_link.get("active", True):
                continue
            if node_link.get("expired"):
                continue
            lb = node_link.get("limit_bytes", 0)
            if lb > 0 and node_link.get("used_bytes", 0) >= lb:
                continue
            lines.append(node_link["vless_link"])
            total_used += node_link.get("used_bytes", 0)
            total_limit += node_link.get("limit_bytes", 0)
            if node_link.get("expires_at"):
                expiries.append(node_link["expires_at"])
    for fl in sub.get("foreign_links", []):
        vl = fl.get("vless_link")
        if not vl:
            continue
        lines.append(vl)
        total_used += int(fl.get("used_bytes") or 0)
    nearest_exp = min(expiries) if expiries else None
    content = base64.b64encode("\n".join(lines).encode()).decode()
    headers = build_sub_headers(f"پنل: {sub['name']}", total_used, total_limit, nearest_exp)
    return Response(content=content, media_type="text/plain", headers=headers)

# ── Auth endpoints ────────────────────────────────────────────────────────────
@app.post("/api/login")
async def api_login(request: Request):
    body = await request.json()
    ip = client_ip(request)
    if hash_password(str(body.get("password", ""))) != AUTH["password_hash"]:
        log_activity("auth", f"تلاش ورود ناموفق از {ip}", "err")
        raise HTTPException(status_code=401, detail="رمز عبور اشتباه است")
    token = await create_session()
    log_activity("auth", f"ورود موفق به پنل از {ip}", "ok")
    resp = JSONResponse({"ok": True})
    resp.set_cookie(SESSION_COOKIE, token, max_age=SESSION_TTL, httponly=True, samesite="lax", path="/")
    return resp

@app.post("/api/logout")
async def api_logout(request: Request):
    await destroy_session(request.cookies.get(SESSION_COOKIE))
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(SESSION_COOKIE, path="/")
    return resp

@app.get("/api/me")
async def api_me(request: Request):
    return {"authenticated": await is_valid_session(request.cookies.get(SESSION_COOKIE))}

@app.post("/api/change-password")
async def api_change_password(request: Request, token=Depends(require_auth)):
    body = await request.json()
    if hash_password(str(body.get("current_password", ""))) != AUTH["password_hash"]:
        raise HTTPException(status_code=400, detail="رمز فعلی اشتباه است")
    new = str(body.get("new_password", ""))
    if len(new) < 4:
        raise HTTPException(status_code=400, detail="رمز جدید باید حداقل ۴ کاراکتر باشد")
    AUTH["password_hash"] = hash_password(new)
    async with SESSIONS_LOCK:
        SESSIONS.clear()
        SESSIONS[token] = time.time() + SESSION_TTL
    await save_state()
    log_activity("auth", "رمز عبور پنل تغییر کرد", "ok")
    return {"ok": True}
# ── Backup / Restore ──────────────────────────────────────────────────────────
@app.get("/api/backup/export")
async def backup_export(_=Depends(require_auth)):
    async with LINKS_LOCK:
        links_snap = dict(LINKS)
    async with SUBS_LOCK:
        subs_snap = dict(SUBS)
    async with NODE_KEYS_LOCK:
        node_keys_snap = dict(NODE_KEYS)
    async with NODES_LOCK:
        nodes_snap = dict(NODES)
    data = {
        "kind": "rvg-backup",
        "version": "9.2",
        "exported_at": datetime.now().isoformat(),
        "host": get_host(),
        "links": links_snap,
        "subs": subs_snap,
        "node_keys": node_keys_snap,
        "nodes": nodes_snap,
        "password_hash": AUTH["password_hash"],
    }
    content = json.dumps(data, ensure_ascii=False, indent=2)
    filename = f"rvg-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    log_activity("system", "فایل بکاپ دانلود شد", "info")
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/backup/import")
async def backup_import(request: Request, _=Depends(require_auth)):
    body = await request.json()
    data = body.get("data")
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="فایل بکاپ نامعتبر است")

    new_links = data.get("links")
    new_subs = data.get("subs")
    new_pw_hash = data.get("password_hash")
    keep_password = bool(body.get("keep_current_password", True))

    if not isinstance(new_links, dict) or not isinstance(new_subs, dict):
        raise HTTPException(status_code=400, detail="ساختار فایل بکاپ نامعتبر است")

    # همه‌ی instance‌های MTProto رو قبل از جایگزینی داده‌ها متوقف کن
    try:
        await mtproto.stop_all()
    except Exception as exc:
        logger.warning(f"توقف MTProto قبل از ایمپورت ناموفق بود: {exc}")

    async with LINKS_LOCK:
        LINKS.clear()
        LINKS.update(new_links)
    async with SUBS_LOCK:
        SUBS.clear()
        SUBS.update(new_subs)

    # نودها و کلیدهای نود اختیاری‌اند (بکاپ‌های قدیمی این کلیدها را ندارند)
    new_node_keys = data.get("node_keys")
    if isinstance(new_node_keys, dict):
        async with NODE_KEYS_LOCK:
            NODE_KEYS.clear()
            NODE_KEYS.update(new_node_keys)
    new_nodes = data.get("nodes")
    if isinstance(new_nodes, dict):
        async with NODES_LOCK:
            NODES.clear()
            for nid, n in new_nodes.items():
                if isinstance(n, dict):
                    NODES[nid] = _normalize_node(n)
        _NODE_CACHE.clear()

    if not keep_password and new_pw_hash:
        AUTH["password_hash"] = new_pw_hash
        async with SESSIONS_LOCK:
            SESSIONS.clear()
            # سشن فعلی رو نگه می‌داریم که کاربر لاگ‌اوت نشه
            token = request.cookies.get(SESSION_COOKIE)
            if token:
                SESSIONS[token] = time.time() + SESSION_TTL

    await save_state()

    try:
        await _restart_mtproto_instances()
    except Exception as exc:
        logger.error(f"راه‌اندازی مجدد MTProto بعد از ایمپورت ناموفق بود: {exc}")

    log_activity("system", "بکاپ با موفقیت روی پنل بازیابی شد", "ok")
    return {"ok": True, "links_count": len(LINKS), "subs_count": len(SUBS), "nodes_count": len(NODES)}
    

# ── Stats ─────────────────────────────────────────────────────────────────────
@app.get("/stats")
async def get_stats(_=Depends(require_auth)):
    async with LINKS_LOCK:
        snap = dict(LINKS)
    return {
        "active_connections": len(connections),
        "total_traffic_mb": round(stats["total_bytes"] / (1024 ** 2), 2),
        "total_requests": stats["total_requests"],
        "total_errors": stats["total_errors"],
        "uptime": uptime(),
        "timestamp": datetime.now().isoformat(),
        "hourly": dict(hourly_traffic),
        "recent_errors": list(error_logs)[-10:],
        "links_count": len(snap),
        "active_links": sum(1 for l in snap.values() if is_link_allowed(l)),
        "expired_links": sum(1 for l in snap.values() if is_link_expired(l)),
        "subs_count": len(SUBS),
    }

@app.get("/api/bot-tcp-proxy/domains")
async def api_bot_tcp_proxy_domains(_=Depends(require_auth)):
    return {"domains": bottokentcpproxy.get_known_domains()}

@app.post("/api/bot-tcp-proxy/start")
async def api_bot_tcp_proxy_start(request: Request, _=Depends(require_auth)):
    body = await request.json()
    token = str(body.get("token", "")).strip()
    # هر لینک MTProto پورت جدای خودش رو داره (per-instance)، پس پورت باید
    # از ورودی کاربر/فرانت (لینکی که TCP Proxy براش ساخته می‌شه) بیاد.
    uid = str(body.get("uuid") or "").strip()
    port = body.get("port")
    if port is None and uid:
        async with LINKS_LOCK:
            link = LINKS.get(uid)
            port = link.get("mtproto_port") if link else None
    if port is None:
        raise HTTPException(status_code=400, detail="پورت (یا uuid لینک) مشخص نشده")
    port = int(port)
    reachable_domains = body.get("reachable_domains") or []
    try:
        bottokentcpproxy.start_job(token, port, reachable_domains=reachable_domains)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    log_activity("system", "جست‌وجوی TCP Proxy آغاز شد", "info")
    return {"ok": True}

@app.post("/api/mtproto/fix-proxy")
async def api_mtproto_fix_proxy(request: Request, _=Depends(require_auth)):
    """راه مستقیم برای درست‌کردن لینک‌های MTProto بدون TCP Proxy:
    توکن Railway رو (اگه فرستاده بشه) ذخیره می‌کنه و بعد برای همه‌ی لینک‌های
    MTProto که هنوز TCP Proxy عمومی ندارن، یکی می‌سازه — بدون نیاز به طی‌کردن
    کل فرآیند جست‌وجوی دامنه."""
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    token = str(body.get("token", "")).strip()
    if token:
        bottokentcpproxy.save_token(token)

    if not bottokentcpproxy.has_saved_token():
        raise HTTPException(status_code=400, detail="توکن Railway ذخیره نشده — آن را در همین درخواست بفرستید")

    async with LINKS_LOCK:
        targets = [
            (uid, d.get("mtproto_port"), d.get("label", ""))
            for uid, d in LINKS.items()
            if d.get("protocol") == "mtproto" and not d.get("mtproto_public_host")
        ]

    fixed, failed = [], []
    for uid, port, label in targets:
        if not port:
            failed.append({"uuid": uid, "label": label, "error": "پورت داخلی ندارد (instance اجرا نشده)"})
            continue
        try:
            pub = await bottokentcpproxy.create_public_proxy_for_port(int(port))
        except Exception as exc:
            failed.append({"uuid": uid, "label": label, "error": str(exc)})
            continue
        async with LINKS_LOCK:
            if uid in LINKS:
                LINKS[uid]["mtproto_public_host"] = pub["domain"]
                LINKS[uid]["mtproto_public_port"] = pub["port"]
                LINKS[uid]["mtproto_proxy_id"] = pub["id"]
                LINKS[uid]["mtproto_public_pending"] = False
        fixed.append({
            "uuid": uid, "label": label,
            "host": pub["domain"], "port": pub["port"],
            "link": generate_share_link(uid, get_host(), remark=f"RVG-{label}", protocol="mtproto"),
        })
        log_activity("link", f"TCP Proxy عمومی «{label}» ساخته شد ({pub['domain']}:{pub['port']})", "ok")

    asyncio.create_task(save_state())
    return {"ok": True, "fixed": fixed, "failed": failed}


@app.get("/api/mtproto/{uid}/stats")
async def api_mtproto_stats(uid: str, _=Depends(require_auth)):
    """آمار خام خود باینری mtproto-proxy برای این لینک.
    اگه total_special_connections صفر بمونه حتی بعد از تلاش برای اتصال، یعنی
    هیچ پکتی به پروسه نمی‌رسه (مشکل مسیر شبکه/TCP Proxy). اگه بالا بره ولی
    اتصال برقرار نشه، یعنی پکت می‌رسه و مشکل در handshake/سکرت است."""
    async with LINKS_LOCK:
        if uid not in LINKS:
            raise HTTPException(status_code=404, detail="link not found")
    return await mtproto.get_stats(uid)


@app.post("/api/zeus-proxy/create")
async def api_zeus_proxy_create(request: Request, _=Depends(require_auth)):
    """ساخت پروکسی Zeus با پشتیبانی از محدودیت حجم، انقضا و اتصال per IP."""
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    token = str(body.get("token", "")).strip()
    # ── کانفیگ‌های اختیاری ──
    traffic_limit_gb = body.get("traffic_limit_gb")
    expires_days = body.get("expires_days")
    max_connections_per_ip = body.get("max_connections_per_ip")
    try:
        result = await zeussocks5.create_zeus_proxy(
            token or None,
            traffic_limit_gb=float(traffic_limit_gb) if traffic_limit_gb is not None else None,
            expires_days=int(expires_days) if expires_days is not None else None,
            max_connections_per_ip=int(max_connections_per_ip) if max_connections_per_ip is not None else None,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"ساخت پروکسی Zeus ناموفق بود: {exc}")
    log_activity("system", f"پروکسی Zeus ساخته شد ({result['domain']}:{result['public_port']})", "ok")
    return {"ok": True, **result}

@app.get("/api/zeus-proxy/status")
async def api_zeus_proxy_status(_=Depends(require_auth)):
    return zeussocks5.get_zeus_status()

@app.post("/api/zeus-proxy/delete")
async def api_zeus_proxy_delete(_=Depends(require_auth)):
    await zeussocks5.delete_zeus_proxy()
    log_activity("system", "پروکسی Zeus حذف شد", "warn")
    return {"ok": True}

@app.post("/api/zeus-proxy/config")
async def api_zeus_proxy_config(request: Request, _=Depends(require_auth)):
    """تغییر کانفیگ‌های پروکسی Zeus (حجم/انقضا/اتصال per IP) بدون ری‌استارت."""
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    traffic_limit_gb = body.get("traffic_limit_gb")
    expires_days = body.get("expires_days")
    max_connections_per_ip = body.get("max_connections_per_ip")
    cfg = zeussocks5.update_zeus_config(
        traffic_limit_gb=float(traffic_limit_gb) if traffic_limit_gb is not None else None,
        expires_days=int(expires_days) if expires_days is not None else None,
        max_connections_per_ip=int(max_connections_per_ip) if max_connections_per_ip is not None else None,
    )
    log_activity("system", f"کانفیگ پروکسی Zeus آپدیت شد", "ok")
    return {"ok": True, "config": cfg}
@app.post("/api/bot-tcp-proxy/stop")
async def api_bot_tcp_proxy_stop(_=Depends(require_auth)):
    stopped = bottokentcpproxy.stop_job()
    if stopped:
        log_activity("system", "جست‌وجوی TCP Proxy متوقف شد", "warn")
    return {"ok": True, "stopped": stopped}

@app.get("/api/bot-tcp-proxy/status")
async def api_bot_tcp_proxy_status(_=Depends(require_auth)):
    return bottokentcpproxy.get_status()

@app.post("/api/bot-tcp-proxy/attach")
async def api_bot_tcp_proxy_attach(request: Request, _=Depends(require_auth)):
    """وقتی جست‌وجو یک دامنه‌ی سالم پیدا کرد (phase=='done')، این دامنه/پورت به‌عنوان
    TCP Proxy عمومیِ همون لینک MTProto مشخص‌شده (با uuid) ثبت می‌شود. اگر uuid
    داده نشده باشه و هیچ لینک MTProtoای وجود نداشته باشه، یکی پیش‌فرض ساخته می‌شود."""
    status = bottokentcpproxy.get_status()
    chosen = status.get("result")
    if status.get("phase") != "done" or not chosen:
        raise HTTPException(status_code=409, detail="هنوز نتیجه‌ای برای ساخت پروکسی آماده نیست")

    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    label = str(body.get("label") or "").strip() or f"TCP-{chosen['domain'].split('.')[0]}"
    uid = str(body.get("uuid") or "").strip() or None

    attached_link = None
    if not uid:
        async with LINKS_LOCK:
            existing = next((u for u, d in LINKS.items() if d.get("protocol") == "mtproto"), None)
        uid = existing

    if not uid:
        uid = generate_uuid()
        secret = mtproto.generate_secret()
        link_data = {
            "label": label, "limit_bytes": 0, "used_bytes": 0,
            "created_at": datetime.now().isoformat(),
            "alpn": "h2,http/1.1", "fingerprint": "chrome", "active": True,
            "expires_at": None, "note": "", "is_default": False, "sub_id": None,
            "protocol": "mtproto", "ad_tag": None, "mtproto_secret": secret,
        }
        async with LINKS_LOCK:
            LINKS[uid] = link_data
        try:
            inst = await mtproto.start_instance(uid, secret=secret, ad_tag=None)
        except Exception as exc:
            logger.error(f"راه‌اندازی mtproto ناموفق بود: {exc}")
            raise HTTPException(status_code=502, detail=f"راه‌اندازی MTProto ناموفق بود: {exc}")
        async with LINKS_LOCK:
            LINKS[uid]["mtproto_port"] = inst["port"]
            LINKS[uid]["mtproto_secret"] = inst["secret"]
        attached_link = {"uuid": uid, "label": label}

    old_proxy_id = None
    async with LINKS_LOCK:
        link = LINKS.get(uid)
        if link is None:
            raise HTTPException(status_code=404, detail="لینک پیدا نشد")
        old_proxy_id = link.get("mtproto_proxy_id")
        link["mtproto_public_host"] = chosen["domain"]
        link["mtproto_public_port"] = chosen["port"]
        link["mtproto_proxy_id"] = chosen["id"]
        link["mtproto_public_pending"] = False
        cur_label = link.get("label", label)

    if old_proxy_id and old_proxy_id != chosen["id"]:
        asyncio.create_task(bottokentcpproxy.delete_public_proxy(old_proxy_id))

    asyncio.create_task(save_state())
    host = get_host()
    share_link = generate_share_link(uid, host, remark=f"RVG-{cur_label}", protocol="mtproto")
    if not attached_link:
        attached_link = {"uuid": uid, "label": cur_label}
    log_activity(
        "link",
        f"TCP Proxy عمومی «{cur_label}» با دامنه‌ی {chosen['domain']}:{chosen['port']} تنظیم شد",
        "ok",
    )
    return {
        "ok": True,
        "result": chosen,
        "attached_link": attached_link,
        "share_link": share_link,
    }


@app.post("/api/domain-gen/start")
async def api_domain_gen_start(request: Request, _=Depends(require_auth)):
    body = await request.json()
    token = str(body.get("token", "")).strip()
    port = int(body.get("port") or CONFIG["port"])
    count = int(body.get("count") or 10)
    try:
        botgeneratedomin.start_job(token, port, target_count=count)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    log_activity("system", f"ساخت {count} دامنه آغاز شد", "info")
    return {"ok": True}

@app.post("/api/domain-gen/stop")
async def api_domain_gen_stop(_=Depends(require_auth)):
    stopped = botgeneratedomin.stop_job()
    if stopped:
        log_activity("system", "ساخت دامنه متوقف شد", "warn")
    return {"ok": True, "stopped": stopped}

@app.get("/api/domain-gen/status")
async def api_domain_gen_status(_=Depends(require_auth)):
    return botgeneratedomin.get_status()

# ── Activity Logs ─────────────────────────────────────────────────────────────
@app.get("/api/activity")
async def get_activity(_=Depends(require_auth)):
    return {"logs": list(activity_logs)[-150:]}

# ── Live connections (with IP) ────────────────────────────────────────────────
@app.get("/api/connections")
async def get_connections(_=Depends(require_auth)):
    async with LINKS_LOCK:
        snap = dict(LINKS)
    grouped: dict[str, dict] = {}
    for conn_id, c in connections.items():
        ip = c.get("ip", "نامشخص")
        link = snap.get(c.get("uuid"))
        label = link.get("label") if link else "نامشخص"
        g = grouped.get(ip)
        if g is None:
            g = {
                "ip": ip,
                "sessions": 0,
                "bytes": 0,
                "labels": set(),
                "transports": set(),
                "first_connected_at": c.get("connected_at"),
                "last_connected_at": c.get("connected_at"),
            }
            grouped[ip] = g
        g["sessions"] += 1
        g["bytes"] += c.get("bytes", 0)
        g["labels"].add(label)
        g["transports"].add(c.get("transport", "vless-ws"))
        ca = c.get("connected_at")
        if ca:
            if not g["first_connected_at"] or ca < g["first_connected_at"]:
                g["first_connected_at"] = ca
            if not g["last_connected_at"] or ca > g["last_connected_at"]:
                g["last_connected_at"] = ca
    for uid, link in snap.items():
        if link.get("protocol") == "mtproto":
            label = link.get("label", "نامشخص")
            for c in mtproto.get_instance_connections(uid):
                ip = c["ip"]
                g = grouped.get(ip)
                if g is None:
                    g = {
                        "ip": ip, "sessions": 0, "bytes": 0,
                        "labels": set(), "transports": set(),
                        "first_connected_at": None, "last_connected_at": None,
                    }
                    grouped[ip] = g
                g["sessions"] += 1
                g["labels"].add(label)
                g["transports"].add("mtproto")
    result = []
    for ip, g in grouped.items():
        result.append({
            "ip": ip,
            "sessions": g["sessions"],
            "labels": sorted(g["labels"]),
            "label": " · ".join(sorted(g["labels"])) if g["labels"] else "نامشخص",
            "transports": sorted(g["transports"]),
            "bytes": g["bytes"],
            "bytes_fmt": fmt_bytes(g["bytes"]),
            "connected_at": g["first_connected_at"],
            "last_connected_at": g["last_connected_at"],
        })
    result.sort(key=lambda x: x.get("last_connected_at") or "", reverse=True)
    return {
        "connections": result,
        "count": len(result),
        "raw_count": len(connections),
    }

# ── Link Management ───────────────────────────────────────────────────────────
async def _create_link_core(body: dict) -> dict:
    label = (body.get("label") or "لینک جدید").strip()[:60]
    lv = float(body.get("limit_value") or 0)
    lu = body.get("limit_unit") or "GB"
    limit_bytes = 0 if lv <= 0 else parse_size_to_bytes(lv, lu)
    exp_days = int(body.get("expires_days") or 0)
    expires_at = (datetime.now() + timedelta(days=exp_days)).isoformat() if exp_days > 0 else None
    note = (body.get("note") or "").strip()[:200]
    sub_id = body.get("sub_id") or None
    protocol = body.get("protocol") or DEFAULT_PROTOCOL
    if protocol not in PROTOCOLS:
        protocol = DEFAULT_PROTOCOL

    alpn_val = str(body.get("alpn") or "h2,http/1.1").strip()[:60]
    fp_val = str(body.get("fingerprint") or "chrome").strip()[:20]
    if fp_val not in ("chrome", "firefox", "ios"):
        fp_val = "chrome"

    uid = generate_uuid()
    link_data = {
        "label": label,
        "limit_bytes": limit_bytes,
        "used_bytes": 0,
        "created_at": datetime.now().isoformat(),
        "alpn": alpn_val,
        "fingerprint": fp_val,
        "active": True,
        "expires_at": expires_at,
        "note": note,
        "is_default": False,
        "sub_id": sub_id,
        "protocol": protocol,
        "ad_tag": None,
    }

    if protocol == "mtproto":
        raw_port = body.get("mtproto_port")
        manual_port = int(raw_port) if raw_port not in (None, "", 0, "0") else None
        if manual_port is not None and not (1 <= manual_port <= 65535):
            raise HTTPException(status_code=400, detail="شماره پورت نامعتبر است")
        raw_domain = (body.get("mtproto_domain") or "").strip()
        domain = mtproto.sanitize_domain(raw_domain)
        try:
            inst = await mtproto.start_instance(
                uid,
                domain=domain,
                preferred_port=manual_port,
                force_port=manual_port is not None,
                ad_tag=None,
            )
        except RuntimeError as exc:
            logger.error(f"راه‌اندازی MTProto ناموفق برای {uid[:8]}: {exc}")
            raise HTTPException(status_code=409, detail=str(exc))
        except Exception as exc:
            logger.error(f"راه‌اندازی MTProto ناموفق برای {uid[:8]}: {exc}")
            raise HTTPException(status_code=502, detail=f"راه‌اندازی MTProto ناموفق: {exc}")
        link_data["mtproto_port"] = inst["port"]
        link_data["mtproto_secret"] = inst["secret"]
        link_data["mtproto_domain"] = inst["domain"]
        link_data["mtproto_manual_port"] = manual_port is not None

        # ── آدرس عمومی دستی ──────────────────────────────────────────────────
        # اگه کاربر TCP Proxy رو خودش از داشبورد Railway ساخته باشه، دامنه و پورت
        # عمومیش رو مستقیم اینجا وارد می‌کنه (مثل proxy.rlwy.net:12345). در این
        # حالت اصلاً سراغ ساخت خودکار/توکن نمی‌ریم.
        pub_host = (body.get("mtproto_public_host") or "").strip()
        raw_pub_port = body.get("mtproto_public_port")
        try:
            pub_port = int(raw_pub_port) if raw_pub_port not in (None, "", 0, "0") else None
        except (TypeError, ValueError):
            pub_port = None
        if pub_host and pub_port:
            link_data["mtproto_public_host"] = pub_host
            link_data["mtproto_public_port"] = pub_port
            link_data["mtproto_public_pending"] = False
        elif bottokentcpproxy.has_saved_token():
            link_data["mtproto_public_pending"] = True
            asyncio.create_task(_attach_mtproto_public_proxy(uid, inst["port"], label))
        else:
            # بدون توکن Railway هیچ TCP Proxy عمومی ساخته نمی‌شه، یعنی این لینک
            # از بیرون اصلاً قابل دسترس نیست. قبلاً این حالت بی‌صدا رد می‌شد و
            # کاربر یه لینک ظاهراً سالم ولی کاملاً مرده می‌گرفت.
            link_data["mtproto_public_pending"] = False
            logger.error(
                f"MTProto[{uid[:8]}]: توکن Railway ذخیره نشده — TCP Proxy عمومی ساخته نشد "
                f"و این لینک از بیرون قابل استفاده نیست. ابتدا از مودال «Bot TCP Proxy» "
                f"توکن Railway را وارد کنید."
            )
            log_activity(
                "link",
                f"«{label}» ساخته شد ولی TCP Proxy ندارد (توکن Railway ذخیره نشده) — لینک کار نمی‌کند",
                "err",
            )

    if protocol == "shadowsocks":
        ss_cipher = body.get("ss_cipher") or DEFAULT_CIPHER
        if ss_cipher not in CIPHERS:
            ss_cipher = DEFAULT_CIPHER
        link_data["ss_cipher"] = ss_cipher
        link_data["ss_password"] = secrets.token_urlsafe(16)
    
    async with LINKS_LOCK:
        LINKS[uid] = link_data

    if sub_id:
        async with SUBS_LOCK:
            if sub_id in SUBS:
                ids = SUBS[sub_id].setdefault("link_ids", [])
                if uid not in ids:
                    ids.append(uid)

    asyncio.create_task(save_state())
    log_activity("link", f"کانفیگ «{label}» ساخته شد", "ok")
    host = get_host()
    return {
        "uuid": uid,
        **LINKS[uid],
        "expired": False,
        "vless_link": generate_share_link(uid, host, remark=f"RVG-{label}", protocol=protocol),
        "sub_url": f"https://{host}/sub/{uid}",
    }

@app.post("/api/links")
async def create_link(request: Request, _=Depends(require_auth)):
    body = await request.json()
    return await _create_link_core(body)

@app.post("/api/node/links")
async def node_create_link(request: Request, key_id: str = Depends(require_node_key)):
    await _require_node_manage(key_id)
    body = await request.json()
    # sub_id در اینجا به گروهِ محلیِ همین نود اشاره دارد (نه پنل مرکزی)؛ اگر معتبر نباشد نادیده گرفته می‌شود
    return await _create_link_core(body)

@app.get("/api/links")
async def list_links(_=Depends(require_auth)):
    host = get_host()
    async with LINKS_LOCK:
        snap = dict(LINKS)
    result = []
    for uid, d in snap.items():
        proto = d.get("protocol", DEFAULT_PROTOCOL)
        extra = {}
        if proto == "mtproto":
            # هر لینک MTProto حالا instance/پورت/TCP-Proxy مستقل خودش رو داره
            extra = {
                "mtproto_public_host": d.get("mtproto_public_host"),
                "mtproto_public_port": d.get("mtproto_public_port"),
                "mtproto_public_pending": bool(
                    d.get("mtproto_public_pending")
                    or (not d.get("mtproto_manual_port") and bottokentcpproxy.has_saved_token()
                        and not d.get("mtproto_public_host"))
                ),
            }
        result.append({
            "uuid": uid,
            **d,
            **extra,
            "protocol": proto,
            "expired": is_link_expired(d),
            "vless_link": generate_share_link(uid, host, remark=f"RVG-{d['label']}", protocol=proto),
            "sub_url": f"https://{host}/sub/{uid}",
        })
    result.sort(key=lambda x: x["created_at"], reverse=True)
    return {"links": result}

@app.patch("/api/links/{uid}")
async def update_link(uid: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    mtproto_action = None
    new_sub = "UNCHANGED"

    async with LINKS_LOCK:
        if uid not in LINKS:
            raise HTTPException(status_code=404, detail="link not found")
        link = LINKS[uid]
        old_sub = link.get("sub_id")
        label = link.get("label")

        if "active" in body:
            new_active = bool(body["active"])
            changed = new_active != link.get("active", True)
            link["active"] = new_active
            log_activity("link", f"کانفیگ «{label}» {'فعال' if new_active else 'غیرفعال'} شد", "ok" if new_active else "warn")
            if changed and link.get("protocol") == "mtproto":
                mtproto_action = ("start" if new_active else "stop", dict(link))

        if "label" in body:
            link["label"] = str(body["label"])[:60]
        # ── ویرایش دستی آدرس عمومی MTProto ────────────────────────────────────
        # برای وقتی که TCP Proxy رو خودت از داشبورد Railway ساختی و می‌خوای
        # دامنه/پورت عمومیش رو روی یک لینک موجود ست کنی، بدون ساخت دوباره.
        if "mtproto_public_host" in body:
            ph = (body.get("mtproto_public_host") or "").strip()
            link["mtproto_public_host"] = ph or None
        if "mtproto_public_port" in body:
            raw_pp = body.get("mtproto_public_port")
            try:
                link["mtproto_public_port"] = (
                    int(raw_pp) if raw_pp not in (None, "", 0, "0") else None
                )
            except (TypeError, ValueError):
                link["mtproto_public_port"] = None
        if link.get("mtproto_public_host") and link.get("mtproto_public_port"):
            link["mtproto_public_pending"] = False
        if "note" in body:
            link["note"] = str(body["note"])[:200]
        if "reset_usage" in body and body["reset_usage"]:
            link["used_bytes"] = 0
            log_activity("link", f"مصرف کانفیگ «{label}» ریست شد", "info")
        if "limit_value" in body:
            lv = float(body.get("limit_value") or 0)
            lu = body.get("limit_unit") or "GB"
            link["limit_bytes"] = 0 if lv <= 0 else parse_size_to_bytes(lv, lu)
        if "expires_days" in body:
            ed = int(body["expires_days"] or 0)
            link["expires_at"] = (datetime.now() + timedelta(days=ed)).isoformat() if ed > 0 else None
        if "alpn" in body:
            alpn_val = str(body["alpn"]).strip()[:60]
            if alpn_val:
                link["alpn"] = alpn_val
        if "fingerprint" in body:
            fp_val = str(body["fingerprint"]).strip()
            link["fingerprint"] = fp_val if fp_val in ("chrome", "firefox", "ios") else "chrome"
        if any(k in body for k in ("label", "note", "limit_value", "expires_days", "alpn", "fingerprint")):
            log_activity("link", f"کانفیگ «{link['label']}» ویرایش شد", "info")
        new_sub = body.get("sub_id", "UNCHANGED")
        if new_sub != "UNCHANGED":
            link["sub_id"] = new_sub or None

    if new_sub != "UNCHANGED":
        async with SUBS_LOCK:
            if old_sub and old_sub in SUBS:
                ids = SUBS[old_sub].get("link_ids", [])
                if uid in ids:
                    ids.remove(uid)
            if new_sub and new_sub in SUBS:
                ids = SUBS[new_sub].setdefault("link_ids", [])
                if uid not in ids:
                    ids.append(uid)

    if mtproto_action:
        action, snap = mtproto_action
        if action == "stop":
            await mtproto.stop_instance(uid)
        else:
            try:
                old_port = snap.get("mtproto_port")
                inst = await mtproto.start_instance(
                    uid,
                    secret=snap.get("mtproto_secret"),
                    domain=snap.get("mtproto_domain", mtproto.DEFAULT_FAKE_TLS_DOMAIN),
                    preferred_port=snap.get("mtproto_port"),
                    force_port=snap.get("mtproto_manual_port", False),
                    ad_tag=snap.get("ad_tag"),
                )
                async with LINKS_LOCK:
                    if uid in LINKS:
                        LINKS[uid]["mtproto_port"] = inst["port"]
                        LINKS[uid]["mtproto_secret"] = inst["secret"]
                if (snap.get("mtproto_proxy_id") and inst["port"] != old_port
                        and not snap.get("mtproto_manual_port", False)):
                    asyncio.create_task(_reattach_mtproto_public_proxy(
                        uid, inst["port"], snap.get("mtproto_proxy_id"), snap.get("label", "")
                    ))
            except Exception as exc:
                logger.error(f"روشن کردن MTProto ناموفق برای {uid[:8]}: {exc}")
                async with LINKS_LOCK:
                    if uid in LINKS:
                        LINKS[uid]["active"] = False
                log_activity("link", f"روشن کردن پروکسی تلگرام «{label}» ناموفق بود", "err")
                asyncio.create_task(save_state())
                raise HTTPException(status_code=502, detail=f"روشن کردن پروکسی تلگرام ناموفق بود: {exc}")

    asyncio.create_task(save_state())
    return {"ok": True}
    
# ===== Endpoint جدید برای به‌روزرسانی ad_tag =====
@app.patch("/api/links/{uid}/ad-tag")
async def update_ad_tag(uid: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    ad_tag = str(body.get("ad_tag", "")).strip()
    if not ad_tag:
        raise HTTPException(status_code=400, detail="ad_tag نمی‌تواند خالی باشد")

    async with LINKS_LOCK:
        if uid not in LINKS:
            raise HTTPException(status_code=404, detail="link not found")
        link = LINKS[uid]
        if link.get("protocol") != "mtproto":
            raise HTTPException(status_code=400, detail="این کانفیگ MTProto نیست")
        link["ad_tag_status"] = "pending"   # ← جدید

    asyncio.create_task(_update_mtproto_ad_tag(uid, ad_tag))
    log_activity("link", f"درخواست به‌روزرسانی ad_tag برای «{link.get('label','')}» ثبت شد", "info")
    return {"ok": True, "message": "ad_tag در حال اعمال است، پروکسی ری‌استارت می‌شود"}


# اندپوینت جدید برای پول کردن وضعیت
@app.get("/api/links/{uid}/ad-tag/status")
async def get_ad_tag_status(uid: str, _=Depends(require_auth)):
    async with LINKS_LOCK:
        link = LINKS.get(uid)
        if not link:
            raise HTTPException(status_code=404, detail="link not found")
        return {
            "status": link.get("ad_tag_status", "idle"),
            "link": link.get("ad_tag_link"),
            "ad_tag": link.get("ad_tag"),
        }

@app.delete("/api/links/{uid}")
async def delete_link(uid: str, _=Depends(require_auth)):
    async with LINKS_LOCK:
        if uid not in LINKS:
            raise HTTPException(status_code=404, detail="link not found")
        label = LINKS[uid].get("label", uid)
        sub_id = LINKS[uid].get("sub_id")
        proto = LINKS[uid].get("protocol")
        proxy_id = LINKS[uid].get("mtproto_proxy_id")
        del LINKS[uid]
    if proto == "mtproto":
        await mtproto.stop_instance(uid)
        if proxy_id:
            asyncio.create_task(bottokentcpproxy.delete_public_proxy(proxy_id))
    if sub_id:
        async with SUBS_LOCK:
            if sub_id in SUBS:
                ids = SUBS[sub_id].get("link_ids", [])
                if uid in ids:
                    ids.remove(uid)
    asyncio.create_task(save_state())
    log_activity("link", f"کانفیگ «{label}» حذف شد", "err")
    return {"ok": True, "deleted": uid}

# ══════════════════════════════════════════════════════════════════════════════
# Node linking — inbound (این پنل صادرکننده‌ی کلید است)
# احراز هویت این بخش با هدر X-RVG-Node-Key انجام می‌شود، نه کوکی سشن.
# ══════════════════════════════════════════════════════════════════════════════
def _parse_parts(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {p.strip() for p in raw.split(",") if p.strip() in NODE_SHARE_PARTS}


@app.post("/api/node/handshake")
async def node_handshake(request: Request, key_id: str = Depends(require_node_key)):
    try:
        body = await request.json()
    except Exception:
        body = {}
    async with NODE_KEYS_LOCK:
        pw_hash = (NODE_KEYS.get(key_id) or {}).get("password_hash")
    if pw_hash:
        given = str(body.get("password") or "")
        if not given:
            raise HTTPException(status_code=401, detail="PASSWORD_REQUIRED")
        if hash_password(given) != pw_hash:
            raise HTTPException(status_code=401, detail="PASSWORD_INVALID")
    peer_host = str(body.get("host") or "").strip()[:120] or client_ip(request)
    async with NODE_KEYS_LOCK:
        entry = NODE_KEYS.get(key_id)
        if entry is not None:
            first_time = not entry.get("peer_host")
            entry["peer_host"] = peer_host
            label = entry.get("label") or key_id[:8]
        else:
            first_time, label = False, key_id[:8]
    if first_time:
        log_activity("node", f"پنل «{peer_host}» با کلید «{label}» متصل شد", "ok")
    async with LINKS_LOCK:
        links_count = len(LINKS)
    async with SUBS_LOCK:
        subs_count = len(SUBS)
    return {
        "ok": True,
        "host": get_host(),
        "version": get_current_version(),
        "links_count": links_count,
        "subs_count": subs_count,
    }


@app.get("/api/node/snapshot")
async def node_snapshot(request: Request, _key_id: str = Depends(require_node_key)):
    """فقط بخش‌هایی که هم درخواست شده و هم برای این کلید مجاز است برگردانده می‌شود."""
    parts = _parse_parts(request.query_params.get("parts"))
    async with NODE_KEYS_LOCK:
        entry = NODE_KEYS.get(_key_id) or {}
        allowed = {p for p in NODE_SHARE_PARTS if (entry.get("share") or {}).get(p, p != "logs")}
    parts &= allowed
    out: dict = {"host": get_host(), "version": get_current_version(), "parts": sorted(parts)}
    if "links" in parts:
        out["links"] = (await list_links(None))["links"]
    if "subs" in parts:
        out["subs"] = (await list_subs(None))["subs"]
    if "logs" in parts:
        out["logs"] = (await get_activity(None))["logs"][-60:]
    if parts & {"usage", "requests"}:
        s = await get_stats(None)
        stats_out = {
            "uptime": s["uptime"],
            "links_count": s["links_count"],
            "active_links": s["active_links"],
            "subs_count": s["subs_count"],
        }
        if "usage" in parts:
            stats_out["total_bytes"] = stats["total_bytes"]
            stats_out["total_traffic_mb"] = s["total_traffic_mb"]
            stats_out["hourly"] = s["hourly"]
            stats_out["active_connections"] = s["active_connections"]
        if "requests" in parts:
            stats_out["total_requests"] = s["total_requests"]
            stats_out["total_errors"] = s["total_errors"]
        out["stats"] = stats_out
    return out


async def _require_node_manage(key_id: str) -> str:
    async with NODE_KEYS_LOCK:
        entry = NODE_KEYS.get(key_id) or {}
        peer = entry.get("peer_host") or "نود"
        allowed = bool(entry.get("can_manage", False))
    if not allowed:
        raise HTTPException(status_code=403, detail="این کلید اجازه‌ی ویرایش/حذف کانفیگ را ندارد")
    return peer


@app.patch("/api/node/links/{uid}")
async def node_update_link(uid: str, request: Request, key_id: str = Depends(require_node_key)):
    peer = await _require_node_manage(key_id)
    result = await update_link(uid, request, None)
    log_activity("node", f"کانفیگ {uid[:8]} از راه دور توسط «{peer}» ویرایش شد", "warn")
    return result


@app.delete("/api/node/links/{uid}")
async def node_delete_link(uid: str, key_id: str = Depends(require_node_key)):
    peer = await _require_node_manage(key_id)
    result = await delete_link(uid, None)
    log_activity("node", f"کانفیگ {uid[:8]} از راه دور توسط «{peer}» حذف شد", "err")
    return result

# ══════════════════════════════════════════════════════════════════════════════
# Node linking — outbound (این پنل به نودهای دیگر وصل می‌شود)
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/api/nodes/keys")
async def list_node_keys(_=Depends(require_auth)):
    host = get_host()
    async with NODE_KEYS_LOCK:
        snap = dict(NODE_KEYS)
    out = []
    for key_id, e in snap.items():
        out.append({
            "key_id": key_id,
            "label": e.get("label", ""),
            "key": build_node_key(e.get("issued_host") or host, e.get("secret", "")),
            "created_at": e.get("created_at"),
            "revoked": bool(e.get("revoked")),
            "share": {p: bool((e.get("share") or {}).get(p, p != "logs")) for p in NODE_SHARE_PARTS},
            "can_manage": bool(e.get("can_manage", False)),
            "has_password": e.get("password_hash") is not None,
            "last_used_at": e.get("last_used_at"),
            "peer_host": e.get("peer_host"),
            "use_count": int(e.get("use_count", 0)),
        })
    out.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return {"keys": out, "host": host}


def _node_key_share(body_share) -> dict:
    """دسترسی‌های خواندن هر کلید؛ پیش‌فرض مثل خروجی نود: همه فعال جز لاگ‌ها."""
    src = body_share if isinstance(body_share, dict) else {}
    return {p: bool(src.get(p, p != "logs")) for p in NODE_SHARE_PARTS}


@app.post("/api/nodes/keys")
async def create_node_key(request: Request, _=Depends(require_auth)):
    try:
        body = await request.json()
    except Exception:
        body = {}
    label = (str(body.get("label") or "").strip() or f"کلید {len(NODE_KEYS) + 1}")[:60]
    share = _node_key_share(body.get("share"))
    can_manage = bool(body.get("can_manage", False))
    password = str(body.get("password") or "").strip()
    host = get_host()
    key_id = generate_uuid()
    secret = secrets.token_urlsafe(24)
    async with NODE_KEYS_LOCK:
        NODE_KEYS[key_id] = {
            "label": label,
            "secret": secret,
            "issued_host": host,
            "created_at": datetime.now().isoformat(),
            "revoked": False,
            "share": share,
            "can_manage": can_manage,
            "password_hash": hash_password(password) if password else None,
            "last_used_at": None,
            "peer_host": None,
            "use_count": 0,
        }
    asyncio.create_task(save_state())
    log_activity("node", f"کلید نود «{label}» ساخته شد", "ok")
    return {
        "ok": True, "key_id": key_id, "label": label,
        "key": build_node_key(host, secret), "share": share, "can_manage": can_manage,
    }


@app.patch("/api/nodes/keys/{key_id}")
async def update_node_key(key_id: str, request: Request, _=Depends(require_auth)):
    try:
        body = await request.json()
    except Exception:
        body = {}
    async with NODE_KEYS_LOCK:
        entry = NODE_KEYS.get(key_id)
        if entry is None:
            raise HTTPException(status_code=404, detail="key not found")
        if "label" in body:
            entry["label"] = (str(body.get("label") or "").strip() or entry["label"])[:60]
        if "share" in body:
            cur = entry.get("share") or {}
            src = body.get("share") if isinstance(body.get("share"), dict) else {}
            entry["share"] = {p: bool(src.get(p, cur.get(p, p != "logs"))) for p in NODE_SHARE_PARTS}
        if "can_manage" in body:
            entry["can_manage"] = bool(body.get("can_manage"))
        if "password" in body:
            pw = str(body.get("password") or "").strip()
            entry["password_hash"] = hash_password(pw) if pw else None
        if "enabled" in body:
            entry["revoked"] = not bool(body.get("enabled"))
        label = entry.get("label", key_id[:8])
        revoked = entry["revoked"]
    asyncio.create_task(save_state())
    log_activity("node", f"کلید نود «{label}» {'غیرفعال شد' if revoked else 'به‌روزرسانی شد'}",
                 "warn" if revoked else "ok")
    return {"ok": True, "key_id": key_id}


@app.delete("/api/nodes/keys/{key_id}")
async def revoke_node_key(key_id: str, _=Depends(require_auth)):
    async with NODE_KEYS_LOCK:
        entry = NODE_KEYS.get(key_id)
        if entry is None:
            raise HTTPException(status_code=404, detail="key not found")
        label = entry.get("label", key_id[:8])
        del NODE_KEYS[key_id]
    asyncio.create_task(save_state())
    log_activity("node", f"کلید نود «{label}» حذف شد", "warn")
    return {"ok": True, "revoked": key_id}


@app.get("/api/nodes/aggregate")
async def nodes_aggregate(request: Request, _=Depends(require_auth)):
    fresh = request.query_params.get("fresh") in ("1", "true", "yes")
    async with NODES_LOCK:
        snap = {nid: dict(n) for nid, n in NODES.items()}
    targets = [(nid, n) for nid, n in snap.items() if n.get("enabled", True)]
    results = await asyncio.gather(
        *(_fetch_node_snapshot(nid, n, fresh=fresh) for nid, n in targets),
        return_exceptions=True,
    )

    nodes_out: list[dict] = []
    for (nid, n), res in zip(targets, results):
        base = _node_public(nid, n)
        if isinstance(res, Exception):
            base.update({"online": False, "error": str(res)[:200]})
        else:
            base.update(res)
        nodes_out.append(base)
    for nid, n in snap.items():
        if not n.get("enabled", True):
            nodes_out.append({**_node_public(nid, n), "online": False, "error": None, "disabled": True})

    local = await get_stats(None)
    async with LINKS_LOCK:
        local_used = sum(l.get("used_bytes", 0) for l in LINKS.values())
    totals = {
        "local_used_bytes": local_used,
        "local_requests": local["total_requests"],
        "local_links": local["links_count"],
        "local_active_links": local["active_links"],
        "local_subs": local["subs_count"],
        "local_connections": local["active_connections"],
        "node_used_bytes": 0, "node_requests": 0, "node_links": 0,
        "node_active_links": 0, "node_subs": 0, "node_connections": 0,
        "nodes_total": len(snap), "nodes_online": 0,
    }
    for n in nodes_out:
        if not n.get("online"):
            continue
        totals["nodes_online"] += 1
        share = n.get("share") or {}
        st = n.get("stats") or {}
        if share.get("usage"):
            totals["node_used_bytes"] += int(st.get("total_bytes") or 0)
            totals["node_connections"] += int(st.get("active_connections") or 0)
        if share.get("requests"):
            totals["node_requests"] += int(st.get("total_requests") or 0)
        if share.get("links"):
            links = n.get("links") or []
            totals["node_links"] += len(links)
            totals["node_active_links"] += sum(1 for l in links if l.get("active") and not l.get("expired"))
        if share.get("subs"):
            totals["node_subs"] += len(n.get("subs") or [])
    totals["used_bytes"] = totals["local_used_bytes"] + totals["node_used_bytes"]
    totals["used_fmt"] = fmt_bytes(totals["used_bytes"])
    totals["node_used_fmt"] = fmt_bytes(totals["node_used_bytes"])
    totals["requests"] = totals["local_requests"] + totals["node_requests"]
    totals["links"] = totals["local_links"] + totals["node_links"]
    totals["active_links"] = totals["local_active_links"] + totals["node_active_links"]
    totals["subs"] = totals["local_subs"] + totals["node_subs"]
    totals["connections"] = totals["local_connections"] + totals["node_connections"]
    return {"nodes": nodes_out, "totals": totals}


async def _fetch_node_snapshot(node_id: str, node: dict, *, fresh: bool = False) -> dict:
    """اسنپ‌شات یک نود را با کش کوتاه‌مدت می‌گیرد. فقط بخش‌های تیک‌خورده منتقل می‌شوند."""
    share = node.get("share") or {}
    parts = sorted(p for p in NODE_SHARE_PARTS if share.get(p))
    cache_key = f"{node_id}|{','.join(parts)}"
    cached = _NODE_CACHE.get(cache_key)
    if not fresh and cached and (time.time() - cached["at"]) < NODE_CACHE_TTL:
        return cached["data"]
    if not parts:
        return {"online": True, "error": None, "stats": {}, "links": [], "subs": [], "logs": []}
    try:
        r = await _node_request(node, "GET", "/api/node/snapshot", params={"parts": ",".join(parts)})
        if r.status_code == 401:
            raise RuntimeError("کلید نود روی پنل مقابل ابطال شده است")
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}")
        payload = r.json()
    except Exception as exc:
        msg = str(exc)[:200] or exc.__class__.__name__
        async with NODES_LOCK:
            if node_id in NODES:
                NODES[node_id]["last_error"] = msg
        return {"online": False, "error": msg, "stats": {}, "links": [], "subs": [], "logs": []}

    now_iso = datetime.now().isoformat()
    async with NODES_LOCK:
        if node_id in NODES:
            NODES[node_id]["last_sync_at"] = now_iso
            NODES[node_id]["last_error"] = None
            NODES[node_id]["peer_version"] = payload.get("version")
    data = {
        "online": True,
        "error": None,
        "last_sync_at": now_iso,
        "peer_version": payload.get("version"),
        "stats": payload.get("stats") or {},
        "links": payload.get("links") or [],
        "subs": payload.get("subs") or [],
        "logs": payload.get("logs") or [],
    }
    _NODE_CACHE[cache_key] = {"at": time.time(), "data": data}
    asyncio.create_task(schedule_save())
    return data


@app.get("/api/nodes")
async def list_nodes(_=Depends(require_auth)):
    async with NODES_LOCK:
        snap = {nid: dict(n) for nid, n in NODES.items()}
    out = [_node_public(nid, n) for nid, n in snap.items()]
    out.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return {"nodes": out, "count": len(out)}


@app.post("/api/nodes/connect")
async def connect_node(request: Request, _=Depends(require_auth)):
    body = await request.json()
    key = str(body.get("key") or "").strip()
    try:
        host, _secret = parse_node_key(key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if host == get_host():
        raise HTTPException(status_code=400, detail="این کلید مربوط به همین پنل است")
    async with NODES_LOCK:
        for nid, n in NODES.items():
            if n.get("host") == host:
                raise HTTPException(status_code=409, detail=f"این پنل قبلاً به‌عنوان «{n.get('label')}» متصل شده است")

    node_password = str(body.get("password") or "").strip()
    candidate = {"host": host, "key": key}
    try:
        r = await _node_request(candidate, "POST", "/api/node/handshake",
                                json_body={"host": get_host(), "version": get_current_version(),
                                           "password": node_password})
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"اتصال به {host} برقرار نشد: {str(exc)[:160]}")
    if r.status_code == 401:
        detail = ""
        try:
            detail = r.json().get("detail") or ""
        except Exception:
            pass
        if detail == "PASSWORD_REQUIRED":
            raise HTTPException(status_code=401, detail="این نود رمز دارد؛ رمز را وارد کنید")
        if detail == "PASSWORD_INVALID":
            raise HTTPException(status_code=401, detail="رمز نود اشتباه است")
        raise HTTPException(status_code=401, detail="کلید توسط پنل مقابل پذیرفته نشد (ابطال‌شده یا نامعتبر)")
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"پاسخ نامعتبر از {host}: HTTP {r.status_code}")
    info = r.json()

    label = (str(body.get("label") or "").strip() or info.get("host") or host)[:60]
    node_id = generate_uuid()
    node = _normalize_node({
        "label": label, "host": host, "key": key,
        "peer_version": info.get("version"),
        "last_sync_at": datetime.now().isoformat(),
    })
    async with NODES_LOCK:
        NODES[node_id] = node
    _NODE_CACHE.clear()
    asyncio.create_task(save_state())
    log_activity("node", f"به نود «{label}» ({host}) متصل شد", "ok")
    return {"ok": True, "node": _node_public(node_id, node), "peer": info}


@app.patch("/api/nodes/{node_id}")
async def update_node(node_id: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    async with NODES_LOCK:
        node = NODES.get(node_id)
        if node is None:
            raise HTTPException(status_code=404, detail="node not found")
        if "label" in body:
            node["label"] = (str(body["label"]).strip() or node["host"])[:60]
        if "enabled" in body:
            node["enabled"] = bool(body["enabled"])
        if "merge_dashboard" in body:
            node["merge_dashboard"] = bool(body["merge_dashboard"])
        share = body.get("share")
        if isinstance(share, dict):
            for p in NODE_SHARE_PARTS:
                if p in share:
                    node["share"][p] = bool(share[p])
        snap = dict(node)
    _NODE_CACHE.clear()
    asyncio.create_task(save_state())
    return {"ok": True, "node": _node_public(node_id, snap)}


@app.delete("/api/nodes/{node_id}")
async def disconnect_node(node_id: str, _=Depends(require_auth)):
    async with NODES_LOCK:
        node = NODES.pop(node_id, None)
    if node is None:
        raise HTTPException(status_code=404, detail="node not found")
    _NODE_CACHE.clear()
    asyncio.create_task(save_state())
    log_activity("node", f"اتصال نود «{node.get('label')}» قطع شد", "warn")
    return {"ok": True, "disconnected": node_id}


async def _proxy_node_link_write(node_id: str, uid: str, method: str,
                                 json_body: dict | None = None) -> dict:
    async with NODES_LOCK:
        node = NODES.get(node_id)
        if node is None:
            raise HTTPException(status_code=404, detail="node not found")
        snap = dict(node)
    try:
        r = await _node_request(snap, method, f"/api/node/links/{uid}", json_body=json_body)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"نود پاسخ نداد: {str(exc)[:160]}")
    if r.status_code >= 400:
        detail = f"HTTP {r.status_code}"
        try:
            detail = r.json().get("detail") or detail
        except Exception:
            pass
        raise HTTPException(status_code=r.status_code, detail=detail)
    _NODE_CACHE.clear()
    return r.json() if r.content else {"ok": True}


@app.post("/api/nodes/{node_id}/subs")
async def proxy_node_create_sub(node_id: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    async with NODES_LOCK:
        node = NODES.get(node_id)
        if node is None:
            raise HTTPException(status_code=404, detail="node not found")
        snap = dict(node)
    try:
        r = await _node_request(snap, "POST", "/api/node/subs", json_body=body)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"نود پاسخ نداد: {str(exc)[:160]}")
    if r.status_code >= 400:
        detail = f"HTTP {r.status_code}"
        try:
            detail = r.json().get("detail") or detail
        except Exception:
            pass
        raise HTTPException(status_code=r.status_code, detail=detail)
    _NODE_CACHE.clear()
    return r.json()


async def _proxy_node_sub_write(node_id: str, sub_id: str, method: str,
                                 json_body: dict | None = None) -> dict:
    async with NODES_LOCK:
        node = NODES.get(node_id)
        if node is None:
            raise HTTPException(status_code=404, detail="node not found")
        snap = dict(node)
    try:
        r = await _node_request(snap, method, f"/api/node/subs/{sub_id}", json_body=json_body)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"نود پاسخ نداد: {str(exc)[:160]}")
    if r.status_code >= 400:
        detail = f"HTTP {r.status_code}"
        try:
            detail = r.json().get("detail") or detail
        except Exception:
            pass
        raise HTTPException(status_code=r.status_code, detail=detail)
    _NODE_CACHE.clear()
    return r.json() if r.content else {"ok": True}


@app.patch("/api/nodes/{node_id}/subs/{sub_id}")
async def proxy_node_update_sub(node_id: str, sub_id: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    return await _proxy_node_sub_write(node_id, sub_id, "PATCH", json_body=body)


@app.delete("/api/nodes/{node_id}/subs/{sub_id}")
async def proxy_node_delete_sub(node_id: str, sub_id: str, _=Depends(require_auth)):
    return await _proxy_node_sub_write(node_id, sub_id, "DELETE")


@app.post("/api/nodes/{node_id}/subs/{sub_id}/links")
async def proxy_node_assign_link_to_sub(node_id: str, sub_id: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    async with NODES_LOCK:
        node = NODES.get(node_id)
        if node is None:
            raise HTTPException(status_code=404, detail="node not found")
        snap = dict(node)
    try:
        r = await _node_request(snap, "POST", f"/api/node/subs/{sub_id}/links", json_body=body)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"نود پاسخ نداد: {str(exc)[:160]}")
    if r.status_code >= 400:
        detail = f"HTTP {r.status_code}"
        try:
            detail = r.json().get("detail") or detail
        except Exception:
            pass
        raise HTTPException(status_code=r.status_code, detail=detail)
    _NODE_CACHE.clear()
    return r.json() if r.content else {"ok": True}


@app.post("/api/nodes/{node_id}/links")
async def proxy_node_create_link(node_id: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    async with NODES_LOCK:
        node = NODES.get(node_id)
        if node is None:
            raise HTTPException(status_code=404, detail="node not found")
        snap = dict(node)
    try:
        r = await _node_request(snap, "POST", "/api/node/links", json_body=body)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"نود پاسخ نداد: {str(exc)[:160]}")
    if r.status_code >= 400:
        detail = f"HTTP {r.status_code}"
        try:
            detail = r.json().get("detail") or detail
        except Exception:
            pass
        raise HTTPException(status_code=r.status_code, detail=detail)
    _NODE_CACHE.clear()
    return r.json()


@app.patch("/api/nodes/{node_id}/links/{uid}")
async def proxy_node_update_link(node_id: str, uid: str, request: Request, _=Depends(require_auth)):
    body = await request.json()
    return await _proxy_node_link_write(node_id, uid, "PATCH", json_body=body)


@app.delete("/api/nodes/{node_id}/links/{uid}")
async def proxy_node_delete_link(node_id: str, uid: str, _=Depends(require_auth)):
    return await _proxy_node_link_write(node_id, uid, "DELETE")

# ══════════════════════════════════════════════════════════════════════════════
# VLESS Relay
# ══════════════════════════════════════════════════════════════════════════════
from protocol.vless.vless import (
    RELAY_BUF,
    parse_vless_header,
    check_and_use,
    relay_ws_to_tcp,
    relay_tcp_to_ws,
)
from protocol.vless.websocket import websocket_tunnel

from protocol.trojan.websocket import trojan_ws_tunnel

app.add_api_websocket_route("/ws/{uuid}", websocket_tunnel)
app.add_api_websocket_route("/trojan-ws", trojan_ws_tunnel)
from protocol.shadowsocks.shadowsocks import generate_ss_link, derive_key, CIPHERS, DEFAULT_CIPHER
from protocol.shadowsocks.websocket import shadowsocks_ws_tunnel
app.add_api_websocket_route("/ss-ws", shadowsocks_ws_tunnel)

# ══════════════════════════════════════════════════════════════════════════════
# XHTTP
# ══════════════════════════════════════════════════════════════════════════════
# نکته: مطابق نسخه‌ی مرجع (xhttp_siz10.py) مود stream-one حذف شده؛ فقط
# packet-up و stream-up فعال هستن. روترهای stream-one دیگه include نمی‌شن.
from protocol.vless.xhttpstreamon import router as xhttp_downlink_router
from protocol.vless.xhttpstreamup import router as xhttp_streamup_router
from protocol.vless.xhttshadpacketup import router as xhttp_packetup_router
app.include_router(xhttp_downlink_router)
app.include_router(xhttp_streamup_router)
app.include_router(xhttp_packetup_router)

from protocol.trojan.xhttpstreamon import router as trojan_xhttp_downlink_router
from protocol.trojan.xhttpstreamup import router as trojan_xhttp_streamup_router
from protocol.trojan.xhttshadpacketup import router as trojan_xhttp_packetup_router
app.include_router(trojan_xhttp_downlink_router)
app.include_router(trojan_xhttp_streamup_router)
app.include_router(trojan_xhttp_packetup_router)

# ── HTTP Proxy ────────────────────────────────────────────────────────────────
_HOP = {"connection","keep-alive","proxy-authenticate","proxy-authorization",
        "te","trailers","transfer-encoding","upgrade","content-encoding","content-length"}

@app.api_route("/proxy/{target_url:path}", methods=["GET","POST","PUT","DELETE","PATCH","HEAD","OPTIONS"])
async def http_proxy(target_url: str, request: Request):
    if not target_url.startswith("http"):
        target_url = "https://" + target_url
    try:
        body = await request.body()
        headers = {k: v for k, v in request.headers.items() if k.lower() not in _HOP and k.lower() != "host"}
        resp = await http_client.request(method=request.method, url=target_url, headers=headers, content=body)
        stats["total_bytes"] += len(resp.content)
        stats["total_requests"] += 1
        hourly_traffic[now_ir().strftime("%H:00")] += len(resp.content)
        return Response(content=resp.content, status_code=resp.status_code,
                        headers={k: v for k, v in resp.headers.items() if k.lower() not in _HOP})
    except Exception as exc:
        stats["total_errors"] += 1
        error_logs.append({"error": str(exc), "url": target_url, "time": datetime.now().isoformat()})
        raise HTTPException(status_code=502, detail=f"Proxy error: {exc}")

# ── Public sub page ───────────────────────────────────────────────────────────
@app.get("/p/{uuid_key}", response_class=HTMLResponse)
async def public_sub_page(uuid_key: str, request: Request):
    from pages import get_public_page_html
    async with SUBS_LOCK:
        sub = next(({"sub_id": sid, **s} for sid, s in SUBS.items() if s.get("uuid_key") == uuid_key), None)
    if not sub:
        return HTMLResponse("<h2 style='font-family:sans-serif;padding:40px'>گروه پیدا نشد</h2>", status_code=404)
    return HTMLResponse(content=get_public_page_html(uuid_key))



@app.get("/api/public/sub/{uuid_key}")
async def public_sub_data(uuid_key: str, request: Request):
    # ۱. احراز هویت و دریافت داده‌ها (همان منطق قبلی شما)
    async with SUBS_LOCK:
        sub_entry = next(((sid, s) for sid, s in SUBS.items() if s.get("uuid_key") == uuid_key), None)
    if not sub_entry:
        raise HTTPException(status_code=404, detail="not found")
    sub_id, sub = sub_entry

    has_pw = sub.get("password_hash") is not None
    if has_pw:
        pw = request.query_params.get("pw", "")
        if hash_password(pw) != sub["password_hash"]:
            return JSONResponse({"locked": True, "name": sub["name"]})

    host = get_host()
    link_ids = sub.get("link_ids", [])
    node_link_ids = sub.get("node_link_ids", [])
    async with LINKS_LOCK:
        snap = dict(LINKS)

    links_out = []
    active_conns = 0
    
    # ۲. ساخت لیست کانفیگ‌ها
    for lid in link_ids:
        link = snap.get(lid)
        if not link: continue
        allowed = is_link_allowed(link)
        conn_count = sum(1 for c in connections.values() if c.get("uuid") == lid)
        active_conns += conn_count
        proto = link.get("protocol", DEFAULT_PROTOCOL)
        links_out.append({
            "uuid": lid,
            "label": link["label"],
            "active": allowed,
            "protocol": proto,
            "used_bytes": link.get("used_bytes", 0),
            "limit_bytes": link.get("limit_bytes", 0),
            "vless_link": generate_share_link(lid, host, remark=f"RVG-{link['label']}", protocol=proto),
        })

    # ۲.۵ کانفیگ‌های نودهای دیگر
    if node_link_ids:
        async with NODES_LOCK:
            nodes_snap = {nid: dict(n) for nid, n in NODES.items()}
        needed_nodes = list({ref.split("::", 1)[0] for ref in node_link_ids if "::" in ref})
        needed_nodes = [nid for nid in needed_nodes if nid in nodes_snap]
        snapshots = await asyncio.gather(
            *(_fetch_node_snapshot(nid, nodes_snap[nid], fresh=True) for nid in needed_nodes),
            return_exceptions=True,
        )
        snap_by_node = dict(zip(needed_nodes, snapshots))
        for ref in node_link_ids:
            if "::" not in ref:
                continue
            nid, uid = ref.split("::", 1)
            node_snap = snap_by_node.get(nid)
            if not node_snap or isinstance(node_snap, Exception):
                continue
            node_link = next((l for l in (node_snap.get("links") or []) if l.get("uuid") == uid), None)
            if not node_link or not node_link.get("vless_link"):
                continue
            lb = node_link.get("limit_bytes", 0)
            allowed = bool(node_link.get("active", True)) and not node_link.get("expired") and not (lb > 0 and node_link.get("used_bytes", 0) >= lb)
            links_out.append({
                "uuid": nid + "::" + uid,
                "label": node_link.get("label", uid),
                "active": allowed,
                "protocol": node_link.get("protocol", DEFAULT_PROTOCOL),
                "used_bytes": node_link.get("used_bytes", 0),
                "limit_bytes": node_link.get("limit_bytes", 0),
                "vless_link": node_link["vless_link"],
            })

    # ۲.۶ کانفیگ‌های ایستا (foreign_links) — مثلاً کانفیگ‌های پنل مرکزی که روی
    # یک نود اضافه شده‌اند؛ چون این نود به پنل مرکزی دسترسی برگشتی ندارد،
    # این کانفیگ‌ها به‌صورت اسنپ‌شات (لینک آماده) ذخیره و همینجا نمایش داده می‌شوند.
    for fl in sub.get("foreign_links", []):
        vl = fl.get("vless_link")
        if not vl:
            continue
        links_out.append({
            "uuid": fl.get("key") or vl,
            "label": fl.get("label", "کانفیگ"),
            "active": True,
            "protocol": fl.get("protocol", DEFAULT_PROTOCOL),
            "used_bytes": fl.get("used_bytes", 0),
            "limit_bytes": 0,
            "vless_link": vl,
        })

    # ۳. تشخیص کلاینت یا مرورگر
    user_agent = request.headers.get("User-Agent", "").lower()
    is_client = any(ua in user_agent for ua in ["v2rayng", "v2rayn", "shadowrocket", "clash", "surfboard", "nekoray"])

    if is_client:
        # اگر کلاینت است: فقط لینک‌های فعال را به صورت Base64 برگردان
        raw_links = "\n".join([l["vless_link"] for l in links_out if l["active"]])
        encoded_data = base64.b64encode(raw_links.encode("utf-8")).decode("utf-8")
        return Response(content=encoded_data, media_type="text/plain")

    # ۴. اگر مرورگر است: دیتای کامل JSON را برگردان
    return {
        "locked": False,
        "name": f"پنل: {sub['name']}",
        "desc": sub.get("desc", ""),
        "sub_url": f"https://{host}/sub-group/{uuid_key}",
        "active_connections": active_conns,
        "links": links_out, # اینجا همان لیست کامل شماست
    }

# ══════════════════════════════════════════════════════════════════════════════
# Version / Auto-Update
# ══════════════════════════════════════════════════════════════════════════════
from updater import (
    get_current_version, get_current_version_info,
    get_latest_version_info, perform_update,
    update_log, update_state, load_update_history,
    REPO, BRANCH, is_newer_version,
)

@app.get("/api/version")
async def api_version(_=Depends(require_auth)):
    current_info = get_current_version_info()
    latest_info = await get_latest_version_info()
    latest_ver = latest_info.get("version")
    update_available = is_newer_version(latest_ver, current_info["version"]) if latest_ver else False
    return {
        "repo": REPO,
        "branch": BRANCH,
        "current": current_info,
        "latest": latest_info,
        "update_available": update_available,
    }

@app.get("/api/update-history")
async def api_update_history(_=Depends(require_auth)):
    return {"history": load_update_history()}

@app.get("/api/update-log")
async def api_update_log(_=Depends(require_auth)):
    return {"running": update_state["running"], "progress": update_state["progress"], "logs": list(update_log)[-100:]}

@app.post("/api/update")
async def api_update(_=Depends(require_auth)):
    if update_state["running"]:
        raise HTTPException(status_code=409, detail="بروزرسانی در حال اجراست")
    update_log.append({"time": time.time(), "msg": "درخواست بروزرسانی ثبت شد، در صف اجرا..."})

    async def _run():
        ok = False
        try:
            ok = await perform_update()
        except Exception as exc:
            import traceback as tb
            update_log.append({"time": time.time(), "msg": f"❌ خطای بحرانی: {exc}"})
            update_log.append({"time": time.time(), "msg": tb.format_exc()[-800:]})
            update_state["running"] = False
        try:
            await save_state()
            log_activity("system", "بروزرسانی پنل " + ("موفق" if ok else "ناموفق") + " بود", "ok" if ok else "err")
        except Exception:
            pass
        if ok:
            update_log.append({"time": time.time(), "msg": "در حال راه‌اندازی مجدد پروسه (بدون خاموش‌شدن کانتینر)..."})
            await asyncio.sleep(1.5)
            try:
                os.execv(sys.executable, [sys.executable] + sys.argv)
            except Exception as exc:
                update_log.append({"time": time.time(), "msg": f"❌ execv شکست خورد: {exc} — fallback به exit"})
                os._exit(0)

    task = asyncio.create_task(_run())

    def _on_done(t: asyncio.Task):
        if t.cancelled():
            return
        exc = t.exception()
        if exc:
            update_log.append({"time": time.time(), "msg": f"❌ Task crash: {exc}"})
            update_state["running"] = False

    task.add_done_callback(_on_done)
    log_activity("system", "درخواست بروزرسانی پنل ثبت شد", "info")
    return {"ok": True, "started": True}

# ── Settings: توقف کامل لاگ‌گیری (برای بیشترین throughput ممکن) ─────────────────
@app.get("/api/settings/logging")
async def get_logging_setting(_=Depends(require_auth)):
    return {"disabled": bool(CONFIG.get("disable_logging"))}


@app.post("/api/settings/logging")
async def set_logging_setting(request: Request, _=Depends(require_auth)):
    body = await request.json()
    disabled = bool(body.get("disabled"))
    CONFIG["disable_logging"] = disabled
    apply_logging_state()
    await save_state()
    return {"ok": True, "disabled": disabled}


# ── HTML Pages ───────────────────────────────────────────────────────────────
from pages import LOGIN_HTML, DASHBOARD_HTML

# ── Central: Announcements & Support ─────────────────────────────────────────
@app.get("/api/announcements")
async def api_announcements(_=Depends(require_auth)):
    return {"announcements": await central.fetch_announcements()}

@app.post("/api/announcements/view")
async def api_announcements_view(request: Request, _=Depends(require_auth)):
    body = await request.json()
    ids = body.get("ids", [])
    if not isinstance(ids, list):
        raise HTTPException(status_code=400, detail="invalid ids")
    await central.report_announcement_views([str(i) for i in ids][:100])
    return {"ok": True}

@app.get("/api/support/messages")
async def api_support_messages(_=Depends(require_auth)):
    messages, blocked = await central.fetch_support_messages()
    return {"messages": messages, "blocked": blocked}

@app.post("/api/support/send")
async def api_support_send(request: Request, _=Depends(require_auth)):
    body = await request.json()
    msg = str(body.get("message", "")).strip()[:2000]
    if not msg:
        raise HTTPException(status_code=400, detail="پیام خالی است")
    result = await central.send_support_message(msg)
    if result.get("blocked"):
        raise HTTPException(status_code=403, detail="شما توسط پشتیبانی بلاک شده‌اید")
    if not result.get("ok"):
        raise HTTPException(status_code=502, detail=result.get("error") or "ارتباط با سرور مرکزی برقرار نشد")
    return {"ok": True}

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if await is_valid_session(request.cookies.get(SESSION_COOKIE)):
        return RedirectResponse(url="/dashboard")
    return HTMLResponse(content=LOGIN_HTML)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not await is_valid_session(request.cookies.get(SESSION_COOKIE)):
        return RedirectResponse(url="/login")
    await ensure_default_link()
    return HTMLResponse(content=DASHBOARD_HTML)

@app.get("/test-ws", response_class=HTMLResponse)
async def test_ws_redirect():
    return HTMLResponse(content="<script>location.href='/dashboard'</script>")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=CONFIG["port"],
        log_level="info",
        workers=1,
        loop="auto",         # uvloop رو در صورت نصب بودن استفاده می‌کنه، وگرنه بدون کرش fallback می‌کنه
        http="auto",
    )
