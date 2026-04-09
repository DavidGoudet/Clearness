# Story 009: View Daily Summary from Calendar

**Epic:** Epic 03 — Calendar & Mood Insights
**Priority:** Medium
**Story Points:** 3
**Status:** Draft

---

## User Story

**As a** user browsing my mood calendar
**I want to** tap on a specific day to see a summary of that day's mood, reflection, and timestamp
**So that** I can revisit my past reflections and recall how I was feeling on a particular day

---

## Acceptance Criteria

### AC1: Tapping a day with a completed chat opens the summary
**Given** a user viewing the monthly calendar
**When** they tap on a day cell that has a completed chat (indicated by a mood emoji)
**Then** a summary overlay or panel is displayed showing the mood emoji with its label (e.g., "Happy" with the corresponding emoji), the user's free-text reflection, and the date and time the chat was completed

### AC2: Tapping an empty day shows a placeholder
**Given** a user viewing the monthly calendar
**When** they tap on a day cell that has no completed chat
**Then** a message is displayed reading "No entry for this day" with no mood, reflection, or timestamp data

### AC3: Summary is dismissible
**Given** a user viewing a daily summary overlay
**When** they tap a close button, tap outside the overlay, or swipe it away
**Then** the summary is dismissed and the user returns to the calendar grid view

### AC4: Summary displays correct data for the selected day
**Given** a user who completed a chat on March 1 with mood "Calm" and reflection "Felt peaceful after a morning walk"
**When** they tap on March 1 in the calendar
**Then** the summary shows the Calm emoji, the label "Calm", the reflection text "Felt peaceful after a morning walk", and the date "March 1, 2026" with the completion time

### AC5: Summary works for any navigated month
**Given** a user who has navigated to a previous month using the calendar arrows
**When** they tap on a day in that previous month
**Then** the correct summary data for that historical day is displayed

---

## Technical Notes

- Backend: the `GET /api/chats/monthly/?year=YYYY&month=MM` endpoint from Story 008 may already return sufficient data (mood, user_response, completed_at) for the summary; alternatively, use `GET /api/chats/{id}/` for full chat details if the monthly endpoint returns only summary-level data
- Frontend: implement the summary as a modal/bottom-sheet component (`DaySummary`) that receives the selected day's chat data as props
- The summary component should handle both states: chat exists (show data) and no chat (show placeholder)
- Date formatting: use a user-friendly format such as "March 1, 2026 at 8:32 PM"
- The summary should not allow editing — it is strictly a read-only view

---

## Dependencies

- Requires Story 008 (View monthly mood calendar) so that the calendar grid and day cells exist to tap on
- Requires Story 006 (Write free-text reflection) so that completed chats with reflection data exist

---

## INVEST Checklist

- [x] **Independent** — Handles only the day-tap summary interaction; the calendar grid itself is delivered by Story 008
- [x] **Negotiable** — The summary presentation (modal vs. bottom sheet vs. inline expansion), data fields shown, and dismiss mechanism can be adjusted
- [x] **Valuable** — Enables users to revisit past reflections, reinforcing the journaling habit and providing personal insight
- [x] **Estimable** — A single UI overlay component with data binding; 3 points reflects moderate frontend work with minimal backend changes
- [x] **Small** — Scoped to the summary display on day tap; does not include the calendar grid, navigation, or mood display
- [x] **Testable** — Each criterion can be verified by tapping days with and without chats, checking displayed data accuracy, testing dismiss behavior, and verifying historical month access
