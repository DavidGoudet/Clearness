# Implementation Plan: Story 008 — View Monthly Mood Calendar

**Story type:** Full-Stack | **Complexity:** Moderate | **PRs:** 1

---

## 1. Backend: Monthly Chats Endpoint

### 1a. New serializer: `MonthlyChatSerializer`
- File: `backend/api/serializers.py`
- Read-only ModelSerializer on `DailyChat` with fields: `id`, `date`, `mood`
- Lightweight — no messages, no timestamps

### 1b. New view: `MonthlyChatListView`
- File: `backend/api/views.py`
- `APIView` with `permission_classes = [IsAuthenticated]`
- `GET` handler reads `year` and `month` query params
- Validates both present and valid (400 otherwise)
- Queries `DailyChat.objects.filter(user=request.user, date__year=year, date__month=month, status="completed")` ordered by `date`
- Returns serialized list

### 1c. Register URL
- File: `backend/api/urls.py`
- `path("chats/monthly/", MonthlyChatListView.as_view(), name="chat-monthly")`

### 1d. Backend tests
- File: `backend/api/tests.py`
- Test class `MonthlyChatAPITest(APITestCase)` following existing patterns
- Cases: completed-only filtering, correct fields, empty month, missing params, invalid params, user isolation, auth required

---

## 2. Frontend: Types & API Service

### 2a. New type: `MonthlyChat`
- File: `frontend/src/types/api.ts`
- Interface: `{ id: number; date: string; mood: Mood }`

### 2b. New service: `getMonthlyChats`
- File: `frontend/src/services/chat.ts`
- `(year: number, month: number) => Promise<MonthlyChat[]>`
- Uses existing `apiRequest` pattern

---

## 3. Frontend: Calendar Components

### 3a. `CalendarPage` — replace stub
- File: `frontend/src/pages/CalendarPage.tsx`
- State: currentYear, currentMonth, chats, isLoading, error
- Fetches on mount and month change via `getMonthlyChats`
- Month navigation handlers (prev/next with year wrapping)
- Renders: header with month label + nav arrows, then `<CalendarGrid>`

### 3b. `CalendarGrid` component
- New file: `frontend/src/components/calendar/CalendarGrid.tsx`
- Props: year, month, moodByDay map, today info
- Renders 7-column CSS Grid: day-of-week headers, leading empty cells, day cells
- Date arithmetic: `new Date(year, month-1, 1).getDay()` for offset, `new Date(year, month, 0).getDate()` for days count

### 3c. `CalendarDay` component
- New file: `frontend/src/components/calendar/CalendarDay.tsx`
- Props: day number, mood (optional), isToday flag
- Renders day number + mood emoji if present
- `.calendar-day--today` class with `border: 2px solid #2d8ab0`

---

## 4. Frontend: Styles

### 4a. `CalendarPage.css`
- File: `frontend/src/pages/CalendarPage.css`
- Page layout, month navigation (flexbox), loading/error states

### 4b. `CalendarGrid.css`
- File: `frontend/src/components/calendar/CalendarGrid.css`
- 7-column CSS Grid, day header styling, day cell styling
- Today highlight, emoji sizing, empty cell styling

---

## 5. Task Order

1. Backend serializer → view → URL → tests (run `python manage.py test`)
2. Frontend type → service function
3. Frontend components: CalendarDay → CalendarGrid → CalendarPage
4. Frontend CSS alongside their components
5. Manual integration verification

---

## Key Design Decisions

- **No calendar library** — requirements are simple enough for vanilla JS + CSS Grid
- **Lightweight serializer** — only `id`, `date`, `mood` to keep response small
- **Completed chats only** — backend filters `status="completed"` so frontend doesn't need to
- **Sunday-start week** — using JS `Date.getDay()` which zero-indexes at Sunday
