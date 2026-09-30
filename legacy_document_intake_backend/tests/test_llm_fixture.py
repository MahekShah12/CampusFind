
import json
from pathlib import Path

import pytest

from app.models.llm import LLMResponse
from app.services.validator import (
    validate_llm_response,
    LLMValidationError
)


FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(filename: str) -> dict:
    with open(
        FIXTURES / filename,
        encoding="utf-8"
    ) as file:
        return json.load(file)


def test_valid_llm_fixture():

    data = load_fixture(
        "valid_llm_response.json"
    )

    response = validate_llm_response(data)

    assert isinstance(
        response,
        LLMResponse
    )

    assert response.extracted.full_name == (
        "Jane Smith"
    )

    assert response.extracted.home_address == (
        "12 Oxford Street, London"
    )


def test_ambiguous_llm_fixture():

    data = load_fixture(
        "ambiguous_llm_response.json"
    )

    response = validate_llm_response(data)

    assert response.clarification_needed is True

    assert response.clarification_question is not None

    assert "children" in (
        response.clarification_question.lower()
    )


def test_malformed_llm_fixture():

    data = load_fixture(
        "malformed_llm_response.json"
    )

    with pytest.raises(LLMValidationError):

        validate_llm_response(data)
