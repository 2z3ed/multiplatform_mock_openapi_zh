INSERT INTO order_audit_snapshot (order_id, platform, audit_status, audit_reason, source_json, snapshot_at) VALUES
('ORD001', 'taobao', 'approved', NULL, '{"reviewer": "system"}', '2026-03-30 00:00:00+00'),
('ORD002', 'jd', 'rejected', '地址信息不完整', '{"reviewer": "admin_001"}', '2026-03-30 00:00:00+00'),
('ORD003', 'taobao', 'pending', NULL, '{"reviewer": null}', '2026-03-30 00:00:00+00'),
('ORD004', 'pdd', 'approved', NULL, '{"reviewer": "system"}', '2026-03-30 00:00:00+00'),
('ORD005', 'jd', 'pending', '等待资质审核', '{"reviewer": null}', '2026-03-30 00:00:00+00');
