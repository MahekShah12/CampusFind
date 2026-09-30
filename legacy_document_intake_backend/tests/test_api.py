"""
API-level tests using FastAPI's TestClient, driven through
app.main (LLM_PROVIDER=mock, no Groq API key required — see
backend/.env / .env.example).
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_endpoint_basic_message():
    response = client.post(
        "/api/chat",
        json={
            "session_id": "api-test-1",
            "message": "My name is Jane Smith."
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data["session_id"] == "api-test-1"
    assert data["state"]["full_name"] == "Jane Smith"
    assert "full_name" in data["confirmed_fields"]
    assert "FICTIONAL DOCUMENT" in data["document"]


def test_chat_endpoint_multiple_fields_and_no_llm_error():
    session_id = "api-test-2"

    r1 = client.post(
        "/api/chat",
        json={
            "session_id": session_id,
            "message": (
                "My name is Jane Smith and I live at "
                "12 Oxford Street."
            )
        }
    )
    assert r1.json()["state"]["full_name"] == "Jane Smith"
    assert r1.json()["state"]["home_address"] == "12 Oxford Street"

    r2 = client.post(
        "/api/chat",
        json={
            "session_id": session_id,
            "message": (
                "Yes, it covers my worldwide assets and "
                "I have no children."
            )
        }
    )

    data = r2.json()
    assert data["state"]["covers_worldwide_assets"] is True
    assert data["state"]["has_children"] is False

    # Mock mode must never surface the generic LLM-failure message.
    assert "couldn't process" not in data["reply"].lower()


def test_openapi_docs_available():
    response = client.get("/openapi.json")
    assert response.status_code == 200