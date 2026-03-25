"""Knowledge base tool for AI layer."""

import httpx


async def search_kb_tool(query: str, top_k: int = 3) -> dict:
    knowledge_service_url = "http://localhost:8003"
    try:
        response = httpx.post(f"{knowledge_service_url}/api/kb/search", json={"query": query, "top_k": top_k}, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "query": query}


def search_kb(query: str, top_k: int = 3) -> dict:
    import asyncio
    return asyncio.run(search_kb_tool(query, top_k))