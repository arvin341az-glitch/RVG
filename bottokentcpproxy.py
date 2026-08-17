# bottokentcpproxy.py
# ══════════════════════════════════════════════════════════════════════════════
# ساخت خودکار TCP Proxy روی Railway — فلوی نهایی:
#   ۱) پینگ واقعیِ دامنه‌ها از سمت مرورگرِ خودِ کاربر انجام می‌شود (نه از سرور پنل؛
#      چون سرور پنل خودش روی Railway/خارج است و همیشه به همه‌چیز دسترسی دارد و
#      نمی‌تواند فیلتر بودنِ یک دامنه از دید اینترنت کاربر را تشخیص دهد). نتیجه‌ی
#      این پینگ (لیست دامنه‌های سالم) از فرانت‌اند به این ماژول پاس داده می‌شود.
#   ۲) با پورتی که کاربر داده، مرتب روی Railway پروکسی ساخته می‌شود (create)؛ اگر دامنه‌ی
#      تصادفیِ برگشتی جزو دامنه‌های «سالم» نبود، حذف (delete) و دوباره تلاش می‌شود — تا
#      وقتی که یک دامنه‌ی سالم گیر بیاید.
#   ۳) به محض پیدا شدن، خودکار به یک لینک تلگرامی (با همان پورت داخلی) وصل می‌شود.
# برای سرعت بالا، ساخت پروکسی به‌صورت موازی (چند تلاش هم‌زمان) ارسال می‌شود.
# ══════════════════════════════════════════════════════════════════════════════

import asyncio
import os
import time
import logging
from collections import deque
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger("RVG-Gateway")

GRAPHQL_URL = "https://backboard.railway.app/graphql/v2"

KNOWN_DOMAINS: tuple[str, ...] = (
    "tokaido.proxy.rlwy.net", "shuttle.proxy.rlwy.net", "hayabusa.proxy.rlwy.net",
    "yamabiko.proxy.rlwy.net", "crossover.proxy.rlwy.net", "tramway.proxy.rlwy.net",
    "autorack.proxy.rlwy.net", "shinkansen.proxy.rlwy.net", "roundhouse.proxy.rlwy.net",
    "turntable.proxy.rlwy.net", "metro.proxy.rlwy.net", "reseau.proxy.rlwy.net",
    "junction.proxy.rlwy.net", "switchback.proxy.rlwy.net", "yamanote.proxy.rlwy.net",
    "zephyr.proxy.rlwy.net", "thomas.proxy.rlwy.net", "centerbeam.proxy.rlwy.net",
    "switchyard.proxy.rlwy.net", "shortline.proxy.rlwy.net", "viaduct.proxy.rlwy.net",
    "ballast.proxy.rlwy.net", "kodama.proxy.rlwy.net", "interchange.proxy.rlwy.net",
    "hopper.proxy.rlwy.net", "mainline.proxy.rlwy.net", "trolley.proxy.rlwy.net",
    "altaria.proxy.rlwy.net", "nozomi.proxy.rlwy.net", "monorail.proxy.rlwy.net",
)

MAX_ATTEMPTS = int(os.environ.get("BOT_TCP_PROXY_MAX_ATTEMPTS", 300))

# چند درخواست هم‌زمان (موازی) در هر راند ساخت پروکسی ارسال شود
CONCURRENCY = int(os.environ.get("BOT_TCP_PROXY_CONCURRENCY", 8))

# تاخیر پایه بین راندهای ساخت (وقتی ریت‌لیمیت نخوریم صفر است = سریع‌ترین حالت)
DELAY_SEC = float(os.environ.get("BOT_TCP_PROXY_DELAY", 0))
MAX_BACKOFF = 15.0

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
TOKEN_FILE = DATA_DIR / ".bot_tcp_proxy_token"

MUTATION_CREATE = """
mutation TcpProxyCreate($environmentId: String!, $serviceId: String!, $applicationPort: Int!) {
  tcpProxyCreate(input: {
    environmentId: $environmentId,
    serviceId: $serviceId,
    applicationPort: $applicationPort
  }) {
    id
    domain
    proxyPort
    applicationPort
  }
}
"""

