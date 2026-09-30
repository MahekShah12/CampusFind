"""
create_llm_service() must select the provider from configuration
and must never require a Groq API key when LLM_PROVIDER=mock.
"""

import pytest

from app.services.llm_service import (
    create_llm_service,
    MockLLMService,
    GroqLLMService,
)


def test_mock_provider_requires_no_api_key():
    service = create_llm_service("mock")
    assert isinstance(service, MockLLMService)


def test_default_provider_is_mock(monkeypatch):
    monkeypatch.setattr(
        "app.services.llm_service.config.LLM_PROVIDER", "mock"
    )
    service = create_llm_service()
    assert isinstance(service, MockLLMService)


def test_groq_provider_is_selectable_without_live_key():
    # Construction must succeed even with an empty key; only calling
    # process_message() should fail (see test_groq_service.py).
    service = create_llm_service("groq")
    assert isinstance(service, GroqLLMService)


def test_unknown_provider_raises():
    with pytest.raises(ValueError):
        create_llm_service("not-a-real-provider")