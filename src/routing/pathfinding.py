"""Accessibility-aware shortest-path routing over a graph."""

import networkx as nx

from src.graph.weighting import accessibility_weight


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
