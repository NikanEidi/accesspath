# 06 — Accessibility prediction: a baseline, and its real limit

## The new ML problem (after the pivot)

Instead of predicting travel time by time-of-day (doesn't fit a walking app, no real data for it), the real, useful ML task is: **predict whether an untagged edge is likely wheelchair-accessible**, using the 178 edges that do have a real `wheelchair` tag as labeled data. The other ~38,800 edges in Downtown Toronto have no tag at all — this model is meant to estimate accessibility for them.

## Building the baseline

Collected every edge with a real `wheelchair` tag (`yes`/`designated` → label 1, `no` → label 0) into a table, with features: `length`, `highway` type, `surface` (or `"unknown"` if missing), and `street_count` (a node attribute, pulled from the edge's `u` endpoint, not the edge itself).

Categorical features (`highway`, `surface`) were one-hot encoded with `pd.get_dummies`. Important detail: encoded the train and test sets separately, then `reindex`ed the test columns to match train's — otherwise if train and test happened to see different category values, the two tables could end up with mismatched columns and the model would break (or silently misalign features).

**Geography-based split, not random:** split on each edge's longitude (`x` of its `u` node) at the median, so train and test edges come from genuinely different halves of Downtown Toronto. This is a stricter test than a random shuffle — it checks whether the model generalizes to an unseen *area*, not just to unseen edges sitting right next to ones it trained on (the same spatial-leakage risk that a random split would miss).

## First result, and why the headline number was misleading

```
accuracy: 0.77
              precision  recall  f1-score  support
0               0.00      0.00    0.00        6
1               0.92      0.83    0.87       81
```

77% accuracy looks fine until you read past it: **0.00 recall on class 0** — the model never correctly identified a single inaccessible edge. It learned to just predict "accessible" for everything, because 158 of 174 labeled edges (91%) are class 1. Accuracy alone hid this completely; `classification_report`'s per-class breakdown is what actually revealed it.

## Trying the standard fix, and finding its real limit

The standard first fix for class imbalance is `class_weight="balanced"` — tells the model to penalize mistakes on the minority class more heavily during training. Tried it:

```
accuracy: 0.75
              precision  recall  f1-score  support
0               0.00      0.00    0.00        6
1               0.92      0.80    0.86       81
```

Still 0.00 recall on class 0. This is the real finding: `class_weight` only helps when there's *enough* minority-class data for the model to find a pattern in, just underweighted by the default loss. Here, the split left only **10 class-0 examples in training** (out of 16 total in the whole dataset) — that's not a weighting problem, it's a hard data-scarcity problem. No amount of reweighting invents information that was never there.

## Takeaway

- A high accuracy number can completely hide a model that's useless for the class that actually matters (the one we're trying to flag safely) — always check a per-class breakdown, not just the overall score, especially with imbalanced data.
- `class_weight="balanced"` is a real tool, but it has a precondition: it rebalances the *importance* of existing examples, it doesn't manufacture new ones. With only 16 real-world examples of the minority class, no amount of reweighting fixes a fundamentally too-small sample.
- This baseline is honestly not resume-ready yet — not because the code is wrong, but because the real-world data available right now isn't enough to support a reliable classifier for the minority class.

**Next:** the real fix is more data, not a different model — expand to a bigger area or multiple cities to collect more real `wheelchair: no` examples before trying the GNN, since a GNN would hit the exact same scarcity problem, just with a fancier model.
