CREATE TABLE IF NOT EXISTS management_dashboard_snapshot (
    id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    metric_value NUMERIC(10, 2) NOT NULL,
    detail_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_metric_type CHECK (metric_type IN ('conversation_count', 'avg_response_time', 'satisfaction_score', 'resolved_case_count'))
);

CREATE INDEX IF NOT EXISTS idx_management_dashboard_snapshot_date ON management_dashboard_snapshot(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_management_dashboard_metric_type ON management_dashboard_snapshot(metric_type);
