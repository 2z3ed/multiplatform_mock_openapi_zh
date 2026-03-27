from decimal import Decimal
from sqlalchemy import ForeignKey, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class CustomerProfile(Base, TimestampMixin):
    __tablename__ = "customer_profile"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False, unique=True)
    total_orders: Mapped[int] = mapped_column(default=0)
    total_spent: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    avg_order_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
