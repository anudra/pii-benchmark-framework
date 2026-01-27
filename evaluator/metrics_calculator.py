"""Metrics calculation logic."""
from __future__ import annotations

from typing import Dict, List, Optional
from collections import defaultdict

from models.ground_truth import GroundTruth
from models.prediction import SystemOutput
from models.results import Metrics, EvaluationResult, ErrorDetail, ErrorCategory
from models.redaction import RedactedDocument
from evaluator.span_matcher import SpanMatcher
from evaluator.redaction_evaluator import RedactionEvaluator


class MetricsCalculator:
	def __init__(self, matching_strategy: str = "strict", iou_threshold: float = 0.5, token_threshold: float = 0.5):
		self.matcher = SpanMatcher(matching_strategy, iou_threshold, token_threshold)
		self.matching_strategy = matching_strategy
		self.redaction_evaluator = RedactionEvaluator()

	def evaluate(self, ground_truths: List[GroundTruth], predictions: List[SystemOutput]) -> EvaluationResult:
		gt_doc_ids = {gt.doc_id for gt in ground_truths}
		pred_doc_ids = {pred.doc_id for pred in predictions}
		if gt_doc_ids != pred_doc_ids:
			missing = gt_doc_ids - pred_doc_ids
			extra = pred_doc_ids - gt_doc_ids
			raise ValueError(f"Document ID mismatch. Missing: {missing}, Extra: {extra}")

		gt_map = {gt.doc_id: gt for gt in ground_truths}
		pred_map = {pred.doc_id: pred for pred in predictions}

		overall_tp = 0
		overall_fp = 0
		overall_fn = 0

		entity_counts = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

		all_false_positives: List[ErrorDetail] = []
		all_false_negatives: List[ErrorDetail] = []

		per_document_metrics: Dict[str, Metrics] = {}

		for doc_id in gt_doc_ids:
			gt = gt_map[doc_id]
			pred = pred_map[doc_id]

			matched_pairs, false_positives, false_negatives = self.matcher.find_matches(gt.entities, pred.predictions)

			tp = len(matched_pairs)
			fp = len(false_positives)
			fn = len(false_negatives)

			overall_tp += tp
			overall_fp += fp
			overall_fn += fn

			doc_metrics = Metrics(true_positives=tp, false_positives=fp, false_negatives=fn)
			doc_metrics.calculate_metrics()
			per_document_metrics[doc_id] = doc_metrics

			for gt_entity, _ in matched_pairs:
				entity_counts[gt_entity.entity_type]["tp"] += 1

			for fp_pred in false_positives:
				entity_counts[fp_pred.entity_type]["fp"] += 1
				all_false_positives.append(
					ErrorDetail(
						doc_id=doc_id,
						entity_type=fp_pred.entity_type,
						start=fp_pred.start,
						end=fp_pred.end,
						text=fp_pred.text or "",
						error_type=ErrorCategory.FALSE_POSITIVE,
					)
				)

			for fn_gt in false_negatives:
				entity_counts[fn_gt.entity_type]["fn"] += 1
				all_false_negatives.append(
					ErrorDetail(
						doc_id=doc_id,
						entity_type=fn_gt.entity_type,
						start=fn_gt.start,
						end=fn_gt.end,
						text=fn_gt.text or "",
						error_type=ErrorCategory.FALSE_NEGATIVE,
					)
				)

		overall_metrics = Metrics(
			true_positives=overall_tp,
			false_positives=overall_fp,
			false_negatives=overall_fn,
		)
		overall_metrics.calculate_metrics()

		per_entity_metrics: Dict[str, Metrics] = {}
		for entity_type, counts in entity_counts.items():
			metrics = Metrics(
				true_positives=counts["tp"],
				false_positives=counts["fp"],
				false_negatives=counts["fn"],
			)
			metrics.calculate_metrics()
			per_entity_metrics[entity_type] = metrics

		total_ground_truth = sum(len(gt.entities) for gt in ground_truths)
		total_predicted = sum(len(pred.predictions) for pred in predictions)

		return EvaluationResult(
			overall_metrics=overall_metrics,
			per_entity_metrics=per_entity_metrics,
			per_document_metrics=per_document_metrics,
			false_positives=all_false_positives,
			false_negatives=all_false_negatives,
			total_documents=len(ground_truths),
			total_ground_truth_entities=total_ground_truth,
			total_predicted_entities=total_predicted,
			matching_strategy=self.matching_strategy,
		)

	def evaluate_single_document(self, ground_truth: GroundTruth, prediction: SystemOutput) -> Dict:
		matched_pairs, false_positives, false_negatives = self.matcher.find_matches(
			ground_truth.entities, prediction.predictions
		)
		tp = len(matched_pairs)
		fp = len(false_positives)
		fn = len(false_negatives)
		metrics = Metrics(true_positives=tp, false_positives=fp, false_negatives=fn)
		metrics.calculate_metrics()
		return {
			"doc_id": ground_truth.doc_id,
			"metrics": metrics,
			"matched_pairs": matched_pairs,
			"false_positives": false_positives,
			"false_negatives": false_negatives,
		}

	def evaluate_with_redaction(
		self,
		ground_truths: List[GroundTruth],
		predictions: List[SystemOutput],
		redacted_docs: Optional[List[RedactedDocument]] = None,
	) -> EvaluationResult:
		result = self.evaluate(ground_truths, predictions)

		if redacted_docs:
			errors, quality = self.redaction_evaluator.evaluate_batch(ground_truths, redacted_docs)
			result.redaction_errors = errors
			result.redaction_quality_score = quality
			result.missed_redactions = len([e for e in errors if e.error_type == "missed_redaction"])
			result.over_redactions = len([e for e in errors if e.error_type == "over_redaction"])

		return result
