"""Basic input validation helpers."""
from __future__ import annotations

from typing import List, Dict


def _is_list_of_dicts(data) -> bool:
	return isinstance(data, list) and all(isinstance(item, dict) for item in data)


def validate_ground_truth(data) -> List[Dict]:
	if not _is_list_of_dicts(data):
		raise ValueError("Ground truth must be a list of objects")
	for item in data:
		if "text" not in item or "entities" not in item:
			raise ValueError("Each ground truth item must include 'text' and 'entities'")
	return data


def validate_predictions(data) -> List[Dict]:
	if not _is_list_of_dicts(data):
		raise ValueError("Predictions must be a list of objects")
	for item in data:
		if "text" not in item:
			raise ValueError("Each prediction item must include 'text'")
		if "predictions" not in item and "detected_entities" not in item:
			raise ValueError("Each prediction item must include 'predictions' or 'detected_entities'")
	return data


def validate_redacted(data) -> List[Dict]:
	if not _is_list_of_dicts(data):
		raise ValueError("Redacted docs must be a list of objects")
	for item in data:
		if "text" not in item or "redacted_text" not in item:
			raise ValueError("Each redacted item must include 'text' and 'redacted_text'")
	return data
