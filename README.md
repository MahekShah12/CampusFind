# Document Intake Assistant

A small conversational web application that collects information for a fictional Personal Wishes Document, maintains structured session state, and generates a live draft document.

This project was developed as part of the Wenup Engineering Candidate Technical Test.

> **Important:** This is a fictional document-generation application and is **not legal advice** and should not be used to create a real legal document.

---

## 1. Project Overview

The Document Intake Assistant conducts a multi-turn conversational interview and collects:

* Full name
* Home address
* Whether the document covers worldwide assets
* Whether the user has children
* Names of children, when applicable
* Executor name
* Executor relationship
* Specific gifts
* Additional wishes

The application maintains an explicit structured state rather than relying on conversation history as the source of truth.

The structured state and generated Personal Wishes Document are updated as information is confirmed.

---

## 2. Architecture

```text
                    User
                      |
                      v
              Frontend UI
             HTML / CSS / JS
                      |
                      v
                FastAPI API
                      |
                      v
             Conversation Service
                      |
              +-------+-------+
              |               |
              v               v
          LLM Service     State Manager
              |               |
       +------+-------+       |
       |              |       |
       v              v       v
   Mock LLM        Groq LLM  Session State
                              |
                    +---------+---------+
                    |                   |
                    v                   v
             State Preview       Document Generator
                                        |
                                        v
                                Draft Document
```

### Source of Truth

The structured session state is the application's source of truth.

Conversation history is used as context, but it is not used as the authoritative state.

LLM output is validated before it is applied to the structured state.

---

## 3. Tech Stack

### Backend

* Python
* FastAPI
* Pydantic
* Pytest

### LLM

* Deterministic Mock LLM for local/default execution
* Groq LLM integration through a separate LLM service

### Frontend

* HTML
* CSS
* JavaScript

No frontend framework or build step is required.

---

## 4. Project Structure

```text
Document Intake Assistant/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── services/
│   │   ├── storage/
│   │   ├── config.py
│   │   └── main.py
│   │
│   ├── tests/
│   │   ├── fixtures/
│   │   └── test_*.py
│   │
│   ├── .env.example
│   ├── .gitignore
│   ├── pytest.ini
│   └── requirements.txt
│
├── frontend/
│   └── index.html
│
├── README.md
├── AI_LOG.md
└── .gitignore
```

---

## 5. Prerequisites

* Python 3.11+ recommended
* Git
* A modern web browser

A Groq API key is optional because the application includes a deterministic Mock LLM.

---

## 6. Backend Setup

Open a terminal in the project directory:

```bash
cd backend
```

Create and activate a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 7. Environment Configuration

Create:

```text
backend/.env
```

For default local execution using the deterministic Mock LLM:

```env
LLM_PROVIDER=mock
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
```

The `.env` file is intentionally not included in source control.

An example configuration is provided in:

```text
backend/.env.example
```

### Using Groq

