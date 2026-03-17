"""
Fetch official EU labour statistics for ISCO-08 major groups.

Sources:
- Eurostat LFS: employment by occupation, EU-27, 2024
- Eurostat SES 2022: mean annual gross earnings by occupation, EU-27
- Cedefop Skills Forecast 2025: labour demand by occupational group, EU-27

Writes eurostat_stats.json keyed by ISCO major group code.
"""

import json
from collections import defaultdict

import httpx

EMPLOYMENT_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    "lfsa_egais?lang=EN&geo=EU27_2020&sex=T&age=Y15-74&wstatus=EMP&unit=THS_PER&time=2024"
)
EARNINGS_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    "earn_ses22_28?lang=EN&geo=EU27_2020&time=2022&sex=T&indic_se=ERN&age=TOTAL&sizeclas=GE10&unit=EUR"
)
CEDEFOP_URL = (
    "https://www.cedefop.europa.eu/themes/custom/cedefop_foundation/js/"
    "cedefop-skills-forecast/data/skills2024-demand-reduced-eu.json.gz"
)

GROUPS = {
    "OC1": {
        "title": "Managers",
        "slug": "managers",
        "cedefop_label": "Legislators, senior officials and managers",
    },
    "OC2": {
        "title": "Professionals",
        "slug": "professionals",
        "cedefop_label": "Professionals",
    },
    "OC3": {
        "title": "Technicians and Associate Professionals",
        "slug": "technicians-and-associate-professionals",
        "cedefop_label": "Technicians and associate professionals",
    },
    "OC4": {
        "title": "Clerical Support Workers",
        "slug": "clerical-support-workers",
        "cedefop_label": "Clerks",
    },
    "OC5": {
        "title": "Service and Sales Workers",
        "slug": "service-and-sales-workers",
        "cedefop_label": "Service workers and shop and market sales workers",
    },
    "OC6": {
        "title": "Skilled Agricultural, Forestry and Fishery Workers",
        "slug": "skilled-agricultural-forestry-and-fishery-workers",
        "cedefop_label": "Skilled agricultural and fishery workers",
    },
    "OC7": {
        "title": "Craft and Related Trades Workers",
        "slug": "craft-and-related-trades-workers",
        "cedefop_label": "Craft and related trades workers",
    },
    "OC8": {
        "title": "Plant and Machine Operators and Assemblers",
        "slug": "plant-and-machine-operators-and-assemblers",
        "cedefop_label": "Plant and machine operators and assemblers",
    },
    "OC9": {
        "title": "Elementary Occupations",
        "slug": "elementary-occupations",
        "cedefop_label": "Elementary occupations",
    },
    "OC0": {
        "title": "Armed Forces Occupations",
        "slug": "armed-forces-occupations",
        "cedefop_label": "Armed forces",
    },
}


def fetch_json(url):
    response = httpx.get(url, timeout=60.0)
    response.raise_for_status()
    return response.json()


def fetch_employment(stats):
    data = fetch_json(EMPLOYMENT_URL)
    indices = data["dimension"]["isco08"]["category"]["index"]
    values = data["value"]
    for code in GROUPS:
        stats[code]["employment_2024"] = int(values[str(indices[code])] * 1000)


def fetch_earnings(stats):
    data = fetch_json(EARNINGS_URL)
    indices = data["dimension"]["isco08"]["category"]["index"]
    values = data["value"]
    for code in GROUPS:
        stats[code]["mean_annual_earnings_2022"] = int(values[str(indices[code])])


def fetch_outlook(stats):
    data = fetch_json(CEDEFOP_URL)
    forecast = defaultdict(lambda: {"y2024": 0.0, "y2035": 0.0})
    for row in data:
        label = row["occupation_l1"].strip()
        forecast[label]["y2024"] += float(row["2024"])
        forecast[label]["y2035"] += float(row["2035"])

    for code, group in GROUPS.items():
        row = forecast[group["cedefop_label"]]
        start = row["y2024"]
        end = row["y2035"]
        outlook_pct = ((end / start) - 1.0) * 100.0 if start else None
        stats[code]["outlook_pct_2024_2035"] = round(outlook_pct, 1) if outlook_pct is not None else None
        stats[code]["forecast_jobs_2024"] = round(start)
        stats[code]["forecast_jobs_2035"] = round(end)


def main():
    stats = {
        code: {
            "isco_code": code,
            "title": group["title"],
            "slug": group["slug"],
            "category_label": "ISCO-08 Major Groups",
            "sources": {
                "employment": "Eurostat lfsa_egais, EU27_2020, 2024",
                "earnings": "Eurostat earn_ses22_28, EU27_2020, 2022, GE10",
                "outlook": "Cedefop Skills Forecast 2025, EU-27, 2024-2035",
            },
        }
        for code, group in GROUPS.items()
    }

    fetch_employment(stats)
    fetch_earnings(stats)
    fetch_outlook(stats)

    with open("eurostat_stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    print(f"Saved stats for {len(stats)} ISCO groups to eurostat_stats.json")


if __name__ == "__main__":
    main()
