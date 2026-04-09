# Implementation Plan: Story-001 -- Sign in with Google OAuth

**Story Type:** Full-Stack | **Points:** 5 | **Branch:** `001-signin-google`

---

## User Story

As a new or returning user, I want to sign in to Clearness using my Google account, so that I can quickly access the app without creating a separate username and password.

## Acceptance Criteria

1. **AC1:** New user signs in with Google -> profile auto-created, JWT returned, redirect to Journal
2. **AC2:** Existing user signs in -> recognized, no duplicate, JWT returned, redirect to Journal
3. **AC3:** Invalid/expired Google token -> rejected, error message displayed
4. **AC4:** Google consent cancelled -> stay on sign-in screen, no error, can retry

---

## Phase 1: Backend Foundation

### Task 1.1: Custom User Model + AUTH_USER_MODEL

**Critical:** Set `AUTH_USER_MODEL = "api.User"` in settings.py BEFORE any migration.

- Define `User(AbstractUser)` in `api/models.py` with: `auth_provider`, `auth_provider_id`, `display_name`, `avatar_emoji`, `timezone`, `reminder_enabled`, `reminder_time`
- `USERNAME_FIELD = "email"`, UniqueConstraint on `(auth_provider, auth_provider_id)`
- Delete existing `0001_initial.py` migration, regenerate from scratch
- Register custom User in `admin.py` with `UserAdmin`

### Task 1.2: Backend Dependencies

Add to `requirements.txt`:
- `djangorestframework-simplejwt>=5.3,<6.0`
- `google-auth>=2.29,<3.0`
- `PyJWT[crypto]>=2.8,<3.0`
- `requests>=2.31,<3.0`

### Task 1.3: JWT + DRF Configuration

Update `settings.py`:
- Add `rest_framework_simplejwt` and `rest_framework_simplejwt.token_blacklist` to INSTALLED_APPS
- Set `JWTAuthentication` as default auth class, `IsAuthenticated` as default permission
- Add `SIMPLE_JWT` config (30-min access, 7-day rotating refresh, blacklist)
- Add `GOOGLE_CLIENT_ID` from environment variable

### Task 1.4: Google Token Verification

Create `api/authentication.py` with `verify_google_token()` using `google.oauth2.id_token.verify_oauth2_token()`.

### Task 1.5: GoogleAuthView

Add `GoogleAuthView(APIView)` to `api/views.py`:
1. Accept `{id_token}`, verify with `verify_google_token()`
2. Find-or-create User by `(auth_provider="google", auth_provider_id)`
3. Generate JWT pair via `RefreshToken.for_user(user)`
4. Return `{access, refresh, user}` on success, 401 on invalid token

Add serializers: `GoogleAuthSerializer` (validates id_token field), `UserSerializer` (user response).

### Task 1.6: Auth URL Routes

Add to `api/urls.py`:
- `auth/google/` -> `GoogleAuthView`
- `auth/refresh/` -> simplejwt `TokenRefreshView`

### Task 1.7: ProfileView (GET /api/me/)

Add `ProfileView(APIView)` with `IsAuthenticated` permission. Returns authenticated user's profile. Needed for frontend silent refresh flow.

### Task 1.8: Environment Configuration

Add `GOOGLE_CLIENT_ID` to `.env.example` and `docker-compose.yml`.

---

## Phase 2: Frontend Infrastructure

### Task 2.1: Frontend Dependencies

Install `react-router-dom` (v7) and `@react-oauth/google`.

### Task 2.2: Design Tokens + Global Styles

Create `styles/variables.css` with design tokens from mockup:
- Primary: `#2d8ab0`, text: `#1a1a1a`, subtitle: `#888`, border: `#ddd`
- Import Inter font
- Mobile-first base layout (375px max-width)

### Task 2.3: API Client with Auth Support

Replace existing `api.ts` with architecture-prescribed structure:
- `services/api.ts` -- `apiRequest<T>()` wrapper with Bearer token injection and 401 retry
- `services/auth.ts` -- `loginWithGoogle()`, `refreshAccessToken()`, `clearTokens()`

### Task 2.4: TypeScript Types

Create `types/api.ts` with `User`, `AuthResponse`, `TokenRefreshResponse` interfaces.

### Task 2.5: AuthProvider + useAuth Hook

Create `hooks/useAuth.tsx`:
- Silent refresh on mount (check localStorage for refresh token)
- Expose `login()`, `logout()`, `user`, `isLoading`, `isAuthenticated`
- Access token in-memory, refresh token in localStorage

### Task 2.6: ProtectedRoute

Create `components/layout/ProtectedRoute.tsx`:
- Show loading while `isLoading`
- Redirect to `/login` if not authenticated
- Render `<Outlet />` with `<BottomNav />` if authenticated

### Task 2.7: React Router Setup

Restructure `App.tsx` and `main.tsx`:
- `/login` -> LoginPage
- Protected: `/journal`, `/calendar`, `/profile` (placeholder pages)
- Catch-all -> redirect to `/journal`
- Wrap in `<AuthProvider>`

---

## Phase 3: Login Page + Google Integration

### Task 3.1: LoginPage Component

