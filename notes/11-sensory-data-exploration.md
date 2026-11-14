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

## What this module does *not* do yet

- Only tested on one edge, not applied across the whole graph.
- `crowding_level`/`edge_crowding` return a category (`"low"`/`"medium"`/
  `"high"`), not yet a numeric weight `nx.shortest_path` could use — same gap
  `accessibility_weight()` didn't have, since it already returns a number.
- Bikes (`total_bike` is in the same dataset) aren't used anywhere yet.
- No `sensory_weight()` function yet, and no routing function that uses it.
- Construction data (Road Reconstruction, Road Resurfacing, Sidewalk
  Construction, Utility Cut Permits — all real, confirmed usable, see
  `research/sensory-accessibility-ontario.md` section 4) hasn't been touched
  at all yet.

## Takeaway

Two real bugs this module, both the useful kind: guessing a dataset slug
that didn't exist (fixed by always checking `status_code`/`text` before
trusting `.json()`), and a geographically-blind "nearest node" match that
silently snapped a Scarborough point 16 km onto a Downtown-only graph (fixed
with a `max_distance_m` cutoff that returns `None` instead of a wrong
answer). Both are the same lesson in two different places: never trust a
"closest match" without checking how close it actually is.
