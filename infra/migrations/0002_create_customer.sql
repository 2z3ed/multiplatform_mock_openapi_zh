CREATE TABLE IF NOT EXISTS customer (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    platform_customer_id VARCHAR(100) NOT NULL,
    display_name VARCHAR(120),
    raw_json JSONB,
    extra_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