MUTATION_DELETE = """
mutation TcpProxyDelete($id: String!) {
  tcpProxyDelete(id: $id)
}
"""

bot_proxy_state = {
    "running": False,
    "phase": "idle",          # idle | searching | done | error | stopped
    "progress": 0,
    "attempts": 0,
    "result": None,            # {domain, port, application_port, id}
    "error": None,
    "stopped_by_user": False,
}
bot_proxy_log: deque = deque(maxlen=300)
_task: Optional[asyncio.Task] = None


def _mask(token: str) -> str:
    if not token or len(token) <= 8:
        return "***"
    return f"{token[:4]}…{token[-4:]}"


def _log(msg: str):
    bot_proxy_log.append({"time": time.time(), "msg": msg})
    logger.info(f"BotTcpProxy: {msg}")


def get_status() -> dict:
    return {
        **bot_proxy_state,
        "has_token": has_saved_token(),
        "logs": list(bot_proxy_log)[-100:],
    }


def get_known_domains() -> list:
    return list(KNOWN_DOMAINS)


def has_saved_token() -> bool:
    try:
        return TOKEN_FILE.exists() and bool(TOKEN_FILE.read_text(encoding="utf-8").strip())
    except Exception:
        return False


def load_token() -> Optional[str]:
    try:
        if TOKEN_FILE.exists():
            val = TOKEN_FILE.read_text(encoding="utf-8").strip()
            return val or None
    except Exception as exc:
        logger.warning(f"BotTcpProxy: خواندن توکن ذخیره‌شده ناموفق بود: {exc}")
    return None


def save_token(token: str):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(token.strip(), encoding="utf-8")
        try:
            os.chmod(TOKEN_FILE, 0o600)
        except Exception:
            pass
    except Exception as exc:
        logger.warning(f"BotTcpProxy: ذخیره‌ی توکن روی دیسک ناموفق بود: {exc}")


def clear_token():
    try:
        TOKEN_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def get_service_context() -> tuple[str, str]:
    service_id = os.environ.get("RAILWAY_SERVICE_ID")
    environment_id = os.environ.get("RAILWAY_ENVIRONMENT_ID")
    if not service_id or not environment_id:
        raise RuntimeError(
            "RAILWAY_SERVICE_ID / RAILWAY_ENVIRONMENT_ID پیدا نشد — "
            "این قابلیت فقط وقتی پنل روی خودِ Railway دیپلوی شده باشه کار می‌کند."
        )
    return service_id, environment_id


def _norm_domain(d: str) -> str:
    return (d or "").strip().rstrip(".").lower()


class _RateLimited(Exception):
    pass


class _AuthError(Exception):
    """فقط برای خطاهای واقعیِ احراز هویت (توکن نامعتبر) — تنها موردی که باید کل فرآیند را متوقف کند."""
    pass


async def _gql(client: httpx.AsyncClient, token: str, query: str, variables: dict) -> dict:
    resp = await client.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=20.0,
    )
    if resp.status_code == 401:
        raise _AuthError("توکن Railway نامعتبر است یا دسترسی کافی ندارد")
    if resp.status_code == 429:
        raise _RateLimited()
    resp.raise_for_status()
    data = resp.json()
    if data.get("errors"):
        msg = "; ".join(e.get("message", "خطای نامشخص") for e in data["errors"])
        # این یک خطای GraphQL معمولی است (مثلاً تداخل موقتی هنگام ساخت هم‌زمان چند پروکسی)
        # و نباید کل فرآیند را متوقف کند — فقط این تلاش را rejected می‌کنیم.
        raise RuntimeError(f"خطای GraphQL: {msg}")
    return data.get("data", {})


async def _create_proxy(client: httpx.AsyncClient, token: str, service_id: str,
                         environment_id: str, application_port: int) -> dict:
    data = await _gql(client, token, MUTATION_CREATE, {
        "environmentId": environment_id,
        "serviceId": service_id,
        "applicationPort": application_port,
    })
    return data["tcpProxyCreate"]


