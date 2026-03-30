"""
Service-level tests for quality_inspection
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.quality_rule import QualityRule
from domain_models.models.quality_inspection_result import QualityInspectionResult
from domain_models.models.quality_alert import QualityAlert
from domain_models.models.customer import Customer
from domain_models.models.conversation import Conversation
from domain_models.models.message import Message
from shared_db.base import Base
from app.services.quality_inspection_service import QualityInspectionService


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
    db_session.commit()
    return {"customer": customer, "conversation": conversation}


class TestQualityInspectionService:
    """Test quality_inspection service"""

    def test_inspect_conversation_no_rules(self, db_session, setup_data):
        """Test inspection when no rules exist"""
        service = QualityInspectionService(db_session)
        results = service.inspect_conversation(1)
        assert len(results) == 0

    def test_inspect_conversation_slow_reply_hit(self, db_session, setup_data):
        """Test slow_reply rule hit"""
        rule = QualityRule(
            rule_code="RULE001",
            rule_name="Slow Reply",
            rule_type="slow_reply",
            severity="high",
            config_json={"max_reply_minutes": 30}
        )
        db_session.add(rule)
        db_session.commit()

        now = datetime.utcnow()
        customer_msg = Message(
            conversation_id=1,
            sender_type="customer",
            content="Hello",
            sent_at=now - timedelta(minutes=45)
        )
        agent_msg = Message(
            conversation_id=1,
            sender_type="agent",
            content="Hi there",
            sent_at=now - timedelta(minutes=10)
        )
        db_session.add(customer_msg)
        db_session.add(agent_msg)
        db_session.commit()

        service = QualityInspectionService(db_session)
        results = service.inspect_conversation(1)

        assert len(results) == 1
        assert results[0]["hit"] is True
        assert results[0]["severity"] == "high"

    def test_inspect_conversation_slow_reply_no_hit(self, db_session, setup_data):
        """Test slow_reply rule no hit"""
        rule = QualityRule(
            rule_code="RULE001",
            rule_name="Slow Reply",
            rule_type="slow_reply",
            severity="medium",
            config_json={"max_reply_minutes": 60}
        )
        db_session.add(rule)
        db_session.commit()

        now = datetime.utcnow()
        customer_msg = Message(
            conversation_id=1,
            sender_type="customer",
            content="Hello",
            sent_at=now - timedelta(minutes=30)
        )
        agent_msg = Message(
            conversation_id=1,
            sender_type="agent",
            content="Hi there",
            sent_at=now - timedelta(minutes=25)
        )
        db_session.add(customer_msg)
        db_session.add(agent_msg)
        db_session.commit()

        service = QualityInspectionService(db_session)
        results = service.inspect_conversation(1)

        assert len(results) == 1
        assert results[0]["hit"] is False

    def test_inspect_conversation_forbidden_word_hit(self, db_session, setup_data):
        """Test forbidden_word rule hit"""
        rule = QualityRule(
            rule_code="RULE002",
            rule_name="Forbidden Words",
            rule_type="forbidden_word",
            severity="high",
            config_json={"words": ["stupid", "idiot"]}
        )
        db_session.add(rule)
        db_session.commit()

        now = datetime.utcnow()
        agent_msg = Message(
            conversation_id=1,
            sender_type="agent",
            content="You are so stupid!",
            sent_at=now
        )
        db_session.add(agent_msg)
        db_session.commit()

        service = QualityInspectionService(db_session)
        results = service.inspect_conversation(1)

        assert len(results) == 1
        assert results[0]["hit"] is True

    def test_inspect_conversation_forbidden_word_no_hit(self, db_session, setup_data):
        """Test forbidden_word rule no hit"""
        rule = QualityRule(
            rule_code="RULE002",
            rule_name="Forbidden Words",
            rule_type="forbidden_word",
            severity="medium",
            config_json={"words": ["stupid", "idiot"]}
        )
        db_session.add(rule)
        db_session.commit()

        now = datetime.utcnow()
        agent_msg = Message(
            conversation_id=1,
            sender_type="agent",
            content="Thank you for your patience!",
            sent_at=now
        )
        db_session.add(agent_msg)
        db_session.commit()

        service = QualityInspectionService(db_session)
        results = service.inspect_conversation(1)

        assert len(results) == 1
        assert results[0]["hit"] is False

    def test_high_severity_hit_creates_alert(self, db_session, setup_data):
        """Test that high severity hit creates alert"""
        rule = QualityRule(
            rule_code="RULE001",
            rule_name="Slow Reply",
            rule_type="slow_reply",
            severity="high",
            config_json={"max_reply_minutes": 30}
        )
        db_session.add(rule)
        db_session.commit()

        now = datetime.utcnow()
        customer_msg = Message(
            conversation_id=1,
            sender_type="customer",
            content="Hello",
            sent_at=now - timedelta(minutes=45)
        )
        agent_msg = Message(
            conversation_id=1,
            sender_type="agent",
            content="Hi there",
            sent_at=now - timedelta(minutes=10)
        )
        db_session.add(customer_msg)
        db_session.add(agent_msg)
        db_session.commit()

        service = QualityInspectionService(db_session)
        results = service.inspect_conversation(1)

        assert len(results) == 1
        assert results[0]["hit"] is True

        alerts = db_session.query(QualityAlert).all()
        assert len(alerts) == 1
        assert alerts[0].alert_level == "high"

    def test_low_severity_hit_no_alert(self, db_session, setup_data):
        """Test that low severity hit does not create alert"""
        rule = QualityRule(
            rule_code="RULE001",
            rule_name="Slow Reply",
            rule_type="slow_reply",
            severity="low",
            config_json={"max_reply_minutes": 30}
        )
        db_session.add(rule)
        db_session.commit()

        now = datetime.utcnow()
        customer_msg = Message(
            conversation_id=1,
            sender_type="customer",
            content="Hello",
            sent_at=now - timedelta(minutes=45)
        )
        agent_msg = Message(
            conversation_id=1,
            sender_type="agent",
            content="Hi there",
            sent_at=now - timedelta(minutes=10)
        )
        db_session.add(customer_msg)
        db_session.add(agent_msg)
        db_session.commit()

        service = QualityInspectionService(db_session)
        results = service.inspect_conversation(1)

        assert len(results) == 1
        assert results[0]["hit"] is True

        alerts = db_session.query(QualityAlert).all()
        assert len(alerts) == 0
