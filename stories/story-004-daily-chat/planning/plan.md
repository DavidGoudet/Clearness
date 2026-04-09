# Story-004: Start Daily Chat with Personalized Greeting — Implementation Plan

**Story Type:** Full-Stack | **Points:** 5 | **Branch:** `004-daily-chat` (current branch)
**Single PR** — `004-daily-chat` into `main`

---

## User Story

As a signed-in user, I want to open the Journal tab and see a personalized greeting that addresses me by name and reflects the time of day, so that I feel welcomed and encouraged to begin my daily reflection.

## Acceptance Criteria

1. **AC1:** New chat created with time-of-day greeting (morning 5:00-11:59, afternoon 12:00-16:59, evening 17:00-4:59)
2. **AC2:** Typing indicator (three pulsing dots) shown for 1-2s before greeting
3. **AC3:** Existing in-progress chat loaded with all previous messages
4. **AC4:** Greeting uses user's display name
5. **AC5:** Chat date uniqueness enforced (return existing chat, don't duplicate)

---

## Architectural Approach

### Data Architecture Decision

The architecture document (Section 2.2.2 and 2.2.3) prescribes a two-model structure: `DailyChat` (parent container) and `ChatMessage` (individual messages). The story's technical notes describe a simpler flat model with `greeting`, `mood`, `user_response`, `bot_reply` directly on the chat. **Follow the architecture document's two-model approach** because:

- It aligns with the documented data model that all future stories (005-010) will build upon
- The `ChatMessage` model with `order`, `sender`, and `message_type` is already prescribed and needed by Story-005 (mood selection) and Story-006 (reflection input)
- The API contract in Section 4.3 returns `messages: [...]` as a nested array, which the frontend types already define
- Building the flat model now would require a migration and rewrite when Story-005 arrives immediately after

This story only writes two ChatMessage rows per new chat (the greeting at order 0 and the mood_prompt at order 1), matching the architecture's prescribed MVP chat flow table (Section 2.2.3).

### Endpoint Design

Follow the architecture's `GET /api/chats/today/?date=YYYY-MM-DD` pattern (Section 4.3). This endpoint is idempotent: GET creates the chat if it does not exist, or returns the existing one. The `date` query parameter implements ADR-004 (client sends local date). The time-of-day for the greeting is determined server-side using the user's stored `timezone` field and the current UTC time.

### Service Layer

The architecture (Section 2.1) prescribes `api/services.py` for business logic. Create this module with a `get_or_create_today_chat()` function that encapsulates the get-or-create + greeting generation logic, keeping the view thin.

### Frontend Component Architecture

The architecture (Section 3.1, 3.5) prescribes these chat components: `ChatMessageList`, `ChatBubble`, `TypingIndicator`. For this story, `JournalPage` becomes the orchestrator that fetches the chat on mount and manages the typing indicator state. A `useChat` hook is not strictly needed yet (it becomes valuable when Story-005 adds interactivity), but introducing `services/chat.ts` sets up the service layer pattern.

---

## Task Breakdown

### Phase 1: Backend — Models and Migration

#### Task 1.1: Create DailyChat and ChatMessage Models

**What:** Add the `DailyChat` and `ChatMessage` models to `backend/api/models.py` following the architecture document's exact schema (Section 2.2.2 and 2.2.3).

**Why:** These are the foundational data models for the entire Journal feature. The `DailyChat` model has a unique constraint on `(user, date)` that enforces AC5 at the database level.

**Key details:**
- `DailyChat`: user (FK), date, mood (blank), summary (blank), status (default in_progress), started_at, completed_at
- `ChatMessage`: daily_chat (FK), sender, message_type, content, order, created_at
- UniqueConstraint on `(user, date)` named `one_chat_per_user_per_day`
- UniqueConstraint on `(daily_chat, order)` named `unique_message_order_per_chat`
- Choices enums: `MoodChoice`, `StatusChoice`, `SenderChoice`, `MessageType` as TextChoices classes

#### Task 1.2: Register Models in Admin

**What:** Add `DailyChat` and `ChatMessage` to `backend/api/admin.py`.

**Why:** Enables manual inspection and debugging of chat data during development.

#### Task 1.3: Generate and Apply Migration

**What:** Run `makemigrations` and `migrate` to create the new database tables.

### Phase 2: Backend — Service Layer, Serializers, View, URL

#### Task 2.1: Create Service Module with Greeting Logic

**What:** Create `backend/api/services.py` with `get_or_create_today_chat(user, local_date)`.

**Why:** The architecture prescribes keeping business logic in `services.py` rather than in views.

**Responsibilities:**
- Look up existing `DailyChat` for this user and date; return it if found (AC3, AC5)
- If not found, determine the time-of-day period from the user's timezone (AC1):
  - Convert current UTC time to user's local time using `zoneinfo.ZoneInfo`
  - Determine period: morning (5:00-11:59), afternoon (12:00-16:59), evening (17:00-4:59)
- Generate greeting using user's `display_name` (AC4): "Good [period], [Name]! How are you feeling today?"
- Create `DailyChat` + two `ChatMessage` rows (greeting at order 0, mood_prompt at order 1) in a transaction
- Handle race condition: catch `IntegrityError` on duplicate, return the existing chat

**Date validation:** Validate that the client-provided date is within +/- 1 day of the server-calculated date for the user's timezone, per ADR-004.

#### Task 2.2: Create Chat Serializers

**What:** Add `ChatMessageSerializer` and `DailyChatSerializer` to `backend/api/serializers.py`.

**Fields:**
- `ChatMessageSerializer`: id, sender, message_type, content, order, created_at (all read-only)
- `DailyChatSerializer`: id, date, mood, summary, status, started_at, completed_at, messages (nested, read-only)

#### Task 2.3: Create TodayChatView

**What:** Add `TodayChatView(APIView)` to `backend/api/views.py` with a `get()` method.

**Responsibilities (kept thin):**
- Extract `date` query parameter, validate format (YYYY-MM-DD)
- Call `services.get_or_create_today_chat(request.user, date_str)`
- Serialize and return the `DailyChat` with nested messages

**Permission:** `IsAuthenticated` (explicit on the view).

#### Task 2.4: Register URL Route

**What:** Add `path("chats/today/", TodayChatView.as_view(), name="chat-today")` to `backend/api/urls.py`.

### Phase 3: Frontend — Types, Service, Components

#### Task 3.1: Add Chat Types

**What:** Add `ChatMessage`, `DailyChat`, and `MoodChoice` interfaces to `frontend/src/types/api.ts`.

#### Task 3.2: Create Chat Service

**What:** Create `frontend/src/services/chat.ts` with `getTodayChat(localDate: string)`.

**Function:** Calls `GET /chats/today/?date=${localDate}` and returns a typed `DailyChat` response. The `localDate` is obtained from `new Date().toLocaleDateString('en-CA')` per ADR-004.

#### Task 3.3: Create TypingIndicator Component

**What:** Create `frontend/src/components/chat/TypingIndicator.tsx` and its CSS file.

**Details:**
- Three `<span className="dot" />` elements inside a container
- CSS animation: pulsing scale/opacity with staggered delays (0s, 0.2s, 0.4s)
- Wrapped in a bot-styled bubble (light grey background, left-aligned)
- Accessible: `aria-label="Clearness is typing"`

#### Task 3.4: Create ChatBubble Component

**What:** Create `frontend/src/components/chat/ChatBubble.tsx` and its CSS file.

**Details:**
- Props: `message: ChatMessage`
- Applies `.chat-bubble.bot` or `.chat-bubble.user` class based on `message.sender`
- Bot messages left-aligned with light-grey background; user messages right-aligned with primary color
- Styling: 78% max-width, 18px border-radius with 6px on tail corner, 12px 16px padding

#### Task 3.5: Create ChatMessageList Component

**What:** Create `frontend/src/components/chat/ChatMessageList.tsx`.

**Details:**
- Props: `messages: ChatMessage[]`, `isTyping: boolean`
- Maps messages to `<ChatBubble />` components
- If `isTyping`, appends `<TypingIndicator />` at bottom
- Auto-scroll-to-bottom via `bottomRef` + `useEffect`

#### Task 3.6: Rewrite JournalPage as Chat View

**What:** Transform the placeholder `frontend/src/pages/JournalPage.tsx` into the daily chat view.

**Behavior on mount:**
1. Compute local date via `new Date().toLocaleDateString('en-CA')`
2. Call `getTodayChat(localDate)` from the chat service
3. **If existing chat with user messages:** Render all messages immediately. No typing indicator.
4. **If new chat (only bot messages, no user messages):**
   - Set `isTyping = true`, show typing indicator in empty chat
   - After 1-1.5s delay, set `isTyping = false` and render the greeting messages
5. Loading and error states handled

**Layout:**
- Chat messages area fills available space (flex: 1, overflow-y: auto)
- No input bar (mood selector in Story-005, text input in Story-006)
- "Journal" header at top

---

## Testing Strategy

### Backend Tests

Add to `backend/api/tests.py`:

| Test | Covers |
|------|--------|
| `test_daily_chat_model_str` | Model string representation |
| `test_chat_message_model_str` | Model string representation |
| `test_one_chat_per_user_per_day_constraint` | AC5: IntegrityError on duplicate (user, date) |
| `test_today_chat_creates_new` | AC1, AC4: GET creates chat with greeting, returns 200 |
| `test_today_chat_returns_existing` | AC3, AC5: Second GET returns same chat |
| `test_today_chat_greeting_morning` | AC1: "Good morning" in greeting |
| `test_today_chat_greeting_afternoon` | AC1: "Good afternoon" in greeting |
| `test_today_chat_greeting_evening` | AC1: "Good evening" in greeting |
| `test_today_chat_greeting_contains_display_name` | AC4: Display name in greeting |
| `test_today_chat_messages_structure` | 2 messages: greeting (order 0) + mood_prompt (order 1) |
| `test_today_chat_unauthenticated` | 401 without auth token |
| `test_today_chat_missing_date_param` | 400 when date missing |
| `test_today_chat_invalid_date_format` | 400 when date is not YYYY-MM-DD |
| `test_today_chat_date_validation` | Date outside +/- 1 day tolerance returns 400 |

### Frontend Verification

- `npm run build` succeeds (TypeScript compiles cleanly)
- `npm run lint` passes (ESLint clean)

---

## Files Summary

### Backend (New/Modified)

| File | Action | Purpose |
|------|--------|---------|
| `backend/api/models.py` | Modify | Add DailyChat and ChatMessage models |
| `backend/api/services.py` | **New** | get_or_create_today_chat() business logic |
| `backend/api/serializers.py` | Modify | Add ChatMessageSerializer, DailyChatSerializer |
| `backend/api/views.py` | Modify | Add TodayChatView |
| `backend/api/urls.py` | Modify | Add chats/today/ route |
| `backend/api/admin.py` | Modify | Register DailyChat, ChatMessage |
| `backend/api/tests.py` | Modify | Add ~14 tests |
| `backend/api/migrations/0002_*.py` | **New** (auto) | Migration for new models |

### Frontend (New/Modified)

| File | Action | Purpose |
|------|--------|---------|
| `frontend/src/types/api.ts` | Modify | Add ChatMessage, DailyChat types |
| `frontend/src/services/chat.ts` | **New** | getTodayChat() API call |
| `frontend/src/components/chat/TypingIndicator.tsx` | **New** | Pulsing dots animation |
| `frontend/src/components/chat/TypingIndicator.css` | **New** | Typing indicator CSS |
| `frontend/src/components/chat/ChatBubble.tsx` | **New** | Message bubble component |
| `frontend/src/components/chat/ChatBubble.css` | **New** | Bubble styling |
| `frontend/src/components/chat/ChatMessageList.tsx` | **New** | Scrollable message list |
| `frontend/src/components/chat/ChatMessageList.css` | **New** | Message list layout |
| `frontend/src/pages/JournalPage.tsx` | Modify (rewrite) | Daily chat view |
| `frontend/src/pages/JournalPage.css` | **New** | Journal page layout |

---

## Key Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Race condition on concurrent chat creation | Wrap in try/except IntegrityError, retry with lookup. Unique constraint is the true guard. |
| Typing indicator delay feels artificial | Keep delay to 1-1.5s. Only show on genuinely new chats, not reloads. |
| Client date manipulation | Server validates date within +/- 1 day of server-calculated date for user's timezone. |

---

## Implementation Order

1. Tasks 1.1 → 1.2 → 1.3 (Models, admin, migration)
2. Tasks 2.1 → 2.2 → 2.3 → 2.4 (Service, serializers, view, URL)
3. Backend tests
4. Tasks 3.1 → 3.2 (Types, service — frontend data layer)
5. Tasks 3.3 → 3.4 → 3.5 → 3.6 (Components, page — frontend UI)
6. Frontend build/lint verification
7. Manual QA against all 5 acceptance criteria
