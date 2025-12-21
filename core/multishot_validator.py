"""
Multi-Shot Validation
ตรวจสอบแต่ละ shot พร้อม validation rules แล้ว aggregate
"""
from typing import List, Dict, Any, Optional
from core.multishot_inspector import MultiShotInspector


class MultiShotValidator:
    """
    Multi-shot inspection with validation rules per shot

    Use case:
    - แต่ละจุด (shot) ต้องมีชิ้นส่วนครบตามกำหนด
    - เช่น nut=10, bolt=30 ทุกจุด
    - ถ้าจุดใดไม่ครบ → FAIL
    """

    def __init__(self, model, validation_rules: Dict[str, Any], strategy: str = 'unanimous'):
        """
        Initialize Multi-Shot Validator

        Args:
            model: YOLO model
            validation_rules: Validation rules dictionary
            strategy: 'unanimous' (ทุก shot ต้อง pass) หรือ 'majority_vote'
        """
        self.model = model
        self.validation_rules = validation_rules
        self.strategy = strategy

        # สร้าง inspector สำหรับ detection
        self.inspector = MultiShotInspector(
            model=model,
            strategy='any',  # ใช้ any เพื่อเก็บ detections ทั้งหมด
            conf_threshold=0.5
        )

    def validate(self, shots: List) -> Dict[str, Any]:
        """
        Inspect และ validate แต่ละ shot

        Args:
            shots: List of images

        Returns:
            Validation result with per-shot details
        """
        # 1. Inspect ทุก shots
        inspection_result = self.inspector.inspect(shots)

        # 2. Validate แต่ละ shot
        shot_validations = []
        for shot_result in inspection_result['shots']:
            validation = self._validate_single_shot(shot_result)
            shot_validations.append(validation)

        # 3. Aggregate validation results
        final_result = self._aggregate_validations(shot_validations)

        # 4. Combine with inspection result
        final_result['inspection_result'] = inspection_result
        final_result['shot_validations'] = shot_validations

        return final_result

    def _validate_single_shot(self, shot_result: Dict) -> Dict[str, Any]:
        """
        Validate single shot ตาม rules

        Args:
            shot_result: Shot result from inspector

        Returns:
            Validation result for this shot
        """
        shot_id = shot_result['shot_id']
        detections = shot_result['detections']

        # นับจำนวนแต่ละ class
        class_counts = {}
        for det in detections:
            class_name = det['class']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

        # ตรวจสอบตาม rules
        validation_results = []
        all_passed = True

        for rule in self.validation_rules.get('rules', []):
            rule_type = rule.get('type')
            class_name = rule.get('class_name')

            if rule_type == 'count_exact':
                expected = rule.get('expected', 0)
                tolerance = rule.get('tolerance', 0)
                actual = class_counts.get(class_name, 0)

                # ตรวจสอบ
                passed = abs(actual - expected) <= tolerance

                validation_results.append({
                    'rule_type': 'count_exact',
                    'class_name': class_name,
                    'expected': expected,
                    'actual': actual,
                    'tolerance': tolerance,
                    'passed': passed,
                    'message': f"{class_name}: {actual}/{expected}" + ("" if passed else f" (FAIL)")
                })

                if not passed:
                    all_passed = False

            elif rule_type == 'count_range':
                min_count = rule.get('min', 0)
                max_count = rule.get('max', 999)
                actual = class_counts.get(class_name, 0)

                passed = min_count <= actual <= max_count

                validation_results.append({
                    'rule_type': 'count_range',
                    'class_name': class_name,
                    'min': min_count,
                    'max': max_count,
                    'actual': actual,
                    'passed': passed,
                    'message': f"{class_name}: {actual} (range: {min_count}-{max_count})" + ("" if passed else " (FAIL)")
                })

                if not passed:
                    all_passed = False

        return {
            'shot_id': shot_id,
            'class_counts': class_counts,
            'validation_results': validation_results,
            'passed': all_passed,
            'status': 'PASS' if all_passed else 'FAIL'
        }

    def _aggregate_validations(self, shot_validations: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate validation results จากทุก shots

        Args:
            shot_validations: List of validation results

        Returns:
            Final aggregated result
        """
        total_shots = len(shot_validations)
        passed_shots = sum(1 for v in shot_validations if v['passed'])
        failed_shots = total_shots - passed_shots

        # Determine final decision based on strategy
        if self.strategy == 'unanimous':
            # ทุก shot ต้อง pass
            final_decision = 'PASS' if passed_shots == total_shots else 'FAIL'
            confidence = 'HIGH' if failed_shots == 0 else 'LOW'

        elif self.strategy == 'majority_vote':
            # มากกว่าครึ่ง pass → PASS
            final_decision = 'PASS' if passed_shots > (total_shots / 2) else 'FAIL'
            confidence = 'HIGH' if passed_shots >= total_shots * 0.75 else 'MEDIUM'

        else:
            # Default: unanimous
            final_decision = 'PASS' if passed_shots == total_shots else 'FAIL'
            confidence = 'HIGH'

        # สร้าง summary
        summary = {
            'total_shots': total_shots,
            'passed_shots': passed_shots,
            'failed_shots': failed_shots,
            'pass_rate': (passed_shots / total_shots * 100) if total_shots > 0 else 0
        }

        # รวบรวมข้อมูลจุดที่ fail
        failed_shot_details = [
            {
                'shot_id': v['shot_id'],
                'class_counts': v['class_counts'],
                'failed_rules': [r for r in v['validation_results'] if not r['passed']]
            }
            for v in shot_validations if not v['passed']
        ]

        return {
            'final_decision': final_decision,
            'confidence': confidence,
            'strategy': self.strategy,
            'summary': summary,
            'failed_shot_details': failed_shot_details
        }


# ===== ตัวอย่างการใช้งาน =====

if __name__ == '__main__':
    from ultralytics import YOLO
    import numpy as np

    # Load model
    model = YOLO('best.pt')

    # กำหนด validation rules
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

    # สร้าง validator
    validator = MultiShotValidator(
        model=model,
        validation_rules=validation_rules,
        strategy='unanimous'  # ทุก shot ต้อง pass
    )

    # ถ่ายภาพ 6 shots (ตัวอย่าง)
    shots = []  # ... capture 6 shots here

    # Validate
    result = validator.validate(shots)

    # แสดงผล
    print(f"\n{'='*60}")
    print(f"Final Decision: {result['final_decision']}")
    print(f"Confidence: {result['confidence']}")
    print(f"{'='*60}")
    print(f"\nSummary:")
    print(f"  Total Shots: {result['summary']['total_shots']}")
    print(f"  Passed: {result['summary']['passed_shots']}")
    print(f"  Failed: {result['summary']['failed_shots']}")
    print(f"  Pass Rate: {result['summary']['pass_rate']:.1f}%")

    # แสดงรายละเอียดแต่ละ shot
    print(f"\nPer-Shot Results:")
    for shot_val in result['shot_validations']:
        status_icon = "✓" if shot_val['passed'] else "✗"
        print(f"  {status_icon} Shot {shot_val['shot_id']}: {shot_val['status']}")
        print(f"     Counts: {shot_val['class_counts']}")

        for val_result in shot_val['validation_results']:
            pass_icon = "✓" if val_result['passed'] else "✗"
            print(f"       {pass_icon} {val_result['message']}")

    # แสดงจุดที่ fail
    if result['failed_shot_details']:
        print(f"\n⚠ Failed Shots Details:")
        for failed in result['failed_shot_details']:
            print(f"  Shot {failed['shot_id']}:")
            print(f"    Actual counts: {failed['class_counts']}")
            print(f"    Failed rules:")
            for rule in failed['failed_rules']:
                print(f"      - {rule['message']}")
