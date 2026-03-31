from datetime import datetime
from typing import Any, Optional
from sqlalchemy.orm import Session

from app.repositories.erp_inventory_snapshot_repository import ERPInventorySnapshotRepository
from app.repositories.order_audit_snapshot_repository import OrderAuditSnapshotRepository
from app.repositories.order_exception_snapshot_repository import OrderExceptionSnapshotRepository
from app.repositories.integration_sync_status_repository import IntegrationSyncStatusRepository
from app.services.audit_service import AuditService
from domain_models.models.erp_inventory_snapshot import ALLOWED_INVENTORY_STATUSES
from domain_models.models.order_audit_snapshot import ALLOWED_AUDIT_STATUSES
from domain_models.models.order_exception_snapshot import ALLOWED_EXCEPTION_TYPES, ALLOWED_EXCEPTION_STATUSES


class IntegrationService:
    def __init__(self, db_session: Session, odoo_provider: Optional[Any] = None):
        self._db_session = db_session
        self._inventory_repo = ERPInventorySnapshotRepository(db_session)
        self._audit_repo = OrderAuditSnapshotRepository(db_session)
        self._exception_repo = OrderExceptionSnapshotRepository(db_session)
        self._sync_status_repo = IntegrationSyncStatusRepository(db_session)
        self._audit_service = AuditService(db_session=db_session)
        self._odoo_provider = odoo_provider

    def _inventory_to_dict(self, snapshot) -> dict:
        return {
            "id": snapshot.id,
            "sku_code": snapshot.sku_code,
            "warehouse_code": snapshot.warehouse_code,
            "available_qty": snapshot.available_qty,
            "reserved_qty": snapshot.reserved_qty,
            "status": snapshot.status,
            "source_json": snapshot.source_json,
            "snapshot_at": snapshot.snapshot_at.isoformat() if snapshot.snapshot_at else None,
            "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
            "updated_at": snapshot.updated_at.isoformat() if snapshot.updated_at else None,
        }

    def _audit_to_dict(self, snapshot) -> dict:
        return {
            "id": snapshot.id,
            "order_id": snapshot.order_id,
            "platform": snapshot.platform,
            "audit_status": snapshot.audit_status,
            "audit_reason": snapshot.audit_reason,
            "source_json": snapshot.source_json,
            "snapshot_at": snapshot.snapshot_at.isoformat() if snapshot.snapshot_at else None,
            "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
            "updated_at": snapshot.updated_at.isoformat() if snapshot.updated_at else None,
        }

    def _exception_to_dict(self, snapshot) -> dict:
        return {
            "id": snapshot.id,
            "order_id": snapshot.order_id,
            "platform": snapshot.platform,
            "exception_type": snapshot.exception_type,
            "exception_status": snapshot.exception_status,
            "detail_json": snapshot.detail_json,
            "snapshot_at": snapshot.snapshot_at.isoformat() if snapshot.snapshot_at else None,
            "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
            "updated_at": snapshot.updated_at.isoformat() if snapshot.updated_at else None,
        }

    def create_inventory_snapshot(
        self,
        sku_code: str,
        warehouse_code: str,
        available_qty: int,
        reserved_qty: int = 0,
        status: str = "normal",
        source_json: Optional[dict] = None,
        snapshot_at: Optional[datetime] = None
    ) -> dict:
        if status not in ALLOWED_INVENTORY_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        snapshot = self._inventory_repo.create(
            sku_code=sku_code,
            warehouse_code=warehouse_code,
            available_qty=available_qty,
            reserved_qty=reserved_qty,
            status=status,
            source_json=source_json,
            snapshot_at=snapshot_at
        )

        self._audit_service.log_event(
            action="inventory_snapshot_created",
            target_type="erp_inventory_snapshot",
            target_id=str(snapshot.id),
            detail=f"Created inventory snapshot for SKU: {sku_code}",
            detail_json={
                "snapshot_id": snapshot.id,
                "sku_code": sku_code,
                "warehouse_code": warehouse_code,
                "available_qty": available_qty,
                "status": status
            }
        )

        return self._inventory_to_dict(snapshot)

    def get_inventory_by_sku_code(self, sku_code: str) -> Optional[dict]:
        snapshot = self._inventory_repo.get_by_sku_code(sku_code)
        if snapshot is None:
            return None
        return self._inventory_to_dict(snapshot)

    def list_inventory(self, sku_code: Optional[str] = None) -> list[dict]:
        if sku_code:
            snapshots = self._inventory_repo.list_by_sku_code(sku_code)
        else:
            snapshots = self._inventory_repo.list_all()
        return [self._inventory_to_dict(s) for s in snapshots]

    def create_order_audit_snapshot(
        self,
        order_id: str,
        platform: str,
        audit_status: str,
        audit_reason: Optional[str] = None,
        source_json: Optional[dict] = None,
        snapshot_at: Optional[datetime] = None
    ) -> dict:
        if audit_status not in ALLOWED_AUDIT_STATUSES:
            raise ValueError(f"Invalid audit_status: {audit_status}")

        snapshot = self._audit_repo.create(
            order_id=order_id,
            platform=platform,
            audit_status=audit_status,
            audit_reason=audit_reason,
            source_json=source_json,
            snapshot_at=snapshot_at
        )

        self._audit_service.log_event(
            action="order_audit_snapshot_created",
            target_type="order_audit_snapshot",
            target_id=str(snapshot.id),
            detail=f"Created audit snapshot for order: {order_id}",
            detail_json={
                "snapshot_id": snapshot.id,
                "order_id": order_id,
                "platform": platform,
                "audit_status": audit_status
            }
        )

        return self._audit_to_dict(snapshot)

    def get_order_audit_by_order_id(self, order_id: str) -> Optional[dict]:
        snapshot = self._audit_repo.get_by_order_id(order_id)
        if snapshot is None:
            return None
        return self._audit_to_dict(snapshot)

    def list_order_audits(self, order_id: Optional[str] = None) -> list[dict]:
        if order_id:
            snapshots = self._audit_repo.list_by_order_id(order_id)
        else:
            snapshots = self._audit_repo.list_all()
        return [self._audit_to_dict(s) for s in snapshots]

    def create_order_exception_snapshot(
        self,
        order_id: str,
        platform: str,
        exception_type: str,
        exception_status: str,
        detail_json: Optional[dict] = None,
        snapshot_at: Optional[datetime] = None
    ) -> dict:
        if exception_type not in ALLOWED_EXCEPTION_TYPES:
            raise ValueError(f"Invalid exception_type: {exception_type}")
        if exception_status not in ALLOWED_EXCEPTION_STATUSES:
            raise ValueError(f"Invalid exception_status: {exception_status}")

        snapshot = self._exception_repo.create(
            order_id=order_id,
            platform=platform,
            exception_type=exception_type,
            exception_status=exception_status,
            detail_json=detail_json,
            snapshot_at=snapshot_at
        )

        self._audit_service.log_event(
            action="order_exception_snapshot_created",
            target_type="order_exception_snapshot",
            target_id=str(snapshot.id),
            detail=f"Created exception snapshot for order: {order_id}",
            detail_json={
                "snapshot_id": snapshot.id,
                "order_id": order_id,
                "platform": platform,
                "exception_type": exception_type,
                "exception_status": exception_status
            }
        )

        return self._exception_to_dict(snapshot)

    def get_order_exception_by_order_id(self, order_id: str) -> Optional[dict]:
        snapshot = self._exception_repo.get_by_order_id(order_id)
        if snapshot is None:
            return None
        return self._exception_to_dict(snapshot)

    def list_order_exceptions(
        self,
        order_id: Optional[str] = None,
        exception_type: Optional[str] = None
    ) -> list[dict]:
        if order_id:
            snapshots = self._exception_repo.list_by_order_id(order_id)
        elif exception_type:
            snapshots = self._exception_repo.list_by_exception_type(exception_type)
        else:
            snapshots = self._exception_repo.list_all()
        return [self._exception_to_dict(s) for s in snapshots]

    def explain_status(
        self,
        type: str,
        sku_code: Optional[str] = None,
        order_id: Optional[str] = None
    ) -> dict:
        explanation = ""
        suggestion = ""

        if type == "inventory":
            if not sku_code:
                raise ValueError("sku_code is required for inventory explanation")
            snapshot = self._inventory_repo.get_by_sku_code(sku_code)
            if snapshot is None:
                return {
                    "explanation": f"未找到 SKU {sku_code} 的库存信息。",
                    "suggestion": "请确认 SKU 编码是否正确，或联系仓库核实库存。"
                }
            if snapshot.status == "normal":
                explanation = f"商品 {sku_code} 库存充足，当前可用库存 {snapshot.available_qty} 件。"
                suggestion = "可告知客户预计1-2天发货。"
            elif snapshot.status == "low":
                explanation = f"商品 {sku_code} 库存紧张，当前可用库存仅 {snapshot.available_qty} 件。"
                suggestion = "建议提醒客户尽快下单，或提供替代商品选项。"
            else:
                explanation = f"商品 {sku_code} 当前缺货，暂无法发货。"
                suggestion = "建议告知客户预计补货时间，或推荐替代商品。"

        elif type == "audit":
            if not order_id:
                raise ValueError("order_id is required for audit explanation")
            snapshot = self._audit_repo.get_by_order_id(order_id)
            if snapshot is None:
                return {
                    "explanation": f"未找到订单 {order_id} 的审核信息。",
                    "suggestion": "请确认订单号是否正确，或联系运营核实审核状态。"
                }
            if snapshot.audit_status == "approved":
                explanation = f"订单 {order_id} 已通过审核，可正常处理。"
                suggestion = "可告知客户订单正在处理中。"
            elif snapshot.audit_status == "rejected":
                reason = snapshot.audit_reason or "未知原因"
                explanation = f"订单 {order_id} 审核未通过，原因：{reason}。"
                suggestion = "建议联系客户补充或修正相关信息。"
            else:
                explanation = f"订单 {order_id} 正在审核中，请耐心等待。"
                suggestion = "可告知客户预计审核时间，如有疑问可联系客服。"

        elif type == "exception":
            if not order_id:
                raise ValueError("order_id is required for exception explanation")
            snapshot = self._exception_repo.get_by_order_id(order_id)
            if snapshot is None:
                return {
                    "explanation": f"未找到订单 {order_id} 的异常信息。",
                    "suggestion": "该订单可能无异常，或请确认订单号是否正确。"
                }
            type_labels = {
                "delay": "物流延误",
                "stockout": "缺货",
                "address": "地址问题",
                "customs": "清关问题",
                "other": "其他异常"
            }
            type_label = type_labels.get(snapshot.exception_type, snapshot.exception_type)
            explanation = f"订单 {order_id} 存在异常：{type_label}，当前状态：{snapshot.exception_status}。"
            if snapshot.exception_status == "open":
                suggestion = "异常正在处理中，建议安抚客户并告知处理进度。"
            elif snapshot.exception_status == "processing":
                suggestion = "异常正在处理中，建议跟进处理进度并及时通知客户。"
            elif snapshot.exception_status == "resolved":
                suggestion = "异常已解决，可告知客户订单将恢复正常处理。"
            else:
                suggestion = "异常已取消，订单可能已取消或问题已撤回。"
        else:
            raise ValueError(f"Invalid type: {type}")

        self._audit_service.log_event(
            action="status_explanation_generated",
            target_type="status_explanation",
            target_id=order_id or sku_code,
            detail=f"Generated {type} status explanation",
            detail_json={
                "type": type,
                "sku_code": sku_code,
                "order_id": order_id,
                "explanation": explanation
            }
        )

        return {
            "explanation": explanation,
            "suggestion": suggestion
        }

    def refresh_from_provider(self, trigger_type: str = "manual") -> dict:
        """Refresh snapshots from the injected Odoo provider.
        
        Returns a summary of created snapshots.
        If no provider is injected, returns an empty result with a message.
        """
        provider_mode = "mock" if hasattr(self._odoo_provider, '__class__') and 'Mock' in self._odoo_provider.__class__.__name__ else "real"
        
        sync_status = self._sync_status_repo.create(
            trigger_type=trigger_type,
            provider_mode=provider_mode,
            started_at=datetime.utcnow(),
        )
        
        if self._odoo_provider is None:
            self._sync_status_repo.update(
                sync_status,
                status="failed",
                error_summary="No Odoo provider configured",
            )
            return {
                "inventory_count": 0,
                "audit_count": 0,
                "exception_count": 0,
                "message": "No Odoo provider configured"
            }

        try:
            inventory_list = self._odoo_provider.get_inventory_list()
            audit_list = self._odoo_provider.get_order_audit_list()
            exception_list = self._odoo_provider.get_order_exception_list()

            inventory_count = 0
            for inv in inventory_list:
                self._inventory_repo.create(
                    sku_code=inv["sku_code"],
                    warehouse_code=inv["warehouse_code"],
                    available_qty=inv["available_qty"],
                    reserved_qty=inv.get("reserved_qty", 0),
                    status=inv.get("status", "normal"),
                    source_json=inv.get("source_json"),
                    snapshot_at=datetime.utcnow()
                )
                inventory_count += 1

            audit_count = 0
            for audit in audit_list:
                self._audit_repo.create(
                    order_id=audit["order_id"],
                    platform=audit["platform"],
                    audit_status=audit["audit_status"],
                    audit_reason=audit.get("audit_reason"),
                    source_json=audit.get("source_json"),
                    snapshot_at=datetime.utcnow()
                )
                audit_count += 1

            exception_count = 0
            for exc in exception_list:
                self._exception_repo.create(
                    order_id=exc["order_id"],
                    platform=exc["platform"],
                    exception_type=exc["exception_type"],
                    exception_status=exc["exception_status"],
                    detail_json=exc.get("detail_json"),
                    snapshot_at=datetime.utcnow()
                )
                exception_count += 1

            self._sync_status_repo.update(
                sync_status,
                status="success",
                inventory_count=inventory_count,
                audit_count=audit_count,
                exception_count=exception_count,
            )

            return {
                "inventory_count": inventory_count,
                "audit_count": audit_count,
                "exception_count": exception_count,
                "message": "Snapshots refreshed successfully"
            }
        except Exception as e:
            self._sync_status_repo.update(
                sync_status,
                status="failed",
                error_summary=str(e),
            )
            raise

    def get_latest_sync_status(self) -> Optional[dict]:
        """Get the latest sync status record."""
        sync_status = self._sync_status_repo.get_latest()
        if sync_status is None:
            return None
        return {
            "id": sync_status.id,
            "trigger_type": sync_status.trigger_type,
            "provider_mode": sync_status.provider_mode,
            "started_at": sync_status.started_at.isoformat() if sync_status.started_at else None,
            "finished_at": sync_status.finished_at.isoformat() if sync_status.finished_at else None,
            "status": sync_status.status,
            "error_summary": sync_status.error_summary,
            "inventory_count": sync_status.inventory_count,
            "audit_count": sync_status.audit_count,
            "exception_count": sync_status.exception_count,
        }

    def refresh_inventory(self, trigger_type: str = "scheduled") -> dict:
        """Refresh inventory snapshots from the injected Odoo provider.
        
        Args:
            trigger_type: Type of trigger (manual/scheduled/api)
            
        Returns:
            Summary of created snapshots.
        """
        provider_mode = "mock" if hasattr(self._odoo_provider, '__class__') and 'Mock' in self._odoo_provider.__class__.__name__ else "real"
        
        sync_status = self._sync_status_repo.create(
            trigger_type=trigger_type,
            provider_mode=provider_mode,
            started_at=datetime.utcnow(),
        )
        
        if self._odoo_provider is None:
            self._sync_status_repo.update(
                sync_status,
                status="failed",
                error_summary="No Odoo provider configured",
            )
            return {
                "inventory_count": 0,
                "message": "No Odoo provider configured"
            }

        try:
            inventory_list = self._odoo_provider.get_inventory_list()

            inventory_count = 0
            for inv in inventory_list:
                self._inventory_repo.create(
                    sku_code=inv["sku_code"],
                    warehouse_code=inv["warehouse_code"],
                    available_qty=inv["available_qty"],
                    reserved_qty=inv.get("reserved_qty", 0),
                    status=inv.get("status", "normal"),
                    source_json=inv.get("source_json"),
                    snapshot_at=datetime.utcnow()
                )
                inventory_count += 1

            self._sync_status_repo.update(
                sync_status,
                status="success",
                inventory_count=inventory_count,
            )

            return {
                "inventory_count": inventory_count,
                "message": "Inventory snapshots refreshed successfully"
            }
        except Exception as e:
            self._sync_status_repo.update(
                sync_status,
                status="failed",
                error_summary=str(e),
            )
            raise

    def refresh_audit(self, trigger_type: str = "scheduled") -> dict:
        """Refresh audit snapshots from the injected Odoo provider.
        
        Args:
            trigger_type: Type of trigger (manual/scheduled/api)
            
        Returns:
            Summary of created snapshots.
        """
        provider_mode = "mock" if hasattr(self._odoo_provider, '__class__') and 'Mock' in self._odoo_provider.__class__.__name__ else "real"
        
        sync_status = self._sync_status_repo.create(
            trigger_type=trigger_type,
            provider_mode=provider_mode,
            started_at=datetime.utcnow(),
        )
        
        if self._odoo_provider is None:
            self._sync_status_repo.update(
                sync_status,
                status="failed",
                error_summary="No Odoo provider configured",
            )
            return {
                "audit_count": 0,
                "message": "No Odoo provider configured"
            }

        try:
            audit_list = self._odoo_provider.get_order_audit_list()

            audit_count = 0
            for audit in audit_list:
                self._audit_repo.create(
                    order_id=audit["order_id"],
                    platform=audit["platform"],
                    audit_status=audit["audit_status"],
                    audit_reason=audit.get("audit_reason"),
                    source_json=audit.get("source_json"),
                    snapshot_at=datetime.utcnow()
                )
                audit_count += 1

            self._sync_status_repo.update(
                sync_status,
                status="success",
                audit_count=audit_count,
            )

            return {
                "audit_count": audit_count,
                "message": "Audit snapshots refreshed successfully"
            }
        except Exception as e:
            self._sync_status_repo.update(
                sync_status,
                status="failed",
                error_summary=str(e),
            )
            raise
