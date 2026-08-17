

import asyncio
import logging
import secrets
import socket
import string
import time
from collections import defaultdict
from typing import Optional

import bottokentcpproxy

logger = logging.getLogger("RVG-Gateway")

IDLE_TIMEOUT = 300  # ثانیه؛ اگه هر دو طرف ساکت بود می‌بندیمش

# ── پیش‌فرض کانفیگ ──
DEFAULT_TRAFFIC_LIMIT_GB = 10.0   # گیگابایت — 0 = نامحدود
DEFAULT_EXPIRES_DAYS = 30          # روز — 0 = بی‌انقضا
DEFAULT_MAX_CONNECTIONS_PER_IP = 3 # حداکثر اتصال همزمان از یک IP — 0 = نامحدود

zeus_proxy_state = {
    "running": False,
    "phase": "idle",      # idle | starting | done | error
    "result": None,        # dict کامل پروکسی
    "error": None,
    # ── آمار مصرف ──
    "bytes_used": 0,       # بایت استفاده‌شده
    "connections_by_ip": {},  # IP -> تعداد اتصال فعال
    "active_connections": 0,
    # ── کانفیگ‌ها ──
    "config": {
        "traffic_limit_gb": DEFAULT_TRAFFIC_LIMIT_GB,
        "expires_days": DEFAULT_EXPIRES_DAYS,
        "max_connections_per_ip": DEFAULT_MAX_CONNECTIONS_PER_IP,
    },
}

_server: Optional[asyncio.base_events.Server] = None
_creds = {"user": None, "password": None}
_connections_by_ip: dict = defaultdict(int)
_bytes_lock = asyncio.Lock() if False else None  # lazy init در event loop


def _rand(n: int, alphabet: str) -> str:
    return "".join(secrets.choice(alphabet) for _ in range(n))


def _free_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))
        return s.getsockname()[1]


def _is_expired() -> bool:
    result = zeus_proxy_state.get("result")
    if not result:
        return False
    expires_days = zeus_proxy_state["config"]["expires_days"]
    if not expires_days:
        return False
    created_at = result.get("created_at", 0)
    return time.time() - created_at > expires_days * 86400


def _is_traffic_exceeded() -> bool:
    limit_gb = zeus_proxy_state["config"]["traffic_limit_gb"]
    if not limit_gb:
        return False
    limit_bytes = limit_gb * 1024 ** 3
    return zeus_proxy_state["bytes_used"] >= limit_bytes


async def _pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, peer_ip: str):
    try:
        while True:
            chunk = await asyncio.wait_for(reader.read(65536), timeout=IDLE_TIMEOUT)
            if not chunk:
                break
            # بررسی انقضا / حجم در حین انتقال
            if _is_expired() or _is_traffic_exceeded():
                break
            writer.write(chunk)
            await writer.drain()
            # ثبت بایت مصرف‌شده
            zeus_proxy_state["bytes_used"] += len(chunk)
    except (asyncio.TimeoutError, ConnectionResetError, BrokenPipeError, OSError):
        pass
    finally:
        try:
            writer.close()
        except Exception:
            pass


