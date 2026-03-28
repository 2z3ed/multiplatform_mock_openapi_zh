-- Migration: 0017_create_analytics_summary.sql
-- Description: 运营指标日聚合表 (Analytics MVP Step 1)
-- Created: 2026-03-28

CREATE TABLE IF NOT EXISTS analytics_summary (
    id BIGSERIAL PRIMARY KEY,
    stat_date DATE NOT NULL UNIQUE,
    recommendation_created_count INTEGER NOT NULL DEFAULT 0,
    recommendation_accepted_count INTEGER NOT NULL DEFAULT 0,
    followup_executed_count INTEGER NOT NULL DEFAULT 0,
    followup_closed_count INTEGER NOT NULL DEFAULT 0,
    operation_campaign_completed_count INTEGER NOT NULL DEFAULT 0,
    extra_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analytics_summary_created_at ON analytics_summary(created_at);
