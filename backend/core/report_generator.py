# Report generation for exports
# Generates JSON and PDF export reports
# Includes all metrics, charts, and error analysis

import json
from typing import Dict, Any
from datetime import datetime
from io import BytesIO

# Try to import PDF libraries
PDF_AVAILABLE = False
try:
    from xhtml2pdf import pisa
    PDF_AVAILABLE = True
except (ImportError, OSError):
    pass


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
    
    # Get diff HTML
    diff_html = evaluation_data.get("diff_html", "")
    
    # Get confusion matrix values
    cm = evaluation_data.get('confusion_matrix', {})
    tp = cm.get('TP', 0)
    tn = cm.get('TN', 0)
    fp = cm.get('FP', 0)
    fn = cm.get('FN', 0)
    
    # Get error details
    errors = evaluation_data.get('errors', [])
    errors_html = _generate_errors_html(errors) if errors else '<p style="color: #999; font-style: italic;">No errors detected</p>'
    
    # Build simple HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                font-size: 10pt;
                color: #000;
                line-height: 1.5;
            }}
            h1 {{
                color: #000;
                border-bottom: 2px solid #000;
                padding-bottom: 8px;
                margin-bottom: 20px;
                font-size: 18pt;
            }}
            h2 {{
                color: #000;
                margin-top: 25px;
                margin-bottom: 10px;
                font-size: 14pt;
                border-bottom: 1px solid #000;
                padding-bottom: 5px;
            }}
            h3 {{
                color: #000;
                margin-top: 15px;
                margin-bottom: 8px;
                font-size: 11pt;
            }}
            .metadata {{
                border: 1px solid #000;
                padding: 15px;
                margin-bottom: 20px;
            }}
            .metadata p {{
                margin: 5px 0;
                font-size: 10pt;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 15px 0;
            }}
            th {{
                background-color: #f0f0f0;
                color: #000;
                padding: 8px;
                text-align: left;
                font-weight: bold;
                font-size: 10pt;
                border: 1px solid #000;
            }}
            td {{
                border: 1px solid #000;
                padding: 8px;
                font-size: 10pt;
            }}
            .metric-line {{
                margin: 8px 0;
                padding: 5px 0;
                border-bottom: 1px dotted #ccc;
            }}
            .diff-container {{
                margin: 20px 0;
                page-break-inside: avoid;
            }}
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
        
        <!-- Entity Detection Evaluation -->
        <h2>1. Entity Detection Evaluation</h2>
        <p><em>Measures how accurately the model identifies PII entity positions</em></p>
        
        <h3>Detection Metrics:</h3>
        <div class="metric-line"><strong>Precision:</strong> {precision:.2f}% (Correctness of predictions)</div>
        <div class="metric-line"><strong>Recall:</strong> {recall:.2f}% (Coverage of actual PII)</div>
        <div class="metric-line"><strong>F1-Score:</strong> {f1_score:.2f}% (Harmonic mean)</div>
        <div class="metric-line"><strong>Accuracy:</strong> {accuracy:.2f}% (Overall correctness)</div>
        
        <h3>Confusion Matrix:</h3>
        <table>
            <tr>
                <th style="width: 25%;"></th>
                <th style="width: 37.5%;">Predicted Positive</th>
                <th style="width: 37.5%;">Predicted Negative</th>
            </tr>
            <tr>
                <td style="font-weight: bold;">Actual Positive</td>
                <td>TP: {tp}</td>
                <td>FN: {fn}</td>
            </tr>
            <tr>
                <td style="font-weight: bold;">Actual Negative</td>
                <td>FP: {fp}</td>
                <td>TN: {tn}</td>
            </tr>
        </table>
        <p><small>
        <strong>TP:</strong> Correctly identified as PII | 
        <strong>TN:</strong> Correctly identified as non-PII | 
        <strong>FP:</strong> Wrongly identified as PII | 
        <strong>FN:</strong> Missed PII
        </small></p>
        
        <!-- Redaction Quality Evaluation -->
        <h2>2. Redaction Quality Evaluation</h2>
        <p><em>Measures how well detected PII entities were actually redacted</em></p>
        
        <h3>Redaction Metrics:</h3>
        <div class="metric-line"><strong>Redaction Accuracy:</strong> {redaction_accuracy:.2f}% ({correct}/{total_entities} correctly redacted)</div>
        <div class="metric-line"><strong>Leak Rate:</strong> {leak_rate:.2f}% ({leaks} unredacted entities)</div>
        <div class="metric-line"><strong>Quality Issues:</strong> {over + under + semi} (Over/Under/Semi redactions)</div>
        <div class="metric-line"><strong>Total Entities:</strong> {total_entities} evaluated</div>
        
        <h3>Redaction Status Summary:</h3>
        <table>
            <tr>
                <th>Status</th>
                <th>Count</th>
                <th>Description</th>
            </tr>
            <tr>
                <td>Correct</td>
                <td>{correct}</td>
                <td>Fully and properly redacted</td>
            </tr>
            <tr>
                <td>Leak</td>
                <td>{leaks}</td>
                <td>Not redacted at all - CRITICAL DATA LEAK!</td>
            </tr>
            <tr>
                <td>Over-redacted</td>
                <td>{over}</td>
                <td>More characters redacted than necessary</td>
            </tr>
            <tr>
                <td>Under-redacted</td>
                <td>{under}</td>
                <td>Partially visible - SECURITY RISK!</td>
            </tr>
            <tr>
                <td>Semi-redacted</td>
                <td>{semi}</td>
                <td>Mostly redacted but some characters visible</td>
            </tr>
        </table>
        
        <!-- Text Comparison (Diff) -->
        <h2 style="page-break-before: always;">3. Text Comparison (Original vs Redacted)</h2>
        <p><em>Color-coded comparison showing how PII was redacted</em></p>
        
        <div class="diff-container">
            {diff_html if diff_html else '<p>Diff visualization not available</p>'}
        </div>
        
        <!-- Errors Summary -->
        <h2>4. Errors Summary</h2>
        <p><strong>Total Errors:</strong> {len(errors)}</p>
        
        {errors_html}
        
    </body>
    </html>
    """
    
    if PDF_AVAILABLE:
        # Generate actual PDF from HTML using xhtml2pdf
        result_file = BytesIO()
        pisa_status = pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=result_file)
        if not pisa_status.err:
            return result_file.getvalue()
    
    # Fallback to HTML if PDF generation fails
    return html_content.encode('utf-8')


def _generate_errors_html(errors: list) -> str:
    """Generate simple HTML for error items"""
    if not errors:
        return '<p><em>No errors detected</em></p>'
    
    html = "<table><tr><th>Type</th><th>Entity</th><th>Position</th><th>Text</th><th>Description</th></tr>"
    for error in errors:
        html += f"""
        <tr>
            <td>{error.get('error_type', 'Unknown')}</td>
            <td>{error.get('entity_type', 'N/A')}</td>
            <td>{error.get('position_start', 'N/A')}-{error.get('position_end', 'N/A')}</td>
            <td>{error.get('text', 'N/A')}</td>
            <td>{error.get('description', 'No description')}</td>
        </tr>
        """
    html += "</table>"
    return html
