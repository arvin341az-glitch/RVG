# telemt.py
# ══════════════════════════════════════════════════════════════════════════════
# بک‌اند جدید MTProto — به‌جای mtg (که در حالت تبلیغ/ad-tag به قول خودِ سازنده‌ش
# «پیچیده‌ترین و باگ‌دارترین بخش کل ابزاره»)، از telemt استفاده می‌کنیم:
# https://github.com/telemt/telemt — پروژه‌ای که خودِ مستندات mtg هم برای adtag
# پیشنهادش می‌ده.
#
# تفاوت معماری مهم: برخلاف mtg (یک پروسه به‌ازای هر کانفیگ/پورت)، telemt یک
# پروسه‌ی مشترک داره که چند «کاربر» (هرکدوم یک سکرت مستقل) روی یک پورت واحد
# سرویس می‌ده. مزیت بزرگش برای ما: اضافه/حذف‌کردن کاربر یا تغییر ad_tag فقط
# نیاز به بازنویسی فایل کانفیگ + SIGHUP (ری‌لود نرم) داره — نه ری‌استارت
# کامل پروسه. یعنی پورت هیچ‌وقت عوض نمی‌شه و دیگه نیازی به هماهنگ نگه‌داشتن
# TCP Proxy روی Railway با پورت جدید نیست (کل دسته‌باگی که با mtg داشتیم).
# ══════════════════════════════════════════════════════════════════════════════

import asyncio
import os
import platform
import secrets
import signal
import stat
import tarfile
import time
import traceback
import logging
from pathlib import Path
from typing import Awaitable, Callable, Optional

import httpx

logger = logging.getLogger("RVG-Gateway")

TELEMT_DIR = Path(os.environ.get("DATA_DIR", "/data")) / "telemt"
TELEMT_BIN = TELEMT_DIR / "telemt"
CONFIG_PATH = TELEMT_DIR / "config.toml"

DEFAULT_TLS_DOMAIN = "www.cloudflare.com"
# پورت مشترک ثابت که همه‌ی کاربرهای MTProto روش سرویس می‌گیرن — چون telemt
# تک‌پورته، فقط یک TCP Proxy روی Railway برای همیشه لازمه.
TELEMT_PORT = int(os.environ.get("TELEMT_PORT", 8477))
API_PORT = int(os.environ.get("TELEMT_API_PORT", 8478))
API_BASE = f"http://127.0.0.1:{API_PORT}"

MAX_LOG_LINES = 300

_proc: Optional[asyncio.subprocess.Process] = None
_log_task: Optional[asyncio.Task] = None
_logs: list = []
_usage_callback: Optional[Callable[[str, int], Awaitable[bool]]] = None
_lock = asyncio.Lock()


def set_usage_callback(cb: Callable[[str, int], Awaitable[bool]]):
    global _usage_callback
    _usage_callback = cb


def _mask_secret(secret: str) -> str:
    if not secret or len(secret) <= 12:
        return "***"
    return f"{secret[:6]}…{secret[-4:]}"


def _log(msg: str, level: str = "info"):
    _logs.append({"time": time.time(), "msg": msg})
    if len(_logs) > MAX_LOG_LINES:
        del _logs[: len(_logs) - MAX_LOG_LINES]
    getattr(logger, level, logger.info)(f"Telemt: {msg}")


def get_logs(tail: int = 80) -> list:
    return list(_logs)[-tail:]


def _release_asset() -> str:
    arch = platform.machine().lower()
    if arch in ("x86_64", "amd64"):
        arch_tag = "x86_64"
    elif arch in ("aarch64", "arm64"):
        arch_tag = "aarch64"
    else:
        raise RuntimeError(f"معماری پشتیبانی‌نشده برای telemt: {arch}")
    return f"telemt-{arch_tag}-linux-gnu.tar.gz"


