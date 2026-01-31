# Product Specification: Evaluation & Benchmarking Framework for Sensitive Data Detection and Redaction

---

## Problem Title

**Building an Evaluation & Benchmarking Framework for PII Detection and Redaction Systems**

---

## Problem Statement

Sensitive data detection and redaction systems are only useful if their **accuracy, reliability, and mistakes are measurable**.
Organizations need a way to **quantitatively evaluate** how well their system detects sensitive data and how correctly it redacts it.

This framework is an **evaluation and benchmarking tool** that measures the performance of a sensitive data detection + redaction pipeline using well-defined metrics and test datasets.

---

## What Is This?

This is **NOT a PII detector**. It's a **judge / examiner** for PII detection + redaction systems.

**Analogy:**
- **Your System**: Tries to find and redact sensitive data
- **This Framework**: Grades how well your system performed with measurable metrics

---

## Objectives

Design and implement a framework that:

* Evaluates the accuracy of sensitive data detection
* Measures redaction correctness
* Identifies false positives and false negatives
* Handles edge cases like overlapping entities, partial redactions
* Produces a clear, interpretable scorecard with visualizations
* Maintains evaluation history
* Supports comparison between different models
* Exports results in multiple formats

---

## User Perspective (What Users Do)

### Step 1: Upload Files

User uploads:
- **Original Text File** (.txt) - The original document
- **Redacted Text File** (.txt) - The document after redaction
- **Ground Truth Labels** (JSON) - What sensitive data actually exists
- **Predicted Labels** (JSON) - What your system detected

### Step 2: Select Evaluation Mode

User chooses:
- **Strict Mode**: Exact character-position matching (for production validation)
- **Lenient Mode**: Allows partial overlaps (for development/testing)

### Step 3: Run Evaluation

User clicks **"Evaluate"** button → System processes → Shows results

### Step 4: View Results

User sees:
- Overall metrics (Precision, Recall, F1-Score)
- Confusion Matrix
- Color-coded diff view showing:
  - ✅ Correctly redacted
  - ❌ Leaks (missed sensitive data)
  - ⚠️ Over-redacted (innocent data redacted)
  - 🔶 Under-redacted (partial redaction)
- Charts and graphs
- Detailed error breakdown

### Step 5: History & Management

- View all previous evaluations in a table
- Compare two evaluations side-by-side
- Export results as PDF or JSON
- Delete old evaluations

---

## Inputs

### 1. Original Text File (.txt)
```
Example:
My email is abcd@gmail.com and PAN is ABCDE1234F.
Phone: +91-9876543210
```

### 2. Redacted Text File (.txt)
```
Example:
My email is ************** and PAN is ************.
Phone: **************
```

### 3. Ground Truth Labels (JSON)

```json
{
  "text": "My email is abcd@gmail.com and PAN is ABCDE1234F.",
  "entities": [
    {
      "entity_type": "EMAIL",
      "start": 12,
      "end": 26,
      "text": "abcd@gmail.com"
    },
    {
      "entity_type": "PAN",
      "start": 39,
      "end": 49,
      "text": "ABCDE1234F"
    }
  ]
}
```

### 4. Predicted Labels (JSON)

```json
{
  "predictions": [
    {
      "entity_type": "EMAIL",
      "start": 12,
      "end": 26
    },
    {
      "entity_type": "PAN",
      "start": 39,
      "end": 49
    }
  ]
}
```

---

## Core Features

### Feature 1: Detection Evaluation

**What it does:** Compares predicted entities against ground truth

**Outputs:**
- **True Positives (TP)**: Correctly detected entities
- **True Negatives (TN)**: Correctly ignored non-sensitive text
- **False Positives (FP)**: Incorrectly flagged safe text
- **False Negatives (FN)**: Missed sensitive data

**Evaluation Modes:**

| Mode | Description | Use Case |
|------|-------------|----------|
| **Strict** | Exact position match required | Production/compliance |
| **Lenient** | 50%+ overlap counts as match | Development/testing |


### Feature 2: Redaction Verification

**What it does:** Verifies that detected entities were actually redacted

**Checks:**
- All true sensitive entities redacted?
- Non-sensitive text unchanged?
- Complete or partial redaction?

**Redaction Categories Detected:**

