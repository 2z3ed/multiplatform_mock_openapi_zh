from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.operation_campaign_repository import OperationCampaignRepository
from app.services.audit_service import AuditService


class OperationCampaignService:
    """Operation campaign service for V2"""

    ALLOWED_UPDATE_FIELDS = {
        "name", "campaign_type", "target_description",
        "audience_json", "preview_text", "extra_json"
    }

    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._repo = OperationCampaignRepository(db_session)
        self._audit_service = AuditService(db_session)

    def _to_dict(self, campaign) -> dict:
        return {
            "id": campaign.id,
            "name": campaign.name,
            "campaign_type": campaign.campaign_type,
            "target_description": campaign.target_description,
            "audience_json": campaign.audience_json,
            "preview_text": campaign.preview_text,
            "status": campaign.status,
            "extra_json": campaign.extra_json,
            "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
            "updated_at": campaign.updated_at.isoformat() if campaign.updated_at else None,
        }

    def get_campaign_by_id(self, id: int) -> Optional[dict]:
        campaign = self._repo.get_by_id(id)
        if campaign is None:
            return None
        return self._to_dict(campaign)

    def list_campaigns(self) -> list[dict]:
        campaigns = self._repo.list_campaigns()
        return [self._to_dict(c) for c in campaigns]

    def create_campaign(
        self,
        name: str,
        campaign_type: str,
        target_description: Optional[str] = None,
        audience_json: Optional[dict] = None,
        preview_text: Optional[str] = None,
        extra_json: Optional[dict] = None
    ) -> Optional[dict]:
        campaign = self._repo.create(
            name=name,
            campaign_type=campaign_type,
            target_description=target_description,
            audience_json=audience_json,
            preview_text=preview_text,
            status="draft",
            extra_json=extra_json
        )
        self._audit_service.operation_campaign_created(
            campaign_id=str(campaign.id),
            name=campaign.name,
            campaign_type=campaign.campaign_type
        )
        return self._to_dict(campaign)

    def update_campaign(self, id: int, updates: dict) -> Optional[dict]:
        campaign = self._repo.get_by_id(id)
        if campaign is None:
            return None
        if campaign.status != "draft":
            return None

        filtered_updates = {k: v for k, v in updates.items() if k in self.ALLOWED_UPDATE_FIELDS}
        if not filtered_updates:
            return None

        result = self._repo.update(id, filtered_updates)
        if result is None:
            return None
        self._audit_service.operation_campaign_updated(
            campaign_id=str(result.id),
            name=result.name,
            campaign_type=result.campaign_type
        )
        return self._to_dict(result)

    def mark_campaign_ready(self, id: int) -> Optional[dict]:
        campaign = self._repo.get_by_id(id)
        if campaign is None:
            return None
        if campaign.status != "draft":
            return None

        result = self._repo.update_status(id, "ready")
        if result is None:
            return None
        self._audit_service.operation_campaign_ready(
            campaign_id=str(result.id),
            name=result.name,
            campaign_type=result.campaign_type
        )
        return self._to_dict(result)

    def complete_campaign(self, id: int) -> Optional[dict]:
        campaign = self._repo.get_by_id(id)
        if campaign is None:
            return None
        if campaign.status != "ready":
            return None

        result = self._repo.update_status(id, "completed")
        if result is None:
            return None
        self._audit_service.operation_campaign_completed(
            campaign_id=str(result.id),
            name=result.name,
            campaign_type=result.campaign_type
        )
        return self._to_dict(result)

    def cancel_campaign(self, id: int) -> Optional[dict]:
        campaign = self._repo.get_by_id(id)
        if campaign is None:
            return None
        if campaign.status == "completed":
            return None
        if campaign.status == "cancelled":
            return None

        result = self._repo.update_status(id, "cancelled")
        if result is None:
            return None
        self._audit_service.operation_campaign_cancelled(
            campaign_id=str(result.id),
            name=result.name,
            campaign_type=result.campaign_type
        )
        return self._to_dict(result)