async def ensure_binary() -> bool:
    if TELEMT_BIN.exists() and os.access(TELEMT_BIN, os.X_OK):
        return True
    t0 = time.monotonic()
    _log("باینری telemt پیدا نشد، شروع دانلود...")
    TELEMT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        asset = _release_asset()
    except Exception as exc:
        _log(f"خطا در تشخیص asset: {exc}", "error")
        return False

    url = f"https://github.com/telemt/telemt/releases/latest/download/{asset}"
    tmp_tar = TELEMT_DIR / asset
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            tmp_tar.write_bytes(resp.content)
        with tarfile.open(tmp_tar, "r:gz") as tf:
            member = next((m for m in tf.getmembers() if m.name.endswith("telemt") and m.isfile()), None)
            if member is None:
                raise RuntimeError("باینری telemt در آرشیو پیدا نشد")
            member.name = "telemt"
            tf.extract(member, TELEMT_DIR)
        tmp_tar.unlink(missing_ok=True)
        st = TELEMT_BIN.stat()
        TELEMT_BIN.chmod(st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        _log(f"✅ باینری telemt نصب شد ({time.monotonic()-t0:.2f}s)")
        return True
    except Exception as exc:
        _log(f"دانلود/نصب telemt شکست خورد: {exc}\n{traceback.format_exc()}", "error")
        return False


def generate_secret() -> str:
    """سکرت خام ۳۲ کاراکتری هگز — فرمت بومی telemt (بدون پیشوند ee/dd)."""
    return secrets.token_hex(16)


def client_secret(raw_secret: str, domain: str = DEFAULT_TLS_DOMAIN) -> str:
    """سکرتی که باید در لینک/کلاینت تلگرام استفاده بشه — چون حالت TLS فعاله،
    فرمتش دقیقاً مثل FakeTLS معمولیه: ee + سکرت خام + هگزِ دامنه."""
    return "ee" + raw_secret + domain.encode().hex()


def _escape_toml_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def write_config(users: dict, ad_tags: dict, port: int = TELEMT_PORT,
                  domain: str = DEFAULT_TLS_DOMAIN) -> Path:
    """کانفیگ پایه (بدون دست‌کاری مستقیم [access.users] بعد از این نقطه — کاربرها
    از این به بعد از طریق Control API واقعیِ telemt (/v1/users) مدیریت می‌شن، نه
    بازنویسی فایل؛ اینجا فقط برای bootstrap اولیه لازمه)."""
    TELEMT_DIR.mkdir(parents=True, exist_ok=True)

    has_any_tag = any(ad_tags.get(uid) for uid in users)

    lines = [
        "[general]",
        f"use_middle_proxy = {'true' if has_any_tag else 'false'}",
        'log_level = "normal"',
        "",
        "[general.modes]",
        "classic = false",
        "secure = false",
        "tls = true",
        "",
        "[general.links]",
        'show = "*"',
        "",
        "[server]",
        f"port = {port}",
        "",
        "[server.api]",
        "enabled = true",
        f'listen = "127.0.0.1:{API_PORT}"',
        'whitelist = ["127.0.0.1/32", "::1/128"]',
        "",
        "[[server.listeners]]",
        'ip = "0.0.0.0"',
        "",
        "[censorship]",
        f'tls_domain = "{_escape_toml_str(domain)}"',
        "mask = true",
        "",
        "[access.users]",
    ]
    for uid, secret in users.items():
        lines.append(f'"{_escape_toml_str(uid)}" = "{secret}"')

    tag_lines = [f'"{_escape_toml_str(uid)}" = "{tag}"' for uid, tag in ad_tags.items() if tag]
    if tag_lines:
        lines += ["", "[access.user_ad_tags]"] + tag_lines

    CONFIG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    _log(f"کانفیگ نوشته شد -> {len(users)} کاربر، {len(tag_lines)} تگ تبلیغ، پورت {port}")
    return CONFIG_PATH


async def _stream_output(proc: asyncio.subprocess.Process):
    assert proc.stdout is not None
    try:
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="ignore").rstrip()
            # حذف کدهای رنگ ANSI برای خوانایی لاگ
            import re as _re
            text = _re.sub(r"\x1b\[[0-9;]*m", "", text)
            if not text:
                continue
            low = text.lower()
            if "error" in low or "panic" in low:
                _log(text, "error")
            elif "warn" in low:
                _log(text, "warning")
            else:
                _logs.append({"time": time.time(), "msg": text})
                if len(_logs) > MAX_LOG_LINES:
                    del _logs[: len(_logs) - MAX_LOG_LINES]
                logger.debug(f"Telemt stdout: {text}")
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        _log(f"خطا در خواندن stdout: {exc}", "error")