If a Groq API key is available:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=YOUR_API_KEY
GROQ_MODEL=llama-3.3-70b-versatile
```

API keys must be stored locally or in the deployment platform's environment variables and must not be committed to Git.

---

## 8. Running the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 9. Running the Frontend

The frontend is a simple static HTML application.

Open:

```text
frontend/index.html
```

in a browser.

For local development, the frontend communicates with the FastAPI backend.

If the backend URL changes, update the API base URL in `frontend/index.html`.

---

## 10. API

### Health Check

```http
GET /health
```

### Chat

```http
POST /api/chat
```

The chat endpoint accepts a session identifier and user message and returns:

* Assistant reply
* Current structured state
* Generated document
* Conversation messages
* Confirmed fields
* Unknown fields

---

## 11. Important Behaviour

### Multiple fields in one message

A single user response can provide several fields at once.

### Corrections

Previously captured information can be corrected without relying on old conversation history as the source of truth.

### Unknown information

Unknown or unconfirmed values are represented explicitly rather than being invented.

### Ambiguity

Ambiguous responses result in clarification questions.

### Contradictions

Potential contradictions are detected and handled before changing confirmed state.

### Explicit empty values

The application distinguishes between:

```text
None
```

meaning information was not provided, and:

```text
[]
```

meaning the user explicitly indicated that there are no values.

For example:

```text
No specific gifts.
```

results in:

```text
specific_gifts = []
```

---

## 12. LLM Reliability

LLM responses are validated using structured Pydantic models before state updates.

The application handles:

* Valid responses
* Malformed JSON
* Invalid response structures
* Invalid field types
* Missing API configuration
* Provider/network errors
* Ambiguous responses
* Contradictions

The deterministic Mock LLM provides predictable local behaviour for testing and development.

---

## 13. Tests

The project contains automated tests covering:

* API behaviour
* State management
* State protection
* Validation
* Mock LLM extraction
* Common language variations
* Corrections
* Contradictions
* Unknown responses
* Ambiguous responses
* Document generation
* Groq service errors
* LLM response validation
* Fixtures

Run:

```bash
cd backend
pytest -q
```

Final verification:

```text
111 passed
```

---

## 14. LLM Fixtures

The test suite includes fixtures for:

```text
backend/tests/fixtures/
├── valid_llm_response.json
├── ambiguous_llm_response.json
└── malformed_llm_response.json
```

These demonstrate handling of valid, ambiguous and malformed model responses.

---

## 15. Mock LLM and Real Provider

The application uses an LLM service abstraction so that the deterministic Mock LLM can be used without paid API access.

The provider can be selected through:

```env
LLM_PROVIDER=mock
```

or:

```env
LLM_PROVIDER=groq
```

This allows the Mock LLM to be replaced by a real provider without changing the rest of the application architecture.

---

## 16. Security

Secrets are kept outside source control.

Do not commit:

```text
.env
```

or real API keys.

Use:

```text
.env.example
```

as the configuration template.

---

## 17. Production Improvements

For a production system, I would improve:

* Persistent database-backed session storage
* Authentication and authorization
* Stronger audit logging
* Additional LLM validation and fallback strategies
* Rate limiting
* Monitoring and observability
* Stronger privacy and data-retention controls
* Secure handling of sensitive user information
* Human review for sensitive document generation
* Production-grade frontend hosting and API configuration

The current implementation intentionally keeps the scope small and focused on the requirements of the technical test.

---

## 18. Disclaimer

This project generates a fictional Personal Wishes Document for demonstration purposes only.

It is **not a legal service, does not provide legal advice, and should not be used as a real legal document**.
---

## Role-Based Claims & Safe Handover (Update)

**Demo login** (no passwords): pick a seeded user on `/login`. The frontend sends `X-User-Email`; the **backend** looks the user up and enforces the role on every protected endpoint (401 not logged in, 403 wrong role).

| Demo user | Role |
|---|---|
| Rahul Sharma / Ananya Patel / Devendra Verma | STUDENT |
| Campus Admin (`admin@campus.edu`) | ADMIN |

**Student:** browse items, report Lost/Found, submit a claim, see only their own claims (`/my-claims`) and reports (`/my-reports`). Cannot approve/reject, see others' claims, or see private details.
**Admin:** `/admin` dashboard (stats + pending claims), `/admin/claims` list, `/admin/claims/:id` review (private verification detail, private image, approve + assign handover location, reject, mark recovered).

**Flow:** claim `PENDING` -> admin approves + picks a handover location -> claim `APPROVED`, item `CLAIMED`, handover `READY_FOR_PICKUP` -> admin "Mark Recovered" -> item `RECOVERED`, handover `COMPLETED`. Reject -> claim `REJECTED`, item stays `ACTIVE`. Approving a claim auto-rejects other pending claims on the same item.

**Privacy:** public item APIs never return `phone`, `private_detail` or a PRIVATE image URL. Admin claim endpoints do; claimant phone is masked.

**API**
- Student: `GET /api/items`, `GET /api/items/{id}`, `GET /api/items/my`, `POST /api/items`, `POST /api/claims`, `GET /api/claims/my`
- Admin: `GET /api/admin/stats`, `GET /api/admin/claims`, `GET /api/admin/claims/{id}`, `PATCH /api/admin/claims/{id}`, `PATCH /api/admin/claims/{id}/handover`, `PATCH /api/admin/items/{id}/recovered`
- Demo auth: `GET /api/auth/demo-users`, `POST /api/auth/login`, `GET /api/auth/me`

**Run**
```
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
cd backend && pytest
```
An existing `campusfind.db` is upgraded automatically (new columns are added on startup). Delete it to re-seed fresh demo data.

The earlier unrelated "Document Intake Assistant" backend is kept untouched in `legacy_document_intake_backend/`.
