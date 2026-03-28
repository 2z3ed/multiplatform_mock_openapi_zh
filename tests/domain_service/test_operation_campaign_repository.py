"""
Repository-level tests for operation_campaign
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.operation_campaign import OperationCampaign
from shared_db.base import Base
from app.repositories.operation_campaign_repository import OperationCampaignRepository


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestOperationCampaignRepository:
    """Test operation campaign repository"""

    def test_create_campaign(self, db_session):
        """Test creating campaign in database"""
        repo = OperationCampaignRepository(db_session)
        campaign = repo.create(
            name="VIP客户回馈活动",
            campaign_type="coupon",
            target_description="向高价值客户发送优惠券",
            preview_text="尊敬的VIP客户，您有一张专属优惠券..."
        )

        assert campaign.id is not None
        assert campaign.name == "VIP客户回馈活动"
        assert campaign.campaign_type == "coupon"
        assert campaign.status == "draft"
        assert campaign.created_at is not None

    def test_create_campaign_default_status_draft(self, db_session):
        """Test creating campaign defaults to draft status"""
        repo = OperationCampaignRepository(db_session)
        campaign = repo.create(
            name="测试活动",
            campaign_type="notification"
        )

        assert campaign.status == "draft"

    def test_create_campaign_optional_fields_null(self, db_session):
        """Test creating campaign with optional fields null"""
        repo = OperationCampaignRepository(db_session)
        campaign = repo.create(
            name="测试活动",
            campaign_type="notification"
        )

        assert campaign.id is not None
        assert campaign.target_description is None
        assert campaign.audience_json is None
        assert campaign.preview_text is None

    def test_get_by_id_exists(self, db_session):
        """Test getting existing campaign by id"""
        repo = OperationCampaignRepository(db_session)
        created = repo.create(
            name="测试活动",
            campaign_type="notification"
        )

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id
        assert result.name == "测试活动"

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent campaign returns None"""
        repo = OperationCampaignRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_list_campaigns(self, db_session):
        """Test listing campaigns"""
        repo = OperationCampaignRepository(db_session)
        
        repo.create(name="活动1", campaign_type="coupon")
        repo.create(name="活动2", campaign_type="notification")
        repo.create(name="活动3", campaign_type="sms")

        results = repo.list_campaigns()
        assert len(results) == 3

    def test_list_campaigns_empty(self, db_session):
        """Test listing campaigns when empty"""
        repo = OperationCampaignRepository(db_session)
        results = repo.list_campaigns()
        assert len(results) == 0

    def test_update_campaign_fields(self, db_session):
        """Test updating campaign fields"""
        repo = OperationCampaignRepository(db_session)
        campaign = repo.create(
            name="原名称",
            campaign_type="notification"
        )

        result = repo.update(campaign.id, {"name": "新名称", "preview_text": "新预览"})
        assert result is not None
        assert result.name == "新名称"
        assert result.preview_text == "新预览"

    def test_update_status_draft_to_ready(self, db_session):
        """Test updating status from draft to ready"""
        repo = OperationCampaignRepository(db_session)
        campaign = repo.create(
            name="测试活动",
            campaign_type="notification"
        )

        result = repo.update_status(campaign.id, "ready")
        assert result is not None
        assert result.status == "ready"

    def test_update_status_invalid_status(self, db_session):
        """Test updating status with invalid status value returns None"""
        repo = OperationCampaignRepository(db_session)
        campaign = repo.create(
            name="测试活动",
            campaign_type="notification"
        )

        result = repo.update_status(campaign.id, "invalid_status")
        assert result is None

    def test_update_status_nonexistent_id(self, db_session):
        """Test updating status for non-existent campaign returns None"""
        repo = OperationCampaignRepository(db_session)
        result = repo.update_status(9999, "ready")
        assert result is None

    def test_extra_json_null(self, db_session):
        """Test creating campaign with extra_json null"""
        repo = OperationCampaignRepository(db_session)
        campaign = repo.create(
            name="测试活动",
            campaign_type="notification",
            extra_json=None
        )

        assert campaign.extra_json is None

    def test_audience_json_writes_and_reads(self, db_session):
        """Test audience_json field can be written and read"""
        repo = OperationCampaignRepository(db_session)
        audience = {"tag_types": ["vip"], "min_orders": 5}
        campaign = repo.create(
            name="测试活动",
            campaign_type="notification",
            audience_json=audience
        )

        assert campaign.audience_json == audience
