from typing import Optional, List
from pydantic import BaseModel


class ExtractedExecutor(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None


class ExtractedInformation(BaseModel):
    full_name: Optional[str] = None
    home_address: Optional[str] = None

    covers_worldwide_assets: Optional[bool] = None

    has_children: Optional[bool] = None

    # For the three list fields below:
    #   None            -> not mentioned in the user's message
    #   []              -> the user explicitly said there are none
    #   ["a", "b", ...] -> the values the user provided
    children: Optional[List[str]] = None

    executor: Optional[ExtractedExecutor] = None

    specific_gifts: Optional[List[str]] = None

    additional_wishes: Optional[List[str]] = None


class LLMResponse(BaseModel):
    extracted: ExtractedInformation

    clarification_needed: bool = False

    clarification_question: Optional[str] = None

    detected_contradiction: bool = False

    contradiction_explanation: Optional[str] = None

    contradiction_field: Optional[str] = None