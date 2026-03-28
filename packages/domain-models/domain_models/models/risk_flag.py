from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class RiskFlag(Base, TimestampMixin):
    __tablename__ = "risk_flag"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    conversation_id: Mapped[int | None] = mapped_column(ForeignKey("conversation.id"), nullable=True)
    risk_type: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
