"""Random Forest baseline for predicting edge accessibility."""

from sklearn.ensemble import RandomForestClassifier


def train_baseline(X_train, y_train, random_state=42):
    """Train a class-balanced Random Forest on edge features.

    class_weight="balanced" only helps when there's some minority-class
    signal to reweight -- it can't fix an absolute data-scarcity problem
    (see notes/06 for the real-data case where this wasn't enough).
    """
    model = RandomForestClassifier(
        n_estimators=100, random_state=random_state, class_weight="balanced"
    )
    model.fit(X_train, y_train)
    return model
