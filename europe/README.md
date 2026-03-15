# AI Exposure of the European Job Market

Analysing how susceptible every occupation in the EU economy is to AI and automation, using data from the [ESCO classification](https://esco.ec.europa.eu/) (European Skills, Competences, Qualifications and Occupations) and [Eurostat](https://ec.europa.eu/eurostat/) Labour Force Survey / Structure of Earnings Survey.

The European counterpart to [karpathy/jobs](https://github.com/karpathy/jobs) (US BLS edition).

## What's here

ESCO covers **~3 000 occupations** organised into ISCO-08 major groups spanning the entire EU economy. We fetch the list and descriptions via the ESCO REST API, pull employment and wage statistics from Eurostat, score each occupation's AI exposure using an LLM, and render an interactive treemap.

## Data pipeline

1. **Fetch occupations** (`fetch_esco.py`) — calls the ESCO API to download all occupation titles, URIs, descriptions, and ISCO-08 codes into `occupations.json`.
2. **Fetch Eurostat stats** (`fetch_eurostat.py`) — downloads EU-wide employment counts (LFS) and median annual wages (Structure of Earnings Survey) by ISCO-08 sub-major group; writes `eurostat_stats.json`.
3. **Score** (`score.py`) — sends each occupation's description to an LLM via OpenRouter. Results saved incrementally to `scores.json`.
4. **Build site data** (`build_site_data.py`) — merges ESCO descriptions, Eurostat stats, and AI exposure scores into `site/data.json`.
5. **Website** (`site/index.html`) — interactive treemap; area = employment, colour = AI exposure.

## Data sources

| Source | What it provides |
|--------|-----------------|
| [ESCO API v1](https://esco.ec.europa.eu/en/use-esco/esco-api) | Occupation titles, descriptions, ISCO-08 mapping |
| [Eurostat LFS `lfsa_egised`](https://ec.europa.eu/eurostat/databrowser/view/lfsa_egised) | Employment by ISCO major group, EU27 |
| [Eurostat SES `earn_ses_pub1a`](https://ec.europa.eu/eurostat/databrowser/view/earn_ses_pub1a) | Median hourly wages by ISCO, EU27 |
| [Cedefop Skills Forecast](https://www.cedefop.europa.eu/en/tools/skills-intelligence) | 10-year employment growth projections |

## Key files

| File | Description |
|------|-------------|
| `occupations.json` | ESCO occupation list with ISCO-08 codes and API URIs |
| `eurostat_stats.json` | Employment + wage data per ISCO sub-major group |
| `scores.json` | AI exposure scores (0–10) with rationales |
| `site/data.json` | Merged dataset for the frontend |
| `site/index.html` | Interactive treemap visualisation |

## AI exposure scoring

Identical rubric to the US edition — see the parent repo's README. Scores run 0 (roofer, dockworker) to 10 (data-entry clerk). Average across EU occupations is expected around 5.0–5.5.

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
# 1. Download ESCO occupation list + descriptions (~3 000 occupations, ~10 min)
uv run python fetch_esco.py

# 2. Download Eurostat employment/wage stats (fast, uses REST API)
uv run python fetch_eurostat.py

# 3. Score AI exposure with an LLM (takes ~2 h for full dataset)
uv run python score.py
# or test on a small slice first:
uv run python score.py --start 0 --end 20

# 4. Build the site data file
uv run python build_site_data.py

# 5. Serve the site
cd site && python -m http.server 8000
```

## Quick demo (pre-seeded data)

The repo ships `site/data.json` pre-populated with ~130 representative ISCO-08 3-digit groups and realistic EU statistics so you can view the site immediately without running the full pipeline:

```bash
cd europe/site && python -m http.server 8000
# open http://localhost:8000
```
