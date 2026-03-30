"""
Service-level tests for quality_rule
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.quality_rule import QualityRule
from shared_db.base import Base
from app.services.quality_rule_service import QualityRuleService


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestQualityRuleService:
    """Test quality_rule service"""

    def test_create_quality_rule(self, db_session):
        """Test creating quality rule through service"""
        service = QualityRuleService(db_session)
        result = service.create(
            rule_code="RULE001",
            rule_name="Slow Reply Check",
            rule_type="slow_reply",
            severity="high",
            description="Check if agent replies too slowly",
            config_json={"max_reply_minutes": 30}
        )

        assert result is not None
        assert result["rule_code"] == "RULE001"
        assert result["rule_name"] == "Slow Reply Check"
        assert result["rule_type"] == "slow_reply"
        assert result["severity"] == "high"

    def test_create_with_invalid_rule_type(self, db_session):
        """Test creating quality rule with invalid rule_type returns None"""
        service = QualityRuleService(db_session)
        result = service.create(
            rule_code="RULE001",
            rule_name="Invalid Rule",
            rule_type="invalid_type"
        )

        assert result is None

    def test_create_with_invalid_severity(self, db_session):
        """Test creating quality rule with invalid severity returns None"""
        service = QualityRuleService(db_session)
        result = service.create(
            rule_code="RULE001",
            rule_name="Invalid Severity",
            rule_type="slow_reply",
            severity="critical"
        )

        assert result is None

    def test_create_duplicate_rule_code(self, db_session):
        """Test creating quality rule with duplicate rule_code returns None"""
        service = QualityRuleService(db_session)
        service.create(
            rule_code="RULE001",
            rule_name="Rule 1",
            rule_type="slow_reply"
        )

        result = service.create(
            rule_code="RULE001",
            rule_name="Rule 2",
            rule_type="forbidden_word"
        )

        assert result is None

    def test_get_by_id(self, db_session):
        """Test getting quality rule by id"""
        service = QualityRuleService(db_session)
        created = service.create(
            rule_code="RULE001",
            rule_name="Test Rule",
            rule_type="slow_reply"
        )

        result = service.get_by_id(created["id"])
        assert result is not None
        assert result["id"] == created["id"]

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent quality rule returns None"""
        service = QualityRuleService(db_session)
        result = service.get_by_id(9999)
        assert result is None

    def test_get_by_rule_code(self, db_session):
        """Test getting quality rule by rule_code"""
        service = QualityRuleService(db_session)
        service.create(
            rule_code="RULE001",
            rule_name="Test Rule",
            rule_type="slow_reply"
        )

        result = service.get_by_rule_code("RULE001")
        assert result is not None
        assert result["rule_code"] == "RULE001"

    def test_get_by_rule_code_not_exists(self, db_session):
        """Test getting non-existent quality rule by rule_code returns None"""
        service = QualityRuleService(db_session)
        result = service.get_by_rule_code("NONEXISTENT")
        assert result is None

    def test_list_all(self, db_session):
        """Test listing all quality rules"""
        service = QualityRuleService(db_session)
        service.create(rule_code="RULE001", rule_name="Rule 1", rule_type="slow_reply")
        service.create(rule_code="RULE002", rule_name="Rule 2", rule_type="forbidden_word")

        results = service.list_all()
        assert len(results) == 2

    def test_list_by_rule_type(self, db_session):
        """Test listing quality rules by rule_type"""
        service = QualityRuleService(db_session)
        service.create(rule_code="RULE001", rule_name="Rule 1", rule_type="slow_reply")
        service.create(rule_code="RULE002", rule_name="Rule 2", rule_type="slow_reply")
        service.create(rule_code="RULE003", rule_name="Rule 3", rule_type="forbidden_word")

        results = service.list_by_rule_type("slow_reply")
        assert len(results) == 2

    def test_list_by_invalid_rule_type(self, db_session):
        """Test listing quality rules by invalid rule_type returns empty list"""
        service = QualityRuleService(db_session)
        service.create(rule_code="RULE001", rule_name="Rule 1", rule_type="slow_reply")

        results = service.list_by_rule_type("invalid_type")
        assert len(results) == 0
