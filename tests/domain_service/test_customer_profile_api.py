"""
API-level tests for customer profile endpoints
"""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.customer_profile import CustomerProfile
from domain_models.models.customer import Customer
from shared_db.base import Base
from app.main import app
from app.api.profile import get_profile_service
from app.services.profile_service import CustomerProfileService


TEST_DB_URL = "sqlite:///test_customer_profile.db"


@pytest.fixture
def db_session():
    import os
    if os.path.exists("test_customer_profile.db"):
        os.remove("test_customer_profile.db")
    from domain_models.models import (
        Customer, Conversation, Message, OrderSnapshot, ShipmentSnapshot,
        AfterSaleCase, KBDocument, KBChunk, AISuggestion, AuditLog, FollowUpTask,
        CustomerProfile
    )
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    if os.path.exists("test_customer_profile.db"):
        os.remove("test_customer_profile.db")


@pytest.fixture
def setup_data(db_session):
    customer = Customer(id=1, platform="jd", platform_customer_id="customer_001")
    db_session.add(customer)
    db_session.commit()
    return {"customer": customer}


@pytest.fixture
def test_client(db_session, setup_data):
    def override_get_profile_service():
        return CustomerProfileService(db_session=db_session)

    app.dependency_overrides[get_profile_service] = override_get_profile_service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


class TestCustomerProfileAPI:
    """Test customer profile API endpoints"""

    def test_get_profile_success(self, test_client, setup_data):
        """Test GET /api/customers/{customer_id}/profile returns profile"""
        test_client.post(
            "/api/profiles",
            json={
                "customer_id": 1,
                "total_orders": 10,
                "total_spent": "1000.00",
                "avg_order_value": "100.00"
            }
        )

        response = test_client.get("/api/customers/1/profile")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == 1
        assert data["total_orders"] == 10

    def test_get_profile_not_found(self, test_client):
        """Test GET non-existent profile returns 404"""
        response = test_client.get("/api/customers/9999/profile")
        assert response.status_code == 404
        assert response.json()["detail"] == "Profile not found"

    def test_create_profile_success(self, test_client, setup_data):
        """Test POST /api/profiles creates profile"""
        response = test_client.post(
            "/api/profiles",
            json={
                "customer_id": 1,
                "total_orders": 10,
                "total_spent": "1000.00",
                "avg_order_value": "100.00"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == 1
        assert data["total_orders"] == 10
        assert data["total_spent"] == "1000.00"
        assert data["avg_order_value"] == "100.00"

    def test_create_profile_duplicate(self, test_client, setup_data):
        """Test POST duplicate profile returns 400"""
        test_client.post(
            "/api/profiles",
            json={
                "customer_id": 1,
                "total_orders": 10,
                "total_spent": "1000.00",
                "avg_order_value": "100.00"
            }
        )

        response = test_client.post(
            "/api/profiles",
            json={
                "customer_id": 1,
                "total_orders": 5,
                "total_spent": "500.00",
                "avg_order_value": "100.00"
            }
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Profile already exists"

    def test_create_profile_invalid_values(self, test_client, setup_data):
        """Test POST with invalid values returns 400"""
        response = test_client.post(
            "/api/profiles",
            json={
                "customer_id": 1,
                "total_orders": -1,
                "total_spent": "1000.00",
                "avg_order_value": "100.00"
            }
        )
        assert response.status_code == 400

    def test_update_profile_success(self, test_client, setup_data):
        """Test PATCH /api/customers/{customer_id}/profile updates profile"""
        create_resp = test_client.post(
            "/api/profiles",
            json={
                "customer_id": 1,
                "total_orders": 5,
                "total_spent": "500.00",
                "avg_order_value": "100.00"
            }
        )

        response = test_client.patch(
            "/api/customers/1/profile",
            json={"total_orders": 10, "total_spent": "1000.00"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_orders"] == 10
        assert data["total_spent"] == "1000.00"

    def test_update_profile_not_found(self, test_client):
        """Test PATCH non-existent profile returns 404"""
        response = test_client.patch(
            "/api/customers/9999/profile",
            json={"total_orders": 10}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Profile not found"

    def test_update_profile_empty_update(self, test_client, setup_data):
        """Test PATCH with empty update returns 400"""
        test_client.post(
            "/api/profiles",
            json={
                "customer_id": 1,
                "total_orders": 5,
                "total_spent": "500.00",
                "avg_order_value": "100.00"
            }
        )

        response = test_client.patch(
            "/api/customers/1/profile",
            json={}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "No valid fields to update"

    def test_update_profile_invalid_values(self, test_client, setup_data):
        """Test PATCH with invalid values returns 400"""
        test_client.post(
            "/api/profiles",
            json={
                "customer_id": 1,
                "total_orders": 5,
                "total_spent": "500.00",
                "avg_order_value": "100.00"
            }
        )

        response = test_client.patch(
            "/api/customers/1/profile",
            json={"total_orders": -1}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid field value"

    def test_delete_profile_success(self, test_client, setup_data):
        """Test DELETE /api/customers/{customer_id}/profile returns success"""
        create_resp = test_client.post(
            "/api/profiles",
            json={
                "customer_id": 1,
                "total_orders": 5,
                "total_spent": "500.00",
                "avg_order_value": "100.00"
            }
        )

        response = test_client.delete("/api/customers/1/profile")
        assert response.status_code == 200
        assert response.json() == {"success": True}

    def test_delete_profile_not_found(self, test_client):
        """Test DELETE non-existent profile returns 404"""
        response = test_client.delete("/api/customers/9999/profile")
        assert response.status_code == 404
        assert response.json()["detail"] == "Profile not found"
