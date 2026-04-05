"""
Quality rule service: evaluates real business facts + explain result
and generates quality inspection findings.

Rules:
1. insufficient_explanation — order/shipment explanation lacks key facts
2. incomplete_after_sale_reply — after-sale reply missing status/amount/reason
3. inventory_reply_conflict — reply conflicts with real inventory state
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.quality_rule_repository import QualityRuleRepository
from app.services.audit_service import AuditService
from domain_models.models.quality_rule import ALLOWED_RULE_TYPES, ALLOWED_SEVERITIES


def _check_insufficient_explanation(
    explain_result: dict,
    conversation_context: dict,
    conversation_id: int,
) -> Optional[dict]:
    """
    Rule 1: If explain result's formatted output is too short or missing
    key order/shipment facts, flag as insufficient explanation.
    """
    formatted = explain_result.get("formatted", "")
    if not formatted or len(formatted) < 10:
        return None

    orders = conversation_context.get("orders", [])
    if not orders:
        return None

    first = orders[0]
    order_facts = first.get("order")
    shipment_facts = first.get("shipment")

    missing = []

    if order_facts:
        status_name = order_facts.get("status_name", "")
        if not status_name or "未知" in status_name:
            missing.append("订单状态缺失")
        if not order_facts.get("order_id"):
            missing.append("订单号缺失")

    if shipment_facts and shipment_facts.get("shipments"):
        s = shipment_facts["shipments"][0]
        if not s.get("express_company") and not s.get("express_no"):
            missing.append("物流信息缺失")
        trace = s.get("trace", [])
        if not trace:
            missing.append("物流轨迹缺失")

    if not missing:
        return None

    severity = "high" if len(missing) >= 2 else "medium"
    evidence = {
        "rule": "insufficient_explanation",
        "formatted_length": len(formatted),
        "missing_facts": missing,
        "order_id": order_facts.get("order_id") if order_facts else None,
        "order_status": order_facts.get("status_name") if order_facts else None,
    }

    return {
        "rule_code": "qc_insufficient_explanation",
        "rule_name": "订单/履约解释不足",
        "rule_type": "insufficient_explanation",
        "severity": severity,
        "rule_description": "AI 建议回复所依据的订单/物流解释缺少关键事实",
        "rule_config": {"min_formatted_length": 10},
        "evidence_json": evidence,
    }


def _check_incomplete_after_sale_reply(
    explain_result: dict,
    conversation_context: dict,
    conversation_id: int,
) -> Optional[dict]:
    """
    Rule 2: If after-sale exists but the explain result doesn't cover
    status / amount / reason adequately, flag as incomplete after-sale reply.
    """
    orders = conversation_context.get("orders", [])
    if not orders:
        return None

    first = orders[0]
    after_sales_facts = first.get("after_sales", [])
    if not after_sales_facts:
        return None

    as_item = after_sales_facts[0]
    formatted = explain_result.get("formatted", "")

    status_name = as_item.get("status_name", "")
    apply_amount = as_item.get("apply_amount")
    reason = as_item.get("reason", "")

    missing = []
    if not status_name or "未知" in status_name:
        missing.append("售后状态缺失")
    elif formatted and status_name not in formatted:
        missing.append("售后状态未在解释中体现")

    if apply_amount:
        amount_str = str(apply_amount)
        if not formatted or amount_str not in formatted:
            missing.append("申请金额未在解释中体现")
    else:
        missing.append("申请金额缺失")

    if reason:
        if not formatted or reason not in formatted:
            missing.append("申请原因未在解释中体现")
    else:
        missing.append("申请原因缺失")

    if not missing:
        return None

    severity = "high" if len(missing) >= 2 else "medium"
    evidence = {
        "rule": "incomplete_after_sale_reply",
        "after_sale_id": as_item.get("after_sale_id"),
        "order_id": as_item.get("order_id"),
        "missing_facts": missing,
        "after_sale_status": status_name,
        "apply_amount": apply_amount,
        "reason": reason,
        "formatted_includes_status": status_name in formatted if formatted else False,
        "formatted_includes_amount": str(apply_amount) in formatted if formatted and apply_amount else False,
    }

    return {
        "rule_code": "qc_incomplete_after_sale",
        "rule_name": "售后回复信息不完整",
        "rule_type": "incomplete_after_sale_reply",
        "severity": severity,
        "rule_description": "AI 建议回复未覆盖售后状态/金额/原因中的关键事实",
        "rule_config": {"required_fields": ["status", "amount", "reason"]},
        "evidence_json": evidence,
    }


def _check_inventory_reply_conflict(
    explain_result: dict,
    conversation_context: dict,
    conversation_id: int,
) -> Optional[dict]:
    """
    Rule 3: If inventory has out_of_stock / low_stock items but the
    explain result suggests availability or doesn't mention the shortage.
    """
    orders = conversation_context.get("orders", [])
    if not orders:
        return None

    first = orders[0]
    inventory_facts = first.get("inventory")
    if not inventory_facts or not inventory_facts.get("items"):
        return None

    formatted = explain_result.get("formatted", "")
    conflicts = []

    for item in inventory_facts.get("items", [])[:3]:
        stock_state = (item.get("stock_state") or "").lower()
        if stock_state not in ("out_of_stock", "low_stock"):
            continue

        product_name = item.get("product_name", item.get("sku_id", ""))
        quantity = item.get("quantity", 0)

        if stock_state == "out_of_stock":
            has_stock_mention = "缺货" in formatted or "无货" in formatted or "暂无" in formatted
            if not has_stock_mention:
                conflicts.append({
                    "product_name": product_name,
                    "stock_state": "out_of_stock",
                    "quantity": quantity,
                    "issue": "库存缺货但解释中未提及",
                })
        else:
            has_low_mention = "紧张" in formatted or "低库存" in formatted or "不足" in formatted
            if not has_low_mention:
                conflicts.append({
                    "product_name": product_name,
                    "stock_state": "low_stock",
                    "quantity": quantity,
                    "issue": "库存紧张但解释中未提及",
                })

    if not conflicts:
        return None

    severity = "high" if any(c["stock_state"] == "out_of_stock" for c in conflicts) else "medium"
    evidence = {
        "rule": "inventory_reply_conflict",
        "conflicts": conflicts,
        "formatted_snippet": formatted[:200] if formatted else "",
    }

    return {
        "rule_code": "qc_inventory_conflict",
        "rule_name": "库存答复与事实不一致",
        "rule_type": "inventory_reply_conflict",
        "severity": severity,
        "rule_description": "库存不足/缺货但 AI 建议回复未正确反映真实库存状态",
        "rule_config": {"check_stock_mentions": True},
        "evidence_json": evidence,
    }


def evaluate_conversation_for_quality(
    conversation_context: dict,
    explain_result: dict,
    conversation_id: int,
) -> list[dict]:
    """
    Evaluate all quality rules against a conversation context + explain result
    and return a list of quality inspection payloads.
    """
    findings = []

    r1 = _check_insufficient_explanation(explain_result, conversation_context, conversation_id)
    if r1:
        findings.append(r1)

    r2 = _check_incomplete_after_sale_reply(explain_result, conversation_context, conversation_id)
    if r2:
        findings.append(r2)

    r3 = _check_inventory_reply_conflict(explain_result, conversation_context, conversation_id)
    if r3:
        findings.append(r3)

    return findings


class QualityRuleService:
    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._repo = QualityRuleRepository(db_session)
        self._audit_service = AuditService(db_session=db_session)

    def _to_dict(self, rule) -> dict:
        return {
            "id": rule.id,
            "rule_code": rule.rule_code,
            "rule_name": rule.rule_name,
            "rule_type": rule.rule_type,
            "severity": rule.severity,
            "description": rule.description,
            "config_json": rule.config_json,
            "created_at": rule.created_at.isoformat() if rule.created_at else None,
            "updated_at": rule.updated_at.isoformat() if rule.updated_at else None,
        }

    def get_by_id(self, id: int) -> Optional[dict]:
        rule = self._repo.get_by_id(id)
        if rule is None:
            return None
        return self._to_dict(rule)

    def get_by_rule_code(self, rule_code: str) -> Optional[dict]:
        rule = self._repo.get_by_rule_code(rule_code)
        if rule is None:
            return None
        return self._to_dict(rule)

    def list_all(self) -> list[dict]:
        rules = self._repo.list_all()
        return [self._to_dict(r) for r in rules]

    def list_by_rule_type(self, rule_type: str) -> list[dict]:
        if rule_type not in ALLOWED_RULE_TYPES:
            return []
        rules = self._repo.list_by_rule_type(rule_type)
        return [self._to_dict(r) for r in rules]

    def create(
        self,
        rule_code: str,
        rule_name: str,
        rule_type: str,
        severity: str = "medium",
        description: Optional[str] = None,
        config_json: Optional[dict] = None
    ) -> Optional[dict]:
        if rule_type not in ALLOWED_RULE_TYPES:
            return None
        if severity not in ALLOWED_SEVERITIES:
            return None

        existing = self._repo.get_by_rule_code(rule_code)
        if existing is not None:
            return None

        rule = self._repo.create(
            rule_code=rule_code,
            rule_name=rule_name,
            rule_type=rule_type,
            severity=severity,
            description=description,
            config_json=config_json
        )

        self._audit_service.log_event(
            action="quality_rule_created",
            target_type="quality_rule",
            target_id=str(rule.id),
            detail=f"Created quality rule: {rule_name}",
            detail_json={
                "rule_id": rule.id,
                "rule_code": rule_code,
                "rule_name": rule_name,
                "rule_type": rule_type,
                "severity": severity
            }
        )

        return self._to_dict(rule)
