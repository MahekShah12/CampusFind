from typing import List, Optional

from app.models.state import DocumentState
from app.models.llm import ExtractedInformation


def _clean_text(value: Optional[str]) -> Optional[str]:
    """Blank strings are treated as 'not provided'."""

    if value is None:
        return None

    value = value.strip()

    return value or None


def _clean_list(values: Optional[List[str]]) -> Optional[List[str]]:
    """
    None stays None (not mentioned).
    [] stays [] (explicitly empty).
    Blank items are dropped.
    """

    if values is None:
        return None

    return [
        item.strip()
        for item in values
        if item and item.strip()
    ]


def update_state(
    state: DocumentState,
    extracted: ExtractedInformation
) -> DocumentState:
    """
    Returns the updated state.

    The update is applied to a deep copy, so the caller's state is
    never left half-modified if something goes wrong.

    List fields:
        None -> not supplied, keep the current value
        []   -> explicitly empty, replace the current value
        [..] -> replace with the supplied values
    """

    new_state = state.model_copy(deep=True)

    full_name = _clean_text(extracted.full_name)
    if full_name is not None:
        new_state.full_name = full_name

    home_address = _clean_text(extracted.home_address)
    if home_address is not None:
        new_state.home_address = home_address

    if extracted.covers_worldwide_assets is not None:
        new_state.covers_worldwide_assets = (
            extracted.covers_worldwide_assets
        )

    if extracted.has_children is not None:
        new_state.has_children = extracted.has_children

        # "I have no children" also clears any children recorded
        # earlier, unless children were supplied in the same update.
        if (
            extracted.has_children is False
            and extracted.children is None
        ):
            new_state.children = []

    children = _clean_list(extracted.children)
    if children is not None:
        new_state.children = children

    if extracted.executor is not None:

        executor_name = _clean_text(extracted.executor.name)
        if executor_name is not None:
            new_state.executor.name = executor_name

        executor_relationship = _clean_text(
            extracted.executor.relationship
        )
        if executor_relationship is not None:
            new_state.executor.relationship = executor_relationship

    specific_gifts = _clean_list(extracted.specific_gifts)
    if specific_gifts is not None:
        new_state.specific_gifts = specific_gifts

    additional_wishes = _clean_list(extracted.additional_wishes)
    if additional_wishes is not None:
        new_state.additional_wishes = additional_wishes

    return new_state