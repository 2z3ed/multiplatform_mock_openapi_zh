-- Migration: 0016_create_operation_campaign.sql
-- Description: 运营活动表 (Operation Campaign MVP Step 1)
-- Created: 2026-03-28

CREATE TABLE IF NOT EXISTS operation_campaign (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    campaign_type VARCHAR(30) NOT NULL,
    target_description TEXT,
    audience_json JSONB,
    preview_text TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'draft',
    extra_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_operation_campaign_status ON operation_campaign(status);
CREATE INDEX IF NOT EXISTS idx_operation_campaign_campaign_type ON operation_campaign(campaign_type);
CREATE INDEX IF NOT EXISTS idx_operation_campaign_created_at ON operation_campaign(created_at);
