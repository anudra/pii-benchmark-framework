# Diff HTML generation
# Creates color-coded HTML diff view comparing original and redacted text
# Color scheme: Green (correct), Red (leak), Bright Yellow (over), Dark Orange (under)

from typing import List, Dict, Any
import html


def generate_diff_html(original_text: str, redacted_text: str, 
                      ground_truth: List[Dict[str, Any]],
                      redaction_analysis: Dict[str, Any]) -> str:
    """Generate color-coded HTML diff view"""
    
    # Create position-to-category mapping
    position_map = {}
    
    # Mark correct redactions (green)
    for item in redaction_analysis["categories"]["correct"]:
        for pos in range(item["start"], item["end"]):
            position_map[pos] = "correct"
    
    # Mark leaks (red)
    for item in redaction_analysis["categories"]["leak"]:
        for pos in range(item["start"], item["end"]):
            position_map[pos] = "leak"
    
    # Mark over-redactions (yellow)
    for item in redaction_analysis["categories"]["over"]:
        for pos in range(item["start"], item["end"]):
            position_map[pos] = "over"
    
    # Mark under-redactions (dark orange)
    for item in redaction_analysis["categories"]["under"]:
        for pos in range(item["start"], item["end"]):
            position_map[pos] = "under"
    
    # Color definitions
    colors = {
        "correct": "#4CAF50",     # Green
        "leak": "#F44336",        # Red  
        "over": "#FFD700",        # Bright Yellow (gold)
        "under": "#ff9036"        # Dark Orange
    }
    
    # Build HTML
    html_output = '<div style="font-family: monospace; white-space: pre-wrap; line-height: 1.8;">'
    html_output += '<div style="display: flex; gap: 40px;">'
    
    # Original text column
    html_output += '<div style="flex: 1;"><strong>Original Text:</strong><br/>'
    current_category = None
    for i, char in enumerate(original_text):
        category = position_map.get(i)
        
        if category != current_category:
            if current_category is not None:
                html_output += '</span>'
            if category is not None:
                color = colors.get(category, "#000")
                text_color = "#333" if category == "over" else "white"
                html_output += f'<span style="background-color: {color}; color: {text_color}; padding: 2px 4px; border-radius: 3px;">'
            current_category = category
        
        html_output += html.escape(char)
    
    if current_category is not None:
        html_output += '</span>'
    html_output += '</div>'
    
    # Redacted text column
    html_output += '<div style="flex: 1;"><strong>Redacted Text:</strong><br/>'
    current_category = None
    for i, char in enumerate(redacted_text):
        category = position_map.get(i)
        
        if category != current_category:
            if current_category is not None:
                html_output += '</span>'
            if category is not None:
                color = colors.get(category, "#000")
                text_color = "#333" if category == "over" else "white"
                html_output += f'<span style="background-color: {color}; color: {text_color}; padding: 2px 4px; border-radius: 3px;">'
            current_category = category
        
        html_output += html.escape(char)
    
    if current_category is not None:
        html_output += '</span>'
    html_output += '</div>'
    
    html_output += '</div>'
    
    # Legend
    html_output += '<div style="margin-top: 20px; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">'
    html_output += '<strong>Legend:</strong><br/>'
    html_output += f'<span style="background-color: {colors["correct"]}; color: white; padding: 2px 8px; border-radius: 3px; margin-right: 10px;">Correct</span>'
    html_output += f'<span style="background-color: {colors["leak"]}; color: white; padding: 2px 8px; border-radius: 3px; margin-right: 10px;">Leak</span>'
    html_output += f'<span style="background-color: {colors["over"]}; color: #333; padding: 2px 8px; border-radius: 3px; margin-right: 10px;">Over-redacted</span>'
    html_output += f'<span style="background-color: {colors["under"]}; color: white; padding: 2px 8px; border-radius: 3px;">Under-redacted</span>'
    html_output += '</div>'
    
    html_output += '</div>'
    
    return html_output

