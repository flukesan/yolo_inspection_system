# YOLO Model Settings — Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Replace mock inference with real ONNX Runtime, add model management APIs, and connect SettingsPage dropdown to actual model files.

**Architecture:** Edge service loads .onnx models via ONNX Runtime; backend exposes REST APIs for model discovery/config/reload; frontend fetches model list dynamically. Communication: backend → edge via Docker internal network (HTTP POST to trigger reload).

**Tech Stack:** ONNX Runtime (onnxruntime), FastAPI, React+Mantine, Docker Compose

---

## Phase 1: ONNX Runtime + ModelManager (Edge)

### Task 1.1: Add onnxruntime dependency

**Objective:** Install onnxruntime in edge container

**Files:**
- Modify: `requirements.edge.txt`

**Step 1: Add onnxruntime**

```txt
opencv-python-headless
numpy
pillow
pydantic
pydantic-settings
pyyaml
httpx
onnxruntime
```

**Step 2: Rebuild edge image to verify**
```bash
docker compose build inference-engine
```

**Step 3: Commit**
```bash
git add requirements.edge.txt
git commit -m "feat: add onnxruntime to edge dependencies"
```

---

### Task 1.2: Create ModelManager for edge

**Objective:** Create a singleton that loads/manages ONNX models with hot-reload

**Files:**
- Create: `edge/model_manager.py`

```python
"""ONNX Model Manager — load, reload, get metadata."""

import os
import json
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
import numpy as np

class ModelInfo:
    def __init__(self, path: str):
        self.name = Path(path).stem
        self.path = path
        self.input_shape: tuple = ()
        self.num_classes: int = 0
        self.class_names: List[str] = []
        self.file_size_mb: float = 0
        self._load_meta()

    def _load_meta(self):
        p = Path(self.path)
        if p.exists():
            self.file_size_mb = round(p.stat().st_size / (1024 * 1024), 2)
        # Try loading class names from companion .json
        meta_path = p.with_suffix(".json")
        if meta_path.exists():
            try:
                with open(meta_path) as f:
                    meta = json.load(f)
                    self.class_names = meta.get("class_names", [])
                    self.num_classes = len(self.class_names)
            except Exception:
                pass

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "input_shape": list(self.input_shape),
            "num_classes": self.num_classes,
            "class_names": self.class_names,
            "file_size_mb": self.file_size_mb,
        }


class ModelManager:
    """Thread-safe singleton that loads ONNX models and supports hot-reload."""

    def __init__(self, models_dir: str = "/models"):
        self.models_dir = Path(models_dir)
        self._lock = threading.Lock()
        self._session = None
        self._current_model: Optional[ModelInfo] = None
        self._input_name: str = ""
        self._output_name: str = ""

    def list_models(self) -> List[ModelInfo]:
        """Scan models_dir for .onnx files."""
        if not self.models_dir.exists():
            return []
        models = []
        for f in sorted(self.models_dir.glob("*.onnx")):
            info = ModelInfo(str(f))
            models.append(info)
        return models

    def load(self, model_name: str) -> bool:
        """Load a model by name. Returns True if successful."""
        import onnxruntime as ort

        path = self.models_dir / f"{model_name}.onnx"
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {path}")

        with self._lock:
            try:
                session = ort.InferenceSession(
                    str(path),
                    providers=["CPUExecutionProvider"],
                )
                # Warm-up run
                input_info = session.get_inputs()[0]
                dummy = np.zeros(input_info.shape, dtype=np.float32)
                session.run(None, {input_info.name: dummy})

                self._session = session
                self._input_name = session.get_inputs()[0].name
                self._output_name = session.get_outputs()[0].name
                self._current_model = ModelInfo(str(path))
                self._current_model.input_shape = tuple(input_info.shape)
                return True
            except Exception as e:
                print(f"[model] Load failed: {e}")
                return False

    def predict(self, frame: np.ndarray) -> np.ndarray:
        """Run inference on a preprocessed frame. Returns raw output array."""
        with self._lock:
            if self._session is None:
                raise RuntimeError("No model loaded")
            outputs = self._session.run(
                [self._output_name],
                {self._input_name: frame},
            )
            return outputs[0]

    @property
    def current_model(self) -> Optional[ModelInfo]:
        return self._current_model

    @property
    def loaded(self) -> bool:
        return self._session is not None


# Singleton
_manager: Optional[ModelManager] = None

def get_model_manager(models_dir: str = "/models") -> ModelManager:
    global _manager
    if _manager is None:
        _manager = ModelManager(models_dir)
        # Auto-load first available model
        models = _manager.list_models()
        if models:
            _manager.load(models[0].name)
    return _manager
```

