from typing import Any, Dict
import re

def sanitize_text(text: str) -> str:
    return text.strip()

def format_timestamp(dt) -> str:
    return dt.strftime("%d %b %Y %H:%M:%S")

def calculate_percentage(value: float) -> str:
    return f"{value * 100:.2f}%"

def validate_entity_type(entity_type: str) -> bool:
    return bool(re.match(r'^[A-Z_]+$', entity_type))
