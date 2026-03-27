"""
Service-level tests for follow-up task
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.follow_up_task import FollowUpTask
from domain_models.models.customer import Customer
from domain_models.models.conversation import Conversation
from shared_db.base import Base
from app.services.followup_service import FollowUpTaskService


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


class TestFollowUpTaskService:
    """Test follow-up task service"""

    def test_create_task_success(self, db_session, setup_data):
        """Test creating task successfully"""
        service = FollowUpTaskService(db_session=db_session)
        result = service.create_task(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task"
        )

        assert result is not None
        assert result["customer_id"] == 1
        assert result["task_type"] == "consultation_no_order"
        assert result["title"] == "Test Task"
        assert result["status"] == "pending"

    def test_create_task_invalid_task_type(self, db_session, setup_data):
        """Test creating task with invalid task_type returns None"""
        service = FollowUpTaskService(db_session=db_session)
        result = service.create_task(
            customer_id=1,
            task_type="invalid_type",
            title="Test Task"
        )
        assert result is None

    def test_create_task_invalid_priority(self, db_session, setup_data):
        """Test creating task with invalid priority returns None"""
        service = FollowUpTaskService(db_session=db_session)
        result = service.create_task(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task",
            priority="invalid_priority"
        )
        assert result is None

    def test_create_task_invalid_trigger_source(self, db_session, setup_data):
        """Test creating task with invalid trigger_source returns None"""
        service = FollowUpTaskService(db_session=db_session)
        result = service.create_task(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task",
            trigger_source="invalid_source"
        )
        assert result is None

    def test_get_task_exists(self, db_session, setup_data):
        """Test getting existing task"""
        service = FollowUpTaskService(db_session=db_session)
        created = service.create_task(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task"
        )

        result = service.get_task(created["id"])
        assert result is not None
        assert result["id"] == created["id"]

    def test_get_task_not_exists(self, db_session):
        """Test getting non-existent task returns None"""
        service = FollowUpTaskService(db_session=db_session)
        result = service.get_task(9999)
        assert result is None

    def test_list_tasks_pagination(self, db_session, setup_data):
        """Test listing tasks with pagination"""
        service = FollowUpTaskService(db_session=db_session)
        for i in range(25):
            service.create_task(
                customer_id=1,
                task_type="consultation_no_order",
                title=f"Task {i}"
            )

        items, total = service.list_tasks(page=1, size=10)
        assert total == 25
        assert len(items) == 10

    def test_list_tasks_invalid_status_returns_empty(self, db_session, setup_data):
        """Test listing with invalid status returns empty"""
        service = FollowUpTaskService(db_session=db_session)
        service.create_task(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task"
        )

        items, total = service.list_tasks(status="invalid_status")
        assert items == []
        assert total == 0

    def test_list_tasks_invalid_priority_returns_empty(self, db_session, setup_data):
        """Test listing with invalid priority returns empty"""
        service = FollowUpTaskService(db_session=db_session)
        service.create_task(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task"
        )

        items, total = service.list_tasks(priority="invalid_priority")
        assert items == []
        assert total == 0

    def test_list_tasks_invalid_task_type_returns_empty(self, db_session, setup_data):
        """Test listing with invalid task_type returns empty"""
        service = FollowUpTaskService(db_session=db_session)
        service.create_task(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task"
        )

        items, total = service.list_tasks(task_type="invalid_type")
        assert items == []
        assert total == 0

    def test_update_task_success(self, db_session, setup_data):
        """Test updating task successfully"""
        service = FollowUpTaskService(db_session=db_session)
        created = service.create_task(
            customer_id=1,
            task_type="consultation_no_order",
            title="Original Title"
        )

        result = service.update_task(created["id"], {"title": "Updated Title", "priority": "high"})
        assert result is not None
        assert result["title"] == "Updated Title"
        assert result["priority"] == "high"

    def test_update_task_empty_updates(self, db_session, setup_data):
        """Test updating with empty updates returns None"""
        service = FollowUpTaskService(db_session=db_session)
        created = service.create_task(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task"
        )

        result = service.update_task(created["id"], {})
        assert result is None

    def test_update_task_invalid_priority(self, db_session, setup_data):
        """Test updating with invalid priority returns None"""
        service = FollowUpTaskService(db_session=db_session)
        created = service.create_task(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task"
        )

        result = service.update_task(created["id"], {"priority": "invalid"})
        assert result is None

    def test_execute_task_success(self, db_session, setup_data):
        """Test executing pending task successfully"""
        service = FollowUpTaskService(db_session=db_session)
        created = service.create_task(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task"
        )

        result = service.execute_task(created["id"], "agent_001")
        assert result is not None
        assert result["status"] == "completed"
        assert result["completed_by"] == "agent_001"
        assert result["completed_at"] is not None

    def test_execute_task_not_pending(self, db_session, setup_data):
        """Test executing non-pending task returns None"""
        service = FollowUpTaskService(db_session=db_session)
        created = service.create_task(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task"
        )
        service.execute_task(created["id"], "agent_001")

        result = service.execute_task(created["id"], "agent_001")
        assert result is None

    def test_execute_task_not_exists(self, db_session):
        """Test executing non-existent task returns None"""
        service = FollowUpTaskService(db_session=db_session)
        result = service.execute_task(9999, "agent_001")
        assert result is None

    def test_close_task_success(self, db_session, setup_data):
        """Test closing pending task successfully"""
        service = FollowUpTaskService(db_session=db_session)
        created = service.create_task(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task"
        )

        result = service.close_task(created["id"], "agent_001")
        assert result is not None
        assert result["status"] == "closed"
        assert result["completed_by"] == "agent_001"

    def test_close_task_not_pending(self, db_session, setup_data):
        """Test closing non-pending task returns None"""
        service = FollowUpTaskService(db_session=db_session)
        created = service.create_task(
            customer_id=1,
            task_type="consultation_no_order",
            title="Test Task"
        )
        service.close_task(created["id"], "agent_001")

        result = service.close_task(created["id"], "agent_001")
        assert result is None

    def test_close_task_not_exists(self, db_session):
        """Test closing non-existent task returns None"""
        service = FollowUpTaskService(db_session=db_session)
        result = service.close_task(9999, "agent_001")
        assert result is None
