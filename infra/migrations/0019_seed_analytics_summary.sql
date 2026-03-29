-- Migration: 0019_seed_analytics_summary.sql
-- Description: 为 analytics_summary 表插入演示数据
-- Created: 2026-03-29

INSERT INTO analytics_summary (
    stat_date,
    recommendation_created_count,
    recommendation_accepted_count,
    followup_executed_count,
    followup_closed_count,
    operation_campaign_completed_count,
    extra_json,
    created_at,
    updated_at
) VALUES
    (
        '2026-03-28',
        3,
        1,
        2,
        1,
        1,
        NULL,
        NOW(),
        NOW()
    ),
    (
        '2026-03-29',
        2,
        1,
        1,
        1,
        0,
        NULL,
        NOW(),
        NOW()
    )
ON CONFLICT (stat_date) DO NOTHING;
