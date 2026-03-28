"""
API-level tests for operation campaign endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.operation_campaign import OperationCampaign
from shared_db.base import Base
from app.main import app
from app.api.operation_campaign import get_campaign_service
from app.services.operation_campaign_service import OperationCampaignService


TEST_DB_URL = "sqlite:///test_operation_campaign.db"


@pytest.fixture
def db_session():
    import os
    if os.path.exists("test_operation_campaign.db"):
        os.remove("test_operation_campaign.db")
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    if os.path.exists("test_operation_campaign.db"):
        os.remove("test_operation_campaign.db")


@pytest.fixture
def test_client(db_session):
    def override_get_campaign_service():
        return OperationCampaignService(db_session=db_session)

    app.dependency_overrides[get_campaign_service] = override_get_campaign_service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


class TestOperationCampaignAPI:
    """Test operation campaign API endpoints"""

    def test_create_campaign_success(self, test_client):
        """Test POST /api/operation-campaigns creates campaign with draft status"""
        response = test_client.post(
            "/api/operation-campaigns",
            json={
                "name": "VIP客户回馈活动",
                "campaign_type": "coupon",
                "target_description": "向高价值客户发送优惠券",
                "preview_text": "尊敬的VIP客户，您有一张专属优惠券..."
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "VIP客户回馈活动"
        assert data["campaign_type"] == "coupon"
        assert data["status"] == "draft"

    def test_get_campaign_success(self, test_client):
        """Test GET /api/operation-campaigns/{id} returns campaign"""
        create_resp = test_client.post(
            "/api/operation-campaigns",
            json={
                "name": "测试活动",
                "campaign_type": "notification"
            }
        )
        campaign_id = create_resp.json()["id"]

        response = test_client.get(f"/api/operation-campaigns/{campaign_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == campaign_id
        assert data["name"] == "测试活动"

    def test_get_campaign_not_found(self, test_client):
        """Test GET /api/operation-campaigns/{id} returns 404 for non-existent"""
        response = test_client.get("/api/operation-campaigns/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Campaign not found"

    def test_list_campaigns_success(self, test_client):
        """Test GET /api/operation-campaigns returns list"""
        test_client.post(
            "/api/operation-campaigns",
            json={"name": "活动1", "campaign_type": "coupon"}
        )
        test_client.post(
            "/api/operation-campaigns",
            json={"name": "活动2", "campaign_type": "notification"}
        )

        response = test_client.get("/api/operation-campaigns")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_campaigns_empty(self, test_client):
        """Test GET /api/operation-campaigns returns empty list"""
        response = test_client.get("/api/operation-campaigns")
        assert response.status_code == 200
        assert response.json() == []

    def test_patch_campaign_in_draft_status_success(self, test_client):
        """Test PATCH /api/operation-campaigns/{id} in draft status succeeds"""
        create_resp = test_client.post(
            "/api/operation-campaigns",
            json={
                "name": "原名称",
                "campaign_type": "notification"
            }
        )
        campaign_id = create_resp.json()["id"]

        response = test_client.patch(
            f"/api/operation-campaigns/{campaign_id}",
            json={"name": "新名称", "preview_text": "新预览"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "新名称"
        assert data["preview_text"] == "新预览"

    def test_patch_campaign_not_found(self, test_client):
        """Test PATCH /api/operation-campaigns/{id} returns 404 for non-existent"""
        response = test_client.patch(
            "/api/operation-campaigns/9999",
            json={"name": "新名称"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Campaign not found"

    def test_patch_campaign_non_draft_status_returns_400(self, test_client):
        """Test PATCH /api/operation-campaigns/{id} returns 400 when not in draft status"""
        create_resp = test_client.post(
            "/api/operation-campaigns",
            json={
                "name": "测试活动",
                "campaign_type": "notification"
            }
        )
        campaign_id = create_resp.json()["id"]

        test_client.post(f"/api/operation-campaigns/{campaign_id}/ready")

        response = test_client.patch(
            f"/api/operation-campaigns/{campaign_id}",
            json={"name": "新名称"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Campaign is not in draft status"

    def test_patch_campaign_update_status_returns_400(self, test_client):
        """Test PATCH /api/operation-campaigns/{id} returns 400 when trying to update status"""
        create_resp = test_client.post(
            "/api/operation-campaigns",
            json={
                "name": "测试活动",
                "campaign_type": "notification"
            }
        )
        campaign_id = create_resp.json()["id"]

        response = test_client.patch(
            f"/api/operation-campaigns/{campaign_id}",
            json={"status": "ready"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Cannot update status directly"

    def test_mark_ready_success(self, test_client):
        """Test POST /api/operation-campaigns/{id}/ready marks campaign ready"""
        create_resp = test_client.post(
            "/api/operation-campaigns",
            json={
                "name": "测试活动",
                "campaign_type": "notification"
            }
        )
        campaign_id = create_resp.json()["id"]

        response = test_client.post(f"/api/operation-campaigns/{campaign_id}/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    def test_mark_ready_not_found(self, test_client):
        """Test POST /api/operation-campaigns/{id}/ready returns 404 for non-existent"""
        response = test_client.post("/api/operation-campaigns/9999/ready")
        assert response.status_code == 404
        assert response.json()["detail"] == "Campaign not found"

    def test_mark_ready_non_draft_returns_400(self, test_client):
        """Test POST /api/operation-campaigns/{id}/ready returns 400 when not in draft status"""
        create_resp = test_client.post(
            "/api/operation-campaigns",
            json={
                "name": "测试活动",
                "campaign_type": "notification"
            }
        )
        campaign_id = create_resp.json()["id"]

        test_client.post(f"/api/operation-campaigns/{campaign_id}/ready")

        response = test_client.post(f"/api/operation-campaigns/{campaign_id}/ready")
        assert response.status_code == 400
        assert response.json()["detail"] == "Campaign is not in draft status"

    def test_complete_success(self, test_client):
        """Test POST /api/operation-campaigns/{id}/complete marks campaign completed"""
        create_resp = test_client.post(
            "/api/operation-campaigns",
            json={
                "name": "测试活动",
                "campaign_type": "notification"
            }
        )
        campaign_id = create_resp.json()["id"]

        test_client.post(f"/api/operation-campaigns/{campaign_id}/ready")

        response = test_client.post(f"/api/operation-campaigns/{campaign_id}/complete")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_complete_not_found(self, test_client):
        """Test POST /api/operation-campaigns/{id}/complete returns 404 for non-existent"""
        response = test_client.post("/api/operation-campaigns/9999/complete")
        assert response.status_code == 404
        assert response.json()["detail"] == "Campaign not found"

    def test_complete_non_ready_returns_400(self, test_client):
        """Test POST /api/operation-campaigns/{id}/complete returns 400 when not in ready status"""
        create_resp = test_client.post(
            "/api/operation-campaigns",
            json={
                "name": "测试活动",
                "campaign_type": "notification"
            }
        )
        campaign_id = create_resp.json()["id"]

        response = test_client.post(f"/api/operation-campaigns/{campaign_id}/complete")
        assert response.status_code == 400
        assert response.json()["detail"] == "Campaign is not in ready status"

    def test_cancel_draft_to_cancelled_success(self, test_client):
        """Test POST /api/operation-campaigns/{id}/cancel cancels from draft"""
        create_resp = test_client.post(
            "/api/operation-campaigns",
            json={
                "name": "测试活动",
                "campaign_type": "notification"
            }
        )
        campaign_id = create_resp.json()["id"]

        response = test_client.post(f"/api/operation-campaigns/{campaign_id}/cancel")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    def test_cancel_ready_to_cancelled_success(self, test_client):
        """Test POST /api/operation-campaigns/{id}/cancel cancels from ready"""
        create_resp = test_client.post(
            "/api/operation-campaigns",
            json={
                "name": "测试活动",
                "campaign_type": "notification"
            }
        )
        campaign_id = create_resp.json()["id"]

        test_client.post(f"/api/operation-campaigns/{campaign_id}/ready")

        response = test_client.post(f"/api/operation-campaigns/{campaign_id}/cancel")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    def test_cancel_not_found(self, test_client):
        """Test POST /api/operation-campaigns/{id}/cancel returns 404 for non-existent"""
        response = test_client.post("/api/operation-campaigns/9999/cancel")
        assert response.status_code == 404
        assert response.json()["detail"] == "Campaign not found"

    def test_cancel_completed_returns_400(self, test_client):
        """Test POST /api/operation-campaigns/{id}/cancel returns 400 when completed"""
        create_resp = test_client.post(
            "/api/operation-campaigns",
            json={
                "name": "测试活动",
                "campaign_type": "notification"
            }
        )
        campaign_id = create_resp.json()["id"]

        test_client.post(f"/api/operation-campaigns/{campaign_id}/ready")
        test_client.post(f"/api/operation-campaigns/{campaign_id}/complete")

        response = test_client.post(f"/api/operation-campaigns/{campaign_id}/cancel")
        assert response.status_code == 400
        assert response.json()["detail"] == "Cannot cancel completed campaign"
