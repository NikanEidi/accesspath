import networkx as nx

from src.graph.sensory_weighting import crowding_level, edge_crowding


def test_crowding_level_low_for_two_quiet_endpoints():
    assert crowding_level(50, 80) == "low"


def test_crowding_level_high_for_two_busy_endpoints():
    assert crowding_level(2000, 5000) == "high"


def test_crowding_level_averages_before_bucketing():
    # One low-ish, one clearly-high endpoint; average (1778) lands in "high".
    assert crowding_level(226, 3330) == "high"


def test_crowding_level_medium_for_a_moderate_average():
    assert crowding_level(300, 500) == "medium"


def _toy_edge_graph():
    G = nx.MultiDiGraph()
    G.add_node("u", y=43.70, x=-79.40)
    G.add_node("v", y=43.705, x=-79.405)
    G.add_edge("u", "v", 0)
    return G


def _toy_candidate_rows():
    return [
        {"location_name": "near u", "latitude": 43.700, "longitude": -79.400, "total_pedestrian": 50},
        {"location_name": "near v", "latitude": 43.705, "longitude": -79.405, "total_pedestrian": 80},
    ]


def test_edge_crowding_computes_a_real_match_on_both_ends():
    G = _toy_edge_graph()
    rows = _toy_candidate_rows()
    assert edge_crowding(G, "u", "v", rows) == "low"


def test_edge_crowding_is_none_when_one_endpoint_has_no_match():
    G = _toy_edge_graph()
    rows = [_toy_candidate_rows()[0]]  # only a match for "u"
    assert edge_crowding(G, "u", "v", rows, max_distance_m=200) is None


def test_edge_crowding_is_none_when_neither_endpoint_has_a_match():
    G = _toy_edge_graph()
    assert edge_crowding(G, "u", "v", [], max_distance_m=200) is None
