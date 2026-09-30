import re
from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator

ItemType = Literal["LOST", "FOUND"]
ItemStatus = Literal["ACTIVE", "CLAIMED", "RECOVERED"]
ClaimStatus = Literal["PENDING", "APPROVED", "REJECTED"]
ClaimDecision = Literal["APPROVED", "REJECTED"]
HandoverStatus = Literal["NOT_ASSIGNED", "READY_FOR_PICKUP", "COMPLETED"]
ImageVisibility = Literal["PUBLIC", "PRIVATE", "NONE"]

PHONE_RE = re.compile(r"^[6-9]\d{9}$")

HANDOVER_LOCATIONS = [
    "College Security Office",
    "Student Help Desk",
    "Main Reception",
    "Library Help Desk",
    "Other",
]


# ---------- User schemas ----------

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str


# ---------- Item schemas ----------

class ItemCreate(BaseModel):
    type: ItemType
    item_name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    date_reported: Optional[str] = None
    phone: str = Field(..., min_length=1)
    image_url: Optional[str] = ""
    image_visibility: ImageVisibility = "PUBLIC"
    private_detail: Optional[str] = ""
    reported_by: Optional[str] = ""
    contact_email: Optional[str] = ""

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v or "")
        if not PHONE_RE.match(digits):
            raise ValueError(
                "phone must be a valid 10-digit mobile number starting with 6-9"
            )
        return digits


class ItemPublicOut(BaseModel):
    """Shape returned by PUBLIC endpoints. Never contains phone,
    private_detail or a PRIVATE image URL."""
    id: int
    type: str
    item_name: str
    category: str
    description: str
    location: str
    date_reported: str
    image_url: Optional[str] = ""
    image_visibility: str = "PUBLIC"
    status: str
    reported_by: Optional[str] = ""
    contact_email: Optional[str] = ""
    is_mine: bool = False

    class Config:
        from_attributes = True


class ItemOwnerOut(ItemPublicOut):
    """Shape returned by GET /api/items/my -- the reporter's own items."""
    phone: Optional[str] = ""
    private_detail: Optional[str] = ""


# ---------- Claim schemas ----------

class ClaimCreate(BaseModel):
    item_id: int
    claimant_name: Optional[str] = ""
    claimant_email: Optional[str] = ""
    claimant_phone: Optional[str] = ""
    claim_detail: str = Field(..., min_length=1)


class MyClaimOut(BaseModel):
    """Student view of their OWN claim. No private detail, no admin data."""
    id: int
    item_id: int
    item_name: str
    item_type: str = ""
    item_location: Optional[str] = ""
    item_image: Optional[str] = ""
    item_image_visibility: Optional[str] = "PUBLIC"
    item_status: str = ""
    claim_detail: str
    status: str
    handover_location: Optional[str] = ""
    handover_status: str = "NOT_ASSIGNED"
    date_claimed: str


class AdminClaimOut(BaseModel):
    id: int
    item_id: int
    item_name: str
    item_type: str = ""
    item_category: str = ""
    item_location: str = ""
    item_description: str = ""
    item_status: str = ""
    item_image: Optional[str] = ""
    item_image_visibility: str = "PUBLIC"
    item_private_detail: Optional[str] = ""
    reporter_name: Optional[str] = ""
    reporter_email: Optional[str] = ""
    reporter_phone: Optional[str] = ""
    claimant_name: Optional[str] = ""
    claimant_email: Optional[str] = ""
    claimant_phone: Optional[str] = ""  # masked
    claim_detail: str
    status: str
    handover_location: Optional[str] = ""
    handover_status: str = "NOT_ASSIGNED"
    reviewed_by_name: Optional[str] = ""
    reviewed_at: Optional[datetime] = None
    date_claimed: str


class ClaimDecisionUpdate(BaseModel):
    status: ClaimDecision
    # Required when approving.
    handover_location: Optional[str] = None


class HandoverUpdate(BaseModel):
    handover_location: Optional[str] = None
    handover_status: Optional[Literal["READY_FOR_PICKUP", "COMPLETED"]] = None


class AdminStats(BaseModel):
    total_items: int
    pending_claims: int
    approved_claims: int
    recovered_items: int


class UploadOut(BaseModel):
    image_url: str
