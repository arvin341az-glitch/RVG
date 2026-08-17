# mtproto_native.py
# ══════════════════════════════════════════════════════════════════════════════
# بک‌اند رسمی MTProto — بعد از تست mtg و telemt که هردو توی ad-tag/middle-proxy
# باگ داشتن (خصوصاً روی Railway)، این ماژول مستقیماً باینری رسمی خودِ تلگرام
# (https://github.com/TelegramMessenger/MTProxy) رو کامپایل و اجرا می‌کنه —
# دقیقاً همون باینری‌ای که تصویر رسمی دیترِ Docker ازش استفاده می‌کنه و ad-tag
# روش تضمینی کار می‌کنه.
#
# معماری: درست مثل نسخه‌ی قدیمی mtg شما — یک پروسه به‌ازای هر لینک/کاربر
# (per-instance / per-port). این باینری رسمی per-process فقط یک ad-tag
# (-P) قبول می‌کنه، ولی چون هرکاربر پروسه‌ی خودش رو داره، این یعنی هرکاربر
# همچنان ad_tag مستقل خودش رو داره — دقیقاً چیزی که RVG نیاز داره.
# ══════════════════════════════════════════════════════════════════════════════
import asyncio
import ipaddress
import os
import platform
import re
import resource
import secrets
import shutil
import socket
import subprocess
import time
import traceback
import logging
from pathlib import Path
from typing import Awaitable, Callable, Optional

import httpx

logger = logging.getLogger("RVG-Gateway")

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
MTP_DIR = DATA_DIR / "mtproxy"
SRC_DIR = MTP_DIR / "src"
BIN_PATH = MTP_DIR / "mtproto-proxy"
BACKEND_CONF = MTP_DIR / "backend.conf"
# نکته: اسم فایل عمداً عوض شده (v2) — نسخه‌های قبلی این پروژه اینجا یک سکرت
# رندوم ۴۸ بایتیِ غلط می‌نوشتن؛ با اسم جدید مطمئنیم روی هر دیپلوی قدیمی هم
# یک‌بار قطعاً از core.telegram.org دانلود واقعی انجام می‌شه، نه cache خراب.
AES_PWD_FILE = MTP_DIR / "proxy-secret-v2"  # از core.telegram.org/getProxySecret دانلود می‌شود (نه رندوم محلی!)

DEFAULT_FAKE_TLS_DOMAIN = ""  # فقط برای سازگاری با لینک‌های قدیمی؛ این باینری از FakeTLS مجزا استفاده نمی‌کنه

MTPROTO_PORT_RANGE_START = int(os.environ.get("MTPROTO_PORT_START", 8500))
MTPROTO_PORT_RANGE_END = int(os.environ.get("MTPROTO_PORT_END", 8600))

MAX_LOG_LINES = 300
PORT_RETRY_ATTEMPTS = 20
PORT_RETRY_DELAY = 0.3
STOP_PORT_FREE_ATTEMPTS = 20
STOP_PORT_FREE_DELAY = 0.3
STARTUP_VERIFY_DELAY = 0.7
BACKEND_CONF_MAX_AGE = 6 * 3600  # هر ۶ ساعت رفرش

WORKERS = int(os.environ.get("MTP_WORKERS", 2))
MAX_CONN = int(os.environ.get("MTP_MAX_CONN", 60000))

_instances: dict = {}
_instances_lock = asyncio.Lock()
_used_ports: set[int] = set()

_usage_callback: Optional[Callable[[str, int], Awaitable[bool]]] = None
_build_lock = asyncio.Lock()
_external_ip: Optional[str] = None
_internal_ip: Optional[str] = None


def set_usage_callback(cb: Callable[[str, int], Awaitable[bool]]):
    global _usage_callback
    _usage_callback = cb
    logger.info("MTP: usage_callback ثبت شد")


def _mask_secret(secret: str) -> str:
    if not secret or len(secret) <= 12:
        return "***"
    return f"{secret[:8]}…{secret[-6:]}"


