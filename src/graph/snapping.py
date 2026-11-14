"""Snapping a real-world (lat, lon) point onto the nearest graph node."""

from geopy.distance import distance


def nearest_node_id(G, target_latlon, max_distance_m=None):
    """Return the id of G's node closest to target_latlon = (lat, lon).

    Works on any graph whose nodes carry "y" (latitude) and "x" (longitude)
    attributes -- the same convention accessibility_weight() already relies on.

    If max_distance_m is given and even the closest node is farther than
    that, returns None instead of a misleading match -- real-world points
    outside the graph's coverage area (e.g. a Scarborough intersection
    snapped onto a Downtown-Toronto-only graph) would otherwise silently
    "snap" to a node kilometers away.
    """
    best_id = min(
        G.nodes,
        key=lambda node_id: distance(
            target_latlon,
            (G.nodes[node_id]["y"], G.nodes[node_id]["x"])
        ).meters
    )

    if max_distance_m is not None:
        best_distance = distance(
            target_latlon,
            (G.nodes[best_id]["y"], G.nodes[best_id]["x"])
        ).meters
        if best_distance > max_distance_m:
            return None

    return best_id


def nearest_row(target_latlon, candidate_rows, lat_key="latitude", lon_key="longitude",
                 max_distance_m=None):
    """Return the candidate_rows dict closest to target_latlon, or None.

    The reverse direction of nearest_node_id: here the candidates are real
    external data rows (e.g. Toronto pedestrian-volume records), and the
    target is usually a graph node's own (y, x) coordinates -- used to find
    which real-world record, if any, applies to a given graph node.
    """
    if not candidate_rows:
        return None

    best_row = min(
        candidate_rows,
        key=lambda row: distance(target_latlon, (row[lat_key], row[lon_key])).meters
    )

    if max_distance_m is not None:
        best_distance = distance(
            target_latlon, (best_row[lat_key], best_row[lon_key])
        ).meters
        if best_distance > max_distance_m:
            return None

    return best_row
