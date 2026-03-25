CREATE TABLE IF NOT EXISTS kb_document (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    source VARCHAR(200),
    content TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'uploaded',
    uploaded_by VARCHAR(100),
    raw_json JSONB,
    extra_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