async def _delete_proxy(client: httpx.AsyncClient, token: str, proxy_id: str):
    try:
        await _gql(client, token, MUTATION_DELETE, {"id": proxy_id})
    except Exception as exc:
        _log(f"⚠ حذف proxy نامطلوب ({proxy_id[:8]}…) ناموفق بود: {exc}")


async def _single_attempt(client: httpx.AsyncClient, token: str, service_id: str,
                           environment_id: str, application_port: int,
                           attempt_no: int, winner_holder: dict, reachable: set,
                           win_lock: asyncio.Lock):
    """یک تلاش برای ساخت پروکسی. اگر دامنه جزو دامنه‌های سالم بود و هنوز برنده‌ای
    اعلام نشده، این را برنده می‌کند؛ در غیر این صورت بلافاصله حذف می‌شود."""
    try:
        proxy = await _create_proxy(client, token, service_id, environment_id, application_port)
    except _AuthError as exc:
        return ("fatal", str(exc))
    except _RateLimited:
        return "rate_limited"
    except RuntimeError as exc:
        _log(f"⚠ خطای موقتی (GraphQL) در تلاش {attempt_no}: {exc}")
        return "retry"
    except Exception as exc:
        _log(f"⚠ خطای موقتی در تلاش {attempt_no}: {exc}")
        return "retry"

    domain_raw = proxy.get("domain", "")
    domain = _norm_domain(domain_raw)
    proxy_id = proxy.get("id")

    if domain not in reachable:
        _log(f"تلاش {attempt_no}: دامنه‌ی {domain_raw} جزو دامنه‌های سالم نیست — حذف می‌شود")
        await _delete_proxy(client, token, proxy_id)
        return "rejected"

    async with win_lock:
        if winner_holder.get("result") is not None:
            await _delete_proxy(client, token, proxy_id)
            return "discarded_after_win"
        winner_holder["result"] = {
            "domain": domain,
            "port": proxy.get("proxyPort"),
            "application_port": proxy.get("applicationPort"),
            "id": proxy_id,
        }
    _log(f"✅ موفق! تلاش {attempt_no}: دامنه‌ی سالم پیدا شد → {domain_raw} — پورت TCP: {proxy.get('proxyPort')}")
    return "won"


async def run_bot_proxy_job(token: str, application_port: int, reachable: set):
    if not reachable:
        bot_proxy_state.update({
            "running": False, "phase": "error",
            "error": "هیچ دامنه‌ی سالمی از مرحله‌ی پینگ ارسال نشده بود",
        })
        return

    win_lock = asyncio.Lock()
    winner_holder: dict = {"result": None}

    bot_proxy_state.update({
        "running": True, "phase": "searching", "progress": 0, "attempts": 0,
        "result": None, "error": None, "stopped_by_user": False,
    })
    _log(
        f"شروع جست‌وجو روی {len(reachable)} دامنه‌ی سالم — همزمانی: {CONCURRENCY} — "
        f"پورت اپلیکیشن {application_port} — توکن {_mask(token)}"
    )

    try:
        service_id, environment_id = get_service_context()
        _log(f"سرویس شناسایی شد (service={service_id[:8]}… env={environment_id[:8]}…)")
    except RuntimeError as exc:
        bot_proxy_state["running"] = False
        bot_proxy_state["phase"] = "error"
        bot_proxy_state["error"] = str(exc)
        _log(f"❌ {exc}")
        return

    backoff = DELAY_SEC
    total_attempts = 0

    try:
        async with httpx.AsyncClient() as client:
            while total_attempts < MAX_ATTEMPTS and winner_holder["result"] is None:
                batch_size = min(CONCURRENCY, MAX_ATTEMPTS - total_attempts)
                tasks = []
                for i in range(batch_size):
                    total_attempts += 1
                    tasks.append(
                        _single_attempt(
                            client, token, service_id, environment_id,
                            application_port, total_attempts, winner_holder,
                            reachable, win_lock,
                        )
                    )

                bot_proxy_state["attempts"] = total_attempts
                bot_proxy_state["progress"] = min(99, int(total_attempts / MAX_ATTEMPTS * 100))

                results = await asyncio.gather(*tasks, return_exceptions=True)

                if winner_holder["result"] is not None:
                    break

                fatal_error = None
                any_rate_limited = False
                for r in results:
                    if isinstance(r, Exception):
                        _log(f"⚠ خطای غیرمنتظره: {r}")
                        continue
                    if isinstance(r, tuple) and r[0] == "fatal":
                        fatal_error = r[1]
                    elif r == "rate_limited":
                        any_rate_limited = True

                if fatal_error:
                    bot_proxy_state["running"] = False
                    bot_proxy_state["phase"] = "error"
                    bot_proxy_state["error"] = fatal_error
                    _log(f"❌ توقف: {fatal_error}")
                    return

                if any_rate_limited:
                    backoff = min(MAX_BACKOFF, max(1.0, backoff * 1.7))
                    _log(f"⏳ ریت‌لیمیت ریلوی — {backoff:.1f} ثانیه صبر می‌کنیم...")
                    await asyncio.sleep(backoff)
                else:
                    backoff = DELAY_SEC
                    if DELAY_SEC:
                        await asyncio.sleep(DELAY_SEC)

        if winner_holder["result"] is not None:
            bot_proxy_state.update({
                "running": False,
                "phase": "done",
                "progress": 100,
                "result": winner_holder["result"],
            })
        else:
            bot_proxy_state["running"] = False
            bot_proxy_state["phase"] = "error"
            bot_proxy_state["error"] = (
                f"بعد از {total_attempts} تلاش، به هیچ‌کدام از دامنه‌های سالم نرسیدیم"
            )
            _log(f"❌ {bot_proxy_state['error']}")

    except asyncio.CancelledError:
        bot_proxy_state.update({
            "running": False,
            "phase": "stopped",
            "error": "فرآیند توسط کاربر متوقف شد",
            "stopped_by_user": True,
        })
        _log("⏹ فرآیند توسط کاربر متوقف شد")


