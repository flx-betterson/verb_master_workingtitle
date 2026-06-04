# Handoff: Backend Scaffold
**GitHub Issues:** #5, #6, #7
**Milestone:** MVP Local

## Task
Scaffold the full monorepo: shared types package, Fastify API with Prisma, React web skeleton.
Implement the three verb API endpoints. Seed the local SQLite database.

## Read first
- `context/schema.md` — locked data model (Prisma schema must match exactly)
- `context/stack.md` — tech stack and versions
- `context/features.md` — language scope (DE + EN)

## Structure to produce
```
package.json              root workspaces config
tsconfig.base.json        shared TS base config
packages/shared/          TypeScript types + enums + TenseInfo constant
apps/api/                 Fastify + Prisma + seed script
apps/web/                 React + Vite skeleton (routes + i18n wired, no quiz UI yet)
```

## Constraints
- TypeScript strict mode everywhere
- translationsEn / translationsDe stored as Json in Prisma (not separate table)
- Prisma enums match context/schema.md enum names exactly
- @@unique([verbId, mood, tense, person]) on Conjugation
- Seed reads data/processed/verbs_final.json (relative to repo root)
- DATABASE_URL env var switches between SQLite (local) and PostgreSQL (prod)
- packages/shared must NOT depend on @prisma/client — define independent API types

## API endpoints (Issue #7)
GET /verbs/random     → VerbSummary (no conjugations, for quiz card)
GET /verbs/:id        → VerbDetail (with all conjugations)
GET /health           → { ok: true }

## Output / Definition of Done
- npm install runs cleanly from repo root
- npx prisma migrate dev runs without errors
- npx prisma db seed populates DB (233 verbs, ~22k conjugations)
- GET /verbs/random returns valid JSON
- GET /verbs/:id returns verb with conjugations array

## Do not
- Implement quiz logic in the API — that's frontend/localStorage
- Add auth middleware
- Build any quiz UI — web skeleton only (App.tsx placeholder)
