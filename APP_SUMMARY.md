# Peled Index App Summary

## App intent
Peled Index is an author-level research scoring app. It enriches publication titles with Crossref metadata, joins journals to SCImago SJR/fields, computes a normalized `author_score`, and exposes search + percentile visualization in a web interface.

## How the system works
1. **Input authors** are loaded from JSON with `name`, `start_year`, and `publications`.
2. **Crossref enrichment** resolves publication title matches, DOI URL, year, venue, citation count, ISSNs, and authorship/preprint flags.
3. **SCImago enrichment** maps ISSNs to SJR values and broad fields.
4. **Scoring** computes per-paper score from citations/year and SJR, weights by first authorship, excludes preprints/invalid-year papers, then normalizes by active years.
5. **Serving layer** loads precomputed results into memory, supports search/details/plot APIs, and renders a static frontend.
6. **Scholar-on-demand path** can search Google Scholar profiles (via SerpAPI), scrape paper titles, score the author, and add the result to in-memory state.

## Core product behavior (user perspective)
- Search an author by name.
- Open an author card with institution, score, total papers, and fields.
- See percentile ranking plots by field.
- If not found, resolve via Scholar profile lookup and compute a score on demand.

## Project structure at a glance
- `core/`: enrichment, scoring pipeline, plotting, Scholar integration.
- `web/`: FastAPI app + API handlers + static frontend.
- `data/`: precomputed results JSON consumed at app startup.
- root-level `helpers.py`/`pipeline.py`/`plots.py`/`main.py`: legacy duplicates while active imports come from `core/` and `web/`.

## Notes on intent alignment
- The current implementation aligns with the stated intent to produce a practical author ranking pipeline and expose it as a searchable UI.
- The design intentionally keeps pipeline execution offline/batch while the web service remains mostly read-only against precomputed data, with Scholar-based scoring as an optional dynamic extension.
