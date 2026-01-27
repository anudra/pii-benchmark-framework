"""Redaction evaluation logic."""
from __future__ import annotations

from typing import List, Tuple

from models.ground_truth import GroundTruth, Entity
from models.redaction import RedactedDocument, RedactionError, RedactionErrorType


class RedactionEvaluator:
	def __init__(self, redaction_markers: List[str] | None = None):
		self.redaction_markers = redaction_markers or ["[REDACTED]", "[PII]", "***", "XXXX"]

	def evaluate(self, ground_truth: GroundTruth, redacted_doc: RedactedDocument) -> Tuple[List[RedactionError], float]:
		if ground_truth.doc_id != redacted_doc.doc_id:
			raise ValueError(f"Document ID mismatch: {ground_truth.doc_id} != {redacted_doc.doc_id}")

		errors: List[RedactionError] = []

		# If redacted spans are not provided, use text-based check only
		if not redacted_doc.redacted_spans:
			missed = 0
			for entity in ground_truth.entities:
				entity_text = entity.text or ""
				if entity_text and entity_text in redacted_doc.redacted_text:
					missed += 1
					errors.append(
						RedactionError(
							doc_id=redacted_doc.doc_id,
							error_type=RedactionErrorType.MISSED_REDACTION,
							entity_type=entity.entity_type,
							start=entity.start,
							end=entity.end,
							expected_text="[REDACTED]",
							actual_text=entity_text,
							severity="high",
						)
					)

			quality = 1.0 - (missed / len(ground_truth.entities)) if ground_truth.entities else 1.0
			return errors, max(0.0, quality)

		for entity in ground_truth.entities:
			error = self._check_entity_redacted(entity, redacted_doc)
			if error:
				errors.append(error)

		errors.extend(self._check_over_redaction(ground_truth, redacted_doc))

		total = len(ground_truth.entities)
		missed = len([e for e in errors if e.error_type in {RedactionErrorType.MISSED_REDACTION, RedactionErrorType.PARTIAL_REDACTION}])
		over = len([e for e in errors if e.error_type == RedactionErrorType.OVER_REDACTION])

		quality = 1.0 - (missed / total) if total > 0 else 1.0
		quality -= (over * 0.05)
		quality = max(0.0, quality)

		return errors, quality

	def _check_entity_redacted(self, entity: Entity, redacted_doc: RedactedDocument) -> RedactionError | None:
		actual_text = redacted_doc.redacted_text[entity.start:entity.end]
		is_redacted = any(marker in actual_text for marker in self.redaction_markers)

		if not is_redacted:
			if actual_text != (entity.text or ""):
				return RedactionError(
					doc_id=redacted_doc.doc_id,
					error_type=RedactionErrorType.PARTIAL_REDACTION,
					entity_type=entity.entity_type,
					start=entity.start,
					end=entity.end,
					expected_text="[REDACTED]",
					actual_text=actual_text,
					severity="high",
				)
			return RedactionError(
				doc_id=redacted_doc.doc_id,
				error_type=RedactionErrorType.MISSED_REDACTION,
				entity_type=entity.entity_type,
				start=entity.start,
				end=entity.end,
				expected_text="[REDACTED]",
				actual_text=actual_text,
				severity="high",
			)

		return None

	def _check_over_redaction(self, ground_truth: GroundTruth, redacted_doc: RedactedDocument) -> List[RedactionError]:
		errors: List[RedactionError] = []
		sensitive_positions = set()
		for entity in ground_truth.entities:
			sensitive_positions.update(range(entity.start, entity.end))

		for marker in self.redaction_markers:
			index = 0
			while index < len(redacted_doc.redacted_text):
				pos = redacted_doc.redacted_text.find(marker, index)
				if pos == -1:
					break
				marker_positions = set(range(pos, pos + len(marker)))
				if not marker_positions.intersection(sensitive_positions):
					errors.append(
						RedactionError(
							doc_id=redacted_doc.doc_id,
							error_type=RedactionErrorType.OVER_REDACTION,
							entity_type="UNKNOWN",
							start=pos,
							end=pos + len(marker),
							expected_text=redacted_doc.text[pos:pos + len(marker)] if pos < len(redacted_doc.text) else "",
							actual_text=marker,
							severity="medium",
						)
					)
				index = pos + 1

		return errors

	def evaluate_batch(
		self,
		ground_truths: List[GroundTruth],
		redacted_docs: List[RedactedDocument],
	) -> Tuple[List[RedactionError], float]:
		gt_map = {gt.doc_id: gt for gt in ground_truths}
		rd_map = {rd.doc_id: rd for rd in redacted_docs}

		if set(gt_map.keys()) != set(rd_map.keys()):
			missing = set(gt_map.keys()) - set(rd_map.keys())
			extra = set(rd_map.keys()) - set(gt_map.keys())
			raise ValueError(f"Document mismatch. Missing: {missing}, Extra: {extra}")

		all_errors: List[RedactionError] = []
		scores: List[float] = []

		for doc_id in gt_map:
			errors, score = self.evaluate(gt_map[doc_id], rd_map[doc_id])
			all_errors.extend(errors)
			scores.append(score)

		avg_score = sum(scores) / len(scores) if scores else 0.0
		return all_errors, avg_score
