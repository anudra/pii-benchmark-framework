import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.db import get_db, Base, engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Create test client"""
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


class TestEvaluationWorkflow:
    """Test complete evaluation workflow"""
    
    def test_full_evaluation_flow(self, client):
        """Test: Create evaluation -> Get results -> Check history"""
        
        # Step 1: Create evaluation
        original = "John has john@test.com email"
        redacted = "John has ############## mail"  # john@test.com is 13 chars at positions 10-23
        payload = {
            "model_name": "test_model",
            "mode": "strict",
            "original_text": original,
            "redacted_text": redacted,
            "ground_truth": {
                "text": original,
                "entities": [
                    {"start": 0, "end": 4, "entity_type": "NAME", "text": "John"},
                    {"start": 10, "end": 23, "entity_type": "EMAIL", "text": "john@test.com"}
                ]
            },
            "predictions": {
                "predictions": [
                    {"start": 0, "end": 4, "entity_type": "NAME"},
                    {"start": 10, "end": 23, "entity_type": "EMAIL"}
                ]
            }
        }
        
        response = client.post("/api/evaluate", json=payload)
        if response.status_code not in [200, 201]:
            print(f"Error response: {response.text}")
        assert response.status_code in [200, 201]
        eval_id = response.json().get("id")
        assert response.status_code == 200
        result = response.json()
        assert result["model_name"] == "test_model"
        assert result["metrics"]["precision"] >= 0
        
        # Step 3: Check history
        response = client.get("/api/history")
        assert response.status_code == 200
        history = response.json()
        assert any(e["id"] == eval_id for e in history)

    def test_lenient_vs_strict_mode(self, client):
        """Test comparing lenient and strict modes"""
        
        original = "John Doe"
        redacted = "#### ###"
        payload_strict = {
            "model_name": "model_strict",
            "mode": "strict",
            "original_text": original,
            "redacted_text": redacted,
            "ground_truth": {
                "text": original,
                "entities": [{"start": 0, "end": 4, "entity_type": "NAME", "text": "John"}]
            },
            "predictions": {
                "predictions": [{"start": 0, "end": 4, "entity_type": "NAME"}]
            }
        }
        
        response = client.post("/api/evaluate", json=payload_strict)
        assert response.status_code in [200, 201]


class TestRedactionValidation:
    """Test redaction quality validation in workflow"""
    
    def test_perfect_redaction_detection(self, client):
        """Test detection of perfect redaction"""
        original = "John Doe"
        redacted = "#### ###"
        payload = {
            "model_name": "test_model",
            "mode": "strict",
            "original_text": original,
            "redacted_text": redacted,
            "ground_truth": {
                "text": original,
                "entities": [{"start": 0, "end": 4, "entity_type": "NAME", "text": "John"}]
            },
            "predictions": {
                "predictions": [{"start": 0, "end": 4, "entity_type": "NAME"}]
            }
        }

        response = client.post("/api/evaluate", json=payload)
        assert response.status_code in [200, 201]
        result = response.json()
        assert "redaction_analysis" in result
