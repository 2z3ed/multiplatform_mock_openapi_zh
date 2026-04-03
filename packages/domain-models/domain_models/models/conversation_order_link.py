from sqlalchemy import ForeignKey, String, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


ALLOWED_LINK_TYPES = {"mentioned", "bound", "primary"}


class ConversationOrderLink(Base, TimestampMixin):
    __tablename__ = "conversation_order_link"
    __table_args__ = (
        UniqueConstraint("conversation_id", "order_id", name="uq_conversation_order"),
        Index("ix_conversation_order_order_id", "order_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversation.id"), nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey("order_core.id"), nullable=False)
    link_type: Mapped[str] = mapped_column(String(20), nullable=False, default="mentioned")
