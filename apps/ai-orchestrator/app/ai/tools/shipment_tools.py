"""Shipment tool for AI layer."""

import httpx


async def get_shipment_tool(order_id: str, platform: str = "jd") -> dict:
    domain_service_url = "http://localhost:8001"
    try:
        response = httpx.get(f"{domain_service_url}/api/shipments/{platform}/{order_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "order_id": order_id, "platform": platform}


def get_shipment(order_id: str, platform: str = "jd") -> dict:
    import asyncio
    return asyncio.run(get_shipment_tool(order_id, platform))