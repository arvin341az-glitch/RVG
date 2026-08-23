# xhttpstreamup.py (trojan)
# ══════════════════════════════════════════════════════════════════════════════
# XHTTP — آپلینک stream-up اختصاصی Trojan (یک POST پیوسته روی یک session).
# مستقل از موتور VLESS، مسیر با پیشوند /txhttp-siz10.
# دقیقاً هم‌راستا با نسخه‌ی مرجع: بدون لاک روی هر chunk (دلیل حذف در
# protocol/vless/xhttpstreamup.py توضیح داده شده — همون منطق اینجا هم صادقه).
# ══════════════════════════════════════════════════════════════════════════════

import time
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException

from main import stats, connections, error_logs
from protocol.trojan.xhttp_core import (
    _TrojanAdaptiveFlow,
    _TrojanQuotaGate,
    ensure_reaper,
    _get_or_create_session,
    _open_tcp_for_session,
    _req_client_ip,
    _teardown,
)

router = APIRouter()


@router.post("/txhttp-siz10/stream-up/{uuid}/{session_id}")
async def trojan_stream_up_upload(uuid: str, session_id: str, request: Request):
    ensure_reaper()
    sess = await _get_or_create_session(uuid, "stream-up", session_id, _req_client_ip(request))
    if sess.get("closed"):
        raise HTTPException(status_code=404, detail="session closed")

    gate = sess.get("gate")
    if gate is None:
        gate = _TrojanQuotaGate(uuid, "upload")
        sess["gate"] = gate

    flow = sess.get("flow")
    if flow is None:
        flow = _TrojanAdaptiveFlow()
        sess["flow"] = flow

    conn = connections[sess["conn_id"]]
    writer = sess["writer"]

    try:
        async for chunk in request.stream():
            if not chunk:
                continue
            sess["last_seen"] = time.time()

            if not await gate.add(len(chunk)):
                raise HTTPException(status_code=403, detail="quota/disabled/unknown")

            stats["total_requests"] += 1
            conn["bytes"] += len(chunk)

            if writer is None:
                await _open_tcp_for_session(session_id, uuid, sess, chunk)
                writer = sess["writer"]
                continue

            if writer.is_closing():
                raise ConnectionError("transport closing")
            writer.write(chunk)
            if flow.should_drain(writer.transport.get_write_buffer_size()):
                await flow.drain(writer)
    except HTTPException:
        await gate.flush()
        await _teardown(session_id, reason="quota/http")
        raise
    except Exception as exc:
        error_logs.append({"error": str(exc), "time": datetime.now().isoformat()})
        await gate.flush()
        await _teardown(session_id, reason=f"stream-error: {type(exc).__name__}")
        raise HTTPException(status_code=502, detail="stream error")

    await gate.flush()
    return {"ok": True}