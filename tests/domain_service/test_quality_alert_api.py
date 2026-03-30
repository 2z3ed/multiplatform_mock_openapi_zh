"""
API-level tests for quality_alert
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


TEST_DB_URL = "sqlite:///test_quality_alert.db"


@pytest.fixture
def db_session():
    if os.path.exists("test_quality_alert.db"):
        os.remove("test_quality_alert.db")
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    if os.path.exists("test_quality_alert.db"):
        os.remove("test_quality_alert.db")


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
    rule = QualityRule(
        id=1,
        rule_code="RULE001",
        rule_name="Test Rule",
        rule_type="slow_reply",
        severity="high"
    )
    db_session.add(rule)
    result = QualityInspectionResult(
        id=1,
        conversation_id=1,
        quality_rule_id=1,
        hit=True,
        severity="high"
    )
    db_session.add(result)
    db_session.commit()
    return {"customer": customer, "conversation": conversation, "rule": rule, "result": result}


class TestQualityAlertAPI:
    """Test quality_alert API endpoints"""

    def test_list_alerts_empty(self, client):
        """Test GET /api/quality/alerts when no alerts exist"""
        response = client.get("/api/quality/alerts")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_list_alerts(self, client, db_session, setup_data):
        """Test GET /api/quality/alerts"""
        alert = QualityAlert(quality_inspection_result_id=1, alert_level="high")
        db_session.add(alert)
        db_session.commit()

        response = client.get("/api/quality/alerts")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_alert_not_found(self, client):
        """Test GET /api/quality/alerts/{id} with non-existent id"""
        response = client.get("/api/quality/alerts/9999")

        assert response.status_code == 404
