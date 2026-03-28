from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.recommendation_repository import RecommendationRepository
from app.services.audit_service import AuditService


class RecommendationService:
    """Recommendation service for V2"""

    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._repo = RecommendationRepository(db_session)
        self._audit_service = AuditService(db_session=db_session)

    def _to_dict(self, recommendation) -> dict:
        return {
            "id": recommendation.id,
            "conversation_id": recommendation.conversation_id,
            "customer_id": recommendation.customer_id,
            "product_id": recommendation.product_id,
            "product_name": recommendation.product_name,
            "reason": recommendation.reason,
            "suggested_copy": recommendation.suggested_copy,
            "status": recommendation.status,
            "extra_json": recommendation.extra_json,
            "created_at": recommendation.created_at.isoformat() if recommendation.created_at else None,
            "updated_at": recommendation.updated_at.isoformat() if recommendation.updated_at else None,
        }

    def get_recommendation_by_id(self, id: int) -> Optional[dict]:
        recommendation = self._repo.get_by_id(id)
        if recommendation is None:
            return None
        return self._to_dict(recommendation)

    def list_recommendations_by_conversation(self, conversation_id: int) -> list[dict]:
        recommendations = self._repo.list_by_conversation(conversation_id)
        return [self._to_dict(r) for r in recommendations]

    def create_recommendation(
        self,
        conversation_id: int,
        customer_id: int,
        product_id: str,
        product_name: str,
        reason: Optional[str] = None,
        suggested_copy: Optional[str] = None,
        extra_json: Optional[dict] = None
    ) -> Optional[dict]:
        recommendation = self._repo.create(
            conversation_id=conversation_id,
            customer_id=customer_id,
            product_id=product_id,
            product_name=product_name,
            reason=reason,
            suggested_copy=suggested_copy,
            status="pending",
            extra_json=extra_json
        )
        
        self._audit_service.recommendation_created(
            recommendation_id=str(recommendation.id),
            conversation_id=str(conversation_id),
            customer_id=str(customer_id),
            product_id=product_id
        )
        
        return self._to_dict(recommendation)

    def accept_recommendation(self, id: int) -> Optional[dict]:
        recommendation = self._repo.get_by_id(id)
        if recommendation is None:
            return None
        if recommendation.status != "pending":
            return None

        result = self._repo.update_status(id, "accepted")
        if result is None:
            return None
        
        self._audit_service.recommendation_accepted(
            recommendation_id=str(id),
            conversation_id=str(recommendation.conversation_id),
            customer_id=str(recommendation.customer_id),
            product_id=recommendation.product_id
        )
        
        return self._to_dict(result)

    def reject_recommendation(self, id: int) -> Optional[dict]:
        recommendation = self._repo.get_by_id(id)
        if recommendation is None:
            return None
        if recommendation.status != "pending":
            return None

        result = self._repo.update_status(id, "rejected")
        if result is None:
            return None
        
        self._audit_service.recommendation_rejected(
            recommendation_id=str(id),
            conversation_id=str(recommendation.conversation_id),
            customer_id=str(recommendation.customer_id),
            product_id=recommendation.product_id
        )
        
        return self._to_dict(result)
