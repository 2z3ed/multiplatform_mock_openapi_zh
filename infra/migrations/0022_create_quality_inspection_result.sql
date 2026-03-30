-- Migration: 0022_create_quality_inspection_result.sql
-- Description: 质检结果表 (Quality Inspection Center MVP)
-- Created: 2026-03-29

CREATE TABLE IF NOT EXISTS quality_inspection_result (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversation(id),
    quality_rule_id BIGINT NOT NULL REFERENCES quality_rule(id),
    hit BOOLEAN NOT NULL DEFAULT FALSE,
    severity VARCHAR(20) NOT NULL,
    evidence_json JSONB,
    inspected_at TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_quality_inspection_result_severity CHECK (severity IN ('low', 'medium', 'high'))
);

CREATE INDEX IF NOT EXISTS idx_quality_inspection_result_conversation_id ON quality_inspection_result(conversation_id);
CREATE INDEX IF NOT EXISTS idx_quality_inspection_result_quality_rule_id ON quality_inspection_result(quality_rule_id);
CREATE INDEX IF NOT EXISTS idx_quality_inspection_result_hit ON quality_inspection_result(hit);
CREATE INDEX IF NOT EXISTS idx_quality_inspection_result_severity ON quality_inspection_result(severity);
