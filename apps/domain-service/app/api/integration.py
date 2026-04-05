from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.integration import (
    InventorySnapshotCreateRequest,
    InventorySnapshotResponse,
    OrderAuditSnapshotCreateRequest,
    OrderAuditSnapshotResponse,
    OrderExceptionSnapshotCreateRequest,
    OrderExceptionSnapshotResponse,
    ExplainStatusRequest,
    ExplainStatusResponse,
    ConversationExplainRequest,
    ConversationExplainResponse,
    SyncStatusResponse,
)
from app.services.integration_service import IntegrationService
from shared_db import get_db

router = APIRouter(prefix="/api/integration", tags=["integration"])


def get_integration_service(db: Session = Depends(get_db)) -> IntegrationService:
    return IntegrationService(db_session=db)


@router.post("/inventory", response_model=InventorySnapshotResponse, status_code=201)
def create_inventory_snapshot(
    req: InventorySnapshotCreateRequest,
    service: IntegrationService = Depends(get_integration_service)
):
    try:
        result = service.create_inventory_snapshot(
            sku_code=req.sku_code,
            warehouse_code=req.warehouse_code,
            available_qty=req.available_qty,
            reserved_qty=req.reserved_qty,
            status=req.status,
            source_json=req.source_json,
            snapshot_at=req.snapshot_at
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/inventory", response_model=list[InventorySnapshotResponse])
def list_inventory_snapshots(
    sku_code: str | None = Query(None, description="Filter by SKU code"),
    service: IntegrationService = Depends(get_integration_service)
):
    return service.list_inventory(sku_code=sku_code)


@router.get("/inventory/{sku_code}", response_model=InventorySnapshotResponse)
def get_inventory_snapshot_by_sku(
    sku_code: str,
    service: IntegrationService = Depends(get_integration_service)
):
    result = service.get_inventory_by_sku_code(sku_code)
    if result is None:
        raise HTTPException(status_code=404, detail="Inventory snapshot not found")
    return result


@router.post("/order-audits", response_model=OrderAuditSnapshotResponse, status_code=201)
def create_order_audit_snapshot(
    req: OrderAuditSnapshotCreateRequest,
    service: IntegrationService = Depends(get_integration_service)
):
    try:
        result = service.create_order_audit_snapshot(
            order_id=req.order_id,
            platform=req.platform,
            audit_status=req.audit_status,
            audit_reason=req.audit_reason,
            source_json=req.source_json,
            snapshot_at=req.snapshot_at
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/order-audits", response_model=list[OrderAuditSnapshotResponse])
def list_order_audit_snapshots(
    order_id: str | None = Query(None, description="Filter by order ID"),
    service: IntegrationService = Depends(get_integration_service)
):
    return service.list_order_audits(order_id=order_id)


@router.get("/order-audits/{order_id}", response_model=OrderAuditSnapshotResponse)
def get_order_audit_snapshot_by_order(
    order_id: str,
    service: IntegrationService = Depends(get_integration_service)
):
    result = service.get_order_audit_by_order_id(order_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Order audit snapshot not found")
    return result


@router.post("/order-exceptions", response_model=OrderExceptionSnapshotResponse, status_code=201)
def create_order_exception_snapshot(
    req: OrderExceptionSnapshotCreateRequest,
    service: IntegrationService = Depends(get_integration_service)
):
    try:
        result = service.create_order_exception_snapshot(
            order_id=req.order_id,
            platform=req.platform,
            exception_type=req.exception_type,
            exception_status=req.exception_status,
            detail_json=req.detail_json,
            snapshot_at=req.snapshot_at
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/order-exceptions", response_model=list[OrderExceptionSnapshotResponse])
def list_order_exception_snapshots(
    order_id: str | None = Query(None, description="Filter by order ID"),
    exception_type: str | None = Query(None, description="Filter by exception type"),
    service: IntegrationService = Depends(get_integration_service)
):
    if order_id and exception_type:
        raise HTTPException(status_code=400, detail="Only one of order_id or exception_type can be specified")
    return service.list_order_exceptions(order_id=order_id, exception_type=exception_type)


@router.get("/order-exceptions/{order_id}", response_model=OrderExceptionSnapshotResponse)
def get_order_exception_snapshot_by_order(
    order_id: str,
    service: IntegrationService = Depends(get_integration_service)
):
    result = service.get_order_exception_by_order_id(order_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Order exception snapshot not found")
    return result


@router.post("/explain-status", response_model=ExplainStatusResponse)
def explain_status(
    req: ExplainStatusRequest,
    service: IntegrationService = Depends(get_integration_service)
):
    try:
        result = service.explain_status(
            type=req.type,
            sku_code=req.sku_code,
            order_id=req.order_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sync-status", response_model=SyncStatusResponse)
def get_sync_status(
    service: IntegrationService = Depends(get_integration_service)
):
    result = service.get_latest_sync_status()
    if result is None:
        raise HTTPException(status_code=404, detail="No sync status found")
    return result


@router.post("/explain/conversation", response_model=ConversationExplainResponse)
def explain_conversation_status(
    req: ConversationExplainRequest,
    db: Session = Depends(get_db),
):
    from app.services.context_aggregation_service import aggregate_conversation_context
    from app.services.explain_service import explain_from_context

    try:
        conv_id = int(req.conversation_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid conversation_id")

    context = aggregate_conversation_context(db, conv_id)
    result = explain_from_context(context)
    return result
