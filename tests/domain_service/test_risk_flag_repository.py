"""
Repository-level tests for risk flag
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.risk_flag import RiskFlag
from domain_models.models.customer import Customer
from domain_models.models.conversation import Conversation
from shared_db.base import Base
from app.repositories.risk_flag_repository import RiskFlagRepository


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


class TestRiskFlagRepository:
    """Test risk flag repository"""

    def test_create_risk_flag(self, db_session):
        """Test creating risk flag"""
        repo = RiskFlagRepository(db=db_session)
        result = repo.create(
            customer_id=1,
            risk_type="negative_sentiment",
            risk_level="medium",
            description="Test description"
        )

        assert result is not None
        assert result.customer_id == 1
        assert result.risk_type == "negative_sentiment"
        assert result.risk_level == "medium"
        assert result.description == "Test description"
        assert result.status == "active"

    def test_create_risk_flag_default_status_active(self, db_session):
        """Test creating risk flag defaults to active status"""
        repo = RiskFlagRepository(db=db_session)
        result = repo.create(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        assert result.status == "active"

    def test_create_risk_flag_default_risk_level_low(self, db_session):
        """Test creating risk flag defaults to low risk level"""
        repo = RiskFlagRepository(db=db_session)
        result = repo.create(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        assert result.risk_level == "low"

    def test_create_risk_flag_conversation_id_nullable(self, db_session):
        """Test creating risk flag allows null conversation_id"""
        repo = RiskFlagRepository(db=db_session)
        result = repo.create(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        assert result.conversation_id is None

    def test_create_risk_flag_description_nullable(self, db_session):
        """Test creating risk flag allows null description"""
        repo = RiskFlagRepository(db=db_session)
        result = repo.create(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        assert result.description is None

    def test_create_risk_flag_extra_json_nullable(self, db_session):
        """Test creating risk flag allows null extra_json"""
        repo = RiskFlagRepository(db=db_session)
        result = repo.create(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        assert result.extra_json is None

    def test_get_by_id_exists(self, db_session):
        """Test getting risk flag by id when exists"""
        repo = RiskFlagRepository(db=db_session)
        created = repo.create(
            customer_id=1,
            risk_type="negative_sentiment"
        )

        result = repo.get_by_id(created.id)

        assert result is not None
        assert result.id == created.id

    def test_get_by_id_not_exists(self, db_session):
        """Test getting risk flag by id when not exists"""
        repo = RiskFlagRepository(db=db_session)
        result = repo.get_by_id(9999)

        assert result is None

    def test_list_by_customer_id(self, db_session):
        """Test listing risk flags by customer_id"""
        repo = RiskFlagRepository(db=db_session)
        repo.create(customer_id=1, risk_type="negative_sentiment")
        repo.create(customer_id=1, risk_type="complaint_tendency")
        repo.create(customer_id=2, risk_type="negative_sentiment")

        results = repo.list_by_customer_id(1)

        assert len(results) == 2

    def test_list_by_customer_id_sorted_by_created_at_desc(self, db_session):
        """Test listing risk flags sorted by created_at desc"""
        from datetime import datetime, timedelta
        
        repo = RiskFlagRepository(db=db_session)
        
        rf1 = RiskFlag(
            customer_id=1,
            risk_type="negative_sentiment",
            risk_level="low",
            status="active"
        )
        rf1.created_at = datetime(2026, 3, 28, 10, 0, 0)
        
        rf2 = RiskFlag(
            customer_id=1,
            risk_type="complaint_tendency",
            risk_level="medium",
            status="active"
        )
        rf2.created_at = datetime(2026, 3, 28, 12, 0, 0)
        
        db_session.add(rf1)
        db_session.add(rf2)
        db_session.commit()

        results = repo.list_by_customer_id(1)

        assert results[0].risk_type == "complaint_tendency"
        assert results[1].risk_type == "negative_sentiment"

    def test_update_status_active_to_resolved(self, db_session):
        """Test updating status from active to resolved"""
        repo = RiskFlagRepository(db=db_session)
        created = repo.create(customer_id=1, risk_type="negative_sentiment")

        result = repo.update_status(created.id, "resolved")

        assert result is not None
        assert result.status == "resolved"

    def test_update_status_active_to_dismissed(self, db_session):
        """Test updating status from active to dismissed"""
        repo = RiskFlagRepository(db=db_session)
        created = repo.create(customer_id=1, risk_type="negative_sentiment")

        result = repo.update_status(created.id, "dismissed")

        assert result is not None
        assert result.status == "dismissed"

    def test_update_status_invalid_status_rejected(self, db_session):
        """Test updating with invalid status is rejected"""
        repo = RiskFlagRepository(db=db_session)
        created = repo.create(customer_id=1, risk_type="negative_sentiment")

        result = repo.update_status(created.id, "invalid_status")

        assert result is None

    def test_create_invalid_risk_type_rejected(self, db_session):
        """Test creating with invalid risk_type is rejected"""
        repo = RiskFlagRepository(db=db_session)
        result = repo.create(
            customer_id=1,
            risk_type="invalid_type"
        )

        assert result is None

    def test_create_invalid_risk_level_rejected(self, db_session):
        """Test creating with invalid risk_level is rejected"""
        repo = RiskFlagRepository(db=db_session)
        result = repo.create(
            customer_id=1,
            risk_type="negative_sentiment",
            risk_level="invalid_level"
        )

        assert result is None
