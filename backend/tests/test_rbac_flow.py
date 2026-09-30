from tests.conftest import STUDENT_A, STUDENT_B, ADMIN, h

LOC = "College Security Office"


# ---------------- Authorization ----------------

def test_admin_endpoints_require_login(client):
    assert client.get("/api/admin/claims").status_code == 401


def test_student_cannot_list_admin_claims(client, pending_claim):
    assert client.get("/api/admin/claims", headers=h(STUDENT_B)).status_code == 403
    assert client.get(f"/api/admin/claims/{pending_claim['id']}", headers=h(STUDENT_B)).status_code == 403
    assert client.get("/api/admin/stats", headers=h(STUDENT_B)).status_code == 403


def test_student_cannot_approve_or_reject(client, pending_claim):
    cid = pending_claim["id"]
    for status in ("APPROVED", "REJECTED"):
        r = client.patch(
            f"/api/admin/claims/{cid}",
            headers=h(STUDENT_B),
            json={"status": status, "handover_location": LOC},
        )
        assert r.status_code == 403
    # Even the reporter of the item cannot decide
    r = client.patch(
        f"/api/admin/claims/{cid}", headers=h(STUDENT_A),
        json={"status": "APPROVED", "handover_location": LOC},
    )
    assert r.status_code == 403


def test_student_cannot_mark_recovered_or_handover(client, found_item, pending_claim):
    assert client.patch(f"/api/admin/items/{found_item['id']}/recovered", headers=h(STUDENT_A)).status_code == 403
    assert client.patch(
        f"/api/admin/claims/{pending_claim['id']}/handover",
        headers=h(STUDENT_B), json={"handover_status": "COMPLETED"},
    ).status_code == 403


def test_public_item_patch_route_is_gone(client, found_item):
    r = client.patch(f"/api/items/{found_item['id']}", headers=h(STUDENT_A), json={"status": "RECOVERED"})
    assert r.status_code == 405


def test_student_sees_only_own_claims(client, found_item, pending_claim):
    mine = client.get("/api/claims/my", headers=h(STUDENT_B)).json()
    assert [c["id"] for c in mine] == [pending_claim["id"]]
    assert client.get("/api/claims/my", headers=h(STUDENT_A)).json() == []
    # the old "list everything" route no longer exists for students
    assert client.get("/api/claims", headers=h(STUDENT_B)).status_code in (404, 405)


def test_my_claims_never_leaks_private_data(client, pending_claim):
    body = client.get("/api/claims/my", headers=h(STUDENT_B)).text
    assert "item_private_detail" not in body
    assert "secret-wallet" not in body


def test_admin_sees_all_claims(client, pending_claim):
    r = client.get("/api/admin/claims", headers=h(ADMIN))
    assert r.status_code == 200
    assert len(r.json()) == 1
    stats = client.get("/api/admin/stats", headers=h(ADMIN)).json()
    assert stats == {"total_items": 1, "pending_claims": 1, "approved_claims": 0, "recovered_items": 0}


# ---------------- Claim flow ----------------

def test_claim_starts_pending(pending_claim):
    assert pending_claim["status"] == "PENDING"
    assert pending_claim["handover_status"] == "NOT_ASSIGNED"


