-- Migration: 0018_create_risk_flag.sql
-- Description: 风险标记表 (Risk Flags MVP Step 1)
-- Created: 2026-03-28

CREATE TABLE IF NOT EXISTS risk_flag (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customer(id),
    conversation_id BIGINT REFERENCES conversation(id),
    risk_type VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL DEFAULT 'low',
    description VARCHAR(500),
    extra_json JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_risk_flag_customer_id ON risk_flag(customer_id);
CREATE INDEX IF NOT EXISTS idx_risk_flag_conversation_id ON risk_flag(conversation_id);
CREATE INDEX IF NOT EXISTS idx_risk_flag_risk_type ON risk_flag(risk_type);
CREATE INDEX IF NOT EXISTS idx_risk_flag_status ON risk_flag(status);
CREATE INDEX IF NOT EXISTS idx_risk_flag_created_at ON risk_flag(created_at);