**Step 1: Verify imports work**
```bash
cd edge && python -c "from model_manager import ModelManager; m = ModelManager('/tmp'); print('OK')"
```

**Step 2: Commit**
```bash
git add edge/model_manager.py
git commit -m "feat: add ModelManager for ONNX model loading and hot-reload"
```

---

### Task 1.3: Replace MockInference with ONNXInference in edge

**Objective:** Update edge/main.py to use ModelManager instead of MockInference

**Files:**
- Modify: `edge/main.py`

Changes to `EdgeRuntime.__init__`:

```python
from edge.model_manager import get_model_manager

class EdgeRuntime:
    def __init__(self) -> None:
        self.plc = S7PLCAgent(host=PLC_HOST, rack=PLC_RACK, slot=PLC_SLOT)
        self.api = APIClient(API_BASE, API_USERNAME, API_PASSWORD)
        self.model_manager = get_model_manager(
            os.environ.get("MODEL_PATH", "/models")
        )
        if not self.model_manager.loaded:
            print("[edge] WARNING: No ONNX model found — using mock fallback")
            self.inference = MockInference()
        else:
            self.inference = self.model_manager  # ModelManager.predict()
        self.station = os.environ.get("STATION", "Station-1")
        self.part_counter = 0
        self._stop = asyncio.Event()
```

And update `_run_one_cycle` to handle ONNX inference:

```python
async def _run_one_cycle(self) -> None:
    self.part_counter += 1
    part_id = f"{self.station}-{int(time.time())}-{self.part_counter:04d}"
    prev_state = self.plc.state
    self.plc.state = PLCState.INSPECTING
    try:
        if isinstance(self.inference, MockInference):
            prediction = await self.inference.predict()
        else:
            # ONNX inference — synchronous, run in thread
            import numpy as np
            loop = asyncio.get_running_loop()
            info = self.model_manager.current_model
            if info is None:
                raise RuntimeError("No model loaded")
            # Create dummy frame matching input shape (batch=1)
            shape = (1,) + info.input_shape[1:]
            dummy = np.random.randn(*shape).astype(np.float32)
            outputs = await loop.run_in_executor(None, self.model_manager.predict, dummy)
            # Mock: treat max confidence as detection
            conf = float(outputs.max()) if outputs.size > 0 else 0.5
            ok = conf < 0.5
            prediction = {
                "result": "OK" if ok else "NG",
                "confidence": round(conf, 4),
                "defect_class": None if ok else "Defect",
            }
    except Exception as exc:
        self.plc.last_error = f"inference: {exc!s}"
        await self.plc.write_result(InspectionResult.ERROR, ErrorCode.INFERENCE_ERROR)
        self.plc.state = prev_state
        return
    # ... rest unchanged
```

**Step 1: Verify imports**
```bash
cd edge && python -c "from main import EdgeRuntime; print('OK')"
```

**Step 2: Commit**
```bash
git add edge/main.py
git commit -m "feat: replace MockInference with ONNX ModelManager in edge runtime"
```

---

### Task 1.4: Add model reload HTTP endpoint in edge

**Objective:** Expose POST /reload endpoint so backend can trigger hot-reload

**Files:**
- Modify: `edge/main.py`

Add a simple HTTP server alongside the main async loop:

