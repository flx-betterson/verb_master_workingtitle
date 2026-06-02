"""
01_conjugate.py
Generate full conjugation tables for all verbs in verb_list.txt using mlconjug3.
Output: data/raw/conjugations.json

Run: python data/scripts/01_conjugate.py
"""

import json
import os
import sys
from pathlib import Path

try:
    import mlconjug3
except ImportError:
    print("ERROR: mlconjug3 not installed. Run: pip install -r data/scripts/requirements.txt")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
VERB_LIST_PATH = SCRIPT_DIR / "verb_list.txt"
OUT_DIR = REPO_ROOT / "data" / "raw"
OUT_PATH = OUT_DIR / "conjugations.json"

# Mapping from mlconjug3 mood keys → our schema Mood enum
MOOD_MAP = {
    "Indicativo": "INDICATIVO",
    "Subjuntivo": "SUBJUNTIVO",
    "Imperativo": "IMPERATIVO",
}

# Mapping from mlconjug3 tense keys → our schema Tense enum
TENSE_MAP = {
    "Presente": "PRESENTE",
    "Pretérito Indefinido": "PRETERITO_INDEFINIDO",
    "Pretérito Imperfecto": "PRETERITO_IMPERFECTO",
    "Pretérito Perfecto Compuesto": "PRETERITO_PERFECTO_COMPUESTO",
    "Pretérito Pluscuamperfecto": "PRETERITO_PLUSCUAMPERFECTO",
    "Futuro": "FUTURO_SIMPLE",
    "Futuro Perfecto": "FUTURO_PERFECTO",
    "Condicional": "CONDICIONAL_SIMPLE",
    "Condicional Perfecto": "CONDICIONAL_PERFECTO",
    # Subjuntivo
    "Presente de Subjuntivo": "PRESENTE",
    "Pretérito Imperfecto de Subjuntivo": "IMPERFECTO_RA",
    # Imperativo
    "Imperativo Afirmativo": "IMPERATIVO_AFIRMATIVO",
    "Imperativo Negativo": "IMPERATIVO_NEGATIVO",
}

# Mapping from mlconjug3 person keys → our schema Person enum
PERSON_MAP = {
    "1s": "YO",
    "2s": "TU",
    "3s": "EL_ELLA_USTED",
    "1p": "NOSOTROS",
    "2p": "VOSOTROS",
    "3p": "ELLOS_ELLAS_USTEDES",
}

