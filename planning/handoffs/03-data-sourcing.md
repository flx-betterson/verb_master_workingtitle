# Handoff: Data Sourcing + ETL
**GitHub Issues:** #3, #4
**Milestone:** MVP Local

## Task
Run the 4-script ETL pipeline to produce `data/processed/verbs_final.json`,
then seed the Supabase database via Prisma.

## Read first
- `context/schema.md` — final data types and enums (MUST match output JSON exactly)
- `context/stack.md` — tech stack decisions
- `data/scripts/requirements.txt` — Python dependencies

## Pipeline order
```
01_conjugate.py   →  data/raw/conjugations.json
02_enrich.py      →  data/raw/enriched.json        (Claude API — translations + tags)
03_merge.py       →  data/processed/verbs_final.json
04_validate.py    →  stdout report (fix issues before seeding)
```
Then: `cd apps/api && npx prisma db seed`

## Constraints
- All mood/tense/person values in output JSON must match enum names in `context/schema.md` exactly
- `translationsEn` and `translationsDe` must be arrays (min 1 item, max 4)
- `cefrLevel` must be one of: A1, A2, B1, B2
- `isIrregular` per conjugation row must be derived from the library, not guessed
- Do not use LLMs to generate conjugation forms — only `mlconjug3`
- Compound tenses (Perfecto Compuesto, Pluscuamperfecto, etc.) are constructed
  from haber auxiliary forms + participio if mlconjug3 does not provide them

## Output / Definition of Done
- `data/processed/verbs_final.json` exists and passes `04_validate.py` with 0 errors
- All 500+ verbs have: conjugations, translationsEn, translationsDe, cefrLevel, thematicGroup
- Prisma seed runs without errors against local SQLite DB
- Row counts logged: verbs table, conjugations table

## Do not
- Modify `context/schema.md` — if the output shape doesn't match, fix the scripts
- Commit `data/raw/` or `data/processed/` — these are gitignored
- Run the seed against Supabase (production) until `04_validate.py` passes locally
