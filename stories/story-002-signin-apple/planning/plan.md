# Implementation Plan: Story-002 -- Sign in with Apple Sign-In

**Story Type:** Full-Stack | **Points:** 5 | **Branch:** `001-signin-google` (building on story-001)

---

## User Story

As a new or returning user, I want to sign in to Clearness using my Apple account so that I can access the app using my preferred identity provider without creating a separate account.

## Acceptance Criteria

1. **AC1:** New user signs in with Apple -> profile created (with Apple-provided name and relay email), JWT returned, redirect to Journal
2. **AC2:** Existing user signs in -> recognized by Apple `sub`, no duplicate, JWT returned, redirect to Journal
3. **AC3:** User chooses "Hide My Email" -> relay email stored normally, profile created successfully
4. **AC4:** Invalid/expired Apple identity token -> rejected, error message displayed
5. **AC5:** Apple consent cancelled -> stay on sign-in screen, no error, can retry

---

## What Already Exists (from Story-001)

- Custom User model with `auth_provider` (google/apple), `auth_provider_id`, `display_name`, `email`
- JWT infrastructure (simplejwt, token refresh, blacklist)
- `GoogleAuthView` pattern to follow for `AppleAuthView`
- AuthProvider with `login(provider, token)` that already accepts `"apple"` as provider type
- LoginPage with disabled Apple button (just needs enabling)
- API client with auth headers and token refresh
- Backend dependencies already installed: `PyJWT[crypto]`, `requests`

## Key Apple-Specific Considerations

1. **Name only on first sign-in:** Apple sends the user's name ONLY during the first authorization. The frontend must capture and forward it to the backend, which must persist it immediately.
2. **Relay email ("Hide My Email"):** Apple may provide a private relay email (e.g., `abc@privaterelay.appleid.com`). Treat as a normal email -- no special handling needed.
3. **Token verification via JWKS:** Apple signs identity tokens with RS256. Verify using Apple's public keys from `https://appleid.apple.com/auth/keys`.
4. **No new backend dependencies needed:** PyJWT and requests are already installed.

---

## Phase 1: Backend

### Task 1.1: Add APPLE_CLIENT_ID to Settings

Add `APPLE_CLIENT_ID = os.environ.get("APPLE_CLIENT_ID", "")` to `settings.py`.
Update `.env.example` and `docker-compose.yml`.

### Task 1.2: Implement verify_apple_token()

Add to `backend/api/authentication.py`:
- Fetch Apple's JWKS from `https://appleid.apple.com/auth/keys`
- Find the matching key by `kid` header
- Decode and verify the identity token with RS256, audience=APPLE_CLIENT_ID, issuer=`https://appleid.apple.com`
- Return `{email, provider_id}` (name comes from frontend, not from token)
- Raise `ValueError` on invalid/expired tokens or key mismatch

### Task 1.3: Add AppleAuthSerializer

Add to `serializers.py`:
- `identity_token` field (required)
- `user_name` field (optional, string) -- Apple sends name only on first auth

### Task 1.4: Implement AppleAuthView

Add to `views.py` following GoogleAuthView pattern:
- `POST /api/auth/apple/` with `AllowAny`
- Validate with `AppleAuthSerializer`
- Call `verify_apple_token()`
- `get_or_create` User with `auth_provider="apple"`, `auth_provider_id=provider_id`
- On create: set email from token, display_name from `user_name` field (fallback to email prefix)
- Generate and return JWT pair + user data
- On `ValueError`: return 401

### Task 1.5: Add URL Route

Add `path("auth/apple/", AppleAuthView.as_view(), name="auth-apple")` to `urls.py`.

### Task 1.6: Backend Tests

Add tests mirroring the Google auth tests:
- `test_apple_auth_new_user` -- mock verify, POST, assert user created with name and email (AC1)
- `test_apple_auth_existing_user` -- pre-create user, assert no duplicate (AC2)
- `test_apple_auth_hide_my_email` -- relay email stored correctly (AC3)
- `test_apple_auth_invalid_token` -- mock raises ValueError, assert 401 (AC4)
- `test_apple_auth_missing_token` -- empty body, assert 400
- `test_apple_auth_no_name_provided` -- name fallback to email prefix

