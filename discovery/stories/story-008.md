# Story 008: View Monthly Mood Calendar

**Epic:** Epic 03 — Calendar & Mood Insights
**Priority:** Medium
**Story Points:** 5
**Status:** Draft

---

## User Story

**As a** user who has been journaling regularly
**I want to** view a monthly calendar grid with mood emojis displayed on the days I completed a chat
**So that** I can visually spot patterns in my mood over time and stay motivated to maintain my reflection habit

---

## Acceptance Criteria

### AC1: Monthly calendar grid renders correctly
**Given** a signed-in user navigating to the Calendar tab
**When** the calendar view loads
**Then** a standard monthly grid is displayed for the current month showing the correct day names as column headers, the correct number of days for the month, and days aligned to the correct day-of-week columns

### AC2: Mood emojis shown on completed days
**Given** a user who has completed chats on multiple days within the displayed month
**When** the calendar grid renders
**Then** each day with a completed chat displays the corresponding mood emoji (Happy, Calm, Neutral, Down, or Frustrated) and days without a completed chat are displayed without any emoji

### AC3: Current day is highlighted
**Given** a user viewing the current month
**When** the calendar grid renders
**Then** today's date cell has a distinct visual highlight (teal-blue border, matching the design system accent color #2d8ab0) that differentiates it from all other day cells

### AC4: Month navigation with previous and next arrows
**Given** a user viewing the calendar for any month
**When** they tap the left arrow
**Then** the calendar navigates to the previous month and loads the corresponding mood data
**When** they tap the right arrow
**Then** the calendar navigates to the next month and loads the corresponding mood data

### AC5: Calendar handles months with different day counts
**Given** a user navigating between months
**When** they view February (28 or 29 days), a 30-day month, or a 31-day month
**Then** the calendar grid correctly displays the right number of days with proper alignment and no visual artifacts or missing days

---

## Technical Notes

- Backend endpoint: `GET /api/chats/monthly/?year=YYYY&month=MM` — returns a list of objects with `date` and `mood` for all completed chats in the specified month
- Frontend: `CalendarView` component renders a CSS grid (7 columns for days of the week); each cell is a `DayCell` component that conditionally renders the mood emoji
- The month/year header is displayed above the grid with left/right arrow buttons for navigation
- Current day detection: compare each cell's date with `new Date()` to apply the highlight class
- Consider pre-fetching adjacent months for smoother navigation
- Empty cells at the start and end of the grid (before the first day and after the last day of the month) should be rendered as blank/inactive cells

---

## Dependencies

- Requires Story 003 (Protected routes and session persistence) for authenticated API access
- Requires Story 006 (Write free-text reflection) so that completed chats with mood data exist to display
- No dependency on Story 009 (daily summary) — the calendar grid and the summary are independent features

---

## INVEST Checklist

- [x] **Independent** — Delivers the calendar grid and mood display without requiring the daily summary (Story 009) or profile stats (Story 010)
- [x] **Negotiable** — Grid layout, emoji sizing, highlight style, navigation animation, and pre-fetching strategy can be adjusted
- [x] **Valuable** — Provides the mood pattern visibility that motivates continued journaling and is a core differentiator of the app
- [x] **Estimable** — Calendar grid rendering and a data-fetching endpoint are well-understood; 5 points reflects the frontend complexity of a custom calendar component plus backend query work
- [x] **Small** — Scoped to the monthly grid with mood emojis and navigation; daily summary overlay is a separate story
- [x] **Testable** — Each criterion can be verified by checking grid rendering across months, verifying emoji placement against chat data, confirming the current day highlight, and testing navigation across month boundaries
