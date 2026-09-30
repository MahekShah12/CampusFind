import pytest

from app.models.llm import LLMResponse
from app.services.validator import (
    validate_llm_response,
    LLMValidationError
)


def test_valid_llm_response():

    data = {
        "extracted": {
            "full_name": "Jane Smith",
            "home_address": None,
            "covers_worldwide_assets": None,
            "has_children": None,
            "children": [],
            "executor": None,
            "specific_gifts": [],
            "additional_wishes": []
        },
        "clarification_needed": False,
        "clarification_question": None,
        "detected_contradiction": False,
        "contradiction_explanation": None
    }

    result = validate_llm_response(data)

    assert isinstance(result, LLMResponse)
    assert result.extracted.full_name == "Jane Smith"


def test_malformed_llm_response():

    data = {
        "wrong_field": "invalid"
    }

    with pytest.raises(LLMValidationError):
        validate_llm_response(data)


def test_invalid_field_type():

    data = {
        "extracted": {
            "full_name": "Jane Smith",
            "home_address": None,
            "covers_worldwide_assets": "maybe",
            "has_children": None,
            "children": [],
            "executor": None,
            "specific_gifts": [],
            "additional_wishes": []
        }
    }

    with pytest.raises(LLMValidationError):
        validate_llm_response(data)