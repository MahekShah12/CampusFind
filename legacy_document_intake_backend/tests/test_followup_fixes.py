"""
Regression tests for the final conversation-handling bug-fix pass:

  1. Pending contradiction clarification is resolved using field
     context, even when the user's follow-up answer contains only
     the new value.
  2. Natural-language correction phrases ("change my name to X",
     "change it to X", etc.) are understood, not only ones that
     start with "actually".
  3. Out-of-topic / unrelated messages never mutate unrelated state
     and never falsely complete the intake.
  4. Additional wishes remain the one field where a general
     statement is accepted at face value.
  5. Corrections keep working after the document is already
     complete, and gift corrections still strip "instead".

These tests are purely additive: they do not modify or weaken any
existing test file.
"""

from app.services.conversation import process_user_message
from app.services.document_generator import generate_document
from app.services.llm_service import MockLLMService


def svc():
    return MockLLMService()


def fill_up_to_address(session_id, service):
    process_user_message(session_id, "My full name is Jane Smith", service)


def fill_up_to_executor(session_id, service):
    process_user_message(session_id, "My full name is Jane Smith", service)
    process_user_message(
        session_id, "I live at 12 Oxford Street", service
    )
    process_user_message(
        session_id, "Yes it covers worldwide assets", service
    )
    process_user_message(session_id, "I have no children", service)


def fill_up_to_gifts(session_id, service):
    fill_up_to_executor(session_id, service)
    process_user_message(session_id, "James is my executor", service)
    process_user_message(session_id, "brother", service)


def complete_intake(session_id, service):
    fill_up_to_gifts(session_id, service)
    process_user_message(session_id, "No specific gifts", service)
    process_user_message(session_id, "No additional wishes", service)


# ---------------------------------------------------------------------
# A. Pending clarification tests
# ---------------------------------------------------------------------


def test_name_contradiction_resolved_by_bare_followup_answer():
    service = svc()
    session_id = "pending-name-1"

    complete_intake(session_id, service)
    process_user_message(session_id, "sorry my name is mahek", service)

    result = process_user_message(session_id, "Mahek", service)

    assert result["state"].full_name == "Mahek"


def test_executor_contradiction_resolved_by_bare_followup_answer():
    service = svc()
    session_id = "pending-executor-1"

    complete_intake(session_id, service)
    process_user_message(session_id, "My executor is Rahul", service)

    result = process_user_message(session_id, "Rahul", service)

    assert result["state"].executor.name == "Rahul"
    assert result["state"].executor.relationship == "brother"


def test_address_contradiction_resolved_by_bare_valid_address():
    service = svc()
    session_id = "pending-address-1"

    complete_intake(session_id, service)
    process_user_message(
        session_id, "My home address is 456 Sadar Road, Nagpur", service
    )

    result = process_user_message(
        session_id, "123 Sadar Road, Nagpur", service
    )

    assert result["state"].home_address == "123 Sadar Road, Nagpur"


def test_pending_clarification_is_cleared_after_resolution():
    service = svc()
    session_id = "pending-clear-1"

    complete_intake(session_id, service)
    process_user_message(session_id, "sorry my name is mahek", service)
    process_user_message(session_id, "Mahek", service)

    from app.storage.session_storage import get_session

    session = get_session(session_id)

    assert session.pending_clarification_field is None


def test_unrelated_message_after_resolution_is_not_treated_as_answer():
    service = svc()
    session_id = "pending-clear-2"

    complete_intake(session_id, service)
    process_user_message(session_id, "sorry my name is mahek", service)
    process_user_message(session_id, "Mahek", service)

    result = process_user_message(
        session_id, "I love playing cricket", service
    )

    assert result["state"].full_name == "Mahek"
    assert result["state"].additional_wishes == ["I love playing cricket"]


# ---------------------------------------------------------------------
# B. Natural correction phrase tests
# ---------------------------------------------------------------------


def test_name_change_with_trailing_change_it_phrase():
    service = svc()
    session_id = "natural-correction-1"

    fill_up_to_address(session_id, service)

    result = process_user_message(
        session_id, "My name is Mahek, change it.", service
    )

    assert result["state"].full_name == "Mahek"


def test_change_my_name_to_phrase():
    service = svc()
    session_id = "natural-correction-2"

    fill_up_to_address(session_id, service)

    result = process_user_message(
        session_id, "Change my name to Mahek.", service
    )

    assert result["state"].full_name == "Mahek"


def test_i_want_to_change_my_name_to_phrase():
    service = svc()
    session_id = "natural-correction-3"

    fill_up_to_address(session_id, service)

    result = process_user_message(
        session_id, "I want to change my name to Mahek.", service
    )

    assert result["state"].full_name == "Mahek"


