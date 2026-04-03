"""
Migration 003: conversation_order_link

- Create conversation_order_link table
- No automatic backfill
"""
import sys
from pathlib import Path

_root = Path(__file__).parent.parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from sqlalchemy import inspect, text
from shared_db.session import engine


def upgrade():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    with engine.begin() as conn:
        if "conversation_order_link" not in existing_tables:
            conn.execute(text("""
                CREATE TABLE conversation_order_link (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    order_id INTEGER NOT NULL,
                    link_type VARCHAR(20) NOT NULL DEFAULT 'mentioned',
                    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
                    CONSTRAINT uq_conversation_order UNIQUE (conversation_id, order_id),
                    FOREIGN KEY (conversation_id) REFERENCES conversation(id),
                    FOREIGN KEY (order_id) REFERENCES order_core(id)
                )
            """))
            conn.execute(text("CREATE INDEX ix_conversation_order_order_id ON conversation_order_link (order_id)"))
            print("  [003] Created table: conversation_order_link")
        else:
            print("  [003] Table conversation_order_link already exists, skipping")


if __name__ == "__main__":
    print("Running migration 003: conversation_order_link")
    upgrade()
    print("Migration 003 complete.")
