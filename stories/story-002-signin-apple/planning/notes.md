# Planning Notes: Story-002

## Context

- **Story source:** `/discovery/stories/story-002.md`
- **Architecture:** `/discovery/architecture.md` section 2.4.3 -- Apple Sign-In verification
- **UI Design:** Apple button already in `/mockup.html` and stub in `LoginPage.tsx`
- **Current branch:** `001-signin-google` (building on uncommitted story-001 changes)

## Architecture Decisions (Pre-decided)

From architecture.md section 2.4.3:
- Apple identity token verified via JWKS (Apple's public keys endpoint)
- PyJWT for JWT decoding with RS256
- Same User model / JWT pattern as Google auth
- No new backend dependencies needed

## Scope

**This story (002):** Apple Sign-In only
**Builds on:** Story-001 (Google OAuth) - same User model, JWT infrastructure, LoginPage
**No architect consultation needed:** follows established OAuth pattern from story-001
