from typing import Optional

from sqlalchemy.orm import Session

from domain_models.models.risk_flag import RiskFlag


ALLOWED_RISK_TYPES = {"negative_sentiment", "complaint_tendency"}
ALLOWED_RISK_LEVELS = {"low", "medium", "high"}
ALLOWED_STATUSES = {"active", "resolved", "dismissed"}


class RiskFlagRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        customer_id: int,
        risk_type: str,
        conversation_id: Optional[int] = None,
        risk_level: str = "low",
        description: Optional[str] = None,
        extra_json: Optional[dict] = None,
    ) -> Optional[RiskFlag]:
        if risk_type not in ALLOWED_RISK_TYPES:
            return None
        if risk_level not in ALLOWED_RISK_LEVELS:
            return None

        risk_flag = RiskFlag(
            customer_id=customer_id,
            conversation_id=conversation_id,
            risk_type=risk_type,
            risk_level=risk_level,
            description=description,
            extra_json=extra_json,
            status="active",
        )
        self.db.add(risk_flag)
        self.db.commit()
        self.db.refresh(risk_flag)
        return risk_flag

    def get_by_id(self, id: int) -> Optional[RiskFlag]:
        return self.db.query(RiskFlag).filter(RiskFlag.id == id).first()

    def list_by_customer_id(self, customer_id: int) -> list[RiskFlag]:
        return (
            self.db.query(RiskFlag)
            .filter(RiskFlag.customer_id == customer_id)
            .order_by(RiskFlag.created_at.desc())
            .all()
        )

    def update_status(self, id: int, status: str) -> Optional[RiskFlag]:
        if status not in ALLOWED_STATUSES:
            return None

        risk_flag = self.get_by_id(id)
        if risk_flag is None:
            return None

        risk_flag.status = status
        self.db.commit()
        self.db.refresh(risk_flag)
        return risk_flag
