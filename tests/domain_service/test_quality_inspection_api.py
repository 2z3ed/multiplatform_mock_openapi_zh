"""
API-level tests for quality_inspection
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models import (
    Customer, Conversation, Message, OrderSnapshot, ShipmentSnapshot,
    AfterSaleCase, KBDocument, KBChunk, AISuggestion, AuditLog, FollowUpTask,
    CustomerTag, CustomerProfile, Recommendation, QualityRule, QualityInspectionResult, QualityAlert
)
from shared_db.base import Base
from app.main import app
from shared_db import get_db


TEST_DB_URL = "sqlite:///test_quality_inspection.db"


@pytest.fixture
def db_session():
    if os.path.exists("test_quality_inspection.db"):
        os.remove("test_quality_inspection.db")
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    if os.path.exists("test_quality_inspection.db"):
        os.remove("test_quality_inspection.db")


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def setup_data(db_session):
    customer = Customer(id=1, platform="jd", platform_customer_id="customer_001")
    db_session.add(customer)
    conversation = Conversation(id=1, platform="jd", customer_id=1, status="open")
    db_session.add(conversation)
    db_session.commit()
    return {"customer": customer, "conversation": conversation}


class TestQualityInspectionAPI:
    """Test quality_inspection API endpoints"""

    def test_inspect_conversation(self, client, setup_data):
        """Test POST /api/quality/inspect"""
        response = client.post(
            "/api/quality/inspect",
            json={"conversation_id": 1}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_results(self, client, setup_data):
        """Test GET /api/quality/results"""
        response = client.get("/api/quality/results")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_results_by_conversation(self, client, setup_data):
        """Test GET /api/quality/results?conversation_id=1"""
        response = client.get("/api/quality/results?conversation_id=1")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_result_not_found(self, client):
        """Test GET /api/quality/results/{id} with non-existent id"""
        response = client.get("/api/quality/results/9999")

        assert response.status_code == 404

    def test_inspect_and_retrieve(self, client, setup_data):
        """Test inspect and then retrieve result"""
        client.post(
            "/api/quality/rules",
            json={
                "rule_code": "RULE001",
                "rule_name": "Test Rule",
                "rule_type": "slow_reply",
                "severity": "medium",
                "config_json": {"max_reply_minutes": 30}
            }
        )

        inspect_response = client.post(
            "/api/quality/inspect",
            json={"conversation_id": 1}
        )

        assert inspect_response.status_code == 200
        results = inspect_response.json()
        assert len(results) == 1

        result_id = results[0]["id"]

        get_response = client.get(f"/api/quality/results/{result_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == result_id
