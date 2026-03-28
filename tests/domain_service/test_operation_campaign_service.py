"""
Service-level tests for operation campaign
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.operation_campaign import OperationCampaign
from domain_models.models.audit_log import AuditLog
from shared_db.base import Base
from app.services.operation_campaign_service import OperationCampaignService


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestOperationCampaignService:
    """Test operation campaign service"""

    def test_create_campaign_default_status_draft(self, db_session):
        """Test creating campaign defaults to draft status"""
        service = OperationCampaignService(db_session=db_session)
        result = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        assert result is not None
        assert result["status"] == "draft"

    def test_create_campaign_optional_fields_null(self, db_session):
        """Test creating campaign with optional fields null"""
        service = OperationCampaignService(db_session=db_session)
        result = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        assert result is not None
        assert result["target_description"] is None
        assert result["audience_json"] is None
        assert result["preview_text"] is None

    def test_get_campaign_by_id_returns_correct_object(self, db_session):
        """Test getting campaign by id returns correct object"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        result = service.get_campaign_by_id(created["id"])
        assert result is not None
        assert result["id"] == created["id"]
        assert result["name"] == "测试活动"

    def test_get_campaign_by_id_not_exists(self, db_session):
        """Test getting non-existent campaign returns None"""
        service = OperationCampaignService(db_session=db_session)
        result = service.get_campaign_by_id(9999)
        assert result is None

    def test_list_campaigns_returns_correct_list(self, db_session):
        """Test listing campaigns"""
        service = OperationCampaignService(db_session=db_session)
        
        service.create_campaign(name="活动1", campaign_type="coupon")
        service.create_campaign(name="活动2", campaign_type="notification")
        service.create_campaign(name="活动3", campaign_type="sms")

        results = service.list_campaigns()
        assert len(results) == 3

    def test_list_campaigns_empty(self, db_session):
        """Test listing campaigns when empty"""
        service = OperationCampaignService(db_session=db_session)
        results = service.list_campaigns()
        assert len(results) == 0

    def test_update_campaign_in_draft_status_success(self, db_session):
        """Test updating campaign in draft status succeeds"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="原名称",
            campaign_type="notification"
        )

        result = service.update_campaign(created["id"], {"name": "新名称", "preview_text": "新预览"})
        assert result is not None
        assert result["name"] == "新名称"
        assert result["preview_text"] == "新预览"

    def test_update_campaign_in_non_draft_status_fails(self, db_session):
        """Test updating campaign in non-draft status fails"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        service.mark_campaign_ready(created["id"])
        result = service.update_campaign(created["id"], {"name": "新名称"})
        assert result is None

    def test_update_campaign_cannot_update_status(self, db_session):
        """Test update_campaign does not allow updating status directly"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        result = service.update_campaign(created["id"], {"status": "ready"})
        assert result is None

    def test_mark_campaign_ready_draft_to_ready_success(self, db_session):
        """Test marking campaign ready from draft to ready succeeds"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        result = service.mark_campaign_ready(created["id"])
        assert result is not None
        assert result["status"] == "ready"

    def test_mark_campaign_ready_not_exists_returns_failure(self, db_session):
        """Test marking non-existent campaign ready returns None"""
        service = OperationCampaignService(db_session=db_session)
        result = service.mark_campaign_ready(9999)
        assert result is None

    def test_mark_campaign_ready_non_draft_status_fails(self, db_session):
        """Test marking campaign ready in non-draft status fails"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        service.mark_campaign_ready(created["id"])
        result = service.mark_campaign_ready(created["id"])
        assert result is None

    def test_complete_campaign_ready_to_completed_success(self, db_session):
        """Test completing campaign from ready to completed succeeds"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        service.mark_campaign_ready(created["id"])
        result = service.complete_campaign(created["id"])
        assert result is not None
        assert result["status"] == "completed"

    def test_complete_campaign_non_ready_status_fails(self, db_session):
        """Test completing campaign in non-ready status fails"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        result = service.complete_campaign(created["id"])
        assert result is None

    def test_cancel_campaign_draft_to_cancelled_success(self, db_session):
        """Test cancelling campaign from draft to cancelled succeeds"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        result = service.cancel_campaign(created["id"])
        assert result is not None
        assert result["status"] == "cancelled"

    def test_cancel_campaign_ready_to_cancelled_success(self, db_session):
        """Test cancelling campaign from ready to cancelled succeeds"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        service.mark_campaign_ready(created["id"])
        result = service.cancel_campaign(created["id"])
        assert result is not None
        assert result["status"] == "cancelled"

    def test_cancel_campaign_completed_status_fails(self, db_session):
        """Test cancelling campaign in completed status fails"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        service.mark_campaign_ready(created["id"])
        service.complete_campaign(created["id"])
        result = service.cancel_campaign(created["id"])
        assert result is None

    def test_cancel_campaign_not_exists_returns_failure(self, db_session):
        """Test cancelling non-existent campaign returns None"""
        service = OperationCampaignService(db_session=db_session)
        result = service.cancel_campaign(9999)
        assert result is None


