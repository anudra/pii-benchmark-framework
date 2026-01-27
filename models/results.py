"""Evaluation results schemas."""
from __future__ import annotations

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Metrics(BaseModel):
	true_positives: int = Field(default=0, ge=0)
	false_positives: int = Field(default=0, ge=0)
	false_negatives: int = Field(default=0, ge=0)
	precision: float = Field(default=0.0, ge=0.0, le=1.0)
	recall: float = Field(default=0.0, ge=0.0, le=1.0)
	f1_score: float = Field(default=0.0, ge=0.0, le=1.0)

	def calculate_metrics(self) -> None:
		tp = self.true_positives
		fp = self.false_positives
		fn = self.false_negatives
		self.precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
		self.recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
		self.f1_score = (
			(2 * self.precision * self.recall) / (self.precision + self.recall)
			if (self.precision + self.recall) > 0
			else 0.0
		)


class ErrorCategory:
	FALSE_POSITIVE = "false_positive"
	FALSE_NEGATIVE = "false_negative"
	MISCLASSIFICATION = "misclassification"
	MISSED_DETECTION = "missed_detection"
	OVER_DETECTION = "over_detection"


class ErrorDetail(BaseModel):
	doc_id: str
	entity_type: str
	start: int
	end: int
	text: str
	error_type: str
	predicted_type: Optional[str] = Field(default=None)
	severity: str = Field(default="medium")

	def __str__(self) -> str:
		if self.predicted_type:
			return (
				f"[{self.doc_id}] {self.error_type}: {self.entity_type}→{self.predicted_type} "
				f"({self.start}-{self.end}) '{self.text}'"
			)
		return f"[{self.doc_id}] {self.error_type}: {self.entity_type}({self.start}-{self.end}) '{self.text}'"


class EvaluationResult(BaseModel):
	overall_metrics: Metrics
	per_entity_metrics: Dict[str, Metrics] = Field(default_factory=dict)
	per_document_metrics: Dict[str, Metrics] = Field(default_factory=dict)

	false_positives: List[ErrorDetail] = Field(default_factory=list)
	false_negatives: List[ErrorDetail] = Field(default_factory=list)
	misclassifications: List[ErrorDetail] = Field(default_factory=list)

	redaction_quality_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
	redaction_errors: List = Field(default_factory=list)
	missed_redactions: int = Field(default=0, ge=0)
	over_redactions: int = Field(default=0, ge=0)

	total_documents: int = Field(default=0, ge=0)
	total_ground_truth_entities: int = Field(default=0, ge=0)
	total_predicted_entities: int = Field(default=0, ge=0)
	matching_strategy: str = Field(default="strict")
	evaluation_timestamp: Optional[str] = Field(default=None)

	def __init__(self, **data):
		super().__init__(**data)
		if self.evaluation_timestamp is None:
			self.evaluation_timestamp = datetime.now().isoformat()
