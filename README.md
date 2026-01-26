# PII Detection & Redaction Evaluation Framework

A tool to benchmark PII detection systems by measuring Precision, Recall, and F1-Score.

## What does it do?

This framework helps you measure how accurate your PII detection system is. You give it:
- Your test documents with labeled sensitive data (ground truth)
- What your system detected (predictions)

It calculates:
- How accurate your detections are (Precision)
- How complete your detections are (Recall)
- Overall performance score (F1)
- What mistakes were made (false positives/negatives)

## Quick Start

### Option 1: Using Docker (Easiest)

```bash
git clone https://github.com/yourusername/pii-benchmark-framework.git
cd pii-benchmark-framework
docker-compose up --build
```

Open `http://localhost:8501` in your browser.

### Option 2: Local Setup

```bash
git clone https://github.com/yourusername/pii-benchmark-framework.git
cd pii-benchmark-framework
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
streamlit run app.py
```

Then go to `http://localhost:8501`

## Project Structure

```
├── app.py                  # Main Streamlit app
├── evaluator/              # Evaluation engine
├── models/                 # Data models
├── utils/                  # Helper functions
├── pages/                  # Dashboard pages
├── data/                   # Sample datasets
├── tests/                  # Unit tests
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── requirements.txt        # Python dependencies
```

## How to Use

**Step 1:** Upload your files
- Ground truth JSON (what should be detected)
- Predictions JSON (what your system detected)

**Step 2:** Pick a matching strategy
- **Strict** - Positions must match exactly (for production testing)
- **Lenient** - 50%+ overlap is okay (for development)
- **Token-Level** - Matches at word level

**Step 3:** Click "Run Evaluation" and view results

### Input Format

**Ground Truth:**
```json
{
  "document_id": "doc_001",
  "text": "Email me at john@example.com",
  "entities": [
    {
      "entity_type": "EMAIL",
      "start": 12,
      "end": 28,
      "text": "john@example.com"
    }
  ]
}
```

**Predictions:**
```json
{
  "document_id": "doc_001",
  "predictions": [
    {
      "entity_type": "EMAIL",
      "start": 12,
      "end": 28
    }
  ]
}
```

## Tech Stack

Python, Streamlit, Pandas, scikit-learn, Plotly, Docker

## Testing

```bash
pytest
```

---

**Built for:** Internship Assessment Project  
**Duration:** 3-day sprint (Jan 27-29, 2026)
