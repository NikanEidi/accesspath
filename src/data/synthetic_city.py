"""Builds Clearwell, a fully synthetic benchmark city, one neighborhood at a time.

Not real OpenStreetMap data (osmnx doesn't apply -- there's no real place to
download). Built directly as networkx graphs, saved as data/clearwell.json.
"""

import json
from pathlib import Path

import networkx as nx

# src/data/synthetic_city.py -> parents[2] is the accesspath/ project root
_DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "clearwell.json"


def build_old_town():
    """A small, mostly-untagged grid -- mirrors real OSM data's sparse coverage."""
    G = nx.MultiDiGraph()

    # 4x4 grid of intersections, named ot_0_0 .. ot_3_3
    rows, cols = 4, 4
    spacing = 0.01  # arbitrary coordinate spacing, not real-world distance

    for r in range(rows):
        for c in range(cols):
            node_id = f"ot_{r}_{c}"
            G.add_node(node_id, x=-80.00 + c * spacing, y=44.00 + r * spacing, street_count=0)

    def add_street(u, v, length, **attrs):
        G.add_edge(u, v, length=length, highway="footway", **attrs)
        G.add_edge(v, u, length=length, highway="footway", **attrs)

    # Horizontal streets
    for r in range(rows):
        for c in range(cols - 1):
            u, v = f"ot_{r}_{c}", f"ot_{r}_{c+1}"
            add_street(u, v, length=100)

    # Vertical streets
    for r in range(rows - 1):
        for c in range(cols):
            u, v = f"ot_{r}_{c}", f"ot_{r+1}_{c}"
            add_street(u, v, length=100)

    # Only a handful of real tags, same sparse pattern as real OSM data
    G["ot_1_1"]["ot_1_2"][0]["wheelchair"] = "yes"
    G["ot_1_2"]["ot_1_1"][0]["wheelchair"] = "yes"
    G["ot_2_2"]["ot_2_3"][0]["surface"] = "gravel"
    G["ot_2_3"]["ot_2_2"][0]["surface"] = "gravel"

    for node_id, data in G.nodes(data=True):
        data["street_count"] = G.degree(node_id)

    return G


def build_university_quarter():
    """A dense, modern, mostly-accessible grid with diagonal shortcuts -- for routing tests."""
    G = nx.MultiDiGraph()

    rows, cols = 6, 6
    spacing = 0.01

    for r in range(rows):
        for c in range(cols):
            node_id = f"uq_{r}_{c}"
            G.add_node(node_id, x=-79.75 + c * spacing, y=44.00 + r * spacing, street_count=0)

    def add_street(u, v, length, wheelchair="designated", surface="concrete"):
        G.add_edge(u, v, length=length, highway="footway", wheelchair=wheelchair, surface=surface)
        G.add_edge(v, u, length=length, highway="footway", wheelchair=wheelchair, surface=surface)

    # Dense regular grid -- modern area, almost everything accessible
    for r in range(rows):
        for c in range(cols - 1):
            add_street(f"uq_{r}_{c}", f"uq_{r}_{c+1}", length=80)

    for r in range(rows - 1):
        for c in range(cols):
            add_street(f"uq_{r}_{c}", f"uq_{r+1}_{c}", length=80)

    # A few diagonal shortcuts, deliberately NOT accessible -- real alternate
    # routes for the routing module to have to choose between.
    diagonals = [
        ("uq_0_0", "uq_1_1"), ("uq_1_1", "uq_2_2"), ("uq_2_2", "uq_3_3"),
        ("uq_3_3", "uq_4_4"), ("uq_4_4", "uq_5_5"),
    ]
    for u, v in diagonals:
        add_street(u, v, length=60, wheelchair="no", surface="gravel")

    for node_id, data in G.nodes(data=True):
        data["street_count"] = G.degree(node_id)

    return G


