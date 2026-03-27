-- Migration: 0014_create_customer_profile.sql
-- Description: 客户档案表 (Customer Profile MVP Step 1)
-- Created: 2026-03-27

CREATE TABLE IF NOT EXISTS customer_profile (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL UNIQUE REFERENCES customer(id),
    total_orders INTEGER NOT NULL DEFAULT 0,
    total_spent DECIMAL(12,2) NOT NULL DEFAULT 0.0,
    avg_order_value DECIMAL(12,2) NOT NULL DEFAULT 0.0,
    extra_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_customer_profile_customer_id ON customer_profile(customer_id);
