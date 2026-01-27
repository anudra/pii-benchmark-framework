# Pydantic models for API request/response validation
# Defines schemas for input validation and output serialization

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Entity(BaseModel):
    entity_type: str
    start: int
    end: int
    text: Optional[str] = None


class GroundTruth(BaseModel):
    text: str
    entities: List[Entity]


class Predictions(BaseModel):
    predictions: List[Entity]


class EvaluationRequest(BaseModel):
    original_text: str
    redacted_text: str
    ground_truth: Dict[str, Any]
    predictions: Dict[str, Any]
    mode: str = Field(default="strict", pattern="^(strict|lenient)$")
    model_name: Optional[str] = "Default"


class MetricsResponse(BaseModel):
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    accuracy: float


class EvaluationResponse(BaseModel):
    id: int
    timestamp: datetime
    model_name: str
    mode: str
    metrics: MetricsResponse
    confusion_matrix: Dict[str, Any]
    per_entity_metrics: Dict[str, Any]
    redaction_analysis: Dict[str, Any]
    diff_html: str
    errors: List[Dict[str, Any]]


class HistoryItem(BaseModel):
    id: int
    timestamp: datetime
    model_name: str
    mode: str
    accuracy: float
    redaction_analysis: Optional[Dict[str, Any]] = None


class ComparisonResponse(BaseModel):
    evaluation1: EvaluationResponse
    evaluation2: EvaluationResponse
    differences: Dict[str, Any]
