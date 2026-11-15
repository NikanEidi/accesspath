# 11 — Real Toronto crowding data, and connecting it to the graph

First real step toward `sensory_weight()`. Before this module, everything in
`research/sensory-accessibility-ontario.md` was research on paper — this is
where I actually pulled real City of Toronto data and got it talking to the
AccessPath graph.

## Getting real data out of Toronto's open data API

Toronto's Open Data portal runs on CKAN, which works in two steps. First,
`package_show` gives you a dataset's metadata and a list of `resources` — not
the actual rows yet. Then you take the resource id you actually want (the one
that's tabular, not a PDF/ZIP) and call `datastore_search` on it to get real
records.

First real bug: I guessed the dataset slug (`traffic-and-pedestrian-volumes`)
and it didn't exist — the request came back with no real JSON body, so
`.json()` threw `JSONDecodeError: Expecting value`. The lesson I took from
this: before trusting `.json()` to work, print `status_code` and `text[:300]`
first to see what the server actually sent back. The real slug turned out to
be `traffic-volumes-at-intersections-for-all-modes`.

## The data is noisier than I expected, and why average alone isn't enough

The resource I used (`tmc_most_recent_summary_data`) gives real pedestrian
counts per Toronto intersection — `total_pedestrian`, plus `latitude`/
`longitude`, plus `latest_count_date`. Real, current (dates in October 2026),
not synthetic.

But each count is a single-day snapshot, not a stable long-term average —
different intersections were counted on different dates. That means two
things: a raw count is noisy on its own, and averaging two raw noisy numbers
together (for two endpoints of one edge) doesn't obviously give something
trustworthy either, since both inputs carry their own single-day noise.

The fix I landed on: **bucket instead of using raw numbers.** I pulled the
full dataset (6,421 intersections, not just a small sample) and computed real
quartiles: 25th percentile = 164, median = 425, 75th percentile = 1197.5. I
used those exact numbers as bucket boundaries (`low` / `medium` / `high`)
instead of guessing round numbers. Bucketing absorbs small day-to-day noise —
a swing from 226 to 250 pedestrians doesn't change the bucket, so the noise
stops mattering once it's inside one bucket.

I wrote this first as `pandas.cut()` with hardcoded quartile values instead
of a hand-written if/elif chain — the same job, but it scales to more buckets
without more code, and it works on a whole list at once instead of one value
at a time.

Once I had buckets, averaging the two raw endpoint counts *before* bucketing
turned out to make sense again — averaging two independent noisy samples
genuinely reduces variance (that's just what averaging does), and bucketing
after the average absorbs whatever noise is left. The two ideas work
together, not against each other.

## Snapping real points onto the graph — and a real mismatch bug

The pedestrian data lives on real-world `(lat, lon)` points (intersections).
The AccessPath graph has its own nodes. To connect them, I built
`nearest_node_id(G, target_latlon)` — for every node in `G`, compute the real
geodesic distance (via `geopy.distance`, not hand-rolled Haversine, same as
Module 0) to the target point, and return whichever node is closest.

First real bug here: I tested it on a Scarborough intersection, and it
returned a node ~16 km away. The function wasn't wrong — it genuinely
returned the closest node *that exists in the graph* — but the graph only
covers Downtown Toronto, and Scarborough isn't in it. A "nearest" match that's
16 km away isn't a real match at all; it's silent garbage.

Fixed it by adding `max_distance_m` to `nearest_node_id`: if even the closest
node is farther than that, return `None` instead of a misleading snap. I
tested it both ways — a point actually inside Downtown Toronto (Brunswick Ave
/ Barton Ave) correctly snapped to a nearby node, and the Scarborough point
correctly returned `None` once I set `max_distance_m=200`.

I also needed the reverse direction: given a graph node's coordinates, find
the nearest *real-world data row* (not a graph node). That's `nearest_row()`
— same idea, same `max_distance_m` safety net, just searching a list of
dicts instead of a graph's nodes.

## Putting it together: crowding level for a real edge

`edge_crowding(G, u, v, candidate_rows, max_distance_m)` is where everything
connects: snap both endpoints of a real edge to the nearest real Toronto
pedestrian record, and if both have a real match within range, average their
`total_pedestrian` counts and bucket the result with `crowding_level()`. If
either endpoint has no real match, it returns `None` rather than guessing —
same honesty rule as `accessibility_weight()` not inventing data for
untagged edges.

Ran it on a real edge in the Downtown Toronto graph: `crowding_level` came
back `"high"` — the first time real Toronto crowding data actually reached
an AccessPath graph edge.

## Turning crowding into a number: `sensory_weight()`

A category isn't something `nx.shortest_path` can route on — I needed an
actual number, the same way `accessibility_weight()` already returns one. So
`sensory_weight(attrs, crowding)` takes an edge's attrs and its crowding
level and returns `length + penalty`, same shape as `accessibility_weight()`.

The penalty scale was the real decision here: `{"low": 0, "medium": 20,
"high": 200}`. That `200` is deliberately nowhere close to
`accessibility_weight()`'s `1000`-point penalty for a real physical barrier
(`wheelchair:no`, untagged steps, construction). A hard physical barrier is
impossible to pass — it should dominate any route choice. Crowding is a
strong preference to avoid, not a wall. I kept this as an explicit test
(`sensory_weight(..., "high") < 1000`) so the two scales can never
accidentally collide later.

I never touch `accessibility_weight()`'s number and `sensory_weight()`'s
number in the same function. They live on two separate edge attributes,
and the only place they're ever allowed to meet is later, through an
explicit `profile` parameter — never blended into one opaque score. That
way the system can always say *why* a route was avoided (stairs vs.
crowding), not just that it was.

## Routing with it: `apply_sensory_weights()` and `find_low_sensory_route()`

These mirror `apply_accessibility_weights()`/`find_accessible_route()`
exactly, on purpose — same shape, different data source. The real
difference: `apply_accessibility_weights()` reads OSM tags that are already
sitting on the graph's edges, but crowding isn't an OSM tag. Every edge has
to be snapped to the nearest real Toronto pedestrian record first, which is
why `apply_sensory_weights()` needs `candidate_rows` as an argument and
`apply_accessibility_weights()` doesn't.

## Testing it on the real graph — and the slow part I expected

First on a toy graph: a short route through a simulated high-crowding
intersection, a longer route that stays quiet. `find_low_sensory_route`
picked the quiet one; plain `nx.shortest_path` (no sensory weight) picked
the short crowded one — confirms the weighting actually changes the
decision, not just the number.

Then the real test, on the actual ~14,123-node Downtown Toronto graph:
comparing plain `nx.shortest_path` against `find_low_sensory_route` on two
real, reasonably distant nodes.

```
plain shortest path length: 111 nodes
low-sensory path length: 74 nodes
same path? False
low-sensory route cost: 16505.79
```

`same_path? False` is the actual result I was after — on real data, not a
toy graph, sensory weighting picks a genuinely different route. (Fewer
nodes on the low-sensory path doesn't mean a shorter *distance* — node
count is intersections crossed, not meters; it could be the same length or
longer, just along fewer, bigger streets instead of a denser grid. I'd need
to sum the real edge lengths to know that for sure.)

This took **9m37s on the first try, and 42m34s on the full real run** —
much slower than I expected. The reason is `apply_sensory_weights` doing an
unindexed linear nearest-neighbor search (`nearest_row` via
`geopy.distance()`) for *both* endpoints of *every* edge in the graph,
against all 6,421 Toronto pedestrian rows, with no spatial index. That's
roughly `edges × 2 × 6,421` distance calculations. A KD-tree/BallTree would
fix this, but I'm deliberately leaving it slow for now — the correctness
result mattered more than the speed, and the fix is well understood, not a
mystery.

## What this module does *not* do yet

- Performance: `apply_sensory_weights` is slow on a real graph (see above) —
  no spatial index yet, left for a later pass.
- Bikes (`total_bike` is in the same dataset) aren't used anywhere yet.
- Construction data (Road Reconstruction, Road Resurfacing, Sidewalk
  Construction, Utility Cut Permits — all real, confirmed usable, see
  `research/sensory-accessibility-ontario.md` section 4) hasn't been touched
  at all yet.
- No `profile` parameter yet that actually combines `accessibility_weight()`
  and `sensory_weight()` for someone who needs both — they exist side by
  side, not yet composed.

## Takeaway

Two real bugs this module, both the useful kind: guessing a dataset slug
that didn't exist (fixed by always checking `status_code`/`text` before
trusting `.json()`), and a geographically-blind "nearest node" match that
silently snapped a Scarborough point 16 km onto a Downtown-only graph (fixed
with a `max_distance_m` cutoff that returns `None` instead of a wrong
answer). Both are the same lesson in two different places: never trust a
"closest match" without checking how close it actually is.
