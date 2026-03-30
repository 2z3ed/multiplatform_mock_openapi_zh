-- Migration: 0025_create_blacklist_customer.sql
-- Description: 黑名单客户表 (Risk Center MVP)
-- Created: 2026-03-29

CREATE TABLE IF NOT EXISTS blacklist_customer (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL UNIQUE,
    reason TEXT,
    source VARCHAR(50) NOT NULL DEFAULT 'manual',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_blacklist_customer_source CHECK (source IN ('manual', 'system', 'complaint'))
);

CREATE INDEX IF NOT EXISTS idx_blacklist_customer_customer_id ON blacklist_customer(customer_id);
CREATE INDEX IF NOT EXISTS idx_blacklist_customer_source ON blacklist_customer(source);
