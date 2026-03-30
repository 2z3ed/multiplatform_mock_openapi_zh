from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON

from shared_db.base import Base
from shared_db.mixins import TimestampMixin

ALLOWED_RISK_TYPES = {"complaint_tendency", "negative_emotion", "blacklisted_customer", "other"}
ALLOWED_SEVERITIES = {"low", "medium", "high"}
ALLOWED_STATUSES = {"open", "resolved", "dismissed", "escalated"}


class RiskCase(Base, TimestampMixin):
    __tablename__ = "risk_case"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(nullable=False)
    customer_id: Mapped[int] = mapped_column(nullable=False)
    risk_type: Mapped[str] = mapped_column(String(30), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    evidence_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
