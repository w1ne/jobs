# AI Exposure of the European Job Market

Analysing how susceptible every occupation in the EU economy is to AI and automation, using data from the [ESCO classification](https://esco.ec.europa.eu/) (European Skills, Competences, Qualifications and Occupations) and [Eurostat](https://ec.europa.eu/eurostat/) Labour Force Survey / Structure of Earnings Survey.

The European counterpart to [karpathy/jobs](https://github.com/karpathy/jobs) (US BLS edition).

## What's here

This European build now ships an official-source grouped dataset based on **10 ISCO-08 major groups** spanning the EU economy. Employment comes from Eurostat LFS, earnings from Eurostat SES, outlook from Cedefop Skills Forecast, and AI exposure is estimated at the group level.

## Data pipeline

1. **Fetch official labour stats** (`fetch_eurostat.py`) — downloads Eurostat employment and earnings data plus Cedefop forecast data for ISCO-08 major groups; writes `eurostat_stats.json`.
2. **Build site data** (`build_site_data.py`) — merges official labour stats with estimated AI exposure scores into `site/data.json`.
3. **Website** (`site/index.html`) — interactive treemap; area = employment, colour = AI exposure.

## Data sources

| Source | What it provides |
|--------|-----------------|
| [Eurostat LFS `lfsa_egais`](https://ec.europa.eu/eurostat/databrowser/view/lfsa_egais/default/table?lang=en) | Employment by occupation, EU27 |
| [Eurostat SES `earn_ses22_28`](https://ec.europa.eu/eurostat/databrowser/view/earn_ses22_28/default/table?lang=en) | Mean annual earnings by occupation, EU27 |
| [Cedefop Skills Forecast](https://www.cedefop.europa.eu/en/tools/skills-intelligence) | 10-year employment growth projections |

## Key files

| File | Description |
|------|-------------|
| `eurostat_stats.json` | Employment, earnings, and outlook data per ISCO major group |
| `site/data.json` | Merged dataset for the frontend |
| `site/index.html` | Interactive treemap visualisation |

## AI exposure scoring

AI exposure is still an estimated layer rather than an official statistic. In this grouped EU build, scores are assigned at the ISCO major-group level using the same rubric as the US edition.

## Setup

```bash
cd europe/
uv sync
```

Requires an OpenRouter API key in `.env` (in the `europe/` directory):
```
OPENROUTER_API_KEY=your_key_here
```

## Usage

```bash
# 1. Download Eurostat/Cedefop group statistics
uv run python fetch_eurostat.py

# 2. Build the site data file
uv run python build_site_data.py

# 3. Serve the site
cd site && python -m http.server 8000
```

## Quick demo (pre-seeded data)

The repo ships `site/data.json` pre-populated with the grouped official-source EU dataset so you can view the site immediately:

```bash
cd europe/site && python -m http.server 8000
# open http://localhost:8000
```
