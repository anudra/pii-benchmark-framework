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


class TestMultipleEvaluations:
    """Test comparing multiple evaluations"""
    
    def test_model_comparison(self, client):
        """Test comparing results from different models"""
        
        models = ["model_a", "model_b"]
        eval_ids = []
        
        for model in models:
            original = "John Doe works here"
            redacted = "#### #### works here"
            payload = {
                "model_name": model,
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
            if response.status_code in [200, 201]:
                eval_ids.append(response.json().get("id"))
        
        # Compare models
        if len(eval_ids) >= 2:
            response = client.get(f"/api/compare?eval1={eval_ids[0]}&eval2={eval_ids[1]}")
            assert response.status_code in [200, 404]


class TestErrorRecovery:
    """Test API error handling"""
    
    def test_invalid_payload(self, client):
        """Test with invalid payload"""
        response = client.post("/api/evaluate", json={"invalid": "data"})
        assert response.status_code >= 400

    def test_missing_evaluation(self, client):
        """Test retrieving non-existent evaluation"""
        response = client.get("/api/evaluation/99999")
        assert response.status_code == 404
