# Common helper functions
# Utility functions used across the application

from typing import Any, Dict
import re


def sanitize_text(text: str) -> str:
    """Sanitize text for display"""
    return text.strip()


def format_timestamp(dt) -> str:
    """Format datetime for display"""
    return dt.strftime("%d %b %Y %H:%M:%S")


def calculate_percentage(value: float) -> str:
    """Convert decimal to percentage string"""
    return f"{value * 100:.2f}%"


def validate_entity_type(entity_type: str) -> bool:
    """Validate entity type format"""
    return bool(re.match(r'^[A-Z_]+$', entity_type))
