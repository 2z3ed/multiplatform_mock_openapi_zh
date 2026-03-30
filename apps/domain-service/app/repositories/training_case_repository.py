from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.training_case import TrainingCase, ALLOWED_CASE_TYPES


class TrainingCaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        case_title: str,
        case_type: str,
        conversation_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        case_summary: Optional[str] = None,
        source_json: Optional[dict] = None
    ) -> TrainingCase:
        case = TrainingCase(
            conversation_id=conversation_id,
            customer_id=customer_id,
            case_title=case_title,
            case_summary=case_summary,
            case_type=case_type,
            source_json=source_json
        )
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case

    def get_by_id(self, id: int) -> Optional[TrainingCase]:
        return self.db.query(TrainingCase).filter(TrainingCase.id == id).first()

    def list_all(self) -> list[TrainingCase]:
        return self.db.query(TrainingCase).order_by(TrainingCase.created_at.desc()).all()

    def list_by_case_type(self, case_type: str) -> list[TrainingCase]:
        return (
            self.db.query(TrainingCase)
            .filter(TrainingCase.case_type == case_type)
            .order_by(TrainingCase.created_at.desc())
            .all()
        )

    def delete(self, id: int) -> bool:
        case = self.get_by_id(id)
        if case is None:
            return False
        self.db.delete(case)
        self.db.commit()
        return True
