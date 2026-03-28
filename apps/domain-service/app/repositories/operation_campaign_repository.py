from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.operation_campaign import OperationCampaign

ALLOWED_STATUSES = {"draft", "ready", "completed", "cancelled"}


class OperationCampaignRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        name: str,
        campaign_type: str,
        target_description: Optional[str] = None,
        audience_json: Optional[dict] = None,
        preview_text: Optional[str] = None,
        status: str = "draft",
        extra_json: Optional[dict] = None
    ) -> OperationCampaign:
        campaign = OperationCampaign(
            name=name,
            campaign_type=campaign_type,
            target_description=target_description,
            audience_json=audience_json,
            preview_text=preview_text,
            status=status,
            extra_json=extra_json
        )
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def get_by_id(self, id: int) -> Optional[OperationCampaign]:
        return self.db.query(OperationCampaign).filter(OperationCampaign.id == id).first()

    def list_campaigns(self) -> list[OperationCampaign]:
        return (
            self.db.query(OperationCampaign)
            .order_by(OperationCampaign.created_at.desc())
            .all()
        )

    def update(self, id: int, updates: dict) -> Optional[OperationCampaign]:
        campaign = self.get_by_id(id)
        if campaign is None:
            return None

        for key, value in updates.items():
            if hasattr(campaign, key):
                setattr(campaign, key, value)

        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def update_status(self, id: int, status: str) -> Optional[OperationCampaign]:
        if status not in ALLOWED_STATUSES:
            return None

        campaign = self.get_by_id(id)
        if campaign is None:
            return None

        campaign.status = status
        self.db.commit()
        self.db.refresh(campaign)
        return campaign
