"""Compare plant-level aggregation rules on saved held-out GPU fold checkpoints."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score

from train_plantsounds_baseline import CLASSES, DATA_DIR, bootstrap_intervals, feature_vector, feature_vector_rich, plant_metrics, read_rows
from train_plantsounds_gpu import PlantMLP, labels_as_indices


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve()
    report = json.loads((run / "report.json").read_text())
    species = report["species"]
    rows = read_rows(DATA_DIR / "metadata.csv", DATA_DIR / "raw", species)
    y = labels_as_indices(np.asarray([row["condition"] for row in rows]))
    groups = np.asarray([row["plant_id"].strip() for row in rows])
    x_versions = {
        "welch32": np.vstack([feature_vector(Path(row["full_path"])) for row in rows]),
        "rich96_envelope": np.vstack([feature_vector_rich(Path(row["full_path"])) for row in rows]),
    }
    probabilities = np.zeros((len(rows), 2), dtype=np.float64)
    seen = np.zeros(len(rows), dtype=bool)
    for fold, heldout_ids in report["fold_heldout_plant_ids"].items():
        mask = np.isin(groups, heldout_ids)
        checkpoint = torch.load(run / "fold_models" / f"fold_{fold}.pt", map_location="cpu", weights_only=False)
        config = checkpoint["config"]
        model = PlantMLP(checkpoint["input_dim"], config["hidden"], config["dropout"])
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        features = x_versions[config["feature_version"]][mask]
        standardized = (features - checkpoint["scaler_mean"]) / checkpoint["scaler_scale"]
        with torch.no_grad():
            logits = model(torch.from_numpy(standardized.astype(np.float32)))
            probabilities[mask] = torch.softmax(logits, dim=1).numpy()
        seen[mask] = True
    if not seen.all():
        raise RuntimeError("Saved fold checkpoints do not cover all events exactly once")
    event_pred = probabilities.argmax(axis=1)
    hard_truth, hard_pred, mean_prob_pred = [], [], []
    for plant in sorted(set(groups)):
        mask = groups == plant
        votes = Counter(int(value) for value in event_pred[mask])
        top = max(votes.values())
        hard_pred.append(sorted(label for label, count in votes.items() if count == top)[0])
        mean_prob_pred.append(int(np.argmax(probabilities[mask].mean(axis=0))))
        hard_truth.append(int(y[mask][0]))
    labels = [CLASSES[int(value)] for value in hard_truth]
    hard_labels = [CLASSES[int(value)] for value in hard_pred]
    soft_labels = [CLASSES[int(value)] for value in mean_prob_pred]
    result = {
        "species": species,
        "source_model_run": run.name,
        "methods": {
            "event_majority_vote": {"n_plants": len(labels), **plant_metrics(labels, hard_labels), "bootstrap_95_ci": bootstrap_intervals(labels, hard_labels)},
            "mean_event_probability": {"n_plants": len(labels), **plant_metrics(labels, soft_labels), "bootstrap_95_ci": bootstrap_intervals(labels, soft_labels)},
        },
        "event_level": {
            "accuracy": float(accuracy_score(y, event_pred)),
            "macro_f1": float(f1_score(y, event_pred, labels=(0, 1), average="macro", zero_division=0)),
        },
        "caveat": "Aggregation comparison reuses the nested outer-fold predictions and is exploratory; it does not establish a new independent performance estimate.",
    }
    (run / "aggregation_metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
