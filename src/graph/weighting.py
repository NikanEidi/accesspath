"""Turns an edge's OSM attributes into a routing weight."""


def accessibility_weight(attrs):
    base = attrs.get("length", 1)
    penalty = 0

    if attrs.get("wheelchair") == "no":
        penalty += 1000
    elif attrs.get("wheelchair") in ("yes", "designated"):
        penalty -= 2

    if attrs.get("surface") in ("gravel", "dirt", "grass", "ground"):
        penalty += 10

    return base + penalty
