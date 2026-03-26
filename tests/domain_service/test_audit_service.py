"""
Service-level tests for audit log persistence
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.audit_log import AuditLog
from shared_db.base import Base
from shared_db.mixins import TimestampMixin
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.audit_service import AuditService


TEST_DB_URL = "sqlite:///:memory:"


class TestAuditLogRepository:
    """Test audit log repository"""

    @pytest.fixture
    def db_session(self):
        engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        yield session
        session.close()

    def test_create_audit_log(self, db_session):
        """Test creating audit log in database"""
        repo = AuditLogRepository(db_session)
        log = repo.create(
            action="test_action",
            actor_type="user",
            actor_id="user_001",
            target_type="conversation",
            target_id="conv_001",
            detail="Test detail",
            detail_json={"key": "value"}
        )
        
        assert log.id is not None
        assert log.action == "test_action"
        assert log.actor_type == "user"
        assert log.actor_id == "user_001"
        assert log.target_type == "conversation"
        assert log.target_id == "conv_001"
        assert log.detail == "Test detail"
        assert log.detail_json == {"key": "value"}
        assert log.created_at is not None

    def test_get_logs_with_filter(self, db_session):
        """Test getting audit logs with filters"""
        repo = AuditLogRepository(db_session)
        repo.create(action="action_1", actor_id="user_001", target_id="conv_001")
        repo.create(action="action_2", actor_id="user_002", target_id="conv_002")
        repo.create(action="action_1", actor_id="user_001", target_id="conv_003")
        
        logs = repo.get_logs(action="action_1")
        assert len(logs) == 2
        
        logs = repo.get_logs(actor_id="user_002")
        assert len(logs) == 1
        assert logs[0].action == "action_2"


class TestAuditServicePersistence:
    """Test audit service persistence"""

    @pytest.fixture
    def db_session(self):
        engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        yield session
        session.close()

    def test_log_event_writes_to_db(self, db_session):
        """Test that log_event writes to database"""
        service = AuditService(db_session=db_session)
        
        result = service.log_event(
            action="test_event",
            actor_type="agent",
            actor_id="agent_001",
            target_type="conversation",
            target_id="conv_001",
            detail="Test event details",
            detail_json={"test": "data"}
        )
        
        assert result["id"] is not None
        assert result["action"] == "test_event"
        
        logs = service.get_logs()
        assert len(logs) == 1
        assert logs[0]["action"] == "test_event"

    def test_provider_mode_switched_logs_to_db(self, db_session):
        """Test provider_mode_switched event is persisted"""
        service = AuditService(db_session=db_session)
        
        result = service.provider_mode_switched(
            platform="jd",
            old_mode="real",
            new_mode="mock"
        )
        
        assert result["action"] == "provider_mode_switched"
        assert result["target_id"] == "jd"
        
        logs = service.get_logs(action="provider_mode_switched")
        assert len(logs) == 1
        assert logs[0]["detail_json"]["old_mode"] == "real"
        assert logs[0]["detail_json"]["new_mode"] == "mock"

    def test_message_sent_logs_to_db(self, db_session):
        """Test message_sent event is persisted"""
        service = AuditService(db_session=db_session)
        
        result = service.message_sent(
            conversation_id="conv_001",
            message_id="msg_001",
            agent_id="agent_001"
        )
        
        assert result["action"] == "message_sent"
        assert result["target_id"] == "msg_001"
        
        logs = service.get_logs(action="message_sent")
        assert len(logs) == 1