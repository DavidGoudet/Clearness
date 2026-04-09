# Epic 04 -- Profile and Account Management

**Priority:** Should Have (MVP)
**Estimated Effort:** M (Medium)
**Target Duration:** 4-6 weeks

---

## Description

Build the Profile tab that displays the user's identity, journey statistics, and account settings. The profile screen shows the user's avatar and name, a 2x2 stats dashboard (total chats, current streak, most frequent mood, longest streak), and settings for daily reminders and privacy management. This epic also includes account deletion functionality, which is required for GDPR/CCPA compliance.

---

## Business Value

- Journey stats (streaks, totals) create a gamification loop that reinforces the daily journaling habit
- Streak visibility directly supports the D7 and D30 retention targets (45% and 25% respectively)
- Daily reminder settings give users control over push notification timing, reducing uninstalls due to unwanted notifications
- Account deletion and privacy settings are regulatory requirements (GDPR, CCPA) and build user trust in a privacy-sensitive domain
- The profile screen rounds out the three-tab navigation, making the app feel complete

---

## Acceptance Criteria (Epic Level)

1. The Profile tab displays the user's avatar (from OAuth or emoji-based), display name, and membership date
2. A 2x2 journey stats grid shows: total chats completed, current streak (consecutive days), most frequent mood (with emoji), and longest streak
3. Stats are calculated from actual chat data and update when new chats are completed
4. The user can configure a daily reminder time for check-in notifications
5. The user can view their privacy settings, including end-to-end encryption status
6. The user can delete their account and all associated data with a confirmation step
7. After account deletion, the user is signed out and returned to the sign-in screen
8. The UI follows the Clearness design system and is usable on mobile viewports

---

## Child Story Candidates

| # | Story Title | Description | Size |
|---|-------------|-------------|------|
| 1 | Profile display component | Build the profile header showing avatar, display name, and "Member since [date]" label, sourced from the user profile API | 2 |
| 2 | User profile API endpoint | Create GET /api/profile/ endpoint returning the authenticated user's name, avatar, join_date, and settings | 2 |
| 3 | Journey stats calculation backend | Implement a service or query set that computes: total completed chats, current streak, longest streak, and most frequent mood for a given user | 5 |
| 4 | Journey stats API endpoint | Create GET /api/profile/stats/ endpoint that returns the four computed stats | 2 |
| 5 | Journey stats dashboard UI | Build the 2x2 grid component that displays the four stats with labels, values, and the mood emoji for "most frequent mood" | 3 |
| 6 | Edit display name | Allow the user to tap their display name, enter a new one, and save it via PATCH /api/profile/ | 2 |
| 7 | Edit avatar | Allow the user to choose from a set of emoji-based avatars or upload a custom image, and save via PATCH /api/profile/ | 3 |
| 8 | Daily reminder settings | Build a settings row where the user can enable/disable a daily reminder and select a preferred time; persist the preference via API | 3 |
| 9 | Push notification scheduling | Integrate with a push notification service to schedule or cancel daily reminders based on the user's saved preference | 5 |
| 10 | Privacy settings display | Show the current encryption status and a link to the privacy policy; include a "Download my data" option placeholder for future implementation | 2 |
| 11 | Account deletion flow | Build a "Delete account" button with a confirmation dialog; on confirm, call DELETE /api/profile/ which removes all user data and revokes the session | 3 |
| 12 | Account deletion backend | Implement DELETE /api/profile/ that permanently removes the user record, all chats, and all associated data; returns 204 on success | 3 |

**Total estimated story points:** ~35

---

## Dependencies

| Epic | Dependency Type | Detail |
|------|----------------|--------|
| Epic 01 -- Authentication and Onboarding | Hard | User must be authenticated; profile is created during onboarding; sign-out is triggered after account deletion |
| Epic 02 -- Journal: Daily Reflection Chat | Hard | Journey stats (total chats, streaks, frequent mood) are computed from chat data; without chats, stats are all zero |

---

## Risks and Considerations

- Streak calculation logic must handle timezone differences consistently with Epic 02's date handling
- Account deletion must be truly permanent and comprehensive to satisfy GDPR "right to erasure"; this includes backups and any cached data
- Push notification integration depends on the deployment context: browser Push API for web, or native push for a future mobile app; scope for MVP should be clarified
- The "Download my data" feature (GDPR data portability) is mentioned as a placeholder; it may need to be promoted to a full story if required for launch
- Stats computation could become expensive for long-term users; consider caching or incremental calculation

---

## Definition of Done

- All acceptance criteria are met
- Stats are accurate and match manual verification against chat data
- Account deletion removes all user data from the database
- Daily reminder preference is persisted and respected
- API endpoints have automated tests
- UI is responsive and matches the Clearness design system on mobile viewports
