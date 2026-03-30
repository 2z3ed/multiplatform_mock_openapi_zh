INSERT INTO order_exception_snapshot (order_id, platform, exception_type, exception_status, detail_json, snapshot_at) VALUES
('ORD006', 'taobao', 'delay', 'open', '{"expected_date": "2026-03-25", "reason": "物流延误"}', '2026-03-30 00:00:00+00'),
('ORD007', 'jd', 'stockout', 'processing', '{"sku_code": "SKU002", "expected_restock": "2026-04-05"}', '2026-03-30 00:00:00+00'),
('ORD008', 'taobao', 'address', 'resolved', '{"issue": "地址模糊", "resolution": "客户补充"}', '2026-03-30 00:00:00+00'),
('ORD009', 'pdd', 'customs', 'open', '{"issue": "清关资料不全", "required_docs": ["invoice", "id_copy"]}', '2026-03-30 00:00:00+00'),
('ORD010', 'taobao', 'other', 'cancelled', '{"issue": "客户取消订单", "cancelled_at": "2026-03-29"}', '2026-03-30 00:00:00+00');
