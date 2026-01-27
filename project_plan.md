# Project Plan

## 3-Day Development Plan

Building this framework in 3 days to get an MVP ready.

---

## Day 1: Backend Stuff

**What I'm building:** The core logic that does the evaluation

**Tasks:**
- Set up project structure and install packages
- Create data models using Pydantic
- Write the span matching logic (exact and partial match)
- Build the metrics calculator (Precision, Recall, F1)

**Goal by EOD:** Have a working backend that can take JSON inputs and output metrics

---

## Day 2: Connect Everything + Start UI

**What I'm building:** Make the backend work with a simple web interface + add storage

**Tasks:**
- Create the main evaluation engine that ties everything together
- Set up Streamlit and get the basic app running
- Add file upload for ground truth, predictions, and redacted docs
- Connect the UI to backend evaluation logic
- **Add SQLite database for evaluation history**
  - Create database schema (evaluations table)
  - Build db_manager.py for saving/retrieving reports
  - Auto-save every evaluation run

**Goal by EOD:** Users can upload files, see evaluation results, and all runs are auto-saved to database

---

## Day 3: Dashboard + History Viewer + Deployment

**What I'm building:** Make it look good, add history features, and make it deployable

**Tasks:**
- Build the dashboard to show metrics nicely
- Add charts using Plotly
- Show error breakdowns (false positives/negatives/misclassifications)
- Create some sample test data with redaction examples
- **Add Previous Reports viewer**
  - Create history page/tab to browse saved evaluations
  - Show table of past runs with timestamps, model names, F1 scores
  - View detailed report for any previous evaluation
  - Compare 2 evaluations side-by-side
- Get Docker working

**Goal by EOD:** Full working app with evaluation history that runs in Docker

---

## What's Included (MVP)

Things I'm definitely building:
- ✅ Upload JSON files (ground truth + predictions + redacted docs)
- ✅ Three matching strategies (strict, lenient, token-level)
- ✅ Calculate Precision, Recall, F1-Score
- ✅ Redaction quality evaluation (missed/over-redaction detection)
- ✅ Show per-entity breakdown (EMAIL, PAN, PHONE, etc.)
- ✅ Show per-document metrics
- ✅ **SQLite database for evaluation history**
- ✅ **Previous reports viewer with comparison feature**
- ✅ Simple dashboard with metrics and charts
- ✅ Error categorization (FP/FN/misclassification)
- ✅ Docker deployment

What I'm skipping for now:
- ❌ Advanced trend analysis/charts over time
- ❌ Confidence threshold tuning
- ❌ Multi-user support
- ❌ API endpoints
- ❌ Comprehensive test suite (just basic testing)

---

## Success Checklist

By the end of Day 3, I should be able to:
- [ ] Upload ground truth, prediction, and redacted document files
- [ ] See overall accuracy metrics (detection + redaction)
- [ ] See per-entity and per-document performance breakdown
- [ ] View lists of false positives, false negatives, and misclassifications
- [ ] View redaction errors (missed/over-redacted)
- [ ] **Browse previous evaluation reports**
- [ ] **Compare performance between different model versions**
- [ ] Run everything in Docker
- [ ] Have sample data to demo with intentional errors

---