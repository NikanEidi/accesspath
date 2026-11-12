"""Feature-table construction for accessibility prediction (baseline and GCN)."""

import pandas as pd


def build_feature_table(graph, edges, require_tagged=True):
    """Build a feature DataFrame for the given (u, v, k, data) edges of graph.

    Pulls street_count/x/y from each edge's u endpoint. If require_tagged, only
    edges with a real wheelchair tag (yes/designated/no) are included --
    untagged edges have no ground-truth label to train or test on.
    """
    rows = []
    for u, v, k, data in edges:
        wheelchair = data.get("wheelchair")
        if require_tagged and wheelchair not in ("yes", "designated", "no"):
            continue

        highway = data.get("highway", "unknown")
        if isinstance(highway, list):
            highway = highway[0]
        surface = data.get("surface", "unknown")
        if isinstance(surface, list):
            surface = surface[0]

        rows.append({
            "u": u, "v": v, "k": k,
            "length": data.get("length", 0),
            "highway": highway,
            "surface": surface,
            "street_count": graph.nodes[u].get("street_count", 0),
            "x": graph.nodes[u].get("x", 0),
            "y": graph.nodes[u].get("y", 0),
            "label": 1 if wheelchair in ("yes", "designated") else 0,
        })
    return pd.DataFrame(rows)


def geographic_split(df, split_col):
    """Split a feature table at its median split_col, not a random shuffle.

    A geography-based split tests whether the model generalizes to a part of
    the city/area it never saw, instead of to unseen edges sitting right next
    to ones it trained on. The split column must NOT be the same one the
    label was generated from, or train/test end up almost entirely different
    classes (a real distribution-shift bug, not a fair test).
    """
    median = df[split_col].median()
    train_df = df[df[split_col] < median]
    test_df = df[df[split_col] >= median]
    return train_df, test_df


def encode_features(train_df, test_df, feature_cols=("length", "street_count"),
                     categorical_cols=("highway", "surface")):
    """One-hot encode categorical columns, aligning test to train's columns.

    train and test can see different categories (e.g. one has a "steps" edge
    the other doesn't), so test is reindexed onto train's columns with 0 for
    anything missing.
    """
    cols = list(feature_cols) + list(categorical_cols)
    train_encoded = pd.get_dummies(train_df[cols], columns=list(categorical_cols))
    test_encoded = pd.get_dummies(test_df[cols], columns=list(categorical_cols))
    test_encoded = test_encoded.reindex(columns=train_encoded.columns, fill_value=0)
    return train_encoded, test_encoded
