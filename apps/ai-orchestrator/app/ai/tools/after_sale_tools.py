"""After-sale tool for AI layer.

Switched to resolve path for identity-aware after-sale context.
Old path: /api/after-sales/{platform}/{after_sale_id}
New path: /api/after-sales/resolve?platform=...&external_order_id=...

When order_id is available, uses resolve path.
When only after_sale_id is available, falls back to old path for compatibility.
"""

import httpx


DOMAIN_SERVICE_URL = "http://domain-service:8001"


async def get_after_sale_tool(
    after_sale_id: str,
    platform: str = "jd",
    order_id: str | None = None,
    source_system: str = "platform",
) -> dict:
    """
    Get after-sale context through the unified order identity resolution path.

    If order_id is provided:
      Calls /api/after-sales/resolve which resolves external_order_id -> internal order
      and looks up after_sale data via identity mapping.

    If only after_sale_id is provided (no order_id):
      Falls back to old path /api/after-sales/{platform}/{after_sale_id} for compatibility.

    Returns a cleaned structure for AI consumption:
    - Prioritizes provider data (real-time)
    - Falls back to DB data if provider unavailable
    - Preserves internal_order_id and identities for debugging
    """
    if order_id:
        return await _get_after_sale_via_resolve(order_id, platform, source_system)
    return await _get_after_sale_legacy(after_sale_id, platform)


async def _get_after_sale_via_resolve(
    order_id: str,
    platform: str,
    source_system: str,
) -> dict:
    try:
        response = httpx.get(
            f"{DOMAIN_SERVICE_URL}/api/after-sales/resolve",
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

    provider = data.get("after_sale_from_provider")
    db_data = data.get("after_sale_from_db")

    if provider and "error" not in provider:
        result["after_sale_status"] = provider.get("status_name", "")
        result["after_sale_type"] = provider.get("type_name", "")
        result["apply_amount"] = provider.get("apply_amount", 0)
        result["approve_amount"] = provider.get("approve_amount", 0)
        result["reason"] = provider.get("reason", "")
        result["source"] = "provider"
    elif db_data:
        result["after_sale_status"] = db_data.get("status", "")
        result["after_sale_type"] = db_data.get("case_type", "")
        result["reason"] = db_data.get("reason", "")
        result["source"] = "db"
    else:
        result["after_sale_status"] = "unknown"
        result["source"] = "none"

    return result


async def _get_after_sale_legacy(after_sale_id: str, platform: str) -> dict:
    try:
        response = httpx.get(
            f"{DOMAIN_SERVICE_URL}/api/after-sales/{platform}/{after_sale_id}",
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "error": str(e),
            "after_sale_id": after_sale_id,
            "platform": platform,
        }


def get_after_sale(
    after_sale_id: str,
    platform: str = "jd",
    order_id: str | None = None,
    source_system: str = "platform",
) -> dict:
    import asyncio
    return asyncio.run(get_after_sale_tool(after_sale_id, platform, order_id, source_system))
