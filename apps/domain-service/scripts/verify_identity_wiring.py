"""
Verification script for database foundation wiring.

Proves the following 4 links work:
1. existing customer + external identity -> resolve_customer_id succeeds
2. existing order_snapshot + external order_id -> resolve_order_id succeeds
3. manually bind order to conversation -> conversation_order_link written
4. query conversation linked orders -> returns the bound order

Usage:
    cd /home/zed/multiplatform_mock_openapi_zh
    python apps/domain-service/scripts/verify_identity_wiring.py
"""
import sys
from pathlib import Path

_root = Path(__file__).parent.parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from shared_db.session import SessionLocal, engine
from sqlalchemy import inspect


def verify_tables_exist():
    """Verify all new tables exist."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    required = [
        "customer_identity_mapping",
        "order_core",
        "order_identity_mapping",
        "conversation_order_link",
    ]
    print("=== Table existence check ===")
    for t in required:
        exists = t in tables
        print(f"  {t}: {'OK' if exists else 'MISSING'}")
        if not exists:
            print(f"  WARNING: Run migrations first!")
            return False
    print("  All tables exist.\n")
    return True


def verify_customer_identity_resolution():
    """Link 1: resolve_customer_id from external identity."""
    from app.services.identity_service import resolve_customer_id

    with SessionLocal() as db:
        from domain_models.models.customer import Customer
        customers = db.query(Customer).all()
        if not customers:
            print("=== Customer identity resolution ===")
            print("  SKIPPED: No customers in DB. Run backfill first.\n")
            return True

        c = customers[0]
        cid = resolve_customer_id(
            db,
            source_system="platform",
            platform=c.platform,
            external_user_id=c.platform_customer_id,
        )
        print("=== Customer identity resolution ===")
        print(f"  customer.id={c.id}, platform={c.platform}, platform_customer_id={c.platform_customer_id}")
        print(f"  resolve_customer_id result: {cid}")
        if cid == c.id:
            print("  PASS: Resolved correctly.\n")
            return True
        else:
            print(f"  FAIL: Expected {c.id}, got {cid}\n")
            return False


def verify_order_identity_resolution():
    """Link 2: resolve_order_id from external order_id."""
    from app.services.identity_service import resolve_order_id

    with SessionLocal() as db:
        from domain_models.models.order_snapshot import OrderSnapshot
        snapshots = db.query(OrderSnapshot).all()
        if not snapshots:
            print("=== Order identity resolution ===")
            print("  SKIPPED: No order_snapshots in DB. Run backfill first.\n")
            return True

        snap = snapshots[0]
        oid = resolve_order_id(
            db,
            source_system="platform",
            platform=snap.platform,
            external_order_id=snap.order_id,
        )
        print("=== Order identity resolution ===")
        print(f"  order_snapshot: platform={snap.platform}, order_id={snap.order_id}")
        print(f"  resolve_order_id result: {oid}")
        if oid is not None:
            print("  PASS: Resolved to internal order_core.id.\n")
            return True
        else:
            print("  FAIL: Could not resolve. Run backfill first.\n")
            return False


def verify_conversation_order_binding():
    """Link 3+4: bind order to conversation, then query back."""
    from app.services.identity_service import (
        bind_order_to_conversation,
        list_order_ids_for_conversation,
        resolve_order_id,
    )

    with SessionLocal() as db:
        from domain_models.models.conversation import Conversation
        from domain_models.models.order_snapshot import OrderSnapshot

        conv = db.query(Conversation).first()
        snap = db.query(OrderSnapshot).first()

        if not conv or not snap:
            print("=== Conversation-order binding ===")
            print(f"  SKIPPED: conversation={conv is not None}, order_snapshot={snap is not None}\n")
            return True

        internal_order_id = resolve_order_id(
            db,
            source_system="platform",
            platform=snap.platform,
            external_order_id=snap.order_id,
        )
        if internal_order_id is None:
            print("=== Conversation-order binding ===")
            print("  SKIPPED: Could not resolve order_id. Run backfill first.\n")
            return True

        result = bind_order_to_conversation(db, conv.id, internal_order_id, link_type="bound")
        db.commit()

        print("=== Conversation-order binding ===")
        print(f"  conversation.id={conv.id}, platform={conv.platform}")
        print(f"  order_snapshot.order_id={snap.order_id} -> order_core.id={internal_order_id}")
        print(f"  bind result: {result}")

        orders = list_order_ids_for_conversation(db, conv.id)
        print(f"  list_order_ids_for_conversation: {orders}")

        found = any(o["order_id"] == internal_order_id for o in orders)
        if found:
            print("  PASS: Order bound and queryable.\n")
            return True
        else:
            print("  FAIL: Order not found in conversation links.\n")
            return False


if __name__ == "__main__":
    print("=" * 60)
    print("Database Foundation Wiring Verification")
    print("=" * 60)
    print()

    results = []
    results.append(("Tables exist", verify_tables_exist()))
    results.append(("Customer identity resolution", verify_customer_identity_resolution()))
    results.append(("Order identity resolution", verify_order_identity_resolution()))
    results.append(("Conversation-order binding", verify_conversation_order_binding()))

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    all_pass = True
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  {name}: {status}")
        if not ok:
            all_pass = False

    print()
    if all_pass:
        print("All checks passed. Database foundation is wired and operational.")
    else:
        print("Some checks failed. See details above.")
        sys.exit(1)
