from typing import List, Dict, Tuple, Any

def calculate_iou(span1: Tuple[int, int], span2: Tuple[int, int]) -> float:
    start1, end1 = span1
    start2, end2 = span2
    
    # Calculate intersection
    intersection_start = max(start1, start2)
    intersection_end = min(end1, end2)
    intersection = max(0, intersection_end - intersection_start)
    
    # Calculate union
    union_start = min(start1, start2)
    union_end = max(end1, end2)
    union = union_end - union_start
    
    if union == 0:
        return 0.0
    
    return intersection / union


def strict_match(gt_entity: Dict[str, Any], pred_entity: Dict[str, Any]) -> bool:
    """Exact position match"""
    return (gt_entity["start"] == pred_entity["start"] and 
            gt_entity["end"] == pred_entity["end"] and 
            gt_entity["entity_type"] == pred_entity["entity_type"])


def lenient_match(gt_entity: Dict[str, Any], pred_entity: Dict[str, Any], 
                 iou_threshold: float = 0.5) -> bool:
    """50%+ overlap match"""
    if gt_entity["entity_type"] != pred_entity["entity_type"]:
        return False
    
    iou = calculate_iou(
        (gt_entity["start"], gt_entity["end"]),
        (pred_entity["start"], pred_entity["end"])
    )
    
    return iou >= iou_threshold


def match_entities(ground_truth: List[Dict[str, Any]], 
                   predictions: List[Dict[str, Any]], 
                   mode: str = "strict") -> Dict[str, Any]:
    """Match predicted entities against ground truth"""
    
    matched_gt = set()
    matched_pred = set()
    true_positives = []
    false_positives = []
    false_negatives = []
    
    # Match each prediction against ground truth
    for pred_idx, pred in enumerate(predictions):
        match_found = False
        
        for gt_idx, gt in enumerate(ground_truth):
            if gt_idx in matched_gt:
                continue
            
            is_match = strict_match(gt, pred) if mode == "strict" else lenient_match(gt, pred)
            
            if is_match:
                matched_gt.add(gt_idx)
                matched_pred.add(pred_idx)
                true_positives.append({
                    "ground_truth": gt,
                    "prediction": pred,
                    "match_type": mode
                })
                match_found = True
                break
        
        if not match_found:
            false_positives.append(pred)
    
    # Identify false negatives (unmatched ground truth)
    for gt_idx, gt in enumerate(ground_truth):
        if gt_idx not in matched_gt:
            false_negatives.append(gt)
    
    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "total_gt": len(ground_truth),
        "total_pred": len(predictions)
    }

