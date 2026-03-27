-- Migration: 0013_create_customer_tag.sql
-- Description: 客户标签表 (Customer Tags MVP Step 1)
-- Created: 2026-03-27

CREATE TABLE IF NOT EXISTS customer_tag (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customer(id),
    tag_type VARCHAR(30) NOT NULL,
    tag_value VARCHAR(100) NOT NULL,
    source VARCHAR(30) NOT NULL DEFAULT 'manual',
    extra_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_customer_tag_unique UNIQUE (customer_id, tag_type, tag_value)
);

CREATE INDEX IF NOT EXISTS idx_customer_tag_customer_id ON customer_tag(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_tag_tag_type ON customer_tag(tag_type);
