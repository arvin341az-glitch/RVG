# websocket.py
# ══════════════════════════════════════════════════════════════════════════════
# Trojan — اندپوینت WebSocket (/trojan-ws)
# پارس هدر و QuotaGate در trojan.py (هسته‌ی مشترک) قرار دارند.
# ══════════════════════════════════════════════════════════════════════════════

import asyncio
import secrets
from datetime import datetime, timezone

from fastapi import WebSocket, WebSocketDisconnect

from main import (
    LINKS,
    LINKS_LOCK,
    stats,
    connections,
    error_logs,
    logger,
    schedule_save,
    log_activity,
)
from protocol.trojan.trojan import (
    RELAY_BUF,
    WRITE_HIGH_WATER,
    _QuotaGate,
    _ws_client_ip,
    _tune_socket,
    _resolve_and_authorize,
)
from protocol.vless.vless import check_and_use


async def _relay_ws_to_tcp(ws: WebSocket, writer: asyncio.StreamWriter, conn_id: str, uuid: str):
    gate = _QuotaGate(uuid, "upload")
    conn = connections.get(conn_id)
    try:
        while True:
            msg = await ws.receive()
            if msg["type"] == "websocket.disconnect":
                break
            data = msg.get("bytes") or (msg.get("text") or "").encode()
            if not data:
                continue
            if not await gate.add(len(data)):
                await ws.close(code=1008, reason="quota/disabled/unknown")
                break
            stats["total_requests"] += 1
            if conn is not None:
                conn["bytes"] += len(data)
            writer.write(data)
            # drain فقط وقتی واقعاً بافر پر باشه، نه هر بار
            if writer.transport.get_write_buffer_size() > WRITE_HIGH_WATER:
                await writer.drain()
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        await gate.flush()
        try:
            writer.write_eof()
        except Exception:
            pass


async def _relay_tcp_to_ws(ws: WebSocket, reader: asyncio.StreamReader, conn_id: str, uuid: str):
    gate = _QuotaGate(uuid, "download")
    conn = connections.get(conn_id)
    # Trojan: بدون response prefix (برخلاف VLESS که \x00\x00 نیاز داره)
    try:
        while True:
            data = await reader.read(RELAY_BUF)
            if not data:
                break
            if not await gate.add(len(data)):
                await ws.close(code=1008, reason="quota/disabled/unknown")
                break
            if conn is not None:
                conn["bytes"] += len(data)
            await ws.send_bytes(data)
    except Exception:
        pass
    finally:
        await gate.flush()


async def trojan_ws_tunnel(ws: WebSocket):
    """
    اندپوینت وب‌سوکت Trojan.
    پسورد داخل استریم اول فرستاده می‌شه، نه در URL.
    """
    await ws.accept()
    ip = _ws_client_ip(ws)
    conn_id = secrets.token_urlsafe(6)
    writer = None
    uuid = None

    try:
        first_msg = await asyncio.wait_for(ws.receive(), timeout=15.0)
        if first_msg["type"] == "websocket.disconnect":
            return
        first_chunk = first_msg.get("bytes") or (first_msg.get("text") or "").encode()
        if not first_chunk:
            return

        uuid, address, port, payload, hlen = await _resolve_and_authorize(first_chunk)
        if uuid is None:
            logger.warning(f"🚫 Trojan-WS rejected [{conn_id}] ip={ip} (not authorized)")
            await ws.close(code=1008, reason="not authorized")
            return

        async with LINKS_LOCK:
            link = LINKS.get(uuid)

        connections[conn_id] = {
            "uuid": uuid,
            "ip": ip,
            "transport": "trojan-ws",
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "bytes": 0,
        }
        logger.info(f"✅ Trojan-WS [{conn_id}] uuid={uuid[:8]}… ip={ip} total={len(connections)}")
        log_activity("connection", f"اتصال Trojan جدید از {ip} (کانفیگ {link.get('label','?')})", "info")

        if not await check_and_use(uuid, hlen, "upload"):
            await ws.close(code=1008, reason="quota/disabled")
            return

        stats["total_requests"] += 1
        connections[conn_id]["bytes"] += hlen
        logger.info(f"➡️  [{conn_id}] Trojan → {address}:{port}")

        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(address, port), timeout=10.0
        )
        _tune_socket(writer)

        if payload:
            writer.write(payload)
            await writer.drain()

        done, pending = await asyncio.wait(
            {
                asyncio.create_task(_relay_ws_to_tcp(ws, writer, conn_id, uuid)),
                asyncio.create_task(_relay_tcp_to_ws(ws, reader, conn_id, uuid)),
            },
            return_when=asyncio.FIRST_COMPLETED,
        )
        for t in pending:
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass

        asyncio.create_task(schedule_save())

    except WebSocketDisconnect as exc:
        logger.info(f"Trojan-WS [{conn_id}] client disconnected: code={getattr(exc,'code',None)}")
    except asyncio.TimeoutError:
        stats["total_errors"] += 1
        error_logs.append({"error": "trojan connection timeout", "time": datetime.now().isoformat()})
    except Exception as exc:
        stats["total_errors"] += 1
        error_logs.append({"error": str(exc), "time": datetime.now().isoformat()})
        logger.error(f"Trojan-WS error [{conn_id}]: {exc}")
    finally:
        if writer:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
        connections.pop(conn_id, None)
        logger.info(f"🔌 Trojan-WS closed [{conn_id}] total={len(connections)}")