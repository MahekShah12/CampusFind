"""
Round 3 regression tests (manual-testing report):

1. Address plausibility must accept realistic addresses that have no
   house/building number, as long as they contain a recognizable
   address/location keyword (e.g. "road", "nagpur") -- while still
   rejecting obvious gibberish ("xyz", "qwerty").
2. An answer that is clearly unrelated to the field currently being
   asked (e.g. "No specific gifts." while the executor's name is
   being requested) must NOT be silently stored under a different
   field, must NOT be mistaken for the field actually being asked,
   and must produce a field-specific clarification instead of a
   generic repeat of the question.

Tests are named Test A-L to match the manual test report.
"""

from app.services.conversation import process_user_message
from app.services.llm_service import MockLLMService, _is_plausible_address


def new_service():
    return MockLLMService()


# ================================================================
# Test A -- address without a house/building number is accepted
# ================================================================

def test_A_address_without_number_is_accepted_and_confirmed():
    svc = new_service()
    session_id = "regress-A"

    process_user_message(session_id, "My name is Jane Smith.", svc)
    result = process_user_message(
        session_id, "nikals mandir road itwari nagpur", svc
    )

    assert result["state"].home_address == (
        "nikals mandir road itwari nagpur"
    )
    assert "home_address" in result["confirmed_fields"]


# ================================================================
# Test B -- garbage addresses are still rejected
# ================================================================

def test_B_garbage_addresses_are_rejected():
    for garbage in ["xyz", "qwerty", "hbblbjvcxdtex cuc"]:
        svc = new_service()
        session_id = f"regress-B-{garbage}"

        process_user_message(session_id, "My name is Jane Smith.", svc)
        result = process_user_message(session_id, garbage, svc)

        assert result["state"].home_address is None, garbage
        assert "home_address" not in result["confirmed_fields"], garbage
        assert not _is_plausible_address(garbage)


# ================================================================
# Test C -- a valid numbered address still works
# ================================================================

def test_C_valid_numbered_address_still_works():
    svc = new_service()
    session_id = "regress-C"

    process_user_message(session_id, "My name is Jane Smith.", svc)
    result = process_user_message(session_id, "12 Oxford Street", svc)

    assert result["state"].home_address == "12 Oxford Street"
    assert "home_address" in result["confirmed_fields"]


# ================================================================
# Test D -- a valid building/locality address (no number) works
# ================================================================

def test_D_valid_building_locality_address_works():
    svc = new_service()
    session_id = "regress-D"

    process_user_message(session_id, "My name is Jane Smith.", svc)
    result = process_user_message(
        session_id, "Gaur Heights Nikals Mandir Road Itwari Nagpur", svc
    )

    assert result["state"].home_address == (
        "Gaur Heights Nikals Mandir Road Itwari Nagpur"
    )
    assert "home_address" in result["confirmed_fields"]


# ================================================================
# Helper: drive a session up to (but not including) the executor
# questions, so "current_field" is deterministically executor_name /
# executor_relationship for the tests below.
# ================================================================

def _reach_executor_name(svc, session_id):
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


def _reach_executor_relationship(svc, session_id):
    _reach_executor_name(svc, session_id)
    process_user_message(session_id, "James", svc)


# ================================================================
# Test E -- wrong-field answer while executor_name is being asked
# ================================================================

def test_E_wrong_field_answer_for_executor_name():
    svc = new_service()
    session_id = "regress-E"

    _reach_executor_name(svc, session_id)
    result = process_user_message(
        session_id, "No specific gifts.", svc
    )

    assert result["state"].executor.name is None
    assert "executor_name" not in result["confirmed_fields"]
    assert "specific_gifts" not in result["confirmed_fields"]
    assert result["state"].specific_gifts == []
    assert "executor" in result["reply"].lower()
    assert "name" in result["reply"].lower()


# ================================================================
# Test F -- wrong-field answer while executor_relationship is asked
# ================================================================

def test_F_wrong_field_answer_for_executor_relationship():
    svc = new_service()
    session_id = "regress-F"

    _reach_executor_relationship(svc, session_id)
    result = process_user_message(
        session_id, "No additional wishes.", svc
    )

    assert result["state"].executor.relationship is None
    assert "executor_relationship" not in result["confirmed_fields"]
    assert "additional_wishes" not in result["confirmed_fields"]
    assert result["state"].additional_wishes == []
    assert "relationship" in result["reply"].lower()


# ================================================================
# Test G -- "No specific gifts." still works when gifts IS the
# field currently being asked (must not be broken by the Test E fix)
# ================================================================

def test_G_valid_no_gifts_still_works():
    svc = new_service()
    result = process_user_message(
        "regress-G", "No specific gifts.", svc
    )

    assert result["state"].specific_gifts == []
    assert "specific_gifts" in result["confirmed_fields"]


# ================================================================
# Test H -- "No additional wishes." still works when wishes IS the
# field currently being asked
# ================================================================

def test_H_valid_no_wishes_still_works():
    svc = new_service()
    result = process_user_message(
        "regress-H", "No additional wishes.", svc
    )

    assert result["state"].additional_wishes == []
    assert "additional_wishes" in result["confirmed_fields"]


# ================================================================
# Test I -- existing executor extraction is not regressed
# ================================================================

def test_I_existing_executor_extraction_still_correct():
    svc = new_service()
    session_id = "regress-I"

    _reach_executor_name(svc, session_id)
    result = process_user_message(
        session_id, "My brother James is my executor.", svc
    )

    assert result["state"].executor.name == "James"
    assert result["state"].executor.relationship == "brother"


# ================================================================
# Test J -- ambiguous children remains correct
# ================================================================

def test_J_ambiguous_children_remains_correct():
    svc = new_service()
    result = process_user_message(
        "regress-J", "Maybe I have children.", svc
    )

    assert result["state"].has_children is None
    assert "has_children" not in result["confirmed_fields"]


# ================================================================
# Test K -- correction remains correct
# ================================================================

def test_K_correction_remains_correct():
    svc = new_service()
    session_id = "regress-K"

    process_user_message(session_id, "My name is Jane Smith.", svc)
    result = process_user_message(
        session_id, "Actually, my name is Jane Brown.", svc
    )

    assert result["state"].full_name == "Jane Brown"


# ================================================================
# Test L -- genuine contradiction remains correct
# ================================================================

def test_L_genuine_contradiction_remains_correct():
    svc = new_service()
    session_id = "regress-L"

    process_user_message(session_id, "My name is Jane Smith.", svc)
    result = process_user_message(
        session_id, "My name is Alice Brown.", svc
    )

    assert result["state"].full_name == "Jane Smith"
    assert "Which is correct" in result["reply"]


# ================================================================
# Multi-field messages that legitimately mention gifts/wishes
# alongside real executor info must still extract everything
# (this must NOT be broken by the Test E / Test F fix).
# ================================================================

def test_multi_field_message_with_executor_and_gifts_still_works():
    svc = new_service()
    session_id = "regress-multi"

    _reach_executor_name(svc, session_id)
    result = process_user_message(
        session_id,
        "No specific gifts. My brother James is my executor.",
        svc
    )

    assert result["state"].executor.name == "James"
    assert result["state"].executor.relationship == "brother"
    assert result["state"].specific_gifts == []