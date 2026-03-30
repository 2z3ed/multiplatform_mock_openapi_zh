CREATE TABLE IF NOT EXISTS order_audit_snapshot (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    audit_status VARCHAR(20) NOT NULL,
    audit_reason VARCHAR(500),
    source_json JSONB,
    snapshot_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_order_audit_order_id ON order_audit_snapshot(order_id);
CREATE INDEX IF NOT EXISTS idx_order_audit_snapshot_at ON order_audit_snapshot(snapshot_at);
