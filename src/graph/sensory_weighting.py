"""Sensory/cognitive-load weighting (crowding, construction, noise) -- kept
fully separate from accessibility_weight() so physical and sensory needs are
never blended into one opaque score. See research/sensory-accessibility-ontario.md
for the design decision behind this.
"""

import pandas as pd

from src.graph.snapping import nearest_row

# Real quartile boundaries from Toronto's full "Traffic Volumes - Multimodal
# Intersection Turning Movement Counts" dataset (6,421 intersections,
# total_pedestrian field): 25th percentile 164, 75th percentile 1197.5.
CROWDING_BINS = [-1, 164, 1197.5, float("inf")]
CROWDING_LABELS = ["low", "medium", "high"]

# Deliberately not as severe as accessibility_weight()'s 1000-point penalty
# for wheelchair:no/steps/construction -- those are real physical barriers
# (impossible to pass), while crowding is a strong preference to avoid, not
# a hard block. Open to tuning once this is actually tested on real routes.
CROWDING_PENALTIES = {"low": 0, "medium": 20, "high": 200}


def crowding_level(count_u, count_v):
    """Bucket an edge's crowding level from its two endpoints' pedestrian counts.

    Averages the two raw counts first (reduces per-point noise from each
    being a single-day snapshot), then buckets the average -- never used as
    a raw number directly, since daily pedestrian counts are noisy samples,
    not a stable average.
    """
    avg = (count_u + count_v) / 2
    bucket = pd.cut([avg], bins=CROWDING_BINS, labels=CROWDING_LABELS)
    return bucket[0]


def edge_crowding(G, u, v, candidate_rows, max_distance_m=200):
    """Return the crowding level for edge (u, v), or None if either endpoint
    has no real pedestrian-count match within max_distance_m.

    Snaps each endpoint to the nearest real-world record in candidate_rows
    (e.g. Toronto pedestrian-volume rows) via nearest_row(), rather than
    guessing a value for coverage the real data doesn't actually have.
    """
    u_latlon = (G.nodes[u]["y"], G.nodes[u]["x"])
    v_latlon = (G.nodes[v]["y"], G.nodes[v]["x"])

    u_match = nearest_row(u_latlon, candidate_rows, max_distance_m=max_distance_m)
    v_match = nearest_row(v_latlon, candidate_rows, max_distance_m=max_distance_m)

    if u_match is None or v_match is None:
        return None

    return crowding_level(u_match["total_pedestrian"], v_match["total_pedestrian"])


def sensory_weight(attrs, crowding):
    """Turn an edge's attrs and its crowding level into a real routing weight.

    Mirrors accessibility_weight()'s shape (base length + penalty) so the two
    functions compose the same way, but never shares a number with it --
    physical and sensory stay on two separate weight attributes, combined
    later by a profile, not blended here.
    """
    base = attrs.get("length", 1)
    penalty = CROWDING_PENALTIES.get(crowding, 0)
    return base + penalty