def test_approve_updates_claim_item_and_handover(client, found_item, pending_claim):
    r = client.patch(
        f"/api/admin/claims/{pending_claim['id']}", headers=h(ADMIN),
        json={"status": "APPROVED", "handover_location": LOC},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "APPROVED"
    assert body["handover_location"] == LOC
    assert body["handover_status"] == "READY_FOR_PICKUP"
    assert body["reviewed_by_name"] == "Admin"
    assert client.get(f"/api/items/{found_item['id']}").json()["status"] == "CLAIMED"

    mine = client.get("/api/claims/my", headers=h(STUDENT_B)).json()[0]
    assert mine["status"] == "APPROVED"
    assert mine["handover_location"] == LOC
    assert mine["handover_status"] == "READY_FOR_PICKUP"


def test_approve_requires_valid_location(client, pending_claim):
    url = f"/api/admin/claims/{pending_claim['id']}"
    assert client.patch(url, headers=h(ADMIN), json={"status": "APPROVED"}).status_code == 400
    assert client.patch(url, headers=h(ADMIN), json={"status": "APPROVED", "handover_location": "Dark alley"}).status_code == 400
    ok = client.patch(url, headers=h(ADMIN), json={"status": "APPROVED", "handover_location": "Other: Hostel Gate Desk"})
    assert ok.status_code == 200


def test_reject_leaves_item_active(client, found_item, pending_claim):
    r = client.patch(f"/api/admin/claims/{pending_claim['id']}", headers=h(ADMIN), json={"status": "REJECTED"})
    assert r.status_code == 200
    assert r.json()["status"] == "REJECTED"
    assert r.json()["handover_status"] == "NOT_ASSIGNED"
    assert client.get(f"/api/items/{found_item['id']}").json()["status"] == "ACTIVE"


def test_decision_is_final(client, pending_claim):
    url = f"/api/admin/claims/{pending_claim['id']}"
    client.patch(url, headers=h(ADMIN), json={"status": "REJECTED"})
    r = client.patch(url, headers=h(ADMIN), json={"status": "APPROVED", "handover_location": LOC})
    assert r.status_code == 400


def test_approving_one_claim_rejects_other_pending(client, db_session, found_item, pending_claim):
    from app import models
    other = models.User(name="Student C", email="c@test.edu", role="STUDENT")
    db_session.add(other); db_session.commit()
    c2 = client.post("/api/claims", headers=h("c@test.edu"),
                     json={"item_id": found_item["id"], "claim_detail": "some other guess"}).json()
    client.patch(f"/api/admin/claims/{pending_claim['id']}", headers=h(ADMIN),
                 json={"status": "APPROVED", "handover_location": LOC})
    assert client.get(f"/api/admin/claims/{c2['id']}", headers=h(ADMIN)).json()["status"] == "REJECTED"


def test_claim_rules(client, found_item, pending_claim):
    # own item
    r = client.post("/api/claims", headers=h(STUDENT_A), json={"item_id": found_item["id"], "claim_detail": "mine"})
    assert r.status_code == 400
    # duplicate pending
    r = client.post("/api/claims", headers=h(STUDENT_B), json={"item_id": found_item["id"], "claim_detail": "again"})
    assert r.status_code == 400
    # not logged in
    assert client.post("/api/claims", json={"item_id": found_item["id"], "claim_detail": "x"}).status_code == 401


# ---------------- Privacy ----------------

def test_public_api_hides_private_data(client, found_item):
    for url in ("/api/items", f"/api/items/{found_item['id']}"):
        text = client.get(url).text  # not even logged in
        assert "private_detail" not in text
        assert "Small Ganesh" not in text
        assert "secret-wallet" not in text
        assert "9876543210" not in text
        assert '"phone"' not in text
    assert client.get(f"/api/items/{found_item['id']}").json()["image_url"] == ""
    # also hidden from another logged-in student
    text = client.get(f"/api/items/{found_item['id']}", headers=h(STUDENT_B)).text
    assert "secret-wallet" not in text and "9876543210" not in text


def test_create_item_response_does_not_leak(client, found_item):
    assert "private_detail" not in found_item and "phone" not in found_item
    assert found_item["image_url"] == ""


def test_admin_verification_endpoint_shows_private_data(client, found_item, pending_claim):
    body = client.get(f"/api/admin/claims/{pending_claim['id']}", headers=h(ADMIN)).json()
    assert body["item_private_detail"] == "Small Ganesh photo inside"
    assert body["item_image"] == "/uploads/secret-wallet.jpg"
    assert body["claim_detail"] == "Small Ganesh photo inside"
    assert body["claimant_name"] == "Student B"
    assert body["reporter_phone"] == "9876543210"
    # claimant phone is masked, never raw
    assert "9123456789" not in str(body)
    assert body["claimant_phone"] in ("", "********89")


def test_public_image_still_public(client):
    r = client.post("/api/items", headers=h(STUDENT_A), json={
        "type": "LOST", "item_name": "Bottle", "category": "Other", "description": "Blue",
        "location": "Library", "phone": "9876543210", "image_url": "http://x/y.jpg",
        "image_visibility": "PUBLIC"})
    assert r.status_code == 201
    assert client.get(f"/api/items/{r.json()['id']}").json()["image_url"] == "http://x/y.jpg"


def test_phone_still_mandatory_and_validated(client):
    base = {"type": "LOST", "item_name": "x", "category": "Other", "description": "d",
            "location": "l", "image_visibility": "NONE"}
    assert client.post("/api/items", headers=h(STUDENT_A), json=base).status_code == 422
    assert client.post("/api/items", headers=h(STUDENT_A), json={**base, "phone": "12345"}).status_code == 422
    assert client.post("/api/items", headers=h(STUDENT_A), json={**base, "phone": "98765 43210"}).status_code == 201


def test_report_requires_login(client):
    r = client.post("/api/items", json={"type": "LOST", "item_name": "x", "category": "o",
                    "description": "d", "location": "l", "phone": "9876543210", "image_visibility": "NONE"})
    assert r.status_code == 401


# ---------------- My reports ----------------

def test_my_reports_only_own_items(client, found_item):
    mine = client.get("/api/items/my", headers=h(STUDENT_A)).json()
    assert [i["id"] for i in mine] == [found_item["id"]]
    assert mine[0]["private_detail"] == "Small Ganesh photo inside"  # owner may see own secret
    assert client.get("/api/items/my", headers=h(STUDENT_B)).json() == []
    assert client.get("/api/items/my").status_code == 401
    assert client.get(f"/api/items/{found_item['id']}", headers=h(STUDENT_A)).json()["is_mine"] is True
    assert client.get(f"/api/items/{found_item['id']}", headers=h(STUDENT_B)).json()["is_mine"] is False


# ---------------- Handover ----------------

def _approve(client, cid, loc=LOC):
    return client.patch(f"/api/admin/claims/{cid}", headers=h(ADMIN),
                        json={"status": "APPROVED", "handover_location": loc})


def test_handover_location_can_be_changed(client, pending_claim):
    cid = pending_claim["id"]
    _approve(client, cid)
    r = client.patch(f"/api/admin/claims/{cid}/handover", headers=h(ADMIN), json={"handover_location": "Main Reception"})
    assert r.status_code == 200
    assert r.json()["handover_location"] == "Main Reception"
    assert r.json()["handover_status"] == "READY_FOR_PICKUP"


def test_handover_only_for_approved(client, pending_claim):
    r = client.patch(f"/api/admin/claims/{pending_claim['id']}/handover", headers=h(ADMIN),
                     json={"handover_location": LOC})
    assert r.status_code == 400


def test_handover_completed_recovers_item(client, found_item, pending_claim):
    cid = pending_claim["id"]
    _approve(client, cid)
    r = client.patch(f"/api/admin/claims/{cid}/handover", headers=h(ADMIN), json={"handover_status": "COMPLETED"})
    assert r.status_code == 200 and r.json()["handover_status"] == "COMPLETED"
    assert client.get(f"/api/items/{found_item['id']}").json()["status"] == "RECOVERED"
    # cannot change afterwards
    assert client.patch(f"/api/admin/claims/{cid}/handover", headers=h(ADMIN),
                        json={"handover_location": "Main Reception"}).status_code == 400


def test_mark_recovered_endpoint(client, found_item, pending_claim):
    cid = pending_claim["id"]
    _approve(client, cid)
    r = client.patch(f"/api/admin/items/{found_item['id']}/recovered", headers=h(ADMIN))
    assert r.status_code == 200
    assert r.json()["item_status"] == "RECOVERED"
    assert r.json()["handover_status"] == "COMPLETED"
    mine = client.get("/api/claims/my", headers=h(STUDENT_B)).json()[0]
    assert mine["handover_status"] == "COMPLETED" and mine["item_status"] == "RECOVERED"
    stats = client.get("/api/admin/stats", headers=h(ADMIN)).json()
    assert stats["recovered_items"] == 1 and stats["approved_claims"] == 1


def test_cannot_recover_item_without_approved_claim(client, found_item, pending_claim):
    r = client.patch(f"/api/admin/items/{found_item['id']}/recovered", headers=h(ADMIN))
    assert r.status_code == 400


def test_recovered_item_cannot_be_claimed(client, found_item, pending_claim):
    _approve(client, pending_claim["id"])
    client.patch(f"/api/admin/items/{found_item['id']}/recovered", headers=h(ADMIN))
    r = client.post("/api/claims", headers=h("student.a@test.edu"), json={"item_id": found_item["id"], "claim_detail": "x"})
    assert r.status_code == 400


# ---------------- Demo auth ----------------

def test_demo_login(client):
    r = client.post("/api/auth/login", json={"email": ADMIN})
    assert r.status_code == 200 and r.json()["role"] == "ADMIN"
    assert client.post("/api/auth/login", json={"email": "nobody@x.com"}).status_code == 404
    assert len(client.get("/api/auth/demo-users").json()) == 3
    assert client.get("/api/auth/me", headers=h(STUDENT_A)).json()["role"] == "STUDENT"
    assert client.get("/api/auth/me").status_code == 401


def test_unknown_user_header_is_rejected(client):
    assert client.get("/api/claims/my", headers=h("ghost@x.com")).status_code == 401
