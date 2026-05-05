"""Model management routes — list, config, reload."""

import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import shutil
from pathlib import Path
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


MODELS_DIR = Path(os.environ.get("MODELS_DIR", "/models"))
MODELS_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_model(
    file: UploadFile = File(...),
    user: dict = Depends(require_role("engineer")),
):
    """Upload a new .onnx model file."""
    if not file.filename or not file.filename.endswith(".onnx"):
        raise HTTPException(status_code=400, detail="Only .onnx files accepted")

    path = MODELS_DIR / file.filename
    try:
        with path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save: {e}")

    # Validate: try loading with onnxruntime
    try:
        import onnxruntime as ort
        ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    except Exception as e:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Invalid ONNX model: {e}")

    file_size_mb = round(path.stat().st_size / (1024 * 1024), 2)
    return {
        "ok": True,
        "name": file.filename,
        "size_mb": file_size_mb,
        "message": f"Model {file.filename} uploaded and validated",
    }


@router.get("/info")
async def get_model_info(
    name: str,
    user: dict = Depends(get_current_user),
):
    """Get detailed info for a specific model."""
    try:
        import onnxruntime as ort
        path = MODELS_DIR / f"{name}.onnx"
        if not path.exists():
            raise HTTPException(status_code=404, detail="Model not found")

        session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
        inputs = session.get_inputs()
        outputs = session.get_outputs()

        # Try loading class names from companion .json
        class_names = []
        meta_path = path.with_suffix(".json")
        if meta_path.exists():
            import json
            with open(meta_path) as f:
                meta = json.load(f)
                class_names = meta.get("class_names", [])

        return {
            "name": name,
            "input_shape": list(inputs[0].shape) if inputs else [],
            "output_shape": list(outputs[0].shape) if outputs else [],
            "num_classes": len(class_names),
            "class_names": class_names,
            "file_size_mb": round(path.stat().st_size / (1024 * 1024), 2),
            "providers": ort.get_available_providers(),
        }
    except ImportError:
        raise HTTPException(status_code=500, detail="onnxruntime not installed on server")
