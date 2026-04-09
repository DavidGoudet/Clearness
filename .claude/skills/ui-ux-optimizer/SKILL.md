---
name: ui-ux-optimizer
description: audit and optimize UI/UX quality across all visual and interaction dimensions
---


Deeply audit and optimize UI/UX quality across all visual and interaction dimensions. Use this skill whenever the user shares a screenshot, code, or description of an interface and wants it improved, reviewed, or polished. Triggers on phrases like "improve the UI", "review my design", "make it look better", "fix the UX", "check my interface", "optimize the visuals", "audit my app", "critique my design", or any time someone shows you a UI and wants feedback or improvements. Also use proactively when generating frontend code — always apply these principles without being asked.UI/UX Optimizer
A comprehensive skill for auditing, critiquing, and transforming interfaces into polished, professional experiences. Apply this skill to any visual interface — screenshots, code, descriptions, or mockups.

Core Philosophy
Good UI/UX is intentional at every level. Every pixel, every spacing unit, every color choice either builds trust and clarity — or erodes it. Your job is to find what's broken, explain why it matters, and fix it precisely.
Approach every audit with a designer's eye + engineer's precision: identify issues at the aesthetic, perceptual, and structural level, then produce concrete code improvements.

The Audit Framework
Always evaluate across ALL six dimensions below. Never skip a category even if it seems fine — absence of problems is still worth noting briefly.

1. 🎨 Color & Contrast
What to check:

WCAG contrast ratios: AA minimum (4.5:1 for body text, 3:1 for large text/UI), AAA preferred (7:1)
Color harmony: Are hues intentional? Is there a clear primary/secondary/accent hierarchy?
Semantic color use: Are danger/success/warning/info states visually distinct and consistent?
Color overload: Are more than 4–5 distinct hues competing for attention?
Dark/light mode appropriateness: Does the palette work in context?
Saturation balance: Is anything over-saturated (garish) or under-saturated (lifeless)?

Common failures:

Gray text on white backgrounds that fails contrast (#999 on #fff = 2.85:1, fails AA)
Pure black (#000) on pure white (#fff) — too harsh, causes halation
Multiple competing accent colors with no hierarchy
Background/text combos that look fine on your calibrated monitor but fail elsewhere

Fix pattern:
css/* Before: fails contrast */
color: #aaaaaa;
background: #ffffff;

/* After: passes AA (4.6:1) */
color: #767676;
background: #ffffff;

/* Better: use design tokens */
--color-text-muted: #6b7280;
--color-text-primary: #111827;
--color-surface: #ffffff;

2. 📐 Spatial Composition & Layout
What to check:

Spacing consistency: Is there a clear spacing scale (4px, 8px, 16px, 24px, 32px, 48px)?
Alignment: Are elements aligned to a grid? Are there accidental 13px gaps?
Visual hierarchy: Does the eye move naturally through the intended reading order?
Density: Is the layout too cramped (anxiety-inducing) or too sparse (wasteful)?
Negative space: Is white space used purposefully to create breathing room?
Asymmetry vs symmetry: Is the choice intentional and consistent?
Component grouping: Are related elements visually grouped (Gestalt proximity)?

Common failures:

Inconsistent padding (16px here, 18px there, 20px somewhere else)
Elements that are "kind of" aligned but not exactly
No clear F-pattern or Z-pattern reading flow
Content that's edge-to-edge with no margin on mobile

Fix pattern:
css/* Use a spacing scale, never arbitrary values */
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
  --space-16: 64px;
}

3. ✨ Motion & Animation
What to check:

Purpose: Does every animation serve communication (feedback, transition, attention) or is it decorative noise?
Duration: Are transitions 150–300ms for micro-interactions, 300–500ms for page transitions?
Easing: Is ease-in-out or custom cubic-bezier used (not jarring linear)?
Reduced motion: Is prefers-reduced-motion respected?
Entrance animations: Do elements enter with intention (fade + slide, not just pop)?
Loading states: Are skeletons or spinners present where data loads?
Hover states: Do interactive elements give clear, immediate feedback?

Common failures:

Animations that are too slow (>500ms) and feel sluggish
linear easing that feels robotic
No hover feedback on clickable elements
Simultaneous animations that compete for attention

Fix pattern:
css/* Purposeful, smooth transitions */
.button {
  transition: 
    background-color 150ms ease-out,
    transform 120ms ease-out,
    box-shadow 150ms ease-out;
}

.button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.button:active {
  transform: translateY(0px);
}

/* Always respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

4. 🖼 Backgrounds & Visual Depth
What to check:

Flat vs dimensional: Does the UI feel like paper cutouts or a coherent spatial system?
Shadow usage: Are shadows consistent (single light source, soft and purposeful)?
Surface hierarchy: Do cards/modals/tooltips feel visually elevated appropriately?
Background interest: Is it a dead #f5f5f5 or does it have subtle texture/gradient?
Layering: Do overlapping elements feel intentionally composed?
Border usage: Are borders used sparingly or overused as separators when spacing could do the job?

Common failures:

Overuse of box-shadow that looks like everything is floating
Inconsistent shadow directions (some from top-left, some from bottom)
Pure flat design with no depth cues, making the hierarchy unclear
Default browser focus rings that look out of place

Fix pattern:
css/* Coherent elevation system */
:root {
  --shadow-sm:  0 1px 2px rgba(0,0,0,0.05);
  --shadow-md:  0 4px 6px -1px rgba(0,0,0,0.08), 0 2px 4px -1px rgba(0,0,0,0.05);
  --shadow-lg:  0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04);
  --shadow-xl:  0 20px 25px -5px rgba(0,0,0,0.08), 0 10px 10px -5px rgba(0,0,0,0.03);
}

