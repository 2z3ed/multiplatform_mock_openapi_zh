"""
Migration 002: order_core + order_identity_mapping + backfill from order_snapshot

- Create order_core table (customer_id nullable=True)
- Create order_identity_mapping table
- Backfill order_core + order_identity_mapping from order_snapshot
"""
import sys
from pathlib import Path

_root = Path(__file__).parent.parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from sqlalchemy import inspect, text
from shared_db.session import engine, SessionLocal


def upgrade():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    with engine.begin() as conn:
        # 1. Create order_core if not exists
        if "order_core" not in existing_tables:
            conn.execute(text("""
                CREATE TABLE order_core (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER,
                    current_status VARCHAR(30) NOT NULL DEFAULT 'unknown',
                    total_amount VARCHAR(32),
                    currency VARCHAR(8),
                    shop_id VARCHAR(100),
                    extra_json JSON,
                    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
                    updated_at DATETIME NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (customer_id) REFERENCES customer(id)
                )
            """))
            conn.execute(text("CREATE INDEX ix_order_core_customer_id ON order_core (customer_id)"))
            print("  [002] Created table: order_core")
        else:
            print("  [002] Table order_core already exists, skipping")

        # 2. Create order_identity_mapping if not exists
        if "order_identity_mapping" not in existing_tables:
            conn.execute(text("""
                CREATE TABLE order_identity_mapping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    source_system VARCHAR(30) NOT NULL DEFAULT 'platform',
                    platform VARCHAR(50) NOT NULL,
                    account_id VARCHAR(100) NOT NULL DEFAULT '',
                    external_order_id VARCHAR(100) NOT NULL,
                    external_status VARCHAR(30),
                    is_primary BOOLEAN NOT NULL DEFAULT 0,
                    extra_json JSON,
                    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
                    updated_at DATETIME NOT NULL DEFAULT (datetime('now')),
                    CONSTRAINT uq_order_identity UNIQUE (source_system, platform, account_id, external_order_id),
                    FOREIGN KEY (order_id) REFERENCES order_core(id)
                )
            """))
            conn.execute(text("CREATE INDEX ix_order_identity_order_id ON order_identity_mapping (order_id)"))
            print("  [002] Created table: order_identity_mapping")
        else:
            print("  [002] Table order_identity_mapping already exists, skipping")

    # 3. Backfill order_core + order_identity_mapping from order_snapshot
    with SessionLocal() as session:
        from domain_models.models.order_snapshot import OrderSnapshot
        from domain_models.models.order_core import OrderCore
        from domain_models.models.order_identity_mapping import OrderIdentityMapping

        snapshots = session.query(OrderSnapshot).all()
        seen = {}  # (platform, order_id) -> order_core_id
        created_orders = 0
        created_mappings = 0

        for snap in snapshots:
            key = (snap.platform, snap.order_id)
            if key not in seen:
                oc = OrderCore(
                    customer_id=snap.customer_id if hasattr(snap, "customer_id") and snap.customer_id else None,
                    current_status=getattr(snap, "status", "unknown") or "unknown",
                    total_amount=getattr(snap, "total_amount", None),
                    currency=getattr(snap, "currency", None),
                    shop_id=None,
                )
                session.add(oc)
                session.flush()
                seen[key] = oc.id
                created_orders += 1

            existing_map = session.query(OrderIdentityMapping).filter_by(
                source_system="platform",
                platform=snap.platform,
                account_id="",
                external_order_id=snap.order_id,
            ).first()
            if not existing_map:
                mapping = OrderIdentityMapping(
                    order_id=seen[key],
                    source_system="platform",
                    platform=snap.platform,
                    account_id="",
                    external_order_id=snap.order_id,
                    external_status=getattr(snap, "status", None),
                    is_primary=True,
                )
                session.add(mapping)
                created_mappings += 1

        session.commit()
        print(f"  [002] Backfilled {created_orders} order_core records, {created_mappings} order_identity_mapping records")


if __name__ == "__main__":
    print("Running migration 002: order_core + order_identity_mapping")
    upgrade()
    print("Migration 002 complete.")
