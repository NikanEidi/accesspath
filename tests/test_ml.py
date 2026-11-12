import networkx as nx
import torch

from src.ml.features import build_feature_table, geographic_split, encode_features
from src.ml.baseline import train_baseline
from src.ml.gcn import GCNLayer, SimpleGCN, normalized_adjacency, train_gcn


def _toy_graph():
    G = nx.MultiDiGraph()
    G.add_node(1, x=-79.0, y=43.0, street_count=3)
    G.add_node(2, x=-79.1, y=43.1, street_count=4)
    G.add_node(3, x=-79.2, y=43.2, street_count=2)
    G.add_node(4, x=-79.3, y=43.3, street_count=5)
    G.add_edge(1, 2, 0, length=10, highway=["footway"], surface="concrete", wheelchair="yes")
    G.add_edge(2, 3, 0, length=20, highway="footway", surface=["gravel"], wheelchair="no")
    G.add_edge(3, 4, 0, length=15, highway="footway", wheelchair="designated")
    G.add_edge(4, 1, 0, length=5, highway="footway", surface="asphalt")  # untagged
    return G


def test_build_feature_table_excludes_untagged_by_default():
    df = build_feature_table(_toy_graph(), _toy_graph().edges(keys=True, data=True))
    assert len(df) == 3
    assert set(df["label"]) == {0, 1}


def test_build_feature_table_can_include_untagged():
    df = build_feature_table(
        _toy_graph(), _toy_graph().edges(keys=True, data=True), require_tagged=False
    )
    assert len(df) == 4


def test_build_feature_table_unwraps_list_valued_tags():
    df = build_feature_table(_toy_graph(), _toy_graph().edges(keys=True, data=True))
    row = df[df["u"] == 1].iloc[0]
    assert row["highway"] == "footway"  # was ["footway"]


def test_geographic_split_puts_each_side_on_the_right_half():
    df = build_feature_table(
        _toy_graph(), _toy_graph().edges(keys=True, data=True), require_tagged=False
    )
    train_df, test_df = geographic_split(df, "x")
    assert len(train_df) + len(test_df) == len(df)
    assert (train_df["x"] < df["x"].median()).all()
    assert (test_df["x"] >= df["x"].median()).all()


def test_encode_features_aligns_train_and_test_columns():
    df = build_feature_table(
        _toy_graph(), _toy_graph().edges(keys=True, data=True), require_tagged=False
    )
    train_df, test_df = geographic_split(df, "x")
    X_train, X_test = encode_features(train_df, test_df)
    assert list(X_train.columns) == list(X_test.columns)
    assert len(X_train) == len(train_df)
    assert len(X_test) == len(test_df)


def test_train_baseline_predicts_one_row_per_input(riverside_district):
    edges = list(riverside_district.edges(keys=True, data=True))
    df = build_feature_table(riverside_district, edges)
    train_df, test_df = geographic_split(df, "y")
    X_train, X_test = encode_features(train_df, test_df)

    model = train_baseline(X_train, train_df["label"])
    preds = model.predict(X_test)
    assert len(preds) == len(test_df)


def test_normalized_adjacency_rows_sum_to_one():
    A = torch.tensor([[0.0, 1.0], [1.0, 0.0]])
    A_norm = normalized_adjacency(A)
    assert torch.allclose(A_norm.sum(dim=1), torch.ones(2))


def test_gcn_layer_output_shape():
    layer = GCNLayer(in_features=4, out_features=3)
    features = torch.rand(5, 4)
    A_norm = normalized_adjacency(torch.eye(5))
    out = layer(features, A_norm)
    assert out.shape == (5, 3)


def test_simple_gcn_end_to_end_shape():
    torch.manual_seed(0)
    model = SimpleGCN(in_features=4, hidden_features=6, num_classes=2)
    features = torch.rand(5, 4)
    A_norm = normalized_adjacency(torch.eye(5))
    out = model(features, A_norm)
    assert out.shape == (5, 2)


def test_train_gcn_reduces_loss():
    torch.manual_seed(0)
    features = torch.rand(10, 3)
    A_norm = normalized_adjacency(torch.eye(10))
    labels = torch.tensor([0, 1] * 5)
    train_mask = torch.tensor([True] * 10)

    model = SimpleGCN(in_features=3, hidden_features=4, num_classes=2)
    with torch.no_grad():
        loss_before = torch.nn.functional.cross_entropy(model(features, A_norm), labels)

    train_gcn(model, features, A_norm, labels, train_mask, epochs=50)
    with torch.no_grad():
        loss_after = torch.nn.functional.cross_entropy(model(features, A_norm), labels)

    assert loss_after < loss_before
