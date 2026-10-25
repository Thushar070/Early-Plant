# PlantSounds model tuning experiments

## Scope and method

These are exploratory follow-up experiments on the supplied Dryad PlantSounds recordings. The task remains dry-versus-cut discrimination within each species. All splits group by README-derived plant ID. Each nested run uses five outer plant folds and three inner plant folds; event features and model selection are fit inside the training side of each fold.

The RTX experiment used PyTorch 2.6.0 with CUDA 12.4 on the NVIDIA GeForce RTX 3050 Laptop GPU (3.77 GB reported VRAM). It searched two feature sets and six MLP settings. The CPU search for tomato compared logistic regression, RBF SVM, ExtraTrees, and histogram gradient boosting on the original Welch and richer spectral/envelope features. Events were weighted inversely by their count per plant.

## Results

| Species | Existing weighted logistic baseline | Nested GPU MLP, mean probability | Difference | Paired 95% plant-bootstrap interval for difference |
|---|---:|---:|---:|---:|
| Tomato | 76.1% plant macro-F1 | 74.3% | -1.8 points | -9.9 to +6.2 points |
| Tobacco | 71.4% plant macro-F1 | 64.0% | -7.4 points | -21.0 to +5.8 points |

The GPU bootstrap intervals include zero and are wide. The point estimates are below the logistic baseline, so the GPU MLP is not used by the application. A first GPU run using majority-vote aggregation scored 72.6% for tomato and 62.1% for tobacco; mean event probabilities improved those values to 74.3% and 64.0%, but still did not beat logistic regression.

The nested CPU search on tomato scored 74.2% plant macro-F1 against 76.2% for its matched baseline. Its selected full-data configuration was logistic regression (C=10) with the original Welch features. RBF SVM won inner tuning in two of five outer folds, but did not produce an overall gain. This CPU search was not run for tobacco.

The paired comparison reproduces the saved baseline report’s plant aggregation and uses the same plant IDs and outer folds. Its bootstrap interval captures plant-sampling variation only. These results remain exploratory: the cohorts and folds have been examined during earlier model development and are not an independent confirmation set. Do not interpret the scores as plant-health detection or external generalization.

## Active model and artifacts

The local upload API continues to use the existing Welch-feature logistic checkpoints. Experimental MLP and alternative-feature artifacts are kept in separate timestamped directories and excluded from the API auto-loader. Earlier checkpoints, dataset files, and reports remain intact.

- Tomato GPU run: `models/plantsounds/tomato_dry_vs_cut_gpu_20261025_165430_utc/`
- Tobacco GPU run: `models/plantsounds/tobacco_dry_vs_cut_gpu_20261025_165610_utc/`
- Tomato CPU search: `models/plantsounds/tomato_dry_vs_cut_tuned_20261025_170604_utc/`
- Paired bootstrap reports are saved as `paired_comparison_to_logistic.json` in each GPU run folder.

To reproduce GPU tuning in the local isolated environment:

```bash
.venv-plantgpu/bin/python ml/src/train_plantsounds_gpu.py --species tomato
.venv-plantgpu/bin/python ml/src/train_plantsounds_gpu.py --species tobacco
```

The dependency pins are in `requirements-gpu.txt`. The virtual environment is local-only and ignored by Git; nothing was deployed.
