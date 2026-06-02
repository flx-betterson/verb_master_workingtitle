"""
02_enrich.py
Enrich verbs with EN/DE translations, CEFR level, thematic group, and isReflexive
using the Claude API. Processes verbs in batches of 50.

Input:  data/raw/conjugations.json
Output: data/raw/enriched.json

Run: python data/scripts/02_enrich.py
"""

import json
import os
import sys
import time
from pathlib import Path

try:
    import anthropic
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: dependencies missing. Run: pip install -r data/scripts/requirements.txt")
    sys.exit(1)

load_dotenv(Path(__file__).parent / ".env")

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
IN_PATH = REPO_ROOT / "data" / "raw" / "conjugations.json"
OUT_PATH = REPO_ROOT / "data" / "raw" / "enriched.json"

BATCH_SIZE = 50
VALID_CEFR = {"A1", "A2", "B1", "B2"}

THEMATIC_GROUPS = [
    "being_existence", "motion_travel", "communication_speech", "cognition_perception",
    "emotion_feeling", "daily_routine", "work_study", "social_interaction",
    "physical_action", "change_transformation", "possession_transaction",
    "creation_destruction", "food_eating", "health_body", "time_sequence", "other"
]

PROMPT_TEMPLATE = """You are a Spanish linguistics expert. For each Spanish verb in the list below,
return a JSON array with one object per verb in the same order.

Each object must have exactly these fields:
- "infinitive": the verb as given
- "translationsEn": array of 1-4 English translations as infinitives (e.g. ["to speak", "to talk"])
- "translationsDe": array of 1-4 German translations as infinitives (e.g. ["sprechen", "reden"])
- "cefrLevel": one of exactly: A1, A2, B1, B2
- "thematicGroup": one of exactly: {groups}
- "isReflexive": true if the verb is inherently reflexive (e.g. levantarse), false otherwise
- "tags": array of strings for any additional tags (can be empty array [])

Rules:
- Prefer the most common, natural translations over literal ones
- For cefrLevel, use the level at which this verb is typically first introduced to learners
- Return ONLY the JSON array, no explanation or markdown

Verbs:
{verbs}"""


def build_prompt(verbs: list[str]) -> str:
    return PROMPT_TEMPLATE.format(
        groups=", ".join(THEMATIC_GROUPS),
        verbs="\n".join(f"- {v}" for v in verbs),
    )


def parse_response(text: str) -> list[dict] | None:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"  ERROR parsing JSON: {e}")
        print(f"  Raw response: {text[:300]}")
        return None


def validate_entry(entry: dict) -> list[str]:
    issues = []
    if not entry.get("translationsEn"):
        issues.append("missing translationsEn")
    if not entry.get("translationsDe"):
        issues.append("missing translationsDe")
    if entry.get("cefrLevel") not in VALID_CEFR:
        issues.append(f"invalid cefrLevel: {entry.get('cefrLevel')}")
    if entry.get("thematicGroup") not in THEMATIC_GROUPS:
        issues.append(f"invalid thematicGroup: {entry.get('thematicGroup')}")
    return issues


def process_batch(client: anthropic.Anthropic, verbs: list[str], attempt: int = 1) -> list[dict] | None:
    if attempt > 3:
        print("  ERROR: max retries reached for this batch")
        return None

    try:
        message = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=4096,
            messages=[{"role": "user", "content": build_prompt(verbs)}],
        )
        text = message.content[0].text
        entries = parse_response(text)
        if entries is None:
            print(f"  Retrying batch (attempt {attempt + 1})...")
            time.sleep(2)
            return process_batch(client, verbs, attempt + 1)
        return entries
    except anthropic.RateLimitError:
        wait = 30 * attempt
        print(f"  Rate limited — waiting {wait}s...")
        time.sleep(wait)
        return process_batch(client, verbs, attempt + 1)
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Copy data/scripts/.env.example to .env and fill it in.")
        sys.exit(1)

    with open(IN_PATH, encoding="utf-8") as f:
        conjugation_data = json.load(f)

    infinitives = [v["infinitive"] for v in conjugation_data]
    print(f"Enriching {len(infinitives)} verbs in batches of {BATCH_SIZE}...")

    client = anthropic.Anthropic(api_key=api_key)
    enrichment_map: dict[str, dict] = {}

    batches = [infinitives[i:i + BATCH_SIZE] for i in range(0, len(infinitives), BATCH_SIZE)]

    for batch_num, batch in enumerate(batches, 1):
        print(f"\nBatch {batch_num}/{len(batches)} ({len(batch)} verbs)...")
        entries = process_batch(client, batch)

        if entries is None:
            print(f"  SKIPPED batch {batch_num} — run again to retry")
            continue

        for entry in entries:
            issues = validate_entry(entry)
            if issues:
                print(f"  WARNING '{entry.get('infinitive')}': {', '.join(issues)}")
            enrichment_map[entry["infinitive"]] = entry

        print(f"  Done — {len(entries)} verbs enriched")
        # Small delay to avoid rate limits
        if batch_num < len(batches):
            time.sleep(1)

    # Merge enrichment into conjugation data
    results = []
    missing = []
    for verb_data in conjugation_data:
        infinitive = verb_data["infinitive"]
        enrichment = enrichment_map.get(infinitive)
        if not enrichment:
            missing.append(infinitive)
            results.append(verb_data)
            continue

        results.append({
            **verb_data,
            "translationsEn": enrichment.get("translationsEn", []),
            "translationsDe": enrichment.get("translationsDe", []),
            "cefrLevel": enrichment.get("cefrLevel", "A2"),
            "thematicGroup": enrichment.get("thematicGroup", "other"),
            "isReflexive": enrichment.get("isReflexive", False),
            "tags": enrichment.get("tags", []),
        })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone. {len(results)} verbs written to {OUT_PATH}")
    if missing:
        print(f"Missing enrichment for ({len(missing)}): {', '.join(missing)}")
        print("Re-run this script to retry missing verbs (already-enriched verbs are included in output).")


if __name__ == "__main__":
    main()
