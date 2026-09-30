from typing import List
from pydantic import BaseModel, Field

from app.models.state import DocumentState


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    state: DocumentState
    document: str
    messages: List[ChatMessage]

    # Additive fields (they default to empty lists) so the UI can show
    # confirmed / unknown / not answered. Everything else in the
    # response is unchanged.
    confirmed_fields: List[str] = Field(default_factory=list)
    unknown_fields: List[str] = Field(default_factory=list)