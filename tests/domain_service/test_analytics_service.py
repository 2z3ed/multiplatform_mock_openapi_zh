"""
Service-level tests for analytics
"""

import pytest
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.recommendation import Recommendation
from domain_models.models.follow_up_task import FollowUpTask
from domain_models.models.operation_campaign import OperationCampaign
from domain_models.models.customer import Customer
from domain_models.models.conversation import Conversation
from domain_models.models.audit_log import AuditLog
from shared_db.base import Base
from app.services.analytics_service import AnalyticsService


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
    customer = Customer(id=1, platform="test", platform_customer_id="test_001", display_name="Test Customer")
    db_session.add(customer)
    
    conversation = Conversation(id=1, customer_id=1, platform="test", status="active")
    db_session.add(conversation)
    
    db_session.commit()
    return {"customer_id": 1, "conversation_id": 1}


class TestAnalyticsService:
    """Test analytics service"""

    def test_summarize_empty_data_returns_zeros(self, db_session, setup_data):
        """Test summarize with no data returns all zeros"""
        service = AnalyticsService(db_session=db_session)
        result = service.summarize_by_date(date(2026, 3, 28))

        assert result["recommendation_created_count"] == 0
        assert result["recommendation_accepted_count"] == 0
        assert result["followup_executed_count"] == 0
        assert result["followup_closed_count"] == 0
        assert result["operation_campaign_completed_count"] == 0

    def test_summarize_recommendation_created_count(self, db_session, setup_data):
        """Test summarize counts recommendation.created_at"""
        service = AnalyticsService(db_session=db_session)

        rec1 = Recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="P1",
            product_name="Product 1",
            status="pending",
            created_at=datetime(2026, 3, 28, 10, 0, 0)
        )
        rec2 = Recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="P2",
            product_name="Product 2",
            status="pending",
            created_at=datetime(2026, 3, 28, 14, 0, 0)
        )
        rec3 = Recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="P3",
            product_name="Product 3",
            status="pending",
            created_at=datetime(2026, 3, 29, 10, 0, 0)
        )
        db_session.add_all([rec1, rec2, rec3])
        db_session.commit()

        result = service.summarize_by_date(date(2026, 3, 28))

        assert result["recommendation_created_count"] == 2

    def test_summarize_recommendation_accepted_count(self, db_session, setup_data):
        """Test summarize counts recommendation.status=accepted with updated_at"""
        service = AnalyticsService(db_session=db_session)

        rec = Recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="P1",
            product_name="Product 1",
            status="accepted",
            created_at=datetime(2026, 3, 27, 10, 0, 0),
            updated_at=datetime(2026, 3, 28, 10, 0, 0)
        )
        db_session.add(rec)
        db_session.commit()

        result = service.summarize_by_date(date(2026, 3, 28))

        assert result["recommendation_accepted_count"] == 1

    def test_summarize_followup_executed_count(self, db_session, setup_data):
        """Test summarize counts followup status=completed (field name: followup_executed_count)"""
        service = AnalyticsService(db_session=db_session)

        task = FollowUpTask(
            customer_id=1,
            task_type="consultation_no_order",
            trigger_source="manual",
            title="Test Task",
            status="completed",
            completed_at=datetime(2026, 3, 28, 10, 0, 0)
        )
        db_session.add(task)
        db_session.commit()

        result = service.summarize_by_date(date(2026, 3, 28))

        assert result["followup_executed_count"] == 1

    def test_summarize_followup_closed_count(self, db_session, setup_data):
        """Test summarize counts followup status=closed"""
        service = AnalyticsService(db_session=db_session)

        task = FollowUpTask(
            customer_id=1,
            task_type="consultation_no_order",
            trigger_source="manual",
            title="Test Task",
            status="closed",
            completed_at=datetime(2026, 3, 28, 10, 0, 0)
        )
        db_session.add(task)
        db_session.commit()

        result = service.summarize_by_date(date(2026, 3, 28))

        assert result["followup_closed_count"] == 1

    def test_summarize_operation_campaign_completed_count(self, db_session, setup_data):
        """Test summarize counts operation_campaign.status=completed"""
        service = AnalyticsService(db_session=db_session)

        campaign = OperationCampaign(
            name="Test Campaign",
            campaign_type="notification",
            status="completed",
            updated_at=datetime(2026, 3, 28, 10, 0, 0)
        )
        db_session.add(campaign)
        db_session.commit()

        result = service.summarize_by_date(date(2026, 3, 28))

        assert result["operation_campaign_completed_count"] == 1

    def test_summarize_upsert_updates_existing(self, db_session, setup_data):
        """Test summarize updates existing record for same date"""
        service = AnalyticsService(db_session=db_session)

        rec = Recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="P1",
            product_name="Product 1",
            status="pending",
            created_at=datetime(2026, 3, 28, 10, 0, 0)
        )
        db_session.add(rec)
        db_session.commit()

        result1 = service.summarize_by_date(date(2026, 3, 28))
        assert result1["recommendation_created_count"] == 1

        rec2 = Recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="P2",
            product_name="Product 2",
            status="pending",
            created_at=datetime(2026, 3, 28, 11, 0, 0)
        )
        db_session.add(rec2)
        db_session.commit()

        result2 = service.summarize_by_date(date(2026, 3, 28))
        assert result2["recommendation_created_count"] == 2

    def test_get_summary_by_date_exists(self, db_session, setup_data):
        """Test get_summary_by_date returns summary when exists"""
        service = AnalyticsService(db_session=db_session)
        service.summarize_by_date(date(2026, 3, 28))

        result = service.get_summary_by_date(date(2026, 3, 28))

        assert result is not None
        assert result["stat_date"] == "2026-03-28"

    def test_get_summary_by_date_not_exists(self, db_session, setup_data):
        """Test get_summary_by_date returns None when not exists"""
        service = AnalyticsService(db_session=db_session)

        result = service.get_summary_by_date(date(2026, 3, 28))

        assert result is None

    def test_list_summaries(self, db_session, setup_data):
        """Test list_summaries returns correct list in range"""
        service = AnalyticsService(db_session=db_session)
        service.summarize_by_date(date(2026, 3, 28))
        service.summarize_by_date(date(2026, 3, 29))
        service.summarize_by_date(date(2026, 3, 30))

        results = service.list_summaries(date(2026, 3, 28), date(2026, 3, 30))

        assert len(results) == 3

    def test_list_summaries_empty_range(self, db_session, setup_data):
        """Test list_summaries returns empty list when no data"""
        service = AnalyticsService(db_session=db_session)
        service.summarize_by_date(date(2026, 3, 28))

        results = service.list_summaries(date(2026, 4, 1), date(2026, 4, 30))

        assert len(results) == 0