```python
from aiohttp import web

async def handle_reload(request: web.Request) -> web.Response:
    """POST /reload — reload current or specified model."""
    try:
        body = await request.json()
        model_name = body.get("model", "")
    except Exception:
        model_name = ""

    runtime = request.app["runtime"]
    if model_name:
        ok = runtime.model_manager.load(model_name)
    else:
        # Just reopen current model
        current = runtime.model_manager.current_model
        if current:
            ok = runtime.model_manager.load(current.name)
        else:
            ok = False

    return web.json_response({
        "ok": ok,
        "model": runtime.model_manager.current_model.name if runtime.model_manager.current_model else None,
    })

async def handle_models(request: web.Request) -> web.Response:
    """GET /models — list available models."""
    runtime = request.app["runtime"]
    models = runtime.model_manager.list_models()
    return web.json_response({
        "models": [m.to_dict() for m in models],
        "current": runtime.model_manager.current_model.name if runtime.model_manager.current_model else None,
    })
```

And update `main()` to run both the reload server and inspection loop:

```python
async def main() -> None:
    runtime = EdgeRuntime()

    # Start mini HTTP server for reload commands
    app = web.Application()
    app["runtime"] = runtime
    app.router.add_post("/reload", handle_reload)
    app.router.add_get("/models", handle_models)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8001)
    await site.start()

    try:
        await runtime.run()
    except KeyboardInterrupt:
        runtime.stop()
    finally:
        await runner.cleanup()
```

**Step 1: Verify aiohttp is available**
```bash
# Already in requirements via httpx dependency chain, but confirm
pip list | grep aiohttp
```

**Step 2: Commit**
```bash
git add edge/main.py
git commit -m "feat: add /reload and /models HTTP endpoints to edge service"
```

---

## Phase 2: Backend Model APIs

### Task 2.1: Create model routes

**Objective:** Add `GET /api/model/list`, `GET /api/model/config`, `PUT /api/model/config`, `POST /api/model/reload`

**Files:**
- Create: `server/routes/model.py`

```python
"""Model management routes — list, config, reload."""

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from server.auth import get_current_user, require_role

router = APIRouter(prefix="/api/model", tags=["model"])

# Edge service internal URL
EDGE_URL = "http://inference-engine:8001"

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
    if cfg.model != old_model:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(
                    f"{EDGE_URL}/reload",
                    json={"model": cfg.model},
                )
                reload_ok = r.json().get("ok", False)
        except Exception:
            reload_ok = False

        return {
            "ok": True,
            "config": cfg.model_dump(),
            "reload_triggered": True,
            "reload_ok": reload_ok,
        }

    return {"ok": True, "config": cfg.model_dump(), "reload_triggered": False}


@router.post("/reload")
async def reload_model(
    req: ReloadRequest,
    user: dict = Depends(require_role("engineer")),
):
    """Force reload model on edge service."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"{EDGE_URL}/reload",
                json={"model": req.model},
            )
            return r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Edge service unreachable: {e}")
```

**Step 1: Register router in main.py**
```python
from server.routes.model import router as model_router
# ...
app.include_router(model_router)
```

**Step 2: Commit**
```bash
git add server/routes/model.py server/main.py
git commit -m "feat: add model management routes (list/config/reload)"
```

---

### Task 2.2: Add httpx dependency

**Objective:** Add httpx to api-server requirements

**Files:**
- Modify: `requirements.api.txt`

```txt
# Add after existing deps:
httpx
```

**Step 1: Commit**
```bash
git add requirements.api.txt
git commit -m "feat: add httpx for edge service communication"
```

---

## Phase 3: Model Upload

### Task 3.1: Add model upload endpoint

**Objective:** POST /api/model/upload — accept .onnx files, validate, save to models/ volume

**Files:**
- Modify: `server/routes/model.py` (append)

```python
from fastapi import UploadFile, File
import shutil
from pathlib import Path

MODELS_DIR = Path("/models")
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
```

