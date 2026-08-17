# trojan.py
# ══════════════════════════════════════════════════════════════════════════════
# Trojan Relay — بهینه‌شده برای حداکثر throughput
#  بهبودها نسبت به نسخه‌ی قبل:
#   1. _TrojanHashCache: هش UUID‌ها رو cache می‌کنه → دیگه هر بار SHA224 محاسبه نمی‌شه
#   2. RELAY_BUF: 256KB → 1MB (4× بیشتر)
#   3. SO_SNDBUF / SO_RCVBUF بزرگ روی سوکت TCP
#   4. _QuotaGate تطبیقی (از xhttp_siz10) به‌جای check_and_use به‌ازای هر chunk
#   5. relay_ws_to_tcp: drain فقط وقتی بافر پر بشه، نه هر بار
#   6. relay_tcp_to_ws: خواندن با read(RELAY_BUF) بدون await اضافه
# ══════════════════════════════════════════════════════════════════════════════

import asyncio
import hashlib
import socket
import time

from fastapi import WebSocket

from main import (
    LINKS,
    LINKS_LOCK,
    logger,
    is_link_allowed,
)
from protocol.vless.vless import check_and_use

RELAY_BUF = 1024 * 1024          # 1 MB — 4× نسبت به قبل
SOCK_BUF = 4 * 1024 * 1024       # 4 MB بافر سوکت سطح OS
WRITE_HIGH_WATER = 512 * 1024    # drain فقط وقتی بیشتر از 512KB در بافر باشه
TROJAN_HEADER_MIN = 56 + 2 + 1 + 1 + 1 + 2 + 2

# تنظیمات QuotaGate تطبیقی
QUOTA_MIN_BATCH = 32 * 1024
QUOTA_MAX_BATCH = 2 * 1024 * 1024
QUOTA_START_BATCH = 128 * 1024
QUOTA_CHECK_INTERVAL = 0.25


# ══════════════════════════════════════════════════════════════════════════════
# Hash Cache — جلوگیری از محاسبه‌ی تکراری SHA224
# ══════════════════════════════════════════════════════════════════════════════

class _TrojanHashCache:
    """
    UUID → trojan_hash رو cache می‌کنه.
    هر بار که LINKS تغییر کنه (UUID اضافه/حذف بشه) باید invalidate بشه.
    از اونجا که LINKS یه dict ساده‌ست و تغییراتش نادره، ما فقط
    snapshot اندازه رو نگه می‌داریم و اگه عوض شد rebuild می‌کنیم.
    """
    def __init__(self):
        self._cache: dict[str, str] = {}   # hash → uuid
        self._snapshot_len: int = -1

    def _rebuild(self, links_snapshot: dict):
        self._cache = {
            hashlib.sha224(uid.encode()).hexdigest(): uid
            for uid in links_snapshot
        }
        self._snapshot_len = len(links_snapshot)

    async def find_uuid(self, pw_hash: str) -> str | None:
        async with LINKS_LOCK:
            if len(LINKS) != self._snapshot_len:
                self._rebuild(LINKS)
            return self._cache.get(pw_hash)


_hash_cache = _TrojanHashCache()


# ══════════════════════════════════════════════════════════════════════════════
# QuotaGate تطبیقی — کمتر await، throughput بالاتر
# ══════════════════════════════════════════════════════════════════════════════

