from datetime import datetime

from sqlalchemy.orm import Session

from app import models

DEMO_ITEMS = [
    dict(
        type="FOUND",
        item_name="iPhone 14 (Midnight Black)",
        category="Electronics",
        description="Found on the second floor study table near the window. Has a matte navy blue protective bumper case and privacy glass screen protector.",
        location="Central Library",
        date_reported="2026-09-30",
        phone="9876543210",
        image_url="https://images.unsplash.com/photo-1592750475338-74b7b21085ab?auto=format&fit=crop&w=800&q=80",
        image_visibility="PUBLIC",
        status="ACTIVE",
        reported_by="Priya Sharma (Student)",
        contact_email="priya.s@campus.edu",
        private_detail="Small Harry Potter Deathly Hallows silver sticker inside the bottom corner of the case, lockscreen shows a golden retriever.",
    ),
    dict(
        type="FOUND",
        item_name="Black Leather Bi-fold Wallet",
        category="Accessories",
        description="Black genuine leather wallet left behind on a corner dining table after lunch hours. Contains cash, student ID, and cards.",
        location="Cafeteria",
        date_reported="2026-09-30",
        phone="9123456780",
        image_url="https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=800&q=80",
        image_visibility="PRIVATE",
        status="ACTIVE",
        reported_by="Amit Deshmukh (Staff)",
        contact_email="cafeteria.admin@campus.edu",
        private_detail="There is a small laminate photo of Lord Ganesh and a blue city metro card hidden inside the zipped coin pouch.",
    ),
    dict(
        type="LOST",
        item_name="Apple AirPods Pro (2nd Gen)",
        category="Electronics",
        description="Lost during the morning lectures in Block A. White charging case with a small scratch near the hinge. Essential for my project work.",
        location="Block A",
        date_reported="2026-09-29",
        phone="8765432109",
        image_url="https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?auto=format&fit=crop&w=800&q=80",
        image_visibility="PUBLIC",
        status="ACTIVE",
        reported_by="Vikram Malhotra",
        contact_email="vikram.m@campus.edu",
        private_detail="",
    ),
    dict(
        type="FOUND",
        item_name="Casio fx-991EX ClassWiz Calculator",
        category="Electronics",
        description="Found in Lecture Hall 204 on desk #14 right after the Engineering Mathematics midterm exam.",
        location="Block B",
        date_reported="2026-09-29",
        phone="7890123456",
        image_url="https://images.unsplash.com/photo-1594980596870-8aa52a78d8cd?auto=format&fit=crop&w=800&q=80",
        image_visibility="PUBLIC",
        status="ACTIVE",
        reported_by="Kavita Rao (TA)",
        contact_email="kavita.rao@campus.edu",
        private_detail="Back cover has a formula cheat sheet taped inside with pencil handwriting and roll number ending in 104.",
    ),
    dict(
        type="LOST",
        item_name="Navy Blue SwissGear Laptop Backpack",
        category="Accessories",
        description="Left near the front row of the main auditorium during the tech symposium inauguration. Contains spiral notebooks and a grey Dell charger.",
        location="Auditorium",
        date_reported="2026-09-28",
        phone="9988776655",
        image_url="https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80",
        image_visibility="PUBLIC",
        status="ACTIVE",
        reported_by="Rohan Verma",
        contact_email="rohan.v@campus.edu",
        private_detail="",
    ),
    dict(
        type="FOUND",
        item_name="Campus Student ID Card",
        category="Documents",
        description="Student identity badge with university lanyard found near the goal post bench after evening football practice.",
        location="Sports Ground",
        date_reported="2026-09-28",
        phone="6234567890",
        image_url="https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=800&q=80",
        image_visibility="PRIVATE",
        status="ACTIVE",
        reported_by="Coach Sandeep",
        contact_email="sports.office@campus.edu",
        private_detail="Card belongs to Computer Science 3rd year student, ID card has a yellow 'Library Pass 2026' sticker on the reverse.",
    ),
    dict(
        type="LOST",
        item_name="Honda Bike Smart Key with Keychain",
        category="Accessories",
        description="Black electronic smart key fob with Honda emblem dropped somewhere between Student Hostel 3 and the bike parking lot.",
        location="Parking",
        date_reported="2026-09-27",
        phone="8899001122",
        image_url="",
        image_visibility="NONE",
        status="ACTIVE",
        reported_by="Siddharth Jain",
        contact_email="siddharth.j@campus.edu",
        private_detail="",
    ),
    dict(
        type="FOUND",
        item_name="Thomas' Calculus (14th Edition) Hardcover",
        category="Books",
        description="Standard university textbook found in the common recreation room on the 1st floor of Hostel Block C.",
        location="Hostel",
        date_reported="2026-09-27",
        phone="7766554433",
        image_url="https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80",
        image_visibility="PUBLIC",
        status="ACTIVE",
        reported_by="Hostel Warden Office",
        contact_email="hostel3.warden@campus.edu",
        private_detail="Inside title page has highlighted dedication 'Gift from Dad 2024' with bookmarks on Chapter 7 integration.",
    ),
    dict(
        type="LOST",
        item_name="Hydro Flask 32oz (Olive Green)",
        category="Other",
        description="Wide mouth insulated vacuum water bottle with black flex cap. Forgotten on the spectator steps near the basketball court.",
        location="Sports Ground",
        date_reported="2026-09-26",
        phone="9445566778",
        image_url="https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=800&q=80",
        image_visibility="PUBLIC",
        status="ACTIVE",
        reported_by="Meera Krishnan",
        contact_email="meera.k@campus.edu",
        private_detail="",
    ),
]

