# xhttp_core.py (trojan)
# ══════════════════════════════════════════════════════════════════════════════
# Trojan XHTTP Core — موتور اختصاصیِ session/quota/flow برای ترنسپورت XHTTP
# روی Trojan. کاملاً مستقل از protocol/vless/xhttp_core.py (بدون فراخوانی
# متقابل و بدون شاخه‌زدن is_trojan) تا هر پروتکل بتونه جدا بهینه/تیون بشه.
#
# تفاوت با VLESS: هدر Trojan نیازی به پیشوند \x00\x00 روی response نداره
# (برخلاف VLESS که برای فریم اول downlink باید 2 بایت اضافه بشه)، و احراز
# هویت هم بر اساس هش پسورد Trojan (نه UUID مستقیم توی هدر) انجام می‌شه.
# ══════════════════════════════════════════════════════════════════════════════

import asyncio
import secrets
import socket
import time
import traceback
from datetime import datetime, timezone

from fastapi import Request, HTTPException

from main import (
    LINKS,
    LINKS_LOCK,
    connections,
    error_logs,
    logger,
    is_link_allowed,
    save_state,
)
from protocol.vless.vless import check_and_use
from protocol.trojan.trojan import parse_trojan_header, find_uuid_by_trojan_hash

TROJAN_XHTTP_BUF = 1024 * 1024        # 1MB — هماهنگ با سایر پروتکل‌ها
TROJAN_DOWNLINK_QUEUE_MAX = 512
TROJAN_SESSION_IDLE_TIMEOUT = 30
TROJAN_SESSION_IDLE_TIMEOUT_ACTIVE = 90
TROJAN_REAPER_INTERVAL = 10
TROJAN_TCP_CONNECT_TIMEOUT = 10.0

TROJAN_SOCK_BUF_SIZE = 4 * 1024 * 1024

# ── AdaptiveFlow (AIMD) مخصوص Trojan-XHTTP ────────────────────────────────────
TROJAN_FLOW_MIN_HW = 256 * 1024
TROJAN_FLOW_MAX_HW = 32 * 1024 * 1024
TROJAN_FLOW_START_HW = 2 * 1024 * 1024   # شروع متعادل (نه ۸MB، نه ۵۱۲KB)
TROJAN_FLOW_FAST_DRAIN_MS = 12.0   # قبلاً 2.0 — خیلی سخت‌گیرانه بود، رو لینک ضعیف
                                    # هیچ‌وقت شرط رشد برقرار نمی‌شد و بافر قفل می‌موند
TROJAN_FLOW_SLOW_DRAIN_MS = 40.0   # قبلاً 25.0

# ── QuotaGate تطبیقی مخصوص Trojan-XHTTP ───────────────────────────────────────
TROJAN_QUOTA_MIN_BATCH = 32 * 1024
TROJAN_QUOTA_MAX_BATCH = 4 * 1024 * 1024
TROJAN_QUOTA_START_BATCH = 256 * 1024
TROJAN_QUOTA_CHECK_INTERVAL = 0.25

TROJAN_PACKET_UP_HIGH_WATER = 2 * 1024 * 1024

trojan_xhttp_sessions: dict = {}
TROJAN_XHTTP_LOCK = asyncio.Lock()

TROJAN_FINGERPRINTS = {
    "chrome": {
        "content-type": "application/grpc",
        "cache-control": "no-cache, no-store",
        "x-accel-buffering": "no",
        "server": "cloudflare",
    },
    "plain": {
        "content-type": "application/octet-stream",
        "cache-control": "no-store",
        "x-accel-buffering": "no",
    },
}
TROJAN_DEFAULT_FINGERPRINT = "chrome"


def _resp_headers(fp: str) -> dict:
    return dict(TROJAN_FINGERPRINTS.get(fp, TROJAN_FINGERPRINTS[TROJAN_DEFAULT_FINGERPRINT]))


def _tune_socket(writer: asyncio.StreamWriter):
    """TCP_NODELAY + بافرهای بزرگ‌تر سوکت مخصوص Trojan-XHTTP."""
    sock = writer.transport.get_extra_info("socket")
    if not sock:
        return
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, TROJAN_SOCK_BUF_SIZE)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, TROJAN_SOCK_BUF_SIZE)
        if hasattr(socket, "TCP_QUICKACK"):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
    except OSError as e:
        logger.warning(f"Trojan-XHTTP _tune_socket failed: {e}")