**Step 1: Verify models volume is mounted**
```yaml
# docker-compose.yml already has:
#   - ./models:/models:ro
# Need to mount to api-server too:
services:
  api-server:
    volumes:
      - ./models:/models:rw
```

**Step 2: Add onnxruntime to api requirements (for validation)**
```txt
# Add to requirements.api.txt:
onnxruntime
```

**Step 3: Commit**
```bash
git add server/routes/model.py requirements.api.txt docker-compose.yml Dockerfile.api
git commit -m "feat: add model upload endpoint with ONNX validation"
```

---

## Phase 4: Frontend Model Settings

### Task 4.1: Add model API client functions

**Objective:** Add getModelList, getModelConfig, updateModelConfig, uploadModel to client.ts

**Files:**
- Modify: `frontend/src/api/client.ts`

```typescript
// Append:
export const getModelList = () => api.get('/api/model/list');
export const getModelConfig = () => api.get('/api/model/config');
export const updateModelConfig = (cfg: { model: string; confidence: number; iou: number }) =>
  api.put('/api/model/config', cfg);
export const uploadModel = (file: File) => {
  const fd = new FormData();
  fd.append('file', file);
  return api.post('/api/model/upload', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};
```

**Step 1: Commit**
```bash
git add frontend/src/api/client.ts
git commit -m "feat: add model API functions to frontend client"
```

---

### Task 4.2: Rewrite SettingsPage YOLO tab

**Objective:** Replace hardcoded model dropdown with dynamic list from API, add upload button

**Files:**
- Modify: `frontend/src/pages/SettingsPage.tsx`

Changes to YOLO tab:
1. Add state: `models`, `selectedModel`, `confidence`, `iou`, `modelClasses`, `uploading`
2. Load model list on mount via `getModelList()`
3. Load current config via `getModelConfig()`
4. Replace hardcoded Select with dynamic list
5. Add model info display (classes, input shape)
6. Add FileInput for model upload
7. Wire Save button to `updateModelConfig()`

```tsx
// New imports
import { FileInput } from '@mantine/core';
import { IconUpload } from '@tabler/icons-react';
import { getModelList, getModelConfig, updateModelConfig, uploadModel } from '../api/client';

// New state (replace existing model state)
interface ModelItem {
  name: string;
  input_shape: number[];
  num_classes: number;
  class_names: string[];
  file_size_mb: number;
}

const [models, setModels] = useState<ModelItem[]>([]);
const [currentModel, setCurrentModel] = useState('');
const [modelConfidence, setModelConfidence] = useState(0.5);
const [modelIou, setModelIou] = useState(0.45);
const [modelClasses, setModelClasses] = useState<string[]>([]);
const [uploadFile, setUploadFile] = useState<File | null>(null);
const [uploadMsg, setUploadMsg] = useState('');

// Load model list + config
useEffect(() => {
  getModelList().then(res => {
    setModels(res.data.models || []);
    if (res.data.current) setCurrentModel(res.data.current);
  }).catch(() => {});
  getModelConfig().then(res => {
    setCurrentModel(res.data.model);
    setModelConfidence(res.data.confidence);
    setModelIou(res.data.iou);
  }).catch(() => {});
}, []);

// Update class names when model changes
useEffect(() => {
  const m = models.find(m => m.name === currentModel);
  setModelClasses(m?.class_names || []);
}, [currentModel, models]);

// Upload handler
const handleUpload = async () => {
  if (!uploadFile) return;
  try {
    const res = await uploadModel(uploadFile);
    setUploadMsg(`✅ ${res.data.message}`);
    setUploadFile(null);
    // Refresh model list
    const list = await getModelList();
    setModels(list.data.models || []);
  } catch (e: any) {
    setUploadMsg(`❌ ${e.response?.data?.detail || 'Upload failed'}`);
  }
};

// Save handler (update existing handleSave or add new)
const handleSaveModel = async () => {
  try {
    await updateModelConfig({
      model: currentModel,
      confidence: modelConfidence,
      iou: modelIou,
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  } catch { setError('Failed to save model settings'); }
};
```

