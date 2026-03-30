"""
Service-level tests for risk_case
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.risk_case import RiskCase
from shared_db.base import Base
from app.services.risk_case_service import RiskCaseService, InvalidStateTransitionError


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestRiskCaseService:
    """Test risk_case service"""

    def test_create_risk_case(self, db_session):
        """Test creating risk case through service"""
        service = RiskCaseService(db_session)
        result = service.create(
            conversation_id=1,
            customer_id=1,
            risk_type="complaint_tendency",
            severity="high",
            evidence_json={"reason": "test"}
        )

        assert result is not None
        assert result["risk_type"] == "complaint_tendency"
        assert result["severity"] == "high"
        assert result["status"] == "open"

    def test_create_with_invalid_risk_type(self, db_session):
        """Test creating risk case with invalid risk_type returns None"""
        service = RiskCaseService(db_session)
        result = service.create(
            conversation_id=1,
            customer_id=1,
            risk_type="invalid_type"
        )

        assert result is None

    def test_create_with_invalid_severity(self, db_session):
        """Test creating risk case with invalid severity returns None"""
        service = RiskCaseService(db_session)
        result = service.create(
            conversation_id=1,
            customer_id=1,
            risk_type="complaint_tendency",
            severity="critical"
        )

        assert result is None

    def test_resolve_open_case(self, db_session):
        """Test resolving open risk case"""
        service = RiskCaseService(db_session)
        created = service.create(
            conversation_id=1,
            customer_id=1,
            risk_type="complaint_tendency"
        )

        result = service.resolve(created["id"])
        assert result is not None
        assert result["status"] == "resolved"

    def test_dismiss_open_case(self, db_session):
        """Test dismissing open risk case"""
        service = RiskCaseService(db_session)
        created = service.create(
            conversation_id=1,
            customer_id=1,
            risk_type="complaint_tendency"
        )

        result = service.dismiss(created["id"])
        assert result is not None
        assert result["status"] == "dismissed"

    def test_escalate_open_case(self, db_session):
        """Test escalating open risk case"""
        service = RiskCaseService(db_session)
        created = service.create(
            conversation_id=1,
            customer_id=1,
            risk_type="complaint_tendency"
        )

        result = service.escalate(created["id"])
        assert result is not None
        assert result["status"] == "escalated"

    def test_resolve_non_open_case_fails(self, db_session):
        """Test that resolving non-open case raises error"""
        service = RiskCaseService(db_session)
        created = service.create(
            conversation_id=1,
            customer_id=1,
            risk_type="complaint_tendency"
        )

        service.resolve(created["id"])

        with pytest.raises(InvalidStateTransitionError):
            service.resolve(created["id"])

    def test_dismiss_non_open_case_fails(self, db_session):
        """Test that dismissing non-open case raises error"""
        service = RiskCaseService(db_session)
        created = service.create(
            conversation_id=1,
            customer_id=1,
            risk_type="complaint_tendency"
        )

        service.dismiss(created["id"])

        with pytest.raises(InvalidStateTransitionError):
            service.dismiss(created["id"])

    def test_escalate_non_open_case_fails(self, db_session):
        """Test that escalating non-open case raises error"""
        service = RiskCaseService(db_session)
        created = service.create(
            conversation_id=1,
            customer_id=1,
            risk_type="complaint_tendency"
        )

        service.escalate(created["id"])

        with pytest.raises(InvalidStateTransitionError):
            service.escalate(created["id"])

    def test_get_by_id(self, db_session):
        """Test getting risk case by id"""
        service = RiskCaseService(db_session)
        created = service.create(
            conversation_id=1,
            customer_id=1,
            risk_type="complaint_tendency"
        )

        result = service.get_by_id(created["id"])
        assert result is not None
        assert result["id"] == created["id"]

    def test_list_all(self, db_session):
        """Test listing all risk cases"""
        service = RiskCaseService(db_session)
        service.create(conversation_id=1, customer_id=1, risk_type="complaint_tendency")
        service.create(conversation_id=2, customer_id=1, risk_type="negative_emotion")

        results = service.list_all()
        assert len(results) == 2