# ── ساخت باینری رسمی از سورس (ریلیز پیش‌کامپایل رسمی وجود نداره) ──────────────
async def ensure_binary() -> bool:
    if BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK):
        return True
    async with _build_lock:
        if BIN_PATH.exists() and os.access(BIN_PATH, os.X_OK):
            return True
        t0 = time.monotonic()
        logger.info("MTP: باینری mtproto-proxy پیدا نشد، شروع build از سورس رسمی تلگرام...")
        MTP_DIR.mkdir(parents=True, exist_ok=True)

        # پکیج‌های لازم برای build (فقط یک‌بار روی هر container)
        try:
            subprocess.run(
                ["bash", "-c",
                 "apt-get update -qq && apt-get install -y -qq "
                 "build-essential libssl-dev zlib1g-dev git curl >/dev/null 2>&1"],
                timeout=180, capture_output=True,
            )
        except Exception as exc:
            logger.warning(f"MTP: نصب build-deps کامل موفق نبود (ممکنه از قبل نصب باشن): {exc}")

        try:
            if SRC_DIR.exists():
                shutil.rmtree(SRC_DIR, ignore_errors=True)
            r = subprocess.run(
                ["git", "clone", "--depth", "1",
                 "https://github.com/TelegramMessenger/MTProxy.git", str(SRC_DIR)],
                timeout=120, capture_output=True, text=True,
            )
            if r.returncode != 0:
                raise RuntimeError(f"git clone شکست خورد: {r.stderr[-500:]}")

            r = subprocess.run(
                ["make"], cwd=str(SRC_DIR), timeout=300, capture_output=True, text=True,
            )
            built = SRC_DIR / "objs" / "bin" / "mtproto-proxy"
            if r.returncode != 0 or not built.exists():
                raise RuntimeError(f"make شکست خورد: {r.stderr[-800:]}")

            shutil.copy2(built, BIN_PATH)
            BIN_PATH.chmod(0o755)
            shutil.rmtree(SRC_DIR, ignore_errors=True)
            logger.info(f"✅ MTP: باینری ساخته شد ({time.monotonic()-t0:.1f}s)")
            return True
        except Exception as exc:
            logger.error(f"MTP: build شکست خورد: {exc}\n{traceback.format_exc()}")
            return False


async def _ensure_backend_conf() -> bool:
    try:
        if BACKEND_CONF.exists():
            age = time.time() - BACKEND_CONF.stat().st_mtime
            if age < BACKEND_CONF_MAX_AGE:
                return True
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get("https://core.telegram.org/getProxyConfig")
            r.raise_for_status()
            MTP_DIR.mkdir(parents=True, exist_ok=True)
            BACKEND_CONF.write_text(r.text, encoding="utf-8")
        return True
    except Exception as exc:
        if BACKEND_CONF.exists():
            logger.warning(f"MTP: رفرش backend.conf شکست خورد، از نسخه‌ی کش‌شده استفاده می‌شود: {exc}")
            return True
        logger.error(f"MTP: دانلود backend.conf ناموفق بود: {exc}")
        return False


AES_PWD_MAX_AGE = 24 * 3600  # طبق توصیه‌ی رسمی: حداکثر هر ۲۴ ساعت رفرش

