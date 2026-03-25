"""After-sale tool for AI layer."""

import httpx


async def get_after_sale_tool(after_sale_id: str, platform: str = "jd") -> dict:
    domain_service_url = "http://domain-service:8001"
    try:
        response = httpx.get(f"{domain_service_url}/api/after-sales/{platform}/{after_sale_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "after_sale_id": after_sale_id, "platform": platform}


def get_after_sale(after_sale_id: str, platform: str = "jd") -> dict:
    import asyncio
    return asyncio.run(get_after_sale_tool(after_sale_id, platform))