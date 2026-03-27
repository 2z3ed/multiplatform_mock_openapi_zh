from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.tags import CreateTagRequest, TagResponse
from app.services.tag_service import CustomerTagService
from shared_db import get_db

router = APIRouter(prefix="/api", tags=["customer-tags"])


def get_tag_service(db: Session = Depends(get_db)) -> CustomerTagService:
    return CustomerTagService(db_session=db)


@router.get("/customers/{customer_id}/tags", response_model=list[TagResponse])
def list_customer_tags(
    customer_id: int,
    service: CustomerTagService = Depends(get_tag_service)
):
    tags = service.list_tags(customer_id)
    return tags


@router.post("/tags", response_model=TagResponse, status_code=201)
def create_tag(
    req: CreateTagRequest,
    service: CustomerTagService = Depends(get_tag_service)
):
    result = service.create_tag(
        customer_id=req.customer_id,
        tag_type=req.tag_type,
        tag_value=req.tag_value,
        source="manual",
        extra_json=req.extra_json
    )
    if result is None:
        existing = service.list_tags(req.customer_id)
        for tag in existing:
            if tag["tag_type"] == req.tag_type and tag["tag_value"] == req.tag_value:
                raise HTTPException(status_code=400, detail="Duplicate tag")
        raise HTTPException(status_code=400, detail="Invalid tag_type")
    return result


@router.delete("/tags/{tag_id}")
def delete_tag(
    tag_id: int,
    service: CustomerTagService = Depends(get_tag_service)
):
    success = service.delete_tag(tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"success": True}
