"""
Context aggregation service for conversation detail page.

Aggregates real business facts (order, shipment, after-sale, inventory)
for a given conversation by following the chain:
  conversation -> conversation_order_link -> order_core -> order_identity_mapping -> provider
"""
from sqlalchemy.orm import Session

from app.repositories.conversation_order_repository import get_by_conversation as _get_links
from app.repositories.order_identity_repository import get_by_order_id as _get_identities
from app.repositories.order_core_repository import get_by_id as _get_order


def _get_provider(platform: str):
    """Lazy-load provider to avoid circular imports."""
    if platform == "jd":
        from providers.jd.mock.provider import JdMockProvider
        return JdMockProvider()
    elif platform == "taobao":
        from providers.taobao.mock.provider import TaobaoMockProvider
        return TaobaoMockProvider()
    elif platform == "douyin_shop":
        from providers.douyin_shop.mock.provider import DouyinShopMockProvider
        return DouyinShopMockProvider()
    elif platform == "wecom_kf":
        from providers.wecom_kf.mock.provider import WecomKfMockProvider
        return WecomKfMockProvider()
    elif platform == "kuaishou":
        from providers.kuaishou.mock.provider import KuaishouMockProvider
        return KuaishouMockProvider()
    elif platform == "xhs":
        from providers.xhs.mock.provider import XhsMockProvider
        return XhsMockProvider()
    return None


_odoo_client_cache = {}


def _get_odoo_client():
    """Get a cached Odoo XML-RPC client."""
    if "obj" in _odoo_client_cache:
        return _odoo_client_cache["uid"], _odoo_client_cache["obj"]
    import os
    from xmlrpc.client import ServerProxy
    url = os.getenv("ODOO_BASE_URL", "http://localhost:8069")
    db = os.getenv("ODOO_DB", "odoo")
    user = os.getenv("ODOO_USERNAME", "demo")
    key = os.getenv("ODOO_API_KEY", "demo")
    common = ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(db, user, key, {})
    if not uid:
        return None, None
    obj = ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)
    _odoo_client_cache["uid"] = uid
    _odoo_client_cache["obj"] = obj
    return uid, obj


def _odoo_ref(val):
    if isinstance(val, list) and len(val) >= 2:
        return val[1]
    return str(val) if val else ""


def _safe_get_odoo_order(order_id: str) -> dict | None:
    try:
        uid, obj = _get_odoo_client()
        if not obj:
            return None
        orders = obj.execute_kw("odoo", uid, "demo", "sale.order", "search_read",
            [[["name", "=", order_id]]],
            {"fields": ["id", "name", "state", "amount_total", "date_order", "partner_id"], "limit": 1}
        )
        if not orders:
            return None
        o = orders[0]
        state_map = {"draft": "created", "sent": "pending_payment", "sale": "paid", "done": "completed", "cancel": "cancelled"}
        state_name_map = {"draft": "草稿", "sent": "已发送", "sale": "已确认", "done": "已完成", "cancel": "已取消"}
        lines = obj.execute_kw("odoo", uid, "demo", "sale.order.line", "search_read",
            [[["order_id", "=", o["id"]]]],
            {"fields": ["id", "product_id", "product_uom_qty", "price_unit", "name"]},
        )
        items = []
        for line in lines:
            prod = _odoo_ref(line.get("product_id"))
            items.append({
                "sku_id": str(line["id"]),
                "sku_name": prod or line.get("name", ""),
                "quantity": int(line.get("product_uom_qty", 0)),
                "price": float(line.get("price_unit", 0)),
                "sub_total": float(line.get("product_uom_qty", 0)) * float(line.get("price_unit", 0)),
            })
        return {
            "order_id": o["name"],
            "status": state_map.get(o.get("state", "draft"), o.get("state", "draft")),
            "status_name": state_name_map.get(o.get("state", "draft"), o.get("state", "draft")),
            "create_time": o.get("date_order", ""),
            "pay_time": o.get("date_order", "") if o.get("state") in ("sale", "done") else "",
            "total_amount": str(o.get("amount_total", 0)),
            "payment_amount": str(o.get("amount_total", 0)),
            "buyer_nick": _odoo_ref(o.get("partner_id")),
            "buyer_phone": "",
            "receiver_name": _odoo_ref(o.get("partner_id")),
            "receiver_phone": "",
            "receiver_address": None,
            "items": items,
        }
    except Exception:
        return None


