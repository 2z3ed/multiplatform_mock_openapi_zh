CREATE TABLE IF NOT EXISTS platform_account (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    provider_mode VARCHAR(20) NOT NULL DEFAULT 'mock',
    config_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
