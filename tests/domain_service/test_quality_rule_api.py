"""
API-level tests for quality_rule
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


TEST_DB_URL = "sqlite:///test_quality_rule.db"


@pytest.fixture
def db_session():
    if os.path.exists("test_quality_rule.db"):
        os.remove("test_quality_rule.db")
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    if os.path.exists("test_quality_rule.db"):
        os.remove("test_quality_rule.db")


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestQualityRuleAPI:
    """Test quality_rule API endpoints"""

    def test_create_quality_rule(self, client):
        """Test POST /api/quality/rules"""
        response = client.post(
            "/api/quality/rules",
            json={
                "rule_code": "RULE001",
                "rule_name": "Slow Reply Check",
                "rule_type": "slow_reply",
                "severity": "high",
                "description": "Check if agent replies too slowly",
                "config_json": {"max_reply_minutes": 30}
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["rule_code"] == "RULE001"
        assert data["rule_name"] == "Slow Reply Check"
        assert data["rule_type"] == "slow_reply"
        assert data["severity"] == "high"

    def test_create_quality_rule_invalid_rule_type(self, client):
        """Test POST /api/quality/rules with invalid rule_type"""
        response = client.post(
            "/api/quality/rules",
            json={
                "rule_code": "RULE001",
                "rule_name": "Invalid Rule",
                "rule_type": "invalid_type"
            }
        )

        assert response.status_code == 422

    def test_create_quality_rule_invalid_severity(self, client):
        """Test POST /api/quality/rules with invalid severity"""
        response = client.post(
            "/api/quality/rules",
            json={
                "rule_code": "RULE001",
                "rule_name": "Invalid Severity",
                "rule_type": "slow_reply",
                "severity": "critical"
            }
        )

        assert response.status_code == 422

    def test_list_quality_rules(self, client):
        """Test GET /api/quality/rules"""
        client.post(
            "/api/quality/rules",
            json={"rule_code": "RULE001", "rule_name": "Rule 1", "rule_type": "slow_reply"}
        )
        client.post(
            "/api/quality/rules",
            json={"rule_code": "RULE002", "rule_name": "Rule 2", "rule_type": "forbidden_word"}
        )

        response = client.get("/api/quality/rules")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_quality_rules_empty(self, client):
        """Test GET /api/quality/rules when empty"""
        response = client.get("/api/quality/rules")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_quality_rule_by_id(self, client):
        """Test GET /api/quality/rules/{id}"""
        create_response = client.post(
            "/api/quality/rules",
            json={"rule_code": "RULE001", "rule_name": "Test Rule", "rule_type": "slow_reply"}
        )
        rule_id = create_response.json()["id"]

        response = client.get(f"/api/quality/rules/{rule_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == rule_id
        assert data["rule_code"] == "RULE001"

    def test_get_quality_rule_by_id_not_found(self, client):
        """Test GET /api/quality/rules/{id} with non-existent id"""
        response = client.get("/api/quality/rules/9999")

        assert response.status_code == 404
