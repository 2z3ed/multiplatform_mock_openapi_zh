CREATE TABLE IF NOT EXISTS training_case (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversation(id),
    customer_id INTEGER,
    case_title VARCHAR(200) NOT NULL,
    case_summary TEXT,
    case_type VARCHAR(30) NOT NULL,
    source_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_training_case_conversation_id ON training_case(conversation_id);
CREATE INDEX IF NOT EXISTS idx_training_case_type ON training_case(case_type);
