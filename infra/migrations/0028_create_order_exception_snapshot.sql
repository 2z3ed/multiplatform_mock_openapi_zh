CREATE TABLE IF NOT EXISTS order_exception_snapshot (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    exception_type VARCHAR(30) NOT NULL,
    exception_status VARCHAR(20) NOT NULL,
    detail_json JSONB,
    snapshot_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_order_exception_order_id ON order_exception_snapshot(order_id);
CREATE INDEX IF NOT EXISTS idx_order_exception_type ON order_exception_snapshot(exception_type);
CREATE INDEX IF NOT EXISTS idx_order_exception_snapshot_at ON order_exception_snapshot(snapshot_at);
