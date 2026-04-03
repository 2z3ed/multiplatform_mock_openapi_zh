from sqlalchemy.orm import Session
from domain_models.models.conversation_order_link import ConversationOrderLink


def get_by_conversation(db: Session, conversation_id: int) -> list[ConversationOrderLink]:
    return db.query(ConversationOrderLink).filter_by(conversation_id=conversation_id).all()


def get_by_order(db: Session, order_id: int) -> list[ConversationOrderLink]:
    return db.query(ConversationOrderLink).filter_by(order_id=order_id).all()


def create(
    db: Session,
    conversation_id: int,
    order_id: int,
    link_type: str = "mentioned",
) -> ConversationOrderLink:
    link = ConversationOrderLink(
        conversation_id=conversation_id,
        order_id=order_id,
        link_type=link_type,
    )
    db.add(link)
    db.flush()
    return link
