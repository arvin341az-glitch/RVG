# xhttpstreamup.py
# ══════════════════════════════════════════════════════════════════════════════
# XHTTP — آپلینک stream-up (یک POST پیوسته روی یک session) برای VLESS
# منطق اصلی (session, quota, adaptive flow) در xhttp_core.py قرار دارد.
# دقیقاً هم‌راستا با نسخه‌ی مرجع: بدون لاک روی هر chunk. اون لاک باعث می‌شد اگر
# rotation دو POST هم‌پوشان بفرسته، ترتیب بایت‌های نوشته‌شده روی TCP به‌هم بریزه
# (چون stream-up بر خلاف packet-up هیچ seq نداره) و همین باعث افت شدید سرعت
# (خرابی داده → قطع/ری‌ترای در لایه‌ی برنامه) می‌شد. اینجا هر session فقط با یک
# POST فعال در آنِ واحد نوشته می‌شه، دقیقاً مثل کد مرجع.
# ══════════════════════════════════════════════════════════════════════════════

import time
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException

from main import stats, connections, error_logs
from protocol.vless.xhttp_core import (
    _AdaptiveFlow,
    _QuotaGate,
    ensure_reaper,
    _get_or_create_session,
    _open_tcp_for_session,
    _req_client_ip,
    _teardown,
)

router = APIRouter()


# ══════════════════════════════ STREAM-UP (یک POST پیوسته) ══════════════════════════════
@router.post("/xhttp-siz10/stream-up/{uuid}/{session_id}")
async def stream_up_upload(uuid: str, session_id: str, request: Request):
    ensure_reaper()
    sess = await _get_or_create_session(uuid, "stream-up", session_id, _req_client_ip(request))
    if sess.get("closed"):
        raise HTTPException(status_code=404, detail="session closed")

    gate = sess.get("gate")
    if gate is None:
        gate = _QuotaGate(uuid, "upload")
        sess["gate"] = gate

    flow = sess.get("flow")
    if flow is None:
        flow = _AdaptiveFlow()
        sess["flow"] = flow

    conn = connections[sess["conn_id"]]   # یک بار لوک‌آپ، نه هر چانک
    writer = sess["writer"]               # ممکنه هنوز None باشه

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