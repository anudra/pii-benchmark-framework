"""Prediction schemas."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class Prediction(BaseModel):
	"""Represents a predicted sensitive entity."""

	entity_type: str = Field(..., description="Predicted entity type")
	start: int = Field(..., ge=0, description="Start character index (inclusive)")
	end: int = Field(..., gt=0, description="End character index (exclusive)")
	text: Optional[str] = Field(default=None, description="Optional predicted text span")
	confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)

	def extract_text(self, document_text: str) -> None:
		if self.text is None and self.start < len(document_text):
			self.text = document_text[self.start:self.end]


class SystemOutput(BaseModel):
	"""Predictions for a document."""

	text: str = Field(..., description="Original document text")
	predictions: List[Prediction] = Field(default_factory=list)
	doc_id: Optional[str] = Field(default=None)
	model_name: Optional[str] = Field(default=None)

	def __init__(self, **data):
		super().__init__(**data)
		if self.doc_id is None:
			self.doc_id = f"doc_{abs(hash(self.text)) % 100000:05d}"
		for prediction in self.predictions:
			prediction.extract_text(self.text)

	def get_predictions_by_type(self, entity_type: str) -> List[Prediction]:
		return [p for p in self.predictions if p.entity_type == entity_type]

	def get_all_entity_types(self) -> List[str]:
		return sorted({p.entity_type for p in self.predictions})
