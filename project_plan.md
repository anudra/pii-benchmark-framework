# Project Implementation Plan

## MVP Goal

Build a functional **PII Evaluation Framework** that can:
- [x]Accept text files + JSON labels as input
- [x]Evaluate detection & redaction accuracy
- [x]Show results with visualizations
- [x]Maintain history of evaluations
- [x]Support comparison and export

**Timeline:** 3 days for MVP

---

## Development Phases (3-Day Sprint)

### Day 1: Backend Foundation + Core Logic

**Goal:** Build complete backend evaluation engine

**Tasks:**
- [x] Set up project structure
- [x] Initialize FastAPI backend
- [x] Create database schema (SQLite)
- [x] Define Pydantic models for GT, predictions, results
- [x] Write input validator
- [x] Implement Span Matcher (strict + lenient modes)
- [x] Implement Metrics Calculator (TP/TN/FP/FN, P/R/F1)
- [x] Implement Redaction Checker (all 5 categories)
- [x] Implement Error Analyzer
- [x] Basic unit tests for critical functions

**Deliverable:** Complete backend evaluation engine working

---

### Day 2: API + LLM + Frontend Core

**Goal:** Create API and basic functional UI

**Tasks:**
- [x] Create all API endpoints:
- [x] Implement database CRUD operations
- [x] LLM Integration
- [x] Create HTML pages (upload, results, history, compare)
- [x] Create basic CSS styling
- [x] Write JavaScript for:
  - [x]File upload
  - [x]API calls
  - [x]Basic results display

**Deliverable:** Working API and LLM + functional (unstyled) UI

---

### Day 3: Visualizations + Export + Docker

**Goal:** Polish UI, add visualizations, and deploy

**Tasks:**
- [x] Implement color-coded diff view
- [x] Add Chart.js visualizations:
  - [x]Confusion matrix heatmap
  - [x]Precision/Recall/F1 bar charts
  - [x]Per-entity breakdown
- [x] Implement history table with actions
- [x] Implement comparison page
- [x] Implement JSON and PDF export
- [x] End-to-end testing
- [x] Write Dockerfile and docker-compose.yml
- [x] Test Docker deployment
- [x] Bug fixes and final polish

**Deliverable:** Complete working system with Docker

---

## Features Breakdown

### MVP Features (Must Have)

| Feature | Status | Priority |
|---------|--------|----------|
| File upload (4 files) | ⏳ TODO | P0 |
| Strict/Lenient mode selection | ⏳ TODO | P0 |
| Detection evaluation (TP/TN/FP/FN) | ⏳ TODO | P0 |
| Metrics calculation (P/R/F1) | ⏳ TODO | P0 |
| Confusion matrix | ⏳ TODO | P0 |
| Redaction verification | ⏳ TODO | P0 |
| Color-coded diff view | ⏳ TODO | P0 |
| History table | ⏳ TODO | P0 |
| View/Delete actions | ⏳ TODO | P0 |
| Export as JSON & PDF | ⏳ TODO | P0 |
| SQLite database | ⏳ TODO | P0 |
| Docker deployment | ⏳ TODO | P0 |

### Post-MVP Features (Nice to Have)

| Feature | Priority |
|---------|----------|
| Batch file upload | P1 |
| Custom entity types | P1 |
| Confidence threshold analysis | P2 |
| ROC curves | P2 |
| API authentication | P2 |
| Multi-user support | P3 |
| Email notifications | P3 |

---

## Testing Strategy

### Unit Tests
**Coverage:** Individual components

**Key Test Cases:**
- [x]Exact match detection
- [x]Partial overlap detection
- [x]Overlapping entities
- [x]Nested entities
- [x]Type mismatches
- [x]Redaction verification
- [x]Edge case: Empty entities
- [x]Edge case: Overlapping redactions

### Integration Tests
**Coverage:** API endpoints

### End-to-End Tests
**Coverage:** Full user workflows
- [x]Upload → Evaluate → View Results
- [x]Upload → Evaluate → Export JSON
- [x]Upload → Evaluate → Export PDF
- [x]View History → Delete Evaluation
- [x]Compare Two Evaluations

---

## Tech Stack Summary

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Backend** | FastAPI | Fast, modern, auto-docs |
| **Frontend** | HTML/CSS/JS | Simple, no framework overhead |
| **Database** | SQLite | No setup, file-based, easy Docker |
| **Charts** | Chart.js | Lightweight, beautiful charts |
| **Export (PDF)** | WeasyPrint | HTML to PDF conversion |
| **Testing** | pytest | Standard Python testing |
| **DevOps** | Docker | Easy deployment |

---

## Metrics for Success

| Metric | Target |
|--------|--------|
| Evaluation Accuracy | 100% (must correctly classify TP/FP/FN) |
| API Response Time | < 2s for evaluation |
| UI Load Time | < 1s |
| Test Coverage | > 80% |
| Docker Build Time | < 5 min |
| End-to-End Test Pass | 100% |


### Future Enhancements

| Feature | Priority | Estimated Time |
|---------|----------|----------------|
| Advanced PDF styling | P1 | +1 day |
| Batch file upload | P1 | +1 day |
| Confidence threshold analysis | P2 | +2 days |
| ROC curves | P2 | +1 day |
| Custom entity types | P1 | +2 days |
| API authentication | P2 | +1 day |
| Multi-user support | P3 | +3 days |
| Email notifications | P3 | +1 day


```
Day 1: Backend Complete
  (Setup + Validator + Matcher + Metrics + Redaction + Error Analyzer)
   ↓
Day 2: API + Basic Frontend
  (All endpoints + HTML pages + JavaScript + Basic styling)
   ↓
Day 3: Polish + Export + Docker
  (Charts + Diff View + Export + Docker + Testing)
```

**Key Strategy:**
- [x]Focus on **functionality over perfection**
- [x]Build **vertically** (one complete feature at a time)
- [x]**Test as you go** (no dedicated testing day)
- [x]Keep UI **simple but functional**
- [x]Use **existing libraries** (no custom implementations)
