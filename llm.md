## LLM Integration Documentation

The PII Benchmark Framework includes an integrated LLM (Large Language Model) feature that automatically analyzes evaluation results and generates actionable insights, recommendations, and quality assessments. This feature leverages OpenRouter API to provide intelligent analysis without requiring users to manually interpret complex metrics.

### Key Features

- **Automatic Analysis**: Generates comprehensive summaries of evaluation results
- **Quality Grading**: Assigns letter grades (A-F) based on performance metrics
- **Prioritized Recommendations**: Provides HIGH/MEDIUM/LOW priority action items
- **Entity-Level Insights**: Per-entity type performance analysis
- **Expandable UI**: Non-intrusive panel design with progressive disclosure
- **Security-First**: Only sends aggregate metrics, never raw PII data

---

## Architecture

```
User Evaluation → Backend Metrics → Database → Generate AI Summary (Optional) → OpenRouter API → LLM Analysis → Database Storage → Frontend Display
```

### Data Analysis Scope

The LLM analyzes **aggregated metrics only** to ensure privacy and security:

**Detection Metrics**
- Precision, Recall, F1 Score, Accuracy
- Confusion Matrix (TP, TN, FP, FN)
- Per-entity type performance breakdown

**Redaction Quality**
- Total entities vs. correctly redacted count
- Data leak detection and counts
- Over/under-redaction statistics
- Overall redaction quality score

**Error Analysis**
- False positive/negative counts by entity type
- Error position information (character offsets)
- Error categorization and patterns

**Evaluation Metadata**
- Model name and version
- Matching mode (strict/lenient)
- Timestamp and evaluation ID

### AI-Generated Output

The system generates a structured response containing:
- Overall performance summary (2-3 sentences)
- Letter grade (A-F) with confidence score
- Strengths and weaknesses analysis
- Prioritized recommendations with justification
- Per-entity type insights
- Redaction quality analysis

---

## Configuration (Add environment variables)

```env
LLM_ENABLED=true
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_TIMEOUT=30
OPENROUTER_SITE_URL=https://your-domain.com
OPENROUTER_APP_NAME=PII Benchmark Framework
```

---

## Implementation

### Backend Components

**LLM Service**
Core service module that handles all LLM interactions, including prompt construction, API communication, and response parsing.

**Database Schema**
Extended Result model with AI summary fields for storing generated insights and timestamps.

**API Endpoints**
- Generate AI summary for an evaluation
- Retrieve existing AI summary from database

### Frontend Components

**UI Panel**
Expandable panel structure with header, collapsible content area, and action buttons.

**JavaScript Functions**
- Check for existing summaries on page load
- Trigger AI analysis via API
- Render summary in UI
- Handle expand/collapse interactions

---

## Security & Privacy

### Data Protection

**Data NOT sent to LLM:**
- Original text containing PII
- Redacted text
- User information
- File paths or system details

**Data sent to LLM:**
- Aggregate metrics (counts, percentages)
- Error positions (character offsets only)
- Entity types (EMAIL, PAN, etc.)
- Evaluation metadata

---
