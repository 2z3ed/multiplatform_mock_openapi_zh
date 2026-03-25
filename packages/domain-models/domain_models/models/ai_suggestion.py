from sqlalchemy import Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class AISuggestion(Base, TimestampMixin):
    __tablename__ = "ai_suggestion"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversation.id"), nullable=False)
    intent: Mapped[str] = mapped_column(String(40), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    suggested_reply: Mapped[str] = mapped_column(Text, nullable=False)
    used_tools: Mapped[list | None] = mapped_column(JSON, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    review_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
