# Story 004: Start Daily Chat with Personalized Greeting

**Epic:** Epic 02 — Journal: Daily Reflection Chat
**Priority:** High
**Story Points:** 5
**Status:** Draft

---

## User Story

**As a** signed-in user
**I want to** open the Journal tab and see a personalized greeting that addresses me by name and reflects the time of day
**So that** I feel welcomed and encouraged to begin my daily reflection

---

## Acceptance Criteria

### AC1: New chat created with time-of-day greeting
**Given** a signed-in user who has not started a chat today
**When** they navigate to the Journal tab
**Then** a new chat is created for today's date and the bot displays a greeting message in the format "Good [morning/afternoon/evening], [Name]! How are you feeling today?" where the time period is based on the user's local time (morning: 5:00-11:59, afternoon: 12:00-16:59, evening: 17:00-4:59)

### AC2: Typing indicator shown before greeting
**Given** a signed-in user opening the Journal tab for a new day
**When** the chat is initialized and the greeting is being prepared
**Then** a typing indicator animation (three pulsing dots) is displayed in a bot message bubble for 1-2 seconds before the greeting text is revealed

### AC3: Existing in-progress chat loaded
**Given** a signed-in user who already started today's chat but did not complete it
**When** they navigate to the Journal tab
**Then** the existing chat is loaded with all previous messages displayed and the chat resumes from where they left off (e.g., mood selection or reflection input)

### AC4: Greeting uses user's display name
**Given** a signed-in user whose profile has a display name
**When** a new daily chat is initiated
**Then** the greeting includes the user's actual display name, not a generic placeholder

### AC5: Chat date uniqueness enforced
**Given** a signed-in user
**When** the backend receives a request to create a chat for today
**Then** if a chat already exists for today's date, the existing chat is returned instead of creating a duplicate

---

## Technical Notes

- Backend endpoint: `GET /api/chats/today/` — returns today's existing chat if one exists, or creates and returns a new chat with the greeting populated
- The greeting message is generated server-side to ensure consistency; time-of-day is determined from the user's timezone (sent as a header or query param)
- Chat model: `id`, `user`, `date` (unique per user per day), `greeting`, `mood`, `user_response`, `bot_reply`, `status` (in_progress/completed), `created_at`, `completed_at`
- Frontend: `ChatView` component fetches today's chat on mount, renders messages as chat bubbles, and shows the typing indicator animation before revealing each bot message
- Bot messages are left-aligned with light-grey background; the typing indicator uses CSS animation with three pulsing dots

---

## Dependencies

- Requires Story 003 (Protected routes and session persistence) so that the user is authenticated and their identity is known
- Requires Story 001 or Story 002 (authentication) so that user profiles with display names exist

---

## INVEST Checklist

- [x] **Independent** — Delivers the chat initialization and greeting flow without depending on mood selection or reflection input
- [x] **Negotiable** — Time-of-day thresholds, greeting wording, typing indicator duration, and animation style can be adjusted
- [x] **Valuable** — Establishes the core Journal experience and creates the personalized, welcoming interaction that drives daily engagement
- [x] **Estimable** — Involves creating the chat model, a backend endpoint, and a frontend chat UI component; 5 points reflects full-stack work with UI animation
- [x] **Small** — Scoped to chat creation and greeting only; mood selection and reflection are separate stories
- [x] **Testable** — Each criterion can be verified by checking greeting content at different times, verifying typing indicator behavior, and testing chat deduplication logic
