# Story 006: Write Free-Text Reflection and Receive Acknowledgment

**Epic:** Epic 02 — Journal: Daily Reflection Chat
**Priority:** High
**Story Points:** 8
**Status:** Draft

---

## User Story

**As a** user who has selected my mood
**I want to** write a free-text reflection about my day and receive a warm, empathetic acknowledgment from the app
**So that** I feel heard and encouraged to continue my daily reflection habit

---

## Acceptance Criteria

### AC1: Text input bar appears after mood selection
**Given** a user who has just selected their mood in today's chat
**When** the mood selection is confirmed and displayed as a user message
**Then** a text input bar is visible at the bottom of the screen with placeholder text such as "Share your thoughts..." and a send button

### AC2: Send button activates only with text
**Given** a user viewing the text input bar
**When** the input field is empty or contains only whitespace
**Then** the send button is visually disabled and non-functional
**When** the user types at least one non-whitespace character
**Then** the send button becomes enabled and visually active

### AC3: Reflection submitted and displayed as user message
**Given** a user who has typed a reflection in the input bar
**When** they tap the send button
**Then** the reflection text is displayed as a user message bubble (right-aligned, accent-blue), the input bar is cleared, and the text is sent to the backend

### AC4: Empathetic acknowledgment displayed with typing indicator
**Given** a user who has submitted their reflection
**When** the backend processes the reflection and returns the bot reply
**Then** a typing indicator (three pulsing dots) is shown in a bot message bubble while the LLM response is being generated, followed by a personalized, empathetic acknowledgment message that feels like a real conversation

### AC5: Acknowledgment is contextual and personalized via LLM
**Given** the chat has a mood and the user has written a free-text reflection
**When** the acknowledgment is generated
**Then** the backend calls the OpenAI API to produce a response that is empathetic, contextually relevant to the user's reflection text, and tonally appropriate to their selected mood
**And** the response feels natural, warm, and conversational — not templated or generic
**Given** the LLM API is unavailable or returns an error
**When** the acknowledgment is generated
**Then** the backend falls back to a short, generic empathetic message (e.g., "Thank you for sharing. Your reflection matters.") and logs the error for monitoring

### AC6: Chat marked as completed after acknowledgment
**Given** a user who has received the bot acknowledgment
**When** the acknowledgment message is displayed
**Then** the chat status is updated to "completed" with a `completed_at` timestamp, and the input bar is hidden

---

## Technical Notes

- Backend endpoint: `PATCH /api/chats/{id}/` — accepts `{ "user_response": "..." }`, calls the LLM service to generate an empathetic `bot_reply` based on the stored mood and the user's reflection text, sets `status` to "completed" and `completed_at` to the current timestamp, and returns the updated chat including `bot_reply`
- **LLM Service (`backend/api/services/llm_service.py`):** Create a dedicated service that wraps the OpenAI API client
  - Uses the `openai` Python package to call the OpenAI Chat Completions API
  - Model and API key are configured via environment variables (`OPENAI_API_KEY`, `OPENAI_MODEL`) — the user will provide credentials for the specific model to use
  - The service builds a system prompt that instructs the model to act as a warm, empathetic journaling companion, taking into account the user's selected mood
  - The user message sent to the API includes the mood and the reflection text
  - Includes error handling: on API failure or timeout, returns a generic fallback message so the user is never left without a response
  - Timeout and retry settings should be configurable via environment variables
- Frontend: after the mood is selected, render the input bar component; on send, PATCH the reflection, show typing indicator while waiting for the backend response, then reveal the bot reply
- Auto-scroll the chat to the latest message after each new message is added
- Input bar component: fixed position at bottom, contains a text field and a send icon button

---

## Dependencies

- Requires Story 005 (Select mood during chat flow) so that a mood exists on the chat record to drive the acknowledgment sentiment
- Requires Story 004 (Start daily chat) so that the chat entity exists

---

## INVEST Checklist

- [x] **Independent** — Handles the reflection input and acknowledgment step only; mood selection and read-only view are separate stories
- [x] **Negotiable** — LLM model choice, system prompt wording, typing indicator behavior, input placeholder text, and auto-scroll behavior can be refined
- [x] **Valuable** — Completes the core daily reflection loop, giving users the sense of being heard which is central to the app's value proposition
- [x] **Estimable** — Involves text input handling, a PATCH endpoint with LLM integration, an OpenAI service layer, error handling with fallback, and typing indicator animation; 8 points reflects full-stack work plus external API integration
- [x] **Small** — Scoped to the reflection and acknowledgment step; does not include mood selection or the read-only completed view
- [x] **Testable** — Each criterion can be verified by submitting reflections with different moods, checking acknowledgment content, verifying send button states, and confirming the chat is marked completed
