from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import httpx
import uuid
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Gateway",
    description="V1 unified API entry point",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

import os

BACKEND_SERVICES = {
    "domain-service": os.getenv("DOMAIN_SERVICE_URL", "http://localhost:8005"),
    "ai-orchestrator": os.getenv("AI_ORCHESTRATOR_URL", "http://localhost:9000"),
    "knowledge-service": os.getenv("KNOWLEDGE_SERVICE_URL", "http://localhost:8003"),
    "mock-platform-server": os.getenv("MOCK_PLATFORM_URL", "http://localhost:8004"),
}


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def log_request(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "api-gateway"}


@app.api_route("/gateway/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request):
    if service not in BACKEND_SERVICES:
        return JSONResponse(
            status_code=404,
            content={"detail": f"Service not found: {service}"}
        )
    
    base_url = BACKEND_SERVICES[service]
    url = f"{base_url}/{path}"
    
    body = None
    if request.method in ["POST", "PUT"]:
        body = await request.body()
    
    headers = dict(request.headers)
    headers.pop("host", None)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params
            )
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.ConnectError:
        return JSONResponse(
            status_code=503,
            content={"detail": f"Service unavailable: {service}"}
        )
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


@app.get("/api/conversations")
async def get_conversations(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/conversations",
            params=request.query_params
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/conversations/{conversation_id}"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/conversations/{conversation_id}/messages",
            params=request.query_params
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/orders/{platform}/{order_id}")
async def get_order(platform: str, order_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/orders/{platform}/{order_id}"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/shipments/{platform}/{order_id}")
async def get_shipment(platform: str, order_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/shipments/{platform}/{order_id}"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/after-sales/{platform}/{after_sale_id}")
async def get_after_sale(platform: str, after_sale_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/after-sales/{platform}/{after_sale_id}"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/inventory/{platform}/{order_id}")
async def get_inventory(platform: str, order_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/inventory/{platform}/{order_id}"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/ai/suggest-reply")
async def suggest_reply(request: Request):
    body = await request.json()
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BACKEND_SERVICES['ai-orchestrator']}/api/ai/suggest-reply",
            json=body
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/messages")
async def send_message(request: Request):
    body = await request.json()
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BACKEND_SERVICES['domain-service']}/api/messages",
            json=body
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/messages/{conversation_id}")
async def get_saved_messages(conversation_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/messages/{conversation_id}"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/kb/documents")
async def upload_document(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_SERVICES['knowledge-service']}/api/kb/documents",
            json=body
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/kb/reindex")
async def reindex_documents():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_SERVICES['knowledge-service']}/api/kb/reindex"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/kb/search")
async def search_knowledge(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_SERVICES['knowledge-service']}/api/kb/search",
            json=body
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/audit-logs")
async def get_audit_logs(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/audit-logs",
            params=request.query_params
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/audit-logs")
async def create_audit_log(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_SERVICES['domain-service']}/api/audit-logs",
            json=body
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/follow-up/tasks")
async def get_follow_up_tasks(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/follow-up/tasks",
            params=request.query_params
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/follow-up/tasks/{task_id}/execute")
async def execute_follow_up_task(task_id: int, request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_SERVICES['domain-service']}/api/follow-up/tasks/{task_id}/execute",
            json=body
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/follow-up/tasks/{task_id}/close")
async def close_follow_up_task(task_id: int, request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_SERVICES['domain-service']}/api/follow-up/tasks/{task_id}/close",
            json=body
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/conversations/{conversation_id}/recommendations")
async def get_recommendations(conversation_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/conversations/{conversation_id}/recommendations"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/recommendations/{recommendation_id}/accept")
async def accept_recommendation(recommendation_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_SERVICES['domain-service']}/api/recommendations/{recommendation_id}/accept"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/recommendations/{recommendation_id}/reject")
async def reject_recommendation(recommendation_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_SERVICES['domain-service']}/api/recommendations/{recommendation_id}/reject"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/risk-flags")
async def get_risk_flags(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/risk-flags",
            params=request.query_params
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/risk-flags")
async def create_risk_flag(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_SERVICES['domain-service']}/api/risk-flags",
            json=body
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/risk-flags/{risk_flag_id}/resolve")
async def resolve_risk_flag(risk_flag_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_SERVICES['domain-service']}/api/risk-flags/{risk_flag_id}/resolve"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/risk-flags/{risk_flag_id}/dismiss")
async def dismiss_risk_flag(risk_flag_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_SERVICES['domain-service']}/api/risk-flags/{risk_flag_id}/dismiss"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/customers/{customer_id}/profile")
async def get_customer_profile(customer_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/customers/{customer_id}/profile"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/customers/{customer_id}/tags")
async def get_customer_tags(customer_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/customers/{customer_id}/tags"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/tags")
async def get_tags():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/tags"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/tags")
async def create_tag(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_SERVICES['domain-service']}/api/tags",
            json=body
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.delete("/api/tags/{tag_id}")
async def delete_tag(tag_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BACKEND_SERVICES['domain-service']}/api/tags/{tag_id}"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/operation-campaigns")
async def get_operation_campaigns():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/operation-campaigns"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/analytics/summaries")
async def get_analytics_summaries(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/analytics/summaries",
            params=request.query_params
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/integration/inventory")
async def list_inventory_snapshots(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/integration/inventory",
            params=request.query_params
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/integration/order-audits")
async def list_order_audit_snapshots(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/integration/order-audits",
            params=request.query_params
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/integration/order-exceptions")
async def list_order_exception_snapshots(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/integration/order-exceptions",
            params=request.query_params
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/integration/sync-status")
async def get_sync_status():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/integration/sync-status"
        )
    if response.status_code == 404:
        return JSONResponse(content={"message": "No sync status found"}, status_code=200)
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/conversations/{conversation_id}/context")
async def get_conversation_context(conversation_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/conversations/{conversation_id}/context"
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/quality/results")
async def get_quality_results(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_SERVICES['domain-service']}/api/quality/results",
            params=request.query_params
        )
    if response.status_code == 404:
        return JSONResponse(content={"message": "No quality results found"}, status_code=200)
    return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/api/quality/auto-evaluate")
async def post_quality_auto_evaluate(request: Request):
    body = await request.body()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_SERVICES['domain-service']}/api/quality/auto-evaluate",
            content=body,
            headers={"Content-Type": "application/json"}
        )
    return JSONResponse(content=response.json(), status_code=response.status_code)