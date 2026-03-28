"""
API-level tests for risk flag endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.customer import Customer
from domain_models.models.conversation import Conversation
from shared_db.base import Base
from app.main import app
from app.api.risk_flag import get_risk_flag_service
from app.services.risk_flag_service import RiskFlagService


TEST_DB_URL = "sqlite:///test_risk_flag.db"


@pytest.fixture
def db_session():
    import os
    if os.path.exists("test_risk_flag.db"):
        os.remove("test_risk_flag.db")
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    customer = Customer(id=1, platform="test", platform_customer_id="test_001", display_name="Test")
    session.add(customer)
    conversation = Conversation(id=1, customer_id=1, platform="test", status="active")
    session.add(conversation)
    session.commit()
    
    yield session
    session.close()
    if os.path.exists("test_risk_flag.db"):
        os.remove("test_risk_flag.db")


@pytest.fixture
def test_client(db_session):
    def override_get_risk_flag_service():
        return RiskFlagService(db_session=db_session)

    app.dependency_overrides[get_risk_flag_service] = override_get_risk_flag_service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


class TestRiskFlagAPI:
    """Test risk flag API endpoints"""

    def test_create_risk_flag_success(self, test_client):
        """Test POST /api/risk-flags creates risk flag with active status"""
        response = test_client.post(
            "/api/risk-flags",
            json={
                "customer_id": 1,
                "risk_type": "negative_sentiment",
                "risk_level": "medium",
                "description": "Test description"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "active"
        assert data["risk_type"] == "negative_sentiment"

    def test_create_risk_flag_optional_conversation_id(self, test_client):
        """Test POST /api/risk-flags allows omitting conversation_id"""
        response = test_client.post(
            "/api/risk-flags",
            json={
                "customer_id": 1,
                "risk_type": "negative_sentiment"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["conversation_id"] is None

    def test_create_risk_flag_optional_risk_level_defaults_to_low(self, test_client):
        """Test POST /api/risk-flags defaults risk_level to low"""
        response = test_client.post(
            "/api/risk-flags",
            json={
                "customer_id": 1,
                "risk_type": "negative_sentiment"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["risk_level"] == "low"

    def test_create_risk_flag_invalid_risk_type(self, test_client):
        """Test POST /api/risk-flags returns 400 for invalid risk_type"""
        response = test_client.post(
            "/api/risk-flags",
            json={
                "customer_id": 1,
                "risk_type": "invalid_type"
            }
        )

        assert response.status_code == 400

    def test_create_risk_flag_invalid_risk_level(self, test_client):
        """Test POST /api/risk-flags returns 400 for invalid risk_level"""
        response = test_client.post(
            "/api/risk-flags",
            json={
                "customer_id": 1,
                "risk_type": "negative_sentiment",
                "risk_level": "invalid_level"
            }
        )

        assert response.status_code == 400

    def test_get_risk_flag_success(self, test_client):
        """Test GET /api/risk-flags/{id} returns risk flag"""
        create_response = test_client.post(
            "/api/risk-flags",
            json={
                "customer_id": 1,
                "risk_type": "negative_sentiment"
            }
        )
        risk_flag_id = create_response.json()["id"]

        response = test_client.get(f"/api/risk-flags/{risk_flag_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == risk_flag_id

    def test_get_risk_flag_not_exists(self, test_client):
        """Test GET /api/risk-flags/{id} returns 404 when not exists"""
        response = test_client.get("/api/risk-flags/9999")

        assert response.status_code == 404

    def test_list_risk_flags_by_customer_id(self, test_client):
        """Test GET /api/risk-flags returns list"""
        test_client.post(
            "/api/risk-flags",
            json={"customer_id": 1, "risk_type": "negative_sentiment"}
        )
        test_client.post(
            "/api/risk-flags",
            json={"customer_id": 1, "risk_type": "complaint_tendency"}
        )

        response = test_client.get("/api/risk-flags?customer_id=1")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_risk_flags_empty(self, test_client):
        """Test GET /api/risk-flags returns empty list"""
        response = test_client.get("/api/risk-flags?customer_id=1")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_risk_flags_missing_customer_id(self, test_client):
        """Test GET /api/risk-flags returns 422 when customer_id missing"""
        response = test_client.get("/api/risk-flags")

        assert response.status_code == 422

    def test_resolve_risk_flag_success(self, test_client):
        """Test POST /api/risk-flags/{id}/resolve resolves risk flag"""
        create_response = test_client.post(
            "/api/risk-flags",
            json={
                "customer_id": 1,
                "risk_type": "negative_sentiment"
            }
        )
        risk_flag_id = create_response.json()["id"]

        response = test_client.post(f"/api/risk-flags/{risk_flag_id}/resolve")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"

    def test_dismiss_risk_flag_success(self, test_client):
        """Test POST /api/risk-flags/{id}/dismiss dismisses risk flag"""
        create_response = test_client.post(
            "/api/risk-flags",
            json={
                "customer_id": 1,
                "risk_type": "negative_sentiment"
            }
        )
        risk_flag_id = create_response.json()["id"]

        response = test_client.post(f"/api/risk-flags/{risk_flag_id}/dismiss")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "dismissed"

    def test_resolve_risk_flag_not_exists(self, test_client):
        """Test POST /api/risk-flags/{id}/resolve returns 404 when not exists"""
        response = test_client.post("/api/risk-flags/9999/resolve")

        assert response.status_code == 404

    def test_dismiss_risk_flag_not_exists(self, test_client):
        """Test POST /api/risk-flags/{id}/dismiss returns 404 when not exists"""
        response = test_client.post("/api/risk-flags/9999/dismiss")

        assert response.status_code == 404

    def test_resolve_risk_flag_non_active_fails(self, test_client):
        """Test POST /api/risk-flags/{id}/resolve returns 400 when not active"""
        create_response = test_client.post(
            "/api/risk-flags",
            json={
                "customer_id": 1,
                "risk_type": "negative_sentiment"
            }
        )
        risk_flag_id = create_response.json()["id"]

        test_client.post(f"/api/risk-flags/{risk_flag_id}/resolve")
        response = test_client.post(f"/api/risk-flags/{risk_flag_id}/resolve")

        assert response.status_code == 400
        assert "not in active status" in response.json()["detail"]

    def test_dismiss_risk_flag_non_active_fails(self, test_client):
        """Test POST /api/risk-flags/{id}/dismiss returns 400 when not active"""
        create_response = test_client.post(
            "/api/risk-flags",
            json={
                "customer_id": 1,
                "risk_type": "negative_sentiment"
            }
        )
        risk_flag_id = create_response.json()["id"]

        test_client.post(f"/api/risk-flags/{risk_flag_id}/dismiss")
        response = test_client.post(f"/api/risk-flags/{risk_flag_id}/dismiss")

        assert response.status_code == 400
        assert "not in active status" in response.json()["detail"]
