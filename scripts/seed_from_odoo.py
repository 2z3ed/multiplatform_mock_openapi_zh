"""
Minimal script to:
1. Connect to Odoo with working credentials (demo/demo)
2. Connect to omni_csx PostgreSQL
3. Pull real sale.order / stock.quant data
4. Create minimal conversations + order bindings
5. Verify the data is queryable
"""
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'providers'))
sys.path.insert(0, os.path.join(BASE_DIR, 'packages', 'shared-db'))
sys.path.insert(0, os.path.join(BASE_DIR, 'packages', 'domain-models'))
sys.path.insert(0, os.path.join(BASE_DIR, 'packages', 'provider-sdk'))
sys.path.insert(0, os.path.join(BASE_DIR, 'packages', 'shared-config'))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps', 'domain-service'))

from xmlrpc.client import ServerProxy
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo"
ODOO_USER = "demo"
ODOO_PASS = "demo"

# Connect to odoo-db container for omni_csx (use Docker IP directly)
DB_URL = "postgresql+psycopg://omni:omni@172.20.0.3:5432/omni_csx"


def _safe_json(val):
    """Convert any Python value to valid JSON string."""
    return json.dumps(val, ensure_ascii=False, default=str)


def _odoo_ref(ref):
    """Convert Odoo XML-RPC reference [id, name] to a clean dict."""
    if isinstance(ref, list) and len(ref) >= 2:
        return {"id": ref[0], "name": str(ref[1])}
    return {"id": ref, "name": str(ref)}


def connect_odoo():
    common = ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
    if not uid:
        raise RuntimeError("Odoo auth failed for demo/demo")
    obj = ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
    print(f"✅ Odoo authenticated: uid={uid}")
    return uid, obj


def connect_db():
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ omni_csx database connected")
    return engine


def pull_sale_orders(obj, uid):
    orders = obj.execute_kw(ODOO_DB, uid, ODOO_PASS, 'sale.order', 'search_read',
        [[['state', 'in', ['sale', 'sent', 'draft']]]],
        {
            'fields': ['id', 'name', 'state', 'amount_total', 'date_order', 'partner_id', 'note'],
            'limit': 20,
            'order': 'date_order DESC',
        }
    )
    print(f"✅ Pulled {len(orders)} sale orders from Odoo")
    return orders


def pull_stock_quants(obj, uid):
    quants = obj.execute_kw(ODOO_DB, uid, ODOO_PASS, 'stock.quant', 'search_read',
        [[]],
        {
            'fields': ['id', 'product_id', 'location_id', 'quantity', 'reserved_quantity'],
            'limit': 50,
        }
    )
    print(f"✅ Pulled {len(quants)} stock quants from Odoo")
    return quants


def pull_stock_picking(obj, uid):
    pickings = obj.execute_kw(ODOO_DB, uid, ODOO_PASS, 'stock.picking', 'search_read',
        [[]],
        {
            'fields': ['id', 'name', 'state', 'origin', 'scheduled_date', 'date_done', 'partner_id'],
            'limit': 30,
        }
    )
    print(f"✅ Pulled {len(pickings)} stock pickings from Odoo")
    return pickings


def seed_inventory(engine, quants):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM erp_inventory_snapshot"))
        for q in quants:
            product = _odoo_ref(q.get('product_id'))
            location = _odoo_ref(q.get('location_id'))
            qty = q.get('quantity', 0)
            reserved = q.get('reserved_quantity', 0)

            if qty <= 0:
                status = 'out_of_stock'
            elif qty < 5:
                status = 'low_stock'
            else:
                status = 'normal'

            conn.execute(text("""
                INSERT INTO erp_inventory_snapshot (
                    sku_code, warehouse_code, available_qty, reserved_qty,
                    status, source_json, snapshot_at, created_at, updated_at
                ) VALUES (
                    :sku_code, :warehouse_code, :available_qty, :reserved_qty,
                    :status, :source_json, :snapshot_at, NOW(), NOW()
                )
            """), {
                'sku_code': f"ODOO_{q['id']}",
                'warehouse_code': location.get('name', 'WH')[:50],
                'available_qty': float(qty),
                'reserved_qty': float(reserved),
                'status': status,
                'source_json': _safe_json({"odoo_id": q["id"], "product": product, "location": location}),
                'snapshot_at': datetime.utcnow().isoformat(),
            })
    print(f"✅ Seeded {len(quants)} inventory snapshots")


