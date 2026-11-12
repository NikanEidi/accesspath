from src.graph.tag_filters import find_edges_with_tag


def test_finds_matching_edges(riverside_district):
    matches = find_edges_with_tag(riverside_district, "wheelchair", "no")
    assert len(matches) > 0
    for u, v, k in matches:
        assert riverside_district[u][v][k]["wheelchair"] == "no"


def test_returns_empty_list_when_nothing_matches(riverside_district):
    matches = find_edges_with_tag(riverside_district, "wheelchair", "a-value-that-does-not-exist")
    assert matches == []


def test_old_town_has_only_a_few_tagged_edges(old_town):
    # Old Town is deliberately sparse -- should be a small, exact count, not "most of the graph".
    matches = find_edges_with_tag(old_town, "wheelchair", "yes")
    assert len(matches) == 2  # one street, both directions
