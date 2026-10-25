"""GPU MLP model search with nested plant-grouped evaluation for PlantSounds."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from train_plantsounds_baseline import (
    CLASSES, DATA_DIR, MODEL_DIR, bootstrap_intervals, feature_vector,
    feature_vector_rich, plant_metrics, read_rows,
)


class PlantMLP(nn.Module):
    def __init__(self, input_dim: int, hidden: int, dropout: float):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(hidden, hidden // 2), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(hidden // 2, 2),
        )

    def forward(self, inputs):
        return self.network(inputs)


def plant_predictions(groups, labels, predictions):
    truth, predicted, plant_ids = [], [], []
    for plant in sorted(set(groups)):
        mask = groups == plant
        votes = Counter(int(value) for value in predictions[mask])
        top = max(votes.values())
        guess = sorted(label for label, count in votes.items() if count == top)[0]
        truth.append(int(labels[mask][0]))
        predicted.append(guess)
        plant_ids.append(str(plant))
    return np.asarray(truth), np.asarray(predicted), plant_ids


def plant_probability_predictions(groups, labels, probabilities):
    truth, predicted, plant_ids = [], [], []
    for plant in sorted(set(groups)):
        mask = groups == plant
        truth.append(int(labels[mask][0]))
        predicted.append(int(np.argmax(probabilities[mask].mean(axis=0))))
        plant_ids.append(str(plant))
    return np.asarray(truth), np.asarray(predicted), plant_ids


def config_grid():
    return [
        {"name": "welch_mlp_64", "feature_version": "welch32", "hidden": 64, "dropout": 0.15, "lr": 0.001, "weight_decay": 0.001},
        {"name": "welch_mlp_128", "feature_version": "welch32", "hidden": 128, "dropout": 0.25, "lr": 0.001, "weight_decay": 0.001},
        {"name": "welch_mlp_128_slow", "feature_version": "welch32", "hidden": 128, "dropout": 0.35, "lr": 0.0004, "weight_decay": 0.01},
        {"name": "rich_mlp_64", "feature_version": "rich96_envelope", "hidden": 64, "dropout": 0.15, "lr": 0.001, "weight_decay": 0.001},
        {"name": "rich_mlp_128", "feature_version": "rich96_envelope", "hidden": 128, "dropout": 0.25, "lr": 0.001, "weight_decay": 0.001},
        {"name": "rich_mlp_128_slow", "feature_version": "rich96_envelope", "hidden": 128, "dropout": 0.35, "lr": 0.0004, "weight_decay": 0.01},
    ]


def labels_as_indices(labels):
    mapping = {label: index for index, label in enumerate(CLASSES)}
    if np.issubdtype(np.asarray(labels).dtype, np.integer):
        values = np.asarray(labels, dtype=np.int64)
        if not set(np.unique(values)).issubset({0, 1}):
            raise ValueError("Numeric class IDs must be 0 or 1")
        return values
    return np.asarray([mapping[str(value)] for value in labels], dtype=np.int64)


def fit_mlp(x_train, y_train, groups_train, config, device, epochs, x_val=None, y_val=None, groups_val=None, patience=18):
    event_counts = Counter(groups_train)
    weights = np.asarray([1.0 / event_counts[group] for group in groups_train], dtype=np.float64)
    scaler = StandardScaler().fit(x_train, sample_weight=weights)
    train_scaled = scaler.transform(x_train).astype(np.float32)
    train_y = labels_as_indices(y_train)
    train_weights = weights * (len(weights) / weights.sum())
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)
    generator = torch.Generator(device="cpu").manual_seed(42)
    dataset = TensorDataset(
        torch.from_numpy(train_scaled),
        torch.from_numpy(train_y),
        torch.from_numpy(train_weights.astype(np.float32)),
    )
    batch_size = min(256, len(dataset))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, generator=generator, drop_last=False)
    model = PlantMLP(train_scaled.shape[1], config["hidden"], config["dropout"]).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config["lr"], weight_decay=config["weight_decay"])
    best_state = None
    best_epoch = epochs
    best_score = -1.0
    stale = 0
    if x_val is not None:
        val_scaled = scaler.transform(x_val).astype(np.float32)
        val_tensor = torch.from_numpy(val_scaled).to(device)
        val_y = labels_as_indices(y_val)
        val_group_array = np.asarray(groups_val)
    for epoch in range(1, epochs + 1):
        model.train()
        for batch_x, batch_y, batch_weight in loader:
            batch_x, batch_y, batch_weight = batch_x.to(device), batch_y.to(device), batch_weight.to(device)
            optimizer.zero_grad(set_to_none=True)
            per_sample = nn.functional.cross_entropy(model(batch_x), batch_y, reduction="none")
            loss = torch.sum(per_sample * batch_weight) / batch_weight.sum()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 3.0)
            optimizer.step()
        if x_val is not None:
            model.eval()
            with torch.no_grad():
                val_probabilities = torch.softmax(model(val_tensor), dim=1).cpu().numpy()
            truth_plants, prediction_plants, _ = plant_probability_predictions(val_group_array, val_y, val_probabilities)
            score = f1_score(truth_plants, prediction_plants, labels=(0, 1), average="macro", zero_division=0)
            if score > best_score:
                best_score, best_epoch, stale = float(score), epoch, 0
                best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            else:
                stale += 1
                if stale >= patience:
                    break
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    return model, scaler, best_epoch, best_score


def predict(model, scaler, x, device):
    model.eval()
    with torch.no_grad():
        values = torch.from_numpy(scaler.transform(x).astype(np.float32)).to(device)
        return model(values).argmax(dim=1).cpu().numpy()


def predict_probabilities(model, scaler, x, device):
    model.eval()
    with torch.no_grad():
        values = torch.from_numpy(scaler.transform(x).astype(np.float32)).to(device)
        return torch.softmax(model(values), dim=1).cpu().numpy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species", choices=("tomato", "tobacco"), required=True)
    parser.add_argument("--outer-folds", type=int, default=5)
    parser.add_argument("--inner-folds", type=int, default=3)
    parser.add_argument("--max-epochs", type=int, default=180)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable; refusing to label a CPU run as GPU training")
    device = torch.device("cuda:0")
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.set_num_threads(2)
    rows = read_rows(DATA_DIR / "metadata.csv", DATA_DIR / "raw", args.species)
    y_strings = np.asarray([row["condition"] for row in rows])
    y = labels_as_indices(y_strings)
    groups = np.asarray([row["plant_id"].strip() for row in rows])
    x_versions = {
        "welch32": np.vstack([feature_vector(Path(row["full_path"])) for row in rows]),
        "rich96_envelope": np.vstack([feature_vector_rich(Path(row["full_path"])) for row in rows]),
    }
    outer = StratifiedGroupKFold(n_splits=args.outer_folds, shuffle=True, random_state=42)
    outer_splits = list(outer.split(np.zeros(len(y)), y, groups))
    oof_probabilities = np.empty((len(y), 2), dtype=np.float64)
    fold_models, scaler_by_fold, heldout_by_fold, feature_by_fold, details = {}, {}, {}, {}, []
    for fold, (outer_train, outer_val) in enumerate(outer_splits, start=1):
        if set(groups[outer_train]) & set(groups[outer_val]):
            raise RuntimeError("Outer CV split leaked a plant")
        inner = StratifiedGroupKFold(n_splits=args.inner_folds, shuffle=True, random_state=733)
        inner_splits = list(inner.split(np.zeros(len(outer_train)), y[outer_train], groups[outer_train]))
        config_results = []
        for config in config_grid():
            inner_oof_probabilities = np.empty((len(outer_train), 2), dtype=np.float64)
            best_epochs = []
            for inner_train_local, inner_val_local in inner_splits:
                train_idx = outer_train[inner_train_local]
                val_idx = outer_train[inner_val_local]
                model, scaler, best_epoch, _ = fit_mlp(
                    x_versions[config["feature_version"]][train_idx], y[train_idx], groups[train_idx], config, device,
                    args.max_epochs, x_versions[config["feature_version"]][val_idx], y[val_idx], groups[val_idx],
                )
                inner_oof_probabilities[inner_val_local] = predict_probabilities(model, scaler, x_versions[config["feature_version"]][val_idx], device)
                best_epochs.append(best_epoch)
            inner_truth, inner_pred, _ = plant_probability_predictions(groups[outer_train], y[outer_train], inner_oof_probabilities)
            score = float(f1_score(inner_truth, inner_pred, labels=(0, 1), average="macro", zero_division=0))
            config_results.append({**config, "inner_plant_macro_f1": score, "inner_best_epochs": best_epochs})
        config_results.sort(key=lambda row: (row["inner_plant_macro_f1"], row["name"]), reverse=True)
        selected = config_results[0]
        selected_epochs = max(1, int(np.median(selected["inner_best_epochs"])))
        fold_model, fold_scaler, _, _ = fit_mlp(
            x_versions[selected["feature_version"]][outer_train], y[outer_train], groups[outer_train], selected, device,
            selected_epochs,
        )
        oof_probabilities[outer_val] = predict_probabilities(fold_model, fold_scaler, x_versions[selected["feature_version"]][outer_val], device)
        fold_models[str(fold)] = fold_model
        scaler_by_fold[str(fold)] = fold_scaler
        heldout_by_fold[str(fold)] = sorted(str(p) for p in set(groups[outer_val]))
        feature_by_fold[str(fold)] = selected["feature_version"]
        details.append({"fold": fold, "selected_config": selected, "refit_epochs": selected_epochs, "validation_plants": len(heldout_by_fold[str(fold)]), "top_inner_candidates": config_results[:4]})
        print(json.dumps({"device": torch.cuda.get_device_name(0), "fold": fold, "selected": selected["name"], "inner_f1": selected["inner_plant_macro_f1"], "outer_plants": len(heldout_by_fold[str(fold)])}), flush=True)

    final_names = Counter(detail["selected_config"]["name"] for detail in details)
    modal_name = final_names.most_common(1)[0][0]
    final_config = next(detail["selected_config"] for detail in details if detail["selected_config"]["name"] == modal_name)
    final_epochs = max(1, int(np.median([detail["refit_epochs"] for detail in details if detail["selected_config"]["name"] == modal_name])))
    final_model, final_scaler, _, _ = fit_mlp(x_versions[final_config["feature_version"]], y, groups, final_config, device, final_epochs)

    truth, pred, plant_ids = plant_probability_predictions(groups, y, oof_probabilities)
    event_predictions = oof_probabilities.argmax(axis=1)
    output = args.output or MODEL_DIR / f"{args.species}_dry_vs_cut_gpu_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_utc')}"
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    fold_dir = output / "fold_models"
    fold_dir.mkdir()
    for fold, model in fold_models.items():
        torch.save({"state_dict": model.state_dict(), "scaler_mean": scaler_by_fold[fold].mean_, "scaler_scale": scaler_by_fold[fold].scale_, "input_dim": model.network[0].in_features, "config": next(detail["selected_config"] for detail in details if str(detail["fold"]) == fold)}, fold_dir / f"fold_{fold}.pt")
    torch.save({"state_dict": final_model.state_dict(), "scaler_mean": final_scaler.mean_, "scaler_scale": final_scaler.scale_, "input_dim": final_model.network[0].in_features, "config": final_config}, output / "model.pt")
    (output / "model_config.json").write_text(json.dumps({"final_config": final_config, "final_epochs": final_epochs, "device_used": torch.cuda.get_device_name(0)}, indent=2) + "\n")
    manifest = json.loads((DATA_DIR / "source_manifest.json").read_text())
    report = {
        "task": "dry versus cut acoustic event classification", "species": args.species,
        "source_doi": "10.5061/dryad.jwstqjqf7", "source_archive_sha256": manifest.get("archive_sha256"),
        "metadata_csv_sha256": hashlib.sha256((DATA_DIR / "metadata.csv").read_bytes()).hexdigest(),
        "evaluation_status": "Exploratory nested GPU model development on previously inspected plant cohorts. Mean-probability aggregation was motivated by an earlier exploratory look at these same outer folds; rerunning nested tuning does not erase that analyst-selection bias. Validate a frozen method on new plants, sites, and recording sessions.",
        "class_names": list(CLASSES), "n_events": len(rows), "n_unique_plants": len(set(groups)),
        "split_method": f"Nested StratifiedGroupKFold outer={args.outer_folds}, inner={args.inner_folds}",
        "plant_aggregation": "mean event probability; inner candidate selection and early stopping use the same aggregation",
        "device": torch.cuda.get_device_name(0), "torch_version": torch.__version__, "cuda_version": torch.version.cuda,
        "candidate_grid": config_grid(), "outer_fold_details": details,
        "fold_heldout_plant_ids": heldout_by_fold, "fold_feature_version": feature_by_fold,
        "final_model_config": final_config, "final_model_feature_version": final_config["feature_version"],
        "final_model_epochs": final_epochs,
        "nested_tuned_plant_level_out_of_fold_metrics": {"unit": "plant; argmax of mean nested outer-fold event probabilities", "n_plants": len(plant_ids), **plant_metrics([CLASSES[int(v)] for v in truth], [CLASSES[int(v)] for v in pred]), "bootstrap_95_ci": bootstrap_intervals([CLASSES[int(v)] for v in truth], [CLASSES[int(v)] for v in pred])},
        "nested_tuned_event_level_out_of_fold_metrics": {"accuracy": float(accuracy_score(y, event_predictions)), "macro_f1": float(f1_score(y, event_predictions, labels=(0, 1), average="macro", zero_division=0))},
        "inference_policy": "Known source plant IDs use their held-out outer-fold checkpoint; unknown IDs use the full-data checkpoint and have no independent validation estimate.",
        "trained_utc": datetime.now(timezone.utc).isoformat(),
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(output), "species": args.species, "device": report["device"], "nested_plant_metrics": report["nested_tuned_plant_level_out_of_fold_metrics"], "final_config": final_config, "epochs": final_epochs}, indent=2), flush=True)


if __name__ == "__main__":
    main()
