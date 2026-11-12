"""Tests for the four edge-case neighborhoods: construction, dead ends, stairs, islands."""

import networkx as nx
import pytest

from src.routing.pathfinding import find_accessible_route


def test_construction_zone_detours_around_the_closed_segment(construction_zone):
    path, cost = find_accessible_route(construction_zone, "cz_0_0", "cz_0_4")
    assert "cz_1_0" in path  # must dip into the bypass row
    # the direct edge straddling the closed segment should not be used
    assert not ("cz_0_2" in path and "cz_0_3" in path)


def test_plain_shortest_path_would_walk_through_construction(construction_zone):
    plain = nx.shortest_path(construction_zone, "cz_0_0", "cz_0_4", weight="length")
    assert plain == ["cz_0_0", "cz_0_1", "cz_0_2", "cz_0_3", "cz_0_4"]


def test_dead_end_through_route_ignores_branches(dead_end_district):
    path, cost = find_accessible_route(dead_end_district, "de_spine_0", "de_spine_4")
    assert "de_branch_0_0" not in path
    assert "de_branch_1_0" not in path


def test_routing_into_a_dead_end_still_works(dead_end_district):
    path, cost = find_accessible_route(dead_end_district, "de_spine_0", "de_branch_0_1")
    assert path[-1] == "de_branch_0_1"
    assert path[0] == "de_spine_0"


def test_untagged_stairs_are_still_treated_as_inaccessible(stairs_only_zone):
    # No wheelchair tag on the stairs edge at all -- relies on the highway=steps rule.
    path, cost = find_accessible_route(stairs_only_zone, "so_bottom", "so_top")
    assert path == ["so_bottom", "so_ramp_mid", "so_top"]


def test_plain_shortest_path_would_pick_the_stairs(stairs_only_zone):
    plain = nx.shortest_path(stairs_only_zone, "so_bottom", "so_top", weight="length")
    assert plain == ["so_bottom", "so_top"]


def test_disconnected_island_has_no_path_to_the_rest_of_the_city(clearwell):
    with pytest.raises(nx.NetworkXNoPath):
        find_accessible_route(clearwell, "di_0", "ot_0_0")


def test_disconnected_island_nodes_can_still_reach_each_other(disconnected_island):
    path, cost = find_accessible_route(disconnected_island, "di_0", "di_3")
    assert path == ["di_0", "di_1", "di_2", "di_3"]
