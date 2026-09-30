"""
Direct tests of MockLLMService's extraction behaviour, matching the
scenarios described in the assignment. The mock must work fully
offline, without any API key, and must never invent information.
"""

from app.services.llm_service import MockLLMService


def process(message, state=None, history=None):
    return MockLLMService().process_message(
        message=message,
        current_state=state or {},
        conversation_history=history or []
    )


def test_extracts_full_name():
    result = process("My name is Jane Smith.")
    assert result.extracted.full_name == "Jane Smith"


def test_extracts_address():
    result = process("I live at 12 Oxford Street.")
    assert result.extracted.home_address == "12 Oxford Street"


def test_extracts_both_name_and_address_in_one_message():
    result = process(
        "My name is Jane Smith and I live at 12 Oxford Street."
    )
    assert result.extracted.full_name == "Jane Smith"
    assert result.extracted.home_address == "12 Oxford Street"


def test_worldwide_assets_yes():
    result = process("Yes, it covers my worldwide assets.")
    assert result.extracted.covers_worldwide_assets is True


def test_worldwide_assets_no():
    result = process("No, it does not cover worldwide assets.")
    assert result.extracted.covers_worldwide_assets is False


def test_no_children():
    result = process("I have no children.")
    assert result.extracted.has_children is False


def test_has_children_with_names():
    result = process("I have children: Alice and Bob.")
    assert result.extracted.has_children is True
    assert result.extracted.children == ["Alice", "Bob"]


def test_executor_name_and_relationship():
    result = process("James is my brother.")
    assert result.extracted.executor.name == "James"
    assert result.extracted.executor.relationship == "brother"


def test_specific_gift_extracted():
    result = process("I want to leave my watch to Alice.")
    assert result.extracted.specific_gifts
    assert any(
        "watch" in gift.lower()
        for gift in result.extracted.specific_gifts
    )


def test_no_specific_gifts_is_explicit_empty_list():
    result = process("No specific gifts.")
    assert result.extracted.specific_gifts == []


def test_additional_wish_extracted():
    result = process("I want my funeral to be private.")
    assert result.extracted.additional_wishes
    assert any(
        "funeral" in wish.lower()
        for wish in result.extracted.additional_wishes
    )


def test_no_additional_wishes_is_explicit_empty_list():
    result = process("No additional wishes.")
    assert result.extracted.additional_wishes == []


def test_ambiguous_children_statement_requests_clarification():
    result = process("Maybe I have children.")
    assert result.extracted.has_children is None
    assert result.clarification_needed is True
    assert result.clarification_question


def test_mock_never_invents_unrelated_fields():
    result = process("My name is Jane Smith.")
    assert result.extracted.home_address is None
    assert result.extracted.has_children is None
    assert result.extracted.executor is None


def test_correction_language_updates_extracted_value():
    result = process(
        "Actually, my name is Jane Brown.",
        state={"full_name": "Jane Smith"}
    )
    assert result.extracted.full_name == "Jane Brown"
    assert result.detected_contradiction is False


def test_unexplained_change_is_a_contradiction_not_silent_update():
    result = process(
        "My name is Jane Brown.",
        state={"full_name": "Jane Smith"}
    )
    assert result.detected_contradiction is True
    assert result.extracted.full_name is None