from sqlalchemy.orm import Session
from domain_models.models.order_core import OrderCore


def get_by_id(db: Session, order_id: int) -> OrderCore | None:
    return db.query(OrderCore).filter_by(id=order_id).first()


def get_by_customer_id(db: Session, customer_id: int) -> list[OrderCore]:
    return db.query(OrderCore).filter_by(customer_id=customer_id).all()


def create(
    db: Session,
    customer_id: int | None = None,
    current_status: str = "unknown",
    total_amount: str | None = None,
    currency: str | None = None,
    shop_id: str | None = None,
) -> OrderCore:
    order = OrderCore(
        customer_id=customer_id,
        current_status=current_status,
        total_amount=total_amount,
        currency=currency,
        shop_id=shop_id,
    )
    db.add(order)
    db.flush()
    return order
