# Learning notes

My own notes as I build AccessPath, numbered in the order I actually learned things. One concept per file.

- [00 — Haversine and why flat-plane distance is wrong](00-haversine-and-distance.md)
- [01 — Graphs, shortest-path algorithms, and a real data surprise](01-graphs-and-shortest-path.md)
- [02 — Designing the accessibility weighting function](02-accessibility-weighting.md)
- [03 — Real routing with accessibility weights](03-routing.md)
- [04 — Dataset coverage at a bigger scale, and real-world proof](04-dataset-coverage.md)
- [05 — Turning routing into a reusable module](05-routing-module-test.md)
- [06 — Accessibility prediction: a baseline, and its real limit](06-accessibility-prediction-baseline.md)
- [07 — Searching for an external accessibility dataset (and why none fit)](07-external-dataset-search.md)
- [08 — Building and visualizing Clearwell](08-clearwell-visualization.md)
- [09 — GNN vs. baseline on Clearwell](09-gnn-baseline-comparison.md) (see notebook `09`; also documents a train/test-split-leaks-the-label bug and its fix)
- [10 — Four edge-case neighborhoods, and two real weighting gaps found along the way](10-edge-case-neighborhoods.md)
- [11 — Real Toronto crowding data, and connecting it to the graph](11-sensory-data-exploration.md) (first module of the sensory/cognitive-load extension; see `research/sensory-accessibility-ontario.md` for the design behind it)
