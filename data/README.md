# Datasets

## Real data

Real road/sidewalk graphs are **not stored here** — they're downloaded on demand from OpenStreetMap via `osmnx` (see `notebooks/01`, `04`), and cached automatically by `osmnx` under `notebooks/cache/` (gitignored, regenerable, not a committed dataset).

- **Ken Sturgeon Park, Newmarket** — first small test area (9 nodes, 22 edges).
- **Financial District, Toronto** — first real coverage test (834 nodes, 2372 edges). 0 real `wheelchair: no` tags found here.
- **Downtown Toronto** — larger-scale real test (14,123 nodes, 39,170 edges). 178 edges with a real `wheelchair` tag, 16 of them `wheelchair: no`, 25,518 with a `surface` tag. Used as the real-world labeled dataset for the Module 6 baseline classifier — found to be too small/imbalanced for a reliable classifier (see `notes/06-accessibility-prediction-baseline.md`).

External datasets were researched as a second real-world source (Project Sidewalk, RampNet, City of Toronto Open Data) and none provided path-level wheelchair/curb-ramp accessibility data for Toronto — see `notes/07-external-dataset-search.md` for the full search and why each one didn't fit.

## Synthetic data: Clearwell

Because real accessibility-tag coverage (above) was too sparse to properly validate a GNN against a baseline, **Clearwell** is a fully fictional, hand-designed benchmark city — built directly with `networkx` (not `osmnx`, since there's no real place to download: `osmnx` only fetches real OpenStreetMap data, which doesn't exist for a made-up city). Stored as a single JSON file (`clearwell.json`, via `nx.node_link_data`/`nx.node_link_graph`), loadable as an ordinary `networkx` graph — every function already built (`accessibility_weight`, `find_accessible_route`, `find_edges_with_tag`) works on it unmodified.

Four neighborhoods, each designed to isolate one specific test:

| Neighborhood | Design | What it tests |
|---|---|---|
| **Old Town** | Sparse, mostly-untagged edges (mirrors real OSM data) | GNN/baseline accessibility *prediction* for untagged edges |
| **Riverside District** | Fully tagged, balanced mix of accessible/inaccessible | Main **training** data — real signal, not a 91%/9% imbalance like the real dataset |
| **University Quarter** | Dense, modern, mostly `wheelchair: yes/designated` | **Routing** tests — a rich network with many real route choices to compare |
| **Industrial Row** | Bad surface (`gravel`/`dirt`) combined with `wheelchair: no` | Stress-tests the **weighting system** under a combined, compounding penalty |

Clearly labeled as a synthetic benchmark everywhere it's used (notes, résumé-facing descriptions) — it validates that the pipeline (weighting → routing → GNN vs. baseline) works correctly under controlled, sufficient data, which the real-world data couldn't support on its own. Not a substitute for real-world validation, which stays documented as a known, honest limitation (see `notes/07`).
