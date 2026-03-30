"""
Repository-level tests for quality_inspection_result
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.quality_inspection_result import QualityInspectionResult
from domain_models.models.quality_rule import QualityRule
from domain_models.models.customer import Customer
from domain_models.models.conversation import Conversation
from shared_db.base import Base
from app.repositories.quality_inspection_result_repository import QualityInspectionResultRepository


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
    db_session.commit()
    return {"customer": customer, "conversation": conversation, "rule": rule}


class TestQualityInspectionResultRepository:
    """Test quality_inspection_result repository"""

    def test_create_result(self, db_session, setup_data):
        """Test creating inspection result"""
        repo = QualityInspectionResultRepository(db_session)
        result = repo.create(
            conversation_id=1,
            quality_rule_id=1,
            hit=True,
            severity="high",
            evidence_json={"violations": [{"delay_minutes": 45}]},
            inspected_at="2026-03-29T12:00:00Z"
        )

        assert result.id is not None
        assert result.conversation_id == 1
        assert result.quality_rule_id == 1
        assert result.hit is True
        assert result.severity == "high"

    def test_get_by_id_exists(self, db_session, setup_data):
        """Test getting existing result by id"""
        repo = QualityInspectionResultRepository(db_session)
        created = repo.create(
            conversation_id=1,
            quality_rule_id=1,
            hit=True,
            severity="high"
        )

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent result returns None"""
        repo = QualityInspectionResultRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_list_all(self, db_session, setup_data):
        """Test listing all results"""
        repo = QualityInspectionResultRepository(db_session)
        repo.create(conversation_id=1, quality_rule_id=1, hit=True, severity="high")
        repo.create(conversation_id=1, quality_rule_id=1, hit=False, severity="low")

        results = repo.list_all()
        assert len(results) == 2

    def test_list_by_conversation(self, db_session, setup_data):
        """Test listing results by conversation_id"""
        repo = QualityInspectionResultRepository(db_session)
        repo.create(conversation_id=1, quality_rule_id=1, hit=True, severity="high")
        repo.create(conversation_id=1, quality_rule_id=1, hit=False, severity="low")

        results = repo.list_by_conversation(1)
        assert len(results) == 2

    def test_list_by_rule(self, db_session, setup_data):
        """Test listing results by quality_rule_id"""
        repo = QualityInspectionResultRepository(db_session)
        repo.create(conversation_id=1, quality_rule_id=1, hit=True, severity="high")

        results = repo.list_by_rule(1)
        assert len(results) == 1

    def test_list_hit_only(self, db_session, setup_data):
        """Test listing only hit results"""
        repo = QualityInspectionResultRepository(db_session)
        repo.create(conversation_id=1, quality_rule_id=1, hit=True, severity="high")
        repo.create(conversation_id=1, quality_rule_id=1, hit=False, severity="low")

        results = repo.list_hit_only()
        assert len(results) == 1
        assert results[0].hit is True

    def test_list_high_severity_hit(self, db_session, setup_data):
        """Test listing high severity hit results"""
        repo = QualityInspectionResultRepository(db_session)
        repo.create(conversation_id=1, quality_rule_id=1, hit=True, severity="high")
        repo.create(conversation_id=1, quality_rule_id=1, hit=True, severity="low")
        repo.create(conversation_id=1, quality_rule_id=1, hit=False, severity="high")

        results = repo.list_high_severity_hit()
        assert len(results) == 1
        assert results[0].hit is True
        assert results[0].severity == "high"
