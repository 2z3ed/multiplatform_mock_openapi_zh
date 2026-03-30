"""
Repository-level tests for training_task
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.training_task import TrainingTask
from shared_db.base import Base
from app.repositories.training_task_repository import TrainingTaskRepository


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestTrainingTaskRepository:
    """Test training_task repository"""

    def test_create_training_task(self, db_session):
        """Test creating training task in database"""
        repo = TrainingTaskRepository(db_session)
        task = repo.create(
            task_name="投诉处理流程复习",
            task_type="review"
        )

        assert task.id is not None
        assert task.task_name == "投诉处理流程复习"
        assert task.task_type == "review"
        assert task.status == "pending"

    def test_create_with_status(self, db_session):
        """Test creating training task with status"""
        repo = TrainingTaskRepository(db_session)
        task = repo.create(
            task_name="产品知识测验",
            task_type="quiz",
            status="in_progress"
        )

        assert task.id is not None
        assert task.status == "in_progress"

    def test_create_with_related_case_id(self, db_session):
        """Test creating training task with related_case_id"""
        repo = TrainingTaskRepository(db_session)
        task = repo.create(
            task_name="关联案例任务",
            task_type="practice",
            related_case_id=1
        )

        assert task.id is not None
        assert task.related_case_id == 1

    def test_create_with_null_related_case_id(self, db_session):
        """Test creating training task with null related_case_id"""
        repo = TrainingTaskRepository(db_session)
        task = repo.create(
            task_name="独立任务",
            task_type="quiz",
            related_case_id=None
        )

        assert task.id is not None
        assert task.related_case_id is None

    def test_get_by_id_exists(self, db_session):
        """Test getting existing task by id"""
        repo = TrainingTaskRepository(db_session)
        created = repo.create(
            task_name="测试任务",
            task_type="review"
        )

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent task returns None"""
        repo = TrainingTaskRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_list_all(self, db_session):
        """Test listing all tasks"""
        repo = TrainingTaskRepository(db_session)
        repo.create(task_name="任务1", task_type="review")
        repo.create(task_name="任务2", task_type="practice")

        results = repo.list_all()
        assert len(results) == 2

    def test_list_by_status(self, db_session):
        """Test listing tasks by status"""
        repo = TrainingTaskRepository(db_session)
        repo.create(task_name="任务1", task_type="review", status="pending")
        repo.create(task_name="任务2", task_type="practice", status="completed")
        repo.create(task_name="任务3", task_type="quiz", status="pending")

        results = repo.list_by_status("pending")
        assert len(results) == 2

    def test_delete(self, db_session):
        """Test deleting task"""
        repo = TrainingTaskRepository(db_session)
        created = repo.create(
            task_name="待删除任务",
            task_type="review"
        )

        success = repo.delete(created.id)
        assert success is True

        result = repo.get_by_id(created.id)
        assert result is None
