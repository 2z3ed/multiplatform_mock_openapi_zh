"""
API-level tests for follow-up task endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.follow_up_task import FollowUpTask
from domain_models.models.customer import Customer
from domain_models.models.conversation import Conversation
from shared_db.base import Base
from app.main import app
from app.api.followup import get_followup_service
from app.services.followup_service import FollowUpTaskService


TEST_DB_URL = "sqlite:///test.db"


@pytest.fixture
def db_session():
    import os
    if os.path.exists("test.db"):
        os.remove("test.db")
    from domain_models.models import (
        Customer, Conversation, Message, OrderSnapshot, ShipmentSnapshot,
        AfterSaleCase, KBDocument, KBChunk, AISuggestion, AuditLog, FollowUpTask
    )
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    if os.path.exists("test.db"):
        os.remove("test.db")


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


@pytest.fixture
def test_client(db_session, setup_data):
    from app.main import app
    from app.api.followup import get_followup_service
    from app.services.followup_service import FollowUpTaskService

    def override_get_followup_service():
        return FollowUpTaskService(db_session=db_session)

    app.dependency_overrides[get_followup_service] = override_get_followup_service
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


class TestFollowUpTaskAPI:
    """Test follow-up task API endpoints"""

    def test_create_task_success(self, test_client, setup_data):
        """Test POST /api/follow-up/tasks creates task"""
        response = test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "consultation_no_order",
                "title": "Test Task"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == 1
        assert data["task_type"] == "consultation_no_order"
        assert data["status"] == "pending"

    def test_create_task_invalid_params(self, test_client, setup_data):
        """Test POST with invalid params returns 400"""
        response = test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "invalid_type",
                "title": "Test Task"
            }
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid task parameters"

    def test_get_task_success(self, test_client, setup_data):
        """Test GET /api/follow-up/tasks/{id} returns task"""
        create_resp = test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "consultation_no_order",
                "title": "Test Task"
            }
        )
        task_id = create_resp.json()["id"]

        response = test_client.get(f"/api/follow-up/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["id"] == task_id

    def test_get_task_not_found(self, test_client):
        """Test GET non-existent task returns 404"""
        response = test_client.get("/api/follow-up/tasks/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    def test_list_tasks_pagination(self, test_client, setup_data):
        """Test GET /api/follow-up/tasks returns paginated results"""
        for i in range(25):
            test_client.post(
                "/api/follow-up/tasks",
                json={
                    "customer_id": 1,
                    "task_type": "consultation_no_order",
                    "title": f"Task {i}"
                }
            )

        response = test_client.get("/api/follow-up/tasks?page=1&size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 25
        assert data["page"] == 1
        assert data["size"] == 10

    def test_list_tasks_invalid_status_returns_empty(self, test_client, setup_data):
        """Test GET with invalid status returns empty"""
        test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "consultation_no_order",
                "title": "Test Task"
            }
        )

        response = test_client.get("/api/follow-up/tasks?status=invalid_status")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_tasks_invalid_priority_returns_empty(self, test_client, setup_data):
        """Test GET with invalid priority returns empty"""
        test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "consultation_no_order",
                "title": "Test Task"
            }
        )

        response = test_client.get("/api/follow-up/tasks?priority=invalid")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_tasks_invalid_task_type_returns_empty(self, test_client, setup_data):
        """Test GET with invalid task_type returns empty"""
        test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "consultation_no_order",
                "title": "Test Task"
            }
        )

        response = test_client.get("/api/follow-up/tasks?task_type=invalid_type")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_update_task_success(self, test_client, setup_data):
        """Test PATCH /api/follow-up/tasks/{id} updates task"""
        create_resp = test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "consultation_no_order",
                "title": "Original Title"
            }
        )
        task_id = create_resp.json()["id"]

        response = test_client.patch(
            f"/api/follow-up/tasks/{task_id}",
            json={"title": "Updated Title", "priority": "high"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["priority"] == "high"

    def test_update_task_not_found(self, test_client):
        """Test PATCH non-existent task returns 404"""
        response = test_client.patch(
            "/api/follow-up/tasks/9999",
            json={"title": "Updated Title"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    def test_update_task_empty_update(self, test_client, setup_data):
        """Test PATCH with empty update returns 400"""
        create_resp = test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "consultation_no_order",
                "title": "Test Task"
            }
        )
        task_id = create_resp.json()["id"]

        response = test_client.patch(
            f"/api/follow-up/tasks/{task_id}",
            json={}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "No valid fields to update"

    def test_update_task_invalid_priority(self, test_client, setup_data):
        """Test PATCH with invalid priority returns 400"""
        create_resp = test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "consultation_no_order",
                "title": "Test Task"
            }
        )
        task_id = create_resp.json()["id"]

        response = test_client.patch(
            f"/api/follow-up/tasks/{task_id}",
            json={"priority": "invalid"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid priority value"

    def test_update_task_reject_lifecycle_fields(self, test_client, setup_data):
        """Test PATCH ignores lifecycle fields in request"""
        create_resp = test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "consultation_no_order",
                "title": "Test Task"
            }
        )
        task_id = create_resp.json()["id"]

        response = test_client.patch(
            f"/api/follow-up/tasks/{task_id}",
            json={
                "title": "Updated Title",
                "status": "completed",
                "completed_by": "agent_001"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "pending"
        assert data["completed_by"] is None

    def test_update_task_only_lifecycle_fields_returns_400(self, test_client, setup_data):
        """Test PATCH with only lifecycle fields returns 400"""
        create_resp = test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "consultation_no_order",
                "title": "Test Task"
            }
        )
        task_id = create_resp.json()["id"]

        response = test_client.patch(
            f"/api/follow-up/tasks/{task_id}",
            json={
                "status": "completed",
                "completed_by": "agent_001"
            }
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "No valid fields to update"

    def test_execute_task_success(self, test_client, setup_data):
        """Test POST /api/follow-up/tasks/{id}/execute executes task"""
        create_resp = test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "consultation_no_order",
                "title": "Test Task"
            }
        )
        task_id = create_resp.json()["id"]

        response = test_client.post(
            f"/api/follow-up/tasks/{task_id}/execute",
            json={"completed_by": "agent_001"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_by"] == "agent_001"

    def test_execute_task_not_found(self, test_client):
        """Test POST execute non-existent task returns 404"""
        response = test_client.post(
            "/api/follow-up/tasks/9999/execute",
            json={"completed_by": "agent_001"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    def test_execute_task_not_pending(self, test_client, setup_data):
        """Test POST execute non-pending task returns 400"""
        create_resp = test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "consultation_no_order",
                "title": "Test Task"
            }
        )
        task_id = create_resp.json()["id"]

        test_client.post(
            f"/api/follow-up/tasks/{task_id}/execute",
            json={"completed_by": "agent_001"}
        )

        response = test_client.post(
            f"/api/follow-up/tasks/{task_id}/execute",
            json={"completed_by": "agent_001"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Task is not in pending status"

    def test_close_task_success(self, test_client, setup_data):
        """Test POST /api/follow-up/tasks/{id}/close closes task"""
        create_resp = test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "consultation_no_order",
                "title": "Test Task"
            }
        )
        task_id = create_resp.json()["id"]

        response = test_client.post(
            f"/api/follow-up/tasks/{task_id}/close",
            json={"completed_by": "agent_001"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "closed"
        assert data["completed_by"] == "agent_001"

    def test_close_task_not_found(self, test_client):
        """Test POST close non-existent task returns 404"""
        response = test_client.post(
            "/api/follow-up/tasks/9999/close",
            json={"completed_by": "agent_001"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    def test_close_task_not_pending(self, test_client, setup_data):
        """Test POST close non-pending task returns 400"""
        create_resp = test_client.post(
            "/api/follow-up/tasks",
            json={
                "customer_id": 1,
                "task_type": "consultation_no_order",
                "title": "Test Task"
            }
        )
        task_id = create_resp.json()["id"]

        test_client.post(
            f"/api/follow-up/tasks/{task_id}/close",
            json={"completed_by": "agent_001"}
        )

        response = test_client.post(
            f"/api/follow-up/tasks/{task_id}/close",
            json={"completed_by": "agent_001"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Task is not in pending status"
