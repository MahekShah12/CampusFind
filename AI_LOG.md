# AI Development Log

## 1. AI Tools Used

### ChatGPT (GPT)

ChatGPT was used during development for:

* Understanding and breaking down the assignment requirements.
* Planning the application architecture and conversation flow.
* Designing the structured document state and data model.
* Planning LLM response validation and error handling.
* Identifying edge cases, contradictions, and clarification scenarios.
* Debugging application behavior.
* Planning regression tests and reviewing test coverage.
* Reviewing implementation decisions against the assignment requirements.

### Claude

Claude was used for targeted backend implementation and debugging, including:

* Improving the deterministic Mock LLM.
* Handling natural-language variations and correction phrases.
* Implementing contradiction and clarification handling.
* Handling explicit empty values such as no gifts or no additional wishes.
* Preventing unrelated messages from incorrectly updating the document state.
* Supporting corrections after document completion.
* Adding and refining regression tests for identified edge cases.

### GPT Antigravity

GPT Antigravity was used for the final frontend UI refinement.

It was used to reorganize the existing `index.html` and improve the **Draft / Live Preview** section so that the generated document is properly organized and fully viewable.

The frontend refinement was intentionally limited to the existing `index.html`. Existing JavaScript functionality, API behavior, backend logic, and application flow were preserved.

---

## 2. Key AI-Assisted Development Areas

### Requirements and Architecture

* Converted the assignment requirements into application components and workflows.
* Defined structured document state as the source of truth.
* Separated frontend, backend, application logic, LLM interaction, and document generation responsibilities.

### Conversation and State Handling

* Designed handling for missing, unclear, contradictory, and corrected information.
* Added contextual handling for short clarification responses.
* Prevented already-captured information from being unnecessarily requested again.
* Ensured unrelated user messages do not incorrectly update the structured state.

### LLM and Mock Provider

* Designed structured LLM responses with validation before state updates.
* Improved deterministic Mock LLM behavior for reliable local testing.
* Added handling for malformed responses and model/API failures.
* Supported both mock and external LLM provider configurations.

### Corrections and Edge Cases

The application was tested and refined for:

* Name corrections.
* Address corrections.
* Executor corrections.
* Gift corrections.
* Additional-wishes updates.
* Contradictory information.
* Explicit values such as no gifts or no additional wishes.
* Short answers to clarification questions.
* Multiple fields provided in a single message.
* Corrections made after the initial document was completed.

### Testing

* Added regression tests for identified conversation and state-management edge cases.
* Repeatedly ran the automated test suite after implementation changes.
* Performed manual testing of conversation flows and document updates.
* Verified frontend behavior after the final UI refinement.

---

## 3. AI Usage Approach

AI tools were used as development assistants for requirements analysis, implementation support, debugging, edge-case identification, testing, and frontend refinement.

AI-generated suggestions and code changes were reviewed and validated through automated tests and manual application testing.

The final application uses **structured state and validated updates as the source of truth** for the generated document rather than relying directly on conversation history.

## 4. Final Validation

The final implementation was validated through:

* Automated backend tests.
* Manual conversation-flow testing.
* Correction and contradiction testing.
* Document generation verification.
* Frontend UI verification.
* Review of backend/frontend separation.
* Verification that secrets and local configuration are not included in the submission.

**Final automated test count:** Update this with the result of the final `pytest -q` run.
