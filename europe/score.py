"""
Score each European occupation's AI exposure using an LLM.

Reads from occupations.json (ESCO list), uses descriptions to score 0-10.
"""

import argparse
import json
import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "google/gemini-2.0-flash-001"
OUTPUT_FILE = "scores.json"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """\
You are an expert analyst evaluating how exposed different occupations are to AI. \
You will be given a title and description of an occupation from the ESCO \
(European Skills, Competences, Qualifications and Occupations) classification.

Rate the occupation's overall **AI Exposure** on a scale from 0 to 10.

AI Exposure measures: how much will AI reshape this occupation? Consider both \
direct effects (AI automating tasks currently done by humans) and indirect \
effects (AI making each worker so productive that fewer are needed).

Calibration anchors (EU context):
- 0–1: Minimal (e.g., Roofer, Fisher, Physical Laborer)
- 4–5: Moderate (e.g., Nurse, Police Officer, Shop Salesperson)
- 8–9: Very high (e.g., Software Developer, Financial Analyst, Translator)
- 10: Maximum (e.g., Data Entry Clerk)

Respond with ONLY a JSON object:
{
  "exposure": <0-10>,
  "rationale": "<2-3 sentences explaining the key factors>"
}
"""

def score_occupation(client, title, description, model):
    response = client.post(
        API_URL,
        headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Occupation: {title}\nDescription: {description}"},
            ],
            "temperature": 0.1,
        },
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
    return json.loads(content)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=None)
    args = parser.parse_args()

    if not os.path.exists("occupations.json"):
        print("Run fetch_esco.py first.")
        return

    with open("occupations.json") as f:
        occupations = json.load(f)

    subset = occupations[args.start:args.end]
    scores = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            scores = json.load(f)

    scored_uris = {s["uri"] for s in scores}
    client = httpx.Client()

    print(f"Scoring {len(subset)} occupations...")
    for idx, occ in enumerate(subset):
        if occ["uri"] in scored_uris:
            continue
        
        print(f"  [{idx+1}/{len(subset)}] {occ['title']}...", end=" ", flush=True)
        try:
            # Note: For demo we use title as description if desc isn't fetched yet
            desc = occ.get("description", "No detailed description available.")
            res = score_occupation(client, occ["title"], desc, args.model)
            scores.append({**occ, **res})
            print(f"exposure={res['exposure']}")
            
            with open(OUTPUT_FILE, "w") as f:
                json.dump(scores, f, indent=2)
        except Exception as e:
            print(f"FAILED: {e}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()