async def _ensure_aes_pwd_file() -> Path:
    """🔴 نکته‌ی حیاتی که علت اصلیِ «پروکسی ساخته می‌شه ولی پینگ نمی‌ده» بود:
    این فایل یک secret دلخواه/رندوم محلی نیست! طبق مستندات رسمی
    (https://github.com/TelegramMessenger/MTProxy#running، مرحله‌ی ۱)، این فایل
    باید دقیقاً از سرور خودِ تلگرام دانلود بشه:
        curl -s https://core.telegram.org/getProxySecret -o proxy-secret
    این کلید AES برای هندشیک بین این پروسه و بک‌اندِ واقعیِ تلگرامه (نه بین
    پروسه و کلاینت). قبلاً اینجا با secrets.token_bytes(48) یک مقدار رندوم
    محلی نوشته می‌شد — باینری با همون مقدار جعلی هم بی‌سروصدا بالا می‌اومد و
    پورت رو باز می‌کرد (برای همین "ساخته می‌شد")، ولی چون کلید واقعی نبود،
    هیچ‌وقت نمی‌تونست با core.telegram.org handshake کنه، پس هیچ ترافیکی رد
    نمی‌شد: کلاینت وصل می‌شد ولی پینگ نمی‌گرفت و دیتا رد نمی‌شد.
    فایل واقعی همیشه ۱۰۴ بایته (توسط خودمون هم تست و تأیید شد) و کاملاً داخل
    بازه‌ی مجاز baینری (۳۲ تا ۲۵۶ بایت) هست."""
    if AES_PWD_FILE.exists():
        age = time.time() - AES_PWD_FILE.stat().st_mtime
        size = AES_PWD_FILE.stat().st_size
        if age < AES_PWD_MAX_AGE and 32 <= size <= 256:
            return AES_PWD_FILE
    MTP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get("https://core.telegram.org/getProxySecret")
            r.raise_for_status()
            data = r.content
            if not (32 <= len(data) <= 256):
                raise RuntimeError(f"سایز غیرمنتظره برای proxy-secret: {len(data)} بایت")
            AES_PWD_FILE.write_bytes(data)
            logger.info(f"MTP: proxy-secret واقعی از core.telegram.org دانلود شد ({len(data)} بایت)")
    except Exception as exc:
        if AES_PWD_FILE.exists() and 32 <= AES_PWD_FILE.stat().st_size <= 256:
            logger.warning(f"MTP: رفرش proxy-secret ناموفق بود، از نسخه‌ی کش‌شده استفاده می‌شود: {exc}")
        else:
            logger.error(f"MTP: دانلود proxy-secret ناموفق بود و نسخه‌ی کش‌شده‌ی معتبری هم نیست: {exc}")
            raise RuntimeError(f"دریافت proxy-secret از core.telegram.org ناموفق بود: {exc}")
    return AES_PWD_FILE


async def _detect_ips() -> tuple[str, str]:
    global _external_ip, _internal_ip
    if _internal_ip is None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                _internal_ip = s.getsockname()[0]
        except Exception:
            _internal_ip = "0.0.0.0"
    if _external_ip is None:
        # نکته‌ی مهم: باید حتماً IPv4 باشه (دقیقاً مثل اسکریپت رسمی که `curl -4`
        # می‌زنه) — چون --nat-info با فرمت <ipv4>:<ipv4> پارس می‌شه و اگه یه IPv6
        # (که پر از ':' هست) برگرده، پارسر باینری خطای "cannot translate host"
        # می‌ده و پروسه فوراً crash می‌کنه.
        transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0")
        for url in ("https://api.ipify.org", "https://digitalresistance.dog/myIp",
                    "https://ipv4.icanhazip.com"):
            try:
                async with httpx.AsyncClient(timeout=8.0, transport=transport) as client:
                    r = await client.get(url)
                    ip = r.text.strip()
                    parsed = ipaddress.ip_address(ip)
                    if not isinstance(parsed, ipaddress.IPv4Address):
                        logger.warning(f"MTP: {url} یک IPv6 برگردوند ({ip})، رد می‌شیم به منبع بعدی")
                        continue
                    _external_ip = ip
                    break
            except Exception:
                continue
        if _external_ip is None:
            logger.warning("MTP: تشخیص IP خارجی (IPv4) ناموفق بود، از internal IP استفاده می‌شود")
            _external_ip = _internal_ip
    return _internal_ip, _external_ip


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("0.0.0.0", port))
            return True
        except OSError:
            return False


