# Feature Requirements

## Language Scope
- Quiz direction: Spanish → German, Spanish → English
- NOT supported: German → English or English → German
- **System languages: German (DE) and English (EN) only**
- The entire UI — labels, instructions, navigation, error messages, onboarding — is fully translated in both DE and EN
- User selects their system language once; it controls both the UI language and which translation (DE/EN) is shown during quizzes
- All verb data stores both `translation_de` and `translation_en`
- i18n must be wired in from day 1 — retrofitting it later is painful

## MVP Features

### Quiz Loop
- Show user a Spanish infinitive → ask for its meaning (DE or EN depending on UI language)
- Show user a tense + person → ask for the conjugated form
- User does NOT type answers — self-assessed: reveal answer, then click "Correct" / "Incorrect"
- After answer reveal: optionally expand the full conjugation table for that verb
- After answer reveal: optionally expand the conjugation rule that applies to that form

### Verb Selection
- Quiz pulls from the full verb dataset
- Spaced repetition or weighted random based on past performance (tracked in localStorage)
- "Difficult" verbs (marked wrong multiple times) surface more often

### Progress Tracking (localStorage, no auth)
- Per-verb correct/incorrect history
- Streak counter
- No account required

## Deferred (post-MVP)
- User accounts and cross-device sync
- Filtering quiz by tense (e.g. "only quiz me on Subjuntivo")
- Mobile app (API is designed to support it from day 1)
- Verb bookmarking / custom lists
- Conjugation rule explanations as expandable cards (data model supports it; UI deferred)

## Data Requirements
See [schema.md](schema.md) for the full data model.

Each verb needs:
- Spanish infinitive
- German translation(s)
- English translation(s)
- Full conjugation table (all tenses, all persons)
- Irregularity flags per conjugated form
- Rule references per conjugated form (for the expandable rule feature)
- Tags: reflexive, common/advanced, thematic group

## Out of Scope (forever, unless explicitly revisited)
- German ↔ English translation direction
- Text input / auto-grading of answers
- Audio pronunciation
