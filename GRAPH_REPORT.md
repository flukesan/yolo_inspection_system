# Codebase Knowledge Graph: YOLO Inspection System
Generated: 2026-05-04 | Language: Python 3.10+ | Framework: PyQt6 + YOLOv8 | Files: ~47 source files

> ระบบตรวจสอบคุณภาพชิ้นงานแบบเรียลไทม์บนไลน์ผลิต ใช้ YOLOv8 ตรวจจับ defect + PyQt6 GUI เชื่อมต่อ PLC ผ่าน Modbus TCP และ MQTT ไปยัง DeviceWise

---

## Entry Points

| File | Trigger | Role |
|------|---------|------|
| `main.py:296` | `if __name__ == "__main__"` | 🚀 Primary — สร้าง QApplication + AppController + MainWindow |
| `debug_qt.py:108` | `if __name__ == "__main__"` | 🔧 Qt diagnostic tool — ตรวจสอบ PyQt6/Qt platform |
| `test_gige_camera.py` | standalone script | 📷 Test GigE Vision camera via harvesters |
| `core/multishot_validator.py:202` | `if __name__ == '__main__'` | 🧪 Standalone validator test mode |

**Primary flow:** `main.py::main()` → `AppController()` → `MainWindow()` → Event loop

---

## Dependency Hierarchy

```
Layer 1: Orchestrator
  └── main.py::AppController (connect/disconnect camera, load model, start/stop inspection)

Layer 2: Settings & Business Logic
  ├── config/settings.py::Settings (JSON-based config loader)
  ├── core/camera_manager.py::CameraManager (USB/RTSP/GigE)
  │   └── core/camera_backends/ (GigE Vision drivers)
  ├── core/yolo_detector.py::YOLODetector (ultralytics YOLOv8)
  ├── core/inspection_engine.py::InspectionEngine (main loop)
  │   ├── core/multishot_inspector.py::MultiShotInspector (multi-shot capture)
  │   └── core/multishot_validator.py::MultiShotValidator (count rules)
  ├── core/mqtt_client.py::MQTTClient (DeviceWise MQTT)
  └── core/data_logger.py::DataLogger (SQLite logging)

Layer 3: UI (PyQt6)
  ├── ui/main_window.py::MainWindow (46 KB — หน้าต่างหลัก)
  │   ├── ui/widgets/camera_view.py::CameraView
  │   ├── ui/widgets/control_panel.py::ControlPanel
  │   ├── ui/widgets/statistics_panel.py::StatisticsPanel
  │   ├── ui/widgets/alert_panel.py::AlertPanel
  │   └── ui/widgets/validation_result_panel.py::ValidationResultPanel
  └── ui/dialogs/ (12 dialogs)
      ├── camera_settings.py, camera_profiles_dialog.py
      ├── model_settings.py, model_profiles_dialog.py
      ├── multishot_*.py (5 dialogs for multi-shot workflow)
      ├── mqtt_settings_dialog.py
      ├── validation_rules_dialog.py
      ├── report_dialog.py
      └── snapshot_training_settings_dialog.py

Layer 4: Utilities
  ├── utils/database.py::Database (SQLite)
  ├── utils/image_processor.py::ImageProcessor (OpenCV)
  ├── utils/plc_communication.py::PLCCommunication (Modbus TCP)
  ├── utils/report_generator.py::ReportGenerator (Excel/openpyxl)
  └── utils/multishot_capture.py (multi-shot capture helper)
```

---

## Core Concepts & Where They Live

- **Camera Management**: `core/camera_manager.py` — รองรับ USB (cv2.VideoCapture), RTSP, GigE Vision (harvesters)
- **YOLO Detection**: `core/yolo_detector.py` — ultralytics YOLOv8, CPU/GPU auto-detect, confidence/IoU thresholds
- **Inspection Engine**: `core/inspection_engine.py` — main loop: จับภาพ → ตรวจจับ → บันทึก → แจ้งเตือน → PLC
- **Multi-Shot Inspection**: `core/multishot_inspector.py` + `multishot_validator.py` — ถ่ายหลายจุดต่อชิ้น ตรวจจำนวนน็อต/bolt
- **MQTT (DeviceWise)**: `core/mqtt_client.py` — paho-mqtt, connect/publish/subscribe ไปยัง DeviceWise IoT Gateway
- **PLC Communication**: `utils/plc_communication.py` — pymodbus, Modbus TCP, อ่าน/เขียน coils/registers
- **Data Logging**: `core/data_logger.py` → `utils/database.py` — SQLite (inspection_results, defect_images)
- **Reports**: `utils/report_generator.py` — pandas + openpyxl → Excel reports
- **Image Processing**: `utils/image_processor.py` — OpenCV: resize, normalize, draw bounding boxes
- **Settings**: `config/settings.py` — JSON-based, camera/YOLO/inspection/PLC/MQTT/validation sections
- **UI (PyQt6)**: `ui/main_window.py` (46KB) — Dark Theme, Signal/Slot architecture (~50 signals)

