"""
GroqLLMService tests using a fake Groq client (no network, no real
API key). These verify the error handling required by the
assignment: missing key, provider/network failure, empty response,
malformed JSON, and invalid structured output must never crash the
app and must never leak internals to the caller.

These do NOT hit the real Groq API. Live Groq mode was not tested
because no API key was provided (see AI_LOG.md).
"""

import pytest

from app.services.llm_service import (
    GroqLLMService,
    LLMConfigurationError,
    LLMProviderError,
    LLMResponseError,
)
from app.services.validator import LLMValidationError


class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeCompletionResponse:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]


class FakeCompletions:
    def __init__(self, content=None, exc=None):
        self._content = content
        self._exc = exc

    def create(self, **kwargs):
        if self._exc:
            raise self._exc
        return FakeCompletionResponse(self._content)


class FakeChat:
    def __init__(self, completions):
        self.completions = completions


class FakeGroqClient:
    def __init__(self, content=None, exc=None):
        self.chat = FakeChat(FakeCompletions(content=content, exc=exc))


VALID_JSON = """
{
  "extracted": {
    "full_name": "Jane Smith",
    "home_address": null,
    "covers_worldwide_assets": null,
    "has_children": null,
    "children": null,
    "executor": null,
    "specific_gifts": null,
    "additional_wishes": null
  },
  "clarification_needed": false,
  "clarification_question": null,
  "detected_contradiction": false,
  "contradiction_explanation": null
}
"""


def test_missing_api_key_raises_configuration_error():
    service = GroqLLMService(api_key="")

    with pytest.raises(LLMConfigurationError):
        service.process_message(
            message="hello", current_state={}, conversation_history=[]
        )


def test_valid_response_is_parsed_and_validated():
    service = GroqLLMService(
        api_key="fake-key",
        client=FakeGroqClient(content=VALID_JSON)
    )

    result = service.process_message(
        message="My name is Jane Smith.",
        current_state={},
        conversation_history=[]
    )

    assert result.extracted.full_name == "Jane Smith"


def test_network_error_is_wrapped_and_safe():
    service = GroqLLMService(
        api_key="fake-key",
        client=FakeGroqClient(exc=ConnectionError("network down"))
    )

    with pytest.raises(LLMProviderError) as exc_info:
        service.process_message(
            message="hello", current_state={}, conversation_history=[]
        )

    # No internals/stack traces leak into the exception message.
    assert "network down" not in str(exc_info.value)


def test_empty_response_raises_response_error():
    service = GroqLLMService(
        api_key="fake-key",
        client=FakeGroqClient(content="")
    )

    with pytest.raises(LLMResponseError):
        service.process_message(
            message="hello", current_state={}, conversation_history=[]
        )


def test_malformed_json_raises_response_error_and_state_unaffected():
    service = GroqLLMService(
        api_key="fake-key",
        client=FakeGroqClient(content="not valid JSON")
    )

    with pytest.raises(LLMResponseError):
        service.process_message(
            message="hello", current_state={}, conversation_history=[]
        )


def test_invalid_structured_output_raises_validation_error():
    service = GroqLLMService(
        api_key="fake-key",
        client=FakeGroqClient(content='{"wrong_field": "invalid"}')
    )

    with pytest.raises(LLMValidationError):
        service.process_message(
            message="hello", current_state={}, conversation_history=[]
        )


def test_api_key_never_appears_in_provider_error():
    service = GroqLLMService(
        api_key="super-secret-key",
        client=FakeGroqClient(
            exc=RuntimeError("auth failed for super-secret-key")
        )
    )

    with pytest.raises(LLMProviderError) as exc_info:
        service.process_message(
            message="hello", current_state={}, conversation_history=[]
        )

    assert "super-secret-key" not in str(exc_info.value)