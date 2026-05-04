"""WebSocket routes — token-authenticated, broker-backed fanout."""
import asyncio
import base64
import json
import time
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from server.auth import verify_token
from server.broker import broker
from server.plc_state import plc_state

router = APIRouter()


async def _authenticate(websocket: WebSocket, token: str | None) -> bool:
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return False
    payload = verify_token(token)
    if not payload or payload.get("type") == "refresh":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return False
    return True


@router.websocket("/api/ws/live")
async def ws_live(websocket: WebSocket, token: str | None = Query(default=None)):
    await websocket.accept()
    if not await _authenticate(websocket, token):
        return
    queue = await broker.subscribe()
    try:
        # Initial state push so dashboards aren't empty.
        await websocket.send_text(json.dumps({"type": "plc_status", **plc_state.snapshot()}))
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                await websocket.send_text(msg)
            except asyncio.TimeoutError:
                # Periodic keepalive
                await websocket.send_text(json.dumps({"type": "ping", "ts": time.time()}))
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await broker.unsubscribe(queue)


@router.websocket("/api/ws/camera")
async def ws_camera(websocket: WebSocket, token: str | None = Query(default=None)):
    """Stream camera frames. Frames are published as base64 JPEG via the broker
    using events of the form {"type": "frame", "frame": "<b64>"}.
    """
    await websocket.accept()
    if not await _authenticate(websocket, token):
        return
    queue = await broker.subscribe()
    try:
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=10.0)
                # Filter to frame events only.
                try:
                    obj = json.loads(msg)
                except Exception:
                    continue
                if obj.get("type") == "frame":
                    await websocket.send_text(msg)
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"type": "ping", "ts": time.time()}))
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await broker.unsubscribe(queue)
