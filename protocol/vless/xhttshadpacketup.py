# xhttshadpacketup.py
# ══════════════════════════════════════════════════════════════════════════════
# XHTTP — آپلینک packet-up (با seq) برای VLESS / Trojan
# منطق اصلی (session, quota) در xhttp_core.py قرار دارد.
# ══════════════════════════════════════════════════════════════════════════════

import time
import traceback
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException
from starlette.requests import ClientDisconnect

from main import stats, connections, error_logs, logger
from protocol.vless.xhttp_core import (
    PACKET_UP_HIGH_WATER,
    _QuotaGate,
    ensure_reaper,
    _get_or_create_session,
    _open_tcp_for_session,
    _req_client_ip,
    _teardown,
)

router = APIRouter()


# ══════════════════════════════ PACKET-UP (آپلینک با seq) ══════════════════════════════
@router.post("/xhttp-siz10/packet-up/{uuid}/{session_id}/{seq}")
async def packet_up_upload(uuid: str, session_id: str, seq: int, request: Request):
    ensure_reaper()
    sess = await _get_or_create_session(uuid, "packet-up", session_id, _req_client_ip(request))
    if sess.get("closed"):
        raise HTTPException(status_code=404, detail="session closed")

    sess["last_seen"] = time.time()
    try:
        body = await request.body()
    except ClientDisconnect:
        # کلاینت قبل از تکمیل ارسال بدنه قطع کرد؛ این یک POST رو نادیده بگیر،
        # ولی session/TCP رو دست‌نخورده نگه دار.
        logger.info(f"XHTTP[packet-up] [{session_id[:8]}] client disconnected mid-body (seq={seq}), session kept alive")
        return {"ok": True, "aborted": True}

    if not body:
        return {"ok": True}

    # قبلاً هر پکت جدا await check_and_use() می‌کرد => هر POST کوچیک قفل
    # سراسری LINKS_LOCK رو می‌گرفت. چون packet-up ذاتاً پکت‌های کوچیک و زیاد
    # می‌فرسته (برخلاف stream-up که یک POST پیوسته‌ست)، این یعنی صدها await
    # روی یک لاک مشترک به‌ازای هر ثانیه -> همون چیزی که سرعت آپلود رو به چند
    # صد kbps محدود می‌کرد. الان از همون _QuotaGate تطبیقی که stream-up
    # استفاده می‌کنه بهره می‌بریم: batch میشه و فقط هر چند صد KB یا هر 250ms
    # یک‌بار واقعاً await check_and_use می‌شه.
    gate = sess.get("gate")
    if gate is None:
        gate = _QuotaGate(uuid)
        sess["gate"] = gate
    if not await gate.add(len(body)):
        await _teardown(session_id, reason="quota/disabled/unknown")
        raise HTTPException(status_code=403, detail="quota/disabled/unknown")

    stats["total_requests"] += 1
    connections[sess["conn_id"]]["bytes"] += len(body)

    try:
        if sess["writer"] is None:
            if seq != 0:
                sess["seq_buf"][seq] = body
                return {"ok": True, "buffered": True}
            await _open_tcp_for_session(session_id, uuid, sess, body)
            nxt = 1
            while nxt in sess["seq_buf"]:
                pending = sess["seq_buf"].pop(nxt)
                if sess["writer"].is_closing():
                    raise ConnectionError("transport closing")
                sess["writer"].write(pending)
                nxt += 1
            sess["next_seq"] = nxt
            return {"ok": True, "connected": True}

        if seq == sess["next_seq"]:
            if sess["writer"].is_closing():
                raise ConnectionError("transport closing")
            sess["writer"].write(body)
            sess["next_seq"] += 1
            while sess["next_seq"] in sess["seq_buf"]:
                pending = sess["seq_buf"].pop(sess["next_seq"])
                if sess["writer"].is_closing():
                    raise ConnectionError("transport closing")
                sess["writer"].write(pending)
                sess["next_seq"] += 1
        else:
            sess["seq_buf"][seq] = body

        if sess["writer"].transport.get_write_buffer_size() > PACKET_UP_HIGH_WATER:
            await sess["writer"].drain()
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error(f"XHTTP[packet-up] [{session_id[:8]}] upload FAILED seq={seq}: {type(exc).__name__}: {exc}\n{tb}")
        error_logs.append({"error": f"packet-up write failed: {type(exc).__name__}: {exc}", "time": datetime.now().isoformat()})
        await _teardown(session_id, reason=f"write-failed: {type(exc).__name__}")
        raise HTTPException(status_code=502, detail="write failed")

    return {"ok": True}
