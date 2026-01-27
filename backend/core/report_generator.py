# Report generation for exports
# Generates JSON and PDF export reports
# Includes all metrics, charts, and error analysis

import json
from typing import Dict, Any
from datetime import datetime


def generate_json_report(evaluation_data: Dict[str, Any]) -> str:
    """Generate JSON export report with separate Detection and Redaction sections"""
    
    # Extract redaction summary if available
    redaction_analysis = evaluation_data.get("redaction_analysis", {})
    redaction_summary = redaction_analysis.get("summary", {}) if isinstance(redaction_analysis, dict) else {}
    
    report = {
        "evaluation_id": evaluation_data.get("id"),
        "timestamp": evaluation_data.get("timestamp", datetime.utcnow()).isoformat(),
        "model_name": evaluation_data.get("model_name", "Default"),
        "mode": evaluation_data.get("mode", "strict"),
        
        # Entity Detection Evaluation
        "entity_detection": {
            "description": "Measures how accurately the model identifies PII entity positions",
            "metrics": {
                "precision": evaluation_data.get("metrics", {}).get("precision", 0),
                "recall": evaluation_data.get("metrics", {}).get("recall", 0),
                "f1_score": evaluation_data.get("metrics", {}).get("f1_score", 0),
                "accuracy": evaluation_data.get("metrics", {}).get("accuracy", 0)
            },
            "confusion_matrix": evaluation_data.get("confusion_matrix", {}),
            "per_entity_metrics": evaluation_data.get("per_entity_metrics", {})
        },
        
        # Redaction Quality Evaluation
        "redaction_quality": {
            "description": "Measures how well detected PII entities were actually redacted",
            "summary": {
                "total_entities": redaction_summary.get("total_entities", 0),
                "correct_redactions": redaction_summary.get("correct_redactions", 0),
                "leaks": redaction_summary.get("leaks", 0),
                "over_redactions": redaction_summary.get("over_redactions", 0),
                "under_redactions": redaction_summary.get("under_redactions", 0),
                "semi_redactions": redaction_summary.get("semi_redactions", 0),
                "redaction_quality_score": redaction_summary.get("redaction_quality_score", 0)
            },
            "detailed_analysis": redaction_analysis.get("categories", {})
        },
        
        # Errors
        "errors": evaluation_data.get("errors", [])
    }
    
    return json.dumps(report, indent=2)


