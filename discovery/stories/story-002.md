# Story 002: Sign in with Apple Sign-In

**Epic:** Epic 01 — Authentication & Onboarding
**Priority:** High
**Story Points:** 5
**Status:** Draft

---

## User Story

**As a** new or returning user
**I want to** sign in to Clearness using my Apple account
**So that** I can access the app using my preferred identity provider without creating a separate account

---

## Acceptance Criteria

### AC1: Successful Apple sign-in for a new user
**Given** a user who has never signed into Clearness before
**When** they tap the "Sign in with Apple" button and complete the Apple authentication flow
**Then** a new Clearness user profile is created with their Apple-provided name and email (or relay email if "Hide My Email" is selected), a valid session token is returned, and they are redirected to the Journal tab

### AC2: Successful Apple sign-in for an existing user
**Given** a user who has previously signed in with Apple
**When** they tap "Sign in with Apple" and complete the authentication flow
**Then** their existing Clearness account is recognized by the Apple `sub` identifier, no duplicate profile is created, a valid session token is returned, and they are redirected to the Journal tab

### AC3: User chooses "Hide My Email"
**Given** a new user going through Apple sign-in
**When** they select the "Hide My Email" option in Apple's consent sheet
**Then** the app stores the Apple private relay email address as their contact email and the user profile is created successfully with all other fields populated normally

### AC4: Invalid or expired Apple identity token
**Given** a user attempting to sign in with Apple
**When** the backend receives an invalid or expired Apple identity token
**Then** the sign-in is rejected, no user profile is created or modified, and the frontend displays a user-friendly error message such as "Sign-in failed. Please try again."

### AC5: Apple consent flow cancelled
**Given** a user on the sign-in screen
**When** they initiate the Apple sign-in flow but cancel or dismiss the Apple consent sheet
**Then** they remain on the sign-in screen with no error message and can retry

---

## Technical Notes

- Backend endpoint: `POST /api/auth/apple/` — accepts an Apple identity token and authorization code, verifies the token against Apple's public keys (JWKS endpoint), creates or retrieves the user, and returns a JWT or session token
- Frontend: integrate Apple Sign-In JS SDK; configure the service ID and redirect URI
- Apple only sends the user's name and email on the first sign-in; the backend must persist these values immediately since they will not be provided again
- Match returning users by the `sub` claim in the Apple identity token, stored as `provider_id`
- User model fields: `display_name`, `email` (may be relay), `auth_provider="apple"`, `provider_id`
- Django: use `PyJWT` with Apple's JWKS for server-side token verification

---

## Dependencies

- None — this is a foundational story; can be developed in parallel with Story 001 (Google OAuth)

---

## INVEST Checklist

- [x] **Independent** — Can be developed and delivered without depending on Google OAuth or other stories
- [x] **Negotiable** — The specific JWT verification approach, token storage strategy, and sign-in button placement can be adjusted
- [x] **Valuable** — Provides an alternative sign-in method required for App Store compliance and user choice
- [x] **Estimable** — Apple Sign-In is a well-documented pattern; 5 points reflects full-stack work with Apple-specific nuances (relay email, one-time name delivery)
- [x] **Small** — Scoped to Apple sign-in only; no session management, route guards, or Google sign-in included
- [x] **Testable** — Each acceptance criterion can be verified through integration tests, including edge cases for "Hide My Email" and token validation