def _safe_get_odoo_shipment(order_id: str) -> dict | None:
    try:
        uid, obj = _get_odoo_client()
        if not obj:
            return None
        pickings = obj.execute_kw("odoo", uid, "demo", "stock.picking", "search_read",
            [[["origin", "=", order_id]]],
            {"fields": ["id", "name", "state", "scheduled_date", "date_done"]},
        )
        if not pickings:
            return None
        shipments = []
        for p in pickings:
            state = p.get("state", "")
            status = "in_transit" if state == "done" else "pending"
            status_name = {"done": "已完成", "assigned": "已分配", "confirmed": "已确认", "draft": "草稿"}.get(state, state)
            shipments.append({
                "shipment_id": str(p["id"]),
                "express_company": "Odoo Warehouse",
                "express_no": p["name"],
                "status": status,
                "status_name": status_name,
                "create_time": p.get("scheduled_date", ""),
                "estimated_arrival": "",
                "trace": [{
                    "time": p.get("date_done") or p.get("scheduled_date") or "",
                    "message": f"拣货单 {p['name']} 状态: {status_name}",
                    "location": "",
                }],
            })
        return {"order_id": order_id, "shipments": shipments}
    except Exception:
        return None


def _safe_get_odoo_inventory(order_id: str) -> dict | None:
    try:
        uid, obj = _get_odoo_client()
        if not obj:
            return None
        quants = obj.execute_kw("odoo", uid, "demo", "stock.quant", "search_read",
            [[]],
            {"fields": ["id", "product_id", "location_id", "quantity", "reserved_quantity"], "limit": 20},
        )
        if not quants:
            return None
        items = []
        for q in quants:
            prod_name = _odoo_ref(q.get("product_id"))
            loc_name = _odoo_ref(q.get("location_id"))
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
        return {"order_id": order_id, "items": items}
    except Exception:
        return None


def _safe_get_order(provider, order_id: str) -> dict | None:
    try:
        dto = provider.get_order(order_id)
        return {
            "order_id": dto.order_id,
            "status": dto.status,
            "status_name": dto.status_name,
            "create_time": dto.create_time,
            "pay_time": dto.pay_time,
            "total_amount": dto.total_amount,
            "payment_amount": dto.payment_amount,
            "buyer_nick": dto.buyer_nick,
            "buyer_phone": dto.buyer_phone,
            "receiver_name": dto.receiver_name,
            "receiver_phone": dto.receiver_phone,
            "receiver_address": {
                "province": dto.receiver_address.province if dto.receiver_address else None,
                "city": dto.receiver_address.city if dto.receiver_address else None,
                "district": dto.receiver_address.district if dto.receiver_address else None,
                "detail": dto.receiver_address.detail if dto.receiver_address else None,
            } if dto.receiver_address else None,
            "items": [
                {
                    "sku_id": item.sku_id,
                    "sku_name": item.sku_name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "sub_total": item.sub_total,
                }
                for item in dto.items
            ],
        }
    except Exception:
        return None


def _safe_get_shipment(provider, order_id: str) -> dict | None:
    try:
        dto = provider.get_shipment(order_id)
        if not dto.shipments:
            return None
        return {
            "order_id": dto.order_id,
            "shipments": [
                {
                    "shipment_id": s.shipment_id,
                    "express_company": s.express_company,
                    "express_no": s.express_no,
                    "status": s.status,
                    "status_name": s.status_name,
                    "create_time": s.create_time,
                    "estimated_arrival": s.estimated_arrival,
                    "trace": [
                        {
                            "time": t.time,
                            "message": t.message,
                            "location": t.location,
                        }
                        for t in s.trace
                    ],
                }
                for s in dto.shipments
            ],
        }
    except Exception:
        return None


