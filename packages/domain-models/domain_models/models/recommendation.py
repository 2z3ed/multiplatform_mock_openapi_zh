from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recommendation"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversation.id"), nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    recommendation_type: Mapped[str] = mapped_column(String(30), nullable=False)
    product_id: Mapped[str] = mapped_column(String(100), nullable=False)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    product_price: Mapped[float | None] = mapped_column(nullable=True)
    product_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_copy: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    accepted: Mapped[bool] = mapped_column(default=False)
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
