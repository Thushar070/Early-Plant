"""Inspect a single PlantSounds-style event WAV and use a trained model if present."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import joblib
import numpy as np
from scipy.io import wavfile

from prepare_plantsounds import parse_source_ids
from train_plantsounds_baseline import MODEL_DIR, feature_vector


def model_for_species(species: str, plant_id: str) -> tuple[object, dict, str] | None:
    override = os.environ.get("PLANTSENSE_MODEL_DIR")
    candidates = [Path(override)] if override else sorted(MODEL_DIR.glob(f"{species}_dry_vs_cut_*"), reverse=True)
    for directory in candidates:
        # The upload service currently implements the Welch32 logistic artifact format.
        # Keep experimental GPU and alternative-feature search runs out of its auto-loader.
        if not re.fullmatch(rf"{re.escape(species)}_dry_vs_cut_\d{{8}}_\d{{6}}_utc", directory.name):
            continue
        report_path = directory / "report.json"
        model_path = directory / "model.joblib"
        if not report_path.is_file() or not model_path.is_file():
            continue
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("task") != "dry versus cut acoustic event classification" or report.get("species") != species:
            continue
        heldout_fold = next(
            (fold for fold, plant_ids in report.get("fold_heldout_plant_ids", {}).items() if plant_id in plant_ids),
            None,
        )
        if heldout_fold:
            heldout_model_path = directory / "fold_models" / f"fold_{heldout_fold}.joblib"
            if heldout_model_path.is_file():
                return joblib.load(heldout_model_path), report, "held_out_source_plant"
        return joblib.load(model_path), report, "unseen_plant_not_validated"
    return None


def analyze(paths: list[Path], species: str) -> dict:
    if not paths:
        raise ValueError("Provide at least one event WAV.")
    identities = [parse_source_ids(path.name) for path in paths]
    plant_ids = {plant_id for plant_id, _ in identities}
    sound_ids = [sound_id for _, sound_id in identities]
    if len(plant_ids) != 1:
        raise ValueError("All uploaded event filenames must have the same id_<plant_id> prefix.")
    if len(set(sound_ids)) != len(sound_ids):
        raise ValueError("Duplicate sound IDs were uploaded; keep one file per sound ID.")
    records = []
    feature_rows = []
    for path, (_, sound_id) in zip(paths, identities):
        sample_rate, audio = wavfile.read(path)
        features = feature_vector(path)
        signal = audio.astype(np.float64)
        if np.issubdtype(audio.dtype, np.integer):
            info = np.iinfo(audio.dtype)
            signal /= max(abs(info.min), info.max)
        records.append({
            "sound_id": sound_id,
            "sample_rate_hz": sample_rate,
            "duration_ms": round(1000 * len(audio) / sample_rate, 3),
            "samples": len(audio),
            "rms": float(np.sqrt(np.mean(signal * signal))),
        })
        feature_rows.append(features)
    matrix = np.vstack(feature_rows)
    result = {
        "status": "analysis_only",
        "event_count": len(paths),
        "plant_id": next(iter(plant_ids)),
        "species_scope": species,
        "classification_available": False,
        "classification": None,
        "scores": None,
        "events": records,
        "note": "Signal measurements are descriptive only. A trained, group-evaluated model is required before classification is available.",
    }
    plant_id = next(iter(plant_ids))
    loaded = model_for_species(species, plant_id)
    if loaded:
        model, report, evaluation_mode = loaded
        predictions = model.predict(matrix)
        probabilities = model.predict_proba(matrix)
        counts = {label: int(np.sum(predictions == label)) for label in model.classes_}
        max_count = max(counts.values())
        tied = [label for label, count in counts.items() if count == max_count]
        mean_probabilities = probabilities.mean(axis=0)
        prediction = tied[0] if len(tied) == 1 else str(model.classes_[int(np.argmax(mean_probabilities))])
        result.update({
            "status": "model_output",
            "classification_available": True,
            "classification": str(prediction),
            "aggregation": "majority vote over uploaded events from one plant; ties are broken by mean raw model score",
            "event_votes": counts,
            "scores": {str(label): float(score) for label, score in zip(model.classes_, mean_probabilities)},
            "model_species": species,
            "evaluation_mode": evaluation_mode,
            "model_cv_event_macro_f1": report["out_of_fold_metrics"]["macro_f1"],
            "model_cv_plant_macro_f1": report["plant_level_out_of_fold_metrics"]["macro_f1"],
            "note": "Experimental dry-versus-cut source-condition output for this species only. Mean scores are not calibrated confidence and this is not a plant-health diagnosis. For a known source plant, inference uses its held-out fold model; an unknown plant uses the full-data model and has no independent validation estimate.",
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wav", required=True, type=Path, nargs="+")
    parser.add_argument("--species", required=True, choices=("tomato", "tobacco"))
    args = parser.parse_args()
    print(json.dumps(analyze(args.wav, args.species)))


if __name__ == "__main__":
    main()