def seed_orders(engine, orders):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM order_audit_snapshot"))
        for o in orders:
            state = o.get('state', 'draft')
            if state in ('sale', 'done'):
                audit_status = 'approved'
            elif state == 'sent':
                audit_status = 'pending'
            else:
                audit_status = 'draft'

            conn.execute(text("""
                INSERT INTO order_audit_snapshot (
                    order_id, platform, audit_status, audit_reason,
                    source_json, snapshot_at, created_at, updated_at
                ) VALUES (
                    :order_id, 'odoo', :audit_status, :audit_reason,
                    :source_json, :snapshot_at, NOW(), NOW()
                )
            """), {
                'order_id': o['name'],
                'audit_status': audit_status,
                'audit_reason': f"Odoo sale order state: {state}",
                'source_json': _safe_json({"odoo_id": o["id"], "state": state, "amount": o.get("amount_total", 0)}),
                'snapshot_at': datetime.utcnow().isoformat(),
            })
    print(f"✅ Seeded {len(orders)} order audit snapshots")


def seed_exceptions(engine, pickings):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM order_exception_snapshot"))
        for p in pickings:
            state = p.get('state', '')
            if state in ('cancel', 'done'):
                exc_type = 'cancelled' if state == 'cancel' else 'delay'
                exc_status = state

                conn.execute(text("""
                    INSERT INTO order_exception_snapshot (
                        order_id, exception_type, exception_status,
                        source_json, snapshot_at, created_at, updated_at
                    ) VALUES (
                        :order_id, :exception_type, :exception_status,
                        :source_json, :snapshot_at, NOW(), NOW()
                    )
                """), {
                    'order_id': p.get('origin', p['name']),
                    'exception_type': exc_type,
                    'exception_status': exc_status,
                    'source_json': _safe_json({"odoo_id": p["id"], "name": p["name"], "state": state}),
                    'snapshot_at': datetime.utcnow().isoformat(),
                })
    print(f"✅ Seeded exception snapshots")


def seed_customers(engine, orders):
    """Create minimal customer records from order partners."""
    partners = set()
    for o in orders:
        partner = o.get('partner_id')
        if partner and isinstance(partner, list) and len(partner) > 1:
            partners.add((partner[0], partner[1]))

    customer_ids = {}
    with engine.begin() as conn:
        for pid, pname in partners:
            existing = conn.execute(text(
                "SELECT id FROM customer WHERE platform = 'odoo' AND platform_customer_id = :pid"
            ), {'pid': str(pid)}).fetchone()
            if existing:
                customer_ids[pid] = existing[0]
            else:
                result = conn.execute(text("""
                    INSERT INTO customer (
                        platform, platform_customer_id, display_name,
                        created_at, updated_at
                    ) VALUES (
                        'odoo', :platform_customer_id, :display_name,
                        NOW(), NOW()
                    ) RETURNING id
                """), {
                    'platform_customer_id': str(pid),
                    'display_name': pname[:100],
                })
                customer_ids[pid] = result.scalar()
    print(f"✅ Seeded {len(customer_ids)} customers")
    return customer_ids


def seed_conversations_and_links(engine, orders, customer_ids):
    """Create minimal conversations, order_core records, and bind them."""
    with engine.begin() as conn:
        for i, o in enumerate(orders[:6]):
            partner = o.get('partner_id')
            customer_id = None
            if partner and isinstance(partner, list) and len(partner) > 1:
                customer_id = customer_ids.get(partner[0])

            if not customer_id:
                result = conn.execute(text("""
                    INSERT INTO customer (
                        platform, platform_customer_id, display_name,
                        created_at, updated_at
                    ) VALUES (
                        'odoo', :platform_customer_id, :display_name,
                        NOW(), NOW()
                    ) RETURNING id
                """), {
                    'platform_customer_id': f"auto_{o['id']}",
                    'display_name': f"Customer for {o['name']}",
                })
                customer_id = result.scalar()

            # Create order_core record
            existing_order = conn.execute(text(
                "SELECT id FROM order_core WHERE extra_json->>'odoo_order_name' = :order_name"
            ), {'order_name': o['name']}).fetchone()

            if existing_order:
                order_core_id = existing_order[0]
            else:
                result = conn.execute(text("""
                    INSERT INTO order_core (
                        customer_id, current_status, total_amount, currency,
                        extra_json, created_at, updated_at
                    ) VALUES (
                        :customer_id, :current_status, :total_amount, 'CNY',
                        :extra_json, NOW(), NOW()
                    ) RETURNING id
                """), {
                    'customer_id': customer_id,
                    'current_status': o.get('state', 'draft'),
                    'total_amount': str(o.get('amount_total', 0)),
                    'extra_json': _safe_json({"odoo_order_id": o["id"], "odoo_order_name": o["name"], "date_order": o.get("date_order")}),
                })
                order_core_id = result.scalar()

                # Create order_identity_mapping (required for context aggregation)
                conn.execute(text("""
                    INSERT INTO order_identity_mapping (
                        order_id, source_system, platform, account_id,
                        external_order_id, external_status, is_primary,
                        extra_json, created_at, updated_at
                    ) VALUES (
                        :order_id, 'odoo', 'odoo', 'demo',
                        :external_order_id, :external_status, true,
                        :extra_json, NOW(), NOW()
                    )
                """), {
                    'order_id': order_core_id,
                    'external_order_id': o['name'],
                    'external_status': o.get('state', 'draft'),
                    'extra_json': _safe_json({"odoo_id": o["id"]}),
                })

            # Create conversation
            conv_name = f"Real Odoo Conversation - {o['name']}"
            existing_conv = conn.execute(text(
                "SELECT id FROM conversation WHERE subject = :name"
            ), {'name': conv_name}).fetchone()

            if existing_conv:
                conv_id = existing_conv[0]
            else:
                result = conn.execute(text("""
                    INSERT INTO conversation (
                        platform, customer_id, status, subject,
                        created_at, updated_at
                    ) VALUES (
                        'odoo', :customer_id, 'active', :subject,
                        NOW(), NOW()
                    ) RETURNING id
                """), {
                    'customer_id': customer_id,
                    'subject': conv_name,
                })
                conv_id = result.scalar()

            # Bind conversation to order_core
            existing_link = conn.execute(text(
                "SELECT id FROM conversation_order_link WHERE conversation_id = :conv_id AND order_id = :order_id"
            ), {'conv_id': conv_id, 'order_id': order_core_id}).fetchone()

            if not existing_link:
                conn.execute(text("""
                    INSERT INTO conversation_order_link (
                        conversation_id, order_id, link_type,
                        created_at, updated_at
                    ) VALUES (
                        :conv_id, :order_id, 'direct',
                        NOW(), NOW()
                    )
                """), {
                    'conv_id': conv_id,
                    'order_id': order_core_id,
                })

            print(f"  Conversation #{conv_id} -> Order #{order_core_id} ({o['name']}, {o['state']}, ¥{o.get('amount_total', 0)})")

    print(f"✅ Seeded conversations and order links")


def verify_data(engine):
    """Verify the seeded data."""
    print("\n" + "=" * 60)
    print("Data Verification")
    print("=" * 60)

    with engine.connect() as conn:
        tables = [
            'erp_inventory_snapshot', 'order_audit_snapshot',
            'order_exception_snapshot', 'customer',
            'conversation', 'conversation_order_link',
        ]
        for t in tables:
            count = conn.execute(text(f'SELECT count(*) FROM "{t}"')).scalar()
            print(f"  {t}: {count} rows")

        # Show sample conversations
        rows = conn.execute(text("""
            SELECT c.id, c.subject, c.platform, col.order_id
            FROM conversation c
            LEFT JOIN conversation_order_link col ON c.id = col.conversation_id
            LEFT JOIN order_core oc ON col.order_id = oc.id
            ORDER BY c.id DESC
            LIMIT 6
        """)).fetchall()
        print("\n  Sample conversations:")
        for r in rows:
            print(f"    conv_id={r[0]}, subject={str(r[1])[:40]}, platform={r[2]}, order_core_id={r[3]}")


def main():
    print("=" * 60)
    print("Odoo Real Data Seed Script")
    print("=" * 60)

    # 1. Connect to Odoo
    uid, obj = connect_odoo()

    # 2. Connect to omni_csx
    engine = connect_db()

    # 3. Pull real data
    orders = pull_sale_orders(obj, uid)
    quants = pull_stock_quants(obj, uid)
    pickings = pull_stock_picking(obj, uid)

    if not orders:
        print("⚠️  No sale orders found in Odoo")
        return

    # 4. Seed data
    print("\n" + "=" * 60)
    print("Seeding omni_csx")
    print("=" * 60)

    seed_inventory(engine, quants)
    seed_orders(engine, orders)
    seed_exceptions(engine, pickings)
    customer_ids = seed_customers(engine, orders)
    seed_conversations_and_links(engine, orders, customer_ids)

    # 5. Verify
    verify_data(engine)

    print("\n" + "=" * 60)
    print("✅ Odoo real data seed complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
