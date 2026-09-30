from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import require_admin
from app.database import get_db

# Every route in this router requires an ADMIN user (403 otherwise).
router = APIRouter(
    prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)]
)


def mask_phone(phone: Optional[str]) -> str:
    digits = (phone or "").strip()
    if not digits:
        return ""
    return "*" * max(len(digits) - 2, 0) + digits[-2:]


def validate_location(location: Optional[str]) -> str:
    loc = (location or "").strip()
    allowed = schemas.HANDOVER_LOCATIONS
    if loc in allowed:
        return loc
    # "Other: <free text>" so admins can name a custom approved spot
    if loc.startswith("Other:") and len(loc[6:].strip()) > 0:
        return loc
    raise HTTPException(
        status_code=400,
        detail="handover_location must be one of: " + ", ".join(allowed),
    )


def to_admin_claim(claim: models.Claim) -> schemas.AdminClaimOut:
    item = claim.item
    return schemas.AdminClaimOut(
        id=claim.id,
        item_id=claim.item_id,
        item_name=item.item_name if item else "",
        item_type=item.type if item else "",
        item_category=item.category if item else "",
        item_location=item.location if item else "",
        item_description=item.description if item else "",
        item_status=item.status if item else "",
        # Admin-only: the real image (even if PRIVATE) and the secret record.
        item_image=(item.image_url or "") if item else "",
        item_image_visibility=item.image_visibility if item else "PUBLIC",
        item_private_detail=(item.private_detail or "") if item else "",
        reporter_name=(item.reported_by or "") if item else "",
        reporter_email=(item.contact_email or "") if item else "",
        reporter_phone=(item.phone or "") if item else "",
        claimant_name=claim.claimant_name or "",
        claimant_email=claim.claimant_email or "",
        claimant_phone=mask_phone(claim.claimant_phone),
        claim_detail=claim.claim_detail,
        status=claim.status,
        handover_location=claim.handover_location or "",
        handover_status=claim.handover_status or "NOT_ASSIGNED",
        reviewed_by_name=claim.reviewer.name if claim.reviewer else "",
        reviewed_at=claim.reviewed_at,
        date_claimed=claim.created_at.strftime("%Y-%m-%d") if claim.created_at else "",
    )


def _get_claim(db: Session, claim_id: int) -> models.Claim:
    claim = db.query(models.Claim).filter(models.Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@router.get("/stats", response_model=schemas.AdminStats)
def stats(db: Session = Depends(get_db)):
    return schemas.AdminStats(
        total_items=db.query(models.Item).count(),
        pending_claims=db.query(models.Claim).filter(models.Claim.status == "PENDING").count(),
        approved_claims=db.query(models.Claim).filter(models.Claim.status == "APPROVED").count(),
        recovered_items=db.query(models.Item).filter(models.Item.status == "RECOVERED").count(),
    )


@router.get("/claims", response_model=list[schemas.AdminClaimOut])
def list_all_claims(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Claim)
    if status:
        query = query.filter(models.Claim.status == status.upper())
    return [to_admin_claim(c) for c in query.order_by(models.Claim.created_at.desc()).all()]


@router.get("/claims/{claim_id}", response_model=schemas.AdminClaimOut)
def get_claim(claim_id: int, db: Session = Depends(get_db)):
    return to_admin_claim(_get_claim(db, claim_id))


@router.patch("/claims/{claim_id}", response_model=schemas.AdminClaimOut)
def decide_claim(
    claim_id: int,
    payload: schemas.ClaimDecisionUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin),
):
    claim = _get_claim(db, claim_id)
    if claim.status != "PENDING":
        raise HTTPException(status_code=400, detail="This claim has already been decided")

    item = claim.item
    now = datetime.utcnow()

    if payload.status == "APPROVED":
        if item.status != "ACTIVE":
            raise HTTPException(
                status_code=400, detail="This item already has an approved claim"
            )
        location = validate_location(payload.handover_location)
        claim.status = "APPROVED"
        claim.handover_location = location
        claim.handover_status = "READY_FOR_PICKUP"
        item.status = "CLAIMED"
        # Only one claim can win: close every other pending claim on the item.
        for other in item.claims:
            if other.id != claim.id and other.status == "PENDING":
                other.status = "REJECTED"
                other.reviewed_by = admin.id
                other.reviewed_at = now
    else:
        claim.status = "REJECTED"
        # Item stays ACTIVE.

    claim.reviewed_by = admin.id
    claim.reviewed_at = now
    db.commit()
    db.refresh(claim)
    return to_admin_claim(claim)


@router.patch("/claims/{claim_id}/handover", response_model=schemas.AdminClaimOut)
def update_handover(
    claim_id: int,
    payload: schemas.HandoverUpdate,
    db: Session = Depends(get_db),
):
    claim = _get_claim(db, claim_id)
    if claim.status != "APPROVED":
        raise HTTPException(status_code=400, detail="Only approved claims have a handover")
    if claim.handover_status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Handover is already completed")

    if payload.handover_location is None and payload.handover_status is None:
        raise HTTPException(status_code=400, detail="Nothing to update")

    if payload.handover_location is not None:
        claim.handover_location = validate_location(payload.handover_location)
        if claim.handover_status == "NOT_ASSIGNED":
            claim.handover_status = "READY_FOR_PICKUP"

    if payload.handover_status is not None:
        if not claim.handover_location:
            raise HTTPException(
                status_code=400, detail="Assign a handover location first"
            )
        if payload.handover_status == "COMPLETED":
            claim.handover_status = "COMPLETED"
            claim.item.status = "RECOVERED"
        else:
            claim.handover_status = "READY_FOR_PICKUP"

    db.commit()
    db.refresh(claim)
    return to_admin_claim(claim)


@router.patch("/items/{item_id}/recovered")
def mark_item_recovered(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    approved = next((c for c in item.claims if c.status == "APPROVED"), None)
    if item.status != "CLAIMED" or approved is None:
        raise HTTPException(
            status_code=400,
            detail="Only an item with an approved claim can be marked recovered",
        )
    if not approved.handover_location:
        raise HTTPException(status_code=400, detail="Assign a handover location first")

    item.status = "RECOVERED"
    approved.handover_status = "COMPLETED"
    db.commit()
    return {
        "item_id": item.id,
        "item_status": item.status,
        "claim_id": approved.id,
        "handover_status": approved.handover_status,
    }
