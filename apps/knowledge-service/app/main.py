from fastapi import FastAPI

from app.api.kb import router as kb_router

app = FastAPI(
    title="Knowledge Service",
    description="V1 knowledge base API for document upload, chunking, and retrieval",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(kb_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "knowledge-service"}