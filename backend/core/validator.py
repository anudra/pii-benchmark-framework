from typing import Dict, Any, List, Tuple

def validate_text_file(content: str) -> Tuple[bool, str]:
    if not content or not content.strip():
        return False, "Text file is empty"
    return True, "Valid"


def validate_ground_truth(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate ground truth JSON format"""
    if "text" not in data:
        return False, "Missing 'text' field in ground truth"
    if "entities" not in data:
        return False, "Missing 'entities' field in ground truth"
    
    if not isinstance(data["entities"], list):
        return False, "'entities' must be a list"
    
    for idx, entity in enumerate(data["entities"]):
        if not all(k in entity for k in ["entity_type", "start", "end"]):
            return False, f"Entity {idx} missing required fields"
        
        if not isinstance(entity["start"], int) or not isinstance(entity["end"], int):
            return False, f"Entity {idx} start/end must be integers"
        
        if entity["start"] >= entity["end"]:
            return False, f"Entity {idx} start must be less than end"
        
        if entity["start"] < 0 or entity["end"] > len(data["text"]):
            return False, f"Entity {idx} positions out of text bounds"
    
    return True, "Valid"


def validate_predictions(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate predictions JSON format"""
    if "predictions" not in data:
        return False, "Missing 'predictions' field"
    
    if not isinstance(data["predictions"], list):
        return False, "'predictions' must be a list"
    
    for idx, pred in enumerate(data["predictions"]):
        if not all(k in pred for k in ["entity_type", "start", "end"]):
            return False, f"Prediction {idx} missing required fields"
        
        if not isinstance(pred["start"], int) or not isinstance(pred["end"], int):
            return False, f"Prediction {idx} start/end must be integers"
        
        if pred["start"] >= pred["end"]:
            return False, f"Prediction {idx} start must be less than end"
    
    return True, "Valid"


def validate_mode(mode: str) -> Tuple[bool, str]:
    """Validate evaluation mode"""
    if mode not in ["strict", "lenient"]:
        return False, "Mode must be 'strict' or 'lenient'"
    return True, "Valid"


def validate_all_inputs(original_text: str, redacted_text: str, 
                       ground_truth: Dict[str, Any], predictions: Dict[str, Any],
                       mode: str) -> Tuple[bool, str]:
    """Validate all inputs"""
    
    # Validate original text
    valid, msg = validate_text_file(original_text)
    if not valid:
        return False, f"Original text: {msg}"
    
    # Validate redacted text
    valid, msg = validate_text_file(redacted_text)
    if not valid:
        return False, f"Redacted text: {msg}"
    
    # Validate ground truth
    valid, msg = validate_ground_truth(ground_truth)
    if not valid:
        return False, f"Ground truth: {msg}"
    
    # Validate predictions
    valid, msg = validate_predictions(predictions)
    if not valid:
        return False, f"Predictions: {msg}"
    
    # Validate mode
    valid, msg = validate_mode(mode)
    if not valid:
        return False, msg
    
    # Validate text lengths match
    if len(original_text) != len(redacted_text):
        return False, "Original and redacted text lengths must match"
    
    return True, "All inputs valid"

