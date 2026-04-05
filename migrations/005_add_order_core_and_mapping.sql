-- Migration: Add order_core and order_identity_mapping tables
-- Version: 005
-- Description: Add unified order core table and identity mapping layer

CREATE TABLE IF NOT EXISTS order_core (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customer(id),
    current_status VARCHAR(30) NOT NULL DEFAULT 'unknown',
    total_amount VARCHAR(32),
    currency VARCHAR(8),
    shop_id VARCHAR(100),
    extra_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index
CREATE INDEX ix_order_core_customer_id ON order_core(customer_id);

-- Order identity mapping
CREATE TABLE IF NOT EXISTS order_identity_mapping (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES order_core(id),
    source_system VARCHAR(30) NOT NULL DEFAULT 'platform',
    platform VARCHAR(50) NOT NULL,
    account_id VARCHAR(100) NOT NULL DEFAULT '',
    external_order_id VARCHAR(100) NOT NULL,
    external_status VARCHAR(30),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    extra_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Unique constraint
ALTER TABLE order_identity_mapping ADD CONSTRAINT uq_order_identity 
    UNIQUE (source_system, platform, account_id, external_order_id);

-- Index
CREATE INDEX ix_order_identity_order_id ON order_identity_mapping(order_id);
