"""Group-aware dry-vs-cut baseline using only source-verified PlantSounds rows."""

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
from scipy.io import wavfile
from scipy.signal import periodogram, welch
from scipy.stats import kurtosis, skew
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "datasets" / "public_plantsounds"
MODEL_DIR = ROOT / "ml" / "models" / "plantsounds"
CLASSES = ("dry", "cut")
BAND_EDGES = np.geomspace(20_000, 150_000, 33)


def read_rows(metadata_path: Path, root: Path, species: str) -> list[dict[str, str]]:
    rows = []
    with metadata_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("species", "").strip().lower() != species:
                continue
            condition = row.get("condition", "").strip().lower()
            if condition not in CLASSES:
                continue
            for field in ("plant_id", "id_source"):
                if not row.get(field, "").strip():
                    raise ValueError(f"Missing verified {field} in metadata row for {row.get('file_path')}")
            rel = Path(row["file_path"])
            if rel.is_absolute() or ".." in rel.parts:
                raise ValueError(f"Metadata file_path must be relative and confined to the dataset: {rel}")
            full = (root / rel).resolve()
            if root.resolve() not in full.parents or not full.is_file():
                raise FileNotFoundError(f"Missing or out-of-root audio path: {full}")
            rows.append({**row, "full_path": str(full), "condition": condition, "species": species})
    if not rows:
        raise ValueError(f"No dry/cut rows found for species={species!r}")
    paths = [row["full_path"] for row in rows]
    if len(paths) != len(set(paths)):
        raise ValueError("Metadata contains duplicate audio paths; remove duplicates before evaluation")
    return rows


def feature_vector(path: Path) -> np.ndarray:
    sample_rate, audio = wavfile.read(path)
    if sample_rate != 500_000:
        raise ValueError(f"Expected 500 kHz source audio, got {sample_rate} Hz: {path}")
    if audio.ndim != 1:
        raise ValueError(f"Expected mono source event, got shape {audio.shape}: {path}")
    if not 900 <= len(audio) <= 1100:
        raise ValueError(f"Expected approximately 2 ms (1000 samples), got {len(audio)}: {path}")
    if np.issubdtype(audio.dtype, np.integer):
        info = np.iinfo(audio.dtype)
        signal = audio.astype(np.float64) / max(abs(info.min), info.max)
    else:
        signal = audio.astype(np.float64)
    frequencies, power = welch(signal, fs=sample_rate, nperseg=min(512, len(signal)))
    band_power = []
    for lo, hi in zip(BAND_EDGES[:-1], BAND_EDGES[1:]):
        use = (frequencies >= lo) & (frequencies < hi)
        band_power.append(float(power[use].mean()) if use.any() else 0.0)
    absolute = np.abs(signal)
    peak_hz = float(frequencies[np.argmax(power)])
    centroid = float(np.sum(frequencies * power) / (np.sum(power) + 1e-15))
    stats = np.array([
        np.sqrt(np.mean(signal * signal)),
        np.max(absolute),
        np.mean(absolute),
        np.std(signal),
        peak_hz,
        centroid,
    ])
    return np.concatenate([np.log10(np.asarray(band_power) + 1e-18), np.log10(stats + 1e-12)])


def feature_vector_rich(path: Path) -> np.ndarray:
    """Expanded event features: finer spectrum, shape, and within-event envelope."""
    sample_rate, audio = wavfile.read(path)
    if sample_rate != 500_000 or audio.ndim != 1 or not 900 <= len(audio) <= 1100:
        raise ValueError(f"Expected mono 500 kHz ~2 ms source event: {path}")
    if np.issubdtype(audio.dtype, np.integer):
        info = np.iinfo(audio.dtype)
        signal = audio.astype(np.float64) / max(abs(info.min), info.max)
    else:
        signal = audio.astype(np.float64)

    frequencies, power = periodogram(signal, fs=sample_rate, window="hann", scaling="spectrum")
    edges = np.geomspace(20_000, 150_000, 65)
    bands = []
    for low, high in zip(edges[:-1], edges[1:]):
        band = power[(frequencies >= low) & (frequencies < high)]
        bands.append(float(np.mean(band)) if band.size else 0.0)
    normalized = power / (power.sum() + 1e-18)
    cumulative = np.cumsum(normalized)
    waveform_skew = float(skew(signal, bias=False)) if np.std(signal) > 1e-12 else 0.0
    waveform_kurtosis = float(kurtosis(signal, bias=False)) if np.std(signal) > 1e-12 else 0.0
    descriptors = np.array([
        np.sqrt(np.mean(signal ** 2)), np.max(np.abs(signal)), np.mean(np.abs(signal)),
        np.std(signal), waveform_skew, waveform_kurtosis,
        np.sum(frequencies * normalized),
        np.sqrt(np.sum(((frequencies - np.sum(frequencies * normalized)) ** 2) * normalized)),
        frequencies[min(int(np.searchsorted(cumulative, 0.85)), len(frequencies) - 1)],
        -np.sum(normalized * np.log(normalized + 1e-18)),
        np.exp(np.mean(np.log(power + 1e-18))) / (np.mean(power) + 1e-18),
        *np.quantile(np.abs(signal), [0.5, 0.75, 0.9, 0.95, 0.99]),
    ])
    # Preserve the short impulse's location and shape within each clip.
    envelope = []
    for section in np.array_split(signal, 16):
        envelope.extend([np.sqrt(np.mean(section ** 2)), np.max(np.abs(section))])
    return np.concatenate([
        np.log10(np.asarray(bands) + 1e-18),
        np.sign(descriptors) * np.log10(np.abs(descriptors) + 1e-12),
        np.log10(np.asarray(envelope) + 1e-12),
    ])


def plant_metrics(truth: list[str], predictions: list[str]) -> dict:
    return {
        "accuracy": float(accuracy_score(truth, predictions)),
        "macro_f1": float(f1_score(truth, predictions, labels=CLASSES, average="macro", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(truth, predictions)),
        "confusion_matrix_labels": list(CLASSES),
        "confusion_matrix": confusion_matrix(truth, predictions, labels=CLASSES).tolist(),
    }


def bootstrap_intervals(truth: list[str], predictions: list[str], repetitions: int = 2000) -> dict:
    rng = np.random.default_rng(42)
    scores = {"accuracy": [], "macro_f1": [], "balanced_accuracy": []}
    truth_array = np.asarray(truth)
    pred_array = np.asarray(predictions)
    for _ in range(repetitions):
        indices = rng.integers(0, len(truth_array), size=len(truth_array))
        y_true, y_pred = truth_array[indices], pred_array[indices]
        scores["accuracy"].append(accuracy_score(y_true, y_pred))
        scores["macro_f1"].append(f1_score(y_true, y_pred, labels=CLASSES, average="macro", zero_division=0))
        scores["balanced_accuracy"].append(balanced_accuracy_score(y_true, y_pred))
    return {
        "method": "percentile bootstrap over plant-level out-of-fold predictions; 2000 resamples; seed 42",
        "confidence_level": 0.95,
        "intervals": {metric: [float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))] for metric, values in scores.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=DATA_DIR / "raw")
    parser.add_argument("--metadata", type=Path, default=DATA_DIR / "metadata.csv")
    parser.add_argument("--species", choices=("tomato", "tobacco"), required=True)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = read_rows(args.metadata.resolve(), args.dataset_root.resolve(), args.species)
    metadata_digest = hashlib.sha256(args.metadata.resolve().read_bytes()).hexdigest()
    source_manifest_path = args.dataset_root.resolve().parent / "source_manifest.json"
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8")) if source_manifest_path.is_file() else None
    plant_groups = np.asarray([row["plant_id"].strip() for row in rows])
    sessions = [row.get("session_id", "").strip() for row in rows]
    labels = np.asarray([row["condition"] for row in rows])
    for label in CLASSES:
        n_plants = len(set(plant_groups[labels == label]))
        if n_plants < args.folds:
            raise ValueError(f"Need at least {args.folds} verified plant IDs for {label}; found {n_plants}")
    if args.folds < 3:
        raise ValueError("At least 3 group folds are required")

    features = np.vstack([feature_vector(Path(row["full_path"])) for row in rows])
    cv = StratifiedGroupKFold(n_splits=args.folds, shuffle=True, random_state=42)
    model = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, class_weight="balanced", max_iter=3000, random_state=42))
    events_per_plant = Counter(plant_groups)
    sample_weights = np.asarray([1.0 / events_per_plant[plant] for plant in plant_groups], dtype=np.float64)
    splits = list(cv.split(features, labels, plant_groups))
    for fold, (train_index, val_index) in enumerate(splits, start=1):
        train_plants = set(plant_groups[train_index])
        val_plants = set(plant_groups[val_index])
        if train_plants & val_plants:
            raise RuntimeError(f"Plant group leakage detected in fold {fold}")
        if set(labels[train_index]) != set(CLASSES) or set(labels[val_index]) != set(CLASSES):
            raise ValueError(f"Fold {fold} lacks one or more classes; cannot report complete grouped evaluation")
    predicted = np.empty_like(labels)
    fold_scores = []
    heldout_plants_by_fold: dict[str, list[str]] = {}
    fold_models = []
    majority_plant_predictions: dict[str, str] = {}
    for fold, (train_index, val_index) in enumerate(splits, start=1):
        fold_model = clone(model)
        fit_weights = sample_weights[train_index]
        fold_model.fit(
            features[train_index],
            labels[train_index],
            standardscaler__sample_weight=fit_weights,
            logisticregression__sample_weight=fit_weights,
        )
        fold_pred = fold_model.predict(features[val_index])
        predicted[val_index] = fold_pred
        train_plants = set(plant_groups[train_index])
        val_plants = set(plant_groups[val_index])
        heldout_plants_by_fold[str(fold)] = sorted(str(plant) for plant in val_plants)
        fold_models.append(fold_model)
        train_plant_labels = {plant: str(labels[np.flatnonzero(plant_groups == plant)[0]]) for plant in train_plants}
        fold_majority = Counter(train_plant_labels.values()).most_common(1)[0][0]
        for plant in val_plants:
            if plant in majority_plant_predictions:
                raise RuntimeError(f"Plant appears in multiple validation folds: {plant}")
            majority_plant_predictions[str(plant)] = fold_majority
        fold_scores.append({
            "fold": fold,
            "train_plant_count": len(set(plant_groups[train_index])),
            "validation_plant_count": len(set(plant_groups[val_index])),
            "accuracy": float(accuracy_score(labels[val_index], fold_pred)),
            "macro_f1": float(f1_score(labels[val_index], fold_pred, labels=CLASSES, average="macro", zero_division=0)),
            "balanced_accuracy": float(balanced_accuracy_score(labels[val_index], fold_pred)),
        })
    model.fit(
        features,
        labels,
        standardscaler__sample_weight=sample_weights,
        logisticregression__sample_weight=sample_weights,
    )
    output = args.output or MODEL_DIR / f"{args.species}_dry_vs_cut_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_utc')}"
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    joblib.dump(model, output / "model.joblib")
    fold_model_dir = output / "fold_models"
    fold_model_dir.mkdir()
    for fold, fold_model in enumerate(fold_models, start=1):
        joblib.dump(fold_model, fold_model_dir / f"fold_{fold}.joblib")
    cm = confusion_matrix(labels, predicted, labels=CLASSES)
    plant_true: list[str] = []
    plant_predicted: list[str] = []
    for plant in sorted(set(plant_groups)):
        plant_mask = plant_groups == plant
        plant_true.append(str(labels[plant_mask][0]))
        plant_predicted.append(Counter(predicted[plant_mask]).most_common(1)[0][0])
    plant_scores = plant_metrics(plant_true, plant_predicted)
    majority_predictions = [majority_plant_predictions[plant] for plant in sorted(set(plant_groups))]
    majority_scores = plant_metrics(plant_true, majority_predictions)
    report = {
        "task": "dry versus cut acoustic event classification",
        "species": args.species,
        "source_doi": "10.5061/dryad.jwstqjqf7",
        "source_archive_sha256": source_manifest.get("archive_sha256") if source_manifest else None,
        "metadata_csv_sha256": metadata_digest,
        "evaluation_status": "Exploratory model-development cross-validation. The same plant cohorts were used to compare unweighted and plant-balanced training; the scores and bootstrap intervals are not independent confirmation. Validate the frozen method on newly collected plants before claiming generalization.",
        "class_names": list(CLASSES),
        "n_events": len(rows),
        "n_unique_plants": len(set(plant_groups)),
        "n_unique_sessions": len(set(session for session in sessions if session)) or None,
        "session_id_coverage": sum(bool(session) for session in sessions) / len(sessions),
        "grouping_key": "verified plant_id parsed from the source README filename convention; all events from the same plant stay in one fold",
        "training_sample_weight": "inverse number of sound events per plant; each plant contributes equal total weight, combined with class-balanced logistic regression",
        "split_method": f"StratifiedGroupKFold(n_splits={args.folds}, shuffle=True, random_state=42)",
        "fold_heldout_plant_ids": heldout_plants_by_fold,
        "inference_policy": "Known source plant IDs are predicted with the fold model that excluded that plant. Unknown IDs use the full-data model and have no independent validation estimate.",
        "fold_metrics": fold_scores,
        "out_of_fold_metrics": {
            "accuracy": float(accuracy_score(labels, predicted)),
            "macro_f1": float(f1_score(labels, predicted, labels=CLASSES, average="macro", zero_division=0)),
            "balanced_accuracy": float(balanced_accuracy_score(labels, predicted)),
            "confusion_matrix_labels": list(CLASSES),
            "confusion_matrix": cm.tolist(),
        },
        "plant_level_out_of_fold_metrics": {
            "unit": "plant; majority vote over that plant's out-of-fold event predictions",
            "n_plants": len(plant_true),
            **plant_scores,
            "bootstrap_95_ci": {
                **bootstrap_intervals(plant_true, plant_predicted),
                "caveat": "Sampling interval only; does not account for model iteration or model-selection uncertainty.",
            },
        },
        "plant_level_majority_baseline": {
            "description": "For each validation fold, always predict the majority training-plant condition.",
            **majority_scores,
        },
        "caveat": "This distinguishes dry from cut source conditions within one species. It is not healthy-versus-stressed detection, and does not establish a general plant diagnosis. Dryad source snippets are 2 ms event clips; report counts and confidence intervals at plant level for publication-quality inference.",
        "trained_utc": datetime.now(timezone.utc).isoformat(),
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "events": len(rows), "plants": len(set(plant_groups)), "plant_level_out_of_fold": report["plant_level_out_of_fold_metrics"], "plant_level_majority_baseline": report["plant_level_majority_baseline"]}, indent=2))


if __name__ == "__main__":
    main()
