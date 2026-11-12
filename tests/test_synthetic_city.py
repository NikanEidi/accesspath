from collections import Counter

import networkx as nx

from src.data.synthetic_city import save_clearwell, load_clearwell


def test_old_town_is_sparse(old_town):
    tagged = sum(
        1 for u, v, k, d in old_town.edges(keys=True, data=True)
        if "wheelchair" in d or "surface" in d
    )
    assert old_town.number_of_edges() == 48
    assert tagged == 4  # deliberately almost-untagged


def test_riverside_is_balanced(riverside_district):
    counts = Counter(
        d.get("wheelchair") for u, v, k, d in riverside_district.edges(keys=True, data=True)
    )
    # Not a 91%/9% real-world imbalance -- both classes well represented.
    assert counts["yes"] > 0
    assert counts["no"] > 0
    ratio = counts["no"] / counts["yes"]
    assert 0.5 < ratio < 1.5


def test_university_quarter_mostly_accessible(university_quarter):
    counts = Counter(
        d.get("wheelchair") for u, v, k, d in university_quarter.edges(keys=True, data=True)
    )
    assert counts["designated"] > counts["no"]


def test_industrial_row_has_a_clean_bypass(industrial_row):
    direct_edge = industrial_row["ir_0_0"]["ir_0_1"][0]
    bypass_edge = industrial_row["ir_1_0"]["ir_1_1"][0]
    assert direct_edge["wheelchair"] == "no"
    assert bypass_edge["wheelchair"] == "yes"


def test_clearwell_combines_all_eight_neighborhoods(clearwell):
    prefixes = {n.split("_")[0] for n in clearwell.nodes}
    assert prefixes == {"ot", "rv", "uq", "ir", "cz", "de", "so", "di"}


def test_save_and_load_round_trip(tmp_path, clearwell):
    path = tmp_path / "clearwell_test.json"
    save_clearwell(path)
    reloaded = load_clearwell(path)

    assert reloaded.number_of_nodes() == clearwell.number_of_nodes()
    assert reloaded.number_of_edges() == clearwell.number_of_edges()
    assert set(reloaded.nodes) == set(clearwell.nodes)
