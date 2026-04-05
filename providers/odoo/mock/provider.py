"""Odoo mock provider that connects to real Odoo via XML-RPC.

Maps real Odoo data to the same DTO format used by other mock providers.
"""
import os
from xmlrpc.client import ServerProxy

from provider_sdk.interfaces.order_provider import OrderProvider
from provider_sdk.interfaces.shipment_provider import ShipmentProvider
from provider_sdk.interfaces.after_sale_provider import AfterSaleProvider
from provider_sdk.dto.order_dto import OrderDTO, OrderItemDTO, AddressDTO
from provider_sdk.dto.shipment_dto import ShipmentDTO, ShipmentRecord, TraceNode
from provider_sdk.dto.after_sale_dto import AfterSaleDTO
from provider_sdk.dto.inventory_dto import InventoryDTO

ODOO_URL = os.getenv("ODOO_BASE_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USER = os.getenv("ODOO_USERNAME", "demo")
ODOO_PASS = os.getenv("ODOO_API_KEY", "demo")

_client_cache = {}


def _get_client():
    if "obj" in _client_cache:
        return _client_cache["uid"], _client_cache["obj"]
    common = ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
    if not uid:
        raise RuntimeError("Odoo auth failed")
    obj = ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
    _client_cache["uid"] = uid
    _client_cache["obj"] = obj
    return uid, obj


def _ref(val):
    if isinstance(val, list) and len(val) >= 2:
        return val[1]
    return str(val) if val else ""


def _map_state(state):
    return {"draft": "created", "sent": "pending_payment", "sale": "paid", "done": "completed", "cancel": "cancelled"}.get(state, state)


def _map_state_name(state):
    return {"draft": "草稿", "sent": "已发送", "sale": "已确认", "done": "已完成", "cancel": "已取消"}.get(state, state)


class OdooMockProvider(OrderProvider, ShipmentProvider, AfterSaleProvider):
    def get_platform(self) -> str:
        return "odoo"

    def get_order(self, order_id: str) -> OrderDTO:
        uid, obj = _get_client()
        orders = obj.execute_kw(ODOO_DB, uid, ODOO_PASS, "sale.order", "search_read",
            [[["name", "=", order_id]]],
            {"fields": ["id", "name", "state", "amount_total", "date_order", "partner_id"], "limit": 1}
        )
        if not orders:
            raise ValueError(f"Order {order_id} not found")
        o = orders[0]
        lines = obj.execute_kw(ODOO_DB, uid, ODOO_PASS, "sale.order.line", "search_read",
            [[["order_id", "=", o["id"]]]],
            {"fields": ["id", "product_id", "product_uom_qty", "price_unit", "name"]},
        )
        items = []
        for line in lines:
            prod = _ref(line.get("product_id"))
            items.append({
                "sku_id": str(line["id"]),
                "sku_name": prod or line.get("name", ""),
                "quantity": int(line.get("product_uom_qty", 0)),
                "price": float(line.get("price_unit", 0)),
                "sub_total": float(line.get("product_uom_qty", 0)) * float(line.get("price_unit", 0)),
            })
        return OrderDTO(
            platform="odoo",
            order_id=o["name"],
            status=_map_state(o.get("state", "draft")),
            status_name=_map_state_name(o.get("state", "draft")),
            create_time=o.get("date_order", ""),
            pay_time=o.get("date_order", "") if o.get("state") in ("sale", "done") else "",
            total_amount=str(o.get("amount_total", 0)),
            freight_amount="0",
            discount_amount="0",
            payment_amount=str(o.get("amount_total", 0)),
            buyer_nick=_ref(o.get("partner_id")),
            buyer_phone="",
            receiver_name=_ref(o.get("partner_id")),
            receiver_phone="",
            receiver_address=None,
            items=items,
            raw_json=o,
        )

    def get_shipment(self, order_id: str) -> ShipmentDTO:
        uid, obj = _get_client()
        pickings = obj.execute_kw(ODOO_DB, uid, ODOO_PASS, "stock.picking", "search_read",
            [[["origin", "=", order_id]]],
            {"fields": ["id", "name", "state", "scheduled_date", "date_done"]},
        )
        shipments = []
        for p in pickings:
            state = p.get("state", "")
            status = "in_transit" if state == "done" else "pending"
            status_name = {"done": "已完成", "assigned": "已分配", "confirmed": "已确认", "draft": "草稿"}.get(state, state)
            shipments.append(ShipmentRecord(
                express_company="Odoo Warehouse",
                express_no=p["name"],
                status=status,
                status_name=status_name,
                trace=[TraceNode(
                    time=p.get("date_done") or p.get("scheduled_date") or "",
                    message=f"拣货单 {p['name']} 状态: {status_name}",
                    location="",
                )],
            ))
        return ShipmentDTO(order_id=order_id, shipments=shipments)

    def get_after_sale(self, after_sale_id: str) -> AfterSaleDTO:
        return AfterSaleDTO(
            after_sale_id=after_sale_id,
            order_id="",
            type="refund",
            type_name="退款",
            status="unknown",
            status_name="未知",
            apply_amount="0",
            approve_amount="0",
            reason="",
            reason_detail="",
        )

    def get_inventory(self, order_id: str) -> InventoryDTO:
        uid, obj = _get_client()
        quants = obj.execute_kw(ODOO_DB, uid, ODOO_PASS, "stock.quant", "search_read",
            [[]],
            {"fields": ["id", "product_id", "location_id", "quantity", "reserved_quantity"], "limit": 20},
        )
        items = []
        for q in quants:
            prod_name = _ref(q.get("product_id"))
            loc_name = _ref(q.get("location_id"))
            qty = q.get("quantity", 0)
            stock_state = "out_of_stock" if qty <= 0 else ("low_stock" if qty < 5 else "in_stock")
            items.append({
                "sku_id": str(q["id"]),
                "product_id": str(q.get("product_id", "")),
                "product_name": prod_name,
                "stock_state": stock_state,
                "quantity": int(qty),
                "warehouse_name": loc_name,
            })
        return InventoryDTO(order_id=order_id, items=items)
