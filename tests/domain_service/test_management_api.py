"""
API-level tests for management endpoints
"""

import os
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models import (
    Customer, Conversation, Message, OrderSnapshot, ShipmentSnapshot,
    AfterSaleCase, KBDocument, KBChunk, AISuggestion, AuditLog, FollowUpTask,
    CustomerTag, CustomerProfile, Recommendation, QualityRule, QualityInspectionResult, QualityAlert,
    RiskCase, BlacklistCustomer,
    ERPInventorySnapshot, OrderAuditSnapshot, OrderExceptionSnapshot,
    VOCTopic, TrainingCase, TrainingTask, ManagementDashboardSnapshot
)
from shared_db.base import Base
from shared_db import get_db
from app.main import app


TEST_DB_URL = "sqlite:///test_management.db"


@pytest.fixture
def db_session():
    if os.path.exists("test_management.db"):
        os.remove("test_management.db")
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    if os.path.exists("test_management.db"):
        os.remove("test_management.db")


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestManagementAPI:
    """Test management API endpoints"""

    def test_create_voc_topic(self, client):
        """Test POST /api/management/voc-topics"""
        response = client.post("/api/management/voc-topics", json={
            "topic_name": "物流延误投诉",
            "topic_type": "complaint",
            "source": "conversation",
            "occurrence_count": 10
        })

        assert response.status_code == 201
        data = response.json()
        assert data["topic_name"] == "物流延误投诉"
        assert data["occurrence_count"] == 10

    def test_create_voc_topic_invalid_type(self, client):
        """Test POST /api/management/voc-topics with invalid type"""
        response = client.post("/api/management/voc-topics", json={
            "topic_name": "测试",
            "topic_type": "invalid",
            "source": "conversation"
        })

        assert response.status_code == 422

    def test_list_voc_topics(self, client):
        """Test GET /api/management/voc-topics"""
        client.post("/api/management/voc-topics", json={
            "topic_name": "主题1",
            "topic_type": "complaint",
            "source": "conversation"
        })
        client.post("/api/management/voc-topics", json={
            "topic_name": "主题2",
            "topic_type": "feedback",
            "source": "survey"
        })

        response = client.get("/api/management/voc-topics")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_voc_topics_by_type(self, client):
        """Test GET /api/management/voc-topics?topic_type=xxx"""
        client.post("/api/management/voc-topics", json={
            "topic_name": "主题1",
            "topic_type": "complaint",
            "source": "conversation"
        })
        client.post("/api/management/voc-topics", json={
            "topic_name": "主题2",
            "topic_type": "feedback",
            "source": "survey"
        })

        response = client.get("/api/management/voc-topics?topic_type=complaint")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["topic_type"] == "complaint"

    def test_create_training_case(self, client):
        """Test POST /api/management/training-cases"""
        response = client.post("/api/management/training-cases", json={
            "case_title": "高效处理案例",
            "case_type": "good"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["case_title"] == "高效处理案例"

    def test_create_training_case_null_foreign_keys(self, client):
        """Test POST /api/management/training-cases with null foreign keys"""
        response = client.post("/api/management/training-cases", json={
            "case_title": "独立案例",
            "case_type": "edge_case"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["conversation_id"] is None

    def test_list_training_cases(self, client):
        """Test GET /api/management/training-cases"""
        client.post("/api/management/training-cases", json={
            "case_title": "案例1",
            "case_type": "good"
        })
        client.post("/api/management/training-cases", json={
            "case_title": "案例2",
            "case_type": "bad"
        })

        response = client.get("/api/management/training-cases")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_create_training_task(self, client):
        """Test POST /api/management/training-tasks"""
        response = client.post("/api/management/training-tasks", json={
            "task_name": "复习任务",
            "task_type": "review",
            "status": "pending"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["task_name"] == "复习任务"

    def test_create_training_task_null_related_case(self, client):
        """Test POST /api/management/training-tasks with null related_case_id"""
        response = client.post("/api/management/training-tasks", json={
            "task_name": "独立任务",
            "task_type": "quiz"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["related_case_id"] is None

    def test_list_training_tasks(self, client):
        """Test GET /api/management/training-tasks"""
        client.post("/api/management/training-tasks", json={
            "task_name": "任务1",
            "task_type": "review"
        })
        client.post("/api/management/training-tasks", json={
            "task_name": "任务2",
            "task_type": "practice"
        })

        response = client.get("/api/management/training-tasks")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_training_tasks_by_status(self, client):
        """Test GET /api/management/training-tasks?status=xxx"""
        client.post("/api/management/training-tasks", json={
            "task_name": "任务1",
            "task_type": "review",
            "status": "pending"
        })
        client.post("/api/management/training-tasks", json={
            "task_name": "任务2",
            "task_type": "practice",
            "status": "completed"
        })

        response = client.get("/api/management/training-tasks?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending"

    def test_create_dashboard_snapshot(self, client):
        """Test POST /api/management/dashboard-snapshots"""
        response = client.post("/api/management/dashboard-snapshots", json={
            "snapshot_date": "2026-03-30",
            "metric_type": "conversation_count",
            "metric_value": 1250.0
        })

        assert response.status_code == 201
        data = response.json()
        assert data["metric_type"] == "conversation_count"
        assert data["metric_value"] == 1250.0

    def test_create_dashboard_snapshot_invalid_metric_type(self, client):
        """Test POST /api/management/dashboard-snapshots with invalid metric_type"""
        response = client.post("/api/management/dashboard-snapshots", json={
            "snapshot_date": "2026-03-30",
            "metric_type": "invalid_metric",
            "metric_value": 100.0
        })

        assert response.status_code == 422

    def test_list_dashboard_snapshots(self, client):
        """Test GET /api/management/dashboard-snapshots"""
        client.post("/api/management/dashboard-snapshots", json={
            "snapshot_date": "2026-03-30",
            "metric_type": "conversation_count",
            "metric_value": 100.0
        })
        client.post("/api/management/dashboard-snapshots", json={
            "snapshot_date": "2026-03-30",
            "metric_type": "avg_response_time",
            "metric_value": 45.0
        })

        response = client.get("/api/management/dashboard-snapshots")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_dashboard_snapshots_by_date(self, client):
        """Test GET /api/management/dashboard-snapshots?snapshot_date=xxx"""
        client.post("/api/management/dashboard-snapshots", json={
            "snapshot_date": "2026-03-30",
            "metric_type": "conversation_count",
            "metric_value": 100.0
        })
        client.post("/api/management/dashboard-snapshots", json={
            "snapshot_date": "2026-03-29",
            "metric_type": "conversation_count",
            "metric_value": 90.0
        })

        response = client.get("/api/management/dashboard-snapshots?snapshot_date=2026-03-30")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
