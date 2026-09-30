from typing import Optional

from app.models.api import ChatMessage
from app.services.state_manager import update_state
from app.services.document_generator import generate_document
from app.services.llm_service import LLMService, LLMServiceError
from app.storage.session_storage import get_session


UNKNOWN_PHRASES = [
    "i don't know",
    "i do not know",
    "dont know",
    "not sure",
    "i'm not sure",
    "i am not sure",
    "unknown",
    "i don't have that information",
    "i do not have that information"
]


def is_unknown_response(message: str) -> bool:
    """
    Detect whether the user explicitly says
    that they do not know the requested information.
    """

    text = message.lower().strip()

    return any(
        phrase in text
        for phrase in UNKNOWN_PHRASES
    )


# NOTE: this is inferred purely from session.state /
# confirmed_fields / unknown_fields, which is sufficient for the
# supported scenarios (multiple fields per message, unknowns,
# corrections, contradictions, out-of-order answers). No separate
# session.current_field is needed because every field question is
# derived deterministically from the same three sources that are
# already part of SessionData.

def get_current_field(
    state,
    confirmed_fields: set[str],
    unknown_fields: set[str]
) -> str | None:
    """
    Determines which field the assistant is currently trying
    to collect.

    This prevents an unknown response from being repeatedly
    asked for the same field.
    """

    if (
        not state.full_name
        and "full_name" not in unknown_fields
    ):
        return "full_name"

    if (
        not state.home_address
        and "home_address" not in unknown_fields
    ):
        return "home_address"

    if (
        state.covers_worldwide_assets is None
        and "covers_worldwide_assets" not in unknown_fields
    ):
        return "covers_worldwide_assets"

    if (
        state.has_children is None
        and "has_children" not in unknown_fields
    ):
        return "has_children"

    if (
        state.has_children is True
        and not state.children
        and "children" not in unknown_fields
    ):
        return "children"

    if (
        not state.executor.name
        and "executor_name" not in unknown_fields
    ):
        return "executor_name"

    if (
        not state.executor.relationship
        and "executor_relationship" not in unknown_fields
    ):
        return "executor_relationship"

    if (
        "specific_gifts" not in confirmed_fields
        and "specific_gifts" not in unknown_fields
    ):
        return "specific_gifts"

    if (
        "additional_wishes" not in confirmed_fields
        and "additional_wishes" not in unknown_fields
    ):
        return "additional_wishes"

    return None


def get_next_question(
    state,
    confirmed_fields: set[str],
    unknown_fields: set[str]
) -> str | None:
    """
    Returns the next required question.

    Confirmed fields are not asked again.
    Unknown fields are skipped.
    """

    if (
        not state.full_name
        and "full_name" not in unknown_fields
    ):
        return "What is your full name?"

    if (
        not state.home_address
        and "home_address" not in unknown_fields
    ):
        return "What is your home address?"

    if (
        state.covers_worldwide_assets is None
        and "covers_worldwide_assets" not in unknown_fields
    ):
        return "Does this document cover your worldwide assets? Please answer yes or no."

    if (
        state.has_children is None
        and "has_children" not in unknown_fields
    ):
        return "Do you have any children? Please answer yes or no."

    if (
        state.has_children is True
        and not state.children
        and "children" not in unknown_fields
    ):
        return "What are the names of your children?"

    if (
        not state.executor.name
        and "executor_name" not in unknown_fields
    ):
        return "Who would you like to appoint as your executor?"

    if (
        not state.executor.relationship
        and "executor_relationship" not in unknown_fields
    ):
        return "What is your executor's relationship to you?"

    if (
        "specific_gifts" not in confirmed_fields
        and "specific_gifts" not in unknown_fields
    ):
        return (
            "Do you have any specific gifts you would like "
            "to include? If not, you can say no."
        )

    if (
        "additional_wishes" not in confirmed_fields
        and "additional_wishes" not in unknown_fields
    ):
        return (
            "Do you have any additional wishes you would "
            "like to include? If not, you can say no."
        )

    return None


