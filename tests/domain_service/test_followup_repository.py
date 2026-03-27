"""
Repository-level tests for follow-up task
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.follow_up_task import FollowUpTask
from domain_models.models.customer import Customer
from domain_models.models.conversation import Conversation
from shared_db.base import Base
from app.repositories.followup_task_repository import FollowUpTaskRepository


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
    conversation = Conversation(
        id=1, platform="jd", customer_id=1, status="open", subject="Test"
    )
    db_session.add(conversation)
    db_session.commit()
    return {"customer": customer, "conversation": conversation}


class TestFollowUpTaskRepository:
    """Test follow-up task repository"""

    def test_create_task(self, db_session, setup_data):
        """Test creating task in database"""
        repo = FollowUpTaskRepository(db_session)
        task = repo.create(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task",
            trigger_source="manual",
            conversation_id=1,
            priority="medium"
        )

        assert task.id is not None
        assert task.customer_id == 1
        assert task.task_type == "consultation_no_order"
        assert task.title == "Test Task"
        assert task.status == "pending"
        assert task.priority == "medium"
        assert task.created_at is not None

    def test_create_task_defaults(self, db_session, setup_data):
        """Test default values"""
        repo = FollowUpTaskRepository(db_session)
        task = repo.create(
            customer_id=1,
            task_type="unpaid",
            title="Default Task"
        )

        assert task.status == "pending"
        assert task.priority == "medium"
        assert task.trigger_source == "manual"

    def test_get_by_id_exists(self, db_session, setup_data):
        """Test getting existing task"""
        repo = FollowUpTaskRepository(db_session)
        created = repo.create(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task"
        )

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id
        assert result.title == "Test Task"

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent task returns None"""
        repo = FollowUpTaskRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_list_by_filters_basic(self, db_session, setup_data):
        """Test listing tasks with basic filters"""
        repo = FollowUpTaskRepository(db_session)
        repo.create(customer_id=1, task_type="consultation_no_order", title="Task 1")
        repo.create(customer_id=1, task_type="unpaid", title="Task 2")

        tasks, total = repo.list_by_filters(customer_id=1)
        assert total == 2
        assert len(tasks) == 2

    def test_list_by_filters_pagination(self, db_session, setup_data):
        """Test listing tasks with pagination"""
        repo = FollowUpTaskRepository(db_session)
        for i in range(25):
            repo.create(customer_id=1, task_type="consultation_no_order", title=f"Task {i}")

        tasks, total = repo.list_by_filters(page=1, size=10)
        assert total == 25
        assert len(tasks) == 10

    def test_update_task(self, db_session, setup_data):
        """Test updating task fields"""
        repo = FollowUpTaskRepository(db_session)
        task = repo.create(
            customer_id=1,
            task_type="consultation_no_order",
            title="Original Title"
        )

        result = repo.update(task.id, {"title": "Updated Title", "priority": "high"})
        assert result.title == "Updated Title"
        assert result.priority == "high"
