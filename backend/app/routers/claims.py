from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/claims", tags=["claims"])


def to_my_claim(claim: models.Claim) -> schemas.MyClaimOut:
    item = claim.item
    # A PRIVATE image is never returned to students, not even the claimant.
    image = ""
    if item and item.image_visibility == "PUBLIC":
        image = item.image_url or ""
    return schemas.MyClaimOut(
        id=claim.id,
        item_id=claim.item_id,
        item_name=item.item_name if item else "",
        item_type=item.type if item else "",
        item_location=item.location if item else "",
        item_image=image,
        item_image_visibility=item.image_visibility if item else "PUBLIC",
        item_status=item.status if item else "",
        claim_detail=claim.claim_detail,
        status=claim.status,
        handover_location=claim.handover_location or "",
        handover_status=claim.handover_status or "NOT_ASSIGNED",
        date_claimed=claim.created_at.strftime("%Y-%m-%d") if claim.created_at else "",
    )


@router.get("/my", response_model=list[schemas.MyClaimOut])
def my_claims(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Only the logged-in user's own claims."""
    claims = (
        db.query(models.Claim)
        .filter(models.Claim.user_id == current_user.id)
        .order_by(models.Claim.created_at.desc())
        .all()
    )
    return [to_my_claim(c) for c in claims]


@router.post("", response_model=schemas.MyClaimOut, status_code=201)
def create_claim(
    payload: schemas.ClaimCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    item = db.query(models.Item).filter(models.Item.id == payload.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.type != "FOUND":
        raise HTTPException(status_code=400, detail="Only FOUND items can be claimed")
    if item.status != "ACTIVE":
        raise HTTPException(
            status_code=400, detail="This item is no longer open for claims"
        )
    if item.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot claim an item you reported")

    duplicate = (
        db.query(models.Claim)
        .filter(
            models.Claim.item_id == item.id,
            models.Claim.user_id == current_user.id,
            models.Claim.status == "PENDING",
        )
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=400, detail="You already have a pending claim for this item"
        )

    # Identity comes from the logged-in user, not from the request body.
    claim = models.Claim(
        item_id=item.id,
        user_id=current_user.id,
        claimant_name=current_user.name,
        claimant_email=current_user.email,
        claimant_phone=(payload.claimant_phone or current_user.phone or "").strip(),
        claim_detail=payload.claim_detail.strip(),
        status="PENDING",
        handover_status="NOT_ASSIGNED",
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return to_my_claim(claim)
