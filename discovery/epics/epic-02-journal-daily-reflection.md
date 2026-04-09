# Epic 02 -- Journal: Daily Reflection Chat

**Priority:** Must Have (MVP)
**Estimated Effort:** L (Large)
**Target Duration:** 6-8 weeks

---

## Description

Build the core feature of Clearness: a daily chat-based journal where users reflect on their day through a structured conversational flow. Each day has exactly one chat session. The app greets the user with a time-of-day-aware message, asks how they are feeling, captures a mood via an emoji selector, accepts a free-text reflection, and closes with an empathetic acknowledgment. Completed chats become read-only.

This is the primary value driver of the application and the feature that delivers on the core value proposition of "a few minutes of daily reflection."

---

## Business Value

- Delivers the primary user experience that defines Clearness as a product
- Drives the daily engagement habit that underpins all retention metrics (D7: 45%, D30: 25%)
- Generates the mood and reflection data that feeds the Calendar and Profile features
- The structured flow keeps MVP scope manageable while still delivering a meaningful journaling experience

---

## Acceptance Criteria (Epic Level)

1. Opening the Journal tab shows today's chat; if no chat exists for today, the structured flow begins automatically
2. The greeting message is personalized by time of day (morning, afternoon, evening) and the user's display name
3. Bot messages appear with a typing indicator animation (three pulsing dots) before the content is revealed
4. The user can select a mood from the five-option emoji selector (Happy, Calm, Neutral, Down, Frustrated)
5. The user can type a free-text reflection and submit it via a send button
6. The app responds with a templated, sentiment-appropriate acknowledgment message
7. Once the flow is complete, the input bar is hidden and the chat is read-only for that day
8. If the user returns later the same day, they see their completed chat in read-only mode
9. Chat messages are persisted to the backend and associated with the authenticated user and the current date
10. The chat UI follows the design system: user bubbles in teal-blue right-aligned, bot bubbles in light grey left-aligned, auto-scroll to latest message

---

## Child Story Candidates

| # | Story Title | Description | Size |
|---|-------------|-------------|------|
| 1 | Daily chat data model | Create Django model for daily chats: id, user FK, date (unique per user+day), greeting, user_response, bot_reply, mood_emoji, mood_label, status (in_progress/completed), completed_at, timestamps | 3 |
| 2 | Chat API endpoints | Implement REST endpoints: GET /api/chats/today/ (get or initiate today's chat), PATCH /api/chats/{id}/ (update with mood, response), GET /api/chats/{date}/ (retrieve a specific day's chat) | 5 |
| 3 | Chat screen layout and message list | Build the chat screen UI with a scrollable message list, fixed bottom input bar, proper alignment (bot left, user right), and auto-scroll behavior | 5 |
| 4 | Time-of-day personalized greeting | Implement greeting logic that selects the appropriate greeting template based on the current time and inserts the user's display name | 2 |
| 5 | Typing indicator animation | Create the three-pulsing-dots animation component that displays before each bot message is revealed | 2 |
| 6 | Mood emoji selector | Build the inline emoji selector component with the five mood options; on selection, the chosen mood is sent to the backend and displayed as a user message bubble | 3 |
| 7 | Free-text input and send | Implement the text input area with a send button that activates only when text is present; on send, the message is displayed as a user bubble and submitted to the backend | 3 |
| 8 | Structured chat flow orchestration | Implement the state machine that drives the chat flow: greeting, ask mood, capture mood, ask reflection, capture text, send acknowledgment, mark complete | 5 |
| 9 | Templated empathetic acknowledgment | Create sentiment-based response templates (one set per mood) and select the appropriate acknowledgment based on the user's chosen mood | 3 |
| 10 | Read-only completed chat state | When a chat has status "completed," hide the input bar, disable interactions, and display a subtle "Chat completed" indicator | 2 |
| 11 | Chat persistence and reload | Ensure that navigating away and returning to the Journal tab, or refreshing the browser, restores the chat to its correct state (in-progress step or read-only) | 3 |
| 12 | One-chat-per-day enforcement | Enforce on both backend (unique constraint on user+date) and frontend (check for existing chat before initiating) that only one chat exists per user per day | 2 |

**Total estimated story points:** ~38

---

## Dependencies

| Epic | Dependency Type | Detail |
|------|----------------|--------|
| Epic 01 -- Authentication and Onboarding | Hard | User must be authenticated to create or view chats; user identity is needed for personalized greetings |

---

## Risks and Considerations

- The structured chat flow must feel natural despite being templated; poor tone will hurt retention
- The typing indicator timing needs tuning -- too fast feels robotic, too slow feels laggy
- The "one chat per day" rule needs clear handling of timezone edge cases (when does "today" roll over?)
- If the user's timezone changes (travel), existing chats should not be lost or duplicated
- Offline support (mentioned in PRD Section 6.2) is deferred to a future epic but the data model should not preclude it

---

## Definition of Done

- All acceptance criteria are met
- Chat flow can be completed end-to-end for a new day
- Returning to a completed chat shows read-only view
- API endpoints have automated tests covering the chat lifecycle
- UI is responsive and matches the Clearness design system on mobile viewports
