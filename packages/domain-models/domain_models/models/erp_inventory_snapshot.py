from datetime import datetime

from sqlalchemy import JSON, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin

ALLOWED_INVENTORY_STATUSES = {"normal", "low", "out_of_stock"}


class ERPInventorySnapshot(Base, TimestampMixin):
    __tablename__ = "erp_inventory_snapshot"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sku_code: Mapped[str] = mapped_column(String(100), nullable=False)
    warehouse_code: Mapped[str] = mapped_column(String(50), nullable=False)
    available_qty: Mapped[int] = mapped_column(nullable=False, default=0)
    reserved_qty: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")
    source_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
