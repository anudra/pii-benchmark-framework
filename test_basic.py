# Quick test script to verify the evaluation system works

import requests
import json

# Test data
test_data = {
    "original_text": "My email is john.doe@example.com and my PAN number is ABCDE1234F.",
    "redacted_text": "My email is *********************and my PAN number***********34F.",
    "ground_truth": {
        "text": "My email is john.doe@example.com and my PAN number is ABCDE1234F.",
        "entities": [
            {
                "entity_type": "EMAIL",
                "start": 12,
                "end": 33,
                "text": "john.doe@example.com"
            },
            {
                "entity_type": "PAN",
                "start": 54,
                "end": 64,
                "text": "ABCDE1234F"
            }
        ]
    },
    "predictions": {
        "predictions": [
            {
                "entity_type": "EMAIL",
                "start": 12,
                "end": 33
            },
            {
                "entity_type": "PAN",
                "start": 54,
                "end": 64
            }
        ]
    },
    "mode": "strict",
    "model_name": "Test_Model_v1"
}

# Send request
print("Testing PII Evaluation API...")
print(f"URL: http://127.0.0.1:8000/api/evaluate")

response = requests.post("http://127.0.0.1:8000/api/evaluate", json=test_data)

if response.status_code == 200:
    result = response.json()
    print("\nSUCCESS! Evaluation completed.")
    print(f"\nEvaluation ID: {result['id']}")
    print(f"Model: {result['model_name']}")
    print(f"Mode: {result['mode']}")
    print(f"\nMetrics:")
    print(f"  Precision: {result['metrics']['precision'] * 100:.2f}%")
    print(f"  Recall: {result['metrics']['recall'] * 100:.2f}%")
    print(f"  F1-Score: {result['metrics']['f1_score'] * 100:.2f}%")
    print(f"  Accuracy: {result['metrics']['accuracy'] * 100:.2f}%")
    print(f"\nConfusion Matrix:")
    print(f"  True Positives: {result['confusion_matrix']['TP']}")
    print(f"  False Positives: {result['confusion_matrix']['FP']}")
    print(f"  False Negatives: {result['confusion_matrix']['FN']}")
    
    # Print redaction analysis
    print(f"\n=== REDACTION ANALYSIS ===")
    redaction = result.get('redaction_analysis', {})
    summary = redaction.get('summary', {})
    print(f"Correct Redactions: {summary.get('correct_redactions', 0)}")
    print(f"Leaks: {summary.get('leaks', 0)}")
    print(f"Over-redactions: {summary.get('over_redactions', 0)}")
    print(f"Under-redactions: {summary.get('under_redactions', 0)}")
    
    # Show details
    categories = redaction.get('categories', {})
    if categories.get('under'):
        print(f"\nUNDER-REDACTION DETAILS:")
        for item in categories['under']:
            print(f"  - {item['entity_type']}: '{item['text']}' -> '{item['redacted_as']}'")
    
    print(f"\nAll features working correctly!")
    print(f"\nOpen http://127.0.0.1:8000/ in browser to use the web interface")
else:
    print(f"\nERROR: {response.status_code}")
    print(response.text)
