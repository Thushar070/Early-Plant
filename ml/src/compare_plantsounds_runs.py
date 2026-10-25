"""Paired plant bootstrap comparing saved grouped logistic and GPU MLP runs."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import torch
from sklearn.metrics import f1_score

from train_plantsounds_baseline import CLASSES, DATA_DIR, feature_vector, feature_vector_rich, read_rows
from train_plantsounds_gpu import PlantMLP


def aggregate_majority(groups, truth, predictions):
    plant_ids = sorted(set(groups))
    y_true, y_pred = [], []
    for plant in plant_ids:
        mask = groups == plant
        votes = Counter(str(value) for value in predictions[mask])
        y_pred.append(votes.most_common(1)[0][0])
        y_true.append(str(truth[mask][0]))
    return plant_ids, np.asarray(y_true), np.asarray(y_pred)


def load_baseline_predictions(rows, baseline_dir):
    report = json.loads((baseline_dir / "report.json").read_text())
    groups = np.asarray([row["plant_id"].strip() for row in rows])
    labels = np.asarray([row["condition"] for row in rows])
    features = np.vstack([feature_vector(Path(row["full_path"])) for row in rows])
    event_predictions = np.empty(len(rows), dtype=object)
    for fold, plant_ids in report["fold_heldout_plant_ids"].items():
        mask = np.isin(groups, plant_ids)
        model = joblib.load(baseline_dir / "fold_models" / f"fold_{fold}.joblib")
        event_predictions[mask] = model.predict(features[mask])
    if np.any(event_predictions == None):
        raise RuntimeError("Baseline folds did not produce predictions for every event")
    return aggregate_majority(groups, labels, event_predictions), report


def load_gpu_predictions(rows, gpu_dir):
    report = json.loads((gpu_dir / "report.json").read_text())
    groups = np.asarray([row["plant_id"].strip() for row in rows])
    labels = np.asarray([row["condition"] for row in rows])
    features = {
        "welch32": np.vstack([feature_vector(Path(row["full_path"])) for row in rows]),
        "rich96_envelope": np.vstack([feature_vector_rich(Path(row["full_path"])) for row in rows]),
    }
    event_probabilities = np.zeros((len(rows), 2), dtype=np.float64)
    covered = np.zeros(len(rows), dtype=bool)
    for fold, plant_ids in report["fold_heldout_plant_ids"].items():
        mask = np.isin(groups, plant_ids)
        checkpoint = torch.load(gpu_dir / "fold_models" / f"fold_{fold}.pt", map_location="cpu", weights_only=False)
        config = checkpoint["config"]
        model = PlantMLP(checkpoint["input_dim"], config["hidden"], config["dropout"])
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        matrix = features[config["feature_version"]][mask]
        matrix = (matrix - checkpoint["scaler_mean"]) / checkpoint["scaler_scale"]
        with torch.no_grad():
            event_probabilities[mask] = torch.softmax(model(torch.from_numpy(matrix.astype(np.float32))), dim=1).numpy()
        covered[mask] = True
    if not covered.all():
        raise RuntimeError("GPU folds did not produce predictions for every event")
    plant_ids = sorted(set(groups))
    y_true, y_pred = [], []
    for plant in plant_ids:
        mask = groups == plant
        y_true.append(str(labels[mask][0]))
        y_pred.append(CLASSES[int(np.argmax(event_probabilities[mask].mean(axis=0)))])
    return (plant_ids, np.asarray(y_true), np.asarray(y_pred)), report


def macro_f1(truth, pred):
    return float(f1_score(truth, pred, labels=CLASSES, average="macro", zero_division=0))


def paired_bootstrap(truth, baseline, candidate, repetitions=20000):
    rng = np.random.default_rng(42)
    differences = np.empty(repetitions)
    for index in range(repetitions):
        sample = rng.integers(0, len(truth), size=len(truth))
        differences[index] = macro_f1(truth[sample], candidate[sample]) - macro_f1(truth[sample], baseline[sample])
    return {
        "repetitions": repetitions,
        "seed": 42,
        "delta_macro_f1_candidate_minus_logistic": float(macro_f1(truth, candidate) - macro_f1(truth, baseline)),
        "percentile_95_interval": [float(np.quantile(differences, 0.025)), float(np.quantile(differences, 0.975))],
        "interpretation": "Plant-resampled paired interval; sampling uncertainty only, not analyst model-selection uncertainty.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species", choices=("tomato", "tobacco"), required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--gpu", type=Path, required=True)
    args = parser.parse_args()
    rows = read_rows(DATA_DIR / "metadata.csv", DATA_DIR / "raw", args.species)
    baseline, baseline_report = load_baseline_predictions(rows, args.baseline.resolve())
    candidate, gpu_report = load_gpu_predictions(rows, args.gpu.resolve())
    if baseline[0] != candidate[0] or not np.array_equal(baseline[1], candidate[1]):
        raise RuntimeError("Baseline and candidate do not contain the same plants and labels")
    reconstructed_baseline_f1 = macro_f1(baseline[1], baseline[2])
    reported_baseline_f1 = baseline_report["plant_level_out_of_fold_metrics"]["macro_f1"]
    if not np.isclose(reconstructed_baseline_f1, reported_baseline_f1, atol=1e-12):
        raise RuntimeError(f"Reconstructed baseline F1 {reconstructed_baseline_f1} does not reproduce report {reported_baseline_f1}")
    result = {
        "species": args.species,
        "n_plants": len(baseline[0]),
        "baseline_run": args.baseline.name,
        "candidate_run": args.gpu.name,
        "baseline_plant_macro_f1": reconstructed_baseline_f1,
        "candidate_plant_macro_f1": macro_f1(candidate[1], candidate[2]),
        "paired_bootstrap": paired_bootstrap(baseline[1], baseline[2], candidate[2]),
        "fold_grouping_matches": baseline_report["fold_heldout_plant_ids"] == gpu_report["fold_heldout_plant_ids"],
        "caveat": "Nested OOF predictions are plant-grouped and compared on identical folds. Results remain exploratory because the dataset and folds have been used for prior model iteration.",
    }
    output = args.gpu.resolve() / "paired_comparison_to_logistic.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
