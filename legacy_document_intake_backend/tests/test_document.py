from app.models.state import DocumentState, Executor
from app.services.document_generator import generate_document


def test_document_contains_state():

    state = DocumentState(
        full_name="Jane Smith",
        home_address="12 Oxford Street",
        covers_worldwide_assets=True,
        has_children=False,
        executor=Executor(
            name="James",
            relationship="brother"
        )
    )

    document = generate_document(state)

    assert "Jane Smith" in document
    assert "12 Oxford Street" in document
    assert "James" in document
    assert "brother" in document


def test_document_contains_disclaimer():

    state = DocumentState()

    document = generate_document(state)

    assert "FICTIONAL DOCUMENT" in document
    assert "NOT LEGAL ADVICE" in document