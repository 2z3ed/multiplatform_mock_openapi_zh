-- Migration: 0021_create_quality_rule.sql
-- Description: 质检规则表 (Quality Inspection Center MVP)
-- Created: 2026-03-29

CREATE TABLE IF NOT EXISTS quality_rule (
    id BIGSERIAL PRIMARY KEY,
    rule_code VARCHAR(50) NOT NULL,
    rule_name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(30) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'medium',
    description TEXT,
    config_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_quality_rule_rule_code UNIQUE (rule_code),
    CONSTRAINT ck_quality_rule_rule_type CHECK (rule_type IN ('slow_reply', 'missed_response', 'forbidden_word')),
    CONSTRAINT ck_quality_rule_severity CHECK (severity IN ('low', 'medium', 'high'))
);

CREATE INDEX IF NOT EXISTS idx_quality_rule_rule_type ON quality_rule(rule_type);
CREATE INDEX IF NOT EXISTS idx_quality_rule_severity ON quality_rule(severity);
