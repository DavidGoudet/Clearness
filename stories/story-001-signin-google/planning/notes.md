# Planning Notes: Story-001

## Context Gathered

- **Story source:** `/discovery/stories/story-001.md`
- **Architecture:** `/discovery/architecture.md` v1.1 -- comprehensive, covers auth flow, data models, JWT config, frontend structure
- **UI Design:** `/mockup.html` -- login screen with "Continue with Google" and "Continue with Apple" buttons
- **Current branch:** `001-signin-google` (clean)

## Architecture Decisions (Pre-decided)

All auth architecture decisions are already documented in `architecture.md`:
- JWT over sessions (ADR-001)
- Custom User extending AbstractUser
- google-auth for server-side token verification
- djangorestframework-simplejwt for JWT management
- React Context for auth state (no Redux/Zustand needed)
- React Router v7 for routing
- @react-oauth/google for GIS SDK integration

No architect consultation was needed -- all decisions are documented and approved.

## Scope Boundaries

**This story (001):** Google OAuth only
**Next story:** Apple Sign-In (separate story, separate SDK)
**Out of scope:** DailyChat/ChatMessage models, Journal UI, Calendar UI, Profile UI, LLM integration

## Design Tokens (from mockup)

- Primary teal: `#2d8ab0`
- Text: `#1a1a1a`
- Subtitle/muted: `#888`
- Border: `#ddd`
- Background: `#fff`
- Bot bubble bg: `#f2f3f5`
- Font: Inter (200, 300, 400, 500, 600)
- Logo: 💎 emoji (64px)
- Button radius: 14px
- Phone frame: 375px width (mobile-first)
