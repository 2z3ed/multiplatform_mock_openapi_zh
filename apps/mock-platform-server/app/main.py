from fastapi import FastAPI

from app.api.routes_douyin_shop import router as douyin_shop_router
from app.api.routes_jd import router as jd_router
from app.api.routes_wecom_kf import router as wecom_kf_router

app = FastAPI(
    title="Mock Platform Server",
    description="V1 multi-platform mock APIs for JD, Douyin Shop, and WeCom KF",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(jd_router)
app.include_router(douyin_shop_router)
app.include_router(wecom_kf_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "mock-platform-server"}
