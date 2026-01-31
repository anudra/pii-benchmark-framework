"""
LLM Service for AI-powered evaluation insights
Integrates with OpenRouter API to generate structured analysis of PII evaluation results
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
LLM_ENABLED = os.getenv("LLM_ENABLED", "false").lower() == "true"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_TIMEOUT = int(os.getenv("OPENROUTER_TIMEOUT", "30"))
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "http://localhost:8000")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "PII Benchmark Framework")


def is_llm_enabled() -> bool:
    """Check if LLM service is enabled and configured"""
    return LLM_ENABLED and bool(OPENROUTER_API_KEY)


def construct_prompt(evaluation_data: Dict[str, Any]) -> str:
    """Construct detailed prompt for LLM analysis"""
    
    metrics = evaluation_data.get("metrics", {})
    confusion_matrix = evaluation_data.get("confusion_matrix", {})
    per_entity_metrics = evaluation_data.get("per_entity_metrics", {})
    redaction_analysis = evaluation_data.get("redaction_analysis", {})
    errors = evaluation_data.get("errors", [])
    
    # Extract redaction summary
    redaction_summary = {}
    if isinstance(redaction_analysis, dict):
        redaction_summary = redaction_analysis.get("summary", {})
    
    prompt = f"""You are an expert AI assistant analyzing PII (Personally Identifiable Information) detection and redaction system performance.

## Evaluation Details
- Model: {evaluation_data.get('model_name', 'Unknown')}
- Mode: {evaluation_data.get('mode', 'strict')}
- Evaluation ID: #{evaluation_data.get('id', 'N/A')}

## Detection Metrics
- Precision: {metrics.get('precision', 0):.4f} ({metrics.get('precision', 0)*100:.2f}%)
- Recall: {metrics.get('recall', 0):.4f} ({metrics.get('recall', 0)*100:.2f}%)
- F1 Score: {metrics.get('f1_score', 0):.4f} ({metrics.get('f1_score', 0)*100:.2f}%)
- Accuracy: {metrics.get('accuracy', 0):.4f} ({metrics.get('accuracy', 0)*100:.2f}%)

## Confusion Matrix
- True Positives (TP): {confusion_matrix.get('TP', 0)} - Correctly detected PII
- True Negatives (TN): {confusion_matrix.get('TN', 0)} - Correctly identified non-PII
- False Positives (FP): {confusion_matrix.get('FP', 0)} - Incorrectly flagged as PII
- False Negatives (FN): {confusion_matrix.get('FN', 0)} - Missed PII entities

## Per-Entity Performance
{json.dumps(per_entity_metrics, indent=2)}

## Redaction Quality
- Total Entities: {redaction_summary.get('total_entities', 0)}
- Correctly Redacted: {redaction_summary.get('correct_redactions', 0)}
- Data Leaks: {redaction_summary.get('leaks', 0)} (CRITICAL - sensitive data not redacted)
- Over-redactions: {redaction_summary.get('over_redactions', 0)} (non-sensitive data redacted)
- Under-redactions: {redaction_summary.get('under_redactions', 0)} (partial redaction)
- Redaction Quality Score: {redaction_summary.get('redaction_quality_score', 0):.4f}

## Error Summary
Total Errors: {len(errors)}
- False Positives: {len([e for e in errors if e.get('error_type') == 'FP'])}
- False Negatives: {len([e for e in errors if e.get('error_type') == 'FN'])}
- Redaction Leaks: {len([e for e in errors if e.get('error_type') == 'LEAK'])}
- Over-redactions: {len([e for e in errors if e.get('error_type') == 'OVER'])}
- Under-redactions: {len([e for e in errors if e.get('error_type') == 'UNDER'])}

## Sample Errors (first 5)
{json.dumps(errors[:5], indent=2) if errors else 'No errors'}

## Task
Analyze this PII evaluation and provide a structured assessment in **valid JSON format only**. Be concise, actionable, and prioritize security issues.

**IMPORTANT: Return ONLY the JSON object. Do NOT include any explanatory text before or after the JSON. Do NOT wrap it in markdown code blocks.**

Return this exact JSON structure:

{{
  "summary": "2-3 sentence overview of overall performance and key findings",
  "overall_grade": "A|B|C|D|F (based on: A=95%+, B=85-94%, C=75-84%, D=65-74%, F=<65%)",
  "confidence_score": 0.0-1.0,
  "strengths": ["list 2-4 specific strengths with metrics"],
  "weaknesses": ["list 2-4 critical weaknesses with impact"],
  "recommendations": [
    {{
      "priority": "high|medium|low",
      "category": "detection|redaction|both",
      "recommendation": "specific actionable fix",
      "justification": "why this matters",
      "expected_impact": "measurable outcome"
    }}
  ],
  "entity_insights": {{
    "ENTITY_TYPE": "brief performance note for each entity type"
  }},
  "redaction_analysis": "security-focused assessment of redaction quality and risks"
}}

