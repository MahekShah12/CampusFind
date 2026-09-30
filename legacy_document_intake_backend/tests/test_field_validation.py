"""
Regression tests for the manual-testing fixes:

- Executor relationship extraction ("My brother James is my
  executor." must not record "executor" itself as the relationship).
- Field-aware plausibility checks for full_name and home_address
  (reject obvious garbage, accept realistic short answers).
- The six end-to-end scenarios from the manual test report.
"""

from app.services.conversation import process_user_message
from app.services.llm_service import MockLLMService, _is_plausible_address


def new_service():
    return MockLLMService()


# ================================================================
# Problem A — executor relationship extraction
# ================================================================

def test_executor_relationship_brother_is_not_the_word_executor():
    svc = new_service()
    result = process_user_message(
        "exec-rel-1", "My brother James is my executor.", svc
    )

    assert result["state"].executor.name == "James"
    assert result["state"].executor.relationship == "brother"


def test_executor_relationship_sister():
    svc = new_service()
    result = process_user_message(
        "exec-rel-2", "My sister Sarah is my executor.", svc
    )

    assert result["state"].executor.name == "Sarah"
    assert result["state"].executor.relationship == "sister"


def test_executor_relationship_father_will_be():
    svc = new_service()
    result = process_user_message(
        "exec-rel-3", "My father John will be my executor.", svc
    )

    assert result["state"].executor.name == "John"
    assert result["state"].executor.relationship == "father"


def test_executor_relationship_mother():
    svc = new_service()
    result = process_user_message(
        "exec-rel-4", "My mother Priya is my executor.", svc
    )

    assert result["state"].executor.name == "Priya"
    assert result["state"].executor.relationship == "mother"


def test_existing_generic_executor_pattern_still_works():
    svc = new_service()
    result = process_user_message(
        "exec-rel-5", "James is my brother.", svc
    )

    assert result["state"].executor.name == "James"
    assert result["state"].executor.relationship == "brother"


def test_short_executor_name_and_relationship_are_field_aware():
    svc = new_service()
    session_id = "exec-rel-6"

    process_user_message(session_id, "My name is Jane Smith.", svc)
    process_user_message(
        session_id, "I live at 12 Oxford Street.", svc
    )
    process_user_message(session_id, "Yes.", svc)
    process_user_message(session_id, "No.", svc)

    process_user_message(session_id, "dychyg", svc)
    result = process_user_message(session_id, "mom", svc)

    assert result["state"].executor.name == "Dychyg"
    assert result["state"].executor.relationship == "mom"


# ================================================================
# Problem C (Test 2) — address plausibility
# ================================================================

def test_address_plausibility_accepts_realistic_addresses():
    for address in [
        "12 Oxford Street",
        "42 MG Road, Nagpur",
        "123 Main Street",
        "Flat 4, 21 Park Avenue",
        "12 Gandhi Nagar, Nagpur",
    ]:
        assert _is_plausible_address(address), address


def test_address_plausibility_rejects_garbage():
    for garbage in ["xyz", "abc", "qwerty", "hbblbjvcxdtex cuc"]:
        assert not _is_plausible_address(garbage), garbage


def test_unknown_then_invalid_then_valid_address():
    svc = new_service()
    session_id = "addr-flow-1"

    r1 = process_user_message(session_id, "I don't know", svc)
    assert "full_name" in r1["unknown_fields"]

    r2 = process_user_message(session_id, "xyz", svc)
    assert r2["state"].home_address is None
    assert "home_address" not in r2["confirmed_fields"]

    r3 = process_user_message(
        session_id, "hbblbjvcxdtex cuc", svc
    )
    assert r3["state"].home_address is None
    assert "home_address" not in r3["confirmed_fields"]

    r4 = process_user_message(
        session_id, "12 Oxford Street", svc
    )
    assert r4["state"].home_address == "12 Oxford Street"
    assert "home_address" in r4["confirmed_fields"]


# ================================================================
# Full-name plausibility (bare answer on the very first turn)
# ================================================================

def test_bare_plausible_name_accepted_on_first_turn():
    svc = new_service()
    result = process_user_message("name-flow-1", "John", svc)
    assert result["state"].full_name == "John"


def test_bare_multiword_plausible_name_accepted_on_first_turn():
    svc = new_service()
    result = process_user_message("name-flow-2", "Jane Smith", svc)
    assert result["state"].full_name == "Jane Smith"


def test_bare_implausible_name_rejected_on_first_turn():
    svc = new_service()
    result = process_user_message("name-flow-3", "xyz", svc)
    assert result["state"].full_name is None


def test_yes_no_answer_is_not_mistaken_for_a_name_on_first_turn():
    """
    A message that clearly matches another field (e.g. children
    yes/no phrasing) must not be misread as a name just because
    full_name happens to be the field currently being collected.
    """
    svc = new_service()
    result = process_user_message(
        "name-flow-4", "I have no children.", svc
    )
    assert result["state"].full_name is None
    assert result["state"].has_children is False


# ================================================================
# End-to-end scenarios from the manual test report
# ================================================================

def test_scenario_1_full_flow_then_correction():
    svc = new_service()
    session_id = "scenario-1"

    steps = [
        "My name is Jane Smith and I live at 12 Oxford Street.",
        "Yes, it covers my worldwide assets and I have no children.",
        "My brother James is my executor.",
        "I want to leave my watch to Alice.",
        "I want my funeral to be private.",
    ]
    for step in steps:
        process_user_message(session_id, step, svc)

    result = process_user_message(
        session_id, "Actually, my name is Jane Brown.", svc
    )
    state = result["state"]

    assert state.full_name == "Jane Brown"
    assert state.home_address == "12 Oxford Street"
    assert state.covers_worldwide_assets is True
    assert state.has_children is False
    assert state.executor.name == "James"
    assert state.executor.relationship == "brother"
    assert state.specific_gifts
    assert state.additional_wishes

    for field in (
        "full_name", "home_address", "covers_worldwide_assets",
        "has_children", "executor_name", "executor_relationship",
        "specific_gifts", "additional_wishes"
    ):
        assert field in result["confirmed_fields"], field


def test_scenario_3_ambiguous_children():
    svc = new_service()
    result = process_user_message(
        "scenario-3", "Maybe I have children.", svc
    )
    assert result["state"].has_children is None
    assert "children" not in result["confirmed_fields"]


def test_scenario_4_explicit_no_gifts():
    svc = new_service()
    result = process_user_message(
        "scenario-4", "No specific gifts.", svc
    )
    assert result["state"].specific_gifts == []
    assert "specific_gifts" in result["confirmed_fields"]


def test_scenario_5_explicit_no_additional_wishes():
    svc = new_service()
    result = process_user_message(
        "scenario-5", "No additional wishes.", svc
    )
    assert result["state"].additional_wishes == []
    assert "additional_wishes" in result["confirmed_fields"]


def test_scenario_6_actual_contradiction_without_correction_wording():
    svc = new_service()
    session_id = "scenario-6"

    process_user_message(session_id, "My name is Jane Smith.", svc)
    result = process_user_message(
        session_id, "My name is Alice Brown.", svc
    )

    assert result["state"].full_name == "Jane Smith"