# Story 010: View Profile and Journey Stats — Implementation Plan

## Scope Analysis

- **Story Type:** Full-Stack (backend endpoints + frontend UI)
- **Complexity:** Moderate
- **Data model changes:** None — uses existing `User` (has `date_joined` via `AbstractUser`) and `DailyChat` models
- **New dependencies:** None
- **Architect consultation:** Not needed

---

## Task Breakdown

### Backend (4 tasks)

#### B1. Add `date_joined` to `UserSerializer`

The `User` model already has `date_joined` from Django's `AbstractUser`. Add it to `UserSerializer.Meta.fields` so the existing `GET /api/me/` endpoint returns it.

**File:** `backend/api/serializers.py`

---

#### B2. Create `ProfileStatsSerializer`

A read-only serializer for the stats response:
- `total_chats` (integer)
- `current_streak` (integer)
- `longest_streak` (integer)
- `most_frequent_mood` (object with `value`, `emoji`, `label` — or `null` if no chats)

**File:** `backend/api/serializers.py`

---

#### B3. Create `ProfileStatsView` — `GET /api/profile/stats/`

New endpoint that computes journey stats from `DailyChat` data:

- **`total_chats`**: `DailyChat.objects.filter(user=request.user, status="completed").count()`
- **`current_streak`**: Query completed chat dates ordered descending, walk backward from today (or yesterday) counting consecutive days
- **`longest_streak`**: Query all completed chat dates ordered ascending, iterate to find the longest consecutive run
- **`most_frequent_mood`**: Aggregate most common mood value from completed chats using Django ORM `Count` + ordering, map to emoji/label using `DailyChat.MOOD_DISPLAY`

Handle the zero-state: if no completed chats, return `total_chats=0`, `current_streak=0`, `longest_streak=0`, `most_frequent_mood=null`.

**Files:** `backend/api/views.py`, `backend/api/urls.py`

---

#### B4. Write backend tests for stats endpoint

Test cases:
- Zero-state (new user, no chats) — all zeros, mood is null
- User with multiple completed chats — correct total count
- Current streak calculation — consecutive days including today
- Current streak calculation — consecutive days ending yesterday (no chat today)
- Current streak broken by a gap day
- Longest streak across full history
- Most frequent mood calculated correctly
- In-progress chats excluded from all stats
- Stats refresh after new chat completion (AC4)

**File:** `backend/api/tests.py`

---

### Frontend (5 tasks)

#### F1. Add `ProfileStats` type and profile service

Add the TypeScript interface for the stats API response to `types/api.ts`.
Create `services/profile.ts` with a `getProfileStats()` function.

**Files:** `frontend/src/types/api.ts`, `frontend/src/services/profile.ts`

---

#### F2. Create `ProfileHeader` component

Displays:
- User avatar emoji (large, centered)
- Display name
- "Member since [formatted date]" — format `date_joined` as readable date (e.g., "March 1, 2026")

Uses `useAuth()` to get user data. The `date_joined` field will now be available from the user object.

**Files:** `frontend/src/components/profile/ProfileHeader.tsx`, `frontend/src/components/profile/ProfileHeader.css`

---

#### F3. Create `StatsGrid` component

A 2×2 grid displaying four stat cards:
1. **Total Chats** — number with label
2. **Current Streak** — number with "days" suffix
3. **Most Frequent Mood** — emoji + label (or "None yet")
4. **Longest Streak** — number with "days" suffix

Each card: icon/emoji at top, value in large text, label below.

**Files:** `frontend/src/components/profile/StatsGrid.tsx`, `frontend/src/components/profile/StatsGrid.css`

---

#### F4. Rewrite `ProfilePage`

Replace the current stub with:
1. Fetch stats on mount via `getProfileStats()`
2. Render `ProfileHeader` (user info from auth context)
3. Render `StatsGrid` (stats from API)
4. Keep the Sign Out button at the bottom
5. Handle loading and error states

**Files:** `frontend/src/pages/ProfilePage.tsx`, `frontend/src/pages/ProfilePage.css`

---

#### F5. Update `User` type to include `date_joined`

Add `date_joined: string` to the `User` interface in `types/api.ts` so the profile header can display it.

**File:** `frontend/src/types/api.ts`

---

## Implementation Order

1. **B1** + **F5**: Add `date_joined` to serializer and TS type (parallel, independent)
2. **B2** + **B3**: Create stats serializer and view
3. **B4**: Backend tests
4. **F1**: Frontend types and service
5. **F2** + **F3**: Profile components (parallel)
6. **F4**: Wire up ProfilePage

---

## Testing Strategy

- **Backend:** Django `APITestCase` tests for the stats endpoint covering all ACs
- **Frontend:** Manual verification of profile display, zero-state, and stats refresh after completing a chat
- **Integration:** Verify `/api/me/` now includes `date_joined`, verify `/api/profile/stats/` returns correct computations

---

## Acceptance Criteria Coverage

| AC | How it's met |
|----|-------------|
| AC1: Profile header | `ProfileHeader` component using `useAuth()` + `date_joined` from updated `UserSerializer` |
| AC2: Stats grid | `StatsGrid` component consuming `GET /api/profile/stats/` |
| AC3: Stats from real data | Server-side ORM queries against `DailyChat` model |
| AC4: Stats refresh | `ProfilePage` re-fetches stats on mount (tab switch triggers remount or re-fetch) |
| AC5: Zero-state | Backend returns zeros/null, frontend displays "0" and "None yet" |
