from fastapi import FastAPI

from app.api.conversations import router as conversations_router
from app.api.context import router as context_router
from app.api.audit import router as audit_router
from app.api.followup import router as followup_router
from app.api.tags import router as tags_router

app = FastAPI(
    title="Domain Service",
    description="V1 unified business APIs for order, shipment, after-sale context",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(conversations_router)
app.include_router(context_router)
app.include_router(audit_router)
app.include_router(followup_router)
app.include_router(tags_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "domain-service"}