import pytest
from backend.core.matcher import match_entities
from backend.core.metrics import calculate_metrics, calculate_per_entity_metrics


class TestMetricsCalculation:
    def test_perfect_detection(self):
        """Test metrics with perfect detection"""
        gt = [{"start": 0, "end": 5, "entity_type": "NAME"}]
        pred = [{"start": 0, "end": 5, "entity_type": "NAME"}]
        match_result = match_entities(gt, pred, mode="strict")
        metrics = calculate_metrics(match_result, len("John Doe"))
        
        assert metrics["precision"] == 1.0
        assert metrics["recall"] == 1.0
        assert metrics["f1_score"] == 1.0

    def test_partial_detection(self):
        """Test metrics with partial detection"""
        gt = [
            {"start": 0, "end": 5, "entity_type": "NAME"},
            {"start": 10, "end": 20, "entity_type": "EMAIL"}
        ]
        pred = [{"start": 0, "end": 5, "entity_type": "NAME"}]
        match_result = match_entities(gt, pred, mode="strict")
        metrics = calculate_metrics(match_result, 20)
        
        assert metrics["precision"] >= 0
        assert metrics["recall"] >= 0

    def test_no_detection(self):
        """Test metrics with no correct detection"""
        gt = [{"start": 0, "end": 5, "entity_type": "NAME"}]
        pred = []
        match_result = match_entities(gt, pred, mode="strict")
        metrics = calculate_metrics(match_result, 10)
        
        assert metrics["precision"] == 0.0
        assert metrics["recall"] == 0.0
        assert metrics["f1_score"] == 0.0


class TestPerEntityMetrics:
    def test_per_entity_calculation(self):
        """Test per entity metrics calculation"""
        gt = [
            {"start": 0, "end": 5, "entity_type": "NAME"},
            {"start": 10, "end": 20, "entity_type": "EMAIL"}
        ]
        pred = [
            {"start": 0, "end": 5, "entity_type": "NAME"},
            {"start": 10, "end": 20, "entity_type": "EMAIL"}
        ]
        match_result = match_entities(gt, pred, mode="strict")
        metrics = calculate_per_entity_metrics(match_result)
        
        assert "NAME" in metrics
        assert "EMAIL" in metrics
        assert metrics["NAME"]["tp"] == 1
        assert metrics["EMAIL"]["tp"] == 1

    def test_empty_predictions(self):
        """Test with empty predictions"""
        gt = [{"start": 0, "end": 5, "entity_type": "NAME"}]
        match_result = match_entities(gt, [], mode="strict")
        metrics = calculate_per_entity_metrics(match_result)
        
        assert "NAME" in metrics
        assert metrics["NAME"]["fn"] == 1
        assert metrics["NAME"]["tp"] == 0
