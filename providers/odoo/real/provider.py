from typing import Any

from providers.odoo.real.client import OdooClient
from providers.odoo.real.mapper import (
    map_inventory,
    map_order_audit,
    map_order_exception,
    map_order_exception_from_picking,
    is_valid_order_origin,
)


class OdooRealProvider:
    """Real provider for Odoo integration using XML-RPC."""

    def __init__(self, client: OdooClient):
        self._client = client

    def get_inventory_list(self) -> list[dict[str, Any]]:
        """Get inventory list from Odoo stock.quant model.
        
        Returns:
            List of standardized inventory dicts compatible with ERPInventorySnapshot
        """
        quants = self._client.search_read(
            model="stock.quant",
            domain=[],
            fields=["id", "product_id", "location_id", "quantity", "reserved_quantity"],
            limit=100,
        )
        return [map_inventory(q) for q in quants]

    def get_order_audit_list(self) -> list[dict[str, Any]]:
        """Get order audit list from Odoo sale.order model.
        
        Returns:
            List of standardized order audit dicts compatible with OrderAuditSnapshot
        """
        orders = self._client.search_read(
            model="sale.order",
            domain=[],
            fields=["id", "name", "state", "note"],
            limit=100,
        )
        return [map_order_audit(o) for o in orders]

    def _get_order_exceptions_from_picking(self) -> list[dict[str, Any]]:
        """Get order exceptions from Odoo stock.picking model.
        
        Limited Support:
        - Only supports: delay, cancelled
        - Only source: stock.picking
        - Order linking is partial: only when origin matches sale.order.name pattern
        
        Returns:
            List of standardized order exception dicts compatible with OrderExceptionSnapshot
        """
        pickings = self._client.search_read(
            model="stock.picking",
            domain=[],
            fields=[
                "id", "name", "state", "origin", "scheduled_date", "date_done",
                "create_date", "picking_type_id", "partner_id", "note"
            ],
            limit=100,
        )
        
        origins_to_verify = set()
        for picking in pickings:
            origin = picking.get("origin")
            if is_valid_order_origin(origin):
                origins_to_verify.add(origin)
        
        existing_orders = {}
        if origins_to_verify:
            try:
                orders = self._client.search_read(
                    model="sale.order",
                    domain=[("name", "in", list(origins_to_verify))],
                    fields=["name"],
                    limit=len(origins_to_verify),
                )
                existing_orders = {o.get("name") for o in orders}
            except Exception:
                existing_orders = set()
        
        exceptions = []
        for picking in pickings:
            origin = picking.get("origin")
            order_exists = origin in existing_orders
            
            exception = map_order_exception_from_picking(picking, order_exists)
            if exception:
                exceptions.append(exception)
        
        return exceptions

    def get_order_exception_list(self) -> list[dict[str, Any]]:
        """Get order exception list from Odoo.
        
        Primary source: stock.picking (delay, cancelled)
        Fallback: sale.order keyword inference (compatibility)
        
        Limited Support:
        - Only supports: delay, cancelled (from stock.picking)
        - Order linking is partial: only when origin matches sale.order.name pattern
        
        Returns:
            List of standardized order exception dicts compatible with OrderExceptionSnapshot
        """
        try:
            exceptions = self._get_order_exceptions_from_picking()
            if exceptions:
                return exceptions
        except Exception:
            pass
        
        orders = self._client.search_read(
            model="sale.order",
            domain=[],
            fields=["id", "name", "state", "note"],
            limit=100,
        )
        return [map_order_exception(o) for o in orders]
