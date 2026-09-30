from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/demo-users", response_model=list[schemas.UserOut])
def demo_users(db: Session = Depends(get_db)):
    """Users shown on the demo login screen."""
    return db.query(models.User).order_by(models.User.role.desc(), models.User.id).all()


@router.post("/login", response_model=schemas.UserOut)
def demo_login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.email == payload.email.strip().lower())
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="Unknown demo user")
    return user


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user
