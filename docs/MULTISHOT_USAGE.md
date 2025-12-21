# Multi-Shot Aggregation - คู่มือการใช้งาน

## 📋 สารบัญ

1. [การเปิดใช้งาน Multi-Shot](#การเปิดใช้งาน-multi-shot)
2. [Training Mode - การเก็บข้อมูล](#training-mode)
3. [Inspection Mode - การตรวจสอบ](#inspection-mode)
4. [Aggregation Strategies](#aggregation-strategies)
5. [Multi-Shot Validation - การตรวจสอบแบบมีเงื่อนไข](#multi-shot-validation)
6. [ตัวอย่างการใช้งาน Code](#ตัวอย่างการใช้งาน-code)

---

## การเปิดใช้งาน Multi-Shot

### Training Mode

```python
# ใน main application
from ui.dialogs.multishot_capture_dialog import MultiShotCaptureDialog
from utils.multishot_capture import MultiShotCapture

# เปิด Multi-Shot Capture Dialog
dialog = MultiShotCaptureDialog(camera_manager, settings, parent=self)

# Connect signal สำหรับรับผลลัพธ์
dialog.capture_completed.connect(self.on_multishot_captured)

# แสดง dialog
dialog.exec()

# Handle ผลลัพธ์
def on_multishot_captured(self, shots, class_name, workpiece_id):
    """
    Callback เมื่อถ่ายภาพเสร็จ

    Args:
        shots: List of captured frames
        class_name: 'OK' or 'NG'
        workpiece_id: Workpiece ID number
    """
    # บันทึกภาพ
    capture = MultiShotCapture(self.camera, num_shots=len(shots))

    metadata = capture.save_training_shots(
        shots=shots,
        workpiece_id=workpiece_id,
        class_name=class_name,
        output_dir=self.settings.get('snapshot_training.output_dir'),
        width=self.settings.get('snapshot_training.width', 640),
        height=self.settings.get('snapshot_training.height', 640),
        resize_mode=self.settings.get('snapshot_training.resize_mode', 'crop')
    )

    print(f"Saved {len(shots)} shots for wp{workpiece_id:03d}")
```

---

### Inspection Mode

```python
from core.multishot_inspector import MultiShotInspector
from utils.multishot_capture import MultiShotCapture
from ui.dialogs.multishot_result_dialog import MultiShotResultDialog

# 1. สร้าง inspector
inspector = MultiShotInspector(
    model=yolo_model,
    strategy='majority_vote',  # หรือ 'unanimous', 'any', 'confidence_weighted'
    conf_threshold=0.5
)

# 2. สร้าง capture helper
capture = MultiShotCapture(
    camera_manager=camera,
    num_shots=4,
    interval=2.0
)

# 3. Capture shots
shots = capture.capture_sequence(
    auto_advance=True,
    progress_callback=lambda current, total: print(f"Shot {current}/{total}"),
    countdown_callback=lambda seconds: print(f"Next shot in {seconds}s")
)

# 4. Inspect
result = inspector.inspect(shots)

# 5. แสดงผลใน dialog
dialog = MultiShotResultDialog(result, parent=self)
dialog.exec()

# 6. ตรวจสอบผลลัพธ์
decision = result['final_decision']['result']  # 'OK' or 'NG'
confidence = result['final_decision']['confidence']  # 'HIGH', 'MEDIUM', 'LOW'

print(f"Decision: {decision} (Confidence: {confidence})")
```

---

## Training Mode

### วิธีการเก็บข้อมูลด้วย Multi-Shot Capture Dialog

1. **เปิด Dialog:**
   ```python
   dialog = MultiShotCaptureDialog(camera_manager, settings, parent=self)
   dialog.exec()
   ```

2. **ตั้งค่า:**
   - เลือก Class: OK หรือ NG
   - จำนวน Shots: 2-9 ภาพ
   - ระยะห่าง: 1-5 วินาที

3. **Workflow:**
   ```
   กด "เริ่มถ่าย" → Countdown → Shot 1 → Countdown → Shot 2 → ... → เสร็จสิ้น
   ```

4. **ผลลัพธ์:**
   ```
   training_images/
   ├── OK/
   │   ├── wp001_shot1.jpg
   │   ├── wp001_shot2.jpg
   │   ├── wp001_shot3.jpg
   │   ├── wp001_shot4.jpg
   │   └── wp001_metadata.json
   ```

---

## Inspection Mode

### Multi-Shot Settings Dialog

```python
from ui.dialogs.multishot_inspection_settings_dialog import MultiShotInspectionSettingsDialog

# เปิด settings dialog
dialog = MultiShotInspectionSettingsDialog(settings, parent=self)
dialog.exec()
```

**การตั้งค่า:**
- ✓ เปิดใช้งาน Multi-Shot Inspection
- จำนวน Shots: 2-9
- ระยะห่าง: 0.5-10 วินาที
- กลยุทธ์: Majority Vote / Unanimous / Any Detection / Confidence Weighted
- ✓ บันทึกภาพทุก shots
- ✓ บันทึก Aggregation Report

---

## Aggregation Strategies

### 1. Majority Vote (แนะนำ) ⭐

```python
inspector = MultiShotInspector(model, strategy='majority_vote')
```

**กลไก:**
- Defect ต้องปรากฏใน **>50%** ของ shots
- ตัวอย่าง: 4 shots → ต้องเจอใน 3 shots ขึ้นไป

**ข้อดี:**
- ✅ Balance ระหว่าง accuracy และ sensitivity
- ✅ ลด false positives
- ✅ เหมาะกับการใช้งานทั่วไป

**Use Case:** งานตรวจสอบทั่วไป

---

### 2. Unanimous (เข้มงวด)

```python
inspector = MultiShotInspector(model, strategy='unanimous')
```

**กลไก:**
- Defect ต้องปรากฏใน **100%** ของ shots
- ตัวอย่าง: 4 shots → ต้องเจอทุกภาพ

**ข้อดี:**
- ✅ Confidence สูงมาก
- ✅ False positive ต่ำสุด

**Use Case:** ชิ้นงานราคาแพง, ไม่อยากทิ้งของดี

---

### 3. Any Detection (ไว)

```python
inspector = MultiShotInspector(model, strategy='any')
```

**กลไก:**
- Defect ปรากฏใน **shot ใดก็ได้**

**ข้อดี:**
- ✅ ตรวจจับทุกความเป็นไปได้
- ✅ ไม่พลาด defects

**Use Case:** Critical defects (อุตสาหกรรมยา, อาหาร, การบิน)

---

### 4. Confidence Weighted (สถิติ)

```python
inspector = MultiShotInspector(model, strategy='confidence_weighted')
```

**กลไก:**
- คำนวณ **weighted average** จาก confidence scores
- Weighted Score = avg_confidence × (votes / total_shots)

**ข้อดี:**
- ✅ Statistical validity
- ✅ Balanced scoring

**Use Case:** R&D, Quality audit, การวิจัย

---

## Multi-Shot Validation

### การตรวจสอบแบบมีเงื่อนไข (Validation Rules)

Multi-Shot Validator ใช้สำหรับกรณีที่ต้องการตรวจสอบ**จำนวนชิ้นส่วนที่แน่นอน**ในแต่ละจุด (shot)

### Use Case

**ตัวอย่าง:** ชิ้นงานมี 6 จุดตรวจสอบ แต่ละจุดต้องมี:
- Nut = 10 ชิ้น
- Bolt = 30 ชิ้น

**เงื่อนไข:** ถ้าจุดใดจุดหนึ่งไม่ตรงตามกำหนด → ชิ้นงาน FAIL

---

### วิธีการใช้งาน

```python
from core.multishot_validator import MultiShotValidator
from utils.multishot_capture import MultiShotCapture
from ultralytics import YOLO

# 1. Load model
model = YOLO('best.pt')

# 2. กำหนด validation rules
validation_rules = {
    "enabled": True,
    "pass_condition": "all",
    "rules": [
        {
            "type": "count_exact",
            "class_name": "nut",
            "expected": 10,
            "tolerance": 0
        },
        {
            "type": "count_exact",
            "class_name": "bolt",
            "expected": 30,
            "tolerance": 0
        }
    ]
}

# 3. สร้าง validator
validator = MultiShotValidator(
    model=model,
    validation_rules=validation_rules,
    strategy='unanimous'  # ทุก shot ต้อง pass
)

# 4. Capture 6 shots (แต่ละจุดตรวจสอบ)
capture = MultiShotCapture(camera, num_shots=6, interval=2.0)
shots = capture.capture_sequence(auto_advance=True)

# 5. Validate
result = validator.validate(shots)

# 6. ตรวจสอบผลลัพธ์
if result['final_decision'] == 'PASS':
    print(f"✅ PASS - ทุกจุดผ่าน ({result['summary']['passed_shots']}/{result['summary']['total_shots']})")
else:
    print(f"❌ FAIL - มี {result['summary']['failed_shots']} จุดไม่ผ่าน")

    # แสดงรายละเอียดจุดที่ fail
    for failed in result['failed_shot_details']:
        print(f"\n  Shot {failed['shot_id']}:")
        print(f"    Actual: {failed['class_counts']}")
        print(f"    Failed rules:")
        for rule in failed['failed_rules']:
            print(f"      - {rule['message']}")
```

---

### Validation Rule Types

#### 1. Count Exact (จำนวนที่แน่นอน)

```python
{
    "type": "count_exact",
    "class_name": "nut",
    "expected": 10,
    "tolerance": 0  # ยอมให้ผิดพลาดได้ ±0
}
```

**เงื่อนไข:** `abs(actual - expected) <= tolerance`

**ตัวอย่าง:**
- expected=10, tolerance=0 → ต้องเจอ 10 ชิ้นพอดี
- expected=10, tolerance=1 → ยอมรับ 9-11 ชิ้น

#### 2. Count Range (ช่วงจำนวน)

```python
{
    "type": "count_range",
    "class_name": "bolt",
    "min": 28,
    "max": 32
}
```

**เงื่อนไข:** `min <= actual <= max`

**Use Case:** ยอมให้มีช่วงค่อนข้างกว้าง

---

### Validation Strategies

#### 1. Unanimous (เข้มงวด) ⭐

```python
validator = MultiShotValidator(model, validation_rules, strategy='unanimous')
```

**กลไก:** **ทุกจุด (100%)** ต้อง pass

**Use Case:**
- ชิ้นงานที่ต้องการความแม่นยำสูง
- แต่ละจุดมีความสำคัญเท่ากัน
- **แนะนำสำหรับการตรวจนับ**

#### 2. Majority Vote

```python
validator = MultiShotValidator(model, validation_rules, strategy='majority_vote')
```

**กลไก:** **>50%** ของจุดต้อง pass

**Use Case:**
- ยอมให้จุดบางจุดไม่ผ่านได้
- ต้องการความยืดหยุ่น

---

### ตัวอย่างผลลัพธ์

**กรณี PASS:**

```
============================================================
Final Decision: PASS
Confidence: HIGH
============================================================

Summary:
  Total Shots: 6
  Passed: 6
  Failed: 0
  Pass Rate: 100.0%

Per-Shot Results:
  ✓ Shot 1: PASS
     Counts: {'nut': 10, 'bolt': 30}
       ✓ nut: 10/10
       ✓ bolt: 30/30
  ✓ Shot 2: PASS
     Counts: {'nut': 10, 'bolt': 30}
       ✓ nut: 10/10
       ✓ bolt: 30/30
  ...
```

**กรณี FAIL:**

```
============================================================
Final Decision: FAIL
Confidence: LOW
============================================================

Summary:
  Total Shots: 6
  Passed: 5
  Failed: 1
  Pass Rate: 83.3%

Per-Shot Results:
  ✓ Shot 1: PASS
  ✓ Shot 2: PASS
  ✗ Shot 3: FAIL
     Counts: {'nut': 9, 'bolt': 30}
       ✗ nut: 9/10 (FAIL)
       ✓ bolt: 30/30
  ...

⚠ Failed Shots Details:
  Shot 3:
    Actual counts: {'nut': 9, 'bolt': 30}
    Failed rules:
      - nut: 9/10 (FAIL)
```

---

### สรุปความแตกต่าง

| Feature | MultiShotInspector | MultiShotValidator |
|---------|-------------------|-------------------|
| **วัตถุประสงค์** | ตรวจหา defects | ตรวจนับจำนวนชิ้นส่วน |
| **Output** | OK/NG based on defects | PASS/FAIL based on counts |
| **Rules** | ไม่มี (detect อย่างเดียว) | มี validation rules |
| **Use Case** | Quality inspection | Assembly verification |
| **ตัวอย่าง** | หารอย scratch, crack | นับ nut=10, bolt=30 |

---

## ตัวอย่างการใช้งาน Code

### ตัวอย่างที่ 1: Inspection พื้นฐาน

```python
from core.multishot_inspector import MultiShotInspector
from utils.multishot_capture import MultiShotCapture

# Load model
from ultralytics import YOLO
model = YOLO('best.pt')

# Create inspector
inspector = MultiShotInspector(
    model=model,
    strategy='majority_vote',
    conf_threshold=0.5
)

# Capture 4 shots
capture = MultiShotCapture(camera, num_shots=4, interval=2.0)
shots = capture.capture_sequence(auto_advance=True)

# Inspect
result = inspector.inspect(shots)

# Check result
if result['final_decision']['result'] == 'NG':
    print(f"❌ REJECT - Found {result['final_decision']['total_defects']} defects")
    for defect in result['aggregation']['confirmed_defects']:
        print(f"  - {defect['class']}: {defect['votes']}/4 shots ({defect['vote_percentage']:.1f}%)")
else:
    print("✅ PASS")
```

**Output:**
```
❌ REJECT - Found 1 defects
  - scratch: 3/4 shots (75.0%)
```

---

### ตัวอย่างที่ 2: เปรียบเทียบ Strategies

```python
# Test different strategies
strategies = ['majority_vote', 'unanimous', 'any', 'confidence_weighted']

for strategy in strategies:
    inspector = MultiShotInspector(model, strategy=strategy)
    result = inspector.inspect(shots)

    print(f"\n{strategy}:")
    print(f"  Decision: {result['final_decision']['result']}")
    print(f"  Confidence: {result['final_decision']['confidence']}")
    print(f"  Defects: {result['final_decision']['defect_summary']}")
```

**Output:**
```
majority_vote:
  Decision: NG
  Confidence: HIGH
  Defects: {'scratch': 3}

unanimous:
  Decision: OK
  Confidence: HIGH
  Defects: {}

any:
  Decision: NG
  Confidence: MEDIUM
  Defects: {'scratch': 3, 'crack': 1}

confidence_weighted:
  Decision: NG
  Confidence: HIGH
  Defects: {'scratch': 3}
```

---

### ตัวอย่างที่ 3: บันทึกผลและภาพ

```python
import os
import json
from datetime import datetime

# Inspect
result = inspector.inspect(shots, save_annotated=True)

# Create result directory
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
result_dir = f"inspection_results/{timestamp}"
os.makedirs(result_dir, exist_ok=True)

# Save shots
for idx, shot_result in enumerate(result['shots'], 1):
    # Save original
    cv2.imwrite(f"{result_dir}/shot{idx}.jpg", shots[idx-1])

    # Save annotated
    if shot_result['annotated_image'] is not None:
        cv2.imwrite(f"{result_dir}/shot{idx}_annotated.jpg", shot_result['annotated_image'])

# Save result JSON
with open(f"{result_dir}/result.json", 'w', encoding='utf-8') as f:
    # Remove non-serializable data (images)
    result_copy = result.copy()
    for shot in result_copy.get('shots', []):
        shot['annotated_image'] = None

    json.dump(result_copy, f, indent=2, ensure_ascii=False)

print(f"Results saved to: {result_dir}")
```

---

## FAQ

### Q1: ต้องใช้ model ที่เทรนพิเศษไหม?

**A:** ไม่ต้อง! ใช้ model เดิมได้เลย

Multi-shot aggregation ทำงาน **หลัง inference** ไม่ได้แก้ model

---

### Q2: Training dataset ต้องเปลี่ยนรูปแบบไหม?

**A:** ไม่ต้อง!

แต่ละภาพ label แยกกันตามปกติ YOLO ไม่รู้ว่าภาพไหนเป็นชิ้นงานเดียวกัน

---

### Q3: เลือก strategy ไหนดี?

**A:** แนะนำ **Majority Vote** สำหรับการใช้งานทั่วไป

| Strategy | Use Case |
|----------|----------|
| Majority Vote | ทั่วไป (แนะนำ) |
| Unanimous | ชิ้นงานราคาแพง |
| Any | Critical defects |
| Confidence Weighted | R&D/Audit |

---

### Q4: กี่ shots ที่เหมาะสม?

**A:** **4 shots** เหมาะสำหรับส่วนใหญ่

- 2-3 shots: เร็ว แต่ confidence ต่ำ
- 4-6 shots: ✓ แนะนำ (balance)
- 9 shots: ช้า แต่ accuracy สูงสุด

---

### Q5: Multi-shot ช้ากว่า single shot เท่าไหร่?

**A:** ช้าประมาณ **N เท่า** (N = จำนวน shots)

- Single shot: ~50ms
- 4 shots: ~200ms
- แต่ได้ confidence สูงกว่ามาก!

---

## สรุป

### ข้อดี Multi-Shot Aggregation:

✅ **ความแม่นยำสูงขึ้น** - ลด false positives/negatives
✅ **Statistical confidence** - มี confidence level
✅ **ยืดหยุ่น** - 4 strategies เลือกได้
✅ **ง่ายต่อการ integrate** - ใช้ model เดิมได้
✅ **Backward compatible** - ไม่กระทบ training pipeline

### เหมาะสำหรับ:

- ✅ ชิ้นงานขนาดใหญ่
- ✅ ต้องการ confidence สูง
- ✅ Critical inspection
- ✅ Quality audit

---

**Happy Inspecting! 🎯**
