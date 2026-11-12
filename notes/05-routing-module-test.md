# 05 — Turning routing into a reusable module

## Why this step mattered

By notebook 04, the actual routing logic (`accessibility_weight`, applying it to a graph, running `nx.shortest_path`) had been copy-pasted into three different notebooks. Every time I wanted to test something, I had to redefine the same function by hand — which is exactly the kind of thing that breaks modularity: if I ever want to change the weighting formula, I'd have to find and update it in every notebook separately, and risk missing one.

## The real structure

```
src/graph/weighting.py       # accessibility_weight()
src/graph/tag_filters.py     # find_edges_with_tag()
src/routing/pathfinding.py   # apply_accessibility_weights() + find_accessible_route()
```

`find_accessible_route(G, source, target)` does the whole job in one call: apply the weighting function to every edge, store it as a real graph attribute, then run `nx.shortest_path`/`nx.shortest_path_length` with that attribute as the cost. It imports `accessibility_weight` from `weighting.py` instead of redefining it.

## Proving it's a real drop-in replacement, not just a refactor

Re-ran the exact same test from notes/04 (Downtown Toronto, source/target set to the endpoints of a real `wheelchair: no` edge) — but this time through the module instead of hand-written code:

```python
from src.routing.pathfinding import find_accessible_route

path_by_acc, cost_by_acc = find_accessible_route(G_big, u_bad, v_bad)
```

```
shortest by length:     [400707035, 516949102]
shortest by acc_weight: [400707035, 3590076075, 3590076072, 6412492716, 516949102]  cost = 198.509...
same route? False
```

Identical result to notes/04's hand-written version — confirming the module is a genuine behavior-preserving refactor, not a rewrite that happens to look similar.

## Takeaway

Modules 2-4 proved the *logic* was correct (weighting math, routing decisions, real-world validation). Module 5 is about proving the *code organization* didn't break anything while making it reusable — any future notebook, or the upcoming ML layer, can now call one function instead of repeating this setup.

**Next:** the travel-time prediction layer (regression baseline vs. GNN) from the original plan.
