from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversation"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open")
    assigned_agent_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    platform_conversation_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_system: Mapped[str | None] = mapped_column(String(30), nullable=True, default="platform")
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    customer = relationship("Customer", back_populates="conversations")
