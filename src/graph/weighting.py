"""Turns an edge's OSM attributes into a routing weight."""


def accessibility_weight(attrs):
    base = attrs.get("length", 1)
    penalty = 0

    if attrs.get("construction") == "yes":
        # Temporarily closed, regardless of what it would normally be tagged.
        penalty += 1000

    wheelchair = attrs.get("wheelchair")
    if wheelchair == "no":
        penalty += 1000
    elif wheelchair in ("yes", "designated"):
        penalty -= 2
    elif attrs.get("highway") == "steps":
        # No explicit wheelchair tag doesn't mean accessible -- stairs are
        # inherently inaccessible even when nobody tagged them that way.
        penalty += 1000

    if attrs.get("surface") in ("gravel", "dirt", "grass", "ground"):
        penalty += 10

    return base + penalty