# IMPORTANT: for the list fields (children, specific_gifts,
# additional_wishes) an explicitly-provided empty list ([]) must
# count as confirmed, just like a non-empty list. Only "not
# mentioned" (None) leaves the field alone. A bare `if extracted.x:`
# check would treat [] as falsy and incorrectly keep asking the
# question, so every field below is checked with `is not None`.

def mark_confirmed_fields(
    session,
    extracted
):
    """
    Tracks which fields have received confirmed information.

    This prevents the application from repeatedly asking for
    information that has already been successfully captured.
    """

    if extracted.full_name is not None:
        session.confirmed_fields.add("full_name")
        session.unknown_fields.discard("full_name")

    if extracted.home_address is not None:
        session.confirmed_fields.add("home_address")
        session.unknown_fields.discard("home_address")

    if extracted.covers_worldwide_assets is not None:
        session.confirmed_fields.add(
            "covers_worldwide_assets"
        )
        session.unknown_fields.discard(
            "covers_worldwide_assets"
        )

    if extracted.has_children is not None:
        session.confirmed_fields.add("has_children")
        session.unknown_fields.discard("has_children")

    if extracted.children is not None:
        session.confirmed_fields.add("children")
        session.unknown_fields.discard("children")

    if extracted.executor is not None:

        if extracted.executor.name is not None:
            session.confirmed_fields.add("executor_name")
            session.unknown_fields.discard("executor_name")

        if extracted.executor.relationship is not None:
            session.confirmed_fields.add(
                "executor_relationship"
            )
            session.unknown_fields.discard(
                "executor_relationship"
            )

    # These fields need an explicit is-not-None check because
    # "no gifts" / "no additional wishes" are valid, confirmed
    # answers represented as an empty list.

    if extracted.specific_gifts is not None:
        session.confirmed_fields.add("specific_gifts")
        session.unknown_fields.discard("specific_gifts")

    if extracted.additional_wishes is not None:
        session.confirmed_fields.add("additional_wishes")
        session.unknown_fields.discard("additional_wishes")


def _extracted_touches_field(extracted, field: Optional[str]) -> bool:
    """
    Whether the given LLM extraction result actually provided a new
    value for the named field (using the same field vocabulary as
    get_current_field / mark_confirmed_fields).
    """

    if not field:
        return False

    if field == "full_name":
        return extracted.full_name is not None

    if field == "home_address":
        return extracted.home_address is not None

    if field == "covers_worldwide_assets":
        return extracted.covers_worldwide_assets is not None

    if field == "has_children":
        return extracted.has_children is not None

    if field == "children":
        return extracted.children is not None

    if field == "executor_name":
        return (
            extracted.executor is not None
            and extracted.executor.name is not None
        )

    if field == "executor_relationship":
        return (
            extracted.executor is not None
            and extracted.executor.relationship is not None
        )

    if field == "specific_gifts":
        return extracted.specific_gifts is not None

    if field == "additional_wishes":
        return extracted.additional_wishes is not None

    return False


def is_intake_complete(session) -> bool:
    """
    Checks whether all required fields have either been
    confirmed or explicitly marked unknown.
    """

    required_fields = {
        "full_name",
        "home_address",
        "covers_worldwide_assets",
        "has_children",
        "executor_name",
        "executor_relationship",
        "specific_gifts",
        "additional_wishes"
    }

    completed_fields = (
        session.confirmed_fields
        | session.unknown_fields
    )

    # Children names are required only when user has children.
    if session.state.has_children is True:
        required_fields.add("children")

    return required_fields.issubset(completed_fields)


