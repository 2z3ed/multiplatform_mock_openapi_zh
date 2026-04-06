"""
Seed multi-platform test conversations into the Omni-CSX database.

Creates minimal but complete conversation chains for:
  jd, taobao, douyin_shop, wecom_kf

Each platform gets 1 conversation with:
  customer → conversation → order_core → order_identity_mapping
  → conversation_order_link → message

external_order_id values are taken from official-sim fixture files
so that mock providers can resolve them via HTTP.

Idempotent: safe to re-run without duplicating data.

Usage:
    python3 scripts/seed_multi_platform_conversations.py
"""
import json
import os
import sys
from datetime import datetime, timezone

# Add project paths for model imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'packages', 'shared-db'))
sys.path.insert(0, os.path.join(BASE_DIR, 'packages', 'domain-models'))
sys.path.insert(0, os.path.join(BASE_DIR, 'packages', 'provider-sdk'))
sys.path.insert(0, os.path.join(BASE_DIR, 'packages', 'shared-config'))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps', 'domain-service'))

from sqlalchemy import create_engine, text
from shared_db.base import Base
# Import models so they register with Base.metadata
from domain_models.models import (
    Customer, Conversation, Message,
    OrderCore, OrderIdentityMapping, ConversationOrderLink,
    AfterSaleCase,
)


# ---------------------------------------------------------------------------
# DB connection (reuse same env vars as seed_from_odoo.py)
# ---------------------------------------------------------------------------
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "omni_csx")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def _safe_json(obj):
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return "{}"


# ---------------------------------------------------------------------------
# Platform sample definitions
# ---------------------------------------------------------------------------
# external_order_id MUST match an order_id in official-sim fixtures so that
# the mock provider can resolve it via HTTP to official-sim-server.
#
# subject is kept generic (order / logistics inquiry) to avoid needing
# after_sale_case records.  If you want a refund-themed sample, add a
# corresponding after_sale_case row.

JD_MESSAGES = [
    {"sender_type": "customer", "sender_id": "jd_cust_mp_001", "content": "你好，我想问一下订单 304857291638 什么时候发货？"},
    {"sender_type": "agent", "sender_id": "agent_001", "content": "您好，李明先生。我帮您查一下，请稍等。"},
    {"sender_type": "agent", "sender_id": "agent_001", "content": "您的订单已付款，目前待发货，预计今天内可以发出。"},
    {"sender_type": "customer", "sender_id": "jd_cust_mp_001", "content": "好的，那大概什么时候能到呢？"},
    {"sender_type": "agent", "sender_id": "agent_001", "content": "从北京仓发出到深圳，正常情况下明天下午就能到。您收到后有任何问题随时联系我们。"},
    {"sender_type": "customer", "sender_id": "jd_cust_mp_001", "content": "好的，谢谢"},
    {"sender_type": "agent", "sender_id": "agent_001", "content": "不客气，祝您生活愉快！有需要随时找我。"},
]

SAMPLES = [
    {
        "platform": "jd",
        "customer_id": "jd_cust_mp_001",
        "display_name": "京东用户-李明",
        "subject": "咨询订单发货",
        "status": "open",
        "order_status": "paid",
        "order_amount": "9999.00",
        "external_order_id": "304857291638",  # jd_user_001, paid order
        "message_content": "请问我的订单什么时候发货？",
        "extra_messages": JD_MESSAGES,
    },
    {
        "platform": "taobao",
        "customer_id": "tb_cust_mp_001",
        "display_name": "淘宝用户",
        "subject": "咨询物流信息",
        "status": "open",
        "order_status": "finished",
        "order_amount": "9999.00",
        "external_order_id": "4728561930472815",  # taobao_user_001, shipped
        "message_content": "帮我查一下这个订单的物流",
    },
    {
        "platform": "douyin_shop",
        "customer_id": "dy_cust_mp_001",
        "display_name": "抖音用户",
        "subject": "咨询订单状态",
        "status": "open",
        "order_status": "paid",
        "order_amount": "159.00",
        "external_order_id": "6847291038472910",  # douyin_user_001, paid
        "message_content": "我的订单现在是什么状态？",
    },
    {
        "platform": "wecom_kf",
        "customer_id": "wc_cust_mp_001",
        "display_name": "企微用户",
        "subject": "售后服务咨询",
        "status": "open",
        "order_status": "paid",
        "order_amount": "159.00",
        "external_order_id": "WK_ORDER_001",  # wecom_user_001, paid
        "message_content": "请问售后服务怎么办理？",
    },
]

