from typing import Dict, List, Any
from collections import defaultdict

def calculate_metrics(match_results: Dict[str, Any], text_length: int) -> Dict[str, Any]:
    
    tp = len(match_results["true_positives"])
    fp = len(match_results["false_positives"])
    fn = len(match_results["false_negatives"])
    
    # True negatives: non-entity characters correctly not flagged
    # This is an approximation based on text length and entity coverage
    gt_coverage = sum(gt["end"] - gt["start"] 
                      for tp_item in match_results["true_positives"] 
                      for gt in [tp_item["ground_truth"]])
    fp_coverage = sum(fp_item["end"] - fp_item["start"] 
                      for fp_item in match_results["false_positives"])
    
    tn = text_length - gt_coverage - fp_coverage
    tn = max(0, tn)  # Ensure non-negative
    
    # Calculate metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0.0
    
    # Confusion matrix
    confusion_matrix = {
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn
    }
    
    # Per-entity type metrics
    per_entity = calculate_per_entity_metrics(match_results)
    
    return {
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1_score, 4),
        "accuracy": round(accuracy, 4),
        "confusion_matrix": confusion_matrix,
        "per_entity_metrics": per_entity
    }


def calculate_per_entity_metrics(match_results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Calculate metrics per entity type"""
    
    entity_stats = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    
    # Count TPs by entity type
    for tp in match_results["true_positives"]:
        entity_type = tp["ground_truth"]["entity_type"]
        entity_stats[entity_type]["tp"] += 1
    
    # Count FPs by entity type
    for fp in match_results["false_positives"]:
        entity_type = fp["entity_type"]
        entity_stats[entity_type]["fp"] += 1
    
    # Count FNs by entity type
    for fn in match_results["false_negatives"]:
        entity_type = fn["entity_type"]
        entity_stats[entity_type]["fn"] += 1
    
    # Calculate metrics for each entity type
    per_entity_metrics = {}
    for entity_type, stats in entity_stats.items():
        tp = stats["tp"]
        fp = stats["fp"]
        fn = stats["fn"]
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        per_entity_metrics[entity_type] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "tp": tp,
            "fp": fp,
            "fn": fn
        }
    
    return per_entity_metrics

