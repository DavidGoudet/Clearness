# Clearness — Product Requirements Document

**Version:** 2.0
**Last Updated:** March 2, 2026
**Status:** MVP Definition
**Created with the help of Claude**

---

## 1. Product Overview

Clearness is a mobile application designed as a smart diary for mental clarity. The app provides a simple, daily conversational space where users can reflect on their day, track their moods over time, and gain clarity through consistent journaling.

### 1.1 Target Audience

- Adults (18+) looking for a simple, structured way to reflect daily
- Users who want to track their moods and spot patterns over time
- Individuals seeking a private, personal space for mental clarity

### 1.2 Core Value Proposition

> A few minutes of daily reflection can bring lasting clarity. Clearness gives you the space to do it.

The app encourages a daily journaling habit through a simple chat-based diary, helping users build self-awareness by reviewing their moods and reflections over time.

---

## 2. App Architecture

### 2.1 Navigation Structure

The app uses a bottom tab navigation with three primary screens:

| Tab | Label | Purpose |
|---|---|---|
| 📖 | Journal | Daily chat for reflection |
| 📅 | Calendar | Monthly mood view with daily summaries |
| 👤 | Profile | Account settings and support resources |

### 2.2 Design System

- **Theme:** Light (white/off-white surfaces, soft shadows)
- **Primary Accent:** Teal-blue (#2d8ab0)
- **Semantic Colors:** Green (positive mood), Blue (neutral), Orange (low mood)
- **Typography:** Inter, weights 200–600
- **Corner Radius:** 12–20px (rounded, approachable)
- **Tone:** Warm, friendly, encouraging

---

## 3. Feature Specifications

### 3.1 Journal — Daily Chat

The journal is the app's primary screen and core feature. Each day has exactly one chat session where the user reflects on their day.

#### 3.1.1 Daily Chat (One Per Day)

Each day features a single conversational chat. The chat is the user's main interaction with the app.

**Behavior:**
- When the user opens the Journal tab, today's chat is shown by default
- If no chat has been started for today, the app initiates the conversation with a greeting personalized by time of day (morning/afternoon/evening) and the user's name
- The app asks "How are you feeling today?" via a chat bubble
- The user responds via free-text input
- The app acknowledges the user's response with an empathetic, contextual reply (templated, sentiment-based for MVP)
- The chat is limited to this structured flow for MVP — it is not an open-ended conversation
- One chat per day: if the user returns later, they see their completed chat (read-only) rather than starting a new one

**Mood Capture:**
- As part of the chat flow, the user selects a mood via an emoji selector: 😊 Happy, 😌 Calm, 😐 Neutral, 😔 Down, 😤 Frustrated
- The selected mood is stored and used in the Calendar view

**Chat UX Details:**
- Bot messages appear with a typing indicator animation (3 pulsing dots) before revealing content
- User messages are styled in accent-blue with right alignment
- Bot messages are styled in white/light-grey with left alignment
- The chat auto-scrolls to the latest message
- Input bar is fixed at the bottom with a send button that activates when text is entered
- Once the chat flow is complete, the input bar is hidden and the chat becomes read-only for that day

---

### 3.2 Calendar — Mood Overview & Daily Summaries

The calendar screen provides a monthly view of the user's moods, allowing them to spot patterns and review past days.

#### 3.2.1 Monthly Mood Calendar

- Standard monthly calendar grid
- Each day that has a completed chat displays the mood emoji selected during that day's chat
- Days without a chat are blank
- The current day is highlighted
- Users can navigate between months (previous/next arrows)

#### 3.2.2 Daily Summary

- Tapping a day on the calendar opens a summary view for that day
- The summary shows:
  - The mood emoji and label
  - The user's free-text response from the chat
  - The date and time of the chat
- If no chat exists for that day, a "No entry for this day" placeholder is shown

---

### 3.3 Profile — Account & Settings

#### 3.3.1 User Identity

- Avatar (emoji-based or custom)
- Display name
- Membership date

#### 3.3.2 Journey Stats

A 2x2 grid showing lifetime metrics:
- Total chats completed
- Current streak (consecutive days)
- Most frequent mood
- Longest streak

#### 3.3.3 Settings

| Setting | Description |
|---|---|
| **Reminders** | Configure daily check-in notification time |
| **Privacy** | End-to-end encryption status, data management |

---

## 4. Authentication

- **Google Sign-In** — OAuth 2.0 via Google Identity Services
- **Apple Sign-In** — Sign in with Apple (required for iOS apps offering third-party login)
- No email/password authentication for MVP
- Users are prompted to sign in on first launch before accessing the app

---

## 5. Data & Privacy

### 5.1 Principles

- **Privacy-first:** Journal entries contain deeply personal content. Privacy is non-negotiable.
- **End-to-end encryption** for all journal data
- **No data selling** — user data is never shared with third parties
- **Local-first option** — users can choose to store data on-device only
- **Easy deletion** — users can delete all data at any time

### 5.2 Data Model (Simplified)

```
User
├── profile (name, avatar, join_date, settings)
├── auth (provider: google | apple, provider_id)
└── daily_chats[]
    ├── id, date (unique per day)
    ├── greeting, user_response, bot_reply
    ├── mood (emoji + label)
    ├── completed_at
    └── status (in_progress | completed)
```

### 5.3 Regulatory Considerations

- The app is positioned as a **wellness tool**, not a medical device
- No clinical claims — language uses "helps you reflect" and "supports your clarity"
- GDPR and CCPA compliance required given the sensitive nature of data
- If integrating AI for chat responses, data processing agreements must cover AI model providers

---

## 6. Technical Considerations

### 6.1 Platform

- **Mobile-first:** iOS and Android (React Native or Flutter recommended)
- **Minimum viable backend:** Authentication (Google + Apple), encrypted data sync, push notifications
- **AI integration:** Chat responses require an LLM endpoint (API-based, not on-device for MVP)

### 6.2 Key Technical Requirements

- Offline support for chats (sync when connected)
- Secure local storage for sensitive data
- Push notification scheduling for daily reminders
- Google and Apple OAuth integration

---

## 7. Success Metrics

| Metric | Target (6 months post-launch) |
|---|---|
| Daily active users (DAU) | 5,000 |
| D7 retention | 45% |
| D30 retention | 25% |
| Chats per active user/week | 5+ |
| App Store rating | 4.6+ |
| NPS score | 50+ |

---

## 8. Risk Factors

| Risk | Severity | Mitigation |
|---|---|---|
| Users in crisis relying on app instead of professional help | High | Clear disclaimers, crisis resource links |
| AI chat provides inappropriate responses | Medium | Guardrails on LLM responses, review of prompt templates, disclaimers |
| Data breach exposing sensitive personal data | High | E2E encryption, SOC 2 compliance, regular security audits |
| Low retention due to simplicity of the experience | Medium | Gentle reminders, celebration of streaks, warm tone |

---

## 9. Roadmap (High Level)

### Phase 1 — MVP
- Daily chat with mood capture (one per day)
- Calendar view with mood display and daily summaries
- Profile with stats and settings
- Google and Apple Sign-In
- Push notification reminders

---

*This document defines the product vision and feature set for Clearness v2.0.*