| Category | Example Original | Example Redacted | Status |
|----------|-----------------|------------------|--------|
| **Correct** | `abcd@gmail.com` | `**************` | ✅ Good |
| **Leak** | `abcd@gmail.com` | `abcd@gmail.com` | ❌ Missed |
| **Over-redaction** | `pan on stove` | `*** on stove` | ⚠️ Innocent data |
| **Under-redaction** | `abcd@gmail.com` | `abcd@****.com` | 🔶 Partial |

### Feature 3: Metrics Calculation

**Computed Metrics:**
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1-Score = 2 × (Precision × Recall) / (Precision + Recall)
- Accuracy = (TP + TN) / (TP + TN + FP + FN)

**Granularity:**
- Overall system metrics
- Per-entity type metrics (EMAIL, PAN, PHONE, etc.)
- Redaction quality score

### Feature 4: Visualization & Diff View

**Color-Coded Diff:**
- Shows original vs redacted side-by-side
- Highlights differences with color codes:
  - 🟢 Green: Correctly redacted
  - 🔴 Red: Leak (missed)
  - 🟡 Yellow: Over-redacted
  - 🟠 Orange: Under-redacted

**Charts & Graphs:**
- Confusion matrix
- Precision-Recall-F1 bar charts
- Per-entity performance breakdown
- Redaction quality pie chart

### Feature 5: History Management

**History Page Features:**
- Table view showing all past evaluations
- Columns:
  - ID (unique identifier)
  - Timestamp
  - Model Name (user-provided or "Default")
  - Evaluation Mode (Strict/Lenient)
  - Overall Accuracy
  - Actions (View Results | Delete)

**Data Persistence:**
- SQLite database stores:
  - Input files (original & redacted text)
  - Ground truth & predicted labels
  - Computed metrics
  - Error analysis results
  - Timestamps and metadata
  - I summary

### Feature 6: Comparison

**Compare Page Features:**
- Select any 2 evaluations from history
- Side-by-side comparison showing:
  - Metric differences (Precision, Recall, F1)
  - Improvement/degradation indicators
  - Visual charts showing differences

### Feature 7: Export Functionality

**Export Formats:**

**1. JSON Export:**
```json
{
  "evaluation_id": "eval_001",
  "timestamp": "24 Jan 2026 10:20:36",
  "model_name": "PII_Detector_v2",
  "mode": "strict",
  "metrics": { ... },
  "confusion_matrix": { ... },
  "errors": { ... }
}
```

**2. PDF Export:**
- Professional report format
- Includes all metrics, charts, and error analysis
- Human-readable summary

---

## Outputs

### 1. Evaluation Scorecard

Display on dashboard:
- AI Summary
- Overall Metrics
- Per-Entity Breakdown
- Confusion Matrix
- Redaction Quality Score

### 2. Error Report

Lists:
- False Positives
- False Negatives
- Misclassified entities
- Redaction errors

### 3. Visual Reports

- Charts and graphs
- Color-coded diff view

### 4. Exportable Reports

- JSON format (machine-readable)
- PDF format (human-readable)

---

## Tech Stack

| Component | Technology | Reason |
|-----------|------------|--------|
| **Frontend** | HTML/CSS, JS | Clean, simple UI |
| **Backend** | FastAPI | Modern, async, fast, auto-docs |
| **Database** | SQLite | Simple, file-based, no setup |
| **DevOps** | Docker | Easy deployment |
| **Metrics** | scikit-learn | Industry-standard metrics |
| **Visualization** | Chart.js | Lightweight charts |
| **LLM functionality** | OpenRouter | Free usage, vast no.of models |

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Correct metric computation | 100% accuracy |
| Handle edge cases | Overlaps, partials, etc. |
| Redaction verification | All categories detected |
| Report clarity | Non-technical users understand |
| Export functionality | PDF + JSON working |
| History management | CRUD operations functional |

---

## What's Out of Scope (MVP)

- Multi-file batch processing
- Multi-language support
- OCR/PDF parsing (text already extracted)
- Advanced ML model training

---

## Bonus Features

After MVP, These are the features that can be done in future:
- Confidence threshold analysis
- ROC curves / AUC scores
- Batch evaluation (multiple files at once)
- API endpoint for programmatic access
- Custom entity type support
- Email notifications for completed evaluations
- Team collaboration features
- Version control for models

---

## Long-term Vision

This framework could evolve into:
- [x]**SaaS Platform**: Multi-tenant evaluation service
- [x]**Enterprise Tool**: Integration with GDPR compliance systems
- [x]**Research Tool**: Academic benchmarking for PII detection
- [x]**Marketplace**: Compare commercial PII detection APIs

---