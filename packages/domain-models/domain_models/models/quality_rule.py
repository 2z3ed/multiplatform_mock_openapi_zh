from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin

ALLOWED_RULE_TYPES = {
    "slow_reply", "missed_response", "forbidden_word",
    "insufficient_explanation", "incomplete_after_sale_reply", "inventory_reply_conflict",
}
ALLOWED_SEVERITIES = {"low", "medium", "high"}


class QualityRule(Base, TimestampMixin):
    __tablename__ = "quality_rule"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rule_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    rule_name: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(30), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    config_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
