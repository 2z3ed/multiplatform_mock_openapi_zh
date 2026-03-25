CREATE TABLE IF NOT EXISTS ai_suggestion (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversation(id),
    intent VARCHAR(40) NOT NULL,
    confidence DOUBLE PRECISION NOT NULL DEFAULT 0,
    suggested_reply TEXT NOT NULL,
    used_tools JSONB,
    risk_level VARCHAR(20) NOT NULL DEFAULT 'low',
    review_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
