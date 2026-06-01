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
_Populated once apps are scaffolded._
