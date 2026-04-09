# Story 007: View Completed Chat as Read-Only

**Epic:** Epic 02 — Journal: Daily Reflection Chat
**Priority:** High
**Story Points:** 2
**Status:** Done

---

## User Story

**As a** user returning to the app after completing today's chat
**I want to** see my completed chat with all messages displayed and no ability to edit or add new messages
**So that** I can review my reflection while the integrity of my daily entry is preserved

---

## Acceptance Criteria

### AC1: Completed chat displays all messages
**Given** a user who has completed today's chat (status is "completed")
**When** they navigate to the Journal tab
**Then** the full chat is displayed in order: bot greeting, mood selection (as user message bubble), user reflection (as user message bubble), and bot acknowledgment (as bot message bubble)

### AC2: Input bar is hidden for completed chats
**Given** a user viewing a completed chat
**When** the chat is rendered
**Then** the text input bar and send button are not visible anywhere on the screen

### AC3: Messages are not editable
**Given** a user viewing a completed chat
**When** they interact with any message bubble (tap, long-press, or other gesture)
**Then** no edit, delete, or modification options are presented and the message content cannot be changed

### AC4: Next day allows a new chat
**Given** a user who completed yesterday's chat
**When** they open the Journal tab on the following calendar day
**Then** a new chat is created for the new day with a fresh greeting, and the previous day's completed chat is no longer shown as the active chat

### AC5: One-chat-per-day enforcement
**Given** a user who has a completed chat for today
**When** any attempt is made to create a second chat for the same date (via API or frontend)
**Then** the existing completed chat is returned and no duplicate chat is created

---

## Technical Notes

- Frontend: the `ChatView` component checks the chat `status` field; if "completed", render all messages but do not mount the input bar component or the mood selector
- Backend: the `GET /api/chats/today/` endpoint returns the existing chat regardless of status; the frontend determines the display mode based on `status`
- Backend validation: the `PATCH /api/chats/{id}/` endpoint should reject updates to chats with status "completed" and return a 400 response
- The unique constraint on (user, date) at the database level ensures one chat per user per day
- No typing indicator is shown when loading a completed chat — messages are rendered immediately since they are historical

---

## Dependencies

- Requires Story 006 (Write free-text reflection and receive acknowledgment) so that chats can reach the "completed" status
- Requires Story 004 (Start daily chat) for the chat loading mechanism

---

## INVEST Checklist

- [x] **Independent** — Addresses the read-only display of completed chats without modifying the chat creation or flow logic
- [x] **Negotiable** — The specific behavior on tap (no action vs. showing timestamp), message rendering order, and styling of completed vs. active chats can be discussed
- [x] **Valuable** — Preserves the integrity of daily reflections and ensures users understand the one-chat-per-day model
- [x] **Estimable** — Primarily frontend conditional rendering with a small backend validation; 2 points reflects low complexity
- [x] **Small** — Scoped to the read-only display and edit prevention; does not include chat creation, mood selection, or reflection input
- [x] **Testable** — Each criterion can be verified by completing a chat and returning to it, attempting edits, checking date rollover behavior, and testing the uniqueness constraint
