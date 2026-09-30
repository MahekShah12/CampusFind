from app.models.state import DocumentState


def test_empty_state():
    state = DocumentState()

    assert state.full_name is None
    assert state.home_address is None
    assert state.covers_worldwide_assets is None
    assert state.has_children is None
    assert state.children == []
    assert state.executor.name is None
    assert state.executor.relationship is None
    assert state.specific_gifts == []
    assert state.additional_wishes == []