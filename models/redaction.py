"""Redaction schemas."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class RedactedSpan(BaseModel):
	"""Represents a redacted span in output."""

	start: int = Field(..., ge=0)
	end: int = Field(..., gt=0)
	entity_type: Optional[str] = Field(default=None)
	redaction_text: str = Field(default="[REDACTED]")


class RedactedDocument(BaseModel):
	"""Document after redaction."""

	text: str = Field(..., description="Original document text")
	redacted_text: str = Field(..., description="Text after redaction")
	redacted_spans: List[RedactedSpan] = Field(default_factory=list)
	doc_id: Optional[str] = Field(default=None)

	def __init__(self, **data):
		super().__init__(**data)
		if self.doc_id is None:
			self.doc_id = f"doc_{abs(hash(self.text)) % 100000:05d}"


class RedactionErrorType:
	MISSED_REDACTION = "missed_redaction"
	PARTIAL_REDACTION = "partial_redaction"
	OVER_REDACTION = "over_redaction"
	INCORRECT_SPAN = "incorrect_span"


class RedactionError(BaseModel):
	"""Details about a redaction error."""

	doc_id: str
	error_type: str
	entity_type: str
	start: int
	end: int
	expected_text: str
	actual_text: str
	severity: str = Field(default="high")

	def __str__(self) -> str:
		return (
			f"[{self.doc_id}] {self.error_type}: {self.entity_type} "
			f"({self.start}-{self.end}) expected='{self.expected_text}' got='{self.actual_text}'"
		)
