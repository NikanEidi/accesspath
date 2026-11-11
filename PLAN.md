# AccessPath — Project Plan

> **Status:** Planning / learning phase (started 2026-11-10) · **Owner:** Nikan Eidi · **Type:** Personal project (safe to publish on public GitHub)
> **Code lives in its own repo:** `~/Desktop/Nikan/accesspath` → later `github.com/NikanEidi/accesspath`. This folder (in nikan-career-assistant) holds a pointer to the plan only.

## 1. What we are building

An accessibility-aware route-finding system. Given a start and end point, it finds the best route using a real road/sidewalk graph (from OpenStreetMap), real travel-time weights (not straight-line distance), and accessibility constraints (wheelchair access, sidewalk surface) pulled from OSM tags. On top of the deterministic routing, a learned model predicts travel time per road segment based on time-of-day/day-of-week patterns.

**Why this project (the gap it closes, and the differentiation):**
- General routing apps (Google Maps) barely support accessibility-aware walking routes — this is a real, underserved niche, not a head-on competition with their live-GPS-fleet moat.
- Combines classic graph algorithms (Dijkstra/A*) with a real ML component (regression baseline → GNN), reusing and extending graph-ML experience from the GraphCart project (RelBench).
- Fully explainable: unlike Google's black-box routing, every edge weight and routing decision can be shown and justified.

## 2. Modules

| # | Module | What it does |
|---|--------|--------------|
| 1 | **Data ingestion** (`src/data/`) | Download/parse OpenStreetMap data for a target area (starting with a Newmarket/Toronto-area bounding box) |
| 2 | **Graph construction** (`src/graph/`) | Convert OSM nodes/ways/tags into a weighted graph (edge weight = Haversine distance, adjusted by road type and accessibility tags) |
| 3 | **Routing** (`src/routing/`) | Dijkstra and A* pathfinding over the graph, with accessibility profiles (e.g. wheelchair, stroller) that penalize or exclude certain edges |
| 4 | **Travel-time prediction** (`src/ml/`) | Baseline: regression model (Random Forest / Gradient Boosting) predicting per-edge travel time from time-of-day/day-of-week features. Stretch: a Graph Neural Network that also uses neighboring-edge structure, compared against the baseline |
| 5 | **Visualization** (`visualize/`) | Plot the road graph and a found route on a real map (e.g. with `folium` or `plotly`) |

## 3. Engineering ideas that make it real (not a toy)

| Topic | Why it matters |
|-------|-----------------|
| Haversine distance | Correct great-circle distance on a sphere, not flat-plane math — the real-world base unit for every edge weight |
| OSM tags as accessibility signal | `wheelchair=yes/no/limited`, `surface=*`, `kerb=*` drive real routing decisions, not a fake synthetic feature |
| A* with Haversine as the heuristic | Faster search than plain Dijkstra, using straight-line distance only as a lower-bound estimate, never as the actual route cost |
| Time-based train/test split | Predicting the future from the past — never a random shuffle, which would leak information (the same lesson learned the hard way on GraphCart) |
| Baseline-before-complexity | A simple regression model ships first and is the yardstick the GNN has to actually beat — a defensible "I measured it, not just assumed it" story |

## 4. Tech stack

- Python
- `osmnx` + `networkx` — OSM download/parsing and graph representation
- `geopy` (or hand-rolled Haversine) — distance calculations
- `scikit-learn` — regression baseline
- A GNN framework (PyTorch Geometric or similar) — stretch goal
- `folium` / `plotly` — map visualization

## 5. Datasets

- OpenStreetMap (via `osmnx`) for the road/sidewalk graph and accessibility tags.
- For travel-time/traffic patterns: a standard traffic-forecasting benchmark (METR-LA or PEMS-BAY) to start, or Toronto Open Data if a good local source is found.

## 6. Learning notes

See `notes/` in the actual repo (`~/Desktop/Nikan/accesspath/notes/`), numbered from `00`, one concept per file, in Nikan's own words — covers Haversine, graphs and shortest-path algorithms, the OSM data model, and regression vs. GNN.