---

## Data Flow (Inspection Cycle)

```
[Camera Capture]
    │  camera_manager.connect() → cv2.VideoCapture / RTSP / GigE
    ▼
[YOLO Detection]
    │  yolo_detector.load_model() → YOLOv8 inference
    │  outputs: bounding boxes, class names, confidence scores
    ▼
[Inspection Engine]
    │  inspection_engine.inspect_once()
    │  ├── Single-shot: 1 image → 1 detection → OK/NG
    │  └── Multi-shot: N images → aggregator → validation rules
    ▼
[Actions Pipeline]
    ├── data_logger.log_inspection() → SQLite
    ├── mqtt_client.publish() → DeviceWise
    ├── plc_communication.write_coil() → PLC signal
    ├── report_generator.generate_excel_report() → Excel
    └── UI update: statistics_panel, alert_panel, camera_view
```

---

## File Responsibility Map

| Category | Files | Size |
|----------|-------|------|
| **Orchestration** | `main.py` | 11.5 KB |
| **Camera** | `core/camera_manager.py`, `core/camera_backends/` | 5.6 KB |
| **Detection** | `core/yolo_detector.py` | 16.1 KB |
| **Inspection Logic** | `core/inspection_engine.py` | 18.9 KB |
| **Multi-Shot** | `core/multishot_inspector.py`, `multishot_validator.py` | 24.8 KB |
| **Communication** | `core/mqtt_client.py`, `utils/plc_communication.py` | 13.9 KB |
| **Data** | `core/data_logger.py`, `utils/database.py` | 9.1 KB |
| **Reports** | `utils/report_generator.py` | ~5 KB |
| **Image Processing** | `utils/image_processor.py` | ~3 KB |
| **UI Main** | `ui/main_window.py` | 46.2 KB |
| **UI Widgets** | `ui/widgets/` (6 files) | ~15 KB |
| **UI Dialogs** | `ui/dialogs/` (12 files) | ~30 KB |
| **Config** | `config/settings.py`, `*.json` | 10.4 KB |
| **Tests** | `test_gige_camera.py` | 5.8 KB |
| **Docs** | `docs/` (2 markdown files) | ~8 KB |
| **Scripts** | `scripts/`, `*.bat` | Docker + Windows automation |

---

## Critical Paths (High-Risk Change Areas)

1. **`inspection_engine.py` ↔ `yolo_detector.py`** — Tight coupling: engine calls detector every frame. Changing detection output format breaks engine.
2. **`main_window.py` (46KB)** — Monolithic UI: 50+ signal/slot connections. Changing one widget may break another via shared signals.
3. **`settings.py` ↔ `app_config.json`** — Config schema shared across ALL modules. Adding a new config key requires updating every reader.
4. **`mqtt_client.py` ↔ DeviceWise** — Network-dependent. Async MQTT callbacks may race with PyQt6 event loop.
5. **Multi-Shot Pipeline**: `multishot_inspector` → `multishot_validator` → `multishot_capture` — 3-file chain, breaking one breaks the workflow.

---

## Verified ✅ vs Inferred ⚠️ Relationships

