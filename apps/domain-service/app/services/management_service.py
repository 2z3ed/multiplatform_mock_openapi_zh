from datetime import date
from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.voc_topic_repository import VOCTopicRepository
from app.repositories.training_case_repository import TrainingCaseRepository
from app.repositories.training_task_repository import TrainingTaskRepository
from app.repositories.management_dashboard_snapshot_repository import ManagementDashboardSnapshotRepository
from app.services.audit_service import AuditService
from domain_models.models.voc_topic import ALLOWED_TOPIC_TYPES, ALLOWED_SOURCES
from domain_models.models.training_case import ALLOWED_CASE_TYPES
from domain_models.models.training_task import ALLOWED_TASK_TYPES, ALLOWED_TASK_STATUSES
from domain_models.models.management_dashboard_snapshot import ALLOWED_METRIC_TYPES


class ManagementService:
    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._voc_topic_repo = VOCTopicRepository(db_session)
        self._training_case_repo = TrainingCaseRepository(db_session)
        self._training_task_repo = TrainingTaskRepository(db_session)
        self._dashboard_snapshot_repo = ManagementDashboardSnapshotRepository(db_session)
        self._audit_service = AuditService(db_session=db_session)

    def _voc_topic_to_dict(self, topic) -> dict:
        return {
            "id": topic.id,
            "topic_name": topic.topic_name,
            "topic_type": topic.topic_type,
            "source": topic.source,
            "occurrence_count": topic.occurrence_count,
            "summary": topic.summary,
            "extra_json": topic.extra_json,
            "created_at": topic.created_at.isoformat() if topic.created_at else None,
            "updated_at": topic.updated_at.isoformat() if topic.updated_at else None,
        }

    def _training_case_to_dict(self, case) -> dict:
        return {
            "id": case.id,
            "conversation_id": case.conversation_id,
            "customer_id": case.customer_id,
            "case_title": case.case_title,
            "case_summary": case.case_summary,
            "case_type": case.case_type,
            "source_json": case.source_json,
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        }

    def _training_task_to_dict(self, task) -> dict:
        return {
            "id": task.id,
            "task_name": task.task_name,
            "task_type": task.task_type,
            "status": task.status,
            "related_case_id": task.related_case_id,
            "detail_json": task.detail_json,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        }

    def _dashboard_snapshot_to_dict(self, snapshot) -> dict:
        return {
            "id": snapshot.id,
            "snapshot_date": str(snapshot.snapshot_date) if snapshot.snapshot_date else None,
            "metric_type": snapshot.metric_type,
            "metric_value": float(snapshot.metric_value) if snapshot.metric_value else None,
            "detail_json": snapshot.detail_json,
            "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
            "updated_at": snapshot.updated_at.isoformat() if snapshot.updated_at else None,
        }

    def create_voc_topic(
        self,
        topic_name: str,
        topic_type: str,
        source: str,
        occurrence_count: int = 0,
        summary: Optional[str] = None,
        extra_json: Optional[dict] = None
    ) -> dict:
        if topic_type not in ALLOWED_TOPIC_TYPES:
            raise ValueError(f"Invalid topic_type: {topic_type}")
        if source not in ALLOWED_SOURCES:
            raise ValueError(f"Invalid source: {source}")

        topic = self._voc_topic_repo.create(
            topic_name=topic_name,
            topic_type=topic_type,
            source=source,
            occurrence_count=occurrence_count,
            summary=summary,
            extra_json=extra_json
        )

        self._audit_service.log_event(
            action="voc_topic_created",
            target_type="voc_topic",
            target_id=str(topic.id),
            detail=f"Created VOC topic: {topic_name}",
            detail_json={
                "topic_id": topic.id,
                "topic_name": topic_name,
                "topic_type": topic_type,
                "occurrence_count": occurrence_count
            }
        )

        return self._voc_topic_to_dict(topic)

    def list_voc_topics(self, topic_type: Optional[str] = None) -> list[dict]:
        if topic_type:
            topics = self._voc_topic_repo.list_by_topic_type(topic_type)
        else:
            topics = self._voc_topic_repo.list_all()
        return [self._voc_topic_to_dict(t) for t in topics]

    def create_training_case(
        self,
        case_title: str,
        case_type: str,
        conversation_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        case_summary: Optional[str] = None,
        source_json: Optional[dict] = None
    ) -> dict:
        if case_type not in ALLOWED_CASE_TYPES:
            raise ValueError(f"Invalid case_type: {case_type}")

        case = self._training_case_repo.create(
            conversation_id=conversation_id,
            customer_id=customer_id,
            case_title=case_title,
            case_summary=case_summary,
            case_type=case_type,
            source_json=source_json
        )

        self._audit_service.log_event(
            action="training_case_created",
            target_type="training_case",
            target_id=str(case.id),
            detail=f"Created training case: {case_title}",
            detail_json={
                "case_id": case.id,
                "case_title": case_title,
                "case_type": case_type,
                "conversation_id": conversation_id
            }
        )

        return self._training_case_to_dict(case)

    def list_training_cases(self, case_type: Optional[str] = None) -> list[dict]:
        if case_type:
            cases = self._training_case_repo.list_by_case_type(case_type)
        else:
            cases = self._training_case_repo.list_all()
        return [self._training_case_to_dict(c) for c in cases]

    def create_training_task(
        self,
        task_name: str,
        task_type: str,
        status: str = "pending",
        related_case_id: Optional[int] = None,
        detail_json: Optional[dict] = None
    ) -> dict:
        if task_type not in ALLOWED_TASK_TYPES:
            raise ValueError(f"Invalid task_type: {task_type}")
        if status not in ALLOWED_TASK_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        task = self._training_task_repo.create(
            task_name=task_name,
            task_type=task_type,
            status=status,
            related_case_id=related_case_id,
            detail_json=detail_json
        )

        self._audit_service.log_event(
            action="training_task_created",
            target_type="training_task",
            target_id=str(task.id),
            detail=f"Created training task: {task_name}",
            detail_json={
                "task_id": task.id,
                "task_name": task_name,
                "task_type": task_type,
                "status": status,
                "related_case_id": related_case_id
            }
        )

        return self._training_task_to_dict(task)

    def list_training_tasks(self, status: Optional[str] = None) -> list[dict]:
        if status:
            tasks = self._training_task_repo.list_by_status(status)
        else:
            tasks = self._training_task_repo.list_all()
        return [self._training_task_to_dict(t) for t in tasks]

    def create_dashboard_snapshot(
        self,
        snapshot_date: date,
        metric_type: str,
        metric_value: float,
        detail_json: Optional[dict] = None
    ) -> dict:
        if metric_type not in ALLOWED_METRIC_TYPES:
            raise ValueError(f"Invalid metric_type: {metric_type}. Allowed: {ALLOWED_METRIC_TYPES}")

        snapshot = self._dashboard_snapshot_repo.create(
            snapshot_date=snapshot_date,
            metric_type=metric_type,
            metric_value=metric_value,
            detail_json=detail_json
        )

        self._audit_service.log_event(
            action="dashboard_snapshot_created",
            target_type="management_dashboard_snapshot",
            target_id=str(snapshot.id),
            detail=f"Created dashboard snapshot: {metric_type} for {snapshot_date}",
            detail_json={
                "snapshot_id": snapshot.id,
                "snapshot_date": str(snapshot_date),
                "metric_type": metric_type,
                "metric_value": metric_value
            }
        )

        return self._dashboard_snapshot_to_dict(snapshot)

    def list_dashboard_snapshots(
        self,
        metric_type: Optional[str] = None,
        snapshot_date: Optional[date] = None
    ) -> list[dict]:
        if snapshot_date:
            snapshots = self._dashboard_snapshot_repo.list_by_date(snapshot_date)
        elif metric_type:
            snapshots = self._dashboard_snapshot_repo.list_by_metric_type(metric_type)
        else:
            snapshots = self._dashboard_snapshot_repo.list_all()
        return [self._dashboard_snapshot_to_dict(s) for s in snapshots]