Create `pages/LoginPage.tsx` matching mockup:
- Diamond emoji logo, "Clearness" title, tagline
- "Continue with Google" button (white bg, #ddd border)
- "Continue with Apple" button (black bg) -- rendered but disabled
- Terms links at bottom
- Auto-redirect if already authenticated

### Task 3.2: Google Identity Services Integration

- Wrap app with `GoogleOAuthProvider` using `VITE_GOOGLE_CLIENT_ID`
- Use `useGoogleLogin()` for consent popup
- On success: call `useAuth().login("google", credential)`, navigate to `/journal`
- On cancel: do nothing (AC4)
- On error: show "Sign-in failed. Please try again." (AC3)

### Task 3.3: Placeholder Authenticated Pages

Create minimal `JournalPage.tsx`, `CalendarPage.tsx`, `ProfilePage.tsx` with placeholder content.

### Task 3.4: BottomNav Component

Create `components/layout/BottomNav.tsx` with Journal/Calendar/Profile tabs using `NavLink`.

### Task 3.5: Vite Environment Config

Add `VITE_GOOGLE_CLIENT_ID` environment variable support.

---

## Testing Strategy

### Backend Tests (Django TestCase / APITestCase)

| Test | Covers |
|------|--------|
| `test_google_auth_new_user` | AC1: Mock verify, POST /api/auth/google/, assert user created + JWT returned |
| `test_google_auth_existing_user` | AC2: Pre-create user, POST, assert no duplicate, same user |
| `test_google_auth_invalid_token` | AC3: Mock verify raises ValueError, assert 401 |
| `test_google_auth_missing_token` | Validation: POST with empty body, assert 400 |
| `test_profile_authenticated` | GET /api/me/ with JWT, assert 200 + user data |
| `test_profile_unauthenticated` | GET /api/me/ without auth, assert 401 |
| `test_token_refresh` | POST /api/auth/refresh/ with valid refresh token, assert new access token |
| `test_user_unique_constraint` | Duplicate (provider, provider_id), assert IntegrityError |

### Manual QA Checklist

- [ ] New Google user signs in -> profile created, lands on /journal
- [ ] Same user signs in again -> no duplicate, lands on /journal
- [ ] Invalid token sent -> error message shown
- [ ] Cancel Google popup -> stay on login, no error
- [ ] Refresh page while authenticated -> silent refresh, stay on /journal
- [ ] Refresh with expired refresh token -> redirect to /login
- [ ] Visit /journal unauthenticated -> redirect to /login
- [ ] Visit /login while authenticated -> redirect to /journal

---

## PR Strategy

**Single PR** on branch `001-signin-google` -> `main`. The story is atomic (backend alone is not user-facing), and keeping it as one PR ensures the auth feature ships as a complete unit.

---

## Prerequisites (Before Coding)

1. **Google Cloud Project:** Create OAuth 2.0 Client ID (Web app), add `http://localhost:5173` as authorized JavaScript origin
2. **PostgreSQL:** Ensure database is accessible for migrations
3. **Branch:** Work on existing `001-signin-google` branch

---

## Files Summary

### Backend (New/Modified)

| File | Action |
|------|--------|
| `backend/clearness/settings.py` | Modify: AUTH_USER_MODEL, SIMPLE_JWT, GOOGLE_CLIENT_ID, INSTALLED_APPS, REST_FRAMEWORK |
| `backend/api/models.py` | Modify: Add User model (keep Item) |
| `backend/api/authentication.py` | New: verify_google_token() |
| `backend/api/views.py` | Modify: Add GoogleAuthView, ProfileView |
| `backend/api/serializers.py` | Modify: Add GoogleAuthSerializer, UserSerializer |
| `backend/api/urls.py` | Modify: Add auth + profile routes |
| `backend/api/admin.py` | Modify: Register custom User |
| `backend/api/migrations/` | Reset: Delete old, regenerate |
| `backend/requirements.txt` | Modify: Add 4 dependencies |
| `.env.example` | Modify: Add GOOGLE_CLIENT_ID |

### Frontend (New/Modified)

| File | Action |
|------|--------|
| `frontend/src/services/api.ts` | New: authenticated fetch wrapper |
| `frontend/src/services/auth.ts` | New: login, refresh, logout functions |
| `frontend/src/types/api.ts` | New: User, AuthResponse types |
| `frontend/src/hooks/useAuth.tsx` | New: AuthProvider + useAuth |
| `frontend/src/pages/LoginPage.tsx` | New: sign-in UI |
| `frontend/src/pages/JournalPage.tsx` | New: placeholder |
| `frontend/src/pages/CalendarPage.tsx` | New: placeholder |
| `frontend/src/pages/ProfilePage.tsx` | New: placeholder |
| `frontend/src/components/layout/ProtectedRoute.tsx` | New: auth guard |
| `frontend/src/components/layout/BottomNav.tsx` | New: tab nav |
| `frontend/src/styles/variables.css` | New: design tokens |
| `frontend/src/App.tsx` | Rewrite: router + AuthProvider |
| `frontend/src/main.tsx` | Modify: import global styles |
| `frontend/src/api.ts` | Delete: replaced by services/api.ts |
| `frontend/package.json` | Modify: add 2 dependencies |

---

## Key Risks

| Risk | Mitigation |
|------|------------|
| AUTH_USER_MODEL after migrations | Task 1.1 deletes old migration first. Must be the very first change. |
| Google Cloud project not set up | Prerequisite: create OAuth credentials before coding |
| Existing Item API tests break | Keep ItemViewSet with explicit `permission_classes = [AllowAny]` |
| Login page flicker on refresh | AuthProvider shows loading state until refresh attempt completes |
