"""Very small demo-only auth.

The frontend "logs in" as one of the seeded demo users and then sends the
user's email in the `X-User-Email` header on every request. The backend looks
the user up and enforces the role on every protected endpoint. This is NOT
production authentication -- it exists so the hackathon demo can show real
server-side role-based access control without OAuth/JWT.
"""
from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import get_db


def get_optional_user(
    x_user_email: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> Optional[models.User]:
    if not x_user_email:
        return None
    return (
        db.query(models.User)
        .filter(models.User.email == x_user_email.strip().lower())
        .first()
    )


def get_current_user(user: Optional[models.User] = Depends(get_optional_user)) -> models.User:
    if user is None:
        raise HTTPException(status_code=401, detail="Login required")
    return user


def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin privileges are required")
    return user
