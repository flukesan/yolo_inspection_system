"""ONNX Model Manager — load, reload, get metadata."""

import json
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional
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

    def _load_meta(self) -> None:
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

    def to_dict(self) -> Dict[str, Any]:
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
        with self._lock:
            return self._current_model

    @property
    def loaded(self) -> bool:
        with self._lock:
            return self._session is not None


# Singleton
_manager: Optional[ModelManager] = None
_manager_lock = threading.Lock()

def get_model_manager(models_dir: str = "/models") -> ModelManager:
    global _manager
    if _manager is None:
        with _manager_lock:
            if _manager is None:  # double-check
                _manager = ModelManager(models_dir)
                models = _manager.list_models()
                if models:
                    _manager.load(models[0].name)
    return _manager
