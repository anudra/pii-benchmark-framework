import pytest
from backend.core.matcher import calculate_iou, strict_match, lenient_match, match_entities


class TestIOU:
    def test_perfect_overlap(self):
        """Test IOU with perfect overlap"""
        iou = calculate_iou((0, 10), (0, 10))
        assert iou == 1.0

    def test_no_overlap(self):
        """Test IOU with no overlap"""
        iou = calculate_iou((0, 5), (10, 15))
        assert iou == 0.0

    def test_partial_overlap(self):
        """Test IOU with 50% overlap"""
        iou = calculate_iou((0, 10), (5, 15))
        assert iou == pytest.approx(0.333, abs=0.01)


class TestStrictMatch:
    def test_exact_match(self):
        """Test exact position and type match"""
        gt = {"start": 0, "end": 5, "entity_type": "NAME"}
        pred = {"start": 0, "end": 5, "entity_type": "NAME"}
        assert strict_match(gt, pred) is True

    def test_position_mismatch(self):
        """Test position mismatch"""
        gt = {"start": 0, "end": 5, "entity_type": "NAME"}
        pred = {"start": 1, "end": 5, "entity_type": "NAME"}
        assert strict_match(gt, pred) is False

    def test_type_mismatch(self):
        """Test type mismatch"""
        gt = {"start": 0, "end": 5, "entity_type": "NAME"}
        pred = {"start": 0, "end": 5, "entity_type": "EMAIL"}
        assert strict_match(gt, pred) is False


class TestLenientMatch:
    def test_lenient_with_overlap(self):
        """Test lenient match with sufficient overlap"""
        gt = {"start": 0, "end": 10, "entity_type": "NAME"}
        pred = {"start": 5, "end": 15, "entity_type": "NAME"}
        assert lenient_match(gt, pred, iou_threshold=0.25) is True

    def test_lenient_no_overlap(self):
        """Test lenient match with no overlap"""
        gt = {"start": 0, "end": 5, "entity_type": "NAME"}
        pred = {"start": 10, "end": 15, "entity_type": "NAME"}
        assert lenient_match(gt, pred) is False

    def test_lenient_type_mismatch(self):
        """Test lenient with type mismatch"""
        gt = {"start": 0, "end": 10, "entity_type": "NAME"}
        pred = {"start": 5, "end": 15, "entity_type": "EMAIL"}
        assert lenient_match(gt, pred) is False


class TestMatchEntities:
    def test_strict_mode_perfect_match(self):
        """Test strict matching with perfect overlap"""
        gt = [{"start": 0, "end": 5, "entity_type": "NAME"}]
        pred = [{"start": 0, "end": 5, "entity_type": "NAME"}]
        result = match_entities(gt, pred, mode="strict")
        assert len(result["true_positives"]) == 1
        assert len(result["false_positives"]) == 0
        assert len(result["false_negatives"]) == 0

    def test_strict_mode_no_match(self):
        """Test strict matching with no match"""
        gt = [{"start": 0, "end": 5, "entity_type": "NAME"}]
        pred = [{"start": 1, "end": 5, "entity_type": "NAME"}]
        result = match_entities(gt, pred, mode="strict")
        assert len(result["true_positives"]) == 0
        assert len(result["false_positives"]) == 1
        assert len(result["false_negatives"]) == 1

    def test_empty_lists(self):
        """Test with empty ground truth and predictions"""
        result = match_entities([], [], mode="strict")
        assert len(result["true_positives"]) == 0
        assert len(result["false_positives"]) == 0
        assert len(result["false_negatives"]) == 0
