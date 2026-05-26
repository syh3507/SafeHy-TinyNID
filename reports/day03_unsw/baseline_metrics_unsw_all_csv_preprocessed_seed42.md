# Day 03 Baseline Metrics

## Command

```powershell
python python/train_baselines.py --processed-npz data/processed/unsw_day03/unsw_all_csv_preprocessed.npz --out-dir reports/day03_unsw --model-dir data/processed/unsw_day03/models --seed 42 --models all --mlp-hidden 32 --mlp-max-iter 100
```

## Dataset And Feature Shape

| Item | Value |
|---|---:|
| Train rows | 175341 |
| Test rows | 82332 |
| Transformed feature dimension | 194 |
| Raw selected features | 42 |

## Label Distribution

| Split | Normal label 0 | Attack label 1 |
|---|---:|---:|
| Train | 56000 | 119341 |
| Test | 37000 | 45332 |

## Model Hyperparameters

| Model | Hyperparameters |
|---|---|
| logistic | `{"C": 1.0, "class_weight": "balanced", "dual": false, "fit_intercept": true, "intercept_scaling": 1, "l1_ratio": null, "max_iter": 1000, "multi_class": "auto", "n_jobs": null, "penalty": "l2", "random_state": 42, "solver": "lbfgs", "tol": 0.0001, "verbose": 0, "warm_start": false}` |
| mlp | `{"activation": "relu", "alpha": 0.0001, "batch_size": 256, "beta_1": 0.9, "beta_2": 0.999, "early_stopping": true, "epsilon": 1e-08, "hidden_layer_sizes": [32], "learning_rate": "constant", "learning_rate_init": 0.001, "max_fun": 15000, "max_iter": 100, "momentum": 0.9, "n_iter_no_change": 10, "nesterovs_momentum": true, "power_t": 0.5, "random_state": 42, "shuffle": true, "solver": "adam", "tol": 0.0001, "validation_fraction": 0.1, "verbose": false, "warm_start": false}` |

## Train/Test Metrics

| Model | Split | Accuracy | Precision | Recall | F1 | AUC | FPR | FNR | TN | FP | FN | TP |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| logistic | train | 0.932862 | 0.949745 | 0.951718 | 0.950730 | 0.984492 | 0.107321 | 0.048282 | 49990 | 6010 | 5762 | 113579 |
| logistic | test | 0.835520 | 0.802290 | 0.930601 | 0.861695 | 0.955956 | 0.280973 | 0.069399 | 26604 | 10396 | 3146 | 42186 |
| mlp | train | 0.945865 | 0.952519 | 0.968753 | 0.960568 | 0.989794 | 0.102911 | 0.031247 | 50237 | 5763 | 3729 | 115612 |
| mlp | test | 0.856957 | 0.806668 | 0.973529 | 0.882278 | 0.973794 | 0.285865 | 0.026471 | 26423 | 10577 | 1200 | 44132 |

## Score Distribution

| Model | Split | Min | Mean | Std | P01 | P05 | P50 | P95 | P99 | Max |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| logistic | train | 0.000000 | 0.642983 | 0.416334 | 0.000000 | 0.000000 | 0.855907 | 0.999878 | 0.999954 | 1.000000 |
| logistic | test | 0.000000 | 0.594596 | 0.407896 | 0.000000 | 0.000000 | 0.698173 | 0.999871 | 0.999964 | 1.000000 |
| mlp | train | 0.000000 | 0.678052 | 0.425259 | 0.000000 | 0.000000 | 0.985328 | 0.999999 | 1.000000 | 1.000000 |
| mlp | test | 0.000000 | 0.642218 | 0.418937 | 0.000000 | 0.000000 | 0.886211 | 0.999997 | 1.000000 | 1.000000 |

## Parameter Artifacts

| Model | Saved model | Full parameter JSON | Train predictions | Test predictions |
|---|---|---|---|---|
| logistic | `data\processed\unsw_day03\models\logistic_unsw_all_csv_preprocessed_seed42.joblib` | `reports\day03_unsw\model_parameters\logistic_unsw_all_csv_preprocessed_seed42_parameters.json` | `reports\day03_unsw\predictions\logistic_unsw_all_csv_preprocessed_seed42_train_predictions.csv` | `reports\day03_unsw\predictions\logistic_unsw_all_csv_preprocessed_seed42_test_predictions.csv` |
| mlp | `data\processed\unsw_day03\models\mlp_unsw_all_csv_preprocessed_seed42.joblib` | `reports\day03_unsw\model_parameters\mlp_unsw_all_csv_preprocessed_seed42_parameters.json` | `reports\day03_unsw\predictions\mlp_unsw_all_csv_preprocessed_seed42_train_predictions.csv` | `reports\day03_unsw\predictions\mlp_unsw_all_csv_preprocessed_seed42_test_predictions.csv` |

## Model Parameter Summary

Full trained parameters are stored in the JSON artifacts above. This section records shapes and counts for quick review.

| Model | Parameter count | Shape summary |
|---|---:|---|
| logistic | 195 | `coef=[1, 194]; intercept=[1]` |
| mlp | 6273 | `coefs=[[194, 32], [32, 1]]; intercepts=[[32], [1]]` |

## Output Files

- Detailed JSON: `reports\day03_unsw\baseline_metrics_unsw_all_csv_preprocessed_seed42.json`
- Metrics CSV: `reports\day03_unsw\baseline_metrics_unsw_all_csv_preprocessed_seed42.csv`
- Manifest: `reports\day03_unsw\baseline_manifest_unsw_all_csv_preprocessed_seed42.json`
- Markdown report: `reports\day03_unsw\baseline_metrics_unsw_all_csv_preprocessed_seed42.md`

## Paper-Aware Interpretation

These are Day 03 software baselines on UNSW-NB15 CSV features. They support the software-baseline and model-selection part of SafeHy-TinyNID. They do not measure FPGA resource use, timing, latency, throughput, or real packet-path feature extraction. The main research novelty remains hybrid-feature packet-path TinyML plus safe bounded online adaptation; these results are the controlled starting point, not the final hardware claim.
