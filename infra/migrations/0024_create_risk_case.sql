-- Migration: 0024_create_risk_case.sql
-- Description: 风险事件表 (Risk Center MVP)
-- Created: 2026-03-29

CREATE TABLE IF NOT EXISTS risk_case (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,
    risk_type VARCHAR(30) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'medium',
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    evidence_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_risk_case_risk_type CHECK (risk_type IN ('complaint_tendency', 'negative_emotion', 'blacklisted_customer', 'other')),
    CONSTRAINT ck_risk_case_severity CHECK (severity IN ('low', 'medium', 'high')),
    CONSTRAINT ck_risk_case_status CHECK (status IN ('open', 'resolved', 'dismissed', 'escalated'))
);

CREATE INDEX IF NOT EXISTS idx_risk_case_conversation_id ON risk_case(conversation_id);
CREATE INDEX IF NOT EXISTS idx_risk_case_customer_id ON risk_case(customer_id);
CREATE INDEX IF NOT EXISTS idx_risk_case_risk_type ON risk_case(risk_type);
CREATE INDEX IF NOT EXISTS idx_risk_case_severity ON risk_case(severity);
CREATE INDEX IF NOT EXISTS idx_risk_case_status ON risk_case(status);
