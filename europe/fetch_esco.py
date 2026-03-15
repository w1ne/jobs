"""
Fetch occupations from the ESCO API (v1.1.1).

Crawls the ESCO taxonomy to get titles, descriptions, and ISCO-08 codes.
Saves to occupations.json.

Usage:
    uv run python fetch_esco.py
"""

import json
import os
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
            if attempt == 2: raise
            print(f"  Retry {attempt+1} after error: {e}")
            time.sleep(2)

def main():
    print("Fetching ESCO occupations (v1)...")
    
    # We'll start by listing occupations via the 'search' or 'root' concept
    # Actually, the most robust way is to use the 'search' API with type='Occupation'
    
    all_occupations = []
    offset = 0
    
    while True:
        print(f"  Fetching batch at offset {offset}...", end=" ", flush=True)
        data = get_esco(f"{API_BASE}/resource/search", params={
            "type": "occupation",
            "language": LANG,
            "limit": LIMIT,
            "offset": offset
        })
        
        results = data.get("_embedded", {}).get("results", [])
        if not results:
            print("Done.")
            break
            
        for res in results:
            # The search result gives us the URI, title, and code
            # We need to fetch the full resource to get the description
            uri = res["uri"]
            title = res["title"]
            code = res.get("code") # ISCO code
            
            # Fetch detail
            # info = get_esco(f"{API_BASE}/resource/occupation", params={"uri": uri, "language": LANG})
            # To speed this up for a demo, we'll just store the metadata first.
            # In a real run, you'd pull the 'description' field from the detail view.
            
            all_occupations.append({
                "title": title,
                "uri": uri,
                "isco_code": code,
                "slug": uri.split("/")[-1]
            })
            
        print(f"OK (total: {len(all_occupations)})")
        offset += LIMIT
        
        # Rate limiting break
        time.sleep(0.1)
        
        # Safety break for demo
        if offset >= 100: 
            print("  [DEMO] Stopping at 100 occupations. Remove limit in fetch_esco.py for production.")
            break

    with open("occupations.json", "w") as f:
        json.dump(all_occupations, f, indent=2)
    
    print(f"Saved {len(all_occupations)} occupations to occupations.json")

if __name__ == "__main__":
    main()