---

## Phase 2: Frontend

### Task 2.1: Add Frontend Dependency

Install `react-apple-signin-auth` for Apple Sign-In JS SDK React wrapper.

### Task 2.2: Add loginWithApple() Service

Add to `services/auth.ts`:
- `loginWithApple(identityToken, userName?)` -> POST `/api/auth/apple/`

### Task 2.3: Update AuthProvider

Update `AuthProvider.tsx` login function to handle `provider === "apple"`:
- Call `loginWithApple(token, userName)`, store tokens, set user

### Task 2.4: Enable Apple Button on LoginPage

Update `LoginPage.tsx`:
- Remove `disabled` and reduced opacity from Apple button
- Integrate Apple Sign-In flow using `react-apple-signin-auth`
- On success: extract `authorization.id_token` and optional `user.name`, call `login("apple", token)`
- On cancel: do nothing (AC5)
- On error: show "Sign-in failed. Please try again." (AC4)

### Task 2.5: Update LoginPage Styles

Update `LoginPage.css`:
- Remove disabled styling from Apple button
- Add active/hover state for Apple button

### Task 2.6: Vite Environment Config

Add `VITE_APPLE_CLIENT_ID` to `frontend/.env` and type declarations.

---

## Testing Strategy

### Backend Tests (Django APITestCase)

| Test | Covers |
|------|--------|
| `test_apple_auth_new_user` | AC1: Mock verify, POST, user created with name |
| `test_apple_auth_existing_user` | AC2: Pre-create user, no duplicate |
| `test_apple_auth_hide_my_email` | AC3: Relay email stored correctly |
| `test_apple_auth_invalid_token` | AC4: Mock raises ValueError, assert 401 |
| `test_apple_auth_missing_token` | Validation: empty body, assert 400 |
| `test_apple_auth_no_name` | Fallback: display_name defaults to email prefix |

### Manual QA Checklist

- [ ] New Apple user signs in -> profile created, lands on /journal
- [ ] Same user signs in again -> no duplicate, lands on /journal
- [ ] "Hide My Email" relay address accepted and stored
- [ ] Invalid token -> error message shown
- [ ] Cancel Apple popup -> stay on login, no error
- [ ] Google sign-in still works (regression)

---

## PR Strategy

**Single PR** continuing on `001-signin-google` branch (both auth stories ship together as a cohesive auth feature).

---

## Files Summary

### Backend (Modified)

| File | Action |
|------|--------|
| `backend/clearness/settings.py` | Add APPLE_CLIENT_ID |
| `backend/api/authentication.py` | Add verify_apple_token() |
| `backend/api/serializers.py` | Add AppleAuthSerializer |
| `backend/api/views.py` | Add AppleAuthView |
| `backend/api/urls.py` | Add auth/apple/ route |
| `backend/api/tests.py` | Add 6 Apple auth tests |
| `.env.example` | Add APPLE_CLIENT_ID |
| `docker-compose.yml` | Add APPLE_CLIENT_ID to backend env |

### Frontend (Modified)

| File | Action |
|------|--------|
| `frontend/src/services/auth.ts` | Add loginWithApple() |
| `frontend/src/hooks/AuthProvider.tsx` | Handle apple provider in login() |
| `frontend/src/pages/LoginPage.tsx` | Enable Apple button, integrate Apple SDK |
| `frontend/src/pages/LoginPage.css` | Update Apple button styles |
| `frontend/.env` | Add VITE_APPLE_CLIENT_ID |
| `frontend/src/vite-env.d.ts` | Add VITE_APPLE_CLIENT_ID type |
| `frontend/package.json` | Add react-apple-signin-auth |

---

## Key Risks

| Risk | Mitigation |
|------|------------|
| Apple Dev account not configured | Prerequisite: need Apple Service ID configured for web domain |
| Apple name only on first sign-in | Frontend captures and sends name; backend persists immediately |
| JWKS key rotation by Apple | Fetch keys on each verification (no caching for MVP) |
| Google sign-in regression | Existing Google tests run alongside new Apple tests |
