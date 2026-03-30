-- Migration: 0023_create_quality_alert.sql
-- Description: 质检告警表 (Quality Inspection Center MVP)
-- Created: 2026-03-29

CREATE TABLE IF NOT EXISTS quality_alert (
    id BIGSERIAL PRIMARY KEY,
    quality_inspection_result_id BIGINT NOT NULL REFERENCES quality_inspection_result(id),
    alert_level VARCHAR(20) NOT NULL DEFAULT 'high',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_quality_alert_result_id UNIQUE (quality_inspection_result_id)
);

CREATE INDEX IF NOT EXISTS idx_quality_alert_alert_level ON quality_alert(alert_level);
