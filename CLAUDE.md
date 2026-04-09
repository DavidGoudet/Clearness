# Clearness — Claude Code Context

## Project Overview
Clearness is a full-stack web application with a Django REST API backend and a React (Vite) frontend using TypeScript.

## Architecture
- **backend/**: Django 5.x project with Django REST Framework
  - `backend/clearness/` — Django project configuration (settings, urls, wsgi, asgi)
  - `backend/api/` — Main API application (models, views, serializers, urls)
- **frontend/**: React 19 + TypeScript app bootstrapped with Vite
  - `frontend/src/` — React source code (TypeScript)
  - Vite dev server proxies `/api/*` requests to Django at `localhost:8000`

## Key Commands

### Backend
```bash
cd backend
source venv/bin/activate
python manage.py runserver        # Start dev server
python manage.py makemigrations   # Create migrations
python manage.py migrate          # Apply migrations
python manage.py test             # Run tests
```

### Frontend
```bash
cd frontend
npm run dev       # Start Vite dev server
npm run build     # Type-check (tsc) + production build
npm run preview   # Preview production build
npm run lint      # Run ESLint
```

### Docker
```bash
cp .env.example .env
docker compose up --build         # Start all services
# Frontend:   http://localhost:3000
# API:        http://localhost:3000/api/items/
# Admin:      http://localhost:3000/admin/
# Direct API: http://localhost:8000/api/items/
```

## Conventions
- API endpoints live under `/api/` prefix
- Django apps go in `backend/` as sibling directories to `clearness/`
- React components go in `frontend/src/components/`
- Use Django REST Framework serializers for all API input/output
- PostgreSQL is the database; connection configured via environment variables

### TypeScript (Frontend)
- **Always use TypeScript** — all frontend source files must use `.ts` or `.tsx` extensions, never `.js` or `.jsx`
- Use `.tsx` for files containing JSX (React components), `.ts` for everything else
- Define explicit types/interfaces for API responses, props, and state — avoid `any`
- Place shared types in dedicated files (e.g., `types.ts`) or co-locate with the module that owns them
- The project uses `strict: true` in `tsconfig.app.json` — do not weaken compiler strictness
- Vite config uses `vite.config.ts` (TypeScript)

### Story Generation & Planning
- **Keep it simple** — Clearness is intentionally a simple app. Resist the urge to over-decompose features into many stories.
- **Fewer, larger stories** — prefer a small number of well-scoped stories over many granular ones. Combine related work into a single story when it can be delivered together.
- **No unnecessary splitting** — do not split stories by layer (e.g., separate backend/frontend/API stories for a single feature). One story should cover the full vertical slice unless there is a clear reason to separate.
- **Ask before generating** — when breaking down a feature, propose the number and scope of stories first and get confirmation before writing them out.
- **YAGNI applies to stories too** — only create stories for what is actually needed now. Do not create stories for hypothetical future enhancements, edge cases, or "nice to haves" unless explicitly requested.
- **Respect requested counts** — if asked for "one user story" or "three epics", generate exactly that number. Do not silently generate more without asking. Err toward fewer, better-scoped stories.

## AI-Specific Anti-Patterns

These rules encode recurring AI failures observed across sessions. They are **not** obvious from code or convention — they capture judgments about how Claude should interact with this project specifically.

### 1. Plan-First Discipline Survives Long Sessions
**Problem:** During extended story implementation sessions (2+ hours), Claude drifted from plan-first behavior and began auto-implementing stories without showing an implementation plan for user approval first.

**Rule:** Before implementing any user story (whether in the story generation phase or implementation phase), always:
1. Create a concise implementation plan (using EnterPlanMode or showing plan context)
2. Get explicit user approval before writing code
3. Do not skip this for "small" or "obvious" stories — the ritual is the reset button for scope creep

**Scope:** Applies to all user story work, regardless of session length or perceived complexity.

### 2. Scope Stays Within Story Boundaries
**Problem:** When implementing a story, Claude would silently refactor adjacent code (shared utilities, parent components, type definitions) not explicitly mentioned in the story, expanding scope without asking.

**Rule:** When implementing a story:
- Only touch code directly required to fulfill acceptance criteria
- If you encounter messy or broken adjacent code, call it out in a comment or summary — do not fix it silently
- Ask before refactoring anything outside the strict story scope, even if it "improves" the surrounding code
- Exception: fixing type errors or import failures in code you directly modified is OK; cleaning up dead code discovered while implementing is not

**Scope:** All feature implementation work.

### 3. Check File Access Before MCP Calls
**Problem:** When working with design tools (Figma, etc.), Claude would make broad `mcp__figma__*` calls exploring design files without first confirming the file path/ID was available, wasting MCP quota and returning errors.

**Rule:** Before invoking design/asset MCP tools:
1. Ask the user for the specific resource URI or file path (or confirm you have it from prior context)
2. Do not make exploratory API calls to "find" the design — this wastes quota
3. Only call the MCP tool once you have a concrete, confirmed resource identifier
4. If you don't have the file/resource info, ask the user first

**Scope:** All MCP tool calls where a resource URI, file path, or ID is required (Figma, design systems, asset libraries).

### 4. Respect User Story Count Requests
**Problem:** When asked "create a user story for authentication," Claude generated four stories (login, signup, password reset, session management) without asking.

**Rule:** If asked for "N stories," generate exactly N, scoped as vertically integrated features. Do not expand to what you think the "complete" set should be. If the number seems wrong (e.g., one story for a complex feature), propose a different count and ask for confirmation — do not unilaterally increase it.

**Scope:** All story generation and breakdown requests.

### 5. Run Tests After Feature Implementation
**Problem:** After implementing features, tests were not run, allowing regressions and test failures to slip through (e.g., chat API tests that used out-of-range dates failed silently until explicitly checked).

**Rule:** After implementing any feature (backend API, frontend component, or service), immediately:
1. Run backend tests: `python manage.py test`
2. Run frontend linting: `npm run lint`
3. Report results to the user
4. Do not consider work complete without verification that tests pass

**Why:** Tests catch broken code before it merges. Running tests at the end of implementation prevents regressions and avoids discovering failures later. This is a hard stop before marking work as done.

**Scope:** All feature implementation work (story implementations, bug fixes, refactoring).

## Self-Heal Rule: Encoding Future Fixes

When a problem repeats across **two or more separate sessions**, it should be encoded here as a permanent anti-pattern rule.

**Process:**
1. Identify the symptom: What went wrong and in what context?
2. Diagnose the root: Is this a behavior that conflicts with the project's goals or user preferences?
3. Write the rule: Phrase it as a constraint or check Claude must perform, not a description of the problem
4. Define scope: When does this rule apply? (all work, story work only, MCP work, etc.)
5. Add to this section with a clear title and format matching the examples above
6. Update MEMORY.md if the fix involves user feedback or preferences that span projects

**Why this matters:** Without encoding recurring fixes, the same pattern repeats in future sessions because Claude starts fresh each conversation. CLAUDE.md is the permanent record of what you've learned about how Claude should interact with *this* project.
