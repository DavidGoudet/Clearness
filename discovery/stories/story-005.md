# Story 005: Select Mood During Chat Flow

**Epic:** Epic 02 — Journal: Daily Reflection Chat
**Priority:** High
**Story Points:** 3
**Status:** Draft

---

## User Story

**As a** user who has just received the daily greeting
**I want to** select my current mood from a set of emoji options displayed inline in the chat
**So that** I can quickly and expressively capture how I am feeling today

---

## Acceptance Criteria

### AC1: Mood selector displayed after greeting
**Given** a user viewing today's chat where the greeting message has been displayed
**When** the greeting animation completes
**Then** an inline mood selector appears within the chat area showing exactly five options: Happy (with smiling emoji), Calm (with relieved emoji), Neutral (with neutral emoji), Down (with pensive emoji), and Frustrated (with angry emoji)

### AC2: Mood selection rendered as user message
**Given** a user viewing the mood selector
**When** they tap one of the five mood options
**Then** the selected mood emoji and label are displayed as a user message bubble (right-aligned, accent-blue background) and the mood selector is hidden

### AC3: Mood persisted to backend
**Given** a user who has selected a mood
**When** the mood is displayed as a user message
**Then** the selected mood value is sent to the backend and saved on the chat record, and the chat status remains "in_progress"

### AC4: Mood cannot be changed after selection
**Given** a user who has already selected a mood for today's chat
**When** they return to the chat or refresh the page
**Then** the mood selector is not shown again and the previously selected mood is displayed as a user message bubble in the correct position in the chat history

### AC5: All five mood options are functional
**Given** a user viewing the mood selector
**When** they select any of the five mood options (Happy, Calm, Neutral, Down, Frustrated)
**Then** each option correctly saves its corresponding mood value and displays the correct emoji and label in the user message bubble

---

## Technical Notes

- Backend endpoint: `PATCH /api/chats/{id}/` — accepts `{ "mood": "happy" }` (or calm, neutral, down, frustrated) and updates the chat record
- Mood values stored as an enum/choice field on the Chat model: `happy`, `calm`, `neutral`, `down`, `frustrated`
- Frontend: `MoodSelector` component rendered inline within the chat message list; emits the selected mood to the parent `ChatView`
- The mood selector should be styled as a horizontal row of tappable emoji buttons with labels beneath each emoji
- After selection, the `MoodSelector` component is replaced with a standard user message bubble showing the chosen mood
- The chat flow state machine: greeting -> mood_selection -> reflection_input -> completed

---

## Dependencies

- Requires Story 004 (Start daily chat with personalized greeting) so that a chat exists and the greeting has been displayed

---

## INVEST Checklist

- [x] **Independent** — Handles only the mood selection step; the greeting is delivered by Story 004 and the reflection input is handled by Story 006
- [x] **Negotiable** — The specific emojis, labels, selector layout (horizontal vs. grid), and animation on selection can be adjusted
- [x] **Valuable** — Captures the user's emotional state, which is the key data point for mood tracking and calendar visualization
- [x] **Estimable** — A well-scoped UI component plus a single PATCH endpoint; 3 points reflects moderate frontend work with straightforward backend logic
- [x] **Small** — Scoped to mood selection only; does not include the greeting, reflection input, or acknowledgment
- [x] **Testable** — Each criterion can be verified by selecting each mood option, checking persistence, refreshing to confirm immutability, and inspecting the rendered chat messages
