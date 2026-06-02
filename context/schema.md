# Data Schema

**Status: FINAL**

---

## Enums

### Mood
```typescript
enum Mood {
  INDICATIVO  = "indicativo",
  SUBJUNTIVO  = "subjuntivo",
  IMPERATIVO  = "imperativo",
}
```

### Tense
Tense values are scoped per mood. Not all tense values are valid in all moods —
valid combinations are documented below and enforced at the application layer (not DB constraint).

```typescript
enum Tense {
  // Indicativo + Subjuntivo shared
  PRESENTE                   = "presente",
  PRET_IMPERFECTO            = "pret_imperfecto",
  PRET_PERFECTO_COMPUESTO    = "pret_perfecto_compuesto",   // he comido
  PRET_PLUSCUAMPERFECTO      = "pret_pluscuamperfecto",     // había comido

  // Indicativo only
  PRET_INDEFINIDO            = "pret_indefinido",
  FUTURO_SIMPLE              = "futuro_simple",
  FUTURO_PERFECTO            = "futuro_perfecto",
  COND_SIMPLE                = "cond_simple",
  COND_PERFECTO              = "cond_perfecto",

  // Subjuntivo only
  SUB_PRET_IMPERFECTO_RA     = "sub_pret_imperfecto_ra",   // -ra form
  SUB_PRET_IMPERFECTO_SE     = "sub_pret_imperfecto_se",   // -se form
  SUB_PRET_PLUSCUAMPERFECTO  = "sub_pret_pluscuamperfecto",
  SUB_FUTURO                 = "sub_futuro",               // rare, legal/formal

  // Imperativo only
  AFIRMATIVO                 = "afirmativo",
  NEGATIVO                   = "negativo",
}
```

**Valid mood + tense combinations:**
| Mood | Valid Tenses |
|---|---|
| INDICATIVO | PRESENTE, PRET_INDEFINIDO, PRET_IMPERFECTO, PRET_PERFECTO_COMPUESTO, PRET_PLUSCUAMPERFECTO, FUTURO_SIMPLE, FUTURO_PERFECTO, COND_SIMPLE, COND_PERFECTO |
| SUBJUNTIVO | PRESENTE, PRET_IMPERFECTO, PRET_PERFECTO_COMPUESTO, PRET_PLUSCUAMPERFECTO, SUB_PRET_IMPERFECTO_RA, SUB_PRET_IMPERFECTO_SE, SUB_PRET_PLUSCUAMPERFECTO, SUB_FUTURO |
| IMPERATIVO | AFIRMATIVO, NEGATIVO |

### Person
```typescript
enum Person {
  YO                    = "yo",
  TU                    = "tu",
  EL_ELLA_USTED         = "el_ella_usted",
  NOSOTROS              = "nosotros",
  VOSOTROS              = "vosotros",
  ELLOS_ELLAS_USTEDES   = "ellos_ellas_ustedes",
}
```

Note: IMPERATIVO has no YO form — those rows do not exist in the database.

---

## Database Models

### Verb
```typescript
type Verb = {
  id:               string        // cuid
  infinitive:       string        // unique — e.g. "comenzar"
  translationsEn:   string[]      // e.g. ["to begin", "to start"]
  translationsDe:   string[]      // e.g. ["beginnen", "anfangen"]
  gerund:           string        // e.g. "comenzando" (stored — can be irregular)
  pastParticiple:   string        // e.g. "comenzado" (stored — can be irregular)
  isReflexive:      boolean
  tags:             string[]      // e.g. ["A1", "common", "motion"]
  conjugations:     Conjugation[]
}
```

`gerund` and `pastParticiple` are stored directly on Verb (not per-person rows)
because they are single forms. Both can be irregular (e.g. hacer → hecho).

### Conjugation
One row per mood × tense × person combination.

