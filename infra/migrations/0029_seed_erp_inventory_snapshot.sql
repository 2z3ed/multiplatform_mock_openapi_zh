INSERT INTO erp_inventory_snapshot (sku_code, warehouse_code, available_qty, reserved_qty, status, source_json, snapshot_at) VALUES
('SKU001', 'WH-BJ', 100, 10, 'normal', '{"supplier": "supplier_a"}', '2026-03-30 00:00:00+00'),
('SKU002', 'WH-SH', 0, 5, 'out_of_stock', '{"supplier": "supplier_b"}', '2026-03-30 00:00:00+00'),
('SKU003', 'WH-BJ', 5, 3, 'low', '{"supplier": "supplier_a"}', '2026-03-30 00:00:00+00'),
('SKU004', 'WH-GZ', 200, 20, 'normal', '{"supplier": "supplier_c"}', '2026-03-30 00:00:00+00'),
('SKU005', 'WH-SH', 0, 0, 'out_of_stock', '{"supplier": "supplier_b"}', '2026-03-30 00:00:00+00');
