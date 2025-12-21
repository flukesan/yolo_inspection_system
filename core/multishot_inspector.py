"""
Multi-Shot Inspection with Aggregation
ระบบตรวจสอบแบบหลายภาพพร้อม aggregation strategies
"""
import time
from typing import List, Dict, Any, Optional
import numpy as np


class MultiShotInspector:
    """
    Multi-shot inspection with various aggregation strategies

    Strategies:
    - majority_vote: Defect must appear in >50% of shots
    - unanimous: Defect must appear in 100% of shots (very strict)
    - any: Defect appears in any shot (very sensitive)
    - confidence_weighted: Weighted average of confidence scores
    """

    STRATEGIES = {
        'majority_vote': 'Majority Vote (≥50%)',
        'unanimous': 'Unanimous (100%)',
        'any': 'Any Detection (≥1)',
        'confidence_weighted': 'Confidence Weighted'
    }

    def __init__(self, model, strategy: str = 'majority_vote', conf_threshold: float = 0.5):
        """
        Initialize Multi-Shot Inspector

        Args:
            model: YOLO model instance
            strategy: Aggregation strategy
            conf_threshold: Confidence threshold for detections
        """
        self.model = model
        self.strategy = strategy
        self.conf_threshold = conf_threshold

        if strategy not in self.STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy}. Must be one of {list(self.STRATEGIES.keys())}")

    def inspect(self, shots: List[np.ndarray], save_annotated: bool = False) -> Dict[str, Any]:
        """
        Inspect multiple shots and aggregate results

        Args:
            shots: List of images (numpy arrays)
            save_annotated: Whether to save annotated images

        Returns:
            Aggregated result dictionary with decision, confidence, and details
        """
        if not shots:
            return {
                'decision': 'ERROR',
                'message': 'No shots provided',
                'total_shots': 0
            }

        # Inference each shot
        shot_results = []
        for i, shot in enumerate(shots, 1):
            result = self._inspect_single_shot(shot, i)
            shot_results.append(result)

        # Aggregate results
        aggregated = self._aggregate_results(shot_results)

        # Add metadata
        aggregated['total_shots'] = len(shots)
        aggregated['strategy'] = self.strategy
        aggregated['conf_threshold'] = self.conf_threshold

        return aggregated

    def _inspect_single_shot(self, image: np.ndarray, shot_id: int) -> Dict[str, Any]:
        """
        Inspect single shot

        Args:
            image: Image to inspect
            shot_id: Shot identifier

        Returns:
            Detection results for this shot
        """
        start_time = time.time()

        # Run YOLO inference
        results = self.model(image, conf=self.conf_threshold, verbose=False)

        # Extract detections
        detections = []
        annotated_image = None

        if results and len(results) > 0:
            result = results[0]

            # Get annotated image
            if hasattr(result, 'plot'):
                annotated_image = result.plot()

            # Extract boxes
            if hasattr(result, 'boxes') and result.boxes is not None:
                boxes = result.boxes

                for i in range(len(boxes)):
                    detections.append({
                        'class': self.model.names[int(boxes.cls[i])],
                        'confidence': float(boxes.conf[i]),
                        'bbox': boxes.xyxy[i].cpu().numpy().tolist()
                    })

        inference_time = (time.time() - start_time) * 1000

        return {
            'shot_id': shot_id,
            'detections': detections,
            'inference_time_ms': round(inference_time, 2),
            'annotated_image': annotated_image
        }

    def _aggregate_results(self, shot_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate results from all shots based on strategy

        Args:
            shot_results: List of results from each shot

        Returns:
            Aggregated result
        """
        if self.strategy == 'majority_vote':
            return self._majority_vote(shot_results)
        elif self.strategy == 'unanimous':
            return self._unanimous(shot_results)
        elif self.strategy == 'any':
            return self._any_detection(shot_results)
        elif self.strategy == 'confidence_weighted':
            return self._confidence_weighted(shot_results)
        else:
            # Fallback to majority vote
            return self._majority_vote(shot_results)

    def _majority_vote(self, shot_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Majority vote: Defect must appear in >50% of shots
        """
        total_shots = len(shot_results)
        threshold = total_shots / 2

        # Count votes for each defect class
        defect_votes = {}
        defect_confidences = {}

        for result in shot_results:
            seen_classes = set()

            for det in result['detections']:
                class_name = det['class']

                # Count vote (only once per shot per class)
                if class_name not in seen_classes:
                    defect_votes[class_name] = defect_votes.get(class_name, 0) + 1
                    seen_classes.add(class_name)

                # Collect confidences
                if class_name not in defect_confidences:
                    defect_confidences[class_name] = []
                defect_confidences[class_name].append(det['confidence'])

        # Determine confirmed defects
        confirmed_defects = []
        for class_name, votes in defect_votes.items():
            if votes > threshold:
                avg_conf = sum(defect_confidences[class_name]) / len(defect_confidences[class_name])
                vote_pct = (votes / total_shots) * 100

                confirmed_defects.append({
                    'class': class_name,
                    'votes': votes,
                    'vote_percentage': round(vote_pct, 1),
                    'avg_confidence': round(avg_conf, 3),
                    'status': 'CONFIRMED'
                })

        # Calculate agreement rate
        agreement_rate = 0
        if defect_votes:
            max_votes = max(defect_votes.values())
            agreement_rate = max_votes / total_shots

        # Final decision
        decision = "NG" if confirmed_defects else "OK"

        # Confidence level
        if confirmed_defects:
            max_vote_pct = max(d['vote_percentage'] for d in confirmed_defects)
            if max_vote_pct >= 75:
                confidence = "HIGH"
            elif max_vote_pct >= 60:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"
        else:
            confidence = "HIGH"  # High confidence in OK result

        # Total inference time
        total_time = sum(r['inference_time_ms'] for r in shot_results)

        return {
            'shots': shot_results,
            'aggregation': {
                'method': 'majority_vote',
                'defect_votes': defect_votes,
                'agreement_rate': round(agreement_rate, 3),
                'confirmed_defects': confirmed_defects
            },
            'final_decision': {
                'result': decision,
                'confidence': confidence,
                'total_defects': len(confirmed_defects),
                'defect_summary': {d['class']: d['votes'] for d in confirmed_defects},
                'total_inference_time_ms': round(total_time, 2)
            }
        }

    def _unanimous(self, shot_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Unanimous: Defect must appear in 100% of shots (very strict)
        """
        total_shots = len(shot_results)

        # Count votes
        defect_votes = {}
        defect_confidences = {}

        for result in shot_results:
            seen_classes = set()

            for det in result['detections']:
                class_name = det['class']

                if class_name not in seen_classes:
                    defect_votes[class_name] = defect_votes.get(class_name, 0) + 1
                    seen_classes.add(class_name)

                if class_name not in defect_confidences:
                    defect_confidences[class_name] = []
                defect_confidences[class_name].append(det['confidence'])

        # Only confirm if unanimous (100%)
        confirmed_defects = []
        for class_name, votes in defect_votes.items():
            if votes == total_shots:  # Must be in ALL shots
                avg_conf = sum(defect_confidences[class_name]) / len(defect_confidences[class_name])

                confirmed_defects.append({
                    'class': class_name,
                    'votes': votes,
                    'vote_percentage': 100.0,
                    'avg_confidence': round(avg_conf, 3),
                    'status': 'UNANIMOUS'
                })

        decision = "NG" if confirmed_defects else "OK"
        confidence = "VERY_HIGH" if confirmed_defects or not defect_votes else "HIGH"

        total_time = sum(r['inference_time_ms'] for r in shot_results)

        return {
            'shots': shot_results,
            'aggregation': {
                'method': 'unanimous',
                'defect_votes': defect_votes,
                'confirmed_defects': confirmed_defects
            },
            'final_decision': {
                'result': decision,
                'confidence': confidence,
                'total_defects': len(confirmed_defects),
                'defect_summary': {d['class']: d['votes'] for d in confirmed_defects},
                'total_inference_time_ms': round(total_time, 2)
            }
        }

    def _any_detection(self, shot_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Any: Defect appears in any shot (very sensitive)
        """
        total_shots = len(shot_results)

        # Collect all unique defects
        defect_votes = {}
        defect_confidences = {}

        for result in shot_results:
            seen_classes = set()

            for det in result['detections']:
                class_name = det['class']

                if class_name not in seen_classes:
                    defect_votes[class_name] = defect_votes.get(class_name, 0) + 1
                    seen_classes.add(class_name)

                if class_name not in defect_confidences:
                    defect_confidences[class_name] = []
                defect_confidences[class_name].append(det['confidence'])

        # Any detection is confirmed
        confirmed_defects = []
        for class_name, votes in defect_votes.items():
            avg_conf = sum(defect_confidences[class_name]) / len(defect_confidences[class_name])
            vote_pct = (votes / total_shots) * 100

            confirmed_defects.append({
                'class': class_name,
                'votes': votes,
                'vote_percentage': round(vote_pct, 1),
                'avg_confidence': round(avg_conf, 3),
                'status': 'DETECTED'
            })

        decision = "NG" if confirmed_defects else "OK"

        # Lower confidence since we accept any detection
        if confirmed_defects:
            max_vote_pct = max(d['vote_percentage'] for d in confirmed_defects)
            if max_vote_pct >= 50:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"
        else:
            confidence = "HIGH"

        total_time = sum(r['inference_time_ms'] for r in shot_results)

        return {
            'shots': shot_results,
            'aggregation': {
                'method': 'any_detection',
                'defect_votes': defect_votes,
                'confirmed_defects': confirmed_defects
            },
            'final_decision': {
                'result': decision,
                'confidence': confidence,
                'total_defects': len(confirmed_defects),
                'defect_summary': {d['class']: d['votes'] for d in confirmed_defects},
                'total_inference_time_ms': round(total_time, 2)
            }
        }

    def _confidence_weighted(self, shot_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Confidence weighted: Use weighted average of confidence scores
        """
        total_shots = len(shot_results)

        # Collect confidences for each class
        defect_confidences = {}
        defect_votes = {}

        for result in shot_results:
            for det in result['detections']:
                class_name = det['class']

                if class_name not in defect_confidences:
                    defect_confidences[class_name] = []
                    defect_votes[class_name] = 0

                defect_confidences[class_name].append(det['confidence'])
                defect_votes[class_name] += 1

        # Calculate weighted average
        confirmed_defects = []
        for class_name, confidences in defect_confidences.items():
            # Average confidence across all detections
            avg_conf = sum(confidences) / len(confidences)

            # Number of shots where this defect appeared
            shots_with_defect = defect_votes[class_name]
            vote_pct = (shots_with_defect / total_shots) * 100

            # Weighted score: combine confidence and occurrence rate
            weighted_score = avg_conf * (vote_pct / 100)

            # Confirm if weighted score is high enough
            if weighted_score > 0.4:  # Threshold for confirmation
                confirmed_defects.append({
                    'class': class_name,
                    'votes': shots_with_defect,
                    'vote_percentage': round(vote_pct, 1),
                    'avg_confidence': round(avg_conf, 3),
                    'weighted_score': round(weighted_score, 3),
                    'status': 'CONFIRMED'
                })

        decision = "NG" if confirmed_defects else "OK"

        # Confidence based on weighted scores
        if confirmed_defects:
            max_score = max(d['weighted_score'] for d in confirmed_defects)
            if max_score >= 0.7:
                confidence = "HIGH"
            elif max_score >= 0.5:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"
        else:
            confidence = "HIGH"

        total_time = sum(r['inference_time_ms'] for r in shot_results)

        return {
            'shots': shot_results,
            'aggregation': {
                'method': 'confidence_weighted',
                'defect_votes': defect_votes,
                'confirmed_defects': confirmed_defects
            },
            'final_decision': {
                'result': decision,
                'confidence': confidence,
                'total_defects': len(confirmed_defects),
                'defect_summary': {d['class']: d['votes'] for d in confirmed_defects},
                'total_inference_time_ms': round(total_time, 2)
            }
        }

    def get_strategy_description(self) -> str:
        """Get description of current strategy"""
        return self.STRATEGIES.get(self.strategy, "Unknown")
