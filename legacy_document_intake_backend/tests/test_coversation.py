"""
Basic conversation flow tests (renamed from the misspelled
tests/test_coversation.py, which was empty).
"""

from app.services.conversation import process_user_message
from app.services.llm_service import MockLLMService


def new_service():
    return MockLLMService()


def test_basic_message_updates_state():
    svc = new_service()

    result = process_user_message(
        "conv-basic-1",
        "My name is Jane Smith.",
        svc
    )

    assert result["state"].full_name == "Jane Smith"
    assert "full_name" in result["confirmed_fields"]


def test_multiple_fields_in_one_message():
    svc = new_service()

    result = process_user_message(
        "conv-multi-1",
        "My name is Jane Smith and I live at 12 Oxford Street.",
        svc
    )

    assert result["state"].full_name == "Jane Smith"
    assert result["state"].home_address == "12 Oxford Street"


def test_multiple_boolean_fields_in_one_message():
    svc = new_service()

    process_user_message(
        "conv-multi-2", "My name is Jane Smith.", svc
    )
    process_user_message(
        "conv-multi-2", "I live at 12 Oxford Street.", svc
    )

    result = process_user_message(
        "conv-multi-2",
        "Yes, it covers worldwide assets and I have no children.",
        svc
    )

    assert result["state"].covers_worldwide_assets is True
    assert result["state"].has_children is False


def test_next_question_is_asked_in_order():
    svc = new_service()

    result = process_user_message(
        "conv-order-1", "My name is Jane Smith.", svc
    )

    assert result["reply"] == "What is your home address?"


def test_explicit_no_gifts_is_confirmed_and_not_repeated():
    svc = new_service()

    result = process_user_message(
        "conv-gifts-1", "No specific gifts.", svc
    )

    assert result["state"].specific_gifts == []
    assert "specific_gifts" in result["confirmed_fields"]
    # The next question must not ask about gifts again.
    assert "gift" not in result["reply"].lower()


def test_explicit_no_additional_wishes_is_confirmed_and_not_repeated():
    svc = new_service()

    result = process_user_message(
        "conv-wishes-1", "No additional wishes.", svc
    )

    assert result["state"].additional_wishes == []
    assert "additional_wishes" in result["confirmed_fields"]
    assert "wishes" not in result["reply"].lower()


def test_full_end_to_end_mock_conversation_reaches_document():
    svc = new_service()
    session_id = "conv-e2e-1"

    process_user_message(
        session_id,
        "My name is Jane Smith and I live at 12 Oxford Street.",
        svc
    )
    process_user_message(
        session_id,
        "Yes, it covers my worldwide assets and I have no children.",
        svc
    )
    process_user_message(session_id, "James is my brother.", svc)
    process_user_message(session_id, "No specific gifts.", svc)
    result = process_user_message(
        session_id, "No additional wishes.", svc
    )

    assert result["reply"] == (
        "Thank you. I have collected all the "
        "required information for your draft."
    )
    assert "Jane Smith" in result["document"]
    assert "James" in result["document"]
    assert "FICTIONAL DOCUMENT" in result["document"]
    assert "NOT LEGAL ADVICE" in result["document"]


def test_llm_exception_is_handled_safely():
    class ExplodingLLMService:
        def process_message(self, **kwargs):
            raise RuntimeError("simulated provider outage")

    result = process_user_message(
        "conv-explode-1", "My name is Jane Smith.", ExplodingLLMService()
    )

    assert "couldn't process" in result["reply"].lower()
    # State must remain untouched by the failure.
    assert result["state"].full_name is None