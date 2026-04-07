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

TB_MESSAGES = [
    {"sender_type": "customer", "sender_id": "tb_cust_mp_001", "content": "你好，我想申请一下这个订单的退货退款"},
    {"sender_type": "agent", "sender_id": "agent_001", "content": "您好，王芳女士。请问退货原因是什么呢？"},
    {"sender_type": "customer", "sender_id": "tb_cust_mp_001", "content": "商品与描述不符，收到的颜色和我下单的不一样"},
    {"sender_type": "agent", "sender_id": "agent_001", "content": "非常抱歉给您带来不好的体验。您的订单已签收，符合 7 天无理由退货条件，我帮您提交退货申请。"},
    {"sender_type": "customer", "sender_id": "tb_cust_mp_001", "content": "好的，那退货流程大概需要多久？"},
    {"sender_type": "agent", "sender_id": "agent_001", "content": "退货申请提交后，商家一般 24 小时内审核。审核通过后您可以预约快递上门取件，退款会在商家签收后 1-3 个工作日原路退回。"},
    {"sender_type": "customer", "sender_id": "tb_cust_mp_001", "content": "好的，那我等审核通过"},
]

DY_MESSAGES = [
    {"sender_type": "customer", "sender_id": "dy_cust_mp_001", "content": "你好，我前天下的单，怎么还没发货呀？"},
    {"sender_type": "agent", "sender_id": "agent_001", "content": "您好，陈先生。抱歉让您久等了，我帮您看一下订单情况。"},
    {"sender_type": "agent", "sender_id": "agent_001", "content": "您的订单已付款成功，目前正在仓库配货中，预计今天内可以发出。"},
    {"sender_type": "customer", "sender_id": "dy_cust_mp_001", "content": "能帮我催一下吗，比较急用"},
    {"sender_type": "agent", "sender_id": "agent_001", "content": "好的，我帮您备注加急处理，发出后会有物流信息更新，您注意查看。"},
    {"sender_type": "customer", "sender_id": "dy_cust_mp_001", "content": "好的，麻烦了"},
]

WC_MESSAGES = [
    {"sender_type": "customer", "sender_id": "wc_cust_mp_001", "content": "你好，请问这款商品有优惠吗？"},
    {"sender_type": "agent", "sender_id": "agent_001", "content": "您好，赵先生。目前这款商品有新品首发的活动，下单立减 30 元。"},
    {"sender_type": "customer", "sender_id": "wc_cust_mp_001", "content": "那这个颜色和黑色有什么区别吗？"},
    {"sender_type": "agent", "sender_id": "agent_001", "content": "颜色区别主要在外观设计，功能和配置是一样的。银色款是本期主推色，库存也比较充足。"},
    {"sender_type": "customer", "sender_id": "wc_cust_mp_001", "content": "好的，那我考虑一下，谢谢"},
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
        "display_name": "淘宝用户-王芳",
        "subject": "申请退货退款咨询",
        "status": "open",
        "order_status": "finished",
        "order_amount": "9999.00",
        "external_order_id": "4728561930472815",  # taobao_user_001, shipped
        "message_content": "你好，我想申请一下这个订单的退货退款",
        "extra_messages": TB_MESSAGES,
        "after_sale": {
            "after_sale_id": "TB_REFUND_4728561930472815",
            "case_type": "refund",
            "status": "processing",
            "reason": "商品与描述不符，申请退货退款",
        },
    },
    {
        "platform": "douyin_shop",
        "customer_id": "dy_cust_mp_001",
        "display_name": "抖音用户-陈浩",
        "subject": "催促订单尽快发货",
        "status": "open",
        "order_status": "paid",
        "order_amount": "159.00",
        "external_order_id": "6847291038472910",  # douyin_user_001, paid
        "message_content": "我前天下的单，怎么还没发货？",
        "extra_messages": DY_MESSAGES,
    },
    {
        "platform": "wecom_kf",
        "customer_id": "wc_cust_mp_001",
        "display_name": "企微用户-赵磊",
        "subject": "商品规格与优惠咨询",
        "status": "open",
        "order_status": "paid",
        "order_amount": "159.00",
        "external_order_id": "WK_ORDER_001",  # wecom_user_001, paid
        "message_content": "请问这款商品有优惠吗？",
        "extra_messages": WC_MESSAGES,
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


MANAGED_CUSTOMER_IDS = (
    "jd_cust_mp_001",
    "tb_cust_mp_001",
    "dy_cust_mp_001",
    "wc_cust_mp_001",
)


def _cleanup_managed_samples(engine) -> None:
    """Delete only the 4 managed demo samples in reverse FK order.

    FK chain:
      message.conversation_id -> conversation.id
      conversation.customer_id -> customer.id
      conversation_order_link.conversation_id -> conversation.id
      conversation_order_link.order_id -> order_core.id
      order_identity_mapping.order_id -> order_core.id
      order_core.customer_id -> customer.id

    Only touches rows reachable from MANAGED_CUSTOMER_IDS.
    """
    placeholders = ",".join(f":c{i}" for i in range(len(MANAGED_CUSTOMER_IDS)))
    params = {f"c{i}": cid for i, cid in enumerate(MANAGED_CUSTOMER_IDS)}

    with engine.begin() as conn:
        # Resolve managed customer DB ids
        rows = conn.execute(text(
            f"SELECT id FROM customer WHERE platform_customer_id IN ({placeholders})"
        ), params).fetchall()
        customer_ids = [r[0] for r in rows]
        if not customer_ids:
            print("  No managed samples to clean up")
            return

        cust_placeholders = ",".join(f":cid{i}" for i in range(len(customer_ids)))
        cust_params = {f"cid{i}": cid for i, cid in enumerate(customer_ids)}

        # Resolve managed conversation ids
        conv_rows = conn.execute(text(
            f"SELECT id FROM conversation WHERE customer_id IN ({cust_placeholders})"
        ), cust_params).fetchall()
        conv_ids = [r[0] for r in conv_rows]
        conv_placeholders = ",".join(f":cvid{i}" for i in range(len(conv_ids))) if conv_ids else "0"
        conv_params = {f"cvid{i}": cid for i, cid in enumerate(conv_ids)} if conv_ids else {}

        # Resolve managed order ids
        order_rows = conn.execute(text(
            f"SELECT id FROM order_core WHERE customer_id IN ({cust_placeholders})"
        ), cust_params).fetchall()
        order_ids = [r[0] for r in order_rows]
        order_placeholders = ",".join(f":oid{i}" for i in range(len(order_ids))) if order_ids else "0"
        order_params = {f"oid{i}": oid for i, oid in enumerate(order_ids)} if order_ids else {}

        # Resolve managed external order ids (for after_sale_case cleanup)
        ext_order_rows = conn.execute(text(
            f"SELECT extra_json->>'external_order_id' FROM order_core WHERE customer_id IN ({cust_placeholders})"
        ), cust_params).fetchall()
        ext_order_ids = [r[0] for r in ext_order_rows if r[0]]
        ext_order_placeholders = ",".join(f":eoid{i}" for i in range(len(ext_order_ids))) if ext_order_ids else "''"
        ext_order_params = {f"eoid{i}": oid for i, oid in enumerate(ext_order_ids)} if ext_order_ids else {}

        # 1. Messages via managed conversations
        if conv_ids:
            result = conn.execute(text(
                f"DELETE FROM message WHERE conversation_id IN ({conv_placeholders})"
            ), conv_params)
            if result.rowcount:
                print(f"  Deleted {result.rowcount} managed messages")

        # 2. Conversation-order links via managed conversations
        if conv_ids:
            result = conn.execute(text(
                f"DELETE FROM conversation_order_link WHERE conversation_id IN ({conv_placeholders})"
            ), conv_params)
            if result.rowcount:
                print(f"  Deleted {result.rowcount} managed conversation_order_links")

        # 3. Order identity mappings via managed orders
        if order_ids:
            result = conn.execute(text(
                f"DELETE FROM order_identity_mapping WHERE order_id IN ({order_placeholders})"
            ), order_params)
            if result.rowcount:
                print(f"  Deleted {result.rowcount} managed order_identity_mappings")

        # 3b. After-sale cases via managed external order ids
        if ext_order_ids:
            result = conn.execute(text(
                f"DELETE FROM after_sale_case WHERE order_id IN ({ext_order_placeholders})"
            ), ext_order_params)
            if result.rowcount:
                print(f"  Deleted {result.rowcount} managed after_sale_cases")

        # 4. Conversations
        if conv_ids:
            result = conn.execute(text(
                f"DELETE FROM conversation WHERE id IN ({conv_placeholders})"
            ), conv_params)
            if result.rowcount:
                print(f"  Deleted {result.rowcount} managed conversations")

        # 5. Order cores
        if order_ids:
            result = conn.execute(text(
                f"DELETE FROM order_core WHERE id IN ({order_placeholders})"
            ), order_params)
            if result.rowcount:
                print(f"  Deleted {result.rowcount} managed order_cores")

        # 6. Customers
        result = conn.execute(text(
            f"DELETE FROM customer WHERE id IN ({cust_placeholders})"
        ), cust_params)
        if result.rowcount:
            print(f"  Deleted {result.rowcount} managed customers")
        else:
            print("  No managed samples to clean up")


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

        # 8. After-sale case (for taobao refund-themed sample)
        after_sale = sample.get("after_sale")
        if after_sale:
            existing_as = conn.execute(text(
                "SELECT id FROM after_sale_case WHERE platform = :p AND after_sale_id = :asid"
            ), {"p": platform, "asid": after_sale["after_sale_id"]}).fetchone()
            if existing_as:
                print(f"  AfterSaleCase already exists")
            else:
                conn.execute(text("""
                    INSERT INTO after_sale_case (
                        platform, after_sale_id, order_id, case_type, status, reason,
                        created_at, updated_at
                    ) VALUES (
                        :platform, :after_sale_id, :order_id, :case_type, :status, :reason,
                        NOW(), NOW()
                    )
                """), {
                    "platform": platform,
                    "after_sale_id": after_sale["after_sale_id"],
                    "order_id": sample["external_order_id"],
                    "case_type": after_sale["case_type"],
                    "status": after_sale["status"],
                    "reason": after_sale["reason"],
                })
                print(f"  AfterSaleCase created ({after_sale['after_sale_id']})")


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

    # Clean up managed demo samples so they can be reseeded with latest definitions
    print("\n--- Cleaning up managed samples ---")
    _cleanup_managed_samples(engine)

    # Fix any out-of-sync sequences (happens when data was inserted with explicit IDs)
    fix_sequences(engine)

    # Reseed managed samples
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
