"""
Contradiction handling: conflicting information given WITHOUT
correction wording must never silently overwrite confirmed state.
The assistant must ask for clarification, and the state must only
change after the user clarifies.
"""

from app.services.conversation import process_user_message
from app.services.llm_service import MockLLMService


def new_service():
    return MockLLMService()


def test_contradiction_does_not_change_state_before_clarification():
    svc = new_service()
    session_id = "contra-children-1"

    process_user_message(session_id, "I have no children.", svc)

    before = process_user_message(session_id, "I have children.", svc)

    assert before["state"].has_children is False
    assert "Which is correct" in before["reply"]


def test_contradiction_is_resolved_after_explicit_correction():
    svc = new_service()
    session_id = "contra-children-2"

    process_user_message(session_id, "I have no children.", svc)
    process_user_message(session_id, "I have children.", svc)

    after = process_user_message(
        session_id, "Actually, I have two children.", svc
    )

    assert after["state"].has_children is True


def test_name_contradiction_without_correction_wording_is_flagged():
    svc = new_service()
    session_id = "contra-name-1"

    process_user_message(session_id, "My name is Jane Smith.", svc)

    result = process_user_message(
        session_id, "My name is Jane Brown.", svc
    )

    assert result["state"].full_name == "Jane Smith"
    assert result["reply"]


def test_ambiguous_answer_requests_clarification_without_state_change():
    svc = new_service()
    session_id = "contra-ambiguous-1"

    result = process_user_message(
        session_id, "Maybe I have children.", svc
    )

    assert result["state"].has_children is None
    assert "clarify" in result["reply"].lower()


def test_invalid_llm_response_does_not_modify_state():
    class BadLLMService:
        def process_message(self, **kwargs):
            raise ValueError("malformed / invalid structured output")

    result = process_user_message(
        "contra-invalid-1", "My name is Jane Smith.", BadLLMService()
    )

    assert result["state"].full_name is None
    assert "couldn't process" in result["reply"].lower()