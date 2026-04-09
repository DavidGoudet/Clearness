# Epic 01 -- Authentication and Onboarding

**Priority:** Must Have (MVP)
**Estimated Effort:** M (Medium)
**Target Duration:** 4-6 weeks

---

## Description

Establish the foundational authentication layer that gates access to the Clearness application. Users must be able to sign in via Google OAuth 2.0 or Apple Sign-In before accessing any feature. On first login, the system creates a user profile automatically and persists a secure session so that returning users are not forced to re-authenticate on every visit.

This epic is the prerequisite for all other epics because every feature depends on knowing who the user is.

---

## Business Value

- Enables secure, passwordless authentication aligned with modern mobile UX expectations
- Removes friction from onboarding (no email/password forms, no email verification)
- Satisfies Apple App Store requirement for Apple Sign-In when third-party login is offered
- Creates the user identity that all other features (journal, calendar, profile) depend on

---

## Acceptance Criteria (Epic Level)

1. A new user can sign in with Google OAuth 2.0 and land on the Journal screen
2. A new user can sign in with Apple Sign-In and land on the Journal screen
3. On first sign-in, a user profile is automatically created with display name and avatar derived from the OAuth provider
4. A returning user with a valid session is taken directly to the Journal screen without re-authenticating
5. A user can sign out, which clears the session and returns them to the sign-in screen
6. Unauthenticated requests to any API endpoint return a 401 response
7. The sign-in screen follows the Clearness design system (light theme, teal-blue accent, Inter font, rounded corners)

---

## Child Story Candidates

| # | Story Title | Description | Size |
|---|-------------|-------------|------|
| 1 | Backend user model and auth foundation | Create the Django user model extensions (avatar, join_date, provider, provider_id) and configure Django REST Framework authentication classes | 3 |
| 2 | Google OAuth backend integration | Implement server-side Google OAuth 2.0 token verification and user-or-create logic; expose POST /api/auth/google/ endpoint | 5 |
| 3 | Apple Sign-In backend integration | Implement server-side Apple Sign-In token verification and user-or-create logic; expose POST /api/auth/apple/ endpoint | 5 |
| 4 | Session and token management | Implement JWT or session-based token issuance on successful OAuth, token refresh, and token revocation on sign-out | 3 |
| 5 | Sign-in screen UI | Build the sign-in screen with the Clearness branding, Google and Apple sign-in buttons, following the design system | 3 |
| 6 | Google Sign-In frontend flow | Integrate Google Identity Services SDK in React; handle the credential response and send it to the backend endpoint | 3 |
| 7 | Apple Sign-In frontend flow | Integrate Apple Sign-In JS SDK in React; handle the authorization response and send it to the backend endpoint | 3 |
| 8 | Automatic profile creation on first login | When a new OAuth user is verified, create their profile record with name and avatar from the provider payload | 2 |
| 9 | Protected route guard | Implement a React route guard that redirects unauthenticated users to the sign-in screen and allows authenticated users through | 2 |
| 10 | Sign-out flow | Implement sign-out button (in Profile tab), call token revocation endpoint, clear local state, redirect to sign-in screen | 2 |
| 11 | Session persistence on app reload | Store the auth token securely so that a browser refresh or app reopen does not require re-authentication | 2 |

**Total estimated story points:** ~33

---

## Dependencies

- None. This is the foundational epic.

---

## Risks and Considerations

- Apple Sign-In requires an Apple Developer account and specific entitlements configured in the Apple Developer portal
- OAuth callback URLs differ between local development, staging, and production; environment configuration must be handled early
- Token storage strategy must balance security (HttpOnly cookies or secure storage) with the mobile-first web context
- If the app is later deployed as a native mobile app, the OAuth flow may need adjustment (redirect URI vs. native SDK)

---

## Definition of Done

- All acceptance criteria are met
- Authentication endpoints have automated tests (unit and integration)
- The sign-in screen is responsive and follows the design system
- Security review confirms tokens are stored securely and sessions expire appropriately
