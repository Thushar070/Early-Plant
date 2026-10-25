# ML experiment notes

## Reproducibility

Training scripts use `SEED = 42` from `src/config.py` to seed Python, NumPy, and PyTorch RNGs when those libraries are available. This improves repeatability but does not guarantee bit-for-bit results across devices, library versions, or kernels.

The existing `train.csv`, `val.csv`, and `test.csv` files were preserved. Their original split-generation procedure and random seed are not present in this repository. The actual row proportions are 70% / 15% / 15%; see `split_manifest.json` for class counts and grouping notes.

The source metadata contains plant species, timestamps, and locations, but no verified plant ID or recording-session ID. Species and location values occur in all three splits. These CSVs therefore do not establish plant- or session-independent evaluation. Do not describe the current partitions as group-aware.

Use `python -m unittest discover -s ml/tests -v` to run the lightweight contract tests. The audio-dimension test requires the ML audio dependencies listed in `requirements.txt`; it is skipped when they are unavailable.

## CPU diagnostic baseline

Run `python ml/src/run_cpu_baselines.py` from the project root with NumPy, SciPy, scikit-learn, and joblib installed. It creates a timestamped, new-only directory under `ml/experiments/`, writes a JSON report and a joblib model, and refuses to overwrite an existing run. It reads only `train.csv` and `val.csv`; it does not open the test CSV. The checked-in run under `experiments/cpu_baseline_20261025/` selected a class-balanced ExtraTrees model at 21.2% validation macro-F1 and 21.3% accuracy, near five-class chance. This is an exploratory diagnostic, not a usable predictor.

The existing test partition was inspected during earlier exploratory analysis. It is therefore contaminated for confirmatory evaluation, even though the reproducible baseline runner avoids it. Do not report those exploratory test metrics as generalization evidence. See [RESEARCH.md](RESEARCH.md) for limitations, literature, and a recommended acquisition/evaluation plan.

## Public PlantSounds research pipeline

`data_sources.json` records the primary source and screened alternatives. The selected Dryad archive is CC0 and its landing page describes 2 ms, 500 kHz WAV events from dry/cut tomato and tobacco, empty pots, and greenhouse noise. The old local five-label dataset is preserved and is not used by this pipeline.

1. Run `python ml/src/prepare_plantsounds.py --archive /path/to/PlantSounds.zip --readme /path/to/README.md` when using a local archive, or omit `--archive` to download from Dryad. It safely extracts into a new directory, hashes the original ZIP, preserves the README, and writes a metadata template plus `metadata.csv`.
2. Review the source-derived labels and IDs. The supplied README documents the `id_<plant_id>_sound_<sound_id>.wav` naming scheme. The importer parses these IDs for plant folders and stores control recording IDs separately. The README does not provide session IDs, so those remain blank; plant ID is the split grouping key.
3. Train one species at a time: `python ml/src/train_plantsounds_baseline.py --species tomato` or `--species tobacco`. It uses 5-fold `StratifiedGroupKFold` grouped by plant ID, weights events so prolific plants do not dominate fitting, reports event- and plant-level out-of-fold metrics with a majority baseline, and stores a fitted logistic-regression pipeline and report in a new, non-overwriting run folder under `ml/models/plantsounds/`. It requires at least 5 plant IDs per condition.
4. The local Next.js upload panel posts same-plant WAV snippets to `/api/analyze` and loads the newest model artifact for the selected species. It accepts mono approximately 2 ms / 500 kHz event snippets, not the existing ordinary-rate 2-second WAV files. A known source plant ID is evaluated with the fold checkpoint that excluded it; an unseen ID uses the full-data checkpoint and is explicitly unvalidated. A model output is only dry-versus-cut for the selected species and is not a health diagnosis. The upload flow asks users to exclude empty-pot and greenhouse-noise controls.

Latest exploratory 5-fold plant-grouped plant macro-F1 is 76.1% for tomato and 71.4% for tobacco; event macro-F1 is 63.3% and 60.4%, respectively. Plant-level majority baselines are 37.4% and 35.7% macro-F1. The same plant cohorts were used while adjusting per-plant training weights, so neither the CV metrics nor the plant-bootstrap intervals are independent confirmation. Freeze the method and validate on newly collected plants (preferably a new site/time cohort) before claiming external performance.

The public archive was supplied locally because direct download was blocked in this environment. Its SHA-256 is recorded in `datasets/public_plantsounds/source_manifest.json`; the extracted source data, supplied README, and original ZIP are retained separately from the pre-existing local dataset. No model was trained on unverified labels or the incompatible local WAV collection. Python tests cover the fail-closed metadata and acquisition contracts; the app build still depends on the project-local Node packages being installed.

## GPU experiment

The separate GPU search requires Python 3.13, an NVIDIA driver, and `ml/requirements-gpu.txt`. It can be rerun with `.venv-plantgpu/bin/python ml/src/train_plantsounds_gpu.py --species tomato` (or `tobacco`). The script refuses to label CPU execution as a GPU run, performs nested plant-grouped tuning, and writes full-data plus outer-fold checkpoints to a new timestamped folder. These exploratory GPU checkpoints are not auto-loaded by the dashboard: the tested GPU MLP did not beat the existing grouped logistic baseline, so the active local predictor remains unchanged.
