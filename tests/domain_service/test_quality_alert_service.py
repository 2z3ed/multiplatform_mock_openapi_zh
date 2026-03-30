"""
Service-level tests for quality_alert
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
from app.services.quality_alert_service import QualityAlertService


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


class TestQualityAlertService:
    """Test quality_alert service"""

    def test_list_all_empty(self, db_session):
        """Test listing all alerts when none exist"""
        service = QualityAlertService(db_session)
        results = service.list_all()
        assert len(results) == 0

    def test_list_all(self, db_session, setup_data):
        """Test listing all alerts"""
        db_session.add(QualityAlert(quality_inspection_result_id=1, alert_level="high"))
        db_session.commit()

        service = QualityAlertService(db_session)
        results = service.list_all()
        assert len(results) == 1

    def test_get_by_id(self, db_session, setup_data):
        """Test getting alert by id"""
        alert = QualityAlert(quality_inspection_result_id=1, alert_level="high")
        db_session.add(alert)
        db_session.commit()

        service = QualityAlertService(db_session)
        result = service.get_by_id(alert.id)
        assert result is not None
        assert result["id"] == alert.id

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent alert returns None"""
        service = QualityAlertService(db_session)
        result = service.get_by_id(9999)
        assert result is None
