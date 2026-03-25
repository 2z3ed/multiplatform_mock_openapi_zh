CREATE TABLE IF NOT EXISTS order_snapshot (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    order_id VARCHAR(100) NOT NULL,
    customer_id BIGINT,
    status VARCHAR(30) NOT NULL,
    total_amount VARCHAR(32),
    currency VARCHAR(8),
    raw_json JSONB,
    extra_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
