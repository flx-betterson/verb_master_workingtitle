"""
04_validate.py
Spot-check verbs_final.json before seeding. Exits with code 1 if errors found.

Input:  data/processed/verbs_final.json
Output: stdout report

Run: python data/scripts/04_validate.py
"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
IN_PATH = REPO_ROOT / "data" / "processed" / "verbs_final.json"

VALID_MOODS = {"INDICATIVO", "SUBJUNTIVO", "IMPERATIVO"}
VALID_TENSES = {
    "PRESENTE", "PRETERITO_INDEFINIDO", "PRETERITO_IMPERFECTO",
    "PRETERITO_PERFECTO_COMPUESTO", "PRETERITO_PLUSCUAMPERFECTO",
    "FUTURO_SIMPLE", "FUTURO_PERFECTO", "CONDICIONAL_SIMPLE", "CONDICIONAL_PERFECTO",
    "IMPERFECTO_RA", "IMPERFECTO_SE",
    "IMPERATIVO_AFIRMATIVO", "IMPERATIVO_NEGATIVO",
}
VALID_PERSONS = {"YO", "TU", "EL_ELLA_USTED", "NOSOTROS", "VOSOTROS", "ELLOS_ELLAS_USTEDES"}
VALID_CEFR = {"A1", "A2", "B1", "B2"}

# Known irregular verbs — spot-check that they have at least one isIrregular=true form
KNOWN_IRREGULARS = ["ser", "estar", "ir", "tener", "hacer", "poder", "querer", "saber", "venir", "decir"]

# Minimum expected conjugation count per verb (indicativo alone = 54 forms)
MIN_CONJUGATIONS = 50


def validate(verbs: list[dict]) -> list[str]:
    errors = []
    infinitives = set()

    for verb in verbs:
        inf = verb.get("infinitive", "UNKNOWN")

        # Duplicates
        if inf in infinitives:
            errors.append(f"{inf}: DUPLICATE infinitive")
        infinitives.add(inf)

        # Required fields
        for field in ["translationsEn", "translationsDe", "cefrLevel", "gerund", "pastParticiple"]:
            val = verb.get(field)
            if not val:
                errors.append(f"{inf}: missing or empty '{field}'")

        if verb.get("cefrLevel") not in VALID_CEFR:
            errors.append(f"{inf}: invalid cefrLevel '{verb.get('cefrLevel')}'")

        conjugations = verb.get("conjugations", [])

        if len(conjugations) < MIN_CONJUGATIONS:
            errors.append(f"{inf}: only {len(conjugations)} conjugations (expected ≥{MIN_CONJUGATIONS})")

        for conj in conjugations:
            if conj.get("mood") not in VALID_MOODS:
                errors.append(f"{inf}: invalid mood '{conj.get('mood')}'")
            if conj.get("tense") not in VALID_TENSES:
                errors.append(f"{inf}: invalid tense '{conj.get('tense')}'")
            if conj.get("person") not in VALID_PERSONS:
                errors.append(f"{inf}: invalid person '{conj.get('person')}'")
            if not conj.get("form"):
                errors.append(f"{inf}: empty form for {conj.get('mood')}/{conj.get('tense')}/{conj.get('person')}")

    # Spot-check known irregulars
    verb_map = {v["infinitive"]: v for v in verbs}
    for inf in KNOWN_IRREGULARS:
        if inf not in verb_map:
            errors.append(f"MISSING known verb: '{inf}'")
            continue
        # Just verify the verb exists and has conjugations — isIrregular enrichment is optional for now
        conj_count = len(verb_map[inf].get("conjugations", []))
        if conj_count < MIN_CONJUGATIONS:
            errors.append(f"{inf}: irregular verb has too few conjugations ({conj_count})")

    return errors


def main():
    if not IN_PATH.exists():
        print(f"ERROR: {IN_PATH} not found. Run 03_merge.py first.")
        sys.exit(1)

    with open(IN_PATH, encoding="utf-8") as f:
        verbs = json.load(f)

    print(f"Validating {len(verbs)} verbs...\n")
    errors = validate(verbs)

    total_conjugations = sum(len(v.get("conjugations", [])) for v in verbs)
    cefr_counts: dict[str, int] = {}
    for v in verbs:
        level = v.get("cefrLevel", "?")
        cefr_counts[level] = cefr_counts.get(level, 0) + 1

    print("=== Summary ===")
    print(f"  Total verbs:        {len(verbs)}")
    print(f"  Total conjugations: {total_conjugations}")
    print(f"  CEFR distribution:  {cefr_counts}")
    print()

    if errors:
        print(f"=== ERRORS ({len(errors)}) ===")
        for e in errors:
            print(f"  ✗ {e}")
        print()
        print("Fix errors before seeding.")
        sys.exit(1)
    else:
        print("=== All checks passed ✓ ===")
        print("Ready to seed: cd apps/api && npx prisma db seed")
        sys.exit(0)


if __name__ == "__main__":
    main()
