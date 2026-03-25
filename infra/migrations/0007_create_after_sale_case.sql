CREATE TABLE IF NOT EXISTS after_sale_case (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    after_sale_id VARCHAR(100) NOT NULL,
    order_id VARCHAR(100),
    case_type VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL,
    reason TEXT,
    raw_json JSONB,
    extra_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
