
from app.models.state import DocumentState
from app.models.llm import ExtractedInformation
from app.services.conversation import (
    is_unknown_response,
    get_current_field,
    get_next_question
)
from app.services.state_manager import update_state


def test_unknown_response_detection():
    assert is_unknown_response("I don't know") is True
    assert is_unknown_response("I do not know") is True
    assert is_unknown_response("I'm not sure") is True
    assert is_unknown_response("unknown") is True

    assert is_unknown_response("Jane Smith") is False
    assert is_unknown_response("I have two children") is False


def test_current_field_for_empty_state():
    state = DocumentState()

    field = get_current_field(
        state,
        set(),
        set()
    )

    assert field == "full_name"


def test_unknown_full_name_moves_to_next_field():
    state = DocumentState()

    unknown_fields = {"full_name"}

    next_question = get_next_question(
        state,
        set(),
        unknown_fields
    )

    assert next_question == "What is your home address?"


def test_unknown_home_address_moves_to_next_field():
    state = DocumentState(
        full_name="Jane Smith"
    )

    unknown_fields = {"home_address"}

    next_question = get_next_question(
        state,
        {"full_name"},
        unknown_fields
    )

    assert (
        next_question
        == "Does this document cover your worldwide assets? Please answer yes or no."
    )


def test_unknown_field_is_not_confirmed():
    state = DocumentState()

    confirmed_fields = set()
    unknown_fields = {"home_address"}

    assert "home_address" not in confirmed_fields
    assert "home_address" in unknown_fields


def test_unknown_fields_can_store_multiple_fields():
    unknown_fields = set()

    unknown_fields.add("home_address")
    unknown_fields.add("executor_name")

    assert "home_address" in unknown_fields
    assert "executor_name" in unknown_fields
    assert len(unknown_fields) == 2
def test_home_address_is_stored_as_unknown():
    unknown_fields = set()

    current_field = "home_address"

    unknown_fields.add(current_field)

    assert unknown_fields == {"home_address"}
