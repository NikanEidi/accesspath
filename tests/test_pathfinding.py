import networkx as nx

from src.routing.pathfinding import find_accessible_route, find_low_sensory_route


def _toy_graph():
    """Short route A-B-D is wheelchair:no; long route A-C-D is fully accessible."""
    G = nx.MultiDiGraph()
    G.add_edge("A", "B", length=10, wheelchair="no")
    G.add_edge("B", "D", length=10, wheelchair="no")
    G.add_edge("A", "C", length=30, wheelchair="yes")
    G.add_edge("C", "D", length=30, wheelchair="yes")
    return G


def test_picks_the_longer_accessible_route_over_the_short_inaccessible_one():
    G = _toy_graph()
    path, cost = find_accessible_route(G, "A", "D")
    assert path == ["A", "C", "D"]


def test_plain_shortest_path_would_have_picked_the_short_route():
    # Sanity check that the toy graph is actually set up the way the test assumes:
    # without accessibility weighting, the short (inaccessible) route wins.
    G = _toy_graph()
    plain_path = nx.shortest_path(G, "A", "D", weight="length")
    assert plain_path == ["A", "B", "D"]


def test_real_industrial_row_bypass(industrial_row):
    # The same compound-penalty scenario, but on an actual built neighborhood,
    # not a hand-written 4-node graph.
    path, cost = find_accessible_route(industrial_row, "ir_0_0", "ir_0_5")
    assert "ir_1_0" in path  # must detour through the clean bypass row


def _toy_sensory_graph():
    """Short route A-B-D passes a crowded intersection; long A-C-D stays quiet."""
    G = nx.MultiDiGraph()
    G.add_node("A", y=43.700, x=-79.400)
    G.add_node("B", y=43.701, x=-79.401)
    G.add_node("C", y=43.700, x=-79.410)
    G.add_node("D", y=43.702, x=-79.402)
    G.add_edge("A", "B", length=10)
    G.add_edge("B", "D", length=10)
    G.add_edge("A", "C", length=30)
    G.add_edge("C", "D", length=30)
    return G


def _toy_sensory_rows():
    return [
        {"latitude": 43.700, "longitude": -79.400, "total_pedestrian": 50},   # near A -- quiet
        {"latitude": 43.701, "longitude": -79.401, "total_pedestrian": 5000}, # near B -- very busy
        {"latitude": 43.700, "longitude": -79.410, "total_pedestrian": 50},   # near C -- quiet
        {"latitude": 43.702, "longitude": -79.402, "total_pedestrian": 50},   # near D -- quiet
    ]


def test_picks_the_longer_quiet_route_over_the_short_crowded_one():
    G = _toy_sensory_graph()
    rows = _toy_sensory_rows()
    path, cost = find_low_sensory_route(G, "A", "D", rows)
    assert path == ["A", "C", "D"]


def test_plain_shortest_path_would_have_picked_the_crowded_route():
    # Sanity check, same pattern as the accessibility test above.
    G = _toy_sensory_graph()
    plain_path = nx.shortest_path(G, "A", "D", weight="length")
    assert plain_path == ["A", "B", "D"]
