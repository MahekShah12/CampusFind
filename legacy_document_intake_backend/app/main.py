from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.api import ChatRequest, ChatResponse
from app.services.conversation import process_user_message
from app.services.llm_service import create_llm_service


app = FastAPI(
    title="Document Intake Assistant",
    version="1.0.0"
)

# Allows the standalone frontend/index.html (opened directly, or
# served from a different origin/port) to call this API locally.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Selected via LLM_PROVIDER in .env ("mock" by default, "groq" once
# a real GROQ_API_KEY is provided). See app/config.py.
llm_service = create_llm_service()


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    result = process_user_message(
        session_id=request.session_id,
        message=request.message,
        llm_service=llm_service
    )

    return ChatResponse(
        session_id=request.session_id,
        reply=result["reply"],
        state=result["state"],
        document=result["document"],
        messages=result["messages"],
        confirmed_fields=sorted(result["confirmed_fields"]),
        unknown_fields=sorted(result["unknown_fields"])
    )