async def allocate_port_async(preferred: int | None = None, force: bool = False, uuid: str = "") -> int | None:
    tag = uuid[:8] if uuid else "?"
    if preferred is not None:
        for _ in range(PORT_RETRY_ATTEMPTS):
            if preferred not in _used_ports and _port_free(preferred):
                return preferred
            await asyncio.sleep(PORT_RETRY_DELAY)
        if force:
            logger.warning(f"MTP[{tag}]: پورت {preferred} آزاد نشد ولی force فعاله، رد می‌شیم به allocate آزاد")
            return None
        logger.warning(f"MTP[{tag}]: پورت قبلی {preferred} آزاد نشد، دنبال پورت جایگزین می‌گردیم")

    for port in range(MTPROTO_PORT_RANGE_START, MTPROTO_PORT_RANGE_END):
        if port in _used_ports:
            continue
        if _port_free(port):
            return port
    logger.error(f"MTP[{tag}]: هیچ پورت آزادی در بازه‌ی {MTPROTO_PORT_RANGE_START}-{MTPROTO_PORT_RANGE_END} نیست")
    return None


def generate_secret() -> str:
    """سکرت خام ۳۲ کاراکتری هگز — فرمت بومی باینری رسمی (بدون پیشوند ee)."""
    return secrets.token_hex(16)


def sanitize_domain(raw: str | None) -> str:
    """دامنه‌ی FakeTLS رو تمیز می‌کنه.
    چرا لازمه: توی دیتای ذخیره‌شده مقادیری مثل
    `[www.cloudflare.com](https://www.cloudflare.com)` (لینک مارک‌داون) وجود داره.
    چون هگزِ همین رشته داخل سکرت ee می‌ره و کلاینت با اون SNI وصل می‌شه،
    هر کاراکتر اضافه باعث شکست کامل handshake می‌شه (وصل نمی‌شه/دیتا رد نمی‌شه)."""
    if not raw:
        return DEFAULT_FAKE_TLS_DOMAIN
    s = str(raw).strip()
    # حالت مارک‌داون: [متن](آدرس) -> فقط متن داخل کروشه
    m = re.match(r"^\[([^\]]+)\]\(.*\)$", s)
    if m:
        s = m.group(1).strip()
    # حذف پروتکل و مسیر، اگه کسی URL کامل وارد کرده باشه
    s = re.sub(r"^[a-zA-Z]+://", "", s).split("/")[0].split("?")[0].strip()
    # فقط کاراکترهای مجاز یک hostname
    if not re.fullmatch(r"[A-Za-z0-9.\-]{1,253}", s) or "." not in s:
        logger.warning(f"MTP: دامنه‌ی نامعتبر {raw!r} — به {DEFAULT_FAKE_TLS_DOMAIN} برگردانده شد")
        return DEFAULT_FAKE_TLS_DOMAIN
    return s.lower()


def client_secret(raw_secret: str, domain: str | None = None) -> str:
    """سکرتی که باید توی لینک تلگرام استفاده بشه.
    - اگه FakeTLS فعاله (دامنه داریم): ee + سکرت خام + هگزِ دامنه
    - وگرنه: dd + سکرت خام (حالت secured؛ از classic خام امن‌تره و کمتر بلاک می‌شه)
    سکرت خام بدون پیشوند = حالت classic که توسط DPI ایران بلاک می‌شه."""
    if domain:
        return "ee" + raw_secret + sanitize_domain(domain).encode().hex()
    return "dd" + raw_secret


def generate_mtproto_link(host: str, port: int, secret: str,
                          domain: str | None = None) -> str:
    return f"tg://proxy?server={host}&port={port}&secret={client_secret(secret, domain)}"


def generate_mtproto_web_link(host: str, port: int, secret: str,
                              domain: str | None = None) -> str:
    return f"https://t.me/proxy?server={host}&port={port}&secret={client_secret(secret, domain)}"


