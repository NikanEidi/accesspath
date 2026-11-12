"""A hand-rolled 2-layer Graph Convolutional Network, in plain PyTorch.

No PyTorch Geometric -- the message-passing math (neighbor-averaging via a
normalized adjacency matrix) is implemented directly instead of calling a
library black box.
"""

import torch
import torch.nn as nn


class GCNLayer(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.linear = nn.Linear(in_features, out_features)

    def forward(self, features, A_norm):
        neighbor_avg = A_norm @ features
        return self.linear(neighbor_avg)


class SimpleGCN(nn.Module):
    def __init__(self, in_features, hidden_features, num_classes):
        super().__init__()
        self.layer1 = GCNLayer(in_features, hidden_features)
        self.layer2 = GCNLayer(hidden_features, num_classes)

    def forward(self, features, A_norm):
        h = torch.relu(self.layer1(features, A_norm))
        return self.layer2(h, A_norm)


def normalized_adjacency(A):
    """Add self-loops and row-normalize an adjacency matrix for GCN message-passing.

    Self-loops (+ I) make sure a node's own features survive the averaging,
    not just its neighbors'. Row-normalizing (dividing by each node's degree)
    keeps the averaging a true average instead of a raw sum.
    """
    A_hat = A + torch.eye(A.shape[0])
    degree = A_hat.sum(dim=1, keepdim=True)
    return A_hat / degree


def train_gcn(model, X, A_norm, y, train_mask, epochs=100, lr=0.01, verbose=False):
    """Train model on the full graph, computing loss only over train_mask.

    train_mask selects which nodes' labels count toward the loss -- the
    model still sees the WHOLE graph during message-passing (masking, not
    physically splitting the graph, which would delete real edges and
    corrupt the neighbor structure for the remaining nodes).

    Call torch.manual_seed(...) before constructing `model`, not here, since
    reproducibility depends on the initial random weights, not the training
    loop itself.
    """
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        out = model(X, A_norm)
        loss = loss_fn(out[train_mask], y[train_mask])
        loss.backward()
        optimizer.step()
        if verbose and epoch % 20 == 0:
            print(f"epoch {epoch}, loss {loss.item():.4f}")
    return model
