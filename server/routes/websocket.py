"""
WebSocket routes — live telemetry + camera streaming.
"""

import asyncio
import json
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# ── camera singleton (lazy init) ──────────────────────────────────

_camera = None


def get_camera():
    """Lazy-init the camera capture singleton."""
    global _camera
    if _camera is None:
        # Defer OpenCV import so the server can start without it
        from server.camera import CameraCapture, CameraConfig
        from server.config import settings
        import os

        source = os.environ.get(
            "CAMERA_SOURCE",
            str(getattr(settings, "camera_source", "0"))
        )
        config = CameraConfig(
            source=source,
            width=getattr(settings, "camera_width", 1920),
            height=getattr(settings, "camera_height", 1080),
            fps=getattr(settings, "camera_fps", 30),
        )
        _camera = CameraCapture(config)
    return _camera


# ── live telemetry WS ─────────────────────────────────────────────

@router.websocket("/api/ws/live")
async def ws_live(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(json.dumps({"echo": data}))
    except WebSocketDisconnect:
        pass


# ── camera stream WS ──────────────────────────────────────────────

@router.websocket("/api/ws/camera")
async def ws_camera(websocket: WebSocket):
    await websocket.accept()

    camera = get_camera()
    opened = camera.open()

    # Send initial status
    await websocket.send_text(json.dumps({
        "type": "status",
        "connected": opened,
        "info": camera.info,
    }))

    # Calculate sleep interval to match target FPS
    interval = 1.0 / max(camera.config.fps, 1)
    frame_count = 0
    start_time = time.time()

    try:
        while True:
            # Non-blocking check for client messages (e.g. pause/resume)
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                # Handle control messages (future use)
                _ = json.loads(msg)
            except asyncio.TimeoutError:
                pass

            # Read & send frame
            success, b64 = camera.read_base64()
            if success and b64:
                payload = {
                    "type": "frame",
                    "data": b64,
                    "timestamp": time.time(),
                }
                await websocket.send_text(json.dumps(payload))
                frame_count += 1
            elif camera.is_opened:
                # Camera opened but read failed — skip frame
                pass
            else:
                # Camera not available — send fallback frame periodically
                if frame_count == 0 or frame_count % 30 == 0:
                    await websocket.send_text(json.dumps({
                        "type": "frame",
                        "data": camera.get_fallback_base64(),
                        "timestamp": time.time(),
                        "fallback": True,
                    }))

            # Pace to target FPS
            await asyncio.sleep(interval)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": str(e),
            }))
        except Exception:
            pass
    finally:
        camera.close()
        elapsed = time.time() - start_time
        actual_fps = frame_count / elapsed if elapsed > 0 else 0
        print(f"[camera] stream ended: {frame_count} frames in {elapsed:.1f}s "
              f"({actual_fps:.1f} fps)")
