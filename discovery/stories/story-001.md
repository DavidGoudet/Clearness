# Story 001: Sign in with Google OAuth

**Epic:** Epic 01 — Authentication & Onboarding
**Priority:** High
**Story Points:** 5
**Status:** Draft

---

## User Story

**As a** new or returning user
**I want to** sign in to Clearness using my Google account
**So that** I can quickly access the app without creating a separate username and password

---

## Acceptance Criteria

### AC1: Successful Google sign-in for a new user
**Given** a user who has never signed into Clearness before
**When** they tap the "Sign in with Google" button and complete the Google consent flow
**Then** a new Clearness user profile is auto-created with their Google display name, email, and avatar URL, a valid session token is returned, and they are redirected to the Journal tab

### AC2: Successful Google sign-in for an existing user
**Given** a user who has previously signed in with Google
**When** they tap "Sign in with Google" and complete the consent flow
**Then** their existing Clearness account is recognized, no duplicate profile is created, a valid session token is returned, and they are redirected to the Journal tab

### AC3: Invalid or expired Google token
**Given** a user attempting to sign in with Google
**When** the backend receives an invalid or expired Google ID token
**Then** the sign-in is rejected, no user profile is created or modified, and the frontend displays a user-friendly error message such as "Sign-in failed. Please try again."

### AC4: Google consent flow cancelled
**Given** a user on the sign-in screen
**When** they initiate the Google sign-in flow but cancel or dismiss the Google consent popup
**Then** they remain on the sign-in screen with no error message and can retry

---

## Technical Notes

- Backend endpoint: `POST /api/auth/google/` — accepts a Google ID token, verifies it against Google's token verification API, creates or retrieves the user, and returns a JWT or session token
- Frontend: integrate Google Identity Services SDK to obtain the credential response containing the ID token
- Store the returned authentication token securely (httpOnly cookie or secure localStorage) for session persistence
- User model fields populated from Google: `display_name`, `email`, `avatar_url`, `auth_provider="google"`, `provider_id`
- Django: use `google-auth` library for server-side token verification

---

## Dependencies

- None — this is a foundational story

---

## INVEST Checklist

- [x] **Independent** — Can be developed and delivered without depending on other stories; Apple sign-in is a separate story
- [x] **Negotiable** — The specific OAuth library, token storage strategy, and UI layout for the sign-in button can be adjusted during implementation
- [x] **Valuable** — Enables users to access the app, which is a prerequisite for all other functionality
- [x] **Estimable** — Google OAuth is a well-understood pattern with clear scope; 5 points reflects full-stack work with third-party integration
- [x] **Small** — Scoped to Google sign-in only; no session management, route guards, or Apple sign-in included
- [x] **Testable** — Each acceptance criterion can be verified through integration tests and manual QA with real and mock Google tokens