def generate_pdf_report(evaluation_data: Dict[str, Any]) -> bytes:
    """Generate PDF export report with separate Detection and Redaction sections"""
    
    # Extract redaction summary
    redaction_analysis = evaluation_data.get("redaction_analysis", {})
    redaction_summary = redaction_analysis.get("summary", {}) if isinstance(redaction_analysis, dict) else {}
    
    # Calculate percentages
    metrics = evaluation_data.get('metrics', {})
    precision = metrics.get('precision', 0) * 100
    recall = metrics.get('recall', 0) * 100
    f1_score = metrics.get('f1_score', 0) * 100
    accuracy = metrics.get('accuracy', 0) * 100
    
    # Redaction metrics
    total_entities = redaction_summary.get("total_entities", 0)
    correct = redaction_summary.get("correct_redactions", 0)
    leaks = redaction_summary.get("leaks", 0)
    over = redaction_summary.get("over_redactions", 0)
    under = redaction_summary.get("under_redactions", 0)
    semi = redaction_summary.get("semi_redactions", 0)
    
    redaction_accuracy = (correct / total_entities * 100) if total_entities > 0 else 0
    leak_rate = (leaks / total_entities * 100) if total_entities > 0 else 0
    
    # For MVP, return HTML that can be converted to PDF
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
            h2 {{ color: #2c3e50; margin-top: 30px; padding-bottom: 5px; }}
            h2.detection {{ border-bottom: 3px solid #4CAF50; }}
            h2.redaction {{ border-bottom: 3px solid #FF9800; }}
            .section {{ background-color: #fafafa; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e0e0e0; }}
            .description {{ color: #666; font-style: italic; margin-bottom: 15px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            .metric-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 15px; margin: 20px 0; }}
            .metric-card {{ background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border: 2px solid #e9ecef; }}
            .metric-card h3 {{ margin: 0; font-size: 14px; color: #666; }}
            .metric-value {{ font-size: 28px; font-weight: bold; color: #4CAF50; margin: 10px 0; }}
            .correct {{ background-color: #e8f5e9; }}
            .leak {{ background-color: #ffebee; }}
            .warning {{ background-color: #fff3e0; }}
            .metadata {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h1>PII Evaluation Report</h1>
        
        <div class="metadata">
            <p><strong>Evaluation ID:</strong> {evaluation_data.get('id', 'N/A')}</p>
            <p><strong>Model:</strong> {evaluation_data.get('model_name', 'Default')}</p>
            <p><strong>Mode:</strong> {evaluation_data.get('mode', 'strict')}</p>
            <p><strong>Timestamp:</strong> {evaluation_data.get('timestamp', 'N/A')}</p>
        </div>
        
        <div class="section">
            <h2 class="detection">Entity Detection Evaluation</h2>
            <p class="description">Measures how accurately the model identifies PII entity positions</p>
            
            <div class="metric-grid">
                <div class="metric-card">
                    <h3>Precision</h3>
                    <div class="metric-value">{precision:.2f}%</div>
                    <p style="font-size: 12px; color: #888;">Correctness of predictions</p>
                </div>
                <div class="metric-card">
                    <h3>Recall</h3>
                    <div class="metric-value">{recall:.2f}%</div>
                    <p style="font-size: 12px; color: #888;">Coverage of actual PII</p>
                </div>
                <div class="metric-card">
                    <h3>F1-Score</h3>
                    <div class="metric-value">{f1_score:.2f}%</div>
                    <p style="font-size: 12px; color: #888;">Harmonic mean</p>
                </div>
                <div class="metric-card">
                    <h3>Accuracy</h3>
                    <div class="metric-value">{accuracy:.2f}%</div>
                    <p style="font-size: 12px; color: #888;">Overall correctness</p>
                </div>
            </div>
            
            <h3>Detection Confusion Matrix</h3>
            <div style="display: inline-block; border: 2px solid #333; margin: 1rem 0;">
                <table style="border-collapse: collapse; text-align: center;">
                    <tr>
                        <td colspan="2" rowspan="2" style="border: none;"></td>
                        <th colspan="2" style="padding: 0.5rem; border-bottom: 2px solid #333;">Predicted</th>
                    </tr>
                    <tr>
                        <th style="padding: 0.5rem; border-bottom: 2px solid #333; border-left: 2px solid #333;">Positive</th>
                        <th style="padding: 0.5rem; border-bottom: 2px solid #333; border-left: 1px solid #ddd;">Negative</th>
                    </tr>
                    <tr>
                        <th rowspan="2" style="padding: 0.5rem; border-right: 2px solid #333; writing-mode: vertical-lr; transform: rotate(180deg);">Actual</th>
                        <th style="padding: 0.5rem; border-right: 2px solid #333; border-bottom: 1px solid #ddd;">Positive</th>
                        <td style="padding: 1rem 2rem; background: #c8e6c9; font-weight: bold; font-size: 1.2rem; border-left: 2px solid #333; border-bottom: 1px solid #ddd;">
                            <div style="font-size: 0.8rem; color: #2e7d32; margin-bottom: 0.25rem;">TP</div>
                            <div>{evaluation_data.get('confusion_matrix', {}).get('TP', 0)}</div>
                        </td>
                        <td style="padding: 1rem 2rem; background: #ffccbc; font-weight: bold; font-size: 1.2rem; border-left: 1px solid #ddd; border-bottom: 1px solid #ddd;">
                            <div style="font-size: 0.8rem; color: #c62828; margin-bottom: 0.25rem;">FN</div>
                            <div>{evaluation_data.get('confusion_matrix', {}).get('FN', 0)}</div>
                        </td>
                    </tr>
                    <tr>
                        <th style="padding: 0.5rem; border-right: 2px solid #333;">Negative</th>
                        <td style="padding: 1rem 2rem; background: #ffccbc; font-weight: bold; font-size: 1.2rem; border-left: 2px solid #333;">
                            <div style="font-size: 0.8rem; color: #c62828; margin-bottom: 0.25rem;">FP</div>
                            <div>{evaluation_data.get('confusion_matrix', {}).get('FP', 0)}</div>
                        </td>
                        <td style="padding: 1rem 2rem; background: #c8e6c9; font-weight: bold; font-size: 1.2rem; border-left: 1px solid #ddd;">
                            <div style="font-size: 0.8rem; color: #2e7d32; margin-bottom: 0.25rem;">TN</div>
                            <div>{evaluation_data.get('confusion_matrix', {}).get('TN', 0)}</div>
                        </td>
                    </tr>
                </table>
                <div style="margin-top: 0.5rem; padding: 0.5rem; font-size: 0.9rem; color: #666;">
                    <strong>TP:</strong> True Positive (Correctly identified as PII) &nbsp; <strong>TN:</strong> True Negative (Correctly identified as non-PII)<br>
                    <strong>FP:</strong> False Positive (Wrongly identified as PII) &nbsp; <strong>FN:</strong> False Negative (Missed PII)
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="redaction">Redaction Quality Evaluation</h2>
            <p class="description">Measures how well detected PII entities were actually redacted</p>
            
            <div class="metric-grid">
                <div class="metric-card correct">
                    <h3>Redaction Accuracy</h3>
                    <div class="metric-value">{redaction_accuracy:.2f}%</div>
                    <p style="font-size: 12px; color: #888;">{correct} / {total_entities} correctly redacted</p>
                </div>
                <div class="metric-card {'leak' if leaks > 0 else 'correct'}">
                    <h3>Leak Rate</h3>
                    <div class="metric-value">{leak_rate:.2f}%</div>
                    <p style="font-size: 12px; color: #888;">{leaks} unredacted entities</p>
                </div>
                <div class="metric-card warning">
                    <h3>Quality Issues</h3>
                    <div class="metric-value">{over + under + semi}</div>
                    <p style="font-size: 12px; color: #888;">Over/Under/Semi redactions</p>
                </div>
                <div class="metric-card">
                    <h3>Total Entities</h3>
                    <div class="metric-value">{total_entities}</div>
                    <p style="font-size: 12px; color: #888;">Evaluated for redaction</p>
                </div>
            </div>
            
            <h3>Redaction Status Summary</h3>
            <table>
                <tr><th>Status</th><th>Count</th><th>Description</th></tr>
                <tr class="correct"><td>Correct</td><td>{correct}</td><td>Fully and properly redacted</td></tr>
                <tr class="leak"><td>Leak</td><td>{leaks}</td><td>Not redacted at all - DATA LEAK!</td></tr>
                <tr class="warning"><td>⚠ Over-redacted</td><td>{over}</td><td>More characters redacted than necessary</td></tr>
                <tr class="warning"><td>⚠ Under-redacted</td><td>{under}</td><td>Partially visible - SECURITY RISK!</td></tr>
                <tr class="warning"><td>⚠ Semi-redacted</td><td>{semi}</td><td>Mostly redacted but some chars visible</td></tr>
            </table>
        </div>
        
        <h2>Errors Summary</h2>
        <p>Total Errors: {len(evaluation_data.get('errors', []))}</p>
        
    </body>
    </html>
    """
    
    return html_content.encode('utf-8')
