-- Migration: 0012_create_follow_up_task.sql
-- Description: 创建跟单任务表 (V2 第一轮)
-- Created: 2026-03-27

CREATE TABLE IF NOT EXISTS follow_up_task (
    id BIGSERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversation(id),
    customer_id INTEGER NOT NULL REFERENCES customer(id),
    order_id VARCHAR(100),
    task_type VARCHAR(30) NOT NULL,
    trigger_source VARCHAR(30) NOT NULL DEFAULT 'manual',
    title VARCHAR(200) NOT NULL,
    description TEXT,
    suggested_copy TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    completed_by VARCHAR(100),
    extra_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_follow_up_task_customer_id ON follow_up_task(customer_id);
CREATE INDEX IF NOT EXISTS idx_follow_up_task_status ON follow_up_task(status);
CREATE INDEX IF NOT EXISTS idx_follow_up_task_task_type ON follow_up_task(task_type);
CREATE INDEX IF NOT EXISTS idx_follow_up_task_conversation_id ON follow_up_task(conversation_id);
