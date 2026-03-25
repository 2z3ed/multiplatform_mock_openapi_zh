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

BACKEND_SERVICES = {
    "domain-service": "http://domain-service:8001",
    "ai-orchestrator": "http://ai-orchestrator:8002",
    "knowledge-service": "http://knowledge-service:8003",
    "mock-platform-server": "http://mock-platform-server:8004",
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


@app.post("/api/ai/suggest-reply")
async def suggest_reply(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_SERVICES['ai-orchestrator']}/api/ai/suggest-reply",
            json=body
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