def _safe_get_after_sale(provider, after_sale_id: str) -> dict | None:
    try:
        dto = provider.get_after_sale(after_sale_id)
        return {
            "after_sale_id": dto.after_sale_id,
            "order_id": dto.order_id,
            "type": dto.type,
            "type_name": dto.type_name,
            "status": dto.status,
            "status_name": dto.status_name,
            "apply_time": dto.apply_time,
            "handle_time": dto.handle_time,
            "apply_amount": dto.apply_amount,
            "approve_amount": dto.approve_amount,
            "reason": dto.reason,
            "reason_detail": dto.reason_detail,
        }
    except Exception:
        return None


def _safe_get_inventory(provider, order_id: str) -> dict | None:
    try:
        dto = provider.get_inventory(order_id)
        if not dto.items:
            return None
        return {
            "order_id": dto.order_id,
            "items": [
                {
                    "sku_id": item.sku_id,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "stock_state": item.stock_state,
                    "quantity": item.quantity,
                    "warehouse_name": item.warehouse_name,
                }
                for item in dto.items
            ],
        }
    except Exception:
        return None


def _find_primary_identity(identities: list) -> dict | None:
    """Find the primary identity, or fall back to the first one."""
    for ident in identities:
        if ident.is_primary:
            return {
                "platform": ident.platform,
                "external_order_id": ident.external_order_id,
                "account_id": ident.account_id,
            }
    if identities:
        first = identities[0]
        return {
            "platform": first.platform,
            "external_order_id": first.external_order_id,
            "account_id": first.account_id,
        }
    return None


def _lookup_after_sale_ids(db: Session, platform: str, external_order_id: str) -> list[str]:
    """Look up after-sale IDs from the AfterSaleCase table for a given order."""
    from domain_models.models.after_sale_case import AfterSaleCase
    cases = db.query(AfterSaleCase).filter_by(
        platform=platform,
        order_id=external_order_id,
    ).all()
    return [c.after_sale_id for c in cases]


def aggregate_conversation_context(
    db: Session,
    conversation_id: int,
) -> dict:
    """
    Aggregate all business facts for a conversation.

    Returns:
    {
        "conversation_id": ...,
        "orders": [
            {
                "internal_order_id": ...,
                "link_type": ...,
                "platform": ...,
                "external_order_id": ...,
                "order": { ... },
                "shipment": { ... },
                "after_sales": [ { ... } ],
                "inventory": { ... },
            }
        ],
    }
    """
    links = _get_links(db, conversation_id)
    orders_context = []

    for link in links:
        order_core = _get_order(db, link.order_id)
        identities = _get_identities(db, link.order_id)
        identity = _find_primary_identity(identities)

        if identity is None:
            orders_context.append({
                "internal_order_id": link.order_id,
                "link_type": link.link_type,
                "platform": None,
                "external_order_id": None,
                "order": None,
                "shipment": None,
                "after_sales": [],
                "inventory": None,
            })
            continue

        platform = identity["platform"]
        external_order_id = identity["external_order_id"]

        order_data = None
        shipment_data = None
        after_sales_data = []
        inventory_data = None

        if platform == "odoo":
            order_data = _safe_get_odoo_order(external_order_id)
            shipment_data = _safe_get_odoo_shipment(external_order_id)
            inventory_data = _safe_get_odoo_inventory(external_order_id)
        else:
            provider = _get_provider(platform)
            if provider:
                order_data = _safe_get_order(provider, external_order_id)
                shipment_data = _safe_get_shipment(provider, external_order_id)
                inventory_data = _safe_get_inventory(provider, external_order_id)

                after_sale_ids = _lookup_after_sale_ids(db, platform, external_order_id)
                for as_id in after_sale_ids:
                    as_data = _safe_get_after_sale(provider, as_id)
                    if as_data:
                        after_sales_data.append(as_data)

                if not after_sales_data:
                    try:
                        as_data = _safe_get_after_sale(provider, external_order_id)
                        if as_data:
                            after_sales_data.append(as_data)
                    except Exception:
                        pass

        orders_context.append({
            "internal_order_id": link.order_id,
            "link_type": link.link_type,
            "platform": platform,
            "external_order_id": external_order_id,
            "order_core_status": order_core.current_status if order_core else None,
            "order": order_data,
            "shipment": shipment_data,
            "after_sales": after_sales_data,
            "inventory": inventory_data,
        })

    return {
        "conversation_id": conversation_id,
        "orders": orders_context,
    }