def is_running() -> bool:
    return _proc is not None and _proc.returncode is None


async def start():
    """پروسه‌ی telemt رو با کانفیگ فعلی (که قبلش با write_config نوشته شده) بالا می‌آره."""
    global _proc, _log_task
    async with _lock:
        if is_running():
            return
        if not await ensure_binary():
            raise RuntimeError("باینری telemt در دسترس نیست")
        if not CONFIG_PATH.exists():
            raise RuntimeError("کانفیگ telemt هنوز نوشته نشده")

        child_env = os.environ.copy()
        try:
            proc = await asyncio.create_subprocess_exec(
                str(TELEMT_BIN), "run", str(CONFIG_PATH),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=child_env,
            )
        except Exception as exc:
            _log(f"اجرای پروسه‌ی telemt شکست خورد: {exc}", "error")
            raise

        _proc = proc
        _log_task = asyncio.create_task(_stream_output(proc))

        await asyncio.sleep(1.0)
        if proc.returncode is not None:
            last = "\n".join(m["msg"] for m in _logs[-8:]) or "(لاگی ثبت نشد)"
            _proc = None
            raise RuntimeError(f"telemt بلافاصله بعد از اجرا متوقف شد (کد {proc.returncode}): {last[:400]}")

        _log(f"✅ telemt بالا اومد (PID={proc.pid}, پورت={TELEMT_PORT})")
        asyncio.create_task(_watch_process(proc))


async def _watch_process(proc: asyncio.subprocess.Process):
    rc = await proc.wait()
    global _proc
    if _proc is proc:
        _proc = None
    if rc not in (0, None, -15, -9, -1):
        _log(f"⚠️ telemt با کد {rc} متوقف شد", "warning")
    else:
        _log(f"telemt با کد {rc} خاتمه یافت")





async def stop():
    global _proc, _log_task
    async with _lock:
        proc = _proc
        _proc = None
        if _log_task:
            _log_task.cancel()
            _log_task = None
    if not proc or proc.returncode is not None:
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
    _log("🔌 telemt متوقف شد")


async def api_wait_ready(timeout: float = 15.0) -> bool:
    deadline = time.monotonic() + timeout
    async with httpx.AsyncClient() as client:
        while time.monotonic() < deadline:
            try:
                r = await client.get(f"{API_BASE}/v1/system/info", timeout=2.0)
                if r.status_code < 500:
                    return True
            except Exception:
                pass
            await asyncio.sleep(0.5)
    return False


async def api_create_user(uid: str, secret: str) -> Optional[dict]:
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_BASE}/v1/users", json={"username": uid, "secret": secret}, timeout=8.0)
        if r.status_code == 409:
            return await api_get_user(uid)
        r.raise_for_status()
        return r.json()


async def api_get_user(uid: str) -> Optional[dict]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE}/v1/users/{uid}", timeout=8.0)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()


async def api_delete_user(uid: str):
    async with httpx.AsyncClient() as client:
        try:
            await client.delete(f"{API_BASE}/v1/users/{uid}", timeout=8.0)
        except Exception as exc:
            _log(f"حذف کاربر {uid[:8]} از telemt ناموفق بود: {exc}", "warning")


