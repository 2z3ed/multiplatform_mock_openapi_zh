"""Order tool for AI layer."""

import httpx


async def get_order_tool(order_id: str, platform: str = "jd") -> dict:
    domain_service_url = "http://localhost:8005"
    try:
        response = httpx.get(f"{domain_service_url}/api/orders/{platform}/{order_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "order_id": order_id, "platform": platform}


def get_order(order_id: str, platform: str = "jd") -> dict:
    import asyncio
    return asyncio.run(get_order_tool(order_id, platform))