from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.quality_rule_repository import QualityRuleRepository
from app.repositories.quality_inspection_result_repository import QualityInspectionResultRepository
from app.repositories.quality_alert_repository import QualityAlertRepository
from app.services.audit_service import AuditService
from domain_models.models.message import Message
from domain_models.models.quality_rule import ALLOWED_RULE_TYPES


class QualityInspectionService:
    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._rule_repo = QualityRuleRepository(db_session)
        self._result_repo = QualityInspectionResultRepository(db_session)
        self._alert_repo = QualityAlertRepository(db_session)
        self._audit_service = AuditService(db_session=db_session)

    def _to_dict(self, result) -> dict:
        return {
            "id": result.id,
            "conversation_id": result.conversation_id,
            "quality_rule_id": result.quality_rule_id,
            "hit": result.hit,
            "severity": result.severity,
            "evidence_json": result.evidence_json,
            "inspected_at": result.inspected_at,
            "created_at": result.created_at.isoformat() if result.created_at else None,
            "updated_at": result.updated_at.isoformat() if result.updated_at else None,
        }

    def get_by_id(self, id: int) -> Optional[dict]:
        result = self._result_repo.get_by_id(id)
        if result is None:
            return None
        return self._to_dict(result)

    def list_all(self) -> list[dict]:
        results = self._result_repo.list_all()
        return [self._to_dict(r) for r in results]

    def list_by_conversation(self, conversation_id: int) -> list[dict]:
        results = self._result_repo.list_by_conversation(conversation_id)
        return [self._to_dict(r) for r in results]

    def inspect_conversation(self, conversation_id: int) -> list[dict]:
        rules = self._rule_repo.list_all()
        results = []

        for rule in rules:
            result = self._inspect_single_rule(conversation_id, rule)
            if result:
                results.append(result)

        self._audit_service.log_event(
            action="quality_inspection_run",
            target_type="conversation",
            target_id=str(conversation_id),
            detail=f"Ran quality inspection for conversation {conversation_id}",
            detail_json={
                "conversation_id": conversation_id,
                "rules_checked": len(rules),
                "results_count": len(results)
            }
        )

        return results

    def _inspect_single_rule(self, conversation_id: int, rule) -> Optional[dict]:
        if rule.rule_type == "slow_reply":
            return self._check_slow_reply(conversation_id, rule)
        elif rule.rule_type == "missed_response":
            return self._check_missed_response(conversation_id, rule)
        elif rule.rule_type == "forbidden_word":
            return self._check_forbidden_word(conversation_id, rule)
        return None

    def _check_slow_reply(self, conversation_id: int, rule) -> Optional[dict]:
        config = rule.config_json or {}
        max_minutes = config.get("max_reply_minutes", 30)

        messages = (
            self._db_session.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.sent_at.asc())
            .all()
        )

        if not messages:
            return self._create_result(conversation_id, rule, False, {})

        max_delay = None
        evidence = {"violations": []}

        for i, msg in enumerate(messages):
            if msg.sender_type == "customer":
                for j in range(i + 1, len(messages)):
                    if messages[j].sender_type == "agent":
                        delay = (messages[j].sent_at - msg.sent_at).total_seconds() / 60
                        if delay > max_minutes:
                            evidence["violations"].append({
                                "customer_message_id": msg.id,
                                "agent_message_id": messages[j].id,
                                "delay_minutes": round(delay, 2)
                            })
                            if max_delay is None or delay > max_delay:
                                max_delay = delay
                        break

        hit = len(evidence["violations"]) > 0
        if hit:
            evidence["max_delay_minutes"] = round(max_delay, 2)

        return self._create_result(conversation_id, rule, hit, evidence)

    def _check_missed_response(self, conversation_id: int, rule) -> Optional[dict]:
        config = rule.config_json or {}
        timeout_minutes = config.get("timeout_minutes", 60)

        messages = (
            self._db_session.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.sent_at.desc())
            .limit(1)
            .first()
        )

        if not messages:
            return self._create_result(conversation_id, rule, False, {})

        last_message = messages
        if last_message.sender_type != "customer":
            return self._create_result(conversation_id, rule, False, {})

        now = datetime.now(last_message.sent_at.tzinfo) if last_message.sent_at.tzinfo else datetime.utcnow()
        elapsed = (now - last_message.sent_at).total_seconds() / 60

        hit = elapsed > timeout_minutes
        evidence = {
            "last_message_id": last_message.id,
            "last_message_sender": last_message.sender_type,
            "elapsed_minutes": round(elapsed, 2),
            "timeout_minutes": timeout_minutes
        }

        return self._create_result(conversation_id, rule, hit, evidence)

    def _check_forbidden_word(self, conversation_id: int, rule) -> Optional[dict]:
        config = rule.config_json or {}
        forbidden_words = config.get("words", [])

        if not forbidden_words:
            return self._create_result(conversation_id, rule, False, {})

        messages = (
            self._db_session.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .filter(Message.sender_type == "agent")
            .order_by(Message.sent_at.asc())
            .all()
        )

        if not messages:
            return self._create_result(conversation_id, rule, False, {})

        evidence = {"violations": []}

        for msg in messages:
            for word in forbidden_words:
                if word.lower() in msg.content.lower():
                    evidence["violations"].append({
                        "message_id": msg.id,
                        "forbidden_word": word,
                        "content_snippet": msg.content[:100] if len(msg.content) > 100 else msg.content
                    })

        hit = len(evidence["violations"]) > 0
        return self._create_result(conversation_id, rule, hit, evidence)

    def _create_result(self, conversation_id: int, rule, hit: bool, evidence: dict) -> dict:
        result = self._result_repo.create(
            conversation_id=conversation_id,
            quality_rule_id=rule.id,
            hit=hit,
            severity=rule.severity,
            evidence_json=evidence,
            inspected_at=datetime.utcnow().isoformat()
        )

        self._audit_service.log_event(
            action="quality_inspection_result_created",
            target_type="quality_inspection_result",
            target_id=str(result.id),
            detail=f"Created inspection result: hit={hit}",
            detail_json={
                "result_id": result.id,
                "conversation_id": conversation_id,
                "rule_id": rule.id,
                "hit": hit,
                "severity": rule.severity
            }
        )

        if hit and rule.severity == "high":
            self._create_alert(result.id)

        return self._to_dict(result)

    def _create_alert(self, quality_inspection_result_id: int) -> None:
        if self._alert_repo.exists_for_result(quality_inspection_result_id):
            return

        self._alert_repo.create(
            quality_inspection_result_id=quality_inspection_result_id,
            alert_level="high"
        )

        self._audit_service.log_event(
            action="quality_alert_created",
            target_type="quality_alert",
            target_id=str(quality_inspection_result_id),
            detail=f"Created quality alert for result {quality_inspection_result_id}",
            detail_json={
                "quality_inspection_result_id": quality_inspection_result_id,
                "alert_level": "high"
            }
        )
