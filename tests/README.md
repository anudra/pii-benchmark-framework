# Test Suite Documentation

## Test Structure

```
tests/
├── unit/              # Unit tests for individual functions
│   ├── test_matcher.py       - Entity matching algorithms
│   ├── test_validator.py     - Input validation
│   ├── test_metrics.py       - Metrics calculation
│   └── test_redaction.py     - Redaction quality checks
├── component/         # Component/integration tests
│   ├── test_api.py           - API endpoints
│   ├── test_error_analyzer.py - Error analysis
│   └── test_diff_generator.py - Diff generation
└── e2e/              # End-to-end tests
    ├── test_evaluation_workflow.py - Full evaluation flow
    └── test_comparison.py          - Model comparison workflow
```

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test category:
```bash
pytest tests/unit/              # Unit tests only
pytest tests/component/         # Component tests only
pytest tests/e2e/              # E2E tests only
```

### Run with coverage:
```bash
pytest --cov=backend tests/
```

### Run specific test:
```bash
pytest tests/unit/test_matcher.py::TestIOU::test_perfect_overlap
```

## Test Coverage

- **Unit Tests**: Core business logic (matcher, validator, metrics, redaction)
- **Component Tests**: API endpoints, error handling, diff generation
- **E2E Tests**: Full evaluation workflows, model comparison, error recovery

## Prerequisites

```bash
pip install pytest pytest-cov fastapi sqlalchemy
```
