"""UI helper utilities."""
from __future__ import annotations

import json
from typing import Any

from models.results import EvaluationResult


def load_json_file(uploaded_file) -> Any:
	if uploaded_file is None:
		return None
	return json.loads(uploaded_file.getvalue().decode("utf-8"))


def export_results_json(results: EvaluationResult) -> str:
	payload = results.model_dump() if hasattr(results, "model_dump") else results.dict()
	return json.dumps(payload, indent=2, default=str)