async def get_stats(uuid: str) -> dict:
    """آمار واقعی از خود باینری (--http-stats روی 127.0.0.1:2398).
    مهم‌ترین فیلد: total_special_connections = تعداد اتصال‌های ورودی کلاینت.
    اگه این صفر بمونه یعنی واقعاً هیچ پکتی نمی‌رسه؛ اگه بالا بره یعنی پکت
    می‌رسه و مشکل جای دیگه‌ست (مثلاً handshake/سکرت)."""
    inst = _instances.get(uuid)
    if not inst or inst["proc"].returncode is not None:
        return {"error": "instance اجرا نیست"}
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            r = await client.get("http://127.0.0.1:2398/stats")
            raw = r.text
    except Exception as exc:
        return {"error": f"دریافت stats ناموفق: {exc}"}

    parsed = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for sep in ("\t", " "):
            if sep in line:
                k, _, v = line.partition(sep)
                parsed[k.strip()] = v.strip()
                break
    interesting = {
        k: parsed[k] for k in (
            "total_special_connections", "active_special_connections",
            "total_max_special_connections", "active_targets",
            "ready_targets", "active_network_events", "tot_forwarded_queries",
        ) if k in parsed
    }
    return {"summary": interesting, "raw": raw[:4000]}


def _mtp_preexec():
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        target = min(65535, hard) if hard != resource.RLIM_INFINITY else 65535
        if target > soft:
            resource.setrlimit(resource.RLIMIT_NOFILE, (target, hard))
    except Exception:
        pass


async def _stream_process_output(uuid: str, proc: asyncio.subprocess.Process, inst: dict):
    assert proc.stdout is not None
    try:
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="ignore").rstrip()
            if not text:
                continue
            inst["logs"].append(text)
            if len(inst["logs"]) > MAX_LOG_LINES:
                del inst["logs"][: len(inst["logs"]) - MAX_LOG_LINES]
            low = text.lower()
            if "error" in low or "fatal" in low:
                logger.error(f"MTP[{uuid[:8]}] stdout: {text}")
            elif "warn" in low:
                logger.warning(f"MTP[{uuid[:8]}] stdout: {text}")
            else:
                logger.info(f"MTP[{uuid[:8]}] stdout: {text}")
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.error(f"MTP[{uuid[:8]}]: خطا در خواندن stdout: {exc}")