class TestOperationCampaignAuditLogs:
    """Test operation campaign audit logging"""

    def test_create_campaign_logs_audit(self, db_session):
        """Test creating campaign writes operation_campaign_created audit"""
        service = OperationCampaignService(db_session=db_session)
        result = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "operation_campaign_created"
        ).all()

        assert len(audit_logs) == 1
        assert audit_logs[0].target_id == str(result["id"])
        assert audit_logs[0].detail_json["name"] == "测试活动"
        assert audit_logs[0].detail_json["campaign_type"] == "notification"
        assert audit_logs[0].detail_json["status"] == "draft"

    def test_update_campaign_logs_audit(self, db_session):
        """Test updating campaign writes operation_campaign_updated audit"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="原名称",
            campaign_type="notification"
        )

        result = service.update_campaign(created["id"], {"name": "新名称"})

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "operation_campaign_updated"
        ).all()

        assert len(audit_logs) == 1
        assert audit_logs[0].target_id == str(created["id"])
        assert audit_logs[0].detail_json["name"] == "新名称"

    def test_mark_ready_logs_audit(self, db_session):
        """Test marking campaign ready writes operation_campaign_ready audit"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        result = service.mark_campaign_ready(created["id"])

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "operation_campaign_ready"
        ).all()

        assert len(audit_logs) == 1
        assert audit_logs[0].target_id == str(created["id"])
        assert audit_logs[0].detail_json["status"] == "ready"

    def test_complete_campaign_logs_audit(self, db_session):
        """Test completing campaign writes operation_campaign_completed audit"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        service.mark_campaign_ready(created["id"])
        result = service.complete_campaign(created["id"])

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "operation_campaign_completed"
        ).all()

        assert len(audit_logs) == 1
        assert audit_logs[0].target_id == str(created["id"])
        assert audit_logs[0].detail_json["status"] == "completed"

    def test_cancel_campaign_logs_audit(self, db_session):
        """Test cancelling campaign writes operation_campaign_cancelled audit"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        result = service.cancel_campaign(created["id"])

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "operation_campaign_cancelled"
        ).all()

        assert len(audit_logs) == 1
        assert audit_logs[0].target_id == str(created["id"])
        assert audit_logs[0].detail_json["status"] == "cancelled"

    def test_update_not_exists_does_not_log_audit(self, db_session):
        """Test updating non-existent campaign does not write audit"""
        service = OperationCampaignService(db_session=db_session)
        result = service.update_campaign(9999, {"name": "新名称"})

        assert result is None

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "operation_campaign_updated"
        ).all()

        assert len(audit_logs) == 0

    def test_update_non_draft_does_not_log_audit(self, db_session):
        """Test updating non-draft campaign does not write audit"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        service.mark_campaign_ready(created["id"])
        result = service.update_campaign(created["id"], {"name": "新名称"})

        assert result is None

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "operation_campaign_updated"
        ).all()

        assert len(audit_logs) == 0

    def test_ready_not_exists_does_not_log_audit(self, db_session):
        """Test marking non-existent campaign ready does not write audit"""
        service = OperationCampaignService(db_session=db_session)
        result = service.mark_campaign_ready(9999)

        assert result is None

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "operation_campaign_ready"
        ).all()

        assert len(audit_logs) == 0

    def test_ready_non_draft_does_not_log_audit(self, db_session):
        """Test marking non-draft campaign ready does not write audit"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        service.mark_campaign_ready(created["id"])
        result = service.mark_campaign_ready(created["id"])

        assert result is None

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "operation_campaign_ready"
        ).all()

        assert len(audit_logs) == 1

    def test_complete_not_exists_does_not_log_audit(self, db_session):
        """Test completing non-existent campaign does not write audit"""
        service = OperationCampaignService(db_session=db_session)
        result = service.complete_campaign(9999)

        assert result is None

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "operation_campaign_completed"
        ).all()

        assert len(audit_logs) == 0

    def test_complete_non_ready_does_not_log_audit(self, db_session):
        """Test completing non-ready campaign does not write audit"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        result = service.complete_campaign(created["id"])

        assert result is None

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "operation_campaign_completed"
        ).all()

        assert len(audit_logs) == 0

    def test_cancel_not_exists_does_not_log_audit(self, db_session):
        """Test cancelling non-existent campaign does not write audit"""
        service = OperationCampaignService(db_session=db_session)
        result = service.cancel_campaign(9999)

        assert result is None

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "operation_campaign_cancelled"
        ).all()

        assert len(audit_logs) == 0

    def test_cancel_completed_does_not_log_audit(self, db_session):
        """Test cancelling completed campaign does not write audit"""
        service = OperationCampaignService(db_session=db_session)
        created = service.create_campaign(
            name="测试活动",
            campaign_type="notification"
        )

        service.mark_campaign_ready(created["id"])
        service.complete_campaign(created["id"])
        result = service.cancel_campaign(created["id"])

        assert result is None

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "operation_campaign_cancelled"
        ).all()

        assert len(audit_logs) == 0