async def api_set_ad_tag(uid: str, ad_tag: Optional[str]):
    """تگ تبلیغ رو برای یک کاربر خاص، بدون هیچ قطعی سرویس، از طریق API تنظیم می‌کنه.
    نکته‌ی مهمی که با تست مستقیم پیدا شد: اسم فیلد صحیح توی API واقعاً
    "user_ad_tag" هست نه "ad_tag" — با اسم اشتباه، درخواست 200 OK برمی‌گرده
    (بدون خطا) ولی مقدار اصلاً اعمال نمی‌شه و همیشه null می‌مونه؛ دقیقاً همین
    باعث می‌شد تبلیغ هیچ‌وقت واقعاً فعال نشه.

    نکته: اگه ad_tag=None باشه (user بدون تبلیغ)، درخواست رو میزنیم تا tag رو
    پاک کنیم، ولی runtime error نمیندازیم اگه applied هم None بود."""
    async with httpx.AsyncClient() as client:
        r = await client.patch(
            f"{API_BASE}/v1/users/{uid}",
            json={"user_ad_tag": ad_tag},
            timeout=8.0,
        )
        r.raise_for_status()
        data = r.json()
        applied = (data.get("data") or {}).get("user_ad_tag")
        if ad_tag and applied != ad_tag:
            _log(
                f"⚠️ ad_tag برای {uid[:8]} ست نشد "
                f"(فرستادیم: {ad_tag!r}, دریافتی: {applied!r}) — "
                f"احتمالاً use_middle_proxy=false است",
                "error",
            )
            raise RuntimeError(f"ad_tag ثبت نشد (پاسخ سرور: user_ad_tag={applied!r})")
        if ad_tag:
            _log(f"✅ ad_tag برای {uid[:8]} اعمال شد: {ad_tag!r}")
        return data


def _read_config_middle_proxy() -> Optional[bool]:
    """مقدار فعلی use_middle_proxy رو از فایل کانفیگ روی دیسک میخونه.
    اگه فایل نبود یا parse نشد، None برمیگردونه."""
    try:
        if not CONFIG_PATH.exists():
            return None
        for line in CONFIG_PATH.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("use_middle_proxy"):
                val = stripped.split("=", 1)[-1].strip().lower()
                return val == "true"
    except Exception:
        pass
    return None


async def _restart_with_config(users: dict, ad_tags: dict, domain: str) -> None:
    """پروسه رو stop میکنه، کانفیگ جدید مینویسه و دوباره start میکنه.
    وقتی use_middle_proxy باید از false به true (یا برعکس) تغییر کنه، چاره‌ای
    جز restart کامل نیست چون این یه config-level setting هست نه API-level.

    مهم: بعد از restart، کاربرها و ad_tag‌ها رو دوباره از طریق Control API
    اعمال می‌کنیم — چون telemt ممکنه [access.user_ad_tags] رو از فایل کانفیگ
    به‌صورت خودکار در runtime اعمال نکنه (مستندات telemt تأکید داره که مدیریت
    باید از طریق API باشه، نه مستقیم از config)."""
    _log("⚙️ restart کامل telemt برای اعمال تغییر use_middle_proxy شروع شد...")
    await stop()
    await asyncio.sleep(0.5)
    write_config(users, ad_tags, port=TELEMT_PORT, domain=domain)
    await start()
    if not await api_wait_ready():
        _log("Control API telemt آماده نشد بعد از restart (timeout)", "warning")
        return

    # بعد از restart، همه‌ی کاربرها و ad_tag‌هاشون رو از طریق API اعمال می‌کنیم.
    # این مرحله حیاتیه چون config file به‌تنهایی کافی نیست — telemt ممکنه
    # user_ad_tags رو از config در startup نخونه.
    for uid, secret in users.items():
        try:
            await api_create_user(uid, secret)
        except Exception as exc:
            _log(f"ساخت/اطمینان از کاربر {uid[:8]} بعد از restart ناموفق بود: {exc}", "warning")
        tag = ad_tags.get(uid)
        if tag:
            try:
                await api_set_ad_tag(uid, tag)
            except Exception as exc:
                _log(f"اعمال ad_tag برای {uid[:8]} بعد از restart ناموفق بود: {exc}", "error")

    _log("✅ restart کامل telemt تموم شد")


