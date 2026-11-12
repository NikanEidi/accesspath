# 10 — Four edge-case neighborhoods, and two real weighting gaps found along the way

## Why expand past the first four neighborhoods

The first four neighborhoods (Old Town, Riverside, University Quarter, Industrial Row) covered data sparsity, balanced training, routing, and compound penalties. But real road networks have other scenarios worth testing deliberately: temporary closures, dead ends, missing tags that still obviously matter, and genuinely unreachable areas. Rather than hope real OSM data happens to contain good examples of each, I built one neighborhood per scenario.

## Two real gaps found in `accessibility_weight` while designing these

Building **Stairs-Only Zone** exposed a real gap: the weighting function only ever looked at the `wheelchair` tag. But a `highway=steps` edge is inherently inaccessible whether or not anyone tagged it `wheelchair:no` — in practice, most staircases in OSM simply have no wheelchair tag at all. Added a rule: if there's no explicit `wheelchair` tag and `highway == "steps"`, treat it as inaccessible anyway. An explicit `wheelchair: yes` (e.g. for a stairlift) still overrides this.

Building **Construction Zone** exposed a second gap: there was no handling at all for temporary closures. Added a `construction == "yes"` check with the same heavy penalty as `wheelchair: no`.

```python
if attrs.get("construction") == "yes":
    penalty += 1000

wheelchair = attrs.get("wheelchair")
if wheelchair == "no":
    penalty += 1000
elif wheelchair in ("yes", "designated"):
    penalty -= 2
elif attrs.get("highway") == "steps":
    penalty += 1000
```

Both gaps were found by deliberately designing a scenario the existing function would fail on, not by reading the code line by line — the same approach as the earlier real-data validation steps.

## The four neighborhoods

| Neighborhood | Design | What it proves |
|---|---|---|
| **Construction Zone** | A direct 2-row grid; one segment of the top row tagged `construction: yes` | Routing detours around a *specific* temporarily-closed segment, not just generally-bad ones |
| **Dead-End District** | A 5-node through "spine" with two 2-node cul-de-sac branches | Through-routes never wander into branches; routing *into* a branch (a valid destination) still works |
| **Stairs-Only Zone** | A direct stairs edge (`highway: steps`, no `wheelchair` tag) next to a longer, explicitly-tagged ramp | The new steps-without-a-tag rule actually changes the routing decision, not just the arithmetic |
| **Disconnected Island** | 4 nodes connected only to each other, zero edges to anywhere else | `find_accessible_route` lets `networkx`'s own `NetworkXNoPath` propagate instead of silently returning something wrong when no route exists |

Each one tests a *decision*, not just a number — verified by comparing the plain `nx.shortest_path` (by `length`) against `find_accessible_route`'s output, the same pattern used since notebook 03.

## Real automated tests, not just notebook prints

Added `pytest` as the test framework (`tests/`, configured via `pytest.ini`), with `conftest.py` fixtures (`scope="session"`) so every neighborhood graph is built exactly once per test run and shared across all tests, instead of being rebuilt from scratch in every single test function.

- `test_weighting.py` — unit tests for `accessibility_weight`, including the two new rules
- `test_tag_filters.py` — `find_edges_with_tag` correctness
- `test_pathfinding.py` — the original short-inaccessible-vs-long-accessible routing proof, now an automated assertion instead of a manual print
- `test_synthetic_city.py` — node/edge counts, tag balance, and a save/load JSON round-trip
- `test_edge_cases.py` — all four new neighborhoods, including `pytest.raises(nx.NetworkXNoPath)` for the disconnected island

31 tests, all passing, running in well under a second — real-OSM-downloading tests are deliberately kept out of this suite since they're slow and depend on network availability; everything here runs fully offline against synthetic data.

## Takeaway

Designing adversarial test scenarios on purpose (not just hoping real data happens to contain them) found two genuine weighting gaps that would have otherwise gone unnoticed indefinitely, since the original real OSM data never happened to contain a bare, untagged staircase or a construction closure in the areas tested so far.
