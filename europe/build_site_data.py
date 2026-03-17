"""
Build site/data.json for the European AI Exposure website.

Produces a grouped EU dataset based on official labour statistics:
- Eurostat employment (2024)
- Eurostat mean annual earnings (2022)
- Cedefop outlook (2024-2035)

AI exposure remains an estimated layer added on top of those official sources.
"""

import json
import os


EXPOSURE_MAP = {
    "OC1": {
        "exposure": 6,
        "education": "Bachelor's degree",
        "rationale": "Managerial work includes planning, reporting, coordination, and decision support tasks that AI can augment heavily, but accountability, negotiation, and organizational authority still limit full substitution.",
    },
    "OC2": {
        "exposure": 7,
        "education": "Bachelor's degree",
        "rationale": "Professional work is often knowledge-dense and document-heavy, making it highly exposed to AI augmentation, although expert judgment, licensing, and client-facing responsibility still matter.",
    },
    "OC3": {
        "exposure": 6,
        "education": "Bachelor's degree",
        "rationale": "Technical support and applied analytical roles contain many structured digital tasks that AI can speed up, but fieldwork, equipment interaction, and operational troubleshooting remain important constraints.",
    },
    "OC4": {
        "exposure": 9,
        "education": "High school diploma",
        "rationale": "Clerical work is among the most exposed categories because much of it involves routine documentation, scheduling, record handling, and information transfer that AI systems can automate directly.",
    },
    "OC5": {
        "exposure": 4,
        "education": "High school diploma",
        "rationale": "Service and sales work mixes some automatable information tasks with in-person interaction, persuasion, physical presence, and context-specific customer handling.",
    },
    "OC6": {
        "exposure": 2,
        "education": "High school diploma",
        "rationale": "Agricultural and fishery work depends heavily on physical environments, machinery, weather, and manual execution, which keeps direct AI substitution relatively limited.",
    },
    "OC7": {
        "exposure": 3,
        "education": "High school diploma",
        "rationale": "Skilled trades involve embodied work in variable real-world conditions, so AI is more likely to assist planning and diagnostics than replace core execution.",
    },
    "OC8": {
        "exposure": 4,
        "education": "High school diploma",
        "rationale": "Plant and machine operation includes standardized processes that can be optimized by automation, but supervision, safety, maintenance, and real-world variability still require people.",
    },
    "OC9": {
        "exposure": 2,
        "education": "High school diploma",
        "rationale": "Elementary occupations still rely heavily on physical execution and site-specific work, leaving AI with a more limited direct role than in office-based occupations.",
    },
    "OC0": {
        "exposure": 3,
        "education": "Bachelor's degree",
        "rationale": "Armed forces occupations can use AI extensively for planning, intelligence, and support, but operational command, training, and mission execution retain strong human constraints.",
    },
}

GROUP_ORDER = ["OC1", "OC2", "OC3", "OC4", "OC5", "OC6", "OC7", "OC8", "OC9", "OC0"]


def main():
    if not os.path.exists("eurostat_stats.json"):
        raise SystemExit("Missing eurostat_stats.json. Run fetch_eurostat.py first.")

    with open("eurostat_stats.json") as f:
        stats = json.load(f)

    data = []
    for code in GROUP_ORDER:
        row = stats[code]
        exposure = EXPOSURE_MAP[code]
        data.append({
            "title": row["title"],
            "slug": row["slug"],
            "category": row["category_label"],
            "pay": row.get("mean_annual_earnings_2022"),
            "jobs": row.get("employment_2024"),
            "outlook": row.get("outlook_pct_2024_2035"),
            "outlook_desc": "Projected change in Cedefop labour demand from 2024 to 2035",
            "education": exposure["education"],
            "exposure": exposure["exposure"],
            "exposure_rationale": exposure["rationale"],
            "url": "",
        })

    os.makedirs("site", exist_ok=True)
    with open("site/data.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"Wrote {len(data)} occupational groups to site/data.json")


if __name__ == "__main__":
    main()
