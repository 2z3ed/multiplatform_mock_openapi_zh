CREATE TABLE IF NOT EXISTS training_task (
    id SERIAL PRIMARY KEY,
    task_name VARCHAR(200) NOT NULL,
    task_type VARCHAR(30) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    related_case_id INTEGER REFERENCES training_case(id),
    detail_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_training_task_type ON training_task(task_type);
CREATE INDEX IF NOT EXISTS idx_training_task_status ON training_task(status);
CREATE INDEX IF NOT EXISTS idx_training_task_related_case_id ON training_task(related_case_id);
