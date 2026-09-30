from app.services.conversation import process_user_message
from app.services.llm_service import MockLLMService


def new_service():
    return MockLLMService()


def _complete_intake(svc, session_id, name="Jane Smith"):
    process_user_message(session_id, f"My name is {name}.", svc)
    process_user_message(session_id, "12 Oxford Street", svc)
    process_user_message(session_id, "yes", svc)
    process_user_message(session_id, "no", svc)
    process_user_message(session_id, "James", svc)
    process_user_message(session_id, "brother", svc)
    process_user_message(session_id, "no gifts", svc)
    return process_user_message(session_id, "no wishes", svc)


def test_name_with_trailing_change_it_extracts_only_the_name():
    svc = new_service()
    result = process_user_message(
        "group1-change-it", "My name is Jane, change it.", svc
    )

    assert result["state"].full_name == "Jane"
    assert result["state"].full_name != "Jane Change It"


def test_name_is_jane_plain():
    svc = new_service()
    result = process_user_message(
        "group1-plain", "My name is Jane.", svc
    )
    assert result["state"].full_name == "Jane"


def test_actually_my_name_is_jane():
    svc = new_service()
    result = process_user_message(
        "group1-actually", "Actually, my name is Jane.", svc
    )
    assert result["state"].full_name == "Jane"


def test_my_full_name_is_jane():
    svc = new_service()
    result = process_user_message(
        "group1-full-name", "My full name is Jane.", svc
    )
    assert result["state"].full_name == "Jane"


def test_bare_name_is_jane():
    svc = new_service()
    result = process_user_message(
        "group1-bare", "Name is Jane.", svc
    )
    assert result["state"].full_name == "Jane"


def test_jane_is_my_name():
    svc = new_service()
    result = process_user_message(
        "group1-is-my-name", "Jane is my name.", svc
    )
    assert result["state"].full_name == "Jane"


def test_name_while_wishes_is_current_field_updates_name_not_wishes():
    svc = new_service()
    session_id = "group2-name-vs-wishes"

    process_user_message(session_id, "unknown", svc)
    process_user_message(session_id, "12 Oxford Street", svc)
    process_user_message(session_id, "yes", svc)
    process_user_message(session_id, "no", svc)
    process_user_message(session_id, "James", svc)
    process_user_message(session_id, "brother", svc)
    process_user_message(session_id, "no gifts", svc)

    result = process_user_message(
        session_id, "My name is Jane.", svc
    )

    assert result["state"].full_name == "Jane"
    assert result["state"].additional_wishes == []
    assert "additional_wishes" not in result["confirmed_fields"]


def test_correction_after_completion_updates_name_and_document():
    svc = new_service()
    session_id = "group3-correction-name"

    completed = _complete_intake(svc, session_id, name="Jane Smith")
    assert "Thank you" in completed["reply"]

    result = process_user_message(
        session_id, "Actually, my name is Jane.", svc
    )

    assert result["state"].full_name == "Jane"
    assert "Jane" in result["document"]
    assert "Jane Smith" not in result["document"]


def test_correction_after_completion_updates_executor():
    svc = new_service()
    session_id = "group3-correction-executor"

    _complete_intake(svc, session_id, name="Anna Lee")

    result = process_user_message(
        session_id, "Actually, my executor is Michael.", svc
    )

    assert result["state"].executor.name == "Michael"
    assert "Michael" in result["document"]


def test_correction_after_completion_updates_address():
    svc = new_service()
    session_id = "group3-correction-address"

    _complete_intake(svc, session_id, name="Anna Lee")

    result = process_user_message(
        session_id,
        "Actually, my address is 45 Baker Street.",
        svc
    )

    assert result["state"].home_address == "45 Baker Street"
    assert "45 Baker Street" in result["document"]


def test_new_wish_after_completion_is_recorded_and_in_document():
    svc = new_service()
    session_id = "group4-new-wish"

    completed = _complete_intake(svc, session_id, name="Anna Lee")
    assert "Thank you" in completed["reply"]

    result = process_user_message(
        session_id, "I like playing cricket.", svc
    )

    assert result["state"].additional_wishes == ["I like playing cricket"]
    assert "I like playing cricket" in result["document"]