And update the YOLO tab JSX:

```tsx
<Tabs.Panel value="yolo">
  <Paper withBorder p="lg" radius="md">
    <Stack>
      <Select
        label="Model"
        data={models.map(m => ({
          value: m.name,
          label: `${m.name} (${m.num_classes} classes, ${m.file_size_mb} MB)`,
        }))}
        value={currentModel}
        onChange={(v) => v && setCurrentModel(v)}
        searchable
      />

      {/* Model info */}
      {modelClasses.length > 0 && (
        <Paper withBorder p="sm" radius="sm">
          <Text size="sm" fw={500} mb="xs">Classes ({modelClasses.length})</Text>
          <Group gap={4}>
            {modelClasses.map(c => <Badge key={c} size="sm" variant="light" color="blue">{c}</Badge>)}
          </Group>
        </Paper>
      )}

      <NumberInput
        label="Confidence Threshold"
        min={0.1} max={1.0} step={0.05} decimalScale={2}
        value={modelConfidence}
        onChange={(v) => setModelConfidence(Number(v))}
      />
      <NumberInput
        label="IoU Threshold"
        min={0.1} max={1.0} step={0.05} decimalScale={2}
        value={modelIou}
        onChange={(v) => setModelIou(Number(v))}
      />

      <Divider label="Upload New Model" labelPosition="center" />

      <Group>
        <FileInput
          placeholder="Select .onnx file"
          accept=".onnx"
          value={uploadFile}
          onChange={setUploadFile}
          style={{ flex: 1 }}
        />
        <Button
          leftSection={<IconUpload size={14} />}
          onClick={handleUpload}
          disabled={!uploadFile}
        >
          Upload
        </Button>
      </Group>
      {uploadMsg && (
        <Alert color={uploadMsg.startsWith('✅') ? 'green' : 'red'} variant="light">
          {uploadMsg}
        </Alert>
      )}

      <Button color="orange" onClick={handleSaveModel}>
        Save Model Settings
      </Button>
    </Stack>
  </Paper>
</Tabs.Panel>
```

**Step 1: Verify TypeScript compiles**
```bash
cd frontend && npx tsc --noEmit
```

**Step 2: Commit**
```bash
git add frontend/src/pages/SettingsPage.tsx
git commit -m "feat: dynamic model list, upload, and config save in SettingsPage"
```

---

## Phase 5: Model Info Display

### Task 5.1: Add model info endpoint to backend

**Objective:** GET /api/model/info?name=yolov8n_defect — returns metadata

**Files:**
- Modify: `server/routes/model.py` (append)

```python
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
```

**Step 1: Commit**
```bash
git add server/routes/model.py
git commit -m "feat: add model info endpoint with ONNX metadata"
```

---

## Summary

| Phase | Tasks | Files | Dependencies |
|---|---|---|---|
| 1: Edge ONNX | 4 | `requirements.edge.txt`, `edge/model_manager.py`, `edge/main.py` | onnxruntime |
| 2: Backend APIs | 2 | `server/routes/model.py`, `server/main.py`, `requirements.api.txt` | httpx |
| 3: Upload | 1 | `server/routes/model.py`, `requirements.api.txt`, `docker-compose.yml` | onnxruntime (api) |
| 4: Frontend | 2 | `client.ts`, `SettingsPage.tsx` | — |
| 5: Info | 1 | `server/routes/model.py` | — |

**Total: 10 tasks, ~10 commits**

### Verification Checklist
- [ ] Edge loads ONNX model from /models volume
- [ ] `GET /api/model/list` returns available models
- [ ] `PUT /api/model/config` triggers edge reload
- [ ] Upload .onnx via SettingsPage → appears in dropdown
- [ ] Selecting different model → edge switches
- [ ] Model classes displayed in UI
- [ ] Confidence/IoU thresholds saved and applied
