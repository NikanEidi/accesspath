# AccessPath

An accessibility-aware route-finding project: given a start and end point, find the best route not just by raw distance, but by real travel time **and** accessibility (wheelchair access, sidewalk surface, curb cuts) — something general-purpose routing apps like Google Maps barely support for walking directions.

## Why this project

Most route-finding demos stop at "shortest path." AccessPath goes further:
- Builds a real road/sidewalk graph from OpenStreetMap data (not a toy grid).
- Computes real-world distances with the Haversine formula (great-circle distance on a sphere, not flat-plane math).
- Finds routes with Dijkstra / A* using real travel-time weights, not straight-line guesses.
- Lets a route be customized per accessibility profile (e.g. wheelchair user, stroller, visually impaired) by penalizing or excluding edges based on OSM accessibility tags.
- Adds a learned layer on top: predicting travel time per road segment based on time of day / day of week, starting with a simple regression baseline and comparing it against a Graph Neural Network.

## Project structure

```
notes/        Learning notes, numbered from 00, one concept per file
notebooks/    Exploratory Jupyter notebooks (data exploration, quick visualization tests)
src/
  data/       Downloading and parsing OpenStreetMap data
  graph/      Turning OSM nodes/ways/tags into a weighted graph
  routing/    Dijkstra / A* pathfinding
  ml/         Travel-time prediction: regression baseline, then GNN
visualize/    Plotting the road graph and found routes on a map
data/         Raw/processed datasets (gitignored)
tests/        Tests
```

## Status

Early planning / learning phase. See `PLAN.md` for the full roadmap and `notes/` for the concepts behind each decision.
