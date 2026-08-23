# websocket.py
# ══════════════════════════════════════════════════════════════════════════════
# Shadowsocks — اندپوینت WebSocket (/ss-ws)
# رمزنگاری AEAD، پارس هدر و توابع کمکی در shadowsocks.py (هسته‌ی مشترک) هستند.
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
    save_state,
    log_activity,
)
from protocol.vless.vless import check_and_use, _QuotaGate
from protocol.shadowsocks.shadowsocks import (
    RELAY_BUF,
    WRITE_HIGH_WATER,
    _AEADStream,
    _ws_client_ip,
    _tune_socket,
    _find_matching_ss_link,
    parse_socks5_addr,
)


async def relay_ws_to_tcp(ws: WebSocket, writer: asyncio.StreamWriter, stream: _AEADStream, conn_id: str, uuid: str):
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
            stream.feed(data)
            try:
                for payload in stream.try_decrypt_chunks():
                    if not payload:
                        continue
                    if not await gate.add(len(payload)):
                        await ws.close(code=1008, reason="quota/disabled")
                        return
                    stats["total_requests"] += 1
                    if conn is not None:
                        conn["bytes"] += len(payload)
                    writer.write(payload)
            except ValueError:
                await ws.close(code=1008, reason="bad aead frame")
                return
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


async def relay_tcp_to_ws(ws: WebSocket, reader: asyncio.StreamReader, stream: _AEADStream, conn_id: str, uuid: str):
    gate = _QuotaGate(uuid, "download")
    conn = connections.get(conn_id)
    try:
        while True:
            data = await reader.read(RELAY_BUF)
            if not data:
                break
            if not await gate.add(len(data)):
                await ws.close(code=1008, reason="quota/disabled")
                break
            if conn is not None:
                conn["bytes"] += len(data)
            frame = stream.encrypt_chunk(data)
            await ws.send_bytes(frame)
    except Exception:
        pass
    finally:
        await gate.flush()


async def shadowsocks_ws_tunnel(ws: WebSocket):
    await ws.accept()
    ip = _ws_client_ip(ws)
    conn_id = secrets.token_urlsafe(6)
    writer = None
    uuid = None

    try:
        loop = asyncio.get_event_loop()
        deadline = loop.time() + 15.0
        raw = bytearray()
        uuid = stream = chunks = None

        while True:
            remaining = deadline - loop.time()
            if remaining <= 0:
                logger.warning(f"🚫 SS-WS timeout در جمع‌آوری هندشیک [{conn_id}] ip={ip}")
                await ws.close(code=1008, reason="handshake timeout")
                return

            msg = await asyncio.wait_for(ws.receive(), timeout=remaining)
            if msg["type"] == "websocket.disconnect":
                return

            chunk = msg.get("bytes") or (msg.get("text") or "").encode()
            if not chunk:
                continue

            raw += chunk
            if len(raw) > 64 * 1024:
                logger.warning(f"🚫 SS-WS هندشیک بیش‌ازحد بزرگ [{conn_id}] ip={ip}")
                await ws.close(code=1008, reason="handshake too large")
                return

            uuid, stream, chunks = await _find_matching_ss_link(bytes(raw))
            if uuid is not None:
                break

        if uuid is None:
            logger.warning(f"🚫 SS-WS rejected [{conn_id}] ip={ip} (no matching key)")
            await ws.close(code=1008, reason="not authorized")
            return

        first_chunk = bytes(raw)

        async with LINKS_LOCK:
            link = LINKS.get(uuid)

        connections[conn_id] = {
            "uuid": uuid,
            "ip": ip,
            "transport": "shadowsocks-ws",
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "bytes": 0,
        }
        logger.info(f"✅ SS-WS [{conn_id}] uuid={uuid[:8]}… ip={ip} total={len(connections)}")
        log_activity("connection", f"اتصال Shadowsocks جدید از {ip} (کانفیگ {link.get('label','?')})", "info")

        # اولین chunk رمزگشایی‌شده شامل هدر SOCKS5-like آدرس مقصد + احتمالاً payload اولیه است
        first_payload = chunks[0]
        address, port, hlen = parse_socks5_addr(first_payload)
        initial_data = first_payload[hlen:]
        extra_chunks = chunks[1:]

        if not await check_and_use(uuid, len(first_chunk), "upload"):
            await ws.close(code=1008, reason="quota/disabled")
            return
        stats["total_requests"] += 1
        connections[conn_id]["bytes"] += len(first_chunk)
        logger.info(f"➡️  [{conn_id}] SS → {address}:{port}")

        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(address, port), timeout=10.0
        )
        _tune_socket(writer)

        if initial_data:
            writer.write(initial_data)
        for c in extra_chunks:
            if c:
                writer.write(c)
        if initial_data or extra_chunks:
            await writer.drain()

        done, pending = await asyncio.wait(
            {
                asyncio.create_task(relay_ws_to_tcp(ws, writer, stream, conn_id, uuid)),
                asyncio.create_task(relay_tcp_to_ws(ws, reader, stream, conn_id, uuid)),
            },
            return_when=asyncio.FIRST_COMPLETED,
        )
        for t in pending:
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass

        asyncio.create_task(save_state())

    except WebSocketDisconnect:
        pass
    except asyncio.TimeoutError:
        stats["total_errors"] += 1
        error_logs.append({"error": "ss connection timeout", "time": datetime.now().isoformat()})
    except Exception as exc:
        stats["total_errors"] += 1
        error_logs.append({"error": str(exc), "time": datetime.now().isoformat()})
        logger.error(f"SS-WS error [{conn_id}]: {exc}")
    finally:
        if writer:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
        connections.pop(conn_id, None)
        logger.info(f"🔌 SS-WS closed [{conn_id}] total={len(connections)}")