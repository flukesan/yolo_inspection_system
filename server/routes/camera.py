"""
Camera management routes — config, status, restart.
"""

import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from server.auth import get_current_user, require_role
from server.config import settings
from server.routes.websocket import get_camera

router = APIRouter(prefix="/api/camera", tags=["camera"])


# ── Models ───────────────────────────────────────────────────────

class CameraConfigOut(BaseModel):
    source: str
    width: int
    height: int
    fps: int
    jpeg_quality: int
    source_type: str
    connected: bool
    actual_resolution: str
    actual_fps: float

class CameraConfigUpdate(BaseModel):
    source: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[int] = None
    jpeg_quality: Optional[int] = None


# ── GET config ───────────────────────────────────────────────────

@router.get("/config")
async def get_camera_config(user: dict = Depends(get_current_user)):
    """Return current camera configuration and live status."""
    cam = get_camera()
    info = cam.info

    return CameraConfigOut(
        source=cam.config.source,
        width=cam.config.width,
        height=cam.config.height,
        fps=cam.config.fps,
        jpeg_quality=cam.config.jpeg_quality,
        source_type=info["type"],
        connected=info["connected"],
        actual_resolution=info["actual"],
        actual_fps=float(info["actual"].split("@")[1].rstrip("fps")) if "@" in info["actual"] else 0.0,
    )


# ── UPDATE config ────────────────────────────────────────────────

# Store camera config overrides (persisted across restarts in-memory)
_camera_overrides: dict = {}


@router.put("/config")
async def update_camera_config(
    update: CameraConfigUpdate,
    user: dict = Depends(require_role("engineer")),
):
    """
    Update camera configuration and restart camera stream.
    Only engineer role can change camera settings.
    """
    cam = get_camera()

    # Track which fields changed
    changed = False

    if update.source is not None and update.source != cam.config.source:
        cam.config.source = update.source
        _camera_overrides["source"] = update.source
        changed = True

    if update.width is not None:
        cam.config.width = update.width
        _camera_overrides["width"] = update.width
        changed = True

    if update.height is not None:
        cam.config.height = update.height
        _camera_overrides["height"] = update.height
        changed = True

    if update.fps is not None:
        cam.config.fps = update.fps
        _camera_overrides["fps"] = update.fps
        changed = True

    if update.jpeg_quality is not None:
        cam.config.jpeg_quality = update.jpeg_quality
        _camera_overrides["jpeg_quality"] = update.jpeg_quality
        changed = True

    if changed:
        # Restart camera with new config
        cam.close()
        success = cam.open()
        new_info = cam.info

        return {
            "ok": True,
            "restarted": True,
            "connected": success,
            "info": {
                "source": cam.config.source,
                "width": cam.config.width,
                "height": cam.config.height,
                "fps": cam.config.fps,
                "jpeg_quality": cam.config.jpeg_quality,
                "source_type": new_info["type"],
                "actual": new_info["actual"],
            }
        }

    return {"ok": True, "restarted": False, "message": "No changes detected"}


# ── RESTART camera ───────────────────────────────────────────────

@router.post("/restart")
async def restart_camera(user: dict = Depends(require_role("engineer"))):
    """Force restart the camera capture (reconnect)."""
    cam = get_camera()
    cam.close()
    success = cam.open()

    return {
        "ok": True,
        "connected": success,
        "info": cam.info,
    }


# ── SNAPSHOT ─────────────────────────────────────────────────────

@router.get("/snapshot")
async def camera_snapshot(user: dict = Depends(get_current_user)):
    """Take a snapshot from the camera (base64 JPEG)."""
    cam = get_camera()

    if not cam.is_opened:
        ok = cam.open()
        if not ok:
            raise HTTPException(status_code=503, detail="Camera not available")

    success, b64 = cam.read_base64()
    if success and b64:
        return {"ok": True, "image": b64}

    # Try fallback
    return {"ok": False, "image": cam.get_fallback_base64(), "fallback": True}
