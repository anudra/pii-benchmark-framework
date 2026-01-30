import pytest
from backend.core.diff_generator import generate_diff_html


class TestDiffGeneration:
    def test_basic_diff(self):
        """Test basic diff generation"""
        original = "John Doe is here"
        redacted = "#### #### is here"
        ground_truth = []
        redaction_analysis = {"categories": {"correct": [], "leak": [], "over": [], "under": []}}
        diff_html = generate_diff_html(original, redacted, ground_truth, redaction_analysis)
        assert diff_html is not None
        assert len(diff_html) > 0

    def test_identical_texts(self):
        """Test diff with identical texts"""
        original = "John Doe"
        redacted = "John Doe"
        ground_truth = []
        redaction_analysis = {"categories": {"correct": [], "leak": [], "over": [], "under": []}}
        diff_html = generate_diff_html(original, redacted, ground_truth, redaction_analysis)
        assert diff_html is not None

    def test_complete_redaction(self):
        """Test diff with complete redaction"""
        original = "Sensitive data"
        redacted = "##############"
        ground_truth = []
        redaction_analysis = {"categories": {"correct": [], "leak": [], "over": [], "under": []}}
        diff_html = generate_diff_html(original, redacted, ground_truth, redaction_analysis)
        assert diff_html is not None
