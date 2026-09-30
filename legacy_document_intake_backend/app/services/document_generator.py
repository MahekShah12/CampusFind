from app.models.state import DocumentState


def generate_document(state: DocumentState) -> str:
    children = (
        ", ".join(state.children)
        if state.children
        else "Not applicable"
        if state.has_children is False
        else "Not provided"
    )

    gifts = (
        "\n".join(f"- {gift}" for gift in state.specific_gifts)
        if state.specific_gifts
        else "None provided"
    )

    wishes = (
        "\n".join(f"- {wish}" for wish in state.additional_wishes)
        if state.additional_wishes
        else "None provided"
    )

    worldwide = (
        "Yes"
        if state.covers_worldwide_assets is True
        else "No"
        if state.covers_worldwide_assets is False
        else "Not confirmed"
    )

    children_status = (
        "Yes"
        if state.has_children is True
        else "No"
        if state.has_children is False
        else "Not confirmed"
    )

    return f"""
PERSONAL WISHES DOCUMENT

FICTIONAL DOCUMENT — NOT LEGAL ADVICE

----------------------------------------

Full Name:
{state.full_name or "Not provided"}

Home Address:
{state.home_address or "Not provided"}

Covers Worldwide Assets:
{worldwide}

Has Children:
{children_status}

Children:
{children}

Executor:
{state.executor.name or "Not provided"}

Executor Relationship:
{state.executor.relationship or "Not provided"}

Specific Gifts:
{gifts}

Additional Wishes:
{wishes}

----------------------------------------

This is a fictional draft generated from the
information provided during the conversation.
It is not legal advice or a legally valid document.
""".strip()