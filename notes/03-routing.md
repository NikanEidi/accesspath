# 03 — Real routing with accessibility weights

## Putting the weight on the graph itself

The weighting function from notes/02 is only useful if `networkx`'s own pathfinding functions can actually read it. `nx.set_edge_attributes` writes a value onto every edge in one call, given a `{(u, v, k): value}` dict — the `k` is needed because `G` is a `MultiDiGraph` (more than one edge can connect the same two nodes), so iterating needs `G.edges(keys=True, data=True)`, not the plain `G.edges(data=True)` used earlier.

```python
weights = {
    (u, v, k): accessibility_weight(data)
    for u, v, k, data in G.edges(keys=True, data=True)
}
nx.set_edge_attributes(G, weights, "acc_weight")
```

Sanity check on the first edge confirmed it: `10.053952309088126 -> 10.053952309088126` — a neutral edge with no accessibility tags, correctly left unchanged.

## Running Dijkstra/A* for real

`networkx` already has Dijkstra/A* built in — no need to implement them by hand:

```python
path = nx.shortest_path(G, source=..., target=..., weight="acc_weight")
cost = nx.shortest_path_length(G, source=..., target=..., weight="acc_weight")
```

`weight` is the key argument: it tells `networkx` which edge attribute to treat as the real cost. Without it, every edge defaults to a cost of 1 (counting hops, not real distance).

## First attempt: no visible difference, and why that's not a bug

Comparing `weight="length"` vs `weight="acc_weight"` between two arbitrary nodes (`nodes[0]` and `nodes[-1]`) gave the exact same route and exact same cost. Not a bug — the `wheelchair: yes/designated` discount is only `-2`, which is under 0.2% of a ~900m route. Even picking a target that was literally one endpoint of a known `wheelchair: designated` edge (found with a new helper, `find_edges_with_tag`, in `src/graph/tag_filters.py`) still gave an identical result, because the discount is simply too small to ever flip a real routing decision between two genuinely different routes — it can only nudge a near-tie.

The actual decision-changing case is the `wheelchair: no` penalty (1000), but no real edge in this dataset has that tag — only `yes`/`designated` were found.

## Validating the real decision-changing case with a synthetic graph

To prove the algorithm actually *avoids* an inaccessible edge (not just that the arithmetic is correct), I built a tiny controlled graph instead of relying on real data that doesn't have the right example:

- Short route `A → B → D` (length 10 + 10 = 20), but both edges tagged `wheelchair: no`.
- Long route `A → C → D` (length 30 + 30 = 60), fully accessible (`wheelchair: yes`).

```
shortest by length:     ['A', 'B', 'D']
shortest by acc_weight: ['A', 'C', 'D']
```

Exactly as designed: by raw distance, the short-but-inaccessible route wins. By `acc_weight`, the algorithm correctly picks the longer route instead, because the `wheelchair: no` penalty (1000 per edge) makes the short route's total cost far higher than the long route's. This is the real proof the weighting changes *decisions*, not just numbers — something the real-data test alone couldn't show given how sparse `wheelchair: no` tags are in this area.

## Takeaway

- Storing the weight as a real graph attribute (not just a standalone function) is what lets `networkx`'s built-in shortest-path functions use it.
- A small, real-world-sized discount (like `-2` for `wheelchair: yes`) will rarely change which route gets picked on its own — it mostly re-ranks near-ties, which is intentional (accessibility shouldn't wildly override practical distance for a minor preference).
- A synthetic test graph is the right tool to validate an algorithm's *decision logic* in isolation, separate from whether real-world data happens to contain the specific scenario needed to observe it.

**Next:** test tag coverage on a bigger area (`04-dataset-coverage.ipynb`) to look for real `wheelchair: no` examples and get a better sense of how coverage scales beyond one small district.
