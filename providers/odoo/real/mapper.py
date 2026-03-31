from typing import Any, Optional
from datetime import datetime
import re


ORDER_NAME_PATTERN = re.compile(r"^S\d{5,}$")


def map_inventory(quant: dict[str, Any]) -> dict[str, Any]:
    """Map Odoo stock.quant to Omni-CSX inventory structure.
    
    Args:
        quant: Odoo stock.quant record
        
    Returns:
        Standardized inventory dict compatible with ERPInventorySnapshot
    """
    product_id = quant.get("product_id", [])
    product_name = product_id[1] if isinstance(product_id, list) and len(product_id) > 1 else str(product_id)
    product_code = product_id[0] if isinstance(product_id, list) and len(product_id) > 0 else "UNKNOWN"
    
    location_id = quant.get("location_id", [])
    location_name = location_id[1] if isinstance(location_id, list) and len(location_id) > 1 else str(location_id)
    
    quantity = quant.get("quantity", 0) or 0
    reserved = quant.get("reserved_quantity", 0) or 0
    available = quantity - reserved
    
    if available <= 0:
        status = "out_of_stock"
    elif available < 10:
        status = "low"
    else:
        status = "normal"
    
    return {
        "sku_code": product_name or f"ODOO-PRODUCT-{product_code}",
        "warehouse_code": location_name or "ODOO-WH-DEFAULT",
        "available_qty": available,
        "reserved_qty": reserved,
        "status": status,
        "source_json": {
            "odoo_model": "stock.quant",
            "odoo_id": quant.get("id"),
            "product_id": product_id,
            "location_id": location_id,
            "quantity": quantity,
        },
    }


def map_order_audit(order: dict[str, Any]) -> dict[str, Any]:
    """Map Odoo sale.order to Omni-CSX order audit structure.
    
    Args:
        order: Odoo sale.order record
        
    Returns:
        Standardized order audit dict compatible with OrderAuditSnapshot
    """
    state = order.get("state", "draft")
    
    state_mapping = {
        "draft": "pending",
        "sent": "pending",
        "sale": "approved",
        "done": "approved",
        "cancel": "rejected",
    }
    audit_status = state_mapping.get(state, "pending")
    
    audit_reason = None
    if state == "cancel":
        audit_reason = order.get("note") or "Order cancelled"
    
    return {
        "order_id": order.get("name", f"ODOO-ORD-{order.get('id')}"),
        "platform": "odoo",
        "audit_status": audit_status,
        "audit_reason": audit_reason,
        "source_json": {
            "odoo_model": "sale.order",
            "odoo_id": order.get("id"),
            "name": order.get("name"),
            "state": state,
        },
    }


def map_order_exception(order: dict[str, Any]) -> dict[str, Any]:
    """Map Odoo sale.order to Omni-CSX order exception structure.
    
    Note: This is a simplified mapping. In real Odoo, exceptions would be
    identified based on specific conditions like delivery delays, stock issues, etc.
    
    Args:
        order: Odoo sale.order record
        
    Returns:
        Standardized order exception dict compatible with OrderExceptionSnapshot
    """
    state = order.get("state", "draft")
    note = order.get("note") or ""
    
    exception_type = "other"
    exception_status = "open"
    
    if "delay" in note.lower() or "late" in note.lower():
        exception_type = "delay"
    elif "stock" in note.lower() or "out of stock" in note.lower():
        exception_type = "stockout"
    elif "address" in note.lower():
        exception_type = "address"
    elif "customs" in note.lower():
        exception_type = "customs"
    
    return {
        "order_id": order.get("name", f"ODOO-ORD-{order.get('id')}"),
        "platform": "odoo",
        "exception_type": exception_type,
        "exception_status": exception_status,
        "detail_json": {
            "odoo_model": "sale.order",
            "odoo_id": order.get("id"),
            "name": order.get("name"),
            "state": state,
            "note": note,
        },
    }


def is_valid_order_origin(origin: Optional[str]) -> bool:
    """Check if origin matches sale.order.name pattern.
    
    Args:
        origin: The origin field from stock.picking
        
    Returns:
        True if origin matches order name pattern (e.g., S00038)
    """
    if not origin or not isinstance(origin, str):
        return False
    return bool(ORDER_NAME_PATTERN.match(origin))


def parse_datetime(value: Any) -> Optional[datetime]:
    """Parse datetime from various formats.
    
    Args:
        value: Datetime value (str, datetime, or None)
        
    Returns:
        Parsed datetime or None
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None
    return None


def map_order_exception_from_picking(
    picking: dict[str, Any],
    order_exists: bool = True,
) -> Optional[dict[str, Any]]:
    """Map Odoo stock.picking to Omni-CSX order exception structure.
    
    Limited Support:
    - Only supports: delay, cancelled
    - Only source: stock.picking
    - Order linking is partial: only when origin matches sale.order.name pattern
    
    Args:
        picking: Odoo stock.picking record
        order_exists: Whether the order exists in sale.order (verified externally)
        
    Returns:
        Standardized order exception dict compatible with OrderExceptionSnapshot,
        or None if no exception signal detected or order cannot be linked.
    """
    origin = picking.get("origin")
    
    if not is_valid_order_origin(origin):
        return None
    
    if not order_exists:
        return None
    
    state = picking.get("state", "")
    scheduled_date = parse_datetime(picking.get("scheduled_date"))
    date_done = parse_datetime(picking.get("date_done"))
    create_date = parse_datetime(picking.get("create_date"))
    
    exception_type = None
    exception_status = None
    detected_at = None
    delay_seconds = 0
    
    if state == "done" and scheduled_date and date_done:
        if date_done > scheduled_date:
            exception_type = "delay"
            exception_status = "resolved"
            detected_at = date_done
            delay_seconds = int((date_done - scheduled_date).total_seconds())
    
    if state == "cancel":
        exception_type = "cancelled"
        exception_status = "cancelled"
        detected_at = create_date
    
    if not exception_type:
        return None
    
    picking_name = picking.get("name", "")
    picking_type_id = picking.get("picking_type_id", [])
    partner_id = picking.get("partner_id", [])
    note = picking.get("note") or ""
    
    return {
        "order_id": origin,
        "platform": "odoo",
        "exception_type": exception_type,
        "exception_status": exception_status,
        "detail_json": {
            "odoo_model": "stock.picking",
            "odoo_id": picking.get("id"),
            "picking_name": picking_name,
            "origin": origin,
            "state": state,
            "scheduled_date": picking.get("scheduled_date"),
            "date_done": picking.get("date_done"),
            "delay_seconds": delay_seconds if exception_type == "delay" else 0,
            "picking_type": picking_type_id[1] if isinstance(picking_type_id, list) and len(picking_type_id) > 1 else None,
            "partner": partner_id[1] if isinstance(partner_id, list) and len(partner_id) > 1 else None,
            "note": note,
            "limited_support": True,
            "source": "stock.picking",
        },
    }
