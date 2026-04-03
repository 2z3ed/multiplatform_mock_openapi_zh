"""Shipment tool for AI layer.

Switched to resolve path for identity-aware shipment context.
Old path: /api/shipments/{platform}/{order_id}
New path: /api/shipments/resolve?platform=...&external_order_id=...
"""

import httpx


DOMAIN_SERVICE_URL = "http://domain-service:8001"


async def get_shipment_tool(order_id: str, platform: str = "jd", source_system: str = "platform") -> dict:
    """
    Get shipment context through the unified order identity resolution path.

    Calls /api/shipments/resolve which:
    1. Resolves external_order_id -> internal order_core.id
    2. Looks up shipment_snapshot via identity mapping
    3. Also fetches live data from platform provider

    Returns a cleaned structure for AI consumption:
    - Prioritizes provider data (real-time)
    - Falls back to snapshot data if provider unavailable
    - Preserves internal_order_id and identities for debugging
    """
    try:
        response = httpx.get(
            f"{DOMAIN_SERVICE_URL}/api/shipments/resolve",
            params={
                "platform": platform,
                "external_order_id": order_id,
                "source_system": source_system,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return {
            "error": str(e),
            "order_id": order_id,
            "platform": platform,
            "resolved": False,
        }

    if not data.get("resolved"):
        return {
            "error": "Could not resolve order identity",
            "order_id": order_id,
            "platform": platform,
            "resolved": False,
        }

    result = {
        "internal_order_id": data.get("internal_order_id"),
        "resolved": True,
        "identities": data.get("identities", []),
    }

    provider = data.get("shipment_from_provider")
    snapshot = data.get("shipment_from_snapshot")

    if provider and "error" not in provider:
        result["shipment_status"] = provider.get("shipments", [{}])[0].get("status_name", "") if provider.get("shipments") else ""
        result["tracking_info"] = provider
        result["source"] = "provider"
    elif snapshot:
        result["shipment_status"] = snapshot.get("shipment_status", "")
        result["tracking_no"] = snapshot.get("tracking_no", "")
        result["carrier"] = snapshot.get("carrier", "")
        result["source"] = "snapshot"
    else:
        result["shipment_status"] = "unknown"
        result["source"] = "none"

    return result


def get_shipment(order_id: str, platform: str = "jd", source_system: str = "platform") -> dict:
    import asyncio
    return asyncio.run(get_shipment_tool(order_id, platform, source_system))
