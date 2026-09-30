from typing import Dict, Optional

from app.models.state import DocumentState
from app.models.api import ChatMessage


class SessionData:

    def __init__(self):
        self.state = DocumentState()
        self.messages: list[ChatMessage] = []
        self.confirmed_fields: set[str] = set()
        self.unknown_fields: set[str] = set()

        # The field name (matching the get_current_field /
        # mark_confirmed_fields vocabulary, e.g. "full_name",
        # "executor_name", "home_address") that a pending
        # contradiction clarification question refers to. When set,
        # the next user message is interpreted in the context of
        # this field so a short answer such as "Mahek" resolves the
        # clarification instead of being dropped. Cleared once the
        # field is actually updated.
        self.pending_clarification_field: Optional[str] = None


_sessions: Dict[str, SessionData] = {}


def get_session(session_id: str) -> SessionData:

    if session_id not in _sessions:
        _sessions[session_id] = SessionData()

    return _sessions[session_id]