async def sync(users: dict, ad_tags: dict, domain: str = DEFAULT_TLS_DOMAIN):
    """نقطه‌ی ورود اصلی برای main.py — طبق مستندات رسمی telemt، مدیریت کاربرها
    باید از طریق Control API انجام بشه، نه بازنویسیِ مستقیم فایل کانفیگ:
      - اگه پروسه اصلاً بالا نیست: کانفیگ اولیه (bootstrap) رو با همون کاربرها
        می‌نویسه و پروسه رو یک‌بار بالا می‌آره.
      - اگه از قبل بالاست: با API کاربرهای جدید/حذف‌شده رو sync میکنه.
      - مهم: اگه use_middle_proxy باید تغییر کنه (مثلاً اولین ad_tag ست شد)،
        telemt رو restart میکنه — چون این تنظیم config-level هست و از API قابل
        تغییر نیست. کانفیگ فایل هم همیشه آپدیت میشه تا بعد از crash/deploy
        درست باشه.
    """
    # همیشه کانفیگ فایل رو آپدیت کن — برای survival از crash/restart
    has_any_tag = any(ad_tags.get(uid) for uid in users)

    if not is_running():
        write_config(users, ad_tags, port=TELEMT_PORT, domain=domain)
        await start()
        if not await api_wait_ready():
            _log("Control API telemt آماده نشد (timeout)", "warning")
        return

    # پروسه از قبل روشنه
    # چک کن آیا use_middle_proxy باید تغییر کنه
    current_middle = _read_config_middle_proxy()
    if current_middle != has_any_tag:
        # config-level change — restart اجباریه
        _log(
            f"⚠️ use_middle_proxy باید از {current_middle} به {has_any_tag} تغییر کنه "
            f"— restart کامل telemt لازمه"
        )
        await _restart_with_config(users, ad_tags, domain)
        return

    # use_middle_proxy عوض نشده — فقط config فایل رو آپدیت کن و از API استفاده کن
    write_config(users, ad_tags, port=TELEMT_PORT, domain=domain)

    try:
        current = await _api_list_usernames()
    except Exception as exc:
        _log(f"خواندن لیست کاربرهای فعلی telemt ناموفق بود: {exc}", "warning")
        current = set()

    for uid, secret in users.items():
        if uid not in current:
            try:
                await api_create_user(uid, secret)
            except Exception as exc:
                _log(f"ساخت کاربر {uid[:8]} در telemt ناموفق بود: {exc}", "error")
        tag = ad_tags.get(uid)
        try:
            await api_set_ad_tag(uid, tag)
        except Exception as exc:
            _log(f"تنظیم ad_tag برای {uid[:8]} ناموفق بود: {exc}", "warning")

    for uid in current - set(users.keys()):
        await api_delete_user(uid)


async def _api_list_usernames() -> set:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE}/v1/users", timeout=8.0)
        r.raise_for_status()
        data = r.json()
        items = data.get("data") or data.get("users") or []
        return {item.get("username") for item in items if item.get("username")}


def generate_mtproto_link(host: str, port: int, raw_secret: str, domain: str = DEFAULT_TLS_DOMAIN) -> str:
    return f"tg://proxy?server={host}&port={port}&secret={client_secret(raw_secret, domain)}"


def get_status() -> dict:
    return {
        "running": is_running(),
        "port": TELEMT_PORT,
        "logs": get_logs(100),
    }
