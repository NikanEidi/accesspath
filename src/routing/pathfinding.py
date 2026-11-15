"""Accessibility-aware shortest-path routing over a graph."""

import networkx as nx

from src.graph.weighting import accessibility_weight
from src.graph.sensory_weighting import edge_crowding, sensory_weight


def apply_accessibility_weights(G, weight_fn=accessibility_weight, attr_name="acc_weight"):
    """Compute and store a routing weight on every edge of G, in place."""
    weights = {
        (u, v, k): weight_fn(data)
        for u, v, k, data in G.edges(keys=True, data=True)
    }
    nx.set_edge_attributes(G, weights, attr_name)
    return G


def find_accessible_route(G, source, target, weight_fn=accessibility_weight, attr_name="acc_weight"):
    """Apply accessibility weights to G and return the shortest accessible route."""
    apply_accessibility_weights(G, weight_fn=weight_fn, attr_name=attr_name)
    path = nx.shortest_path(G, source=source, target=target, weight=attr_name)
    cost = nx.shortest_path_length(G, source=source, target=target, weight=attr_name)
    return path, cost


def apply_sensory_weights(G, candidate_rows, max_distance_m=200, attr_name="sensory_weight"):
    """Compute and store a crowding-based routing weight on every edge of G, in place.

    Unlike apply_accessibility_weights(), this needs real-world data per edge
    (candidate_rows, e.g. Toronto pedestrian-volume rows) since crowding isn't
    an OSM tag -- each edge's endpoints get snapped to the nearest real record.
    """
    weights = {}
    for u, v, k, data in G.edges(keys=True, data=True):
        crowding = edge_crowding(G, u, v, candidate_rows, max_distance_m=max_distance_m)
        weights[(u, v, k)] = sensory_weight(data, crowding)
    nx.set_edge_attributes(G, weights, attr_name)
    return G


def find_low_sensory_route(G, source, target, candidate_rows, max_distance_m=200, attr_name="sensory_weight"):
    """Apply sensory weights to G and return the shortest low-crowding route."""
    apply_sensory_weights(G, candidate_rows, max_distance_m=max_distance_m, attr_name=attr_name)
    path = nx.shortest_path(G, source=source, target=target, weight=attr_name)
    cost = nx.shortest_path_length(G, source=source, target=target, weight=attr_name)
    return path, cost
