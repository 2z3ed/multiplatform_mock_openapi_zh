CREATE TABLE IF NOT EXISTS erp_inventory_snapshot (
    id SERIAL PRIMARY KEY,
    sku_code VARCHAR(100) NOT NULL,
    warehouse_code VARCHAR(50) NOT NULL,
    available_qty INTEGER NOT NULL DEFAULT 0,
    reserved_qty INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'normal',
    source_json JSONB,
    snapshot_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_erp_inventory_sku_code ON erp_inventory_snapshot(sku_code);
CREATE INDEX IF NOT EXISTS idx_erp_inventory_snapshot_at ON erp_inventory_snapshot(snapshot_at);
