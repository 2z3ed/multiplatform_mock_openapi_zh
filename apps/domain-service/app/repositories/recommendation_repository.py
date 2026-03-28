from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.recommendation import Recommendation, ALLOWED_STATUSES


class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        conversation_id: int,
        customer_id: int,
        product_id: str,
        product_name: str,
        reason: Optional[str] = None,
        suggested_copy: Optional[str] = None,
        status: str = "pending",
        extra_json: Optional[dict] = None
    ) -> Recommendation:
        recommendation = Recommendation(
            conversation_id=conversation_id,
            customer_id=customer_id,
            product_id=product_id,
            product_name=product_name,
            reason=reason,
            suggested_copy=suggested_copy,
            status=status,
            extra_json=extra_json
        )
        self.db.add(recommendation)
        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation

    def get_by_id(self, id: int) -> Optional[Recommendation]:
        return self.db.query(Recommendation).filter(Recommendation.id == id).first()

    def list_by_conversation(self, conversation_id: int) -> list[Recommendation]:
        return (
            self.db.query(Recommendation)
            .filter(Recommendation.conversation_id == conversation_id)
            .order_by(Recommendation.created_at.desc())
            .all()
        )

    def update_status(self, id: int, status: str) -> Optional[Recommendation]:
        if status not in ALLOWED_STATUSES:
            return None

        recommendation = self.get_by_id(id)
        if recommendation is None:
            return None

        recommendation.status = status
        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation
