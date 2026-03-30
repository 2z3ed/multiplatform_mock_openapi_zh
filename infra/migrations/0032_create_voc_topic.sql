CREATE TABLE IF NOT EXISTS voc_topic (
    id SERIAL PRIMARY KEY,
    topic_name VARCHAR(200) NOT NULL,
    topic_type VARCHAR(30) NOT NULL,
    source VARCHAR(30) NOT NULL,
    occurrence_count INTEGER NOT NULL DEFAULT 0,
    summary TEXT,
    extra_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_voc_topic_type ON voc_topic(topic_type);
CREATE INDEX IF NOT EXISTS idx_voc_topic_source ON voc_topic(source);
