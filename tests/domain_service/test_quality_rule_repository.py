"""
Repository-level tests for quality_rule
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.quality_rule import QualityRule
from shared_db.base import Base
from app.repositories.quality_rule_repository import QualityRuleRepository


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestQualityRuleRepository:
    """Test quality_rule repository"""

    def test_create_quality_rule(self, db_session):
        """Test creating quality rule in database"""
        repo = QualityRuleRepository(db_session)
        rule = repo.create(
            rule_code="RULE001",
            rule_name="Slow Reply Check",
            rule_type="slow_reply",
            severity="medium",
            description="Check if agent replies too slowly",
            config_json={"max_reply_minutes": 30}
        )

        assert rule.id is not None
        assert rule.rule_code == "RULE001"
        assert rule.rule_name == "Slow Reply Check"
        assert rule.rule_type == "slow_reply"
        assert rule.severity == "medium"
        assert rule.config_json == {"max_reply_minutes": 30}
        assert rule.created_at is not None

    def test_create_with_minimal_fields(self, db_session):
        """Test creating quality rule with minimal fields"""
        repo = QualityRuleRepository(db_session)
        rule = repo.create(
            rule_code="RULE002",
            rule_name="Forbidden Word Check",
            rule_type="forbidden_word"
        )

        assert rule.id is not None
        assert rule.severity == "medium"
        assert rule.description is None
        assert rule.config_json is None

    def test_get_by_id_exists(self, db_session):
        """Test getting existing quality rule by id"""
        repo = QualityRuleRepository(db_session)
        created = repo.create(
            rule_code="RULE001",
            rule_name="Test Rule",
            rule_type="slow_reply"
        )

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id
        assert result.rule_code == "RULE001"

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent quality rule returns None"""
        repo = QualityRuleRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_get_by_rule_code_exists(self, db_session):
        """Test getting existing quality rule by rule_code"""
        repo = QualityRuleRepository(db_session)
        repo.create(
            rule_code="RULE001",
            rule_name="Test Rule",
            rule_type="slow_reply"
        )

        result = repo.get_by_rule_code("RULE001")
        assert result is not None
        assert result.rule_code == "RULE001"

    def test_get_by_rule_code_not_exists(self, db_session):
        """Test getting non-existent quality rule by rule_code returns None"""
        repo = QualityRuleRepository(db_session)
        result = repo.get_by_rule_code("NONEXISTENT")
        assert result is None

    def test_list_all(self, db_session):
        """Test listing all quality rules"""
        repo = QualityRuleRepository(db_session)
        repo.create(rule_code="RULE001", rule_name="Rule 1", rule_type="slow_reply")
        repo.create(rule_code="RULE002", rule_name="Rule 2", rule_type="forbidden_word")
        repo.create(rule_code="RULE003", rule_name="Rule 3", rule_type="missed_response")

        results = repo.list_all()
        assert len(results) == 3
        rule_codes = [r.rule_code for r in results]
        assert "RULE001" in rule_codes
        assert "RULE002" in rule_codes
        assert "RULE003" in rule_codes

    def test_list_all_empty(self, db_session):
        """Test listing quality rules when none exist"""
        repo = QualityRuleRepository(db_session)
        results = repo.list_all()
        assert len(results) == 0

    def test_list_by_rule_type(self, db_session):
        """Test listing quality rules by rule_type"""
        repo = QualityRuleRepository(db_session)
        repo.create(rule_code="RULE001", rule_name="Rule 1", rule_type="slow_reply")
        repo.create(rule_code="RULE002", rule_name="Rule 2", rule_type="slow_reply")
        repo.create(rule_code="RULE003", rule_name="Rule 3", rule_type="forbidden_word")

        results = repo.list_by_rule_type("slow_reply")
        assert len(results) == 2
        assert all(r.rule_type == "slow_reply" for r in results)

    def test_unique_rule_code(self, db_session):
        """Test that rule_code must be unique"""
        repo = QualityRuleRepository(db_session)
        repo.create(rule_code="RULE001", rule_name="Rule 1", rule_type="slow_reply")

        with pytest.raises(Exception):
            repo.create(rule_code="RULE001", rule_name="Rule 2", rule_type="forbidden_word")
