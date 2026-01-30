import pytest
from backend.core.validator import validate_ground_truth, validate_predictions


class TestGroundTruthValidation:
    def test_valid_ground_truth(self):
        """Test valid ground truth format"""
        gt = {
            "entities": [
                {"start": 0, "end": 5, "entity_type": "NAME"}
            ],
            "text": "John Doe"
        }
        is_valid, msg = validate_ground_truth(gt)
        assert is_valid is True

    def test_missing_text(self):
        """Test ground truth missing text field"""
        gt = {"entities": []}
        is_valid, msg = validate_ground_truth(gt)
        assert is_valid is False
        assert "text" in msg

    def test_invalid_entity_format(self):
        """Test ground truth with invalid entity format"""
        gt = {
            "entities": [{"start": 0, "end": 5}],
            "text": "John Doe"
        }
        is_valid, msg = validate_ground_truth(gt)
        assert is_valid is False


class TestPredictionsValidation:
    def test_valid_predictions(self):
        """Test valid predictions format"""
        pred = {
            "predictions": [
                {"start": 0, "end": 5, "entity_type": "NAME"}
            ]
        }
        is_valid, msg = validate_predictions(pred)
        assert is_valid is True

    def test_missing_predictions_field(self):
        """Test predictions with missing field"""
        pred = {}
        is_valid, msg = validate_predictions(pred)
        assert is_valid is False

    def test_empty_predictions(self):
        """Test predictions with empty list"""
        pred = {"predictions": []}
        is_valid, msg = validate_predictions(pred)
        assert is_valid is True