def build_industrial_row():
    """Mostly bad-surface + inaccessible, with one clean bypass -- stress-tests the weighting."""
    G = nx.MultiDiGraph()

    rows, cols = 3, 6
    spacing = 0.01

    for r in range(rows):
        for c in range(cols):
            node_id = f"ir_{r}_{c}"
            G.add_node(node_id, x=-79.60 + c * spacing, y=44.00 + r * spacing, street_count=0)

    def add_street(u, v, length, wheelchair, surface):
        G.add_edge(u, v, length=length, highway="footway", wheelchair=wheelchair, surface=surface)
        G.add_edge(v, u, length=length, highway="footway", wheelchair=wheelchair, surface=surface)

    # Main row (r=0): the "direct" path, but compound-penalized -- bad surface AND inaccessible.
    for c in range(cols - 1):
        add_street(f"ir_0_{c}", f"ir_0_{c+1}", length=90, wheelchair="no", surface="gravel")

    # A clean bypass one row over (r=1), fully accessible, slightly longer.
    for c in range(cols - 1):
        add_street(f"ir_1_{c}", f"ir_1_{c+1}", length=110, wheelchair="yes", surface="concrete")

    # Connect the two rows at both ends only, so the bypass is a real detour, not a shortcut.
    add_street("ir_0_0", "ir_1_0", length=20, wheelchair="yes", surface="concrete")
    add_street(f"ir_0_{cols-1}", f"ir_1_{cols-1}", length=20, wheelchair="yes", surface="concrete")

    # A third, unused row (r=2) just for extra graph density/realism.
    for c in range(cols - 1):
        add_street(f"ir_2_{c}", f"ir_2_{c+1}", length=100, wheelchair="no", surface="dirt")
    add_street("ir_1_0", "ir_2_0", length=20, wheelchair="no", surface="gravel")

    for node_id, data in G.nodes(data=True):
        data["street_count"] = G.degree(node_id)

    return G


def build_riverside_district():
    """A fully-tagged, balanced grid -- the main training data (not a 91%/9% imbalance).

    Geographically clustered (homophilic), not a checkerboard: real accessibility
    tends to cluster by area, and a checkerboard is actively adversarial for a
    GNN's neighbor-averaging (every neighbor has the opposite label, which
    cancels the useful signal instead of reinforcing it -- confirmed the hard way
    on the first version of this neighborhood, see notes/09).
    """
    G = nx.MultiDiGraph()

    rows, cols = 5, 6
    spacing = 0.01

    for r in range(rows):
        for c in range(cols):
            node_id = f"rv_{r}_{c}"
            G.add_node(node_id, x=-79.90 + c * spacing, y=44.00 + r * spacing, street_count=0)

    def add_street(u, v, length, wheelchair, surface):
        G.add_edge(u, v, length=length, highway="footway", wheelchair=wheelchair, surface=surface)
        G.add_edge(v, u, length=length, highway="footway", wheelchair=wheelchair, surface=surface)

    # Geographic clusters: west half (c<3) accessible, east half (c>=3) not --
    # a real, learnable, balanced (50/50) split where neighbors share labels.
    # Surface mostly follows the same cluster, but is deliberately flipped right
    # at the boundary columns (c=2,3) so it's a strong signal, not a perfect
    # giveaway -- the model has to actually combine features, not just look up
    # one of them.
    def tags_for(r, c):
        accessible = c < 3
        wheelchair = "yes" if accessible else "no"
        if c in (2, 3):
            surface = "gravel" if accessible else "asphalt"
        else:
            surface = "asphalt" if accessible else "gravel"
        return wheelchair, surface

    for r in range(rows):
        for c in range(cols - 1):
            u, v = f"rv_{r}_{c}", f"rv_{r}_{c+1}"
            wheelchair, surface = tags_for(r, c)
            add_street(u, v, length=100, wheelchair=wheelchair, surface=surface)

    for r in range(rows - 1):
        for c in range(cols):
            u, v = f"rv_{r}_{c}", f"rv_{r+1}_{c}"
            wheelchair, surface = tags_for(r, c)
            add_street(u, v, length=100, wheelchair=wheelchair, surface=surface)

    for node_id, data in G.nodes(data=True):
        data["street_count"] = G.degree(node_id)

    return G


def build_construction_zone():
    """A direct route blocked by one construction-closed segment -- a surgical detour."""
    G = nx.MultiDiGraph()

    cols = 5
    spacing = 0.01
    base_x = -79.45

    for r in range(2):
        for c in range(cols):
            node_id = f"cz_{r}_{c}"
            G.add_node(node_id, x=base_x + c * spacing, y=44.00 + r * spacing, street_count=0)

    def add_street(u, v, length, **attrs):
        G.add_edge(u, v, length=length, highway="footway", **attrs)
        G.add_edge(v, u, length=length, highway="footway", **attrs)

    # Top row: the direct route, accessible everywhere EXCEPT one closed segment.
    for c in range(cols - 1):
        if c == 2:
            add_street(f"cz_0_{c}", f"cz_0_{c+1}", length=80, wheelchair="yes", surface="asphalt", construction="yes")
        else:
            add_street(f"cz_0_{c}", f"cz_0_{c+1}", length=80, wheelchair="yes", surface="asphalt")

    # Bottom row: a clean, always-open bypass.
    for c in range(cols - 1):
        add_street(f"cz_1_{c}", f"cz_1_{c+1}", length=90, wheelchair="yes", surface="asphalt")

    # Connect the rows only at both ends, so the bypass is a real detour.
    add_street("cz_0_0", "cz_1_0", length=15, wheelchair="yes", surface="asphalt")
    add_street(f"cz_0_{cols-1}", f"cz_1_{cols-1}", length=15, wheelchair="yes", surface="asphalt")

    for node_id, data in G.nodes(data=True):
        data["street_count"] = G.degree(node_id)

    return G


def build_dead_end_district():
    """A through street with real cul-de-sac branches (degree-1 dead ends)."""
    G = nx.MultiDiGraph()

    spacing = 0.01
    base_x = -79.30

    spine_len = 5
    for i in range(spine_len):
        G.add_node(f"de_spine_{i}", x=base_x + i * spacing, y=44.00, street_count=0)

    def add_street(u, v, length, **attrs):
        G.add_edge(u, v, length=length, highway="footway", **attrs)
        G.add_edge(v, u, length=length, highway="footway", **attrs)

    # The through street -- always has a real way from end to end.
    for i in range(spine_len - 1):
        add_street(f"de_spine_{i}", f"de_spine_{i+1}", length=80, wheelchair="yes", surface="asphalt")

    # Cul-de-sac branches off spine nodes 1 and 3 -- each ends in a true dead end.
    for branch_i, spine_node in enumerate((1, 3)):
        for depth in range(2):
            node = f"de_branch_{branch_i}_{depth}"
            prev = f"de_spine_{spine_node}" if depth == 0 else f"de_branch_{branch_i}_{depth-1}"
            G.add_node(node, x=base_x + spine_node * spacing, y=44.00 + (depth + 1) * spacing, street_count=0)
            add_street(prev, node, length=40, wheelchair="yes", surface="asphalt")

    for node_id, data in G.nodes(data=True):
        data["street_count"] = G.degree(node_id)

    return G


def build_stairs_only_zone():
    """Stairs with no wheelchair tag at all (should still be inaccessible), next to a tagged ramp."""
    G = nx.MultiDiGraph()

    spacing = 0.01
    base_x = -79.15

    G.add_node("so_bottom", x=base_x, y=44.00, street_count=0)
    G.add_node("so_top", x=base_x, y=44.00 + 2 * spacing, street_count=0)
    G.add_node("so_ramp_mid", x=base_x + spacing, y=44.00 + spacing, street_count=0)

    # The stairs: shortest, but NO wheelchair tag -- relies on the highway=steps rule, not a tag.
    G.add_edge("so_bottom", "so_top", length=30, highway="steps", surface="concrete")
    G.add_edge("so_top", "so_bottom", length=30, highway="steps", surface="concrete")

    # A longer, explicitly-tagged ramp around the same climb.
    G.add_edge("so_bottom", "so_ramp_mid", length=35, highway="footway", wheelchair="yes", surface="asphalt")
    G.add_edge("so_ramp_mid", "so_bottom", length=35, highway="footway", wheelchair="yes", surface="asphalt")
    G.add_edge("so_ramp_mid", "so_top", length=35, highway="footway", wheelchair="yes", surface="asphalt")
    G.add_edge("so_top", "so_ramp_mid", length=35, highway="footway", wheelchair="yes", surface="asphalt")

    for node_id, data in G.nodes(data=True):
        data["street_count"] = G.degree(node_id)

    return G


def build_disconnected_island():
    """A small cluster with zero edges to anywhere else -- genuinely unreachable."""
    G = nx.MultiDiGraph()

    spacing = 0.01
    base_x = -79.00

    for i in range(4):
        G.add_node(f"di_{i}", x=base_x + i * spacing, y=44.00, street_count=0)

    def add_street(u, v, length, **attrs):
        G.add_edge(u, v, length=length, highway="footway", **attrs)
        G.add_edge(v, u, length=length, highway="footway", **attrs)

    for i in range(3):
        add_street(f"di_{i}", f"di_{i+1}", length=60, wheelchair="yes", surface="asphalt")

    for node_id, data in G.nodes(data=True):
        data["street_count"] = G.degree(node_id)

    return G


def build_clearwell():
    """Combines all eight neighborhoods into one city graph (disjoint node name prefixes)."""
    G = nx.MultiDiGraph()
    for builder in (
        build_old_town, build_riverside_district, build_university_quarter, build_industrial_row,
        build_construction_zone, build_dead_end_district, build_stairs_only_zone, build_disconnected_island,
    ):
        G = nx.compose(G, builder())
    return G


def save_clearwell(path=_DEFAULT_PATH):
    G = build_clearwell()
    data = nx.node_link_data(G, edges="edges")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


def load_clearwell(path=_DEFAULT_PATH):
    with open(path) as f:
        data = json.load(f)
    return nx.node_link_graph(data, edges="edges")


if __name__ == "__main__":
    path = save_clearwell()
    print(f"Saved Clearwell to {path}")
