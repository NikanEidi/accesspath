# 08 — Building and visualizing Clearwell

## Why a synthetic city, and why not osmnx

Module 6/7 found that real OSM accessibility tags are too sparse (16-178 tagged edges out of ~39,000) to train or properly validate a classifier. Rather than stop there, I built **Clearwell** — a fully fictional benchmark city, designed so every neighborhood tests one specific thing, with as much labeled data as the test needs.

`osmnx` doesn't apply here: it only downloads real OpenStreetMap data, and Clearwell isn't a real place. Everything is built directly with plain `networkx` instead — nodes get `x`/`y` coordinates and edges get `length`/`wheelchair`/`surface` attributes exactly like a real osmnx graph would, which is what lets every function I already built (`accessibility_weight`, `find_accessible_route`, `find_edges_with_tag`) work on it completely unchanged.

## The four neighborhoods (`src/data/synthetic_city.py`)

| Neighborhood | Builder function | Design | Tests |
|---|---|---|---|
| **Old Town** | `build_old_town()` | 4x4 grid, only 4/48 edges tagged | Prediction for untagged edges (mirrors real sparse data) |
| **Riverside District** | `build_riverside_district()` | 5x5 grid, checkerboard pattern — exactly 40 accessible / 40 inaccessible | Main **training** data — a real, learnable, non-imbalanced signal |
| **University Quarter** | `build_university_quarter()` | 6x6 dense grid, 120 accessible edges + 5 inaccessible diagonal "shortcuts" | **Routing** — proven that `shortest by length` picks the inaccessible diagonal, which the accessibility-weighted router has to route around |
| **Industrial Row** | `build_industrial_row()` | 3x6 rows: a direct but compound-penalized route (bad surface AND inaccessible) vs. a slightly longer, fully clean bypass | **Weighting under compound penalty** — proven the router picks the longer bypass despite the stacked penalty |

Each builder is independently testable — every one was verified on its own (node/edge counts, tag distribution, and a real routing test) before being combined.

## Combining and persisting

```python
def build_clearwell():
    G = nx.MultiDiGraph()
    for builder in (build_old_town, build_riverside_district, build_university_quarter, build_industrial_row):
        G = nx.compose(G, builder())
    return G
```

`nx.compose` merges graphs by node name — safe here because every neighborhood uses its own name prefix (`ot_`, `rv_`, `uq_`, `ir_`), so there's no risk of two different neighborhoods' nodes colliding.

Saved with `nx.node_link_data(G, edges="edges")` → `json.dump`, and reloaded with `nx.node_link_graph(data, edges="edges")`, into a single `data/clearwell.json` (95 nodes, 294 edges total).

## A real path bug, and the actual lesson in it

`load_clearwell()`'s default path (`"data/clearwell.json"`) is a *relative* path — it resolves against whatever directory the Python process's current working directory happens to be, not against where `synthetic_city.py` itself lives. Calling it from the project root worked by coincidence (cwd happened to be `accesspath/`), but calling it from a notebook failed, because Jupyter's cwd is `accesspath/notebooks/`, so it looked for `accesspath/notebooks/data/clearwell.json`, which doesn't exist.

Fixed by computing the default path from the module's own file location instead of trusting the caller's cwd:

```python
from pathlib import Path
_DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "clearwell.json"
```

`Path(__file__)` is `src/data/synthetic_city.py`'s own location; `.parents[2]` walks up two directory levels (`src/data` → `src` → `accesspath`) to the project root, regardless of where the code is run from.

**Also hit (again) the Jupyter kernel caching issue** from earlier notebooks: after fixing the file, the notebook still raised the *old* error — because the kernel had already imported `synthetic_city` once and Python doesn't re-read an edited `.py` file for a module already in memory. Needed a kernel restart, not just a cell re-run, to pick up the fix.

## Visualizing

Plotted with plain `networkx` (`nx.draw`, `pos` built manually from each node's `x`/`y`), not `osmnx.plot_graph` (which expects osmnx-specific graph metadata this synthetic graph doesn't have). Edges colored green (`wheelchair: yes/designated`), red (`wheelchair: no`), gray (untagged) — all four neighborhoods' design patterns are visible at a glance in one image (`visualize/clearwell-city-graph.png`).

First render had all four neighborhoods squished into thin, overlapping vertical lines — the coordinate spacing *within* each neighborhood (0.001) was 10x smaller than the spacing *between* neighborhoods (0.05), and Industrial Row's starting x-coordinate accidentally overlapped University Quarter's range entirely. Fixed by increasing the internal spacing to match the inter-neighborhood gap, and moving Industrial Row's base coordinate further out.

**Next:** build the GNN on Clearwell (training on Riverside District, testing accessibility prediction on Old Town's untagged edges), compared against the Module 6 baseline.
