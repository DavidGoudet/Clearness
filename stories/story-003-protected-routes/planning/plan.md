# Story-003: Protected Routes and Session Persistence — Implementation Plan

## Overview

Extend the existing authentication infrastructure to close four gaps: return-URL preservation on redirect, server-side token blacklisting on sign-out, and global 401 handling when token refresh fails mid-session. Session persistence on page refresh (AC2) is already fully working.

**Story Type:** Full-Stack
**Branch:** `003-protected-routes` (from `001-signin-google`)
**Single PR** — changes are small and tightly coupled.

---

## Task Breakdown

### Task 1 — Backend: Add Logout Endpoint (AC3)

**What:** Create `POST /api/auth/logout/` that blacklists the refresh token server-side.

**Approach:**
- New `LogoutView` in `api/views.py` — accepts `{ "refresh": "<token>" }`, calls `token.blacklist()` via simplejwt's built-in blacklist support (already enabled in settings).
- New `LogoutSerializer` in `api/serializers.py` — validates the refresh token field.
- Register route in `api/urls.py`.
- Requires authentication (`IsAuthenticated`).

**Why:** Currently sign-out only clears client-side state. A stolen refresh token would remain valid until natural expiry (7 days). Server-side blacklisting closes this gap.

### Task 2 — Frontend: Preserve Return URL on Redirect (AC1)

**What:** When `ProtectedRoute` redirects to `/login`, pass the originally requested path. After successful login, redirect back to that path instead of always going to `/journal`.

**Approach:**
- `ProtectedRoute.tsx` — pass `state={{ from: location.pathname }}` in the `<Navigate>` to `/login`.
- `LoginPage.tsx` — read `location.state?.from` and navigate there (defaulting to `/journal`) after successful login.

### Task 3 — Frontend: Global 401 Handling After Refresh Failure (AC4)

**What:** When an API request gets 401 AND the automatic token refresh also fails, clear auth state and redirect to login.

**Approach:**
- Add an event-based mechanism: `api.ts` emits an `auth:expired` event when refresh fails on 401 retry.
- `AuthProvider.tsx` listens for this event and calls `logout()`, which clears tokens and sets `user` to `null`.
- `ProtectedRoute` already handles the redirect when `isAuthenticated` becomes `false`.

**Why event-based:** Avoids coupling the API layer to React Router or auth context directly. Clean separation of concerns.

### Task 4 — Frontend: Call Backend Logout on Sign-Out (AC3)

**What:** Update the `logout()` flow to call `POST /api/auth/logout/` before clearing client-side state.

**Approach:**
- Add `logoutFromServer()` in `services/auth.ts` that posts the refresh token to `/api/auth/logout/`.
- Update `AuthProvider.logout()` to call this (fire-and-forget — don't block on failure since we still want client-side cleanup to succeed).

### Task 5 — Tests

**Backend tests:**
- Logout endpoint returns 200 and blacklists token
- Blacklisted refresh token cannot be used to get new access token
- Logout without auth returns 401

**Frontend considerations:**
- No frontend test framework is currently set up — skip frontend unit tests for now. Manual verification against ACs.

---

## Files Modified

| File | Change |
|------|--------|
| `backend/api/views.py` | Add `LogoutView` |
| `backend/api/serializers.py` | Add `LogoutSerializer` |
| `backend/api/urls.py` | Add `auth/logout/` route |
| `backend/api/tests.py` | Add logout endpoint tests |
| `frontend/src/components/layout/ProtectedRoute.tsx` | Pass return URL in Navigate state |
| `frontend/src/pages/LoginPage.tsx` | Read return URL, redirect after login |
| `frontend/src/services/api.ts` | Emit `auth:expired` event on refresh failure |
| `frontend/src/services/auth.ts` | Add `logoutFromServer()` |
| `frontend/src/hooks/AuthProvider.tsx` | Listen for `auth:expired`, call server logout |

---

## Testing Strategy

1. **Backend unit tests** for logout endpoint (Task 5)
2. **Manual E2E verification:**
   - Visit `/journal` when logged out → redirected to `/login` → log in → returned to `/journal`
   - Visit `/profile` when logged out → redirected to `/login` → log in → returned to `/profile`
   - Refresh page while logged in → stays logged in
   - Sign out → tokens cleared, redirected to `/login`, refresh token blacklisted
   - Simulate expired token (manually clear access token) → next API call triggers refresh → works transparently
   - Simulate expired refresh token → redirected to `/login`

---

## Acceptance Criteria Mapping

| AC | Covered By |
|----|-----------|
| AC1: Redirect + preserve return URL | Task 2 |
| AC2: Session persists across refresh | Already working (no changes needed) |
| AC3: Sign-out clears session fully | Tasks 1 + 4 |
| AC4: Expired token triggers re-auth | Task 3 |
