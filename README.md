# AccessPath

An accessibility-aware route-finding project: given a start and end point, find the best route not just by raw distance, but by **real accessibility** (wheelchair access, sidewalk surface, construction closures, stairs) — something general-purpose routing apps like Google Maps barely support for walking directions.

On top of deterministic routing, a Graph Neural Network predicts accessibility for road segments that have no OSM tag at all, and is honestly compared against a simple baseline classifier.

## Why this project

Most route-finding demos stop at "shortest path." AccessPath goes further:
- Builds a real road/sidewalk graph from OpenStreetMap data (not a toy grid) using `osmnx`/`networkx`.
- Computes real-world distances with the Haversine formula (great-circle distance on a sphere, not flat-plane math).
- Finds routes with Dijkstra / A* using accessibility-aware weights — a route can be forced to avoid untagged stairs, temporary construction closures, or bad surfaces, not just minimize distance.
- Predicts accessibility for untagged edges with a hand-rolled Graph Neural Network (plain PyTorch, no PyTorch Geometric), compared against a Random Forest baseline on the exact same split.
- When real OSM accessibility-tag coverage turned out too sparse to validate that comparison properly (only 16 real `wheelchair: no` tags found across all of Downtown Toronto), built **Clearwell** — a fully synthetic, purpose-designed benchmark city with 8 neighborhoods, each isolating one specific test (data sparsity, balanced training, routing, compound penalties, construction closures, dead ends, untagged stairs, disconnected areas).
- Extending beyond physical accessibility into a **sensory/cognitive-load dimension** (crowding, noise, construction) — a separate weighting layer for people who need to avoid overstimulating environments, not physical barriers. Built on real Toronto pedestrian-volume data (6,421 intersections, City of Toronto Open Data), snapped onto the real OSM graph, and kept deliberately separate from physical accessibility weighting: the two are never blended into one score, only ever composed through an explicit profile, so the system can always say *why* a route was avoided. See `research/sensory-accessibility-ontario.md` for the research behind this and `notes/11` onward for the build.

## Project structure

```
notes/        Learning notes, numbered from 00, one concept per file, in my own words
notebooks/    Jupyter notebooks — one per module, markdown explanation above every code cell
research/     Source-validated research behind the sensory/cognitive-load extension
src/
  data/       The Clearwell synthetic benchmark city (networkx graphs, JSON save/load)
  graph/      Turning OSM/graph tags into a weighted, accessibility-aware graph, plus
              real-world-to-graph snapping and sensory/crowding weighting
  routing/    Dijkstra / A* pathfinding with accessibility and sensory weights
  ml/         Accessibility prediction: Random Forest baseline + hand-rolled GCN
visualize/    Real rendered graph/route/matrix visualizations (PNGs), embedded in notes
data/         Small, committed synthetic dataset (clearwell.json) + dataset-coverage notes
tests/        pytest suite — 63 tests, all passing, fully offline against synthetic data
```

## Status

Built and tested. The full physical-accessibility pipeline works end to end: real-OSM graph construction → accessibility weighting → Dijkstra/A* routing → a baseline-vs-GNN accessibility-prediction comparison, validated against a custom-built 8-neighborhood synthetic city because real-world accessibility-tag coverage proved too sparse to rely on alone. Two real gaps in the weighting logic (temporary construction closures, untagged stairs) were found and fixed by deliberately designing adversarial test neighborhoods.

The sensory/cognitive-load extension is in progress: real Toronto crowding data is pulled, bucketed, and turned into a routing weight (`sensory_weight()`), with its own `apply_sensory_weights()`/`find_low_sensory_route()` mirroring the physical-accessibility routing functions. Validated on the real ~14,123-node Downtown Toronto graph — sensory-aware routing picks a genuinely different route than plain shortest-path on real data, not just in a toy test. Known open item: the real-graph snapping step is currently slow (no spatial index yet), left for a later optimization pass since correctness mattered more than speed for this stage.

See `PLAN.md` for the full roadmap and `notes/` for the reasoning behind every decision — including two honestly-reported ML debugging stories (a label/split leakage bug, and a checkerboard pattern that was simultaneously a trivial feature-proxy and adversarial for GNN message-passing).