async def start_instance(
    uuid: str,
    secret: str | None = None,
    domain: str = DEFAULT_FAKE_TLS_DOMAIN,   # دامنه‌ی FakeTLS (حالت ee)
    preferred_port: int | None = None,
    force_port: bool = False,
    ad_tag: str | None = None,
) -> dict:
    t0 = time.monotonic()
    # همیشه تمیزش کن — دیتای ذخیره‌شده ممکنه رشته‌ی خراب داشته باشه
    domain = sanitize_domain(domain)
    logger.info(f"MTP[{uuid[:8]}]: start_instance (preferred_port={preferred_port}, force={force_port}, ad_tag={ad_tag})")

    async with _instances_lock:
        existing = _instances.get(uuid)
        if existing and existing["proc"].returncode is None:
            logger.info(f"MTP[{uuid[:8]}]: از قبل در حال اجراست روی پورت {existing['port']}")
            return existing

        if not await ensure_binary():
            raise RuntimeError("باینری mtproto-proxy در دسترس نیست (build ناموفق)")
        if not await _ensure_backend_conf():
            raise RuntimeError("دریافت backend.conf از core.telegram.org ناموفق بود")

        port = await allocate_port_async(preferred_port, force=force_port, uuid=uuid)
        if port is None:
            if force_port and preferred_port is not None:
                raise RuntimeError(f"پورت {preferred_port} در حال حاضر اشغال است")
            raise RuntimeError("پورت آزادی برای MTProto باقی نمانده")

        if secret is None or len(secret) != 32:
            secret = generate_secret()

        internal_ip, external_ip = await _detect_ips()
        aes_pwd = await _ensure_aes_pwd_file()

        cmd_base = [
            str(BIN_PATH),
            "-p", "2398",           # پورت کنترل داخلی (هرچی، فقط باید آزاد باشه per-process)
            "-H", str(port),        # پورت واقعی MTProto که کلاینت بهش وصل می‌شه
            "-C", str(MAX_CONN),
            "--aes-pwd", str(aes_pwd),
            "-u", "root",
            str(BACKEND_CONF),
            "--allow-skip-dh",
            "--http-stats",         # /stats روی 127.0.0.1:2398 — تنها راه قطعی برای
                                    # دیدن این‌که واقعاً چند اتصال ورودی رسیده
            "--nat-info", f"{internal_ip}:{external_ip}",
        ]

        # ── FakeTLS (حالت ee) ─────────────────────────────────────────────────
        # 🔴 باگ دومی که اینجا بود: طبق مثال رسمی خودِ تلگرام برای حالت FakeTLS
        # (issue #340 روی TelegramMessenger/MTProxy)، دستور واقعی این‌جوریه:
        #   mtproto-proxy ... -M 1 -6 --domain www.my.amazing.domain
        # یعنی -M (تعداد worker) همیشه باید کنار -D/--domain بیاد — نه اینکه با
        # هم قاطی نشن. کد قبلی با این فرض غلط که "worker با TLS-transport
        # توصیه نمی‌شه" وقتی FakeTLS فعال بود (که چون domain همیشه یک مقدار
        # پیش‌فرض داره یعنی تقریباً همیشه) اصلاً -M رو نمی‌فرستاد. این دقیقاً
        # همون چیزیه که باعث می‌شد حالت ad_tag (که برای مسیر middle-proxy به
        # تعداد worker مشخص نیاز داره) بی‌ثبات/غیرفعال بمونه — تبلیغ توی UI
        # "ثبت شده" نشون داده می‌شد ولی عملاً کار نمی‌کرد.
        use_faketls = bool(domain)
        cmd_base += ["-M", str(WORKERS)]
        if use_faketls:
            cmd_base += ["-D", domain]

        tail = ["-S", secret]
        if ad_tag:
            tail += ["-P", ad_tag]

        # ── چرا -6 حیاتیه ──────────────────────────────────────────────────────
        # روتر/پروکسی داخلی Railway به کانتینر از طریق IPv6 وصل می‌شه. باینری رسمی
        # به‌صورت پیش‌فرض فقط روی 0.0.0.0 (IPv4-only) گوش می‌ده، پس اتصال‌های
        # TCP Proxy اصلاً به پروسه نمی‌رسن — نه ارور، نه لاگ، نه پینگ؛ دقیقاً همون
        # علامتی که دیدیم. با -6 سوکت AF_INET6 با IPV6_V6ONLY=0 ساخته می‌شه یعنی
        # dual-stack (هم IPv4 هم IPv6) که مستندات Railway هم همینو توصیه می‌کنه.
        # اگه محیطی IPv6 نداشت، باینری بالا نمیاد؛ در اون صورت بدون -6 fallback می‌کنیم.
        attempts = [(["-6"] + tail, "IPv6 dual-stack"), (tail, "IPv4-only (fallback)")]

        proc = None
        mode_used = ""
        for extra, mode_label in attempts:
            cmd = cmd_base + extra
            try:
                candidate = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    preexec_fn=_mtp_preexec,
                )
            except Exception as exc:
                logger.error(f"MTP[{uuid[:8]}]: اجرای پروسه ({mode_label}) شکست خورد: {exc}")
                continue

            await asyncio.sleep(STARTUP_VERIFY_DELAY)
            if candidate.returncode is None:
                proc = candidate
                mode_used = mode_label
                break

            out = b""
            try:
                if candidate.stdout:
                    out = await asyncio.wait_for(candidate.stdout.read(4000), timeout=2.0)
            except Exception:
                pass
            logger.warning(
                f"MTP[{uuid[:8]}]: حالت {mode_label} کار نکرد "
                f"(کد {candidate.returncode}): {out.decode('utf-8', 'ignore')[-300:]}"
            )

        if proc is None:
            _used_ports.discard(port)
            raise RuntimeError("mtproto-proxy در هیچ‌کدام از حالت‌های IPv6/IPv4 بالا نیامد")

        _used_ports.add(port)
        inst = {
            "proc": proc, "port": port, "secret": secret, "domain": domain,
            "ad_tag": ad_tag, "external_ip": external_ip,
            "logs": [], "started_at": time.time(), "used_bytes_reported": 0,
        }
        _instances[uuid] = inst
        inst["log_task"] = asyncio.create_task(_stream_process_output(uuid, proc, inst))

        logger.info(
            f"✅ MTP[{uuid[:8]}]: PID={proc.pid} port={port} mode={mode_used} "
            f"secret={_mask_secret(secret)} ad_tag={ad_tag} external_ip={external_ip} "
            f"({time.monotonic()-t0:.2f}s)"
        )
        asyncio.create_task(_watch_process(uuid, proc))
        return inst


