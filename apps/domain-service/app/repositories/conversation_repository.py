"""Conversation repository for DB operations."""
from typing import Optional
from sqlalchemy.orm import Session
from domain_models.models.conversation import Conversation


def list_all(
    db: Session,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Conversation]:
    query = db.query(Conversation)
    if platform:
        query = query.filter(Conversation.platform == platform)
    if status:
        query = query.filter(Conversation.status == status)
    query = query.order_by(Conversation.id.desc())
    return query.offset(skip).limit(limit).all()


def count_all(
    db: Session,
    platform: Optional[str] = None,
    status: Optional[str] = None,
) -> int:
    query = db.query(Conversation)
    if platform:
        query = query.filter(Conversation.platform == platform)
    if status:
        query = query.filter(Conversation.status == status)
    return query.count()


def get_by_id(db: Session, conversation_id: int) -> Optional[Conversation]:
    return db.query(Conversation).filter_by(id=conversation_id).first()