class _TrojanQuotaGate:
    """batch quota check تطبیقی (EWMA)، مستقل از موتور VLESS."""
    __slots__ = ("uuid", "pending", "last_check", "ok", "batch_bytes", "rate_ewma")

    def __init__(self, uuid: str):
        self.uuid = uuid
        self.pending = 0
        self.last_check = time.monotonic()
        self.ok = True
        self.batch_bytes = TROJAN_QUOTA_START_BATCH
        self.rate_ewma = 0.0

    async def add(self, nbytes: int) -> bool:
        if not self.ok:
            return False
        self.pending += nbytes
        now = time.monotonic()
        elapsed = now - self.last_check
        if self.pending >= self.batch_bytes or elapsed >= TROJAN_QUOTA_CHECK_INTERVAL:
            flush, self.pending = self.pending, 0
            if elapsed > 0:
                inst_rate = flush / elapsed
                self.rate_ewma = inst_rate if self.rate_ewma == 0 else (0.7 * self.rate_ewma + 0.3 * inst_rate)
                target = int(self.rate_ewma * TROJAN_QUOTA_CHECK_INTERVAL)
                self.batch_bytes = max(TROJAN_QUOTA_MIN_BATCH, min(TROJAN_QUOTA_MAX_BATCH, target or TROJAN_QUOTA_MIN_BATCH))
            self.last_check = now
            try:
                self.ok = await check_and_use(self.uuid, flush)
            except Exception as exc:
                logger.error(f"Trojan-XHTTP QuotaGate.add failed uuid={self.uuid[:8]}: {type(exc).__name__}: {exc}")
                self.ok = False
            return self.ok
        return True

    async def flush(self) -> bool:
        if self.pending:
            flush, self.pending = self.pending, 0
            try:
                self.ok = self.ok and await check_and_use(self.uuid, flush)
            except Exception as exc:
                logger.error(f"Trojan-XHTTP QuotaGate.flush failed uuid={self.uuid[:8]}: {type(exc).__name__}: {exc}")
                self.ok = False
        return self.ok


class _TrojanAdaptiveFlow:
    """high-water تطبیقی برای drain()، مستقل از موتور VLESS."""
    __slots__ = ("high_water", "last_drain_ms")

    def __init__(self):
        self.high_water = TROJAN_FLOW_START_HW
        self.last_drain_ms = 0.0

    def should_drain(self, buf_size: int) -> bool:
        return buf_size > self.high_water

    async def drain(self, writer: asyncio.StreamWriter):
        t0 = time.monotonic()
        await writer.drain()
        elapsed_ms = (time.monotonic() - t0) * 1000
        self.last_drain_ms = elapsed_ms
        if elapsed_ms < TROJAN_FLOW_FAST_DRAIN_MS:
            self.high_water = min(TROJAN_FLOW_MAX_HW, int(self.high_water * 2.0) + 65536)
        elif elapsed_ms > TROJAN_FLOW_SLOW_DRAIN_MS:
            self.high_water = max(TROJAN_FLOW_MIN_HW, self.high_water // 2)


def _req_client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "نامشخص"


async def _open_tcp_from_trojan_header(first_chunk: bytes):
    """هدر Trojan رو پارس، هش پسورد رو برای احراز هویت resolve و TCP مقصد رو باز می‌کنه."""
    pw_hash, command, address, port, payload = await parse_trojan_header(first_chunk)
    resolved_uuid = await find_uuid_by_trojan_hash(pw_hash)
    if resolved_uuid is None:
        raise ValueError("trojan auth failed")

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(address, port), timeout=TROJAN_TCP_CONNECT_TIMEOUT
        )
    except asyncio.TimeoutError:
        logger.error(f"Trojan-XHTTP TCP connect TIMEOUT -> {address}:{port} (>{TROJAN_TCP_CONNECT_TIMEOUT}s)")
        raise
    except OSError as exc:
        logger.error(f"Trojan-XHTTP TCP connect FAILED -> {address}:{port}: {type(exc).__name__}: {exc}")
        raise

    _tune_socket(writer)
    if payload:
        writer.write(payload)
        await writer.drain()
    return reader, writer, address, port


async def _check_link(uuid: str):
    async with LINKS_LOCK:
        link = LINKS.get(uuid)
    proto = (link or {}).get("protocol", "") or ""
    if not link or not proto.startswith("trojan") or not is_link_allowed(link):
        raise HTTPException(status_code=403, detail="not authorized")


async def _get_or_create_session(uuid: str, mode: str, session_id: str, ip: str = "نامشخص") -> dict:
    """Session بر اساس session_id که خودِ کلاینت در URL می‌فرسته، lazily ساخته می‌شه."""
    async with TROJAN_XHTTP_LOCK:
        sess = trojan_xhttp_sessions.get(session_id)
        if sess is not None:
            sess["last_seen"] = time.time()
            return sess
        conn_id = secrets.token_urlsafe(6)
        connections[conn_id] = {
            "uuid": uuid,
            "ip": ip,
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "bytes": 0,
            "transport": f"trojan-xhttp-{mode}",
        }
        sess = {
            "uuid": uuid, "mode": mode, "writer": None,
            "downlink_task": None, "uplink_task": None,
            "down_q": asyncio.Queue(maxsize=TROJAN_DOWNLINK_QUEUE_MAX),
            "last_seen": time.time(),
            "conn_id": conn_id, "tcp_open": False, "closed": False,
            "seq_buf": {}, "next_seq": 0,
            "gate": None,   # لازی: _TrojanQuotaGate مخصوص stream-up
            "flow": None,   # لازی: _TrojanAdaptiveFlow مخصوص stream-up
        }
        trojan_xhttp_sessions[session_id] = sess
        logger.info(f"new Trojan-XHTTP[{mode}] session [{session_id[:8]}] uuid={uuid[:8]} ip={ip}")
        return sess


