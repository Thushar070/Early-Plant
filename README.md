# PlantSense AI

PlantSense AI is a research prototype exploring whether recorded plant-associated sounds can distinguish known recording conditions. It is not a validated plant-health or stress diagnosis system.

## Data and task

The repository contains two separate experiments:

| Dataset | Scope | Evaluation |
|---|---|---|
| Original local dataset | 1,000 two-second, 22.05 kHz recordings labelled across five categories: drought, heat stress, mechanical damage, nutrient deficiency, and pest infestation. Label provenance and plant/session IDs are unverified. | Existing train/validation partitions; not plant- or session-grouped. Used only for exploratory diagnostics. |
| [Dryad PlantSounds](https://datadryad.org/dataset/doi:10.5061/dryad.jwstqjqf7) | Source archive has 5,477 short WAV events at 500 kHz, including controls. The modeled task uses dry-versus-cut events separately for tomato (2,282 events; 107 plants) and tobacco (781 events; 63 plants). | Five-fold stratified cross-validation grouped by plant ID. Session IDs are unavailable. |

The PlantSounds classification target is **dry vs. cut within a species**. It does not represent healthy-vs-stressed classification. The two datasets and their scores are not directly comparable.

## Approaches tried

### Original five-class experiment

Validation results below are the best logged epoch for neural approaches, or the reported validation result for the classical baseline. All use the original non-grouped split; the labels and provenance are unverified.

| Approach | Validation accuracy | Validation macro-F1 |
|---|---:|---:|
| Log-spaced Welch spectral features: majority baseline | 20.7% | 6.9% |
| Log-spaced Welch features: linear SVM | 18.0% | 17.6% |
| Log-spaced Welch features: RBF SVM | 19.3% | 19.6% |
| Log-spaced Welch features: class-balanced ExtraTrees (best classical model) | 21.3% | 21.2% |
| Log-Mel CNN | 25.3% | 22.9% |
| AST embedding classifier | 26.0% | 21.4% |
| AST fine-tuning | 20.7% | 14.1% |
| PANNs embedding classifier | 23.3% | 23.1% |
| PANNs with augmentation | 22.7% | 22.4% |
| PANNs fine-tuning | 23.3% | 22.1% |

Five-class chance accuracy is 20%. The results are near chance and are not evidence of reliable stress classification.

### PlantSounds dry-vs-cut experiments

The starting baseline uses Welch spectral bands and waveform summaries with class-balanced logistic regression. Events are weighted by plant, and predictions are also aggregated to the plant level.

| Species | Events / plants | Baseline plant accuracy | Baseline plant macro-F1 | Event macro-F1 |
|---|---:|---:|---:|---:|
| Tomato | 2,282 / 107 | 76.6% | 76.1% | 63.3% |
| Tobacco | 781 / 63 | 71.4% | 71.4% | 60.4% |

Further model comparisons:

| Search | Approaches | Plant-level macro-F1 | Comparison |
|---|---|---:|---|
| CPU nested search (tomato) | Welch and richer spectral/envelope features; logistic regression, RBF SVM, ExtraTrees, Random Forest, and histogram gradient boosting | 74.2% | Below the matched logistic baseline (76.2%). |
| GPU nested search (tomato) | Six MLP configurations using Welch or richer features; RTX 3050 | 74.3% with mean-probability aggregation | Below logistic baseline (76.1%). Majority-vote aggregation scored 72.6%. |
| GPU nested search (tobacco) | Same MLP search and aggregation comparison; RTX 3050 | 64.0% with mean-probability aggregation | Below logistic baseline (71.4%). Majority-vote aggregation scored 62.1%. |

GPU tuning used five outer plant folds and three inner plant folds. The additional CPU search was run for tomato only. Neural models and pretrained AST/PANNs approaches were explored on the original five-class dataset; they do not have directly comparable plant-grouped PlantSounds scores.

## Interpretation

- The strongest PlantSounds results are exploratory cross-validation estimates on cohorts repeatedly used during model development, not independent confirmation.
- Plant grouping reduces leakage between recordings from the same plant, but the source has no session IDs and does not establish generalization to new sites, sensors, or acquisition sessions.
- The original five-class dataset has unverified labels and non-grouped partitions; its scores are near chance.
- Validate a frozen pipeline on newly collected plants and sessions before making broader performance claims. The current research target is not a general plant-stress diagnosis.

## Project notes

- [ML experiment details](ml/MODEL_EXPERIMENTS.md)
- [Research scope and limitations](ml/RESEARCH.md)
- [Dataset sources](ml/data_sources.json)
- [PlantSounds source metadata and manifest](datasets/public_plantsounds/)
