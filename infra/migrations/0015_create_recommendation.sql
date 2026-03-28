-- Migration: 0015_create_recommendation.sql
-- Description: 推荐记录表 (Recommendation MVP Step 1)
-- Created: 2026-03-28

CREATE TABLE IF NOT EXISTS recommendation (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversation(id),
    customer_id BIGINT NOT NULL REFERENCES customer(id),
    product_id VARCHAR(100) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    reason TEXT,
    suggested_copy TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    extra_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recommendation_conversation_id ON recommendation(conversation_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_customer_id ON recommendation(customer_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_status ON recommendation(status);
CREATE INDEX IF NOT EXISTS idx_recommendation_created_at ON recommendation(created_at);
