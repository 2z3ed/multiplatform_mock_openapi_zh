-- Migration: Add conversation_order_link table
-- Version: 006
-- Description: Add table for linking conversations to orders

CREATE TABLE IF NOT EXISTS conversation_order_link (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversation(id),
    order_id INTEGER NOT NULL REFERENCES order_core(id),
    link_type VARCHAR(20) NOT NULL DEFAULT 'mentioned',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Unique constraint
ALTER TABLE conversation_order_link ADD CONSTRAINT uq_conversation_order 
    UNIQUE (conversation_id, order_id);

-- Index
CREATE INDEX ix_conversation_order_order_id ON conversation_order_link(order_id);

-- Add platform_conversation_id and source_system columns to conversation if not exists
-- (These may already exist based on conversation.py model inspection)
-- ALTER TABLE conversation ADD COLUMN IF NOT EXISTS platform_conversation_id VARCHAR(100);
-- ALTER TABLE conversation ADD COLUMN IF NOT EXISTS source_system VARCHAR(30) DEFAULT 'platform';
