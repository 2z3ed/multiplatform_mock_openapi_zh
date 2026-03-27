"""
API-level tests for customer tag endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.customer_tag import CustomerTag
from domain_models.models.customer import Customer
from shared_db.base import Base
from app.main import app
from app.api.tags import get_tag_service
from app.services.tag_service import CustomerTagService


TEST_DB_URL = "sqlite:///test_customer_tag.db"


@pytest.fixture
def db_session():
    import os
    if os.path.exists("test_customer_tag.db"):
        os.remove("test_customer_tag.db")
    from domain_models.models import (
        Customer, Conversation, Message, OrderSnapshot, ShipmentSnapshot,
        AfterSaleCase, KBDocument, KBChunk, AISuggestion, AuditLog, FollowUpTask,
        CustomerTag
    )
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    if os.path.exists("test_customer_tag.db"):
        os.remove("test_customer_tag.db")


@pytest.fixture
def setup_data(db_session):
    customer = Customer(id=1, platform="jd", platform_customer_id="customer_001")
    db_session.add(customer)
    db_session.commit()
    return {"customer": customer}


@pytest.fixture
def test_client(db_session, setup_data):
    def override_get_tag_service():
        return CustomerTagService(db_session=db_session)

    app.dependency_overrides[get_tag_service] = override_get_tag_service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


class TestCustomerTagAPI:
    """Test customer tag API endpoints"""

    def test_get_tags_success(self, test_client, setup_data):
        """Test GET /api/customers/{customer_id}/tags returns tag list"""
        test_client.post(
            "/api/tags",
            json={
                "customer_id": 1,
                "tag_type": "behavior",
                "tag_value": "high_value"
            }
        )
        test_client.post(
            "/api/tags",
            json={
                "customer_id": 1,
                "tag_type": "preference",
                "tag_value": "electronics"
            }
        )

        response = test_client.get("/api/customers/1/tags")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_tags_empty(self, test_client, setup_data):
        """Test GET /api/customers/{customer_id}/tags returns empty list"""
        response = test_client.get("/api/customers/1/tags")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_tag_success(self, test_client, setup_data):
        """Test POST /api/tags creates tag"""
        response = test_client.post(
            "/api/tags",
            json={
                "customer_id": 1,
                "tag_type": "segment",
                "tag_value": "vip"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == 1
        assert data["tag_type"] == "segment"
        assert data["tag_value"] == "vip"
        assert data["source"] == "manual"

    def test_create_tag_invalid_tag_type(self, test_client, setup_data):
        """Test POST with invalid tag_type returns 400"""
        response = test_client.post(
            "/api/tags",
            json={
                "customer_id": 1,
                "tag_type": "invalid_type",
                "tag_value": "some_value"
            }
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid tag_type"

    def test_create_tag_duplicate(self, test_client, setup_data):
        """Test POST duplicate tag returns 400"""
        test_client.post(
            "/api/tags",
            json={
                "customer_id": 1,
                "tag_type": "preference",
                "tag_value": "electronics"
            }
        )

        response = test_client.post(
            "/api/tags",
            json={
                "customer_id": 1,
                "tag_type": "preference",
                "tag_value": "electronics"
            }
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Duplicate tag"

    def test_delete_tag_success(self, test_client, setup_data):
        """Test DELETE /api/tags/{tag_id} returns success"""
        create_resp = test_client.post(
            "/api/tags",
            json={
                "customer_id": 1,
                "tag_type": "behavior",
                "tag_value": "test"
            }
        )
        tag_id = create_resp.json()["id"]

        response = test_client.delete(f"/api/tags/{tag_id}")
        assert response.status_code == 200
        assert response.json() == {"success": True}

    def test_delete_tag_not_found(self, test_client):
        """Test DELETE non-existent tag returns 404"""
        response = test_client.delete("/api/tags/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Tag not found"
