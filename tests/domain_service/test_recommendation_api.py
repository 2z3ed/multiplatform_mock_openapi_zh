"""
API-level tests for recommendation endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.customer import Customer
from domain_models.models.conversation import Conversation
from shared_db.base import Base
from app.main import app
from app.api.recommendation import get_recommendation_service
from app.services.recommendation_service import RecommendationService


TEST_DB_URL = "sqlite:///test_recommendation.db"


@pytest.fixture
def db_session():
    import os
    if os.path.exists("test_recommendation.db"):
        os.remove("test_recommendation.db")
    from domain_models.models import (
        Customer, Conversation, Message, OrderSnapshot, ShipmentSnapshot,
        AfterSaleCase, KBDocument, KBChunk, AISuggestion, AuditLog, FollowUpTask,
        CustomerTag, CustomerProfile, Recommendation
    )
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    if os.path.exists("test_recommendation.db"):
        os.remove("test_recommendation.db")


@pytest.fixture
def setup_data(db_session):
    customer = Customer(id=1, platform="jd", platform_customer_id="customer_001")
    db_session.add(customer)
    conversation = Conversation(id=1, platform="jd", customer_id=1, status="open")
    db_session.add(conversation)
    db_session.commit()
    return {"customer": customer, "conversation": conversation}


@pytest.fixture
def test_client(db_session, setup_data):
    def override_get_recommendation_service():
        return RecommendationService(db_session=db_session)

    app.dependency_overrides[get_recommendation_service] = override_get_recommendation_service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


class TestRecommendationAPI:
    """Test recommendation API endpoints"""

    def test_create_recommendation_success(self, test_client, setup_data):
        """Test POST /api/recommendations creates recommendation with pending status"""
        response = test_client.post(
            "/api/recommendations",
            json={
                "conversation_id": 1,
                "customer_id": 1,
                "product_id": "PROD001",
                "product_name": "Test Product",
                "reason": "Recommended for you",
                "suggested_copy": "You might like this!"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["conversation_id"] == 1
        assert data["customer_id"] == 1
        assert data["product_id"] == "PROD001"
        assert data["status"] == "pending"

    def test_get_recommendation_success(self, test_client, setup_data):
        """Test GET /api/recommendations/{id} returns recommendation"""
        create_resp = test_client.post(
            "/api/recommendations",
            json={
                "conversation_id": 1,
                "customer_id": 1,
                "product_id": "PROD001",
                "product_name": "Test Product"
            }
        )
        recommendation_id = create_resp.json()["id"]

        response = test_client.get(f"/api/recommendations/{recommendation_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == recommendation_id
        assert data["product_id"] == "PROD001"

    def test_get_recommendation_not_found(self, test_client):
        """Test GET /api/recommendations/{id} returns 404 for non-existent"""
        response = test_client.get("/api/recommendations/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Recommendation not found"

    def test_list_recommendations_by_conversation_success(self, test_client, setup_data):
        """Test GET /api/conversations/{conversation_id}/recommendations returns list"""
        test_client.post(
            "/api/recommendations",
            json={"conversation_id": 1, "customer_id": 1, "product_id": "PROD001", "product_name": "Product 1"}
        )
        test_client.post(
            "/api/recommendations",
            json={"conversation_id": 1, "customer_id": 1, "product_id": "PROD002", "product_name": "Product 2"}
        )

        response = test_client.get("/api/conversations/1/recommendations")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_recommendations_by_conversation_empty(self, test_client, setup_data):
        """Test GET /api/conversations/{conversation_id}/recommendations returns empty list"""
        response = test_client.get("/api/conversations/1/recommendations")
        assert response.status_code == 200
        assert response.json() == []

    def test_accept_recommendation_success(self, test_client, setup_data):
        """Test POST /api/recommendations/{id}/accept accepts recommendation"""
        create_resp = test_client.post(
            "/api/recommendations",
            json={
                "conversation_id": 1,
                "customer_id": 1,
                "product_id": "PROD001",
                "product_name": "Test Product"
            }
        )
        recommendation_id = create_resp.json()["id"]

        response = test_client.post(f"/api/recommendations/{recommendation_id}/accept")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

    def test_reject_recommendation_success(self, test_client, setup_data):
        """Test POST /api/recommendations/{id}/reject rejects recommendation"""
        create_resp = test_client.post(
            "/api/recommendations",
            json={
                "conversation_id": 1,
                "customer_id": 1,
                "product_id": "PROD001",
                "product_name": "Test Product"
            }
        )
        recommendation_id = create_resp.json()["id"]

        response = test_client.post(f"/api/recommendations/{recommendation_id}/reject")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"

    def test_accept_recommendation_not_found(self, test_client):
        """Test POST /api/recommendations/{id}/accept returns 404 for non-existent"""
        response = test_client.post("/api/recommendations/9999/accept")
        assert response.status_code == 404
        assert response.json()["detail"] == "Recommendation not found"

    def test_reject_recommendation_not_found(self, test_client):
        """Test POST /api/recommendations/{id}/reject returns 404 for non-existent"""
        response = test_client.post("/api/recommendations/9999/reject")
        assert response.status_code == 404
        assert response.json()["detail"] == "Recommendation not found"

    def test_accept_recommendation_not_pending_returns_400(self, test_client, setup_data):
        """Test POST /api/recommendations/{id}/accept returns 400 when not pending"""
        create_resp = test_client.post(
            "/api/recommendations",
            json={
                "conversation_id": 1,
                "customer_id": 1,
                "product_id": "PROD001",
                "product_name": "Test Product"
            }
        )
        recommendation_id = create_resp.json()["id"]

        test_client.post(f"/api/recommendations/{recommendation_id}/accept")

        response = test_client.post(f"/api/recommendations/{recommendation_id}/accept")
        assert response.status_code == 400
        assert response.json()["detail"] == "Recommendation is not in pending status"

    def test_reject_recommendation_not_pending_returns_400(self, test_client, setup_data):
        """Test POST /api/recommendations/{id}/reject returns 400 when not pending"""
        create_resp = test_client.post(
            "/api/recommendations",
            json={
                "conversation_id": 1,
                "customer_id": 1,
                "product_id": "PROD001",
                "product_name": "Test Product"
            }
        )
        recommendation_id = create_resp.json()["id"]

        test_client.post(f"/api/recommendations/{recommendation_id}/reject")

        response = test_client.post(f"/api/recommendations/{recommendation_id}/reject")
        assert response.status_code == 400
        assert response.json()["detail"] == "Recommendation is not in pending status"
