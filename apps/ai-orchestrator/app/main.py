from fastapi import FastAPI

from app.api.ai import router as ai_router

app = FastAPI(
    title="AI Orchestrator",
    description="V1 AI suggestion workflow with LangGraph",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(ai_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-orchestrator"}