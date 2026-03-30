"""
Service-level tests for management_service
"""

import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared_db.base import Base
from app.services.management_service import ManagementService


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestManagementService:
    """Test management service"""

    def test_create_voc_topic(self, db_session):
        """Test creating VOC topic"""
        service = ManagementService(db_session)
        result = service.create_voc_topic(
            topic_name="物流延误投诉",
            topic_type="complaint",
            source="conversation",
            occurrence_count=10
        )

        assert result["id"] is not None
        assert result["topic_name"] == "物流延误投诉"
        assert result["occurrence_count"] == 10

    def test_create_voc_topic_invalid_type(self, db_session):
        """Test creating VOC topic with invalid type"""
        service = ManagementService(db_session)
        with pytest.raises(ValueError, match="Invalid topic_type"):
            service.create_voc_topic(
                topic_name="测试",
                topic_type="invalid_type",
                source="conversation"
            )

    def test_create_voc_topic_invalid_source(self, db_session):
        """Test creating VOC topic with invalid source"""
        service = ManagementService(db_session)
        with pytest.raises(ValueError, match="Invalid source"):
            service.create_voc_topic(
                topic_name="测试",
                topic_type="complaint",
                source="invalid_source"
            )

    def test_list_voc_topics(self, db_session):
        """Test listing VOC topics"""
        service = ManagementService(db_session)
        service.create_voc_topic(topic_name="主题1", topic_type="complaint", source="conversation")
        service.create_voc_topic(topic_name="主题2", topic_type="feedback", source="survey")

        results = service.list_voc_topics()
        assert len(results) == 2

    def test_create_training_case(self, db_session):
        """Test creating training case"""
        service = ManagementService(db_session)
        result = service.create_training_case(
            case_title="高效处理案例",
            case_type="good",
            conversation_id=1,
            customer_id=100
        )

        assert result["id"] is not None
        assert result["case_title"] == "高效处理案例"
        assert result["conversation_id"] == 1

    def test_create_training_case_invalid_type(self, db_session):
        """Test creating training case with invalid type"""
        service = ManagementService(db_session)
        with pytest.raises(ValueError, match="Invalid case_type"):
            service.create_training_case(
                case_title="测试",
                case_type="invalid_type"
            )

    def test_create_training_case_null_foreign_keys(self, db_session):
        """Test creating training case with null foreign keys"""
        service = ManagementService(db_session)
        result = service.create_training_case(
            case_title="独立案例",
            case_type="edge_case",
            conversation_id=None,
            customer_id=None
        )

        assert result["conversation_id"] is None
        assert result["customer_id"] is None

    def test_list_training_cases(self, db_session):
        """Test listing training cases"""
        service = ManagementService(db_session)
        service.create_training_case(case_title="案例1", case_type="good")
        service.create_training_case(case_title="案例2", case_type="bad")

        results = service.list_training_cases()
        assert len(results) == 2

    def test_create_training_task(self, db_session):
        """Test creating training task"""
        service = ManagementService(db_session)
        result = service.create_training_task(
            task_name="复习任务",
            task_type="review",
            status="pending",
            related_case_id=1
        )

        assert result["id"] is not None
        assert result["task_name"] == "复习任务"
        assert result["related_case_id"] == 1

    def test_create_training_task_invalid_type(self, db_session):
        """Test creating training task with invalid type"""
        service = ManagementService(db_session)
        with pytest.raises(ValueError, match="Invalid task_type"):
            service.create_training_task(
                task_name="测试",
                task_type="invalid_type"
            )

    def test_create_training_task_invalid_status(self, db_session):
        """Test creating training task with invalid status"""
        service = ManagementService(db_session)
        with pytest.raises(ValueError, match="Invalid status"):
            service.create_training_task(
                task_name="测试",
                task_type="review",
                status="invalid_status"
            )

    def test_list_training_tasks(self, db_session):
        """Test listing training tasks"""
        service = ManagementService(db_session)
        service.create_training_task(task_name="任务1", task_type="review")
        service.create_training_task(task_name="任务2", task_type="practice")

        results = service.list_training_tasks()
        assert len(results) == 2

    def test_create_dashboard_snapshot(self, db_session):
        """Test creating dashboard snapshot"""
        service = ManagementService(db_session)
        result = service.create_dashboard_snapshot(
            snapshot_date=date(2026, 3, 30),
            metric_type="conversation_count",
            metric_value=1250.0
        )

        assert result["id"] is not None
        assert result["metric_type"] == "conversation_count"
        assert result["metric_value"] == 1250.0

    def test_create_dashboard_snapshot_invalid_metric_type(self, db_session):
        """Test creating dashboard snapshot with invalid metric_type"""
        service = ManagementService(db_session)
        with pytest.raises(ValueError, match="Invalid metric_type"):
            service.create_dashboard_snapshot(
                snapshot_date=date(2026, 3, 30),
                metric_type="invalid_metric",
                metric_value=100.0
            )

    def test_list_dashboard_snapshots(self, db_session):
        """Test listing dashboard snapshots"""
        service = ManagementService(db_session)
        service.create_dashboard_snapshot(
            snapshot_date=date(2026, 3, 30),
            metric_type="conversation_count",
            metric_value=100.0
        )
        service.create_dashboard_snapshot(
            snapshot_date=date(2026, 3, 30),
            metric_type="avg_response_time",
            metric_value=45.0
        )

        results = service.list_dashboard_snapshots()
        assert len(results) == 2

    def test_list_dashboard_snapshots_by_date(self, db_session):
        """Test listing dashboard snapshots by date"""
        service = ManagementService(db_session)
        service.create_dashboard_snapshot(
            snapshot_date=date(2026, 3, 30),
            metric_type="conversation_count",
            metric_value=100.0
        )
        service.create_dashboard_snapshot(
            snapshot_date=date(2026, 3, 29),
            metric_type="conversation_count",
            metric_value=90.0
        )

        results = service.list_dashboard_snapshots(snapshot_date=date(2026, 3, 30))
        assert len(results) == 1
