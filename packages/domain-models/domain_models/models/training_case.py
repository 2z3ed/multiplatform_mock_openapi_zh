from sqlalchemy import JSON, String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin

ALLOWED_CASE_TYPES = {"good", "bad", "typical", "edge_case"}


class TrainingCase(Base, TimestampMixin):
    __tablename__ = "training_case"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("conversation.id"), nullable=True)
    customer_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    case_title: Mapped[str] = mapped_column(String(200), nullable=False)
    case_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    case_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