# Haber auxiliary forms for constructing compound tenses if library omits them
HABER = {
    "PRETERITO_PERFECTO_COMPUESTO": {
        "YO": "he", "TU": "has", "EL_ELLA_USTED": "ha",
        "NOSOTROS": "hemos", "VOSOTROS": "habéis", "ELLOS_ELLAS_USTEDES": "han",
    },
    "PRETERITO_PLUSCUAMPERFECTO": {
        "YO": "había", "TU": "habías", "EL_ELLA_USTED": "había",
        "NOSOTROS": "habíamos", "VOSOTROS": "habíais", "ELLOS_ELLAS_USTEDES": "habían",
    },
    "FUTURO_PERFECTO": {
        "YO": "habré", "TU": "habrás", "EL_ELLA_USTED": "habrá",
        "NOSOTROS": "habremos", "VOSOTROS": "habréis", "ELLOS_ELLAS_USTEDES": "habrán",
    },
    "CONDICIONAL_PERFECTO": {
        "YO": "habría", "TU": "habrías", "EL_ELLA_USTED": "habría",
        "NOSOTROS": "habríamos", "VOSOTROS": "habríais", "ELLOS_ELLAS_USTEDES": "habrían",
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_verb_list(path: Path) -> list[str]:
    verbs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                verbs.append(line)
    return verbs


def extract_form(raw_form: str) -> str:
    """Strip pronoun prefix if mlconjug3 returns 'yo hablo' instead of 'hablo'."""
    pronouns = ["yo ", "tú ", "él ", "ella ", "usted ", "nosotros ", "nosotras ",
                "vosotros ", "vosotras ", "ellos ", "ellas ", "ustedes "]
    for p in pronouns:
        if raw_form.startswith(p):
            return raw_form[len(p):]
    return raw_form


def conjugate_verb(conjugator, infinitive: str) -> dict:
    try:
        result = conjugator.conjugate(infinitive)
    except Exception as e:
        print(f"  WARNING: could not conjugate '{infinitive}': {e}")
        return None

    conjugations = []
    past_participle = None
    gerund = None

    raw = result.conjug_info

    for mood_key, tenses in raw.items():
        if mood_key not in MOOD_MAP:
            # Handle non-personal forms
            if "Participio" in mood_key or "Participio" in str(tenses):
                for _, form in tenses.items() if isinstance(tenses, dict) else []:
                    past_participle = extract_form(str(form))
            if "Gerundio" in mood_key:
                for _, form in tenses.items() if isinstance(tenses, dict) else []:
                    gerund = extract_form(str(form))
            continue

        mood = MOOD_MAP[mood_key]

        for tense_key, persons in tenses.items():
            tense = TENSE_MAP.get(tense_key)
            if not tense:
                print(f"  UNMAPPED tense: '{tense_key}' — add to TENSE_MAP")
                continue

            if not isinstance(persons, dict):
                continue

            for person_key, form in persons.items():
                person = PERSON_MAP.get(person_key)
                if not person:
                    continue
                if form is None or str(form).strip() == "-":
                    continue

                conjugations.append({
                    "mood": mood,
                    "tense": tense,
                    "person": person,
                    "form": extract_form(str(form)),
                    "isIrregular": False,  # enriched in merge step
                    "ruleCode": None,
                    "noteEn": None,
                    "noteDe": None,
                })

    return {
        "infinitive": infinitive,
        "gerund": gerund,
        "pastParticiple": past_participle,
        "conjugations": conjugations,
    }


def build_compound_tenses(verb_data: dict) -> dict:
    """Construct compound tenses from haber + participio if missing."""
    participle = verb_data.get("pastParticiple")
    if not participle:
        return verb_data

    existing = {
        (c["mood"], c["tense"], c["person"])
        for c in verb_data["conjugations"]
    }

    for tense, aux_forms in HABER.items():
        for person, aux in aux_forms.items():
            key = ("INDICATIVO", tense, person)
            if key not in existing:
                verb_data["conjugations"].append({
                    "mood": "INDICATIVO",
                    "tense": tense,
                    "person": person,
                    "form": f"{aux} {participle}",
                    "isIrregular": False,
                    "ruleCode": None,
                    "noteEn": None,
                    "noteDe": None,
                })

    return verb_data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    verbs = load_verb_list(VERB_LIST_PATH)
    print(f"Conjugating {len(verbs)} verbs...")

    conjugator = mlconjug3.Conjugator(language="es")

    # Debug: print raw structure of first verb so you can verify TENSE_MAP/PERSON_MAP
    print("\n--- DEBUG: raw conjug_info keys for 'hablar' ---")
    sample = conjugator.conjugate("hablar")
    for mood, tenses in sample.conjug_info.items():
        print(f"  Mood: {repr(mood)}")
        if isinstance(tenses, dict):
            for tense, persons in tenses.items():
                person_keys = list(persons.keys()) if isinstance(persons, dict) else persons
                print(f"    Tense: {repr(tense)} → persons: {person_keys}")
    print("--- END DEBUG ---\n")

    results = []
    failed = []

    for i, infinitive in enumerate(verbs, 1):
        print(f"[{i}/{len(verbs)}] {infinitive}", end=" ... ", flush=True)
        data = conjugate_verb(conjugator, infinitive)
        if data is None:
            failed.append(infinitive)
            print("FAILED")
            continue
        data = build_compound_tenses(data)
        results.append(data)
        print(f"OK ({len(data['conjugations'])} forms)")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone. {len(results)} verbs written to {OUT_PATH}")
    if failed:
        print(f"Failed ({len(failed)}): {', '.join(failed)}")
        print("Add failed verbs to TENSE_MAP/PERSON_MAP or remove from verb_list.txt")


if __name__ == "__main__":
    main()