### Verified ✅ (direct import/grep match):
- `main.py` imports `Settings`, `CameraManager`, `YOLODetector`, `InspectionEngine`, `DataLogger`, `MQTTClient`, `Database`, `ImageProcessor`, `PLCCommunication`, `ReportGenerator`, `MainWindow`
- `core/__init__.py` exports: CameraManager, YOLODetector, InspectionEngine, DataLogger, MQTTClient
- `utils/__init__.py` exports: Database, ImageProcessor, PLCCommunication, ReportGenerator
- `config/__init__.py` exports: Settings
- `ui/__init__.py` exports: MainWindow
- `multishot_validator.py` imports `MultiShotInspector` from `core.multishot_inspector`
- `test_gige_camera.py` imports `harvesters.core.Harvester`
- `settings.py` reads `app_config.json` (JSON-based config)
- 50+ PyQt6 signal/slot connections in `main_window.py` and widgets
- **InspectionEngine** (verified methods): `__init__(camera_manager, yolo_detector, data_logger)`, `start()`, `stop()`, `pause()`, `resume()`, `inspect_once()` — calls `camera_manager.get_frame()` + `yolo_detector.detect()` in the inspection loop
- **MQTTClient** (verified methods): `connect()`, `disconnect()`, `publish_inspection_result()`, `_prepare_defects_data()`
- **Database** (verified methods): `connect()`, `create_tables()`, `insert_inspection()`, `get_inspections()`
- **PLCCommunication** (verified methods): `connect()`, `disconnect()`, `read_trigger()`, `write_result()`, `read_register()`, `write_register()`, `get_status()`
- **MainWindow** imports all 5 widgets + 6 dialog classes directly
- InspectionEngine stores `self.camera_manager`, `self.yolo_detector`, `self.data_logger`, `self.mqtt_client` — dependency injection confirmed

### Inferred ⚠️ (convention/logic, NOT confirmed by source):
- Multi-shot dialogs likely depend on `MultiShotInspector` for capture workflow
- Model profiles in `model_profiles_dialog.py` inferred to work with `yolo_detector.py` model loading
- `plc_communication.py` likely called from `inspection_engine.py` on defect detection

---

## Integration Points

| System | Protocol | Library | Config Location |
|--------|----------|---------|-----------------|
| **PLC** | Modbus TCP | `pymodbus` | `settings.py` → PLC section |
| **DeviceWise IoT** | MQTT | `paho-mqtt` | `settings.py` → MQTT section |
| **GigE Camera** | GenICam | `harvesters` + `genicam` | `camera_profiles.json` |
| **SQLite DB** | Local file | `sqlite3` (built-in) | `data/` directory |
| **Excel Reports** | Local file | `openpyxl` | `reports/` directory |
| **YOLOv8 Model** | Local file | `ultralytics` | `models/yolov8_defect.pt` |

---

## Notes for AI Coding Agents

### 🔴 Before Adding Features:
- **Check `settings.py` FIRST** — almost every module reads config from it. New features likely need config keys.
- **`main_window.py` is monolithic (46KB)** — prefer adding new widgets in `ui/widgets/` and connecting via signals rather than extending the main window.
- **The inspection pipeline is linear** (`camera → yolo → engine → actions`) — adding a stage means threading it into this chain correctly.

### 🟡 When Modifying:
- **YOLO output format changes** affect `inspection_engine.py`, `multishot_inspector.py`, `multishot_validator.py`, and `statistics_panel.py` — test all 4.
- **MQTT topic changes** must match DeviceWise gateway config.
- **PyQt6 signal connections (~50)** — use `debug_qt.py` to verify GUI stability after changes.

### 🟢 Low-Risk Areas:
- `utils/image_processor.py` — isolated, only depends on OpenCV
- `utils/report_generator.py` — isolated, only depends on pandas/openpyxl
- `docs/` — documentation, no code impact
- `scripts/` — Docker/Windows automation, no code dependency

### ⚠️ Known Pitfalls:
1. **No unit tests** — only `test_gige_camera.py` exists as a test. All other modules are untested.
2. **No type hints** in most files — behavior inferred from variable names, not annotations.
3. **Hardcoded paths** — `data/`, `reports/`, `models/` assumed relative to CWD. Changing working directory may break.
4. **GigE camera requires native drivers** — `harvesters` + `genicam` have complex native dependencies, not included in Docker variants.
5. **MQTT is fire-and-forget** — no retry/reconnection logic confirmed in `mqtt_client.py` (only `_generate_client_id` method confirmed).
6. **SQLite is local-only** — no support for remote DB or cloud sync (by design for factory floor).

### 📋 Suggested Improvements:
- [ ] **Split `main_window.py`** — 46KB monolith → smaller widgets with clear signal contracts
- [ ] **Add unit tests** — at minimum for `yolo_detector.py`, `inspection_engine.py`, `database.py`
- [ ] **Add type hints** — `inspection_engine.py` (19KB) and `multishot_inspector.py` (15KB) are the largest untapped files
- [ ] **Config validation** — `settings.py` loads JSON but doesn't validate schema/sanity check values
- [ ] **MQTT reconnect** — add retry with exponential backoff for factory floor resilience
- [ ] **Multi-model support** — `yolo_detector.py` currently loads 1 model; could support model-per-class
- [ ] **Logging framework** — replace `print()` statements with structured logging