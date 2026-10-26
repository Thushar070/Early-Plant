# PlantSense AI

PlantSense AI is an ongoing student research project exploring whether machine learning can identify plant-stress conditions from recorded sounds. Current work compares the initial five-class dataset with a narrower benchmark built from published plant-acoustic recordings. The project is still exploratory; it is not a validated plant-health diagnosis system.

## Datasets under study

The project started with the [Mendeley Data dataset *Audio signals from stressed plants*](https://data.mendeley.com/datasets/rjmc7rrvdx/1) (DOI: [10.17632/rjmc7rrvdx.1](https://doi.org/10.17632/rjmc7rrvdx.1), published 22 October 2024, CC BY 4.0). Its description covers plant audio recordings and accompanying stress and environmental metadata. The local project copy contains 1,000 two-second, 22.05 kHz WAV recordings across five labels: drought, heat stress, mechanical damage, nutrient deficiency, and pest infestation.

A second, complementary dataset is [Dryad PlantSounds](https://datadryad.org/dataset/doi:10.5061/dryad.jwstqjqf7):

| Dataset | Scope | Evaluation |
|---|---|---|
| Mendeley: five stress labels | Initial project dataset; five-category classification. | Existing train/validation partitions; not plant- or session-grouped. Results are exploratory. |
| Dryad PlantSounds | Source archive has 5,477 short WAV events at 500 kHz, including controls. The current modeled task uses dry-versus-cut events separately for tomato (2,282 events; 107 plants) and tobacco (781 events; 63 plants). | Five-fold stratified cross-validation grouped by plant ID. Session IDs are unavailable. |

The PlantSounds classification target is **dry vs. cut within a species**. It complements the original Mendeley five-class task but does not represent healthy-vs-stressed classification. Results across the two datasets are not directly comparable.

## Experiments so far

### Original five-class experiment

Validation results below are the best logged epoch for neural approaches, or the reported validation result for the classical baseline. All use the same existing split, which does not keep plants or recording sessions separate between partitions.

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

## Current findings and next steps

- On the initial Mendeley dataset, the five-class models are near the 20% chance-accuracy level. The next step is to improve the signal and evaluation pipeline, not to claim reliable classification.
- On PlantSounds, grouped evaluation provides a better test of performance on unseen plants. The GPU and expanded CPU searches have not improved on the spectral logistic-regression baseline so far.
- These results are still exploratory: plant cohorts have been revisited during model development, and PlantSounds does not provide session IDs. Further work should test a frozen approach on newly recorded plants and sessions.
- The long-term goal remains studying plant-stress acoustics; the current PlantSounds model only separates dry and cut conditions within each species.

## Project notes

- [ML experiment details](ml/MODEL_EXPERIMENTS.md)
- [Research scope and limitations](ml/RESEARCH.md)
- [Dataset sources](ml/data_sources.json)
- [PlantSounds source metadata and manifest](datasets/public_plantsounds/)
