"""Span matching logic."""
from __future__ import annotations

from typing import List, Tuple

from models.ground_truth import Entity
from models.prediction import Prediction


class SpanMatcher:
	def __init__(self, strategy: str = "strict", iou_threshold: float = 0.5, token_threshold: float = 0.5):
		self.strategy = strategy.lower()
		self.iou_threshold = iou_threshold
		self.token_threshold = token_threshold
		if self.strategy not in {"strict", "lenient", "token"}:
			raise ValueError("Invalid strategy. Use strict, lenient, or token.")

	def match(self, ground_truth: Entity, prediction: Prediction) -> bool:
		if ground_truth.entity_type != prediction.entity_type:
			return False
		if self.strategy == "strict":
			return ground_truth.start == prediction.start and ground_truth.end == prediction.end
		if self.strategy == "lenient":
			return self._iou(ground_truth, prediction) >= self.iou_threshold
		if self.strategy == "token":
			return self._token_overlap(ground_truth, prediction) >= self.token_threshold
		return False

	def _iou(self, gt: Entity, pred: Prediction) -> float:
		overlap_start = max(gt.start, pred.start)
		overlap_end = min(gt.end, pred.end)
		overlap = max(0, overlap_end - overlap_start)
		union_start = min(gt.start, pred.start)
		union_end = max(gt.end, pred.end)
		union = union_end - union_start
		return overlap / union if union > 0 else 0.0

	def _token_overlap(self, gt: Entity, pred: Prediction) -> float:
		gt_tokens = set((gt.text or "").lower().split())
		pred_tokens = set((pred.text or "").lower().split())
		if not gt_tokens and not pred_tokens:
			return 0.0
		common = gt_tokens.intersection(pred_tokens)
		total = gt_tokens.union(pred_tokens)
		return len(common) / len(total) if total else 0.0

	def find_matches(
		self,
		ground_truths: List[Entity],
		predictions: List[Prediction],
	) -> Tuple[List[Tuple[Entity, Prediction]], List[Prediction], List[Entity]]:
		matched_pairs: List[Tuple[Entity, Prediction]] = []
		matched_gt = set()
		matched_pred = set()

		for pred_idx, pred in enumerate(predictions):
			for gt_idx, gt in enumerate(ground_truths):
				if gt_idx in matched_gt:
					continue
				if self.match(gt, pred):
					matched_pairs.append((gt, pred))
					matched_gt.add(gt_idx)
					matched_pred.add(pred_idx)
					break

		false_positives = [p for i, p in enumerate(predictions) if i not in matched_pred]
		false_negatives = [g for i, g in enumerate(ground_truths) if i not in matched_gt]

		return matched_pairs, false_positives, false_negatives
