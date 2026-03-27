from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class CustomerProfile(Base, TimestampMixin):
    __tablename__ = "customer_profile"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False, unique=True)
    intent_level: Mapped[str | None] = mapped_column(String(30), nullable=True)
    purchase_power: Mapped[str | None] = mapped_column(String(30), nullable=True)
    category_preference: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    price_preference: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    total_orders: Mapped[int] = mapped_column(default=0)
    total_spent: Mapped[float] = mapped_column(default=0.0)
    avg_order_value: Mapped[float] = mapped_column(default=0.0)
    last_order_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(30), nullable=True)
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
