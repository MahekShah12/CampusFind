"""
Focused regression tests for:

- FIX 1A: additional full-name phrasings ("Name is Eve",
  "Eve is my name", "My full name is Eve").
- FIX 1B: additional executor phrasings ("James is my executor",
  "James will be my executor") that previously extracted nothing at
  all (or, in the "Eve is my name" case, wrongly produced executor
  information instead of a full name).
- FIX 2: gift-correction output no longer keeps the trailing
  correction word "instead" as part of the gift text.

These are intentionally narrow, additive tests. The full existing
suite (see the other test files) already covers everything these
fixes must not break.
"""

from app.services.conversation import process_user_message
from app.services.llm_service import MockLLMService


def new_service():
    return MockLLMService()


def test_name_is_eve():
    result = process_user_message(
        "phrasing-name-is-eve", "Name is Eve", new_service()
    )
    assert result["state"].full_name == "Eve"


def test_eve_is_my_name():
    result = process_user_message(
        "phrasing-eve-is-my-name", "Eve is my name", new_service()
    )
    assert result["state"].full_name == "Eve"
    # Must never be misread as executor information.
    assert (
        result["state"].executor.name is None
        and result["state"].executor.relationship is None
    )


def test_my_full_name_is_eve():
    result = process_user_message(
        "phrasing-full-name-is-eve", "My full name is Eve", new_service()
    )
    assert result["state"].full_name == "Eve"


def test_james_is_my_executor_extracts_name_only():
    result = process_user_message(
        "phrasing-james-is-executor",
        "James is my executor",
        new_service()
    )
    assert result["state"].executor.name == "James"
    assert result["state"].executor.relationship != "executor"


def test_james_will_be_my_executor_extracts_name_only():
    result = process_user_message(
        "phrasing-james-will-be-executor",
        "James will be my executor",
        new_service()
    )
    assert result["state"].executor.name == "James"
    assert result["state"].executor.relationship != "executor"


def test_brother_james_still_extracts_relationship():
    result = process_user_message(
        "phrasing-brother-james",
        "My brother James is my executor",
        new_service()
    )
    assert result["state"].executor.name == "James"
    assert result["state"].executor.relationship == "brother"


def test_gift_correction_strips_trailing_instead():
    svc = new_service()
    session_id = "phrasing-gift-correction"

    process_user_message(
        session_id, "I want to leave my watch to Sarah.", svc
    )
    result = process_user_message(
        session_id,
        "Actually, leave my watch to Sarah instead.",
        svc
    )

    assert result["state"].specific_gifts == ["Watch to Sarah"]


def test_gift_without_correction_is_unaffected():
    """
    The word "instead" must only be stripped as a trailing correction
    marker; ordinary gift phrasing without it must be unchanged.
    """
    result = process_user_message(
        "phrasing-gift-plain",
        "I want to leave my watch to Sarah.",
        new_service()
    )
    assert result["state"].specific_gifts == ["Watch to Sarah"]