class _QuotaGate:
    __slots__ = ("uuid", "pending", "last_check", "ok", "batch_bytes", "rate_ewma")

    def __init__(self, uuid: str):
        self.uuid = uuid
        self.pending = 0
        self.last_check = time.monotonic()
        self.ok = True
        self.batch_bytes = QUOTA_START_BATCH
        self.rate_ewma = 0.0

    async def add(self, nbytes: int) -> bool:
        if not self.ok:
            return False
        self.pending += nbytes
        now = time.monotonic()
        elapsed = now - self.last_check
        if self.pending >= self.batch_bytes or elapsed >= QUOTA_CHECK_INTERVAL:
            flush, self.pending = self.pending, 0
            if elapsed > 0:
                inst = flush / elapsed
                self.rate_ewma = inst if self.rate_ewma == 0 else (0.7 * self.rate_ewma + 0.3 * inst)
                target = int(self.rate_ewma * QUOTA_CHECK_INTERVAL)
                self.batch_bytes = max(QUOTA_MIN_BATCH, min(QUOTA_MAX_BATCH, target or QUOTA_MIN_BATCH))
            self.last_check = now
            try:
                self.ok = await check_and_use(self.uuid, flush)
            except Exception as exc:
                logger.error(f"Trojan _QuotaGate.add failed uuid={self.uuid[:8]}: {exc}")
                self.ok = False
        return self.ok

    async def flush(self) -> bool:
        if self.pending:
            flush, self.pending = self.pending, 0
            try:
                self.ok = self.ok and await check_and_use(self.uuid, flush)
            except Exception as exc:
                logger.error(f"Trojan _QuotaGate.flush failed uuid={self.uuid[:8]}: {exc}")
                self.ok = False
        return self.ok


# ══════════════════════════════════════════════════════════════════════════════
# توابع کمکی
# ══════════════════════════════════════════════════════════════════════════════

def _ws_client_ip(ws: WebSocket) -> str:
    fwd = ws.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    real_ip = ws.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return ws.client.host if ws.client else "نامشخص"


def trojan_hash(password: str) -> str:
    return hashlib.sha224(password.encode()).hexdigest()


async def find_uuid_by_trojan_hash(pw_hash: str) -> str | None:
    return await _hash_cache.find_uuid(pw_hash)


def _tune_socket(writer: asyncio.StreamWriter):
    """TCP_NODELAY + بافرهای بزرگ برای کاهش overhead سیستم‌عامل."""
    sock = writer.transport.get_extra_info("socket")
    if not sock:
        return
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SOCK_BUF)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, SOCK_BUF)
        if hasattr(socket, "TCP_QUICKACK"):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
    except OSError as e:
        logger.warning(f"Trojan _tune_socket failed: {e}")


async def parse_trojan_header(chunk: bytes):
    """
    فرمت Trojan:
      56 bytes hex(SHA224(password)) + CRLF + CMD(1) + ATYP(1) + ADDR + PORT(2) + CRLF + payload
    """
    if len(chunk) < TROJAN_HEADER_MIN:
        raise ValueError("chunk too small for trojan header")

    pw_hash = chunk[:56].decode("ascii", errors="ignore")
    pos = 56

    if chunk[pos:pos + 2] != b"\r\n":
        raise ValueError("invalid trojan header: missing CRLF after hash")
    pos += 2

    command = chunk[pos]; pos += 1
    atyp = chunk[pos]; pos += 1

    if atyp == 1:
        address = ".".join(str(b) for b in chunk[pos:pos + 4]); pos += 4
    elif atyp == 3:
        dlen = chunk[pos]; pos += 1
        address = chunk[pos:pos + dlen].decode("utf-8", errors="ignore"); pos += dlen
    elif atyp == 4:
        ab = chunk[pos:pos + 16]; pos += 16
        address = ":".join(f"{ab[i]:02x}{ab[i+1]:02x}" for i in range(0, 16, 2))
    else:
        raise ValueError(f"unknown trojan atyp: {atyp}")

    port = int.from_bytes(chunk[pos:pos + 2], "big"); pos += 2

    if chunk[pos:pos + 2] != b"\r\n":
        raise ValueError("invalid trojan header: missing trailing CRLF")
    pos += 2

    return pw_hash, command, address, port, chunk[pos:]


async def _resolve_and_authorize(first_chunk: bytes):
    pw_hash, command, address, port, payload = await parse_trojan_header(first_chunk)
    uuid = await find_uuid_by_trojan_hash(pw_hash)
    async with LINKS_LOCK:
        link = LINKS.get(uuid) if uuid else None
    if not is_link_allowed(link):
        return None, None, None, None, None
    return uuid, address, port, payload, len(first_chunk)


# اندپوینت trojan_ws_tunnel و توابع relay آن به protocol/trojan/websocket.py منتقل شدند.
# _QuotaGate اینجا باقی می‌ماند چون هم توسط websocket.py و هم منطق‌های دیگر استفاده می‌شود.
