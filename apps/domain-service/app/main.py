from fastapi import FastAPI

from app.api.conversations import router as conversations_router
from app.api.context import router as context_router
from app.api.audit import router as audit_router
from app.api.followup import router as followup_router
from app.api.tags import router as tags_router
from app.api.profile import router as profile_router
from app.api.recommendation import router as recommendation_router, conversation_router
from app.api.operation_campaign import router as operation_campaign_router
from app.api.analytics import router as analytics_router
from app.api.risk_flag import router as risk_flag_router
from app.api.quality_rule import router as quality_rule_router
from app.api.quality_inspection import router as quality_inspection_router
from app.api.quality_alert import router as quality_alert_router
from app.api.risk_case import router as risk_case_router
from app.api.blacklist_customer import router as blacklist_customer_router
from app.api.integration import router as integration_router
from app.api.management import router as management_router
from app.api.messages import router as messages_router
from app.scheduler import start_scheduler, stop_scheduler

app = FastAPI(
    title="Domain Service",
    description="V1 unified business APIs for order, shipment, after-sale context",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


@app.on_event("startup")
def on_startup():
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()

app.include_router(conversations_router)
app.include_router(context_router)
app.include_router(audit_router)
app.include_router(followup_router)
app.include_router(tags_router)
app.include_router(profile_router)
app.include_router(recommendation_router)
app.include_router(conversation_router)
app.include_router(operation_campaign_router)
app.include_router(analytics_router)
app.include_router(risk_flag_router)
app.include_router(quality_rule_router)
app.include_router(quality_inspection_router)
app.include_router(quality_alert_router)
app.include_router(risk_case_router)
app.include_router(blacklist_customer_router)
app.include_router(integration_router)
app.include_router(management_router)
app.include_router(messages_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "domain-service"}