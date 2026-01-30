# Test Cases - PII Benchmark Framework

## 1) Entity Matching Tests

### Strict Mode
- **TC-01**: Exact position match → true positive
- **TC-02**: Position mismatch (off by 1) → false positive
- **TC-03**: Type mismatch → false positive
- **TC-04**: Multiple entities exact match → all matched correctly
- **TC-05**: Empty predictions and ground truth → zero errors

### Lenient Mode (50% IOU)
- **TC-06**: 50% overlap match → true positive
- **TC-07**: 49% overlap → false positive + false negative
- **TC-08**: Wrong entity type with overlap → false positive

---

## 2) Input Validation Tests

### Ground Truth Validation
- **TC-09**: Valid format with all fields → accepted
- **TC-10**: Missing 'entities' field → validation error
- **TC-11**: Missing 'text' field → validation error
- **TC-12**: Invalid start/end positions → validation error
- **TC-13**: Empty entities list → accepted

### Predictions Validation
- **TC-14**: Valid format with required fields → accepted
- **TC-15**: Missing required fields → validation error
- **TC-16**: Invalid entity positions → validation error

---

## 3) Metrics Calculation Tests

### Basic Metrics
- **TC-17**: Perfect detection (TP=10, FP=0, FN=0) → precision=1.0, recall=1.0, f1=1.0
- **TC-18**: Partial detection (TP=8, FP=2, FN=3) → metrics calculated correctly
- **TC-19**: No detection (TP=0, FN=10) → precision=0, recall=0, f1=0

### Per-Entity Metrics
- **TC-20**: Calculate metrics per entity type → separate scores for NAME, EMAIL, etc.
- **TC-21**: Entity type with no predictions → FN count correct
- **TC-22**: Entity type with no ground truth → FP count correct

---

## 4) Redaction Quality Tests

### Redaction Detection
- **TC-23**: Completely redacted entity → score 1.0
- **TC-24**: Partially redacted entity (leaked chars) → score < 1.0
- **TC-25**: No redaction → score 0.0
- **TC-26**: Mixed redaction (some leaked, some redacted) → score calculated correctly

---

## 5) API Endpoint Tests

### Evaluation Endpoint
- **TC-27**: POST /api/evaluate with valid payload → 200 response with ID
- **TC-28**: POST /api/evaluate with invalid format → 400 error
- **TC-29**: GET /api/evaluation/{id} with valid ID → returns full data
- **TC-30**: GET /api/evaluation/{id} with invalid ID → 404 error

### History & Comparison
- **TC-31**: GET /api/history → returns list of evaluations
- **TC-32**: GET /api/history?model=name → filters by model
- **TC-33**: GET /api/compare?eval1=id1&eval2=id2 → comparison returned
- **TC-34**: Compare with invalid ID → 404 error

### AI Summary
- **TC-35**: POST generate-summary → summary generated with grades
- **TC-36**: GET existing summary → summary retrieved
- **TC-37**: Generate with disabled LLM → error handled gracefully

---

## 6) Error Handling Tests

### Error Analysis
- **TC-38**: MISSING_ENTITY errors detected → categorized correctly
- **TC-39**: POSITION_MISMATCH errors detected → recorded with details
- **TC-40**: Multiple error types → all categorized independently

### Edge Cases
- **TC-41**: Very large entity list (1000+) → processed without errors
- **TC-42**: Empty text input → validation handled
- **TC-43**: Special characters in text → escaped properly in output

---

## 7) Diff Generation Tests

- **TC-44**: Diff between identical texts → no changes
- **TC-45**: Diff original vs redacted → differences highlighted
- **TC-46**: Complete redaction → all marked as changes
- **TC-47**: HTML structure valid → renders without errors

---

## 8) End-to-End Workflow Tests

- **TC-48**: Upload → Parse → Validate → Evaluate → Store → Retrieve
- **TC-49**: Strict mode evaluation → rigid matching enforced
- **TC-50**: Lenient mode evaluation → 50% overlap enforced
- **TC-51**: Create two evaluations → Compare → differences shown
- **TC-52**: Filter history by model → correct subset returned

---

## 9) Frontend Integration Tests

- **TC-53**: Generate AI Summary button → dropdown opens with loader
- **TC-54**: Existing AI Summary → dropdown closed by default
- **TC-55**: Per-Entity Analysis cards → hover effects work
- **TC-56**: Metrics displayed → precision, recall, f1, accuracy visible
- **TC-57**: Grade badge shown → A(green), B(blue), C(orange), D/F(red)

---

## 10) Performance Tests

- **TC-58**: Process 100 entities → under 100ms
- **TC-59**: Process 1000 entities → under 1000ms
- **TC-60**: Generate AI summary → under 5s
- **TC-61**: Concurrent 10 requests → all processed without errors

---

# Test Execution Mapping

| Test Category | Location | Cases |
|---------------|----------|-------|
| Unit - Matching | `tests/unit/test_matcher.py` | TC-01 to TC-08 |
| Unit - Validation | `tests/unit/test_validator.py` | TC-09 to TC-16 |
| Unit - Metrics | `tests/unit/test_metrics.py` | TC-17 to TC-22 |
| Unit - Redaction | `tests/unit/test_redaction.py` | TC-23 to TC-26 |
| Component - API | `tests/component/test_api.py` | TC-27 to TC-37 |
| Component - Error | `tests/component/test_error_analyzer.py` | TC-38 to TC-43 |
| Component - Diff | `tests/component/test_diff_generator.py` | TC-44 to TC-47 |
| E2E - Workflow | `tests/e2e/test_evaluation_workflow.py` | TC-48 to TC-52 |
| Manual - Frontend | Browser Testing | TC-53 to TC-57 |
| Manual - Performance | Load Testing | TC-58 to TC-61 |

---

## How to Run Tests

```bash
# All tests
pytest

# Specific category
pytest tests/unit/
pytest tests/component/
pytest tests/e2e/

# With coverage
pytest --cov=backend

# Specific test
pytest tests/unit/test_matcher.py::TestStrictMatch::test_exact_match

# Verbose output
pytest -v
```
