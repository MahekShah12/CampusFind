import pytest

from app.models.state import DocumentState, Executor
from app.models.llm import LLMResponse
from app.services.document_generator import generate_document
from app.services.validator import validate_llm_response, LLMValidationError
from app.services.conversation import process_user_message


def test_document_contains_state():

    state = DocumentState(
        full_name="Jane Smith",
        home_address="12 Oxford Street",
        covers_worldwide_assets=True,
        has_children=False,
        executor=Executor(
            name="James",
            relationship="brother"
        )
    )

    document = generate_document(state)

    assert "Jane Smith" in document
    assert "12 Oxford Street" in document
    assert "James" in document
    assert "brother" in document


def test_document_contains_disclaimer():

    state = DocumentState()

    document = generate_document(state)

    assert "FICTIONAL DOCUMENT" in document
    assert "NOT LEGAL ADVICE" in document

# ============================================================
# STATE PROTECTION
#
# Invalid or malformed LLM output must never be able to modify
# session.state. Validation happens before any state update.
# ============================================================

def test_wrong_field_shape_is_rejected_before_reaching_state():

    with pytest.raises(LLMValidationError):
        validate_llm_response({"wrong_field": "invalid"})


def test_invalid_field_type_is_rejected_before_reaching_state():

    with pytest.raises(LLMValidationError):
        validate_llm_response(
            {
                "extracted": {
                    "covers_worldwide_assets": "maybe"
                }
            }
        )


def test_malformed_llm_response_does_not_modify_conversation_state():

    class BrokenLLMService:
        def process_message(self, **kwargs):
            raise ValueError("malformed JSON from provider")

    result = process_user_message(
        "state-protect-malformed-1",
        "My name is Jane Smith.",
        BrokenLLMService()
    )

    assert result["state"].full_name is None
    assert result["state"] == DocumentState()


def test_state_object_identity_is_not_replaced_on_failure():

    class BrokenLLMService:
        def process_message(self, **kwargs):
            raise RuntimeError("provider error")

    session_id = "state-protect-identity-1"

    # Establish some confirmed state first.
    from app.services.llm_service import MockLLMService
    process_user_message(
        session_id, "My name is Jane Smith.", MockLLMService()
    )

    before = process_user_message(
        session_id, "irrelevant message", BrokenLLMService()
    )

    # The previously confirmed value must survive the failed turn.
    assert before["state"].full_name == "Jane Smith"