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
            G.add_node(node_id, x=-79.90 + c * spacing, y=44.00 + r * spacing, street_count=0)

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
            G.add_node(node_id, x=-79.75 + c * spacing, y=44.00 + r * spacing, street_count=0)

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
    """A fully-tagged, balanced grid -- the main training data (not a 91%/9% imbalance)."""
    G = nx.MultiDiGraph()

    rows, cols = 5, 5
    spacing = 0.01

    for r in range(rows):
        for c in range(cols):
            node_id = f"rv_{r}_{c}"
            G.add_node(node_id, x=-79.95 + c * spacing, y=44.00 + r * spacing, street_count=0)

    def add_street(u, v, length, wheelchair, surface):
        G.add_edge(u, v, length=length, highway="footway", wheelchair=wheelchair, surface=surface)
        G.add_edge(v, u, length=length, highway="footway", wheelchair=wheelchair, surface=surface)

    # Checkerboard pattern: alternates accessible/inaccessible by position,
    # so the split is a real, learnable ~balanced mix, not random noise.
    def tags_for(r, c):
        if (r + c) % 2 == 0:
            return "yes", "asphalt"
        else:
            return "no", "gravel"

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


def build_clearwell():
    """Combines all four neighborhoods into one city graph (disjoint node name prefixes)."""
    G = nx.MultiDiGraph()
    for builder in (build_old_town, build_riverside_district, build_university_quarter, build_industrial_row):
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