def start_job(token: Optional[str], application_port: int, reachable_domains: Optional[list] = None):
    global _task
    token = (token or "").strip()
    if not token:
        token = load_token() or ""
    if not token:
        raise RuntimeError("توکن Railway وارد نشده و توکن ذخیره‌شده‌ای هم وجود ندارد")
    if bot_proxy_state["running"]:
        raise RuntimeError("یک فرآیند ساخت TCP Proxy از قبل در حال اجراست")

    reachable = {_norm_domain(d) for d in (reachable_domains or []) if _norm_domain(d)}
    if not reachable:
        raise RuntimeError("اول باید مرحله‌ی پینگ دامنه‌ها (از مرورگر خودت) انجام شود")

    save_token(token)
    _task = asyncio.create_task(run_bot_proxy_job(token, application_port, reachable))
    return _task


def stop_job() -> bool:
    global _task
    if _task and not _task.done():
        _task.cancel()
        return True
    return False


# ══════════════════════════════════════════════════════════════════════════════
# ساخت/حذف TCP Proxy عمومی برای یک پورت دلخواه — بدون محدودیت به دامنه‌ی خاص
# با استفاده از توکنی که کاربر یک‌بار ذخیره کرده — این توابع توسط main.py
# هنگام ساخت/حذف/تغییر پورت کانفیگ‌های Telegram Proxy صدا زده می‌شوند.
# ══════════════════════════════════════════════════════════════════════════════

async def create_public_proxy_for_port(application_port: int) -> dict:
    token = load_token()
    if not token:
        raise RuntimeError("توکن Railway ذخیره نشده — ابتدا یک‌بار از بخش Bot TCP Proxy توکن را وارد کنید")

    service_id, environment_id = get_service_context()
    async with httpx.AsyncClient() as client:
        proxy = await _create_proxy(client, token, service_id, environment_id, application_port)

    return {
        "id": proxy.get("id"),
        "domain": _norm_domain(proxy.get("domain", "")),
        "port": proxy.get("proxyPort"),
        "application_port": proxy.get("applicationPort"),
    }


async def delete_public_proxy(proxy_id: str):
    token = load_token()
    if not token or not proxy_id:
        return
    async with httpx.AsyncClient() as client:
        await _delete_proxy(client, token, proxy_id)
