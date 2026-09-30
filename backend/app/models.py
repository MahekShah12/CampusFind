from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True, default="")
    role = Column(String, nullable=False, default="STUDENT")  # STUDENT | ADMIN

    claims = relationship("Claim", back_populates="user", foreign_keys="Claim.user_id")
    items = relationship("Item", back_populates="owner", foreign_keys="Item.user_id")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # LOST | FOUND
    item_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String, nullable=False)
    date_reported = Column(String, nullable=False)
    phone = Column(String, nullable=True, default="")
    image_url = Column(String, nullable=True, default="")
    # PUBLIC = shown to everyone, PRIVATE = hidden from public views (used
    # only for ownership verification, same treatment as private_detail),
    # NONE = no image was uploaded at all.
    image_visibility = Column(String, nullable=False, default="PUBLIC")
    private_detail = Column(Text, nullable=True, default="")
    status = Column(String, nullable=False, default="ACTIVE")  # ACTIVE | CLAIMED | RECOVERED
    reported_by = Column(String, nullable=True, default="")
    contact_email = Column(String, nullable=True, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    # Who reported this item (used for "My Reports" and ownership checks)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", back_populates="items", foreign_keys=[user_id])
    claims = relationship("Claim", back_populates="item")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    claimant_name = Column(String, nullable=True, default="")
    claimant_email = Column(String, nullable=True, default="")
    claimant_phone = Column(String, nullable=True, default="")
    claim_detail = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="PENDING")  # PENDING | APPROVED | REJECTED
    created_at = Column(DateTime, default=datetime.utcnow)
    # Admin review + safe handover
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    handover_location = Column(String, nullable=True, default="")
    # NOT_ASSIGNED | READY_FOR_PICKUP | COMPLETED
    handover_status = Column(String, nullable=False, default="NOT_ASSIGNED")

    item = relationship("Item", back_populates="claims")
    user = relationship("User", back_populates="claims", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
