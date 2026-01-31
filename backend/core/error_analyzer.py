from typing import Dict, List, Any

def analyze_errors(match_results: Dict[str, Any], redaction_analysis: Dict[str, Any], original_text: str = "") -> List[Dict[str, Any]]:
    
    errors = []
    
    # False Positives (incorrectly detected entities)
    for fp in match_results["false_positives"]:
        # Extract actual text from original_text using start/end positions
        extracted_text = ""
        if original_text and "start" in fp and "end" in fp:
            extracted_text = original_text[fp["start"]:fp["end"]]
        else:
            extracted_text = fp.get("text", "")
        
        errors.append({
            "error_type": "FP",
            "entity_type": fp["entity_type"],
            "position_start": fp["start"],
            "position_end": fp["end"],
            "text": extracted_text,
            "description": f"FP in '{extracted_text}': Incorrectly detected as {fp['entity_type']} (Position: {fp['start']}-{fp['end']})"
        })
    
    # False Negatives (missed entities)
    for fn in match_results["false_negatives"]:
        # Extract actual text from original_text using start/end positions
        extracted_text = ""
        if original_text and "start" in fn and "end" in fn:
            extracted_text = original_text[fn["start"]:fn["end"]]
        else:
            extracted_text = fn.get("text", "")
        
        errors.append({
            "error_type": "FN",
            "entity_type": fn["entity_type"],
            "position_start": fn["start"],
            "position_end": fn["end"],
            "text": extracted_text,
            "description": f"FN: {fn['entity_type']} '{extracted_text}' was not detected (Position: {fn['start']}-{fn['end']})"
        })
    
    # Redaction Leaks
    for leak in redaction_analysis["categories"]["leak"]:
        errors.append({
            "error_type": "LEAK",
            "entity_type": leak["entity_type"],
            "position_start": leak["start"],
            "position_end": leak["end"],
            "text": leak["text"],
            "description": f"LEAK: {leak['entity_type']} '{leak['text']}' was not redacted (Position: {leak['start']}-{leak['end']})"
        })
    
    # Over-redactions
    for over in redaction_analysis["categories"]["over"]:
        errors.append({
            "error_type": "OVER",
            "entity_type": "N/A",
            "position_start": over["start"],
            "position_end": over["end"],
            "text": over["text"],
            "description": f"OVER: Non-sensitive text '{over['text']}' was over-redacted as '{over['redacted_as']}'"
        })
    
    # Under-redactions
    for under in redaction_analysis["categories"]["under"]:
        errors.append({
            "error_type": "UNDER",
            "entity_type": under["entity_type"],
            "position_start": under["start"],
            "position_end": under["end"],
            "text": under["text"],
            "description": f"UNDER: {under['entity_type']} '{under['text']}' was under-redacted as '{under['redacted_as']}' (SECURITY RISK!)"
        })
    
    return errors

