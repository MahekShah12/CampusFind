import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import CORS_ORIGINS, SEED_DEMO_DATA, UPLOAD_DIR
from app.database import Base, engine, SessionLocal
from app import models  # noqa: F401  (ensures models are registered on Base)
from app.routers import items, claims, upload, auth, admin
from app.migrate import run_light_migrations
from app.seed import seed_if_empty

app = FastAPI(title="CampusFind API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    run_light_migrations(engine)
    if SEED_DEMO_DATA:
        db = SessionLocal()
        try:
            seed_if_empty(db)
        finally:
            db.close()


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(items.router)
app.include_router(claims.router)
app.include_router(upload.router)
app.include_router(admin.router)