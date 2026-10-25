"""Nested plant-grouped model and feature search for PlantSounds dry-vs-cut."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from train_plantsounds_baseline import (
    CLASSES, DATA_DIR, MODEL_DIR, bootstrap_intervals, feature_vector,
    feature_vector_rich, plant_metrics, read_rows,
)


def candidates() -> list[dict]:
    configs = []
    for feature_version in ("welch32", "rich96_envelope"):
        configs.extend([
            {"name": "logistic_c10", "feature_version": feature_version, "family": "logistic", "params": {"C": 10.0}},
            {"name": "rbf_svc_c30", "feature_version": feature_version, "family": "rbf_svc", "params": {"C": 30.0}},
            {"name": "extra_trees_leaf3", "feature_version": feature_version, "family": "extra_trees", "params": {"min_samples_leaf": 3}},
            {"name": "hist_gradient_100", "feature_version": feature_version, "family": "hist_gradient", "params": {"max_iter": 100}},
        ])
    return configs


def build_model(config: dict):
    family = config["family"]
    params = config["params"]
    if family == "logistic":
        estimator = LogisticRegression(C=params["C"], class_weight="balanced", max_iter=4000, random_state=42)
    elif family == "rbf_svc":
        estimator = SVC(C=params["C"], kernel="rbf", gamma="scale", class_weight=None, random_state=42)
    elif family == "extra_trees":
        estimator = ExtraTreesClassifier(n_estimators=200, min_samples_leaf=params["min_samples_leaf"], max_features=0.8, class_weight=None, random_state=42, n_jobs=1)
    elif family == "random_forest":
        estimator = RandomForestClassifier(n_estimators=200, min_samples_leaf=params["min_samples_leaf"], max_features="sqrt", class_weight=None, random_state=42, n_jobs=1)
    elif family == "hist_gradient":
        estimator = HistGradientBoostingClassifier(max_iter=params["max_iter"], learning_rate=0.08, l2_regularization=1.0, max_leaf_nodes=15, random_state=42)
    elif family == "gradient_boost":
        estimator = GradientBoostingClassifier(n_estimators=params["n_estimators"], learning_rate=params["learning_rate"], max_depth=2, min_samples_leaf=5, random_state=42)
    else:
        raise ValueError(f"Unknown model family: {family}")
    return make_pipeline(StandardScaler(), estimator)


def plant_predictions(groups: np.ndarray, labels: np.ndarray, predictions: np.ndarray) -> tuple[list[str], list[str], list[str]]:
    truth, predicted, plant_ids = [], [], []
    for plant in sorted(set(groups)):
        mask = groups == plant
        votes = Counter(str(value) for value in predictions[mask])
        top = max(votes.values())
        # Stable tie-breaking makes every report reproducible.
        guess = sorted(label for label, count in votes.items() if count == top)[0]
        truth.append(str(labels[mask][0]))
        predicted.append(guess)
        plant_ids.append(str(plant))
    return truth, predicted, plant_ids


def grouped_fit(model, x, y, groups):
    event_counts = Counter(groups)
    weights = np.asarray([1.0 / event_counts[group] for group in groups], dtype=float)
    model.fit(x, y, standardscaler__sample_weight=weights, **{f"{model.steps[-1][0]}__sample_weight": weights})
    return model


def tune_on_training(x_by_version, y, groups, folds=3):
    cv = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=733)
    splits = list(cv.split(np.zeros(len(y)), y, groups))
    choices = []
    for config in candidates():
        oof = np.empty_like(y)
        for train_index, val_index in splits:
            train_groups, val_groups = set(groups[train_index]), set(groups[val_index])
            if train_groups & val_groups:
                raise RuntimeError("Inner tuning split leaked a plant group")
            if set(y[train_index]) != set(CLASSES) or set(y[val_index]) != set(CLASSES):
                raise ValueError("Inner tuning fold is missing a class")
            model = build_model(config)
            model = grouped_fit(model, x_by_version[config["feature_version"]][train_index], y[train_index], groups[train_index])
            oof[val_index] = model.predict(x_by_version[config["feature_version"]][val_index])
        truth, prediction, _ = plant_predictions(groups, y, oof)
        choices.append({**config, "inner_plant_macro_f1": float(f1_score(truth, prediction, labels=CLASSES, average="macro", zero_division=0))})
    choices.sort(key=lambda row: (row["inner_plant_macro_f1"], row["name"]), reverse=True)
    return choices[0], choices


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species", choices=("tomato", "tobacco"), required=True)
    parser.add_argument("--outer-folds", type=int, default=5)
    parser.add_argument("--inner-folds", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = read_rows(DATA_DIR / "metadata.csv", DATA_DIR / "raw", args.species)
    y = np.asarray([row["condition"] for row in rows])
    groups = np.asarray([row["plant_id"].strip() for row in rows])
    x_by_version = {
        "welch32": np.vstack([feature_vector(Path(row["full_path"])) for row in rows]),
        "rich96_envelope": np.vstack([feature_vector_rich(Path(row["full_path"])) for row in rows]),
    }
    outer_cv = StratifiedGroupKFold(n_splits=args.outer_folds, shuffle=True, random_state=42)
    outer_splits = list(outer_cv.split(np.zeros(len(y)), y, groups))
    nested_oof = np.empty_like(y)
    baseline_oof = np.empty_like(y)
    fold_models = {}
    heldout_plants_by_fold = {}
    feature_version_by_fold = {}
    outer_details = []

    for fold, (train_index, val_index) in enumerate(outer_splits, start=1):
        if set(groups[train_index]) & set(groups[val_index]):
            raise RuntimeError(f"Outer fold {fold} leaked a plant group")
        if set(y[train_index]) != set(CLASSES) or set(y[val_index]) != set(CLASSES):
            raise ValueError(f"Outer fold {fold} is missing a class")
        selected, tuning_table = tune_on_training(
            {key: value[train_index] for key, value in x_by_version.items()},
            y[train_index], groups[train_index], folds=args.inner_folds,
        )
        final_fold_model = build_model(selected)
        grouped_fit(final_fold_model, x_by_version[selected["feature_version"]][train_index], y[train_index], groups[train_index])
        nested_oof[val_index] = final_fold_model.predict(x_by_version[selected["feature_version"]][val_index])

        baseline_config = {"feature_version": "welch32", "family": "logistic", "params": {"C": 1.0}}
        baseline = build_model(baseline_config)
        grouped_fit(baseline, x_by_version["welch32"][train_index], y[train_index], groups[train_index])
        baseline_oof[val_index] = baseline.predict(x_by_version["welch32"][val_index])

        fold_models[str(fold)] = final_fold_model
        heldout_plants_by_fold[str(fold)] = sorted(str(value) for value in set(groups[val_index]))
        feature_version_by_fold[str(fold)] = selected["feature_version"]
        outer_details.append({
            "fold": fold,
            "train_plant_count": len(set(groups[train_index])),
            "validation_plant_count": len(set(groups[val_index])),
            "selected_config": selected,
            "top_inner_candidates": tuning_table[:5],
        })
        print(json.dumps({"fold": fold, "selected": selected, "outer_plants": len(set(groups[val_index]))}), flush=True)

    # Use the modal inner-CV choice from the outer training searches for the full-data inference checkpoint.
    selected_configs = [detail["selected_config"] for detail in outer_details]
    config_keys = [json.dumps(config, sort_keys=True) for config in selected_configs]
    selected_key = Counter(config_keys).most_common(1)[0][0]
    final_config = json.loads(selected_key)
    final_model = build_model(final_config)
    grouped_fit(final_model, x_by_version[final_config["feature_version"]], y, groups)

    nested_truth, nested_prediction, plant_ids = plant_predictions(groups, y, nested_oof)
    baseline_truth, baseline_prediction, _ = plant_predictions(groups, y, baseline_oof)
    output = args.output or MODEL_DIR / f"{args.species}_dry_vs_cut_tuned_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_utc')}"
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    joblib.dump(final_model, output / "model.joblib")
    fold_dir = output / "fold_models"
    fold_dir.mkdir()
    for fold, model in fold_models.items():
        joblib.dump(model, fold_dir / f"fold_{fold}.joblib")

    train_meta_path = DATA_DIR / "metadata.csv"
    manifest_path = DATA_DIR / "source_manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    report = {
        "task": "dry versus cut acoustic event classification",
        "species": args.species,
        "source_doi": "10.5061/dryad.jwstqjqf7",
        "source_archive_sha256": manifest.get("archive_sha256"),
        "metadata_csv_sha256": hashlib.sha256(train_meta_path.read_bytes()).hexdigest(),
        "evaluation_status": "Exploratory nested model development on previously inspected plant cohorts. Outer folds were excluded from each fold's hyperparameter and feature selection, but repeated analyst iteration on this dataset means results are not independent confirmation. Validate a frozen pipeline on new plants, sites, and acquisition sessions.",
        "class_names": list(CLASSES),
        "n_events": len(rows),
        "n_unique_plants": len(set(groups)),
        "grouping_key": "source README plant ID; all events per plant held out together",
        "split_method": f"Nested StratifiedGroupKFold: outer={args.outer_folds}, inner={args.inner_folds}; outer random_state=42; inner random_state=733",
        "selection_metric": "inner plant-level macro-F1 after majority vote over each plant's held-out events",
        "candidate_search": "Welch32 and rich96_envelope features; tuned logistic regression, RBF SVC, ExtraTrees, RandomForest, histogram gradient boosting, and gradient boosting. Events weighted inversely by event count per plant during fitting.",
        "outer_fold_details": outer_details,
        "fold_heldout_plant_ids": heldout_plants_by_fold,
        "fold_feature_version": feature_version_by_fold,
        "final_model_config": final_config,
        "final_model_feature_version": final_config["feature_version"],
        "final_model_selection": "Modal inner-CV-selected configuration among outer training folds, refit on all source plants; outer performance is the nested OOF procedure, not the full-data checkpoint's independent test score.",
        "nested_tuned_plant_level_out_of_fold_metrics": {
            "unit": "plant; majority vote over nested outer-fold event predictions",
            "n_plants": len(plant_ids),
            **plant_metrics(nested_truth, nested_prediction),
            "bootstrap_95_ci": bootstrap_intervals(nested_truth, nested_prediction),
        },
        "matched_baseline_plant_level_out_of_fold_metrics": {
            "unit": "same outer folds; existing Welch32 + weighted logistic regression baseline",
            "n_plants": len(plant_ids),
            **plant_metrics(baseline_truth, baseline_prediction),
            "bootstrap_95_ci": bootstrap_intervals(baseline_truth, baseline_prediction),
        },
        "nested_tuned_event_level_out_of_fold_metrics": {
            "accuracy": float(accuracy_score(y, nested_oof)),
            "macro_f1": float(f1_score(y, nested_oof, labels=CLASSES, average="macro", zero_division=0)),
        },
        "matched_baseline_event_level_out_of_fold_metrics": {
            "accuracy": float(accuracy_score(y, baseline_oof)),
            "macro_f1": float(f1_score(y, baseline_oof, labels=CLASSES, average="macro", zero_division=0)),
        },
        "inference_policy": "Known source plant IDs use their selected outer-fold model; unknown IDs use the full-data checkpoint and have no independent validation estimate.",
        "trained_utc": datetime.now(timezone.utc).isoformat(),
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "species": args.species, "selected_final_config": final_config, "tuned_plant_level": report["nested_tuned_plant_level_out_of_fold_metrics"], "baseline_plant_level": report["matched_baseline_plant_level_out_of_fold_metrics"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
