"""
Fetch occupations from the ESCO API (v1.1.1).

Crawls the ESCO taxonomy to get titles, descriptions, and ISCO-08 codes.
Saves to occupations.json.

Usage:
    uv run python fetch_esco.py
"""

import argparse
import json
import time
import httpx

API_BASE = "https://ec.europa.eu/esco/api"
LANG = "en"
LIMIT = 20  # Batch size for search/list

def get_esco(url, params=None):
    """Helper to call ESCO API with retries."""
    for attempt in range(3):
        try:
            resp = httpx.get(url, params=params, timeout=30.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt == 2:
                raise
            print(f"  Retry {attempt+1} after error: {e}")
            time.sleep(2)


def extract_text(value):
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in ("literal", "value", "@value", "en"):
            text = extract_text(value.get(key))
            if text:
                return text
        for nested in value.values():
            text = extract_text(nested)
            if text:
                return text
    if isinstance(value, list):
        for item in value:
            text = extract_text(item)
            if text:
                return text
    return None


def extract_description(payload):
    for key in ("description", "definition", "scopeNote"):
        text = extract_text(payload.get(key))
        if text:
            return text
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", default=LANG)
    parser.add_argument("--batch-size", type=int, default=LIMIT)
    parser.add_argument("--max-occupations", type=int, default=None)
    args = parser.parse_args()

    print("Fetching ESCO occupations (v1)...")

    all_occupations = []
    offset = 0

    while True:
        print(f"  Fetching batch at offset {offset}...", end=" ", flush=True)
        data = get_esco(f"{API_BASE}/resource/search", params={
            "type": "occupation",
            "language": args.language,
            "limit": args.batch_size,
            "offset": offset
        })

        results = data.get("_embedded", {}).get("results", [])
        if not results:
            print("Done.")
            break

        for res in results:
            uri = res["uri"]
            title = res["title"]
            code = res.get("code")
            detail = get_esco(f"{API_BASE}/resource/occupation", params={
                "uri": uri,
                "language": args.language,
            })

            all_occupations.append({
                "title": title,
                "uri": uri,
                "isco_code": code,
                "slug": uri.split("/")[-1],
                "description": extract_description(detail),
            })

            if args.max_occupations is not None and len(all_occupations) >= args.max_occupations:
                break

        print(f"OK (total: {len(all_occupations)})")
        offset += args.batch_size

        time.sleep(0.1)

        if args.max_occupations is not None and len(all_occupations) >= args.max_occupations:
            print(f"  Reached requested cap of {args.max_occupations} occupations.")
            break

    with open("occupations.json", "w") as f:
        json.dump(all_occupations, f, indent=2)

    print(f"Saved {len(all_occupations)} occupations to occupations.json")

if __name__ == "__main__":
    main()