def test_contextual_change_it_to_for_full_name():
    service = svc()
    session_id = "natural-correction-4"

    result = process_user_message(
        session_id, "Change it to Mahek.", service
    )

    assert result["state"].full_name == "Mahek"


def test_contextual_change_it_to_for_address():
    service = svc()
    session_id = "natural-correction-5"

    fill_up_to_address(session_id, service)

    result = process_user_message(
        session_id, "Change it to 123 Sadar Road, Nagpur.", service
    )

    assert result["state"].home_address == "123 Sadar Road, Nagpur"


def test_contextual_change_it_to_for_executor():
    service = svc()
    session_id = "natural-correction-6"

    fill_up_to_executor(session_id, service)

    result = process_user_message(
        session_id, "Change it to Rahul.", service
    )

    assert result["state"].executor.name == "Rahul"


def test_natural_correction_works_after_document_completion():
    service = svc()
    session_id = "natural-correction-7"

    complete_intake(session_id, service)

    result = process_user_message(
        session_id, "Change my name to Mahek.", service
    )

    assert result["state"].full_name == "Mahek"


def test_multiple_consecutive_name_changes_keep_latest_value():
    service = svc()
    session_id = "natural-correction-8"

    process_user_message(session_id, "My full name is Jane", service)
    process_user_message(
        session_id, "Actually, my name is Sarah.", service
    )
    result = process_user_message(
        session_id, "Actually, my name is Mahek.", service
    )

    assert result["state"].full_name == "Mahek"


# ---------------------------------------------------------------------
# C. Out-of-topic tests
# ---------------------------------------------------------------------


def test_out_of_topic_address_does_not_set_address():
    service = svc()
    session_id = "off-topic-address-1"

    process_user_message(session_id, "My full name is Jane Smith", service)

    result = process_user_message(
        session_id, "I love playing cricket", service
    )

    assert result["state"].home_address is None
    assert "address" in result["reply"].lower()


def test_out_of_topic_worldwide_assets_asks_yes_no():
    service = svc()
    session_id = "off-topic-worldwide-1"

    fill_up_to_address(session_id, service)
    process_user_message(session_id, "I live at 12 Oxford Street", service)

    result = process_user_message(
        session_id, "I like painting", service
    )

    assert result["state"].covers_worldwide_assets is None
    assert "yes" in result["reply"].lower() and "no" in result["reply"].lower()


def test_out_of_topic_children_asks_yes_no():
    service = svc()
    session_id = "off-topic-children-1"

    fill_up_to_address(session_id, service)
    process_user_message(session_id, "I live at 12 Oxford Street", service)
    process_user_message(
        session_id, "Yes it covers worldwide assets", service
    )

    result = process_user_message(
        session_id, "I love cricket", service
    )

    assert result["state"].has_children is None
    assert "yes" in result["reply"].lower() and "no" in result["reply"].lower()


def test_out_of_topic_executor_does_not_invent_name():
    service = svc()
    session_id = "off-topic-executor-1"

    fill_up_to_executor(session_id, service)

    result = process_user_message(
        session_id, "I like playing cricket", service
    )

    assert result["state"].executor.name is None


def test_out_of_topic_gifts_does_not_confirm_gift():
    service = svc()
    session_id = "off-topic-gifts-1"

    fill_up_to_gifts(session_id, service)

    result = process_user_message(
        session_id, "I love playing cricket", service
    )

    assert result["state"].specific_gifts == []


def test_out_of_topic_message_does_not_mutate_any_field():
    service = svc()
    session_id = "off-topic-state-protection-1"

    process_user_message(session_id, "My full name is Jane Smith", service)

    before = process_user_message(session_id, "I love cricket", service)

    state = before["state"]

    assert state.home_address is None
    assert state.covers_worldwide_assets is None
    assert state.has_children is None
    assert state.executor.name is None
    assert state.specific_gifts == []


def test_out_of_topic_children_names_does_not_invent_a_name():
    service = svc()
    session_id = "off-topic-children-2"

    fill_up_to_address(session_id, service)
    process_user_message(session_id, "I live at 12 Oxford Street", service)
    process_user_message(
        session_id, "Yes it covers worldwide assets", service
    )
    process_user_message(session_id, "Yes I have children", service)

    result = process_user_message(
        session_id, "I love playing cricket", service
    )

    assert result["state"].children == []


# ---------------------------------------------------------------------
# D. Additional wishes tests
# ---------------------------------------------------------------------


