# Verb Master (Working Title)

Spanish verb conjugation quiz app. Users are quizzed on verb meanings and conjugated forms.
Semi-tri-lingual: Spanish ↔ German, Spanish ↔ English (not German ↔ English).

## Context Files
Read these before working on a task — they contain locked decisions and rationale.

- [context/features.md](context/features.md) — feature requirements, MVP scope, deferred items
- [context/stack.md](context/stack.md) — tech stack with rationale
- [context/schema.md](context/schema.md) — data schema (verb, conjugation, translation structures)

## Monorepo Structure
```
apps/
  web/              React + Vite + TypeScript + Tailwind + React Router + Zustand
  api/              Fastify + TypeScript + Prisma
packages/
  shared/           TypeScript types shared between web and api
context/            Agent handoff docs (non-code)
```

## Current Phase
**Step 1 — Data Schema design** (no code written yet)

## Key Commands

```bash
# Install all dependencies (run from repo root)
npm install

# Development
npm run dev:api        # Fastify API on http://localhost:3001
npm run dev:web        # Vite frontend on http://localhost:3000

# Database (run from apps/api/)
npx prisma migrate dev --name <name>   # apply schema changes
npx prisma db seed                     # seed from data/processed/verbs_final.json
npx prisma studio                      # visual DB browser

# Data pipeline (run from data/scripts/ with .venv active)
python 01_conjugate.py   # generate conjugations
python 02_enrich.py      # Claude API — translations + tags
python 03_merge.py       # merge into verbs_final.json
python 04_validate.py    # pre-seed validation
```
