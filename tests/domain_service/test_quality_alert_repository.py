"""
Repository-level tests for quality_alert
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.quality_alert import QualityAlert
from domain_models.models.quality_inspection_result import QualityInspectionResult
from domain_models.models.quality_rule import QualityRule
from domain_models.models.customer import Customer
from domain_models.models.conversation import Conversation
from shared_db.base import Base
from app.repositories.quality_alert_repository import QualityAlertRepository


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


class TestQualityAlertRepository:
    """Test quality_alert repository"""

    def test_create_alert(self, db_session, setup_data):
        """Test creating alert"""
        repo = QualityAlertRepository(db_session)
        alert = repo.create(
            quality_inspection_result_id=1,
            alert_level="high"
        )

        assert alert.id is not None
        assert alert.quality_inspection_result_id == 1
        assert alert.alert_level == "high"

    def test_get_by_id_exists(self, db_session, setup_data):
        """Test getting existing alert by id"""
        repo = QualityAlertRepository(db_session)
        created = repo.create(quality_inspection_result_id=1)

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent alert returns None"""
        repo = QualityAlertRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_get_by_result_id(self, db_session, setup_data):
        """Test getting alert by quality_inspection_result_id"""
        repo = QualityAlertRepository(db_session)
        repo.create(quality_inspection_result_id=1)

        result = repo.get_by_result_id(1)
        assert result is not None
        assert result.quality_inspection_result_id == 1

    def test_list_all(self, db_session, setup_data):
        """Test listing all alerts"""
        repo = QualityAlertRepository(db_session)
        repo.create(quality_inspection_result_id=1)

        results = repo.list_all()
        assert len(results) == 1

    def test_exists_for_result_true(self, db_session, setup_data):
        """Test exists_for_result returns True when alert exists"""
        repo = QualityAlertRepository(db_session)
        repo.create(quality_inspection_result_id=1)

        exists = repo.exists_for_result(1)
        assert exists is True

    def test_exists_for_result_false(self, db_session):
        """Test exists_for_result returns False when alert does not exist"""
        repo = QualityAlertRepository(db_session)
        exists = repo.exists_for_result(9999)
        assert exists is False

    def test_unique_result_id(self, db_session, setup_data):
        """Test that quality_inspection_result_id must be unique"""
        repo = QualityAlertRepository(db_session)
        repo.create(quality_inspection_result_id=1)

        with pytest.raises(Exception):
            repo.create(quality_inspection_result_id=1)