DEMO_USERS = [
    dict(name="Rahul Sharma", email="rahul.sharma@campus.edu", phone="9876543210", role="STUDENT"),
    dict(name="Ananya Patel", email="ananya.p@campus.edu", phone="9123456789", role="STUDENT"),
    dict(name="Devendra Verma", email="dev.v@campus.edu", phone="9456789012", role="STUDENT"),
    dict(name="Campus Admin", email="admin@campus.edu", phone="9000000000", role="ADMIN"),
]

# item_name fragment -> demo user email who "reported" it (so My Reports has data)
ITEM_OWNERS = {
    "Wallet": "dev.v@campus.edu",
    "iPhone": "dev.v@campus.edu",
    "Calculator": "rahul.sharma@campus.edu",
    "AirPods": "rahul.sharma@campus.edu",
    "Backpack": "ananya.p@campus.edu",
    "Hydro Flask": "ananya.p@campus.edu",
}


def seed_if_empty(db: Session) -> None:
    if db.query(models.Item).count() > 0:
        return

    users = [models.User(**u) for u in DEMO_USERS]
    db.add_all(users)
    db.commit()

    by_email = {u.email: u for u in users}
    admin = by_email["admin@campus.edu"]

    items = [models.Item(**i) for i in DEMO_ITEMS]
    for it in items:
        for fragment, email in ITEM_OWNERS.items():
            if fragment in it.item_name:
                it.user_id = by_email[email].id
    db.add_all(items)
    db.commit()

    # A couple of demo claims so the Claims page isn't empty on first run.
    wallet = next((i for i in items if "Wallet" in i.item_name), None)
    phone_item = next((i for i in items if "iPhone" in i.item_name), None)
    calculator = next((i for i in items if "Calculator" in i.item_name), None)

    claims = []
    if wallet:
        claims.append(
            models.Claim(
                item_id=wallet.id,
                user_id=users[0].id,
                claimant_name="Rahul Sharma",
                claimant_email="rahul.sharma@campus.edu",
                claimant_phone="9876543210",
                claim_detail="There is a small laminate photo of Lord Ganesh and my blue city metro card hidden inside the zipped coin pouch. My driving license is also inside.",
                status="PENDING",
            )
        )
    if phone_item:
        claims.append(
            models.Claim(
                item_id=phone_item.id,
                user_id=users[1].id,
                claimant_name="Ananya Patel",
                claimant_email="ananya.p@campus.edu",
                claimant_phone="9123456789",
                claim_detail="Small Harry Potter silver sticker on the inner bottom case and a golden retriever wallpaper.",
                status="APPROVED",
                reviewed_by=admin.id,
                reviewed_at=datetime.utcnow(),
                handover_location="Student Help Desk",
                handover_status="READY_FOR_PICKUP",
            )
        )
        phone_item.status = "CLAIMED"
    if calculator:
        claims.append(
            models.Claim(
                item_id=calculator.id,
                user_id=users[2].id,
                claimant_name="Devendra Verma",
                claimant_email="dev.v@campus.edu",
                claimant_phone="9456789012",
                claim_detail="It's a black calculator with nothing on the cover.",
                status="REJECTED",
                reviewed_by=admin.id,
                reviewed_at=datetime.utcnow(),
            )
        )

    if claims:
        db.add_all(claims)
        db.commit()