```typescript
type Conjugation = {
  id:           string         // cuid
  verbId:       string         // → Verb.id
  mood:         Mood
  tense:        Tense
  person:       Person
  form:         string         // the conjugated word, e.g. "comienza"
  isIrregular:  boolean
  ruleId:       string | null  // → Rule.id, null if regular or rule not mapped
  noteEn:       string | null  // only for aspectual/semantic shifts (e.g. saber: "to find out" in pret. indefinido)
  noteDe:       string | null  // same, in German
}
```

`noteEn` / `noteDe` are null for the vast majority of rows. Used only for verbs
that genuinely shift meaning across tenses (conocer, saber, querer, poder, etc.).

### Rule
Conjugation rule reference. Links a conjugation pattern to a human-readable explanation.

```typescript
type Rule = {
  id:             string   // cuid
  code:           string   // unique — e.g. "stem_e_ie", "go_yo", "spelling_c_qu"
  descriptionEn:  string
  descriptionDe:  string
}
```

---

## UserProgress (localStorage — no database model)

Persisted via Zustand's localStorage middleware. Not sent to the API.

```typescript
type VerbRecord = {
  correct:   number
  incorrect: number
  lastSeen:  number    // Unix timestamp ms
}

type UserProgress = {
  language:    "de" | "en"
  streak:      number
  lastSeenDate: string            // ISO date string — for streak calculation
  verbHistory: Record<string, VerbRecord>  // keyed by Verb.id
}
```

Weighting logic (frontend): verbs with a higher `incorrect / (correct + incorrect)` ratio
surface more frequently. Verbs not yet seen are treated as highest priority.

---

## TenseInfo (static constant — not a database model)

Tense descriptions are immutable facts about Spanish grammar, identical across all verbs.
Stored as a typed constant in `packages/shared`, consumed directly by the frontend.
No API call, no DB table, no joins.

```typescript
type TenseInfo = {
  mood:        Mood
  tense:       Tense
  nameEn:      string   // e.g. "Simple Present"
  nameDe:      string   // e.g. "Präsens"
  spanishName: string   // e.g. "Presente de Indicativo"
  usageEn:     string   // short explanation of when this tense is used (1-3 sentences)
  usageDe:     string
}

// Consumed as:
// import { TENSE_INFO } from "@verb-master/shared"
// const info = TENSE_INFO[Mood.INDICATIVO][Tense.PRESENTE]
```

`TENSE_INFO` is a nested lookup: `Record<Mood, Partial<Record<Tense, TenseInfo>>>`.
`Partial` because not all Tense values are valid for all Moods.

---

## Shared TypeScript types (packages/shared)

The types above (Verb, Conjugation, Rule, Mood, Tense, Person) are defined in
`packages/shared` and imported by both `apps/web` and `apps/api`.

`UserProgress` lives in `apps/web` only — the API has no knowledge of it.

---

## Design Decisions

- **Mood + Tense as separate enums** (not one combined paradigm) — enables clean
  querying by mood (`WHERE mood = 'subjuntivo'`) and by tense independently.
- **gerund/pastParticiple on Verb, not Conjugation rows** — they are single forms
  with no person dimension; storing them separately avoids NULL person rows.
- **isIrregular per Conjugation row** — allows the UI to highlight individual
  irregular forms within an otherwise regular paradigm (e.g. go-yo verbs).
- **ruleId nullable** — MVP data may not have all rules mapped; the schema supports
  it without blocking the quiz.
- **noteEn/noteDe nullable on Conjugation** — covers the ~10-20 verbs with aspectual
  meaning shifts across tenses (conocer, saber, querer, poder…). Null for all others.
- **TenseInfo as static constant, not DB table** — 16 immutable rows don't belong in
  a database. Typed constant in packages/shared, consumed by frontend directly.
- **All tenses stored from day 1** — avoids a costly re-gather later when quiz
  scope expands beyond MVP tenses.
- **Vosotros included** — European Spanish focus; standard in textbooks.