def process_user_message(
    session_id: str,
    message: str,
    llm_service: LLMService
):
    """
    Main application flow.

    Responsibilities:
    1. Store conversation history.
    2. Handle explicit unknown responses.
    3. Send user message to LLM service.
    4. Validate/handle clarification.
    5. Handle contradictions.
    6. Update structured state only after valid response.
    7. Track confirmed fields.
    8. Ask the next required question.
    9. Generate document preview.
    """

    session = get_session(session_id)

    current_field = get_current_field(
        session.state,
        session.confirmed_fields,
        session.unknown_fields
    )

    session.messages.append(
        ChatMessage(
            role="user",
            content=message
        )
    )

    if is_unknown_response(message) and current_field:

        session.unknown_fields.add(current_field)
        session.confirmed_fields.discard(current_field)

        next_question = get_next_question(
            session.state,
            session.confirmed_fields,
            session.unknown_fields
        )

        if next_question:

            reply = (
                "No problem. I'll mark that information as "
                "unknown for now and continue.\n\n"
                + next_question
            )

        else:

            reply = (
                "No problem. I'll mark that information as "
                "unknown for now. I have collected all the "
                "required information for the draft."
            )

        session.messages.append(
            ChatMessage(
                role="assistant",
                content=reply
            )
        )

        document = generate_document(
            session.state
        )

        return {
            "reply": reply,
            "state": session.state,
            "document": document,
            "messages": session.messages,
            "confirmed_fields": session.confirmed_fields,
            "unknown_fields": session.unknown_fields
        }

    effective_field = session.pending_clarification_field or current_field

    try:

        llm_response = llm_service.process_message(
            message=message,
            current_state=session.state.model_dump(),
            conversation_history=[
                msg.model_dump()
                for msg in session.messages
            ],
            current_field=effective_field
        )

    except LLMServiceError:

        # Graceful handling of known LLM/provider failures.
        # The real cause was already logged inside the service;
        # only a safe, generic message reaches the user.
        reply = (
            "I'm sorry, but I couldn't process that response "
            "right now. Please try again."
        )

        session.messages.append(
            ChatMessage(
                role="assistant",
                content=reply
            )
        )

        document = generate_document(
            session.state
        )

        return {
            "reply": reply,
            "state": session.state,
            "document": document,
            "messages": session.messages,
            "confirmed_fields": session.confirmed_fields,
            "unknown_fields": session.unknown_fields
        }

    except Exception:

        # Any other unexpected failure is handled the same safe
        # way; state is never touched.
        reply = (
            "I'm sorry, but I couldn't process that response "
            "right now. Please try again."
        )

        session.messages.append(
            ChatMessage(
                role="assistant",
                content=reply
            )
        )

        document = generate_document(
            session.state
        )

        return {
            "reply": reply,
            "state": session.state,
            "document": document,
            "messages": session.messages,
            "confirmed_fields": session.confirmed_fields,
            "unknown_fields": session.unknown_fields
        }

    # State is intentionally left untouched: no update_state()
    # call happens on this path.

    if llm_response.clarification_needed:

        reply = (
            llm_response.clarification_question
            or (
                "I'm not completely sure I understood that. "
                "Could you please clarify?"
            )
        )

    # State is intentionally left untouched until the user
    # clarifies which value is correct.

    elif llm_response.detected_contradiction:

        session.pending_clarification_field = (
            llm_response.contradiction_field or effective_field
        )

        reply = (
            llm_response.contradiction_explanation
            or (
                "There seems to be a contradiction with "
                "information provided earlier. "
                "Could you please clarify?"
            )
        )

    else:

        # IMPORTANT:
        # Update structured state ONLY after the LLM response
        # has passed validation inside the LLM service.

        session.state = update_state(
            session.state,
            llm_response.extracted
        )

        mark_confirmed_fields(
            session,
            llm_response.extracted
        )

        if (
            session.pending_clarification_field
            and _extracted_touches_field(
                llm_response.extracted,
                session.pending_clarification_field
            )
        ):
            session.pending_clarification_field = None

        next_question = get_next_question(
            session.state,
            session.confirmed_fields,
            session.unknown_fields
        )

        if next_question:

            reply = next_question

        else:

            reply = (
                "Thank you. I have collected all the "
                "required information for your draft."
            )

    session.messages.append(
        ChatMessage(
            role="assistant",
            content=reply
        )
    )

    document = generate_document(
        session.state
    )

    return {
        "reply": reply,
        "state": session.state,
        "document": document,
        "messages": session.messages,
        "confirmed_fields": session.confirmed_fields,
        "unknown_fields": session.unknown_fields
    }