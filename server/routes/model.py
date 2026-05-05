"""Model management routes — list, config, reload."""

import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from server.auth import get_current_user, require_role

router = APIRouter(prefix="/api/model", tags=["model"])

# Edge service internal URL
EDGE_URL = os.environ.get("EDGE_URL", "http://inference-engine:8001")

class ModelItem(BaseModel):
    name: str
    input_shape: list
    num_classes: int
    class_names: list
    file_size_mb: float

class ModelListResponse(BaseModel):
    models: List[ModelItem]
    current: Optional[str] = None

class ModelConfig(BaseModel):
    model: str
    confidence: float = 0.5
    iou: float = 0.45

class ReloadRequest(BaseModel):
    model: str = ""

# ── In-memory config ────────────────────────────────────────────

_model_config = ModelConfig(model="yolov8n_defect")


@router.get("/list", response_model=ModelListResponse)
async def list_models(user: dict = Depends(get_current_user)):
    """Get available models from edge service."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{EDGE_URL}/models")
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return ModelListResponse(models=[], current=None)


@router.get("/config", response_model=ModelConfig)
async def get_model_config(user: dict = Depends(get_current_user)):
    """Get current model config."""
    return _model_config


@router.put("/config")
async def update_model_config(
    cfg: ModelConfig,
    user: dict = Depends(require_role("engineer")),
):
    """Update model, confidence, IOU threshold."""
    global _model_config
    old_model = _model_config.model
    _model_config = cfg

    # Trigger reload on edge if model changed
    reload_triggered = False
    reload_ok = False
    if cfg.model != old_model:
        reload_triggered = True
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(
                    f"{EDGE_URL}/reload",
                    json={"model": cfg.model},
                )
                reload_ok = r.json().get("ok", False)
        except Exception:
            pass

    return {
        "ok": True,
        "config": cfg.model_dump(),
        "reload_triggered": reload_triggered,
        "reload_ok": reload_ok,
    }


@router.post("/reload")
async def reload_model(
    req: ReloadRequest,
    user: dict = Depends(require_role("engineer")),
):
    """Force reload model on edge service."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"{EDGE_URL}/reload",
                json={"model": req.model},
            )
            return r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Edge service unreachable: {e}")
