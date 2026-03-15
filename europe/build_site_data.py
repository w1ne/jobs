"""
Build site/data.json for the European AI Exposure website.
Merges scores and Eurostat statistics.
"""

import json
import os

def main():
    if not os.path.exists("scores.json") or not os.path.exists("eurostat_stats.json"):
        print("Run score.py and fetch_eurostat.py first. (Using demo data for now)")
        # Create a tiny demo dataset if files missing
        data = [
            {"title": "Software Developer", "category": "Professionals", "pay": 55000, "jobs": 2100000, "exposure": 8, "exposure_rationale": "Core tasks are digital and information-based."},
            {"title": "Construction Worker", "category": "Craft and related trades", "pay": 28000, "jobs": 4500000, "exposure": 1, "exposure_rationale": "High physical component in unstructured environments."},
            {"title": "Financial Analyst", "category": "Professionals", "pay": 62000, "jobs": 800000, "exposure": 9, "exposure_rationale": "Data-heavy quantitative analysis is highly susceptible."},
            {"title": "Nurse", "category": "Professionals", "pay": 38000, "jobs": 3200000, "exposure": 4, "exposure_rationale": "Mix of physical care and digital record keeping."},
        ]
    else:
        with open("scores.json") as f:
            scores = json.json.load(f)
        with open("eurostat_stats.json") as f:
            euro_stats = json.load(f)

        data = []
        for s in scores:
            isco = s.get("isco_code", "")
            major_group = isco[0] if isco else "unknown"
            stats = euro_stats.get(major_group, {})
            
            # Simple heuristic: split major group employment across its occupations
            # In a real app, you'd use weights or more granular stats if available.
            data.append({
                "title": s["title"],
                "slug": s["slug"],
                "category": f"ISCO Group {major_group}",
                "pay": stats.get("median_pay_annual"),
                "jobs": stats.get("employment", 10000) // 100, # Mock split
                "exposure": s["exposure"],
                "exposure_rationale": s["rationale"],
                "education": "Varies",
                "outlook": 2, # Default outlook
                "url": s["uri"]
            })

    os.makedirs("site", exist_ok=True)
    with open("site/data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Wrote {len(data)} items to site/data.json")

if __name__ == "__main__":
    main()
