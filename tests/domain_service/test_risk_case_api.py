"""
API-level tests for risk_case
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models import (
    Customer, Conversation, Message, OrderSnapshot, ShipmentSnapshot,
    AfterSaleCase, KBDocument, KBChunk, AISuggestion, AuditLog, FollowUpTask,
    CustomerTag, CustomerProfile, Recommendation, QualityRule, QualityInspectionResult, QualityAlert,
    RiskCase, BlacklistCustomer
)
from shared_db.base import Base
from app.main import app
from shared_db import get_db


TEST_DB_URL = "sqlite:///test_risk_case.db"


@pytest.fixture
def db_session():
    if os.path.exists("test_risk_case.db"):
        os.remove("test_risk_case.db")
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    if os.path.exists("test_risk_case.db"):
        os.remove("test_risk_case.db")


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestRiskCaseAPI:
    """Test risk_case API endpoints"""

    def test_create_risk_case(self, client):
        """Test POST /api/risk/cases"""
        response = client.post(
            "/api/risk/cases",
            json={
                "conversation_id": 1,
                "customer_id": 1,
                "risk_type": "complaint_tendency",
                "severity": "high",
                "evidence_json": {"reason": "test"}
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["risk_type"] == "complaint_tendency"
        assert data["severity"] == "high"
        assert data["status"] == "open"

    def test_create_risk_case_invalid_risk_type(self, client):
        """Test POST /api/risk/cases with invalid risk_type"""
        response = client.post(
            "/api/risk/cases",
            json={
                "conversation_id": 1,
                "customer_id": 1,
                "risk_type": "invalid_type"
            }
        )

        assert response.status_code == 422

    def test_list_risk_cases(self, client):
        """Test GET /api/risk/cases"""
        client.post(
            "/api/risk/cases",
            json={"conversation_id": 1, "customer_id": 1, "risk_type": "complaint_tendency"}
        )
        client.post(
            "/api/risk/cases",
            json={"conversation_id": 2, "customer_id": 1, "risk_type": "negative_emotion"}
        )

        response = client.get("/api/risk/cases")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_risk_case_by_id(self, client):
        """Test GET /api/risk/cases/{id}"""
        create_response = client.post(
            "/api/risk/cases",
            json={"conversation_id": 1, "customer_id": 1, "risk_type": "complaint_tendency"}
        )
        risk_case_id = create_response.json()["id"]

        response = client.get(f"/api/risk/cases/{risk_case_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == risk_case_id

    def test_resolve_risk_case(self, client):
        """Test POST /api/risk/cases/{id}/resolve"""
        create_response = client.post(
            "/api/risk/cases",
            json={"conversation_id": 1, "customer_id": 1, "risk_type": "complaint_tendency"}
        )
        risk_case_id = create_response.json()["id"]

        response = client.post(f"/api/risk/cases/{risk_case_id}/resolve")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"

    def test_dismiss_risk_case(self, client):
        """Test POST /api/risk/cases/{id}/dismiss"""
        create_response = client.post(
            "/api/risk/cases",
            json={"conversation_id": 1, "customer_id": 1, "risk_type": "complaint_tendency"}
        )
        risk_case_id = create_response.json()["id"]

        response = client.post(f"/api/risk/cases/{risk_case_id}/dismiss")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "dismissed"

    def test_escalate_risk_case(self, client):
        """Test POST /api/risk/cases/{id}/escalate"""
        create_response = client.post(
            "/api/risk/cases",
            json={"conversation_id": 1, "customer_id": 1, "risk_type": "complaint_tendency"}
        )
        risk_case_id = create_response.json()["id"]

        response = client.post(f"/api/risk/cases/{risk_case_id}/escalate")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "escalated"

    def test_resolve_non_open_case_fails(self, client):
        """Test that resolving non-open case returns 400"""
        create_response = client.post(
            "/api/risk/cases",
            json={"conversation_id": 1, "customer_id": 1, "risk_type": "complaint_tendency"}
        )
        risk_case_id = create_response.json()["id"]

        client.post(f"/api/risk/cases/{risk_case_id}/resolve")

        response = client.post(f"/api/risk/cases/{risk_case_id}/resolve")

        assert response.status_code == 400
