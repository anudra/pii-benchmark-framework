"""Ground truth schemas."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class Entity(BaseModel):
	"""Represents a labeled sensitive entity in the document."""

	entity_type: str = Field(..., description="Entity type (EMAIL, PAN, PHONE, etc.)")
	start: int = Field(..., ge=0, description="Start character index (inclusive)")
	end: int = Field(..., gt=0, description="End character index (exclusive)")
	text: Optional[str] = Field(default=None, description="Optional text span")

	def extract_text(self, document_text: str) -> None:
		if self.text is None and self.start < len(document_text):
			self.text = document_text[self.start:self.end]


class GroundTruth(BaseModel):
	"""Ground truth for a document."""

	text: str = Field(..., description="Original document text")
	entities: List[Entity] = Field(default_factory=list, description="Labeled entities")
	doc_id: Optional[str] = Field(default=None, description="Optional document id")

	def __init__(self, **data):
		super().__init__(**data)
		if self.doc_id is None:
			self.doc_id = f"doc_{abs(hash(self.text)) % 100000:05d}"
		for entity in self.entities:
			entity.extract_text(self.text)

	def get_entities_by_type(self, entity_type: str) -> List[Entity]:
		return [e for e in self.entities if e.entity_type == entity_type]

	def get_all_entity_types(self) -> List[str]:
		return sorted({e.entity_type for e in self.entities})
