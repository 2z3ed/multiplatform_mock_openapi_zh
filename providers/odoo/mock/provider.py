from typing import Any


class OdooMockProvider:
    """Mock provider for Odoo integration.
    
    Returns mock data that maps directly to snapshot create parameters.
    """

    def get_inventory_list(self) -> list[dict[str, Any]]:
        """Return mock inventory data.
        
        Returns list of dicts compatible with ERPInventorySnapshot create.
        """
        return [
            {
                "sku_code": "ODOO-SKU-001",
                "warehouse_code": "ODOO-WH-BJ",
                "available_qty": 100,
                "reserved_qty": 10,
                "status": "normal",
                "source_json": {
                    "odoo_model": "stock.quant",
                    "odoo_id": 1,
                    "product_id": 101,
                    "location_id": 1,
                },
            },
            {
                "sku_code": "ODOO-SKU-002",
                "warehouse_code": "ODOO-WH-SH",
                "available_qty": 5,
                "reserved_qty": 2,
                "status": "low",
                "source_json": {
                    "odoo_model": "stock.quant",
                    "odoo_id": 2,
                    "product_id": 102,
                    "location_id": 2,
                },
            },
        ]

    def get_order_audit_list(self) -> list[dict[str, Any]]:
        """Return mock order audit data.
        
        Returns list of dicts compatible with OrderAuditSnapshot create.
        """
        return [
            {
                "order_id": "ODOO-ORD-001",
                "platform": "odoo",
                "audit_status": "approved",
                "audit_reason": None,
                "source_json": {
                    "odoo_model": "sale.order",
                    "odoo_id": 1,
                    "state": "sale",
                },
            },
            {
                "order_id": "ODOO-ORD-002",
                "platform": "odoo",
                "audit_status": "pending",
                "audit_reason": None,
                "source_json": {
                    "odoo_model": "sale.order",
                    "odoo_id": 2,
                    "state": "draft",
                },
            },
        ]

    def get_order_exception_list(self) -> list[dict[str, Any]]:
        """Return mock order exception data.
        
        Returns list of dicts compatible with OrderExceptionSnapshot create.
        """
        return [
            {
                "order_id": "ODOO-ORD-003",
                "platform": "odoo",
                "exception_type": "delay",
                "exception_status": "open",
                "detail_json": {
                    "odoo_model": "sale.order",
                    "odoo_id": 3,
                    "issue": "shipping_delay",
                    "days_delayed": 3,
                },
            },
            {
                "order_id": "ODOO-ORD-004",
                "platform": "odoo",
                "exception_type": "stockout",
                "exception_status": "processing",
                "detail_json": {
                    "odoo_model": "sale.order",
                    "odoo_id": 4,
                    "issue": "out_of_stock",
                    "missing_sku": "ODOO-SKU-003",
                },
            },
        ]
