# Story 010: View Profile and Journey Stats

**Epic:** Epic 04 — Profile & Account Management
**Priority:** Medium
**Story Points:** 5
**Status:** Draft

---

## User Story

**As a** user who has been journaling with Clearness
**I want to** view my profile information and journey statistics including total chats, streaks, and most frequent mood
**So that** I can see my progress, feel a sense of accomplishment, and stay motivated to continue my reflection habit

---

## Acceptance Criteria

### AC1: Profile header displays user information
**Given** a signed-in user navigating to the Profile tab
**When** the profile screen loads
**Then** a profile header is displayed showing the user's avatar (from their Google/Apple account or a default placeholder), their display name, and a "Member since [date]" label with the date they first signed in, formatted as a readable date (e.g., "Member since March 1, 2026")

### AC2: Journey stats grid displays four metrics
**Given** a signed-in user with completed chats
**When** the profile screen loads
**Then** a 2x2 stats grid is displayed showing: total number of completed chats, current streak (consecutive days with a completed chat up to and including today or yesterday), most frequent mood (emoji and label), and longest streak (most consecutive days ever)

### AC3: Stats are calculated from actual chat data
**Given** a user who has completed 15 chats over the past 20 days with the last 5 days being consecutive and "Calm" being selected 7 times
**When** the profile screen loads
**Then** the stats show: Total Chats = 15, Current Streak = 5, Most Frequent Mood = Calm (with emoji), and Longest Streak is accurately calculated from the full chat history

### AC4: Stats update after a new chat is completed
**Given** a user who views their profile, then completes a new daily chat
**When** they return to the Profile tab
**Then** the stats are refreshed and reflect the newly completed chat (total chats incremented, streak recalculated, mood frequency updated)

### AC5: Zero-state for new users with no chats
**Given** a newly registered user who has not completed any chats
**When** they navigate to the Profile tab
**Then** the profile header shows their name and join date, and the stats grid shows: Total Chats = 0, Current Streak = 0, Most Frequent Mood = "None yet", and Longest Streak = 0

---

## Technical Notes

- Backend endpoints:
  - `GET /api/profile/` — returns user profile data: `display_name`, `email`, `avatar_url`, `date_joined`
  - `GET /api/profile/stats/` — returns computed stats: `total_chats`, `current_streak`, `most_frequent_mood`, `longest_streak`
- Stats computation should be performed server-side using Django ORM queries against the Chat model:
  - `total_chats`: count of chats with status "completed" for the user
  - `current_streak`: count consecutive completed-chat dates backward from today (or yesterday if no chat today)
  - `most_frequent_mood`: mode of the mood field across all completed chats
  - `longest_streak`: requires iterating ordered chat dates to find the longest consecutive run
- Frontend: `ProfileView` component with a `ProfileHeader` sub-component and a `StatsGrid` sub-component
- Consider caching stats on the backend if computation becomes expensive at scale; for MVP, real-time calculation is acceptable
- Avatar fallback: if no avatar URL is available from the auth provider, display a default avatar (initials circle or generic icon)

---

## Dependencies

- Requires Story 003 (Protected routes and session persistence) for authenticated API access
- Requires Story 001 or Story 002 (authentication) so that user profile data (name, avatar, join date) exists
- Benefits from Story 006 (Write free-text reflection) so that completed chat data exists for meaningful stats, though the zero-state is handled

---

## INVEST Checklist

- [x] **Independent** — Delivers the profile display and stats as a standalone screen; does not modify the Journal or Calendar features
- [x] **Negotiable** — Stats grid layout, specific stat definitions (e.g., current streak including today vs. yesterday), avatar fallback design, and additional stats can be discussed
- [x] **Valuable** — Provides users with a sense of progress and accomplishment that reinforces the daily journaling habit
- [x] **Estimable** — Involves two backend endpoints with aggregation queries and a frontend profile screen; 5 points reflects backend computation complexity plus frontend layout work
- [x] **Small** — Scoped to profile display and stats only; does not include settings, reminders, or account deletion
- [x] **Testable** — Each criterion can be verified by checking profile data accuracy, computing expected stats from known chat data, testing the zero-state, and confirming stats update after new chat completion
