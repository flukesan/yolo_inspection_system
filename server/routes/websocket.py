"""WebSocket routes."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/api/ws/live")
async def ws_live(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f'{{"echo": "{data}"}}')
    except WebSocketDisconnect:
        pass

@router.websocket("/api/ws/camera")
async def ws_camera(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
            await websocket.send_text('{"frame": "base64_placeholder"}')
    except WebSocketDisconnect:
        pass
