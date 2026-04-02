# peled-index

Compute an author-level research score from a JSON list of authors and publication titles by enriching metadata via Crossref and journal SJR/fields via SCImago (SJR 2024 dataset in this repo).

## What it does

For each author in an input JSON file, the pipeline:
- queries Crossref for each publication title (+ author name) and selects a best match
- extracts: DOI URL, year, venue, citation count, journal ISSNs, first-author flag, preprint flag
- looks up SCImago SJR and mapped high-level fields by ISSN (from `scimagojr2024.csv`)
- computes an `author_score` from citations/year and journal SJR, normalized by active years
- writes a results JSON file with per-author details and per-paper enrichment

There is also a plotting script to visualize where a candidate ranks (percentile) within their fields.

## Repo layout

- `main.py` - example entrypoint that runs the pipeline
- `pipeline.py` - orchestration + scoring logic
- `helpers.py` - Crossref + SCImago parsing and matching helpers
- `plots.py` - percentile + histogram plots from the produced results JSON
- `scimagojr2024.csv` - SCImago Journal Rank dataset (semicolon-delimited)
- `intent.txt` - coding/style guidelines for future changes

## Input format (JSON)

The pipeline expects a JSON array of author objects. Minimum fields used:
- `name` (string)
- `start_year` (number/string parseable to int)
- `publications` (array of strings; paper titles)

Optional:
- `institution` (string)

Example:
```json
[
  {
    "name": "Ada Lovelace",
    "institution": "Example University",
    "start_year": 2018,
    "publications": [
      "A Paper Title",
      "Another Paper Title"
    ]
  }
]
```

## Output format (JSON)

The output is a JSON array, one entry per author, with:
- `author_score`
- `total_papers`
- `fields` (mapped high-level fields)
- `papers` (enriched paper records: year, citations, doi url, SJR, flags, etc.)

## How to run

### 1) Install dependencies

This repo currently does not include a `requirements.txt`. Based on imports, you likely need:
- `requests`
- `ftfy`
- (for plotting) `numpy`, `matplotlib`

Install (example):
```bash
python -m pip install requests ftfy numpy matplotlib
```

### 2) Run the pipeline

`main.py` is currently hard-coded to local Windows paths. Update these three paths before running:
- `input_json_path`
- `output_json_path`
- `scimago_file_path` (can point to `./scimagojr2024.csv`)

Then:
```bash
python main.py
```

Alternatively, call the function directly:
```python
from pipeline import run_pipeline

run_pipeline('input.json', 'out.json', 'scimagojr2024.csv')
```

### 3) Plot candidate percentile (optional)

`plots.py` is also hard-coded (results path + candidate name). Update:
- `RESULTS_JSON_PATH`
- `CANDIDATE_NAME`

Then:
```bash
python plots.py
```
