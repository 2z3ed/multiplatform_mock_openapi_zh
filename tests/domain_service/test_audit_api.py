"""
API-level tests for audit logs endpoint
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared_db.base import Base
from app.repositories.audit_log_repository import AuditLogRepository


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_client():
    from app.main import app
    return TestClient(app)


class TestAuditLogsAPI:
    """Test audit logs API endpoints"""

    def test_get_audit_logs_returns_data(self, test_client):
        """Test that GET /api/audit-logs endpoint works"""
        response = test_client.get("/api/audit-logs")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_create_audit_log_saves(self, test_client):
        """Test that POST /api/audit-logs creates log"""
        response = test_client.post(
            "/api/audit-logs",
            json={
                "action": "test_action_api",
                "actor_type": "agent",
                "actor_id": "agent_001",
                "target_type": "conversation",
                "target_id": "conv_test",
                "detail": "Test via API"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "log" in data