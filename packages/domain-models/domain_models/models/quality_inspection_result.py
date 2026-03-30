from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin

ALLOWED_SEVERITIES = {"low", "medium", "high"}


class QualityInspectionResult(Base, TimestampMixin):
    __tablename__ = "quality_inspection_result"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversation.id"), nullable=False)
    quality_rule_id: Mapped[int] = mapped_column(ForeignKey("quality_rule.id"), nullable=False)
    hit: Mapped[bool] = mapped_column(nullable=False, default=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    evidence_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    inspected_at: Mapped[str | None] = mapped_column(Text, nullable=True)
