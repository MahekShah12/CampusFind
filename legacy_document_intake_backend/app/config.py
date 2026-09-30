import os

from dotenv import load_dotenv

load_dotenv()


# Which LLM implementation to use: "mock" (default, no API key needed)
# or "groq" (requires GROQ_API_KEY).
LLM_PROVIDER = (os.getenv("LLM_PROVIDER") or "mock").strip().lower()

# Intentionally blank by default. Never hard-code a key here.
GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()

GROQ_MODEL = (
    os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile"
).strip()