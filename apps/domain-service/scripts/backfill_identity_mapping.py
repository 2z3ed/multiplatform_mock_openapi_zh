"""
Backfill script: customer identity mapping + order core + order identity mapping.

This script can be run standalone after migrations have created the tables.
It is idempotent: it checks for existing records before creating new ones.

Usage:
    cd /home/zed/multiplatform_mock_openapi_zh
    python apps/domain-service/scripts/backfill_identity_mapping.py
"""
import sys
from pathlib import Path

_root = Path(__file__).parent.parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from shared_db.session import SessionLocal


def backfill_customer_identities():
    """Create customer_identity_mapping records from existing customers."""
    from domain_models.models.customer import Customer
    from domain_models.models.customer_identity_mapping import CustomerIdentityMapping

    with SessionLocal() as session:
        customers = session.query(Customer).all()
        created = 0
        for c in customers:
            existing = session.query(CustomerIdentityMapping).filter_by(
                source_system="platform",
                platform=getattr(c, "platform", ""),
                account_id="",
                external_user_id=getattr(c, "platform_customer_id", ""),
            ).first()
            if not existing:
                mapping = CustomerIdentityMapping(
                    customer_id=c.id,
                    source_system="platform",
                    platform=getattr(c, "platform", ""),
                    account_id="",
                    external_user_id=getattr(c, "platform_customer_id", ""),
                    external_user_name=getattr(c, "display_name", None),
                    is_primary=True,
                )
                session.add(mapping)
                created += 1
        session.commit()
        print(f"  Backfilled {created} customer identity mappings")


def backfill_order_core():
    """Create order_core + order_identity_mapping from order_snapshot."""
    from domain_models.models.order_snapshot import OrderSnapshot
    from domain_models.models.order_core import OrderCore
    from domain_models.models.order_identity_mapping import OrderIdentityMapping

    with SessionLocal() as session:
        snapshots = session.query(OrderSnapshot).all()
        seen = {}  # (platform, order_id) -> order_core_id
        created_orders = 0
        created_mappings = 0

        for snap in snapshots:
            key = (snap.platform, snap.order_id)
            if key not in seen:
                oc = OrderCore(
                    customer_id=getattr(snap, "customer_id", None) or None,
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
        print(f"  Backfilled {created_orders} order_core records, {created_mappings} order_identity_mapping records")


if __name__ == "__main__":
    print("Running backfill: customer identity mappings...")
    backfill_customer_identities()
    print("Running backfill: order_core + order_identity_mapping...")
    backfill_order_core()
    print("Backfill complete.")