async def _watch_process(uuid: str, proc: asyncio.subprocess.Process):
    rc = await proc.wait()
    async with _instances_lock:
        cur = _instances.get(uuid)
        if cur and cur["proc"] is proc:
            _used_ports.discard(cur["port"])
            t = cur.get("log_task")
            if t:
                t.cancel()
            last_logs = cur.get("logs", [])[-10:]
            del _instances[uuid]
        else:
            last_logs = []
    if rc not in (0, None, -15, -9):
        logger.warning(f"⚠️ MTP[{uuid[:8]}]: پروسه با کد {rc} متوقف شد")
        if last_logs:
            logger.warning(f"MTP[{uuid[:8]}]: آخرین لاگ‌ها:\n" + "\n".join(last_logs))
    else:
        logger.info(f"MTP[{uuid[:8]}]: پروسه با کد {rc} خاتمه یافت")


async def stop_instance(uuid: str):
    logger.info(f"MTP[{uuid[:8]}]: stop_instance")
    async with _instances_lock:
        inst = _instances.pop(uuid, None)
    if not inst:
        return
    _used_ports.discard(inst["port"])
    t = inst.get("log_task")
    if t:
        t.cancel()
        try:
            await t
        except (asyncio.CancelledError, Exception):
            pass

    proc = inst["proc"]
    if proc.returncode is None:
        try:
            proc.terminate()
            await asyncio.wait_for(proc.wait(), timeout=5.0)
        except (asyncio.TimeoutError, ProcessLookupError):
            try:
                proc.kill()
                await proc.wait()
            except ProcessLookupError:
                pass

    for _ in range(STOP_PORT_FREE_ATTEMPTS):
        if _port_free(inst["port"]):
            break
        await asyncio.sleep(STOP_PORT_FREE_DELAY)
    logger.info(f"🔌 MTP[{uuid[:8]}]: متوقف شد (پورت {inst['port']} آزاد شد)")


def get_instance_info(uuid: str) -> dict | None:
    inst = _instances.get(uuid)
    if not inst:
        return None
    return {
        "port": inst["port"], "secret": inst["secret"], "domain": inst["domain"],
        "ad_tag": inst.get("ad_tag"), "running": inst["proc"].returncode is None,
        "pid": inst["proc"].pid, "started_at": inst.get("started_at"),
        "logs": inst.get("logs", [])[-50:],
    }


def get_instance_connections(uuid: str) -> list[dict]:
    inst = _instances.get(uuid)
    if not inst or inst["proc"].returncode is not None:
        return []
    port = inst["port"]
    result = []
    try:
        import psutil
        for conn in psutil.net_connections(kind="inet"):
            if (conn.laddr and conn.laddr.port == port
                    and conn.status == "ESTABLISHED" and conn.raddr):
                result.append({"ip": conn.raddr.ip, "port": conn.raddr.port})
    except ImportError:
        pass
    except Exception as exc:
        logger.debug(f"MTP[{uuid[:8]}]: خطا در خواندن اتصالات: {exc}")
    return result


async def stop_all():
    async with _instances_lock:
        uuids = list(_instances.keys())
    logger.info(f"MTP: shutdown — {len(uuids)} instance در حال توقف")
    for uid in uuids:
        try:
            await stop_instance(uid)
        except Exception as exc:
            logger.error(f"MTP[{uid[:8]}]: خطا حین shutdown: {exc}")