def test_existing_gift_plus_no_gifts_is_contradiction_not_overwrite():
    svc = new_service()
    session_id = "group5-gift-contradiction"

    process_user_message(session_id, "My name is Anna Lee.", svc)
    process_user_message(session_id, "12 Oxford Street", svc)
    process_user_message(session_id, "yes", svc)
    process_user_message(session_id, "no", svc)
    process_user_message(session_id, "James", svc)
    process_user_message(session_id, "brother", svc)

    with_gift = process_user_message(
        session_id, "leave my watch to Sarah", svc
    )
    assert with_gift["state"].specific_gifts == ["Watch to Sarah"]

    result = process_user_message(
        session_id, "I don't have any specific gifts.", svc
    )

    assert "which is correct" in result["reply"].lower()
    assert result["state"].specific_gifts == ["Watch to Sarah"]
    assert "Watch to Sarah" in result["document"]


def test_explicit_no_gifts_with_no_prior_gift_is_confirmed_empty():
    svc = new_service()
    result = process_user_message(
        "group6-no-gifts", "I don't have any specific gifts.", svc
    )

    assert result["state"].specific_gifts == []
    assert "specific_gifts" in result["confirmed_fields"]


def test_explicit_no_wishes_with_no_prior_wish_is_confirmed_empty():
    svc = new_service()
    session_id = "group7-no-wishes-then-add"

    result = process_user_message(
        session_id, "I don't have any additional wishes.", svc
    )
    assert result["state"].additional_wishes == []
    assert "additional_wishes" in result["confirmed_fields"]

    result2 = process_user_message(
        session_id,
        "I want to add that I like playing cricket.",
        svc
    )
    assert result2["state"].additional_wishes == ["I like playing cricket"]


def test_existing_wish_plus_no_wishes_is_contradiction_not_overwrite():
    svc = new_service()
    session_id = "group7-wish-contradiction"

    process_user_message(session_id, "My name is Anna Lee.", svc)
    process_user_message(session_id, "12 Oxford Street", svc)
    process_user_message(session_id, "yes", svc)
    process_user_message(session_id, "no", svc)
    process_user_message(session_id, "James", svc)
    process_user_message(session_id, "brother", svc)
    process_user_message(session_id, "no gifts", svc)

    with_wish = process_user_message(
        session_id, "I want to plant a tree in my memory.", svc
    )
    assert with_wish["state"].additional_wishes == [
        "I want to plant a tree in my memory"
    ]

    result = process_user_message(
        session_id, "I don't have any additional wishes.", svc
    )

    assert "which is correct" in result["reply"].lower()
    assert result["state"].additional_wishes == [
        "I want to plant a tree in my memory"
    ]
    assert "I want to plant a tree in my memory" in result["document"]


def test_name_is_eve():
    svc = new_service()
    result = process_user_message("group8-name-is-eve", "Name is Eve", svc)
    assert result["state"].full_name == "Eve"


def test_eve_is_my_name_not_executor():
    svc = new_service()
    result = process_user_message(
        "group8-eve-is-my-name", "Eve is my name", svc
    )
    assert result["state"].full_name == "Eve"
    assert result["state"].executor.name is None
    assert result["state"].executor.relationship is None


def test_my_full_name_is_eve():
    svc = new_service()
    result = process_user_message(
        "group8-full-name-eve", "My full name is Eve", svc
    )
    assert result["state"].full_name == "Eve"


def test_james_is_my_executor_no_invented_relationship():
    svc = new_service()
    result = process_user_message(
        "group8-james-executor", "James is my executor", svc
    )
    assert result["state"].executor.name == "James"
    assert result["state"].executor.relationship is None


def test_james_will_be_my_executor_no_invented_relationship():
    svc = new_service()
    result = process_user_message(
        "group8-james-will-be-executor",
        "James will be my executor",
        svc
    )
    assert result["state"].executor.name == "James"
    assert result["state"].executor.relationship is None


def test_my_brother_james_is_my_executor():
    svc = new_service()
    result = process_user_message(
        "group8-brother-james", "My brother James is my executor", svc
    )
    assert result["state"].executor.name == "James"
    assert result["state"].executor.relationship == "brother"


def test_gift_correction_strips_instead():
    svc = new_service()
    session_id = "group8-gift-correction"

    process_user_message(
        session_id, "I want to leave my watch to Sarah.", svc
    )
    result = process_user_message(
        session_id,
        "Actually, leave my watch to Sarah instead.",
        svc
    )

    assert result["state"].specific_gifts == ["Watch to Sarah"]