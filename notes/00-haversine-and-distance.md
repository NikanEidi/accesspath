# 00 — Haversine and why flat-plane distance is wrong

I started AccessPath by asking a simple question: if I want to find the "nearest" route, can't I just measure the straight-line (Euclidean) distance between two points and pick whichever is shortest?

Turns out, no — and the reason is actually pretty obvious once you see it: you can't walk or drive in a straight line through buildings and lakes. A route has to follow the actual road/sidewalk network. So straight-line distance tells you nothing about how long a real trip will take.

## The real approach: model it as a graph

The road network becomes a graph:
- every intersection (or point along a path) is a **node**
- every road/sidewalk segment connecting two nodes is an **edge**
- every edge has a **weight** — not straight-line distance, but something like "how long does it actually take to get through this segment"

Then an algorithm like Dijkstra or A* finds the path through this graph with the lowest total weight. That's the real "shortest route."

## So where does straight-line distance still matter?

Two places:

1. **Computing the weight of a single edge.** If I know the GPS coordinates of the two endpoints of a road segment, I still need the straight-line distance *between those two points* to know how long that one segment is. For that, I can't just use flat-plane Pythagoras, because I'm measuring on a sphere (Earth), not a flat map.

2. **A\* heuristic.** A* uses straight-line distance from a node to the destination as a quick, optimistic estimate ("this node probably isn't too far from the goal") to decide which nodes to explore first. It's never the actual answer — just a way to make the search faster.

## Haversine: distance on a sphere, not a flat map

If I used plain Pythagoras on `(lat, lng)` coordinates, it would be roughly fine for very short distances inside a city, but it's fundamentally the wrong math — I'd be treating a curved surface as if it were flat.

Haversine instead computes the **great-circle distance**: the shortest path between two points along the surface of a sphere. (Same idea as why a flight path looks curved on a flat map — it's actually the shortest route on the globe.)

The formula, step by step:

```
a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlng/2)
c = 2 × atan2(√a, √(1−a))
distance = R × c
```

Where:
- `lat` / `lng` = latitude / longitude (the north-south and east-west coordinates of a point)
- `Δlat`, `Δlng` = the difference in latitude/longitude between the two points, in radians
- `R` = Earth's radius (~6371 km)
- `a` and `c` aren't abbreviations for anything — they're just conventional intermediate variable names:
  - `a` is a helper value (squared half-chord length) on the way to finding the angle
  - `c` is the actual **angular distance** (in radians) between the two points, as seen from Earth's center

The logic: compute `a` → use it to get `c` (the real angle between the two points) → multiply `c` by `R` to turn that angle into an actual arc-length distance along the sphere's surface.

In code, I won't hand-write this — `geopy.distance` or `osmnx`/`networkx` already do it. But I wanted to understand what's underneath it before I use it as a black box, especially since I'll later be adjusting edge weights manually for accessibility.

## Takeaway

- Euclidean/flat-plane distance ≠ real route distance, because real movement follows a network, not a straight line.
- The network is modeled as a graph (nodes = intersections, edges = road segments, weights = real travel cost).
- Haversine gives the correct distance between two GPS points on a sphere — used to compute edge weights, and as the heuristic inside A*, never as the final route length by itself.

**Next:** `01-graphs-and-shortest-path.md` — how Dijkstra and A* actually walk the graph to find the lowest-weight path.
