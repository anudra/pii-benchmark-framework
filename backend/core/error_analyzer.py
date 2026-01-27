from typing import Dict, List, Any

def analyze_errors(match_results: Dict[str, Any], redaction_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    
    errors = []
    
    # False Positives (incorrectly detected entities)
    for fp in match_results["false_positives"]:
        errors.append({
            "error_type": "FP",
            "entity_type": fp["entity_type"],
            "position_start": fp["start"],
            "position_end": fp["end"],
            "text": fp.get("text", ""),
            "description": f"False positive: '{fp.get('text', '')}' incorrectly detected as {fp['entity_type']}"
        })
    
    # False Negatives (missed entities)
    for fn in match_results["false_negatives"]:
        errors.append({
            "error_type": "FN",
            "entity_type": fn["entity_type"],
            "position_start": fn["start"],
            "position_end": fn["end"],
            "text": fn.get("text", ""),
            "description": f"False negative: {fn['entity_type']} '{fn.get('text', '')}' was not detected"
        })
    
    # Redaction Leaks
    for leak in redaction_analysis["categories"]["leak"]:
        errors.append({
            "error_type": "LEAK",
            "entity_type": leak["entity_type"],
            "position_start": leak["start"],
            "position_end": leak["end"],
            "text": leak["text"],
            "description": f"Redaction leak: {leak['entity_type']} '{leak['text']}' was not redacted"
        })
    
    # Over-redactions
    for over in redaction_analysis["categories"]["over"]:
        errors.append({
            "error_type": "OVER",
            "entity_type": "N/A",
            "position_start": over["start"],
            "position_end": over["end"],
            "text": over["text"],
            "description": f"Over-redaction: Non-sensitive text '{over['text']}' was redacted as '{over['redacted_as']}'"
        })
    
    # Under-redactions
    for under in redaction_analysis["categories"]["under"]:
        errors.append({
            "error_type": "UNDER",
            "entity_type": under["entity_type"],
            "position_start": under["start"],
            "position_end": under["end"],
            "text": under["text"],
            "description": f"Under-redaction: {under['entity_type']} '{under['text']}' partially redacted as '{under['redacted_as']}'"
        })
    
    # Semi-redactions
    for semi in redaction_analysis["categories"]["semi"]:
        errors.append({
            "error_type": "SEMI",
            "entity_type": semi["entity_type"],
            "position_start": semi["start"],
            "position_end": semi["end"],
            "text": semi["text"],
            "description": f"Semi-redaction: {semi['entity_type']} '{semi['text']}' partially visible as '{semi['redacted_as']}'"
        })
    
    return errors

