-- Migration: 0020_seed_recommendation.sql
-- Description: 为 conv_001 插入推荐商品演示数据
-- Created: 2026-03-29

INSERT INTO recommendation (
    conversation_id,
    customer_id,
    product_id,
    product_name,
    reason,
    suggested_copy,
    status,
    extra_json,
    created_at,
    updated_at
) VALUES
    (
        1,
        1,
        'demo-rec-001',
        '海尔冰箱 BCD-501',
        '用户当前关注冰箱品类，且近期有团购活动',
        '这款海尔冰箱近期活动力度不错，如果您主要关注大容量和性价比，可以优先看看这款',
        'pending',
        NULL,
        NOW(),
        NOW()
    ),
    (
        1,
        1,
        'demo-rec-002',
        '小米洗衣机 12kg',
        '用户存在多品类咨询，适合补充一个洗衣机推荐',
        '如果您也在看洗衣机，这款小米 12kg 目前活动价比较合适，可以一起对比看看',
        'pending',
        NULL,
        NOW(),
        NOW()
    )
ON CONFLICT DO NOTHING;
