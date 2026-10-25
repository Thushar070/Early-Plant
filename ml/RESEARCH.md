# Research-informed prototype plan

## What this prototype can claim today

The original local dataset contains 1,000 two-second mono WAV files at 22,050 Hz with five labels. Its Nyquist limit is 11,025 Hz, so it cannot represent acoustic energy above that frequency. A CPU baseline using log-spaced Welch power bands scored 21.2% macro-F1 / 21.3% accuracy. Five-way chance accuracy is 20%. These labels have unverified provenance and no reliable plant/session IDs; treat the model and its test exploration as legacy diagnostic artifacts only. They are not used by the new upload path.

Prior exploratory analysis also inspected the existing test split. Those test figures are contaminated by model-selection exploration and must not be presented as held-out generalization results. The baseline runner intentionally reads only `train.csv` and `val.csv`.

The CSVs do not establish plant- or recording-session-independent splits. The current labels and recording provenance are not independently verified. The source paper below studied tomato and tobacco under particular controlled conditions; its reported performance does not transfer to these five labels or this dataset.

## Selected public source and task scope

The best accessible primary source found is Khait et al.'s Dryad PlantSounds dataset. Dryad describes 2 ms, 500 kHz WAV clips from tomato and tobacco, with folder-level conditions for dry plants, freshly cut plants, empty-pot controls, and greenhouse noise. Dryad's reuse guidance says datasets are CC0; cite the dataset regardless. See `data_sources.json` for screened alternatives.

The prototype's narrow training target is **dry versus cut within one species**, separately for tomato and tobacco. This is grounded in source conditions but is not a healthy-versus-stressed detector and does not establish general stress diagnosis. Controls are retained in the extracted archive and metadata template but excluded from this narrow task.

The user supplied the Dryad README, which documents filenames as `id_<plant_id>_sound_<sound_id>.wav`; controls use the ID as a recording-instance ID. The acquisition code preserves that README and fills plant/sound IDs directly from the filename. It does not invent session IDs, which the README does not provide. Training requires a nonblank plant ID and records its source; all events from a plant remain together within a fold.

The runtime could not download Dryad directly, but the user supplied the archive and README. Both are preserved under `datasets/public_plantsounds/`, separate from the existing files. The archive SHA-256 is `5134d53a9d5e8d225bfa1c31d13d0c7f9da09b4c9edb9749168aa9a2ef0a1b63`. The importer found 5,477 source WAVs and populated plant IDs from the README filename convention; control recording-instance IDs are kept separate. The README does not define session IDs.

## Current exploratory grouped results

The fixed baseline is log-spaced Welch power bands plus waveform summaries, standardized and classified with class-balanced logistic regression. Training weights each event inversely by the number of events for its plant. All events for a plant stay together in 5-fold stratified group cross-validation. The primary table metric is plant-level macro-F1 from majority voting over out-of-fold event predictions; per-plant bootstrap intervals quantify sampling variation only.

| Species | Events | Plants | Plant accuracy | Plant macro-F1 (95% bootstrap interval) | Majority baseline macro-F1 | Event macro-F1 |
|---|---:|---:|---:|---:|---:|---:|
| Tomato | 2,282 | 107 | 76.6% | 76.1% (67.2–84.2%) | 37.4% | 63.3% |
| Tobacco | 781 | 63 | 71.4% | 71.4% (60.2–80.9%) | 35.7% | 60.4% |

**These are exploratory development scores, not independent confirmation.** We compared event-weighting variants on the same plant cohorts and retained all run artifacts. The CV predictions and bootstrap intervals do not account for that model iteration or selection. The Dryad source has no separate session IDs, and plant-held-out CV does not establish generalization to new sensors, sites, or acquisition conditions. Freeze the pipeline and collect a new plant/site cohort for confirmatory evaluation before making generalization claims. These scores are not comparable to the old five-class metrics or the source paper's different tasks.

```bash
python ml/src/prepare_plantsounds.py
# Review the source-derived IDs in datasets/public_plantsounds/metadata.csv
python ml/src/train_plantsounds_baseline.py --species tomato
python ml/src/train_plantsounds_baseline.py --species tobacco
```

Evaluation uses fixed, seeded `StratifiedGroupKFold` folds grouped by plant ID, reports out-of-fold metrics, and writes a full-data model plus each fold model. The UI/API only load this new model family. Upload analysis accepts one or more mono, approximately 2 ms, 500 kHz WAV snippets from the same plant; it does not resample ordinary 22.05 kHz dashboard audio into ultrasound. Source plant IDs use their held-out fold model; unknown IDs use the full-data model and have no independent validation estimate.

## Recommendations for the next data/model iteration

1. **Establish provenance and ground truth.** Record species/cultivar, plant ID, treatment protocol, stress onset, sensor ID, location, recording session, environmental conditions, and independent physiological measurements. Use negative/control plants and sham-handled controls.
2. **Capture the intended band correctly.** Choose a calibrated microphone and analog front end for the target frequency range. Set sampling rate above twice the highest frequency of interest with anti-alias filtering and margin; retain raw recordings and calibration measurements. Current 22.05 kHz files cannot support claims about emissions above 11.025 kHz.
3. **Control nuisance variation.** Log distance, orientation, gain, temperature, humidity, background noise, chamber/greenhouse, and time. Record ambient/control channels and repeat across days, sensors, and sites. Avoid random clip splits when clips share a plant or session.
4. **Design a meaningful evaluation.** Split by plant and session, reserve a final site/time cohort, report class counts and confidence intervals, and compare against majority and simple signal baselines. Tune only on training/validation groups; open the untouched test set once after the protocol is frozen.
5. **Start with transparent baselines.** Compare spectral summaries, calibrated spectrogram CNNs, and pretrained audio representations only after checking the input bandwidth and provenance. Use nested/group-aware validation, class-wise precision/recall, macro-F1, calibration, and ablations. Require replicated improvement over controls before adding predictions to the user-facing prototype.
6. **Keep the product honest.** Until external validation exists, describe this as a research prototype. Show dataset coverage, acquisition metadata, model version, validation protocol, uncertainty, and known limitations. Do not present simulated dashboard values as live sensing or model output.

## Sources

- Khait et al. (2023), *Sounds emitted by plants under stress are airborne and informative*, Cell. [PubMed record](https://pubmed.ncbi.nlm.nih.gov/37001499/). The reported experimental setting and metrics are study-specific.
- Khait et al. (2023), Dryad data package. [Dataset and README](https://datadryad.org/dataset/doi:10.5061/dryad.jwstqjqf7). The paper's recordings and conditions should not be assumed to describe this repository's WAV files.
- Dryad, [reuse guidance](https://dev.datadryad.org/help/guides/reuse) and [REST API documentation](https://github.com/datadryad/dryad-app/blob/main/documentation/apis/README.md).
- Son et al. (2024), *Is plant acoustic communication fact or fiction?*, New Phytologist. [DOI](https://doi.org/10.1111/nph.19648). Useful for framing uncertainty around interpretation and communication claims.
- *Plant ultrasound detection: a cost-effective method for identifying plant ultrasonic emissions* (2024). [PubMed record](https://pubmed.ncbi.nlm.nih.gov/38345027/). Motivates careful, standardized detection and acquisition methods.
- *Plant Health Monitoring using Acoustics* (European Acoustics Association Forum, 2025). [Paper](https://dael.euracoustics.org/confs/fa2025/data/articles/000682.pdf), discusses acquisition standardization and unresolved measurement questions.
