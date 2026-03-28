"""
Service-level tests for risk flag
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.risk_flag import RiskFlag
from domain_models.models.customer import Customer
from domain_models.models.conversation import Conversation
from domain_models.models.audit_log import AuditLog
from shared_db.base import Base
from app.services.risk_flag_service import RiskFlagService


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
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


class TestRiskFlagService:
    """Test risk flag service"""

    def test_create_risk_flag_default_status_active(self, db_session):
        """Test creating risk flag defaults to active status"""
        service = RiskFlagService(db_session=db_session)
        result = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        assert result is not None
        assert result["status"] == "active"

    def test_create_risk_flag_default_risk_level_low(self, db_session):
        """Test creating risk flag defaults to low risk level"""
        service = RiskFlagService(db_session=db_session)
        result = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        assert result["risk_level"] == "low"

    def test_create_risk_flag_conversation_id_nullable(self, db_session):
        """Test creating risk flag allows null conversation_id"""
        service = RiskFlagService(db_session=db_session)
        result = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        assert result["conversation_id"] is None

    def test_create_risk_flag_description_nullable(self, db_session):
        """Test creating risk flag allows null description"""
        service = RiskFlagService(db_session=db_session)
        result = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        assert result["description"] is None

    def test_create_risk_flag_extra_json_nullable(self, db_session):
        """Test creating risk flag allows null extra_json"""
        service = RiskFlagService(db_session=db_session)
        result = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        assert result["extra_json"] is None

    def test_get_risk_flag_by_id_exists(self, db_session):
        """Test getting risk flag by id when exists"""
        service = RiskFlagService(db_session=db_session)
        created = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        result = service.get_risk_flag_by_id(created["id"])

        assert result is not None
        assert result["id"] == created["id"]

    def test_get_risk_flag_by_id_not_exists(self, db_session):
        """Test getting risk flag by id when not exists"""
        service = RiskFlagService(db_session=db_session)
        result = service.get_risk_flag_by_id(9999)

        assert result is None

    def test_list_risk_flags_by_customer_id(self, db_session):
        """Test listing risk flags by customer_id"""
        service = RiskFlagService(db_session=db_session)
        service.create_risk_flag(customer_id=1, risk_type="negative_sentiment")
        service.create_risk_flag(customer_id=1, risk_type="complaint_tendency")
        service.create_risk_flag(customer_id=2, risk_type="negative_sentiment")

        results = service.list_risk_flags_by_customer_id(1)

        assert len(results) == 2

    def test_resolve_risk_flag_active_to_resolved_success(self, db_session):
        """Test resolving risk flag from active to resolved succeeds"""
        service = RiskFlagService(db_session=db_session)
        created = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        result, error = service.resolve_risk_flag(created["id"])

        assert result is not None
        assert error is None
        assert result["status"] == "resolved"

    def test_dismiss_risk_flag_active_to_dismissed_success(self, db_session):
        """Test dismissing risk flag from active to dismissed succeeds"""
        service = RiskFlagService(db_session=db_session)
        created = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        result, error = service.dismiss_risk_flag(created["id"])

        assert result is not None
        assert error is None
        assert result["status"] == "dismissed"

    def test_resolve_risk_flag_not_exists_returns_failure(self, db_session):
        """Test resolving non-existent risk flag returns failure"""
        service = RiskFlagService(db_session=db_session)
        result, error = service.resolve_risk_flag(9999)

        assert result is None
        assert error == "not_found"

    def test_dismiss_risk_flag_not_exists_returns_failure(self, db_session):
        """Test dismissing non-existent risk flag returns failure"""
        service = RiskFlagService(db_session=db_session)
        result, error = service.dismiss_risk_flag(9999)

        assert result is None
        assert error == "not_found"

    def test_resolve_risk_flag_non_active_status_fails(self, db_session):
        """Test resolving risk flag when status is not active fails"""
        service = RiskFlagService(db_session=db_session)
        created = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        service.resolve_risk_flag(created["id"])
        result, error = service.resolve_risk_flag(created["id"])

        assert result is None
        assert error == "not_active"

    def test_dismiss_risk_flag_non_active_status_fails(self, db_session):
        """Test dismissing risk flag when status is not active fails"""
        service = RiskFlagService(db_session=db_session)
        created = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        service.dismiss_risk_flag(created["id"])
        result, error = service.dismiss_risk_flag(created["id"])

        assert result is None
        assert error == "not_active"

    def test_create_risk_flag_invalid_risk_type_returns_failure(self, db_session):
        """Test creating risk flag with invalid risk_type returns None"""
        service = RiskFlagService(db_session=db_session)
        result = service.create_risk_flag(
            customer_id=1,
            risk_type="invalid_type"
        )

        assert result is None

    def test_create_risk_flag_invalid_risk_level_returns_failure(self, db_session):
        """Test creating risk flag with invalid risk_level returns None"""
        service = RiskFlagService(db_session=db_session)
        result = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment",
            risk_level="invalid_level"
        )

        assert result is None


class TestRiskFlagAuditLogs:
    """Test risk flag audit logging"""

    def test_create_risk_flag_logs_audit(self, db_session):
        """Test creating risk flag writes risk_flag_created audit"""
        service = RiskFlagService(db_session=db_session)
        result = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment",
            risk_level="medium"
        )

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "risk_flag_created"
        ).all()

        assert len(audit_logs) == 1
        assert audit_logs[0].target_id == str(result["id"])
        assert audit_logs[0].detail_json["risk_type"] == "negative_sentiment"
        assert audit_logs[0].detail_json["risk_level"] == "medium"
        assert audit_logs[0].detail_json["status"] == "active"

    def test_resolve_risk_flag_logs_audit(self, db_session):
        """Test resolving risk flag writes risk_flag_resolved audit"""
        service = RiskFlagService(db_session=db_session)
        created = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        result, error = service.resolve_risk_flag(created["id"])

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "risk_flag_resolved"
        ).all()

        assert len(audit_logs) == 1
        assert audit_logs[0].target_id == str(created["id"])
        assert audit_logs[0].detail_json["status"] == "resolved"

    def test_dismiss_risk_flag_logs_audit(self, db_session):
        """Test dismissing risk flag writes risk_flag_dismissed audit"""
        service = RiskFlagService(db_session=db_session)
        created = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        result, error = service.dismiss_risk_flag(created["id"])

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "risk_flag_dismissed"
        ).all()

        assert len(audit_logs) == 1
        assert audit_logs[0].target_id == str(created["id"])
        assert audit_logs[0].detail_json["status"] == "dismissed"

    def test_create_failure_does_not_log_audit(self, db_session):
        """Test creating risk flag with invalid data does not write audit"""
        service = RiskFlagService(db_session=db_session)
        try:
            service.create_risk_flag(
                customer_id=1,
                risk_type="invalid_type"
            )
        except Exception:
            pass

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "risk_flag_created"
        ).all()

        assert len(audit_logs) == 0

    def test_resolve_not_exists_does_not_log_audit(self, db_session):
        """Test resolving non-existent risk flag does not write audit"""
        service = RiskFlagService(db_session=db_session)
        result, error = service.resolve_risk_flag(9999)

        assert error == "not_found"

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "risk_flag_resolved"
        ).all()

        assert len(audit_logs) == 0

    def test_dismiss_not_exists_does_not_log_audit(self, db_session):
        """Test dismissing non-existent risk flag does not write audit"""
        service = RiskFlagService(db_session=db_session)
        result, error = service.dismiss_risk_flag(9999)

        assert error == "not_found"

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "risk_flag_dismissed"
        ).all()

        assert len(audit_logs) == 0

    def test_resolve_non_active_does_not_log_audit(self, db_session):
        """Test resolving risk flag when not active does not write audit"""
        service = RiskFlagService(db_session=db_session)
        created = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        service.resolve_risk_flag(created["id"])
        result, error = service.resolve_risk_flag(created["id"])

        assert error == "not_active"

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "risk_flag_resolved"
        ).all()

        assert len(audit_logs) == 1

    def test_dismiss_non_active_does_not_log_audit(self, db_session):
        """Test dismissing risk flag when not active does not write audit"""
        service = RiskFlagService(db_session=db_session)
        created = service.create_risk_flag(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        service.dismiss_risk_flag(created["id"])
        result, error = service.dismiss_risk_flag(created["id"])

        assert error == "not_active"

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "risk_flag_dismissed"
        ).all()

        assert len(audit_logs) == 1
