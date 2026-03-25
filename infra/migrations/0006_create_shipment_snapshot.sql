CREATE TABLE IF NOT EXISTS shipment_snapshot (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    order_id VARCHAR(100) NOT NULL,
    shipment_status VARCHAR(30) NOT NULL,
    tracking_no VARCHAR(100),
    carrier VARCHAR(60),
    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    raw_json JSONB,
    extra_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
