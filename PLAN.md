# AccessPath — Project Plan

> **Status:** Planning / learning phase (started 2026-11-10) · **Owner:** Nikan Eidi · **Type:** Personal project (safe to publish on public GitHub)
> **Code lives in its own repo:** `~/Desktop/Nikan/accesspath` → later `github.com/NikanEidi/accesspath`. This folder (in nikan-career-assistant) holds a pointer to the plan only.

## 1. What we are building

An accessibility-aware route-finding system. Given a start and end point, it finds the best route using a real road/sidewalk graph (from OpenStreetMap), real distance weights (Haversine, not straight-line guesses), and accessibility constraints (wheelchair access, sidewalk surface) pulled from OSM tags. On top of the deterministic routing, a learned model predicts accessibility for edges that have no OSM tag at all.

**Pivot (2026-11-12):** the original plan here was a travel-time-by-time-of-day prediction layer (regression baseline vs. GNN). Dropped after realizing it doesn't actually fit this project: time-of-day traffic variability is a driving-app problem, not a walking/accessibility one (pedestrian speed doesn't swing with rush hour the way vehicle speed does), and there's no real local dataset for it anyway. Replaced with a better-motivated ML task that uses data this project already has: **predicting accessibility for untagged edges** (the real gap found in Module 4 — only 178 of 39,170 Downtown Toronto edges have a `wheelchair` tag at all) from each edge's own attributes (`highway` type, `surface`, `street_count`) plus its position in the graph. This is also a more natural GNN use case: an edge's accessibility is plausibly correlated with its neighbors' (same block, same path), which is exactly the kind of signal a GNN propagates and a plain regression baseline can't see.

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
| 4 | **Accessibility prediction for untagged edges** (`src/ml/`) | Baseline: a classifier (Random Forest / Logistic Regression) predicting likely accessibility from an edge's own attributes (`highway`, `surface`, `street_count`). Stretch: a Graph Neural Network that also uses neighboring-edge/node structure, compared against the baseline on held-out, geographically-split real tagged edges |
| 5 | **Visualization** (`visualize/`) | Plot the road graph and a found route on a real map (e.g. with `folium` or `plotly`) |

## 3. Engineering ideas that make it real (not a toy)

| Topic | Why it matters |
|-------|-----------------|
| Haversine distance | Correct great-circle distance on a sphere, not flat-plane math — the real-world base unit for every edge weight |
| OSM tags as accessibility signal | `wheelchair=yes/no/limited`, `surface=*`, `kerb=*` drive real routing decisions, not a fake synthetic feature |
| A* with Haversine as the heuristic | Faster search than plain Dijkstra, using straight-line distance only as a lower-bound estimate, never as the actual route cost |
| Geography-based train/test split | Held-out edges come from a different area than training, never a random shuffle — otherwise two nearby edges with near-identical features/neighbors could land on both sides of the split, leaking information (the same lesson learned the hard way on GraphCart, just spatial instead of temporal here) |
| Baseline-before-complexity | A simple regression model ships first and is the yardstick the GNN has to actually beat — a defensible "I measured it, not just assumed it" story |

## 4. Tech stack

- Python
- `osmnx` + `networkx` — OSM download/parsing and graph representation
- `geopy` (or hand-rolled Haversine) — distance calculations
- `scikit-learn` — regression baseline
- A GNN framework (PyTorch Geometric or similar) — stretch goal
- `folium` / `plotly` — map visualization

## 5. Datasets

- OpenStreetMap (via `osmnx`) for the road/sidewalk graph, accessibility tags, and the labels for the accessibility-prediction task itself (the ~178 real tagged edges found in Downtown Toronto).

## 6. Learning notes

See `notes/` in the actual repo (`~/Desktop/Nikan/accesspath/notes/`), numbered from `00`, one concept per file, in Nikan's own words — covers Haversine, graphs and shortest-path algorithms, the OSM data model, and regression vs. GNN.
