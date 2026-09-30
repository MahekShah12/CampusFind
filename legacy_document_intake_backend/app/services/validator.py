from pydantic import ValidationError

from app.models.llm import LLMResponse


class LLMValidationError(Exception):
    pass


def validate_llm_response(
    data: dict
) -> LLMResponse:

    try:

        return LLMResponse.model_validate(data)

    except ValidationError as exc:

        raise LLMValidationError(
            f"Invalid LLM response: {exc}"
        ) from exc