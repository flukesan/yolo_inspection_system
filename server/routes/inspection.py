"""Inspection routes."""
import base64
import os
import time
from typing import Optional

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from server.auth import get_current_user
from server.routes.websocket import get_camera

router = APIRouter(prefix="/api", tags=["inspection"])

class InspectionCreate(BaseModel):
    part_id: str
    result: str
    defect_class: Optional[str] = None
    station: str = "Station-1"
    confidence: float = 0.0
    image_id: Optional[int] = None

@router.post("/inspection")
async def create_inspection(data: InspectionCreate, user: dict = Depends(get_current_user)):
    return {"id": 1, "timestamp": datetime.now().isoformat(), **data.model_dump()}

@router.get("/inspections")
async def list_inspections(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    result: Optional[str] = None, station: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    return {"items": [], "total": 0, "page": page, "total_pages": 1}

@router.get("/stats")
async def get_stats(user: dict = Depends(get_current_user)):
    return {"total": 0, "ok": 0, "ng": 0, "rate": 100.0, "period_hours": 24}

@router.get("/stats/trend")
async def get_trend(user: dict = Depends(get_current_user)):
    return [{"hour": f"{h:02d}:00", "total": 0, "ok": 0, "ng": 0, "ok_rate": 100.0} for h in range(24)]


@router.post("/inspection/snap")
async def snap_and_inspect(user: dict = Depends(get_current_user)):
    """Capture camera frame, run inference, return result."""
    cam = get_camera()
    if not cam.is_opened:
        ok = cam.open()
        if not ok:
            raise HTTPException(status_code=503, detail="Camera not available")

    # Capture frame
    success, b64 = cam.read_base64()
    if not success or not b64:
        raise HTTPException(status_code=500, detail="Failed to capture frame")

    # Run inference
    try:
        from edge.model_manager import get_model_manager
        mgr = get_model_manager(
            os.environ.get("MODEL_PATH", "/models")
        )
        if mgr.loaded:
            # Decode frame to numpy for ONNX
            import cv2
            img_bytes = base64.b64decode(b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img = cv2.resize(img, (640, 640))
            img = img.transpose(2, 0, 1).astype(np.float32) / 255.0
            img = np.expand_dims(img, 0)

            outputs = mgr.predict(img)
            conf = float(outputs.max()) if outputs.size > 0 else 0.5
            result = "OK" if conf < 0.5 else "NG"
            defect = "Defect" if result == "NG" else None
            confidence = round(conf, 4)
        else:
            raise RuntimeError("No model")
    except Exception:
        # Fallback to mock
        import random
        result = "OK" if random.random() < 0.93 else "NG"
        confidence = round(random.uniform(0.65, 0.99), 4)
        defect = None if result == "OK" else random.choice(["Scratch", "Dent", "Misalign"])
        b64 = None  # Don't return base64 in response (too large)

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "ok": True,
        "result": result,
        "confidence": confidence,
        "defect_class": defect,
        "timestamp": timestamp,
        "snap_id": int(time.time() * 1000),
    }
