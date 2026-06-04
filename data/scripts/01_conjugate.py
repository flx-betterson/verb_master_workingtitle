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

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

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

# Mapping from mlconjug3 mood keys → our schema Mood enum.
# mlconjug3 uses "Condicional" as a separate mood — we flatten it into INDICATIVO
# since our schema treats condicional as tenses of indicativo.
MOOD_MAP = {
    "Indicativo": "INDICATIVO",
    "Subjuntivo": "SUBJUNTIVO",
    "Imperativo": "IMPERATIVO",
    "Condicional": "INDICATIVO",
}

# mlconjug3 tense keys include the mood prefix and use inconsistent casing across verbs,
# e.g. "Indicativo Presente" and "Indicativo presente" both occur.
# normalize_tense_key() strips the mood prefix and lowercases before this lookup.
TENSE_MAP = {
    # Indicativo / Condicional (after stripping mood prefix)
    "presente":                       "PRESENTE",
    "pretérito imperfecto":           "PRETERITO_IMPERFECTO",
    "pretérito perfecto compuesto":   "PRETERITO_PERFECTO_COMPUESTO",
    "pretérito pluscuamperfecto":     "PRETERITO_PLUSCUAMPERFECTO",
    "pretérito perfecto simple":      "PRETERITO_INDEFINIDO",
    "pretérito indefinido":           "PRETERITO_INDEFINIDO",
    "futuro":                         "FUTURO_SIMPLE",
    "futuro perfecto":                "FUTURO_PERFECTO",
    "condicional":                    "CONDICIONAL_SIMPLE",   # "Condicional Condicional" → "condicional"
    "simple":                         "CONDICIONAL_SIMPLE",   # "Condicional simple" → "simple"
    "perfecto":                       "CONDICIONAL_PERFECTO", # "Condicional perfecto" → "perfecto"
    # Subjuntivo (after stripping "subjuntivo " prefix)
    "pretérito imperfecto 1":         "IMPERFECTO_RA",
    "pretérito imperfecto 2":         "IMPERFECTO_SE",
    "pretérito perfecto":             "PRETERITO_PERFECTO_COMPUESTO",
    "pretérito pluscuamperfecto 1":   "PRETERITO_PLUSCUAMPERFECTO",
    # Imperativo (after stripping "imperativo " prefix)
    "afirmativo":                     "IMPERATIVO_AFIRMATIVO",
    "negativo":                       "IMPERATIVO_NEGATIVO",
    "non":                            "IMPERATIVO_NEGATIVO",  # mlconjug3 French-origin quirk
    # Skipped intentionally:
    # "pretérito anterior"            — archaic tense, not in schema
    # "pretérito pluscuamperfecto 2"  — subjuntivo -se form, schema only stores -ra
    # "futuro" / "futuro perfecto"    — subjuntivo future, rare but kept via shared key above
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

# The library's Gerundio section always returns the past participle, not the gerund.
# We ignore it entirely and construct the gerund from the infinitive instead.
# Overrides cover stem-changing and other irregular gerunds.
# Irregular past participles. Regular ones are constructed by construct_past_participle().
# The library's Participo section is unreliable (prepends stem/char to correct form)
# so we ignore it entirely and construct from the infinitive.
PARTICIPLE_OVERRIDES: dict[str, str] = {
    "abrir":      "abierto",
    "cubrir":     "cubierto",
    "decir":      "dicho",
    "escribir":   "escrito",
    "hacer":      "hecho",
    "satisfacer": "satisfecho",
    "morir":      "muerto",
    "poner":      "puesto",
    "componer":   "compuesto",
    "proponer":   "propuesto",
    "oponer":     "opuesto",
    "resolver":   "resuelto",
    "absolver":   "absuelto",
    "volver":     "vuelto",
    "devolver":   "devuelto",
    "envolver":   "envuelto",
    "romper":     "roto",
    "ver":        "visto",
    "prever":     "previsto",
    "freír":      "frito",
    "imprimir":   "impreso",
}

GERUND_OVERRIDES: dict[str, str] = {
    "ser":       "siendo",
    "ir":        "yendo",
    "poder":     "pudiendo",
    "dormir":    "durmiendo",
    "morir":     "muriendo",
    "decir":     "diciendo",
    "pedir":     "pidiendo",
    "sentir":    "sintiendo",
    "seguir":    "siguiendo",
    "conseguir": "consiguiendo",
    "venir":     "viniendo",
    "repetir":   "repitiendo",
    "medir":     "midiendo",
    "servir":    "sirviendo",
    "hervir":    "hirviendo",
    "mentir":    "mintiendo",
    "preferir":  "prefiriendo",
    "reír":      "riendo",
    "freír":     "friendo",
    "corregir":  "corrigiendo",
    "elegir":    "eligiendo",
    "traer":     "trayendo",
    "caer":      "cayendo",
    "leer":      "leyendo",
    "creer":     "creyendo",
    "oír":       "oyendo",
    "huir":      "huyendo",
    "incluir":   "incluyendo",
    "construir": "construyendo",
    "destruir":  "destruyendo",
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


def construct_gerund(infinitive: str) -> str:
    """Construct gerund from infinitive. Overrides cover irregular stem-changers."""
    if infinitive in GERUND_OVERRIDES:
        return GERUND_OVERRIDES[infinitive]
    if infinitive.endswith("ar"):
        return infinitive[:-2] + "ando"
    if infinitive.endswith("er") or infinitive.endswith("ir"):
        return infinitive[:-2] + "iendo"
    return infinitive


def construct_past_participle(infinitive: str) -> str:
    """Construct past participle from infinitive. Overrides cover irregular forms."""
    if infinitive in PARTICIPLE_OVERRIDES:
        return PARTICIPLE_OVERRIDES[infinitive]
    if infinitive.endswith("ar"):
        return infinitive[:-2] + "ado"
    if infinitive.endswith("er") or infinitive.endswith("ir"):
        return infinitive[:-2] + "ido"
    return infinitive


def normalize_tense_key(mood_key: str, raw_tense_key: str) -> str:
    """'Indicativo Pretérito imperfecto' → 'pretérito imperfecto'"""
    key = raw_tense_key.lower().strip()
    prefix = mood_key.lower().strip() + " "
    if key.startswith(prefix):
        key = key[len(prefix):]
    return key


def fix_encoding(s: str) -> str:
    """Fix UTF-8 mojibake (bytes decoded as Latin-1 then re-stringified)."""
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return s


def extract_nested_str(val) -> str | None:
    """Recurse into nested dicts/OrderedDicts until a non-empty string is found."""
    if isinstance(val, str):
        return val if val.strip() not in ("-", "", "None") else None
    if isinstance(val, dict):
        for v in val.values():
            result = extract_nested_str(v)
            if result:
                return result
    return None


def extract_form(raw_form) -> str:
    """Extract clean verb form: resolve nested dicts, fix encoding, strip pronouns."""
    s = extract_nested_str(raw_form)
    if not s:
        return ""
    s = fix_encoding(s)
    pronouns = ["yo ", "tú ", "él ", "ella ", "usted ", "nosotros ", "nosotras ",
                "vosotros ", "vosotras ", "ellos ", "ellas ", "ustedes "]
    for p in pronouns:
        if s.startswith(p):
            return s[len(p):]
    return s


def conjugate_verb(conjugator, infinitive: str) -> dict:
    try:
        result = conjugator.conjugate(infinitive)
    except Exception as e:
        print(f"  WARNING: could not conjugate '{infinitive}': {e}")
        return None

    conjugations = []
    raw = result.conjug_info

    for mood_key, tenses in raw.items():
        if mood_key not in MOOD_MAP:
            # Gerundio and Participo are intentionally ignored — the library stores
            # wrong/corrupted values for both. They are constructed from the infinitive.
            known_ignored = ("Gerundio", "Participo", "Participio", "Infinitivo", "Infinitif")
            if not any(x in mood_key for x in known_ignored):
                print(f"  UNMAPPED mood: '{mood_key}' — add to MOOD_MAP if needed")
            continue

        mood = MOOD_MAP[mood_key]

        for tense_key, persons in tenses.items():
            normalized = normalize_tense_key(mood_key, tense_key)
            tense = TENSE_MAP.get(normalized)
            if not tense:
                if normalized not in ("pretérito anterior", "pretérito pluscuamperfecto 2"):
                    print(f"  UNMAPPED tense: '{tense_key}' (normalized: '{normalized}') — add to TENSE_MAP")
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

    # Deduplicate by (mood, tense, person) — last value wins.
    # The library returns both an ML-predicted entry (Title Case tense key, unreliable)
    # and a database-driven entry (sentence case tense key, correct). The database form
    # comes last in iteration so it overwrites the ML garbage for irregular verbs.
    seen: dict[tuple, dict] = {}
    for conj in conjugations:
        seen[(conj["mood"], conj["tense"], conj["person"])] = conj
    conjugations = list(seen.values())

    gerund = construct_gerund(infinitive)
    past_participle = construct_past_participle(infinitive)

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
                print(f"    Tense: {repr(tense)} -> persons: {person_keys}")
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
