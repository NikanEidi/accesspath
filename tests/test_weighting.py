from src.graph.weighting import accessibility_weight


def test_no_tags_returns_raw_length():
    assert accessibility_weight({"length": 50}) == 50


def test_wheelchair_no_adds_heavy_penalty():
    weight = accessibility_weight({"length": 50, "wheelchair": "no"})
    assert weight == 50 + 1000


def test_wheelchair_yes_gives_small_discount():
    weight = accessibility_weight({"length": 50, "wheelchair": "yes"})
    assert weight == 50 - 2


def test_wheelchair_designated_gives_small_discount():
    weight = accessibility_weight({"length": 50, "wheelchair": "designated"})
    assert weight == 50 - 2


def test_bad_surface_adds_small_penalty():
    weight = accessibility_weight({"length": 50, "surface": "gravel"})
    assert weight == 50 + 10


def test_good_surface_no_penalty():
    weight = accessibility_weight({"length": 50, "surface": "asphalt"})
    assert weight == 50


def test_missing_length_defaults_to_one():
    weight = accessibility_weight({})
    assert weight == 1


def test_compound_penalty_stacks():
    # Both a bad surface AND wheelchair:no should stack, not override each other.
    weight = accessibility_weight({"length": 50, "wheelchair": "no", "surface": "gravel"})
    assert weight == 50 + 1000 + 10


def test_construction_adds_heavy_penalty():
    weight = accessibility_weight({"length": 50, "construction": "yes"})
    assert weight == 50 + 1000


def test_untagged_steps_are_treated_as_inaccessible():
    # No explicit wheelchair tag at all -- highway=steps alone should trigger the penalty.
    weight = accessibility_weight({"length": 30, "highway": "steps"})
    assert weight == 30 + 1000


def test_steps_explicitly_marked_accessible_are_not_penalized():
    # An explicit wheelchair:yes should override the steps assumption (e.g. a stairlift).
    weight = accessibility_weight({"length": 30, "highway": "steps", "wheelchair": "yes"})
    assert weight == 30 - 2
