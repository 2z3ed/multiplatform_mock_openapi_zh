from sqlalchemy import JSON, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class OrderCore(Base, TimestampMixin):
    __tablename__ = "order_core"
    __table_args__ = (
        Index("ix_order_core_customer_id", "customer_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customer.id"), nullable=True)
    current_status: Mapped[str] = mapped_column(String(30), nullable=False, default="unknown")
    total_amount: Mapped[str | None] = mapped_column(String(32), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    shop_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
