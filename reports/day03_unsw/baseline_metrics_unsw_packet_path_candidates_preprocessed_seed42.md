# Day 03 Baseline Metrics

## Command

```powershell
python python/train_baselines.py --processed-npz data/processed/unsw_day03/unsw_packet_path_candidates_preprocessed.npz --out-dir reports/day03_unsw --model-dir data/processed/unsw_day03/models --seed 42 --models all --mlp-hidden 32 --mlp-max-iter 100
```

## Dataset And Feature Shape

| Item | Value |
|---|---:|
| Train rows | 175341 |
| Test rows | 82332 |
| Transformed feature dimension | 170 |
| Raw selected features | 18 |

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
| logistic | train | 0.922477 | 0.917316 | 0.973882 | 0.944753 | 0.973925 | 0.187071 | 0.026118 | 45524 | 10476 | 3117 | 116224 |
| logistic | test | 0.805798 | 0.753092 | 0.963028 | 0.845219 | 0.942420 | 0.386838 | 0.036972 | 22687 | 14313 | 1676 | 43656 |
| mlp | train | 0.934904 | 0.914711 | 0.997352 | 0.954246 | 0.982205 | 0.198179 | 0.002648 | 44902 | 11098 | 316 | 119025 |
| mlp | test | 0.813402 | 0.748108 | 0.996691 | 0.854692 | 0.961851 | 0.411162 | 0.003309 | 21787 | 15213 | 150 | 45182 |

## Score Distribution

| Model | Split | Min | Mean | Std | P01 | P05 | P50 | P95 | P99 | Max |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| logistic | train | 0.000000 | 0.636169 | 0.406714 | 0.000000 | 0.000000 | 0.824132 | 0.999702 | 0.999747 | 1.000000 |
| logistic | test | 0.000000 | 0.595765 | 0.396622 | 0.000000 | 0.000000 | 0.647061 | 0.999701 | 0.999711 | 1.000000 |
| mlp | train | 0.000000 | 0.680467 | 0.414710 | 0.000000 | 0.000000 | 0.972995 | 0.999995 | 0.999997 | 1.000000 |
| mlp | test | 0.000000 | 0.648154 | 0.406177 | 0.000000 | 0.000000 | 0.763780 | 0.999960 | 0.999996 | 1.000000 |

## Parameter Artifacts

| Model | Saved model | Full parameter JSON | Train predictions | Test predictions |
|---|---|---|---|---|
| logistic | `data\processed\unsw_day03\models\logistic_unsw_packet_path_candidates_preprocessed_seed42.joblib` | `reports\day03_unsw\model_parameters\logistic_unsw_packet_path_candidates_preprocessed_seed42_parameters.json` | `reports\day03_unsw\predictions\logistic_unsw_packet_path_candidates_preprocessed_seed42_train_predictions.csv` | `reports\day03_unsw\predictions\logistic_unsw_packet_path_candidates_preprocessed_seed42_test_predictions.csv` |
| mlp | `data\processed\unsw_day03\models\mlp_unsw_packet_path_candidates_preprocessed_seed42.joblib` | `reports\day03_unsw\model_parameters\mlp_unsw_packet_path_candidates_preprocessed_seed42_parameters.json` | `reports\day03_unsw\predictions\mlp_unsw_packet_path_candidates_preprocessed_seed42_train_predictions.csv` | `reports\day03_unsw\predictions\mlp_unsw_packet_path_candidates_preprocessed_seed42_test_predictions.csv` |

## Model Parameter Summary

Full trained parameters are stored in the JSON artifacts above. This section records shapes and counts for quick review.

| Model | Parameter count | Shape summary |
|---|---:|---|
| logistic | 171 | `coef=[1, 170]; intercept=[1]` |
| mlp | 5505 | `coefs=[[170, 32], [32, 1]]; intercepts=[[32], [1]]` |

## Output Files

- Detailed JSON: `reports\day03_unsw\baseline_metrics_unsw_packet_path_candidates_preprocessed_seed42.json`
- Metrics CSV: `reports\day03_unsw\baseline_metrics_unsw_packet_path_candidates_preprocessed_seed42.csv`
- Manifest: `reports\day03_unsw\baseline_manifest_unsw_packet_path_candidates_preprocessed_seed42.json`
- Markdown report: `reports\day03_unsw\baseline_metrics_unsw_packet_path_candidates_preprocessed_seed42.md`

## Paper-Aware Interpretation

These are Day 03 software baselines on UNSW-NB15 CSV features. They support the software-baseline and model-selection part of SafeHy-TinyNID. They do not measure FPGA resource use, timing, latency, throughput, or real packet-path feature extraction. The main research novelty remains hybrid-feature packet-path TinyML plus safe bounded online adaptation; these results are the controlled starting point, not the final hardware claim.
