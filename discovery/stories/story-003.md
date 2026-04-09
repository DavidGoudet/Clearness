# Story 003: Protected Routes and Session Persistence

**Epic:** Epic 01 — Authentication & Onboarding
**Priority:** High
**Story Points:** 3
**Status:** Draft

---

## User Story

**As an** authenticated user
**I want to** remain signed in across page refreshes and be redirected to sign-in if my session expires
**So that** I have a seamless experience without repeated logins while my data stays secure from unauthorized access

---

## Acceptance Criteria

### AC1: Unauthenticated user redirected to sign-in
**Given** a user who is not signed in (no valid token stored)
**When** they attempt to navigate to any protected route (Journal, Calendar, or Profile)
**Then** they are redirected to the sign-in screen and the originally requested route is preserved so they can be redirected after successful sign-in

### AC2: Session persists across page refresh
**Given** a user who is currently signed in with a valid session token
**When** they refresh the browser page or close and reopen the tab
**Then** the token is retrieved from secure storage, validated, and the user remains signed in without needing to re-authenticate

### AC3: Sign-out clears session
**Given** a user who is currently signed in
**When** they tap the "Sign out" button on the Profile screen
**Then** the authentication token is removed from storage, any in-memory auth state is cleared, and the user is redirected to the sign-in screen

### AC4: Expired or invalid token triggers re-authentication
**Given** a user whose authentication token has expired or become invalid
**When** any API request is made and the backend returns a 401 Unauthorized response
**Then** the frontend clears the stored token, redirects the user to the sign-in screen, and does not display the protected content

---

## Technical Notes

- Implement a React route guard component (e.g., `ProtectedRoute`) that checks for a valid auth token before rendering child routes
- Store the authentication token in an httpOnly cookie (preferred) or secure localStorage
- On app initialization, check for an existing token and validate it against a lightweight backend endpoint such as `GET /api/auth/verify/`
- Sign-out action: clear token from storage and reset the React auth context/state
- Add an Axios/fetch interceptor to catch 401 responses globally and trigger the re-authentication flow
- Protected routes: `/journal`, `/calendar`, `/profile`; public route: `/sign-in`

---

## Dependencies

- Requires Story 001 (Google OAuth) or Story 002 (Apple Sign-In) to be completed so that authentication tokens exist to manage

---

## INVEST Checklist

- [x] **Independent** — Focuses solely on route protection and session lifecycle; does not include sign-in UI or provider-specific logic
- [x] **Negotiable** — Token storage mechanism (cookie vs. localStorage), redirect behavior, and token refresh strategy can be discussed
- [x] **Valuable** — Protects user data from unauthorized access and provides session continuity for a seamless experience
- [x] **Estimable** — Route guards and token management are well-understood frontend patterns; 3 points reflects moderate frontend work with a small backend verification endpoint
- [x] **Small** — Scoped to route protection, token persistence, sign-out, and 401 handling; no sign-in provider logic included
- [x] **Testable** — Each criterion can be verified by simulating unauthenticated access, page refreshes, sign-out actions, and expired tokens
