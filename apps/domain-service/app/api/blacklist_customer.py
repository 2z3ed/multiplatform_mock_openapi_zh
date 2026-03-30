from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.blacklist_customer import BlacklistCustomerCreateRequest, BlacklistCustomerResponse
from app.services.blacklist_customer_service import BlacklistCustomerService
from shared_db import get_db

router = APIRouter(prefix="/api/risk/blacklist", tags=["blacklist-customers"])


def get_blacklist_customer_service(db: Session = Depends(get_db)) -> BlacklistCustomerService:
    return BlacklistCustomerService(db_session=db)


@router.post("", response_model=BlacklistCustomerResponse, status_code=201)
def create_blacklist_customer(
    req: BlacklistCustomerCreateRequest,
    service: BlacklistCustomerService = Depends(get_blacklist_customer_service)
):
    result = service.create(
        customer_id=req.customer_id,
        reason=req.reason,
        source=req.source
    )
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to create blacklist customer (already exists or invalid source)")
    return result


@router.get("", response_model=list[BlacklistCustomerResponse])
def list_blacklist_customers(
    service: BlacklistCustomerService = Depends(get_blacklist_customer_service)
):
    return service.list_all()


@router.delete("/{customer_id}", status_code=204)
def delete_blacklist_customer(
    customer_id: int,
    service: BlacklistCustomerService = Depends(get_blacklist_customer_service)
):
    success = service.delete(customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blacklist customer not found")
    return None
