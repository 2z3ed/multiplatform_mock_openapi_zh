from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.voc_topic import VOCTopic, ALLOWED_TOPIC_TYPES, ALLOWED_SOURCES


class VOCTopicRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        topic_name: str,
        topic_type: str,
        source: str,
        occurrence_count: int = 0,
        summary: Optional[str] = None,
        extra_json: Optional[dict] = None
    ) -> VOCTopic:
        topic = VOCTopic(
            topic_name=topic_name,
            topic_type=topic_type,
            source=source,
            occurrence_count=occurrence_count,
            summary=summary,
            extra_json=extra_json
        )
        self.db.add(topic)
        self.db.commit()
        self.db.refresh(topic)
        return topic

    def get_by_id(self, id: int) -> Optional[VOCTopic]:
        return self.db.query(VOCTopic).filter(VOCTopic.id == id).first()

    def list_all(self) -> list[VOCTopic]:
        return self.db.query(VOCTopic).order_by(VOCTopic.created_at.desc()).all()

    def list_by_topic_type(self, topic_type: str) -> list[VOCTopic]:
        return (
            self.db.query(VOCTopic)
            .filter(VOCTopic.topic_type == topic_type)
            .order_by(VOCTopic.created_at.desc())
            .all()
        )

    def delete(self, id: int) -> bool:
        topic = self.get_by_id(id)
        if topic is None:
            return False
        self.db.delete(topic)
        self.db.commit()
        return True
