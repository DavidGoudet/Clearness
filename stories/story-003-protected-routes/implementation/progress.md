# Story-003 Implementation Progress

## Status: Complete

## Changes Made

### Backend
1. **`api/serializers.py`** — Added `LogoutSerializer` (validates `refresh` field)
2. **`api/views.py`** — Added `LogoutView` (POST /api/auth/logout/) that blacklists refresh token via simplejwt
3. **`api/urls.py`** — Registered `auth/logout/` route
4. **`api/tests.py`** — Added 4 tests: blacklist success, blacklisted token can't refresh, unauthenticated returns 401, missing body returns 400

### Frontend
5. **`components/layout/ProtectedRoute.tsx`** — Passes `state={{ from: location.pathname }}` when redirecting to `/login`
6. **`pages/LoginPage.tsx`** — Reads `location.state.from` and redirects there after login (defaults to `/journal`)
7. **`services/api.ts`** — Added `authExpiredEvent` (EventTarget); emits `expired` when 401 refresh fails
8. **`services/auth.ts`** — Added `logoutFromServer()` that calls POST /api/auth/logout/ (fire-and-forget)
9. **`hooks/AuthProvider.tsx`** — Logout calls `logoutFromServer()` before clearing; listens for `auth:expired` event to auto-logout

## Deviations from Plan
None.

## Test Results
- Backend: 22/22 tests pass (4 new)
- Frontend: TypeScript compiles cleanly, ESLint passes
