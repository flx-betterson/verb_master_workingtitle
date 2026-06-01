# Tech Stack

## Decisions

### Monorepo
- **Tool**: npm workspaces (no Turborepo — overkill for this scope)
- **Rationale**: Single repo, shared types package, no extra tooling overhead

### Frontend — `apps/web/`
| Library | Version target | Rationale |
|---|---|---|
| React | 19 | Component model, ecosystem |
| Vite | latest | Fast DX, no SSR complexity needed |
| TypeScript | 5.x | Type safety across the stack |
| Tailwind CSS | 4.x | Rapid UI iteration |
| React Router | v7 | Routing |
| Zustand | latest | Lightweight state + localStorage persistence for quiz progress |
| i18next + react-i18next | latest | Full UI i18n for DE and EN (not optional — baked in from day 1) |

### Backend — `apps/api/`
| Library | Version target | Rationale |
|---|---|---|
| Fastify | 5.x | TypeScript-first, built-in JSON schema validation, faster than Express |
| Prisma | latest | TypeScript-native ORM, clean migration tooling, easy SQLite→PostgreSQL swap |
| PostgreSQL | 16 | Production database |
| SQLite | — | Local dev only (swapped via Prisma provider env var) |

### Shared — `packages/shared/`
- TypeScript types only (no runtime code)
- Verb schema types, API response shapes, enums (Tense, Mood, Person, Language)

## Auth Decision
**No auth for MVP.** Progress tracked in `localStorage` via Zustand persist middleware.
Auth (account creation, sync) added post-launch if the app gets traction.
Migration path: on signup, user uploads their localStorage state to a new account.

## Deployment Targets (when ready)
| App | Host | Tier |
|---|---|---|
| Frontend | Vercel | Free |
| API | Railway or Render | Free |
| Database | Supabase or Railway PostgreSQL | Free |

## Explicitly Rejected
- Next.js — fullstack not needed; would close off future mobile API reuse
- Express — no native TS types for request bodies, Fastify is strictly better here
- NestJS — over-engineered for a side project
- LLMs for conjugation data — hallucination risk on deterministic grammar rules; use existing datasets instead
