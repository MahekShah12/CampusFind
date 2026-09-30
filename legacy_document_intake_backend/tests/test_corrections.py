"""
Correction handling: previously confirmed values can be replaced
when the user's wording clearly signals a correction. The old
value must not remain in the state or the generated document.
"""

from app.services.conversation import process_user_message
from app.services.llm_service import MockLLMService


def new_service():
    return MockLLMService()


def test_name_correction_updates_state_and_document():
    svc = new_service()
    session_id = "corr-name-1"

    process_user_message(session_id, "My name is Jane Smith.", svc)
    result = process_user_message(
        session_id, "Actually, my name is Jane Brown.", svc
    )

    assert result["state"].full_name == "Jane Brown"
    assert "Jane Brown" in result["document"]
    assert "Jane Smith" not in result["document"]


def test_address_correction_updates_state():
    svc = new_service()
    session_id = "corr-addr-1"

    process_user_message(
        session_id, "I live at 12 Oxford Street.", svc
    )
    result = process_user_message(
        session_id,
        "Actually, my address should be 45 Baker Street.",
        svc
    )

    assert result["state"].home_address == "45 Baker Street"


def test_children_correction_after_confirmed_no_children():
    svc = new_service()
    session_id = "corr-children-1"

    process_user_message(session_id, "I have no children.", svc)
    result = process_user_message(
        session_id, "Actually, I have two children.", svc
    )

    assert result["state"].has_children is True


def test_executor_correction():
    svc = new_service()
    session_id = "corr-exec-1"

    process_user_message(session_id, "James is my brother.", svc)
    result = process_user_message(
        session_id, "Actually, my executor is my sister Sarah.", svc
    )

    assert result["state"].executor.name == "Sarah"
    assert result["state"].executor.relationship == "sister"


def test_document_reflects_corrected_state_only():
    svc = new_service()
    session_id = "corr-doc-1"

    process_user_message(session_id, "My name is Jane Smith.", svc)
    process_user_message(
        session_id, "I live at 12 Oxford Street.", svc
    )
    process_user_message(
        session_id, "Actually, my name is Jane Brown.", svc
    )
    result = process_user_message(
        session_id, "No specific gifts.", svc
    )

    document = result["document"]

    assert "Jane Brown" in document
    assert "Jane Smith" not in document
    assert "12 Oxford Street" in document