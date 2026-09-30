from app.models.llm import (
    LLMResponse,
    ExtractedInformation,
    ExtractedExecutor
)
from app.models.state import DocumentState
from app.services.state_manager import update_state


def test_state_update():

    state = DocumentState()

    extracted = ExtractedInformation(
        full_name="Jane Smith",
        home_address="12 Oxford Street",
        covers_worldwide_assets=True,
        has_children=False,
        executor=ExtractedExecutor(
            name="James",
            relationship="brother"
        )
    )

    updated = update_state(
        state,
        extracted
    )

    assert updated.full_name == "Jane Smith"
    assert updated.home_address == "12 Oxford Street"
    assert updated.covers_worldwide_assets is True
    assert updated.has_children is False
    assert updated.executor.name == "James"
    assert updated.executor.relationship == "brother"