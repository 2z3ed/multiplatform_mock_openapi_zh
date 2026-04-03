"""
Migration 001: customer_identity_mapping + conversation external identifiers

- Create customer_identity_mapping table
- Add platform_conversation_id to conversation
- Add source_system to conversation
- Backfill customer_identity_mapping from existing customers
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
        # 1. Create customer_identity_mapping if not exists
        if "customer_identity_mapping" not in existing_tables:
            conn.execute(text("""
                CREATE TABLE customer_identity_mapping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    source_system VARCHAR(30) NOT NULL DEFAULT 'platform',
                    platform VARCHAR(50) NOT NULL,
                    account_id VARCHAR(100) NOT NULL DEFAULT '',
                    external_user_id VARCHAR(100) NOT NULL,
                    external_user_name VARCHAR(120),
                    is_primary BOOLEAN NOT NULL DEFAULT 0,
                    extra_json JSON,
                    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
                    updated_at DATETIME NOT NULL DEFAULT (datetime('now')),
                    CONSTRAINT uq_customer_identity UNIQUE (source_system, platform, account_id, external_user_id),
                    FOREIGN KEY (customer_id) REFERENCES customer(id)
                )
            """))
            conn.execute(text("CREATE INDEX ix_customer_identity_customer_id ON customer_identity_mapping (customer_id)"))
            print("  [001] Created table: customer_identity_mapping")
        else:
            print("  [001] Table customer_identity_mapping already exists, skipping")

        # 2. Add platform_conversation_id to conversation if not exists
        if "conversation" in existing_tables:
            cols = [c["name"] for c in inspector.get_columns("conversation")]
            if "platform_conversation_id" not in cols:
                conn.execute(text(
                    "ALTER TABLE conversation ADD COLUMN platform_conversation_id VARCHAR(100)"
                ))
                print("  [001] Added column: conversation.platform_conversation_id")
            else:
                print("  [001] Column conversation.platform_conversation_id already exists, skipping")

            if "source_system" not in cols:
                conn.execute(text(
                    "ALTER TABLE conversation ADD COLUMN source_system VARCHAR(30) DEFAULT 'platform'"
                ))
                print("  [001] Added column: conversation.source_system")
            else:
                print("  [001] Column conversation.source_system already exists, skipping")

    # 3. Backfill customer_identity_mapping from existing customers
    with SessionLocal() as session:
        from domain_models.models.customer import Customer
        from domain_models.models.customer_identity_mapping import CustomerIdentityMapping

        customers = session.query(Customer).all()
        backfilled = 0
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
                backfilled += 1
        session.commit()
        print(f"  [001] Backfilled {backfilled} customer identity mappings")


if __name__ == "__main__":
    print("Running migration 001: customer_identity_mapping")
    upgrade()
    print("Migration 001 complete.")