Critical priorities:
1. Data leaks are CRITICAL security issues - prioritize them as HIGH
2. Grade based on F1-score primarily
3. Consider both detection AND redaction quality
4. Be specific with metrics in insights
5. Keep recommendations actionable and prioritized
"""
    
    return prompt


def parse_llm_response(response_text: str) -> Optional[Dict[str, Any]]:
    """Parse LLM response, handling markdown code blocks and extracting JSON"""
    try:
        # Remove markdown code blocks if present
        cleaned = response_text.strip()
        
        # Try to find JSON object in the response
        # Look for opening brace
        json_start = cleaned.find('{')
        if json_start == -1:
            print(f"DEBUG - No opening brace found in response")
            return None
        
        # Find matching closing brace
        brace_count = 0
        json_end = -1
        for i in range(json_start, len(cleaned)):
            if cleaned[i] == '{':
                brace_count += 1
            elif cleaned[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break
        
        if json_end == -1:
            print(f"DEBUG - No matching closing brace found")
            return None
        
        # Extract JSON string
        json_str = cleaned[json_start:json_end]
        
        # Parse JSON
        return json.loads(json_str)
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text[:500]}")
        return None
    except Exception as e:
        print(f"Unexpected error parsing response: {e}")
        return None


def generate_ai_summary(evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AI-powered summary for evaluation results
    
    Args:
        evaluation_data: Dictionary containing evaluation metrics and results
        
    Returns:
        Dictionary with AI analysis or error information
    """
    
    if not is_llm_enabled():
        return {
            "error": "LLM service is not enabled",
            "message": "Set LLM_ENABLED=true and configure OPENROUTER_API_KEY in .env"
        }
    
    try:
        # Construct prompt
        prompt = construct_prompt(evaluation_data)
        
        # Call OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": OPENROUTER_SITE_URL,
            "X-Title": OPENROUTER_APP_NAME,
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # Lower temperature for more consistent analysis
            "max_tokens": 2000
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=OPENROUTER_TIMEOUT
        )
        
        # Check for HTTP errors first
        if not response.ok:
            try:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", response.text[:200])
            except:
                error_msg = response.text[:200]
            
            return {
                "error": f"API Error ({response.status_code})",
                "message": error_msg,
                "status_code": response.status_code
            }
        
        # Extract response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON response from API",
                "message": f"Response: {response.text[:300]}"
            }
        
        # Check for API error in response
        if "error" in response_data:
            return {
                "error": "API returned error",
                "message": response_data["error"].get("message", str(response_data["error"]))
            }
        
        # Check for choices
        if "choices" not in response_data or len(response_data["choices"]) == 0:
            return {
                "error": "No response from LLM",
                "message": "API returned empty choices array",
                "raw_response": str(response_data)[:300]
            }
        
        llm_response = response_data["choices"][0]["message"]["content"]
        
        # Parse JSON response
        parsed_summary = parse_llm_response(llm_response)
        
        if not parsed_summary:
            # Log the actual response for debugging
            print(f"DEBUG - Failed to parse LLM response:")
            print(f"Response length: {len(llm_response)}")
            print(f"First 500 chars: {llm_response[:500]}")
            print(f"Last 100 chars: {llm_response[-100:]}")
            
            return {
                "error": "Failed to parse LLM response",
                "message": "LLM did not return valid JSON. Check that the model supports JSON output.",
                "raw_response": llm_response[:500]
            }
        
        # Add metadata
        timestamp = evaluation_data.get("timestamp")
        parsed_summary["_meta"] = {
            "model": OPENROUTER_MODEL,
            "generated_at": timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp),
            "evaluation_id": evaluation_data.get("id")
        }
        
        return parsed_summary
        
    except requests.exceptions.Timeout:
        return {
            "error": "Request timeout",
            "message": "LLM API request timed out. Try again or increase OPENROUTER_TIMEOUT."
        }
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_msg = "Unknown error"
        
        if status_code == 401:
            error_msg = "Invalid API key. Check OPENROUTER_API_KEY in .env"
        elif status_code == 402:
            error_msg = "Payment required. Add credits to your OpenRouter account"
        elif status_code == 429:
            error_msg = "Rate limit exceeded. Try again in a moment"
        elif status_code >= 500:
            error_msg = "OpenRouter service error. Try again later"
        else:
            error_msg = f"HTTP {status_code}: {e.response.text[:200]}"
        
        return {
            "error": "API request failed",
            "message": error_msg,
            "status_code": status_code
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e)
        }
