import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import Base, get_db
from app.main import app

STUDENT_A = "student.a@test.edu"
STUDENT_B = "student.b@test.edu"
ADMIN = "admin@test.edu"


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = Session()
    db.add_all(
        [
            models.User(name="Student A", email=STUDENT_A, phone="9876543210", role="STUDENT"),
            models.User(name="Student B", email=STUDENT_B, phone="9123456789", role="STUDENT"),
            models.User(name="Admin", email=ADMIN, phone="9000000000", role="ADMIN"),
        ]
    )
    db.commit()
    yield db
    db.close()


@pytest.fixture()
def client(db_session):
    def override():
        yield db_session

    app.dependency_overrides[get_db] = override
    # No `with` block -> startup (real DB seeding) is not triggered.
    yield TestClient(app)
    app.dependency_overrides.clear()


def h(email):
    return {"X-User-Email": email}


@pytest.fixture()
def found_item(client):
    """Student A reports a FOUND item with a PRIVATE image + secret."""
    r = client.post(
        "/api/items",
        headers=h(STUDENT_A),
        json={
            "type": "FOUND",
            "item_name": "Black Wallet",
            "category": "Accessories",
            "description": "Black leather wallet",
            "location": "Cafeteria",
            "phone": "9876543210",
            "image_url": "/uploads/secret-wallet.jpg",
            "image_visibility": "PRIVATE",
            "private_detail": "Small Ganesh photo inside",
        },
    )
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture()
def pending_claim(client, found_item):
    """Student B claims the item."""
    r = client.post(
        "/api/claims",
        headers=h(STUDENT_B),
        json={"item_id": found_item["id"], "claim_detail": "Small Ganesh photo inside"},
    )
    assert r.status_code == 201, r.text
    return r.json()
