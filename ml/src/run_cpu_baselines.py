"""Reproducible CPU baselines for the current small plant-audio dataset.

This is a diagnostic experiment, not a validated plant-stress detector. It
reads only train.csv and val.csv; it deliberately never opens test.csv.
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import scipy
from scipy.io import wavfile
from scipy.signal import welch
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, LinearSVC

ROOT = Path(__file__).resolve().parents[2]
CLASSES = ["Drought", "Heat Stress", "Mechanical Damage", "Nutrient Deficiency", "Pest Infestation"]
BANDS = np.geomspace(30.0, 11025.0, 65)


def read_manifest(csv_path: Path) -> tuple[list[Path], np.ndarray]:
    paths: list[Path] = []
    labels: list[int] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            label = row["label"]
            if label not in CLASSES:
                raise ValueError(f"Unknown label {label!r} in {csv_path}")
            paths.append(Path(row["audio_path"]))
            labels.append(CLASSES.index(label))
    return paths, np.asarray(labels, dtype=np.int64)


def extract_features(path: Path) -> np.ndarray:
    sample_rate, audio = wavfile.read(path)
    if audio.ndim != 1:
        audio = audio.mean(axis=1)
    if np.issubdtype(audio.dtype, np.integer):
        info = np.iinfo(audio.dtype)
        audio = audio.astype(np.float32) / max(abs(info.min), info.max)
    else:
        audio = audio.astype(np.float32)
    if len(audio) < 64 or sample_rate <= 0:
        raise ValueError(f"Invalid/short audio: {path}")

    freqs, power = welch(audio, fs=sample_rate, nperseg=min(1024, len(audio)))
    bands = []
    for low, high in zip(BANDS[:-1], BANDS[1:]):
        mask = (freqs >= low) & (freqs < high)
        bands.append(float(np.mean(power[mask])) if mask.any() else 0.0)
    spectral = np.log10(np.asarray(bands, dtype=np.float64) + 1e-12)
    stats = np.asarray([
        np.sqrt(np.mean(audio.astype(np.float64) ** 2)),
        np.max(np.abs(audio)),
        np.mean(np.abs(audio)),
        np.std(audio),
    ])
    return np.concatenate([spectral, np.log10(stats + 1e-12)])


def load_features(paths: list[Path]) -> np.ndarray:
    return np.vstack([extract_features(path) for path in paths])


def metric_row(name: str, model, x, y) -> dict:
    predicted = model.predict(x)
    return {
        "model": name,
        "accuracy": float(accuracy_score(y, predicted)),
        "macro_f1": float(f1_score(y, predicted, average="macro", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y, predicted)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New output directory; it must not already exist")
    args = parser.parse_args()
    output = args.output or ROOT / "ml" / "experiments" / datetime.now(timezone.utc).strftime("cpu_baseline_%Y%m%d_%H%M%S_utc")
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)

    train_paths, y_train = read_manifest(ROOT / "train.csv")
    val_paths, y_val = read_manifest(ROOT / "val.csv")
    x_train, x_val = load_features(train_paths), load_features(val_paths)

    candidates = [
        ("majority_baseline", DummyClassifier(strategy="most_frequent")),
        ("linear_svc_c1", make_pipeline(StandardScaler(), LinearSVC(C=1.0, random_state=42, max_iter=10000))),
        ("rbf_svc_c1", make_pipeline(StandardScaler(), SVC(C=1.0, kernel="rbf", class_weight="balanced"))),
        ("extra_trees_balanced", ExtraTreesClassifier(n_estimators=400, min_samples_leaf=2, class_weight="balanced", random_state=42, n_jobs=-1)),
    ]
    results = []
    fitted = {}
    for name, model in candidates:
        model.fit(x_train, y_train)
        results.append(metric_row(name, model, x_val, y_val))
        fitted[name] = model

    best = max(results, key=lambda row: (row["macro_f1"], row["balanced_accuracy"], row["accuracy"]))
    joblib.dump(fitted[best["model"]], output / "selected_model.joblib")
    report = {
        "experiment": "CPU handcrafted log-band spectral baselines",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "seed": 42,
        "selection_metric": "validation macro F1, then balanced accuracy, then accuracy",
        "test_set_used": False,
        "validation_metrics": results,
        "selected_model": best["model"],
        "selected_model_validation": best,
        "data": {
            "train_rows": len(y_train),
            "validation_rows": len(y_val),
            "classes": CLASSES,
            "sample_rate_hz": 22050,
            "duration_seconds": 2,
            "input_nyquist_hz": 11025,
            "plant_or_session_group_ids_verified": False,
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "interpretation": "Exploratory baseline only. Validation partitions lack verified plant/session grouping; labels and recording provenance are unverified. The pre-existing test partition was already examined during exploratory analysis and is not a pristine confirmatory holdout. No test metrics are reported.",
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "selected_model": best["model"], "validation": best}, indent=2))


if __name__ == "__main__":
    main()
