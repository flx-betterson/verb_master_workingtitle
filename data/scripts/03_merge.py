"""
03_merge.py
Final merge and normalisation pass. Produces the seed-ready JSON.

Input:  data/raw/enriched.json
Output: data/processed/verbs_final.json

Run: python data/scripts/03_merge.py
"""

import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
IN_PATH = REPO_ROOT / "data" / "raw" / "enriched.json"
OUT_PATH = REPO_ROOT / "data" / "processed" / "verbs_final.json"

# Verb+tense combinations where meaning genuinely shifts.
# Format: { infinitive: { tense: { "en": "...", "de": "..." } } }
ASPECT_NOTES: dict[str, dict[str, dict[str, str]]] = {
    "saber": {
        "PRETERITO_INDEFINIDO": {
            "en": "to find out (discovery, not ongoing knowledge)",
            "de": "herausfinden (Entdeckung, nicht fortlaufendes Wissen)",
        },
    },
    "conocer": {
        "PRETERITO_INDEFINIDO": {
            "en": "to meet (for the first time)",
            "de": "kennenlernen (zum ersten Mal)",
        },
    },
    "querer": {
        "PRETERITO_INDEFINIDO": {
            "en": "to try (attempted but did not succeed)",
            "de": "versuchen (Versuch, der nicht gelang)",
        },
        "PRETERITO_IMPERFECTO": {
            "en": "to want (ongoing desire)",
            "de": "wollen (anhaltender Wunsch)",
        },
    },
    "poder": {
        "PRETERITO_INDEFINIDO": {
            "en": "to manage to / to succeed in",
            "de": "es schaffen / gelingen",
        },
        "PRETERITO_IMPERFECTO": {
            "en": "to be able to (general ability, not specific attempt)",
            "de": "können (allgemeine Fähigkeit)",
        },
    },
    "tener": {
        "PRETERITO_INDEFINIDO": {
            "en": "to receive / to get",
            "de": "bekommen / erhalten",
        },
    },
}


def apply_aspect_notes(verb_data: dict) -> dict:
    infinitive = verb_data["infinitive"]
    notes = ASPECT_NOTES.get(infinitive, {})
    if not notes:
        return verb_data

    for conj in verb_data["conjugations"]:
        tense_notes = notes.get(conj["tense"])
        if tense_notes and conj["mood"] == "INDICATIVO":
            conj["noteEn"] = tense_notes["en"]
            conj["noteDe"] = tense_notes["de"]

    return verb_data


def main():
    with open(IN_PATH, encoding="utf-8") as f:
        verbs = json.load(f)

    print(f"Merging {len(verbs)} verbs...")

    results = []
    for verb in verbs:
        verb = apply_aspect_notes(verb)
        results.append(verb)

    total_conjugations = sum(len(v["conjugations"]) for v in results)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Done.")
    print(f"  Verbs:        {len(results)}")
    print(f"  Conjugations: {total_conjugations}")
    print(f"  Output:       {OUT_PATH}")


if __name__ == "__main__":
    main()
