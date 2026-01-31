import pytest
from backend.core.error_analyzer import analyze_errors


class TestErrorAnalysis:
    def test_analyze_errors_false_positives(self):
        """Test error analysis with false positives"""
        match_results = {
            "false_positives": [
                {
                    "entity_type": "NAME",
                    "start": 0,
                    "end": 5,
                    "text": "John"
                }
            ],
            "false_negatives": [],
            "true_positives": [],
            "true_negatives": []
        }
        redaction_analysis = {"categories": {"correct": [], "leak": [], "over": [], "under": []}}
        errors = analyze_errors(match_results, redaction_analysis, "John is here")
        assert len(errors) > 0
        assert errors[0]["error_type"] == "FP"

    def test_analyze_errors_false_negatives(self):
        """Test error analysis with false negatives"""
        match_results = {
            "false_positives": [],
            "false_negatives": [
                {
                    "entity_type": "PHONE",
                    "start": 10,
                    "end": 22,
                    "text": "555-123-4567"
                }
            ],
            "true_positives": [],
            "true_negatives": []
        }
        redaction_analysis = {"categories": {"correct": [], "leak": [], "over": [], "under": []}}
        errors = analyze_errors(match_results, redaction_analysis, "Call me 555-123-4567")
        assert len(errors) > 0
        assert errors[0]["error_type"] == "FN"

    def test_empty_errors(self):
        """Test with no errors"""
        match_results = {
            "false_positives": [],
            "false_negatives": [],
            "true_positives": [],
            "true_negatives": []
        }
        redaction_analysis = {"categories": {"correct": [], "leak": [], "over": [], "under": []}}
        errors = analyze_errors(match_results, redaction_analysis, "")
        assert len(errors) == 0
