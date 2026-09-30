from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user, get_optional_user
from app.database import get_db

router = APIRouter(prefix="/api/items", tags=["items"])

VALID_TYPES = {"LOST", "FOUND"}
VALID_VISIBILITY = {"PUBLIC", "PRIVATE", "NONE"}


def to_public_item(
    item: models.Item, current_user: Optional[models.User] = None
) -> schemas.ItemPublicOut:
    # PUBLIC endpoints never expose: reporter phone, private_detail, or the
    # URL of a PRIVATE image. Those are only available to the owner
    # (GET /api/items/my) or through the admin claim-review endpoints.
    image_url = "" if item.image_visibility == "PRIVATE" else (item.image_url or "")
    return schemas.ItemPublicOut(
        id=item.id,
        type=item.type,
        item_name=item.item_name,
        category=item.category,
        description=item.description,
        location=item.location,
        date_reported=item.date_reported,
        image_url=image_url,
        image_visibility=item.image_visibility,
        status=item.status,
        reported_by=item.reported_by or "",
        contact_email=item.contact_email or "",
        is_mine=bool(current_user and item.user_id == current_user.id),
    )


def to_owner_item(item: models.Item, current_user: models.User) -> schemas.ItemOwnerOut:
    base = to_public_item(item, current_user).model_dump()
    # The reporter may see their own image / secret / phone.
    base["image_url"] = item.image_url or ""
    return schemas.ItemOwnerOut(
        **base,
        phone=item.phone or "",
        private_detail=item.private_detail or "",
    )


@router.get("", response_model=list[schemas.ItemPublicOut])
def list_items(
    search: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_user),
):
    query = db.query(models.Item)

    if type:
        query = query.filter(models.Item.type == type.upper())
    if status:
        query = query.filter(models.Item.status == status.upper())
    if category and category != "All":
        query = query.filter(models.Item.category == category)
    if location and location != "All":
        query = query.filter(models.Item.location == location)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                models.Item.item_name.ilike(like),
                models.Item.description.ilike(like),
                models.Item.category.ilike(like),
                models.Item.location.ilike(like),
            )
        )

    items = query.order_by(models.Item.created_at.desc()).all()
    return [to_public_item(i, current_user) for i in items]


# NOTE: must be declared before "/{item_id}" so "my" isn't parsed as an id.
@router.get("/my", response_model=list[schemas.ItemOwnerOut])
def my_items(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    items = (
        db.query(models.Item)
        .filter(models.Item.user_id == current_user.id)
        .order_by(models.Item.created_at.desc())
        .all()
    )
    return [to_owner_item(i, current_user) for i in items]


@router.get("/{item_id}", response_model=schemas.ItemPublicOut)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_user),
):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return to_public_item(item, current_user)


@router.post("", response_model=schemas.ItemPublicOut, status_code=201)
def create_item(
    payload: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if payload.type == "FOUND" and not (payload.private_detail or "").strip():
        raise HTTPException(
            status_code=400,
            detail="private_detail is required for FOUND items",
        )

    image_url = "" if payload.image_visibility == "NONE" else (payload.image_url or "")
    if payload.image_visibility != "NONE" and not image_url:
        raise HTTPException(
            status_code=400,
            detail="image_url is required unless image_visibility is NONE",
        )

    item = models.Item(
        type=payload.type,
        item_name=payload.item_name.strip(),
        category=payload.category.strip(),
        description=payload.description.strip(),
        location=payload.location.strip(),
        date_reported=payload.date_reported or datetime.utcnow().strftime("%Y-%m-%d"),
        phone=payload.phone,
        image_url=image_url,
        image_visibility=payload.image_visibility,
        private_detail=payload.private_detail or "",
        status="ACTIVE",
        reported_by=(payload.reported_by or "").strip() or current_user.name,
        contact_email=(payload.contact_email or "").strip() or current_user.email,
        user_id=current_user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return to_public_item(item, current_user)

# There is intentionally NO public PATCH /api/items/{id}: item status can only
# change through the admin claim/handover endpoints (routers/admin.py).