async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info("peername")
    peer_ip = peer[0] if peer else "unknown"

    # ── بررسی انقضا و حجم قبل از پذیرش ──
    if _is_expired():
        logger.info(f"ZeusSocks5: رد شد (منقضی) — {peer_ip}")
        writer.close()
        return
    if _is_traffic_exceeded():
        logger.info(f"ZeusSocks5: رد شد (حجم تمام شد) — {peer_ip}")
        writer.close()
        return

    # ── بررسی حداکثر اتصال per IP ──
    max_per_ip = zeus_proxy_state["config"]["max_connections_per_ip"]
    if max_per_ip and _connections_by_ip.get(peer_ip, 0) >= max_per_ip:
        logger.info(f"ZeusSocks5: رد شد (حداکثر اتصال از {peer_ip}) ← {_connections_by_ip.get(peer_ip)}/{max_per_ip}")
        writer.close()
        return

    _connections_by_ip[peer_ip] = _connections_by_ip.get(peer_ip, 0) + 1
    zeus_proxy_state["active_connections"] = zeus_proxy_state.get("active_connections", 0) + 1
    zeus_proxy_state["connections_by_ip"] = dict(_connections_by_ip)

    try:
        # ── مرحله ۱: handshake ──
        head = await reader.readexactly(2)
        if head[0] != 0x05:
            return
        nmethods = head[1]
        methods = await reader.readexactly(nmethods)
        if 0x02 not in methods:
            writer.write(b"\x05\xff")
            await writer.drain()
            return
        writer.write(b"\x05\x02")
        await writer.drain()

        # ── مرحله ۲: احراز هویت (RFC1929) ──
        auth_head = await reader.readexactly(2)
        ulen = auth_head[1]
        uname = (await reader.readexactly(ulen)).decode(errors="ignore")
        plen_b = await reader.readexactly(1)
        plen = plen_b[0]
        passwd = (await reader.readexactly(plen)).decode(errors="ignore")

        if uname != _creds["user"] or passwd != _creds["password"]:
            writer.write(b"\x01\x01")
            await writer.drain()
            return
        writer.write(b"\x01\x00")
        await writer.drain()

        # ── مرحله ۳: درخواست اتصال ──
        req_head = await reader.readexactly(4)
        ver, cmd, _rsv, atyp = req_head
        if ver != 0x05 or cmd != 0x01:
            writer.write(b"\x05\x07\x00\x01\x00\x00\x00\x00\x00\x00")
            await writer.drain()
            return

        if atyp == 0x01:
            addr_bytes = await reader.readexactly(4)
            dst_addr = socket.inet_ntoa(addr_bytes)
        elif atyp == 0x03:
            dlen_b = await reader.readexactly(1)
            dst_addr = (await reader.readexactly(dlen_b[0])).decode(errors="ignore")
        elif atyp == 0x04:
            addr_bytes = await reader.readexactly(16)
            dst_addr = socket.inet_ntop(socket.AF_INET6, addr_bytes)
        else:
            writer.write(b"\x05\x08\x00\x01\x00\x00\x00\x00\x00\x00")
            await writer.drain()
            return

        port_bytes = await reader.readexactly(2)
        dst_port = int.from_bytes(port_bytes, "big")

        try:
            remote_reader, remote_writer = await asyncio.wait_for(
                asyncio.open_connection(dst_addr, dst_port), timeout=10.0
            )
        except Exception:
            writer.write(b"\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00")
            await writer.drain()
            return

        writer.write(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")
        await writer.drain()

        await asyncio.gather(
            _pipe(reader, remote_writer, peer_ip),
            _pipe(remote_reader, writer, peer_ip),
            return_exceptions=True,
        )
    except (asyncio.IncompleteReadError, ConnectionResetError, OSError):
        pass
    except Exception as exc:
        logger.warning(f"ZeusSocks5: خطای غیرمنتظره برای {peer_ip}: {exc}")
    finally:
        try:
            writer.close()
        except Exception:
            pass
        _connections_by_ip[peer_ip] = max(0, _connections_by_ip.get(peer_ip, 1) - 1)
        if _connections_by_ip[peer_ip] == 0:
            _connections_by_ip.pop(peer_ip, None)
        zeus_proxy_state["active_connections"] = max(0, zeus_proxy_state.get("active_connections", 1) - 1)
        zeus_proxy_state["connections_by_ip"] = dict(_connections_by_ip)

        # اگه حجم تموم شد یا منقضی شده، پروکسی رو حذف کن
        if _is_traffic_exceeded() or _is_expired():
            asyncio.get_event_loop().create_task(_auto_delete("حجم تمام شد" if _is_traffic_exceeded() else "منقضی شد"))


async def _auto_delete(reason: str):
    logger.info(f"ZeusSocks5: حذف خودکار — {reason}")
    try:
        await delete_zeus_proxy()
    except Exception as e:
        logger.warning(f"ZeusSocks5: خطا در حذف خودکار: {e}")


async def _ensure_local_server() -> int:
    global _server
    if _server is not None:
        return _server.sockets[0].getsockname()[1]

    _creds["user"] = _rand(8, string.ascii_lowercase)
    _creds["password"] = _rand(14, string.ascii_letters + string.digits)
    port = _free_local_port()

    _server = await asyncio.start_server(_handle_client, "0.0.0.0", port)
    logger.info(f"ZeusSocks5: سرور محلی روی پورت {port} بالا آمد")
    return port


async def create_zeus_proxy(
    token: Optional[str] = None,
    traffic_limit_gb: Optional[float] = None,
    expires_days: Optional[int] = None,
    max_connections_per_ip: Optional[int] = None,
) -> dict:
    """ساخت پروکسی Zeus با کانفیگ‌های حجم، انقضا و محدودیت اتصال per IP."""
    token = (token or "").strip()
    if token:
        bottokentcpproxy.save_token(token)
    if not bottokentcpproxy.has_saved_token():
        raise RuntimeError("توکن Railway وارد نشده و توکن ذخیره‌شده‌ای هم وجود ندارد")

    # ── اعمال کانفیگ‌ها ──
    cfg = zeus_proxy_state["config"]
    if traffic_limit_gb is not None:
        cfg["traffic_limit_gb"] = max(0.0, float(traffic_limit_gb))
    if expires_days is not None:
        cfg["expires_days"] = max(0, int(expires_days))
    if max_connections_per_ip is not None:
        cfg["max_connections_per_ip"] = max(0, int(max_connections_per_ip))

    zeus_proxy_state.update({"running": True, "phase": "starting", "error": None, "bytes_used": 0})
    _connections_by_ip.clear()
    zeus_proxy_state["active_connections"] = 0
    zeus_proxy_state["connections_by_ip"] = {}

    try:
        local_port = await _ensure_local_server()
        pub = await bottokentcpproxy.create_public_proxy_for_port(local_port)
        config_str = f"{_creds['user']}:{_creds['password']}@{pub['domain']}:{pub['port']}"
        result = {
            "user": _creds["user"],
            "password": _creds["password"],
            "local_port": local_port,
            "domain": pub["domain"],
            "public_port": pub["port"],
            "proxy_id": pub["id"],
            "config": config_str,
            "created_at": time.time(),
            "traffic_limit_gb": cfg["traffic_limit_gb"],
            "expires_days": cfg["expires_days"],
            "max_connections_per_ip": cfg["max_connections_per_ip"],
        }
        zeus_proxy_state.update({"running": True, "phase": "done", "result": result, "error": None})
        return result
    except Exception as exc:
        zeus_proxy_state.update({"running": False, "phase": "error", "error": str(exc)})
        raise


async def delete_zeus_proxy():
    """TCP Proxy عمومی رو حذف و سرور SOCKS5 محلی رو می‌بندد."""
    global _server
    result = zeus_proxy_state.get("result")
    if result and result.get("proxy_id"):
        try:
            await bottokentcpproxy.delete_public_proxy(result["proxy_id"])
        except Exception as e:
            logger.warning(f"ZeusSocks5: خطا در حذف TCP Proxy: {e}")
    if _server is not None:
        _server.close()
        await _server.wait_closed()
        _server = None
    _creds["user"] = None
    _creds["password"] = None
    _connections_by_ip.clear()
    zeus_proxy_state.update({
        "running": False,
        "phase": "idle",
        "result": None,
        "error": None,
        "bytes_used": 0,
        "active_connections": 0,
        "connections_by_ip": {},
    })


def get_zeus_status() -> dict:
    result = zeus_proxy_state.get("result")
    cfg = zeus_proxy_state["config"]
    extra = {}
    if result:
        # محاسبه درصد حجم مصرفی
        limit_bytes = cfg["traffic_limit_gb"] * 1024 ** 3 if cfg["traffic_limit_gb"] else 0
        used = zeus_proxy_state.get("bytes_used", 0)
        extra["bytes_used"] = used
        extra["bytes_used_gb"] = round(used / (1024 ** 3), 3)
        extra["traffic_limit_bytes"] = limit_bytes
        extra["traffic_percent"] = round(used / limit_bytes * 100, 1) if limit_bytes else None
        # محاسبه روزهای مانده
        created_at = result.get("created_at", 0)
        if cfg["expires_days"]:
            elapsed = time.time() - created_at
            remaining_sec = cfg["expires_days"] * 86400 - elapsed
            extra["expires_remaining_hours"] = round(max(0, remaining_sec) / 3600, 1)
        else:
            extra["expires_remaining_hours"] = None
        extra["is_expired"] = _is_expired()
        extra["is_traffic_exceeded"] = _is_traffic_exceeded()
    return {
        **zeus_proxy_state,
        "has_token": bottokentcpproxy.has_saved_token(),
        **extra,
    }


def update_zeus_config(
    traffic_limit_gb: Optional[float] = None,
    expires_days: Optional[int] = None,
    max_connections_per_ip: Optional[int] = None,
) -> dict:
    """تغییر کانفیگ‌ها بدون ری‌استارت پروکسی (اعمال فوری)."""
    cfg = zeus_proxy_state["config"]
    if traffic_limit_gb is not None:
        cfg["traffic_limit_gb"] = max(0.0, float(traffic_limit_gb))
    if expires_days is not None:
        cfg["expires_days"] = max(0, int(expires_days))
    if max_connections_per_ip is not None:
        cfg["max_connections_per_ip"] = max(0, int(max_connections_per_ip))
    # به‌روزرسانی result هم اگه پروکسی فعال است
    result = zeus_proxy_state.get("result")
    if result:
        result["traffic_limit_gb"] = cfg["traffic_limit_gb"]
        result["expires_days"] = cfg["expires_days"]
        result["max_connections_per_ip"] = cfg["max_connections_per_ip"]
    return cfg
