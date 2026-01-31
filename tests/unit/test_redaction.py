import pytest
from backend.core.redaction_checker import check_redaction_status, check_over_redaction


class TestRedactionStatus:
    def test_perfect_redaction(self):
        """Test perfect redaction detection"""
        original = "John Doe"
        redacted = "#### ###"
        status = check_redaction_status(original, redacted, 0, 4)
        assert status == "correct"

    def test_leaked_entity(self):
        """Test leaked entity detection"""
        original = "John Doe"
        redacted = "John Doe"
        status = check_redaction_status(original, redacted, 0, 4)
        assert status == "leak"

    def test_partial_redaction(self):
        """Test partial redaction detection"""
        original = "John Doe"
        redacted = "Joh# Doe"
        status = check_redaction_status(original, redacted, 0, 4)
        assert status == "under"


class TestOverRedaction:
    def test_over_redaction_detection(self):
        """Test detection of over-redacted regions"""
        original = "John is 30 years old"
        redacted = "#### ## ## ##### ###"
        entities = [{"start": 0, "end": 4, "entity_type": "NAME"}]
        
        over_redacted = check_over_redaction(original, redacted, entities)
        assert isinstance(over_redacted, list)

    def test_no_over_redaction(self):
        """Test when there's no over-redaction"""
        original = "John is here"
        redacted = "#### is here"
        entities = [{"start": 0, "end": 4, "entity_type": "NAME"}]
        
        over_redacted = check_over_redaction(original, redacted, entities)
        assert len(over_redacted) == 0

    def test_empty_entities(self):
        """Test with empty entities list"""
        original = "John Doe"
        redacted = "#### ###"
        over_redacted = check_over_redaction(original, redacted, [])
        assert isinstance(over_redacted, list)