/* Subtle background texture instead of flat gray */
body {
  background-color: #f8fafc;
  background-image: radial-gradient(circle at 1px 1px, #e2e8f0 1px, transparent 0);
  background-size: 24px 24px;
}

5. 🔤 Typography & Visual Hierarchy
What to check:

Type scale: Is there a clear, limited hierarchy (h1, h2, h3, body, caption, label)?
Font pairing: Are 1–2 fonts used max? Do they complement each other?
Line height: Is body text 1.5–1.7? Headings 1.1–1.3?
Letter spacing: Is tracking tight for headings (-0.02em) and relaxed for uppercase labels (0.05–0.1em)?
Font weight usage: Is weight used for emphasis, not just size?
Orphans and widows: Do headlines wrap awkwardly?
Reading width: Is body text max ~65–75 characters per line (60–70ch)?

Common failures:

Too many font sizes creating visual chaos
Body text at 12–13px that's exhausting to read
No visual difference between h2 and h3
All-caps body text (accessibility/readability issue)

Fix pattern:
css/* Clean type scale using modular scale */
:root {
  --text-xs:   0.75rem;   /* 12px */
  --text-sm:   0.875rem;  /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg:   1.125rem;  /* 18px */
  --text-xl:   1.25rem;   /* 20px */
  --text-2xl:  1.5rem;    /* 24px */
  --text-3xl:  1.875rem;  /* 30px */
  --text-4xl:  2.25rem;   /* 36px */
}

body {
  font-size: var(--text-base);
  line-height: 1.6;
  max-width: 68ch; /* Optimal reading width */
}

6. 🧩 Visual Details & Polish
What to check:

Border radius consistency: Is it the same value system throughout?
Icon consistency: Are icons from the same family, same weight, same size grid?
Image treatment: Are images cropped consistently? Aspect ratios locked?
Empty states: Are zero/loading/error states designed, not just forgotten?
Focus states: Are they visible, accessible, and styled to match the design?
Cursor behavior: Are pointer cursors on clickable, default on non-interactive?
Form elements: Are inputs, selects, checkboxes styled consistently and not browser-default?
Scrollbars: On custom scroll containers, are scrollbars styled or hidden intentionally?

Common failures:

Mix of rounded and sharp-cornered elements
Browser-default blue focus rings clashing with a custom palette
Inputs that look interactive but don't respond visually to focus
Icons at mismatched sizes (16px next to 24px)

Fix pattern:
css/* Consistent border radius system */
:root {
  --radius-sm:   4px;
  --radius-md:   8px;
  --radius-lg:  12px;
  --radius-xl:  16px;
  --radius-full: 9999px;
}

/* Custom focus state */
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}

/* Cursor consistency */
button, [role="button"], a, label, select { cursor: pointer; }
[disabled] { cursor: not-allowed; }

Audit Output Format
When auditing an interface, structure your response like this:
Quick Assessment
One paragraph: overall impression, design maturity, biggest wins and biggest gaps.
Critical Issues (fix immediately)
Issues that break usability, fail accessibility, or destroy trust. Max 3–5.
Important Improvements (fix soon)
Issues that reduce quality but don't break functionality. Max 5–7.
Refinements (polish pass)
Subtle improvements that elevate from good to great. Max 5.
What's Working
Acknowledge what's already strong — don't only criticize.
🔧 Code Changes
Provide specific, ready-to-use code for every issue identified. No vague suggestions. If you say "improve the contrast," provide the new hex values.