# link_type: use 'primary' which is in ALLOWED_LINK_TYPES and semantically
# indicates this is the main order for the conversation.
LINK_TYPE = "primary"


def fix_sequences(engine) -> None:
    """Ensure all sequences are in sync with max(id) values."""
    for table in ("customer", "conversation", "order_core", "order_identity_mapping",
                   "conversation_order_link", "message", "after_sale_case"):
        try:
            with engine.connect() as conn:
                max_id = conn.execute(text(
                    f"SELECT COALESCE(MAX(id), 0) FROM {table}"
                )).scalar()
                conn.execute(text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), GREATEST({max_id}, 1))"
                ))
                conn.commit()
        except Exception:
            pass  # Table may not exist yet


def seed_platform(engine, sample: dict) -> None:
    """Seed one platform sample idempotently."""
    platform = sample["platform"]
    print(f"\n--- Seeding {platform} ---")

    with engine.begin() as conn:
        # 1. Customer
        existing = conn.execute(text(
            "SELECT id FROM customer WHERE platform = :p AND platform_customer_id = :cid"
        ), {"p": platform, "cid": sample["customer_id"]}).fetchone()
        if existing:
            customer_db_id = existing[0]
            print(f"  Customer already exists (id={customer_db_id})")
        else:
            result = conn.execute(text("""
                INSERT INTO customer (
                    platform, platform_customer_id, display_name,
                    created_at, updated_at
                ) VALUES (
                    :platform, :platform_customer_id, :display_name,
                    NOW(), NOW()
                ) RETURNING id
            """), {
                "platform": platform,
                "platform_customer_id": sample["customer_id"],
                "display_name": sample["display_name"],
            })
            customer_db_id = result.scalar()
            print(f"  Customer created (id={customer_db_id})")

        # 2. Order core
        existing_order = conn.execute(text(
            "SELECT id FROM order_core WHERE extra_json->>'seed_platform' = :p AND extra_json->>'seed_customer_id' = :cid"
        ), {"p": platform, "cid": sample["customer_id"]}).fetchone()
        if existing_order:
            order_core_id = existing_order[0]
            print(f"  OrderCore already exists (id={order_core_id})")
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
                "customer_id": customer_db_id,
                "current_status": sample["order_status"],
                "total_amount": sample["order_amount"],
                "extra_json": _safe_json({
                    "seed_platform": platform,
                    "seed_customer_id": sample["customer_id"],
                    "external_order_id": sample["external_order_id"],
                }),
            })
            order_core_id = result.scalar()
            print(f"  OrderCore created (id={order_core_id})")

        # 3. Order identity mapping
        existing_ident = conn.execute(text(
            "SELECT id FROM order_identity_mapping WHERE platform = :p AND external_order_id = :eid"
        ), {"p": platform, "eid": sample["external_order_id"]}).fetchone()
        if existing_ident:
            print(f"  OrderIdentityMapping already exists")
        else:
            conn.execute(text("""
                INSERT INTO order_identity_mapping (
                    order_id, source_system, platform, account_id,
                    external_order_id, external_status, is_primary,
                    extra_json, created_at, updated_at
                ) VALUES (
                    :order_id, 'platform', :platform, '',
                    :external_order_id, :external_status, true,
                    :extra_json, NOW(), NOW()
                )
            """), {
                "order_id": order_core_id,
                "platform": platform,
                "external_order_id": sample["external_order_id"],
                "external_status": sample["order_status"],
                "extra_json": _safe_json({"seed": True}),
            })
            print(f"  OrderIdentityMapping created")

        # 4. Conversation
        existing_conv = conn.execute(text(
            "SELECT id FROM conversation WHERE platform = :p AND subject = :subj"
        ), {"p": platform, "subj": sample["subject"]}).fetchone()
        if existing_conv:
            conv_id = existing_conv[0]
            print(f"  Conversation already exists (id={conv_id})")
        else:
            result = conn.execute(text("""
                INSERT INTO conversation (
                    platform, customer_id, status, subject,
                    created_at, updated_at
                ) VALUES (
                    :platform, :customer_id, :status, :subject,
                    NOW(), NOW()
                ) RETURNING id
            """), {
                "platform": platform,
                "customer_id": customer_db_id,
                "status": sample["status"],
                "subject": sample["subject"],
            })
            conv_id = result.scalar()
            print(f"  Conversation created (id={conv_id})")

        # 5. Conversation-order link
        existing_link = conn.execute(text(
            "SELECT id FROM conversation_order_link WHERE conversation_id = :cid AND order_id = :oid"
        ), {"cid": conv_id, "oid": order_core_id}).fetchone()
        if existing_link:
            print(f"  ConversationOrderLink already exists")
        else:
            conn.execute(text("""
                INSERT INTO conversation_order_link (
                    conversation_id, order_id, link_type,
                    created_at, updated_at
                ) VALUES (
                    :conv_id, :order_id, :link_type,
                    NOW(), NOW()
                )
            """), {
                "conv_id": conv_id,
                "order_id": order_core_id,
                "link_type": LINK_TYPE,
            })
            print(f"  ConversationOrderLink created")

        # 6. Message (first customer message)
        existing_msg = conn.execute(text(
            "SELECT id FROM message WHERE conversation_id = :cid AND sender_type = 'customer'"
        ), {"cid": conv_id}).fetchone()
        if existing_msg:
            print(f"  Message already exists")
        else:
            conn.execute(text("""
                INSERT INTO message (
                    conversation_id, sender_type, sender_id, content,
                    sent_at, created_at, updated_at
                ) VALUES (
                    :conv_id, 'customer', :sender_id, :content,
                    NOW(), NOW(), NOW()
                )
            """), {
                "conv_id": conv_id,
                "sender_id": sample["customer_id"],
                "content": sample["message_content"],
            })
            print(f"  Message created")

        # 7. Extra messages (for JD canonical conversation)
        extra_messages = sample.get("extra_messages", [])
        if extra_messages:
            for i, msg in enumerate(extra_messages):
                existing_extra = conn.execute(text(
                    "SELECT id FROM message WHERE conversation_id = :cid AND content = :content AND sender_type = :st"
                ), {"cid": conv_id, "content": msg["content"], "st": msg["sender_type"]}).fetchone()
                if existing_extra:
                    print(f"  Extra message {i+1} already exists, skipping")
                else:
                    offset_minutes = (i + 1) * 5
                    conn.execute(text("""
                        INSERT INTO message (
                            conversation_id, sender_type, sender_id, content,
                            sent_at, created_at, updated_at
                        ) VALUES (
                            :conv_id, :sender_type, :sender_id, :content,
                            NOW() - INTERVAL '%s minutes', NOW(), NOW()
                        )
                    """ % offset_minutes), {
                        "conv_id": conv_id,
                        "sender_type": msg["sender_type"],
                        "sender_id": msg["sender_id"],
                        "content": msg["content"],
                    })
                    print(f"  Extra message {i+1} created ({msg['sender_type']}: {msg['content'][:30]}...)")


def ensure_tables(engine) -> None:
    """Create any missing tables (order_core, order_identity_mapping, conversation_order_link)."""
    # Only create tables that don't have migration files but are defined in models
    with engine.connect() as conn:
        existing = set(r[0] for r in conn.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )).fetchall())
    missing = []
    for table_name in ("order_core", "order_identity_mapping", "conversation_order_link"):
        if table_name not in existing:
            missing.append(table_name)
    if missing:
        print(f"  Creating missing tables: {', '.join(missing)}")
        for tname in missing:
            table = Base.metadata.tables.get(tname)
            if table is not None:
                table.create(engine, checkfirst=True)
        print(f"  ✅ Tables created")
    else:
        print(f"  All required tables exist")


def main():
    print("=" * 60)
    print("Seed Multi-Platform Test Conversations")
    print("=" * 60)

    engine = create_engine(DATABASE_URL)

    # Ensure all required tables exist
    ensure_tables(engine)

    # Fix any out-of-sync sequences (happens when data was inserted with explicit IDs)
    fix_sequences(engine)

    for sample in SAMPLES:
        seed_platform(engine, sample)

    # Quick verification
    print("\n" + "=" * 60)
    print("Verification")
    print("=" * 60)

    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT id, platform, status, subject FROM conversation ORDER BY id DESC LIMIT 10"
        )).fetchall()
        print(f"\nLatest conversations ({len(rows)} rows):")
        for r in rows:
            print(f"  #{r[0]} | {r[1]:15s} | {r[2]:8s} | {r[3]}")

        # Count by platform
        rows2 = conn.execute(text(
            "SELECT platform, COUNT(*) FROM conversation GROUP BY platform ORDER BY platform"
        )).fetchall()
        print(f"\nConversations by platform:")
        for r in rows2:
            print(f"  {r[0]:15s} : {r[1]}")

        # Count messages
        msg_count = conn.execute(text(
            "SELECT COUNT(*) FROM message WHERE sender_type = 'customer'"
        )).scalar()
        print(f"\nCustomer messages: {msg_count}")

    print("\n✅ Done.")


if __name__ == "__main__":
    main()