class TestAnalyticsAuditLogs:
    """Test analytics audit logging"""

    def test_summarize_logs_audit(self, db_session, setup_data):
        """Test summarize writes analytics_summary_generated audit"""
        service = AnalyticsService(db_session=db_session)
        result = service.summarize_by_date(date(2026, 3, 28))

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "analytics_summary_generated"
        ).all()

        assert len(audit_logs) == 1
        assert audit_logs[0].target_id == "2026-03-28"
        assert audit_logs[0].detail_json["stat_date"] == "2026-03-28"

    def test_summarize_empty_data_logs_audit(self, db_session, setup_data):
        """Test summarize with no data still writes audit"""
        service = AnalyticsService(db_session=db_session)
        result = service.summarize_by_date(date(2026, 3, 28))

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "analytics_summary_generated"
        ).all()

        assert len(audit_logs) == 1
        assert audit_logs[0].detail_json["recommendation_created_count"] == 0

    def test_summarize_upsert_logs_audit(self, db_session, setup_data):
        """Test summarize for same date again still writes audit (upsert)"""
        service = AnalyticsService(db_session=db_session)
        service.summarize_by_date(date(2026, 3, 28))

        rec = Recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="P1",
            product_name="Product 1",
            status="pending",
            created_at=datetime(2026, 3, 28, 10, 0, 0)
        )
        db_session.add(rec)
        db_session.commit()

        result = service.summarize_by_date(date(2026, 3, 28))

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "analytics_summary_generated"
        ).all()

        assert len(audit_logs) == 2
        assert audit_logs[1].detail_json["recommendation_created_count"] == 1