def test_additional_wishes_accepts_general_statement():
    service = svc()
    session_id = "additional-wishes-1"

    complete_intake(session_id, service)

    result = process_user_message(
        session_id, "I love playing cricket", service
    )

    assert result["state"].additional_wishes == ["I love playing cricket"]


def test_additional_wish_after_completion_updates_state():
    service = svc()
    session_id = "additional-wishes-2"

    complete_intake(session_id, service)

    result = process_user_message(
        session_id, "I really enjoy gardening on weekends", service
    )

    assert result["state"].additional_wishes


def test_name_change_is_not_captured_as_additional_wish():
    service = svc()
    session_id = "additional-wishes-3"

    complete_intake(session_id, service)

    result = process_user_message(
        session_id, "Actually, my name is Mahek.", service
    )

    assert result["state"].full_name == "Mahek"
    assert result["state"].additional_wishes == []


def test_gift_message_is_not_captured_as_additional_wish():
    service = svc()
    session_id = "additional-wishes-4"

    complete_intake(session_id, service)

    result = process_user_message(
        session_id, "I want to leave my watch to Sarah.", service
    )

    assert result["state"].specific_gifts == ["Watch to Sarah"]
    assert result["state"].additional_wishes == []


# ---------------------------------------------------------------------
# E. Correction / document consistency tests
# ---------------------------------------------------------------------


def test_name_correction_updates_generated_document():
    service = svc()
    session_id = "doc-consistency-1"

    complete_intake(session_id, service)
    process_user_message(session_id, "sorry my name is mahek", service)
    result = process_user_message(session_id, "Mahek", service)

    document = generate_document(result["state"])

    assert "Mahek" in document
    assert "Jane Smith" not in document


def test_executor_correction_updates_generated_document():
    service = svc()
    session_id = "doc-consistency-2"

    complete_intake(session_id, service)
    process_user_message(session_id, "My executor is Rahul", service)
    result = process_user_message(session_id, "Rahul", service)

    document = generate_document(result["state"])

    assert "Rahul" in document


def test_address_correction_updates_generated_document():
    service = svc()
    session_id = "doc-consistency-3"

    complete_intake(session_id, service)
    process_user_message(
        session_id, "My home address is 456 Sadar Road, Nagpur", service
    )
    result = process_user_message(
        session_id, "123 Sadar Road, Nagpur", service
    )

    document = generate_document(result["state"])

    assert "123 Sadar Road, Nagpur" in document
    assert "456 Sadar Road, Nagpur" not in document


def test_gift_correction_updates_generated_document_without_instead():
    service = svc()
    session_id = "doc-consistency-4"

    fill_up_to_gifts(session_id, service)
    result = process_user_message(
        session_id, "Actually, leave my watch to Sarah instead.", service
    )

    assert result["state"].specific_gifts == ["Watch to Sarah"]

    document = generate_document(result["state"])

    assert "Watch to Sarah" in document
    assert "instead" not in document.lower()


def test_multiple_fields_corrected_in_one_message():
    service = svc()
    session_id = "doc-consistency-5"

    process_user_message(
        session_id,
        "My full name is Jane Smith and my executor is James.",
        service
    )

    result = process_user_message(
        session_id,
        "Actually, my name is Mahek and my executor is Rahul.",
        service
    )

    assert result["state"].full_name == "Mahek"
    assert result["state"].executor.name == "Rahul"


def test_correction_preserves_unrelated_fields():
    service = svc()
    session_id = "doc-consistency-6"

    complete_intake(session_id, service)

    before = process_user_message(session_id, "Mahek", service)
    result = process_user_message(
        session_id, "Change my name to Mahek.", service
    )

    assert result["state"].home_address == before["state"].home_address
    assert result["state"].executor.name == before["state"].executor.name


# ---------------------------------------------------------------------
# F. Explicit empty-value tests
# ---------------------------------------------------------------------


def test_existing_gift_then_no_gifts_is_a_contradiction_not_silent_erase():
    service = svc()
    session_id = "empty-value-1"

    fill_up_to_gifts(session_id, service)
    process_user_message(
        session_id, "I want to leave my watch to Sarah.", service
    )

    result = process_user_message(
        session_id, "I don't have any specific gifts.", service
    )

    assert result["state"].specific_gifts == ["Watch to Sarah"]
    assert "Which is correct" in result["reply"]


def test_existing_wish_then_no_wishes_is_a_contradiction_not_silent_erase():
    service = svc()
    session_id = "empty-value-2"

    complete_intake(session_id, service)
    process_user_message(
        session_id, "I love playing cricket", service
    )

    result = process_user_message(
        session_id, "I don't have any additional wishes.", service
    )

    assert result["state"].additional_wishes == ["I love playing cricket"]
    assert "Which is correct" in result["reply"]