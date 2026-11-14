import networkx as nx

from src.graph.snapping import nearest_node_id, nearest_row


def _toy_graph():
    """Three nodes spread out in both latitude and longitude."""
    G = nx.MultiDiGraph()
    G.add_node("north", y=43.80, x=-79.40)
    G.add_node("south", y=43.60, x=-79.40)
    G.add_node("east", y=43.70, x=-79.20)
    return G


def test_nearest_node_finds_closest_of_several():
    G = _toy_graph()
    # Clearly closest to "south" (same longitude, nearby latitude).
    target = (43.61, -79.40)
    assert nearest_node_id(G, target) == "south"


def test_nearest_node_handles_point_exactly_on_a_node():
    G = _toy_graph()
    target = (43.70, -79.20)  # exact coordinates of "east"
    assert nearest_node_id(G, target) == "east"


def test_nearest_node_is_correct_in_both_directions():
    G = nx.MultiDiGraph()
    # "lat_close" matches the target's latitude exactly but is far in longitude.
    G.add_node("lat_close", y=43.70, x=-79.60)
    # "balanced" is moderately close in both latitude and longitude --
    # the true nearest point, not just the best match on a single axis.
    G.add_node("balanced", y=43.705, x=-79.405)

    target = (43.70, -79.40)
    assert nearest_node_id(G, target) == "balanced"


def test_nearest_node_returns_none_beyond_max_distance():
    G = _toy_graph()
    # Real Scarborough coordinates, ~16km from any node in the toy graph --
    # the exact kind of out-of-coverage match that produced a bad snap earlier.
    target = (43.7732636699038, -79.2200726425321)
    assert nearest_node_id(G, target, max_distance_m=200) is None


def test_nearest_node_within_max_distance_still_returns_the_match():
    G = _toy_graph()
    target = (43.61, -79.40)  # same as the basic closest-of-several case
    assert nearest_node_id(G, target, max_distance_m=5000) == "south"


def _toy_rows():
    return [
        {"location_name": "quiet corner", "latitude": 43.80, "longitude": -79.40, "total_pedestrian": 50},
        {"location_name": "busy corner", "latitude": 43.60, "longitude": -79.40, "total_pedestrian": 3000},
    ]


def test_nearest_row_finds_the_closest_record():
    rows = _toy_rows()
    target = (43.61, -79.40)  # close to "busy corner"
    match = nearest_row(target, rows)
    assert match["location_name"] == "busy corner"


def test_nearest_row_returns_none_beyond_max_distance():
    rows = _toy_rows()
    # Real Scarborough coordinates, far from either toy row.
    target = (43.7732636699038, -79.2200726425321)
    assert nearest_row(target, rows, max_distance_m=200) is None


def test_nearest_row_returns_none_for_empty_candidates():
    target = (43.61, -79.40)
    assert nearest_row(target, []) is None
