# PII Detection & Redaction Evaluation Framework

A benchmarking tool to measure the accuracy of PII detection systems using Precision, Recall, and F1-Score metrics.

## What does it do?

- Compare your PII detection system's output against ground truth labels
- Calculate accuracy metrics (Precision, Recall, F1-Score)
- Identify false positives and false negatives
- Generate detailed error reports

## Quick Start

### Option 1: Using Docker (Recommended)

```bash
git clone https://github.com/yourusername/pii-benchmark-framework.git
cd pii-benchmark-framework
docker-compose up --build
```

Open browser at `http://localhost:8501`

### Option 2: Local Setup

```bash
git clone https://github.com/yourusername/pii-benchmark-framework.git
cd pii-benchmark-framework
python -m venv venv
venv\Scripts\activate  # Windows (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

Open browser at `http://localhost:8501`

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

## Usage

Upload two JSON files:
1. **Ground Truth** - Human-verified labels
2. **Predictions** - Your system's output

Click "Run Evaluation" to see results.

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

**Author:** [Your Name] - Internship Assessment 2026
