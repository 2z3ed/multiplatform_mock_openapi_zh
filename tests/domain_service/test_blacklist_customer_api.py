"""
API-level tests for blacklist_customer
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


TEST_DB_URL = "sqlite:///test_blacklist.db"


@pytest.fixture
def db_session():
    if os.path.exists("test_blacklist.db"):
        os.remove("test_blacklist.db")
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    if os.path.exists("test_blacklist.db"):
        os.remove("test_blacklist.db")


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestBlacklistCustomerAPI:
    """Test blacklist_customer API endpoints"""

    def test_create_blacklist(self, client):
        """Test POST /api/risk/blacklist"""
        response = client.post(
            "/api/risk/blacklist",
            json={
                "customer_id": 1,
                "reason": "Test reason",
                "source": "manual"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == 1
        assert data["reason"] == "Test reason"

    def test_create_blacklist_invalid_source(self, client):
        """Test POST /api/risk/blacklist with invalid source"""
        response = client.post(
            "/api/risk/blacklist",
            json={
                "customer_id": 1,
                "source": "invalid_source"
            }
        )

        assert response.status_code == 422

    def test_create_duplicate_customer(self, client):
        """Test creating blacklist with duplicate customer_id returns 400"""
        client.post(
            "/api/risk/blacklist",
            json={"customer_id": 1}
        )

        response = client.post(
            "/api/risk/blacklist",
            json={"customer_id": 1}
        )

        assert response.status_code == 400

    def test_list_blacklist(self, client):
        """Test GET /api/risk/blacklist"""
        client.post(
            "/api/risk/blacklist",
            json={"customer_id": 1, "reason": "Customer 1"}
        )
        client.post(
            "/api/risk/blacklist",
            json={"customer_id": 2, "reason": "Customer 2"}
        )

        response = client.get("/api/risk/blacklist")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_delete_blacklist(self, client):
        """Test DELETE /api/risk/blacklist/{customer_id}"""
        client.post(
            "/api/risk/blacklist",
            json={"customer_id": 1}
        )

        response = client.delete("/api/risk/blacklist/1")

        assert response.status_code == 204

        list_response = client.get("/api/risk/blacklist")
        assert len(list_response.json()) == 0

    def test_delete_non_existent(self, client):
        """Test DELETE /api/risk/blacklist/{customer_id} with non-existent customer"""
        response = client.delete("/api/risk/blacklist/9999")

        assert response.status_code == 404
