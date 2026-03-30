"""
Repository-level tests for training_case
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.training_case import TrainingCase
from shared_db.base import Base
from app.repositories.training_case_repository import TrainingCaseRepository


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestTrainingCaseRepository:
    """Test training_case repository"""

    def test_create_training_case(self, db_session):
        """Test creating training case in database"""
        repo = TrainingCaseRepository(db_session)
        case = repo.create(
            case_title="高效处理客户投诉案例",
            case_type="good"
        )

        assert case.id is not None
        assert case.case_title == "高效处理客户投诉案例"
        assert case.case_type == "good"

    def test_create_with_foreign_keys(self, db_session):
        """Test creating training case with foreign keys"""
        repo = TrainingCaseRepository(db_session)
        case = repo.create(
            case_title="关联会话案例",
            case_type="typical",
            conversation_id=1,
            customer_id=100
        )

        assert case.id is not None
        assert case.conversation_id == 1
        assert case.customer_id == 100

    def test_create_with_null_foreign_keys(self, db_session):
        """Test creating training case with null foreign keys"""
        repo = TrainingCaseRepository(db_session)
        case = repo.create(
            case_title="独立案例",
            case_type="edge_case",
            conversation_id=None,
            customer_id=None
        )

        assert case.id is not None
        assert case.conversation_id is None
        assert case.customer_id is None

    def test_get_by_id_exists(self, db_session):
        """Test getting existing case by id"""
        repo = TrainingCaseRepository(db_session)
        created = repo.create(
            case_title="测试案例",
            case_type="good"
        )

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent case returns None"""
        repo = TrainingCaseRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_list_all(self, db_session):
        """Test listing all cases"""
        repo = TrainingCaseRepository(db_session)
        repo.create(case_title="案例1", case_type="good")
        repo.create(case_title="案例2", case_type="bad")

        results = repo.list_all()
        assert len(results) == 2

    def test_list_by_case_type(self, db_session):
        """Test listing cases by case_type"""
        repo = TrainingCaseRepository(db_session)
        repo.create(case_title="案例1", case_type="good")
        repo.create(case_title="案例2", case_type="bad")
        repo.create(case_title="案例3", case_type="good")

        results = repo.list_by_case_type("good")
        assert len(results) == 2

    def test_delete(self, db_session):
        """Test deleting case"""
        repo = TrainingCaseRepository(db_session)
        created = repo.create(
            case_title="待删除案例",
            case_type="typical"
        )

        success = repo.delete(created.id)
        assert success is True

        result = repo.get_by_id(created.id)
        assert result is None
