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


class TestEvaluationEndpoint:
    def test_create_evaluation(self, client):
        """Test creating an evaluation"""
        original = "John works here"
        redacted = "#### works here"
        payload = {
            "model_name": "test_model",
            "mode": "strict",
            "original_text": original,
            "redacted_text": redacted,
            "ground_truth": {
                "text": original,
                "entities": [
                    {"start": 0, "end": 4, "entity_type": "NAME", "text": "John"}
                ]
            },
            "predictions": {
                "predictions": [
                    {"start": 0, "end": 4, "entity_type": "NAME"}
                ]
            }
        }
        response = client.post("/api/evaluate", json=payload)
        if response.status_code != 200 and response.status_code != 201:
            print(f"Response: {response.text}")
        assert response.status_code in [200, 201]

    def test_get_evaluation(self, client):
        """Test retrieving an evaluation"""
        response = client.get("/api/evaluation/1")
        assert response.status_code in [200, 404]


class TestHistoryEndpoint:
    def test_get_history(self, client):
        """Test retrieving evaluation history"""
        response = client.get("/api/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_history_with_filter(self, client):
        """Test retrieving history with filters"""
        response = client.get("/api/history?model=test_model")
        assert response.status_code == 200


class TestCompareEndpoint:
    def test_compare_evaluations(self, client):
        """Test comparing two evaluations"""
        response = client.get("/api/compare?eval1=1&eval2=2")
        assert response.status_code in [200, 404]
