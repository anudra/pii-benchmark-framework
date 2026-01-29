from typing import Dict, List, Any, Tuple

def check_redaction_status(original: str, redacted: str, start: int, end: int) -> str:
    
    original_span = original[start:end]
    redacted_span = redacted[start:end]
    
    # Correct: fully redacted (all characters changed)
    if all(redacted_span[i] != original_span[i] for i in range(len(redacted_span))):
        return "correct"
    
    # Leak: not redacted at all
    if original_span == redacted_span:
        return "leak"
    
    # Partial redaction - under-redacted (some characters not changed)
    changed_chars = sum(1 for i in range(len(redacted_span)) if redacted_span[i] != original_span[i])
    total_chars = len(redacted_span)
    
    if 0 < changed_chars < total_chars:
        return "under"  # Partially redacted = under-redacted
    
    return "unknown"


def check_over_redaction(original: str, redacted: str, gt_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find over-redacted regions (non-sensitive data redacted)"""
    
    over_redactions = []
    
    # Create a set of protected positions
    protected = set()
    for entity in gt_entities:
        for pos in range(entity["start"], entity["end"]):
            protected.add(pos)
    
    # Find redacted regions outside protected areas
    i = 0
    while i < len(original):
        if i not in protected and original[i] != redacted[i]:
            # Found start of over-redaction
            start = i
            while i < len(original) and i not in protected and original[i] != redacted[i]:
                i += 1
            end = i
            
            over_redactions.append({
                "start": start,
                "end": end,
                "text": original[start:end],
                "redacted_as": redacted[start:end]
            })
        else:
            i += 1
    
    return over_redactions


def analyze_redaction(original_text: str, redacted_text: str, 
                     ground_truth: List[Dict[str, Any]],
                     match_results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze redaction quality"""
    
    redaction_analysis = {
        "correct": [],
        "leak": [],
        "over": [],
        "under": []
    }
    
    # Check true positives (correctly detected - check if redacted)
    for tp in match_results["true_positives"]:
        gt = tp["ground_truth"]
        status = check_redaction_status(original_text, redacted_text, gt["start"], gt["end"])
        
        redaction_analysis[status].append({
            "entity_type": gt["entity_type"],
            "start": gt["start"],
            "end": gt["end"],
            "text": gt.get("text", original_text[gt["start"]:gt["end"]]),
            "redacted_as": redacted_text[gt["start"]:gt["end"]]
        })
    
    # Check false negatives (missed detections - should be redacted but weren't)
    for fn in match_results["false_negatives"]:
        status = check_redaction_status(original_text, redacted_text, fn["start"], fn["end"])
        
        if status == "leak":
            redaction_analysis["leak"].append({
                "entity_type": fn["entity_type"],
                "start": fn["start"],
                "end": fn["end"],
                "text": fn.get("text", original_text[fn["start"]:fn["end"]]),
                "redacted_as": redacted_text[fn["start"]:fn["end"]]
            })
    
    # Check for over-redaction
    over_redactions = check_over_redaction(original_text, redacted_text, ground_truth)
    redaction_analysis["over"] = over_redactions
    
    # Calculate summary statistics
    total_entities = len(ground_truth)
    summary = {
        "total_entities": total_entities,
        "correct_redactions": len(redaction_analysis["correct"]),
        "leaks": len(redaction_analysis["leak"]),
        "over_redactions": len(redaction_analysis["over"]),
        "under_redactions": len(redaction_analysis["under"]),
        "redaction_quality_score": round(
            len(redaction_analysis["correct"]) / total_entities if total_entities > 0 else 0.0,
            4
        )
    }
    
    return {
        "categories": redaction_analysis,
        "summary": summary
    }

