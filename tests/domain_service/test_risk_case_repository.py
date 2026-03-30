"""
Repository-level tests for risk_case
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.risk_case import RiskCase
from shared_db.base import Base
from app.repositories.risk_case_repository import RiskCaseRepository


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestRiskCaseRepository:
    """Test risk_case repository"""

    def test_create_risk_case(self, db_session):
        """Test creating risk case in database"""
        repo = RiskCaseRepository(db_session)
        risk_case = repo.create(
            conversation_id=1,
            customer_id=1,
            risk_type="complaint_tendency",
            severity="high",
            evidence_json={"reason": "test"}
        )

        assert risk_case.id is not None
        assert risk_case.conversation_id == 1
        assert risk_case.customer_id == 1
        assert risk_case.risk_type == "complaint_tendency"
        assert risk_case.severity == "high"
        assert risk_case.status == "open"

    def test_create_with_minimal_fields(self, db_session):
        """Test creating risk case with minimal fields"""
        repo = RiskCaseRepository(db_session)
        risk_case = repo.create(
            conversation_id=1,
            customer_id=1,
            risk_type="negative_emotion"
        )

        assert risk_case.id is not None
        assert risk_case.severity == "medium"
        assert risk_case.evidence_json is None

    def test_get_by_id_exists(self, db_session):
        """Test getting existing risk case by id"""
        repo = RiskCaseRepository(db_session)
        created = repo.create(
            conversation_id=1,
            customer_id=1,
            risk_type="complaint_tendency"
        )

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent risk case returns None"""
        repo = RiskCaseRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_list_all(self, db_session):
        """Test listing all risk cases"""
        repo = RiskCaseRepository(db_session)
        repo.create(conversation_id=1, customer_id=1, risk_type="complaint_tendency")
        repo.create(conversation_id=2, customer_id=1, risk_type="negative_emotion")

        results = repo.list_all()
        assert len(results) == 2

    def test_list_by_customer(self, db_session):
        """Test listing risk cases by customer_id"""
        repo = RiskCaseRepository(db_session)
        repo.create(conversation_id=1, customer_id=1, risk_type="complaint_tendency")
        repo.create(conversation_id=2, customer_id=1, risk_type="negative_emotion")
        repo.create(conversation_id=3, customer_id=2, risk_type="other")

        results = repo.list_by_customer(1)
        assert len(results) == 2

    def test_update_status(self, db_session):
        """Test updating status"""
        repo = RiskCaseRepository(db_session)
        created = repo.create(
            conversation_id=1,
            customer_id=1,
            risk_type="complaint_tendency"
        )

        assert created.status == "open"

        updated = repo.update_status(created.id, "resolved")
        assert updated.status == "resolved"

    def test_delete(self, db_session):
        """Test deleting risk case"""
        repo = RiskCaseRepository(db_session)
        created = repo.create(
            conversation_id=1,
            customer_id=1,
            risk_type="complaint_tendency"
        )

        success = repo.delete(created.id)
        assert success is True

        result = repo.get_by_id(created.id)
        assert result is None