async def _teardown(session_id: str, reason: str = ""):
    async with TROJAN_XHTTP_LOCK:
        sess = trojan_xhttp_sessions.pop(session_id, None)
    if not sess:
        return
    sess["closed"] = True
    for t in ("uplink_task", "downlink_task"):
        task = sess.get(t)
        if task:
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass
    writer = sess.get("writer")
    if writer:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
    connections.pop(sess.get("conn_id"), None)
    dq = sess.get("down_q")
    if dq:
        try:
            dq.put_nowait(None)
        except Exception:
            pass
    suffix = f" reason={reason}" if reason else ""
    logger.info(f"closed Trojan-XHTTP[{sess.get('mode')}] [{session_id[:8]}] total={len(trojan_xhttp_sessions)}{suffix}")


async def _reaper():
    while True:
        await asyncio.sleep(TROJAN_REAPER_INTERVAL)
        now = time.time()
        async with TROJAN_XHTTP_LOCK:
            stale = []
            for sid, s in trojan_xhttp_sessions.items():
                idle = now - s["last_seen"]
                if s.get("tcp_open"):
                    if idle > TROJAN_SESSION_IDLE_TIMEOUT_ACTIVE:
                        stale.append(sid)
                else:
                    if idle > TROJAN_SESSION_IDLE_TIMEOUT:
                        stale.append(sid)
        for sid in stale:
            await _teardown(sid, reason="idle-timeout")


_reaper_started = False


def ensure_reaper():
    global _reaper_started
    if not _reaper_started:
        asyncio.create_task(_reaper())
        _reaper_started = True


async def _pump_tcp_to_queue(session_id: str, uuid: str, reader: asyncio.StreamReader, down_q: asyncio.Queue, conn_id: str = ""):
    """Trojan نیازی به پیشوند \\x00\\x00 نداره — برخلاف VLESS، فریم اول دستکاری نمی‌شه."""
    gate = _TrojanQuotaGate(uuid)
    close_reason = "remote-eof"
    cached_conn = connections.get(conn_id) if conn_id else None
    try:
        while True:
            try:
                data = await reader.read(TROJAN_XHTTP_BUF)
            except (ConnectionResetError, OSError) as exc:
                close_reason = f"tcp-read-error: {type(exc).__name__}: {exc}"
                logger.warning(f"Trojan-XHTTP[{session_id[:8]}] downlink read error: {close_reason}")
                break
            if not data:
                break
            if not await gate.add(len(data)):
                close_reason = "quota-exceeded"
                logger.warning(f"Trojan-XHTTP[{session_id[:8]}] downlink quota exceeded, closing")
                break
            if cached_conn is not None:
                cached_conn["bytes"] += len(data)
            await down_q.put(data)
    except asyncio.CancelledError:
        close_reason = "cancelled"
    except Exception as exc:
        tb = traceback.format_exc()
        close_reason = f"unexpected: {type(exc).__name__}: {exc}"
        logger.error(f"Trojan-XHTTP[{session_id[:8]}] downlink pump crashed: {type(exc).__name__}: {exc}\n{tb}")
    finally:
        await gate.flush()
        await _teardown(session_id, reason=close_reason)


async def _open_tcp_for_session(session_id: str, uuid: str, sess: dict, first_chunk: bytes):
    try:
        reader, writer, address, port = await _open_tcp_from_trojan_header(first_chunk)
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error(f"Trojan-XHTTP[{sess['mode']}] [{session_id[:8]}] connect/parse FAILED: {type(exc).__name__}: {exc}\n{tb}")
        error_logs.append({"error": f"trojan-xhttp connect failed: {type(exc).__name__}: {exc}", "time": datetime.now().isoformat()})
        raise
    logger.info(f"connect Trojan-XHTTP[{sess['mode']}] [{session_id[:8]}] -> {address}:{port}")
    sess["writer"] = writer
    sess["tcp_open"] = True
    sess["downlink_task"] = asyncio.create_task(
        _pump_tcp_to_queue(session_id, uuid, reader, sess["down_q"], conn_id=sess["conn_id"])
    )
    asyncio.create_task(save_state())


def _downstream_gen(sess: dict):
    async def gen():
        try:
            while True:
                chunk = await sess["down_q"].get()
                if chunk is None:
                    break
                sess["last_seen"] = time.time()
                yield chunk
        finally:
            pass
    return gen()
