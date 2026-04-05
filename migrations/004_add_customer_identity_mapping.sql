-- Migration: Add customer_identity_mapping table
-- Version: 004
-- Description: Add table for customer identity mapping to support multiple external identities per customer

CREATE TABLE IF NOT EXISTS customer_identity_mapping (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customer(id),
    source_system VARCHAR(30) NOT NULL DEFAULT 'platform',
    platform VARCHAR(50) NOT NULL,
    account_id VARCHAR(100) NOT NULL DEFAULT '',
    external_user_id VARCHAR(100) NOT NULL,
    external_user_name VARCHAR(120),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    extra_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Unique constraint
ALTER TABLE customer_identity_mapping ADD CONSTRAINT uq_customer_identity 
    UNIQUE (source_system, platform, account_id, external_user_id);

-- Index
CREATE INDEX ix_customer_identity_customer_id ON customer_identity_mapping(customer_id);
