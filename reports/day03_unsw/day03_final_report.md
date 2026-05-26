# Day 03 UNSW-NB15 Final Report

## Scope

This report records the Day 03 software baseline for SafeHy-TinyNID. It is a software and dataset milestone, not an RTL or FPGA measurement milestone.

The results support reproducible baseline construction and feature understanding. They do not claim packet-path FPGA throughput, latency, timing closure, or safe online adaptation.

## Commands Run

```powershell
python python/load_unsw.py --data-dir data/raw --out-dir reports/day03_unsw
python python/preprocess_unsw.py --data-dir data/raw --out-dir data/processed/unsw_day03 --summary-dir reports/day03_unsw --feature-mode all_csv
python python/preprocess_unsw.py --data-dir data/raw --out-dir data/processed/unsw_day03 --summary-dir reports/day03_unsw --feature-mode packet_path_candidates
python python/train_baselines.py --processed-npz data/processed/unsw_day03/unsw_all_csv_preprocessed.npz --out-dir reports/day03_unsw --model-dir data/processed/unsw_day03/models --seed 42 --models all --mlp-hidden 32 --mlp-max-iter 100
python python/train_baselines.py --processed-npz data/processed/unsw_day03/unsw_packet_path_candidates_preprocessed.npz --out-dir reports/day03_unsw --model-dir data/processed/unsw_day03/models --seed 42 --models all --mlp-hidden 32 --mlp-max-iter 100
python python/quantize_sim.py --processed-npz data/processed/unsw_day03/unsw_all_csv_preprocessed.npz --out-dir data/processed/unsw_day03/quantized --report-dir reports/day03_unsw
python python/quantize_sim.py --processed-npz data/processed/unsw_day03/unsw_packet_path_candidates_preprocessed.npz --out-dir data/processed/unsw_day03/quantized --report-dir reports/day03_unsw
```

## Dataset Inspection

| Split | Rows | Columns |
|---|---:|---:|
| Train | 175341 | 45 |
| Test | 82332 | 45 |

| Split | Normal `label=0` | Attack `label=1` |
|---|---:|---:|
| Train | 56000 | 119341 |
| Test | 37000 | 45332 |

Missing values after the current normalization rule: none detected.

Columns excluded from model input:

| Column | Reason |
|---|---|
| `id` | Identifier/order field; not a deployable detection feature. |
| `label` | Binary target label. |
| `attack_cat` | Attack-category target; using it for binary detection would leak label information. |

Attack category distribution:

| Attack Category | Train Count | Test Count |
|---|---:|---:|
| Normal | 56000 | 37000 |
| Generic | 40000 | 18871 |
| Exploits | 33393 | 11132 |
| Fuzzers | 18184 | 6062 |
| DoS | 12264 | 4089 |
| Reconnaissance | 10491 | 3496 |
| Analysis | 2000 | 677 |
| Backdoor | 1746 | 583 |
| Shellcode | 1133 | 378 |
| Worms | 130 | 44 |

Feature category review:

| Category | Count | Meaning |
|---|---:|---|
| `packet_path_candidate` | 10 | Easier to approximate from parser/header/simple counters. |
| `flow_lite_candidate` | 8 | Needs small counters or timing windows. |
| `stateful_flow_feature` | 24 | Needs flow tables, bidirectional state, timing history, or application parsing. |
| `target_or_leakage` | 3 | Excluded from model input. |

## Feature Sets

| Feature Mode | Raw Selected Features | Numerical | Categorical | Transformed Dimension |
|---|---:|---:|---:|---:|
| `all_csv` | 42 | 39 | 3 | 194 |
| `packet_path_candidates` | 18 | 15 | 3 | 170 |

`all_csv` is the main software/flow-feature baseline. `packet_path_candidates` is an early hardware-oriented sanity check, not the final hybrid packet feature set.

## Model Configuration

| Model | Configuration |
|---|---|
| Logistic Regression | `max_iter=1000`, `class_weight=balanced`, `random_state=42` |
| Tiny MLP | `hidden_layer_sizes=(32,)`, `activation=relu`, `batch_size=256`, `learning_rate_init=0.001`, `early_stopping=True`, `max_iter=100`, `random_state=42` |

## Train/Test Metrics

| Feature Mode | Model | Split | Accuracy | Precision | Recall | F1 | AUC | FPR | FNR |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `all_csv` | Logistic Regression | Train | 0.932862 | 0.949745 | 0.951718 | 0.950730 | 0.984492 | 0.107321 | 0.048282 |
| `all_csv` | Logistic Regression | Test | 0.835520 | 0.802290 | 0.930601 | 0.861695 | 0.955956 | 0.280973 | 0.069399 |
| `all_csv` | Tiny MLP | Train | 0.945865 | 0.952519 | 0.968753 | 0.960568 | 0.989794 | 0.102911 | 0.031247 |
| `all_csv` | Tiny MLP | Test | 0.856957 | 0.806668 | 0.973529 | 0.882278 | 0.973794 | 0.285865 | 0.026471 |
| `packet_path_candidates` | Logistic Regression | Train | 0.922477 | 0.917316 | 0.973882 | 0.944753 | 0.973925 | 0.187071 | 0.026118 |
| `packet_path_candidates` | Logistic Regression | Test | 0.805798 | 0.753092 | 0.963028 | 0.845219 | 0.942420 | 0.386838 | 0.036972 |
| `packet_path_candidates` | Tiny MLP | Train | 0.934904 | 0.914711 | 0.997352 | 0.954246 | 0.982205 | 0.198179 | 0.002648 |
| `packet_path_candidates` | Tiny MLP | Test | 0.813402 | 0.748108 | 0.996691 | 0.854692 | 0.961851 | 0.411162 | 0.003309 |

## Quantization Summary

This is feature quantization only. Model weights and activation ranges are not yet quantized.

| Feature Mode | Feature Count | Train MAE | Train Max Error | Train MSE | Test MAE | Test Max Error | Test MSE |
|---|---:|---:|---:|---:|---:|---:|---:|
| `all_csv` | 194 | 0.01041760 | 0.76641846 | 0.00130501 | 0.01029579 | 42.79971313 | 0.00178100 |
| `packet_path_candidates` | 170 | 0.00448544 | 0.40859556 | 0.00054380 | 0.00437863 | 7.95662689 | 0.00052140 |

Quantization parameter artifacts:

| Feature Mode | Scale CSV | INT8 NPZ |
|---|---|---|
| `all_csv` | `data/processed/unsw_day03/quantized/unsw_all_csv_preprocessed_feature_int8_scales.csv` | `data/processed/unsw_day03/quantized/unsw_all_csv_preprocessed_feature_int8.npz` |
| `packet_path_candidates` | `data/processed/unsw_day03/quantized/unsw_packet_path_candidates_preprocessed_feature_int8_scales.csv` | `data/processed/unsw_day03/quantized/unsw_packet_path_candidates_preprocessed_feature_int8.npz` |

## Full Parameter And Prediction Artifacts

Full model parameters are saved separately rather than pasted into this report.

| Feature Mode | Model | Full Parameter JSON | Prediction CSVs |
|---|---|---|---|
| `all_csv` | Logistic Regression | `reports/day03_unsw/model_parameters/logistic_unsw_all_csv_preprocessed_seed42_parameters.json` | `reports/day03_unsw/predictions/logistic_unsw_all_csv_preprocessed_seed42_train_predictions.csv`, `reports/day03_unsw/predictions/logistic_unsw_all_csv_preprocessed_seed42_test_predictions.csv` |
| `all_csv` | Tiny MLP | `reports/day03_unsw/model_parameters/mlp_unsw_all_csv_preprocessed_seed42_parameters.json` | `reports/day03_unsw/predictions/mlp_unsw_all_csv_preprocessed_seed42_train_predictions.csv`, `reports/day03_unsw/predictions/mlp_unsw_all_csv_preprocessed_seed42_test_predictions.csv` |
| `packet_path_candidates` | Logistic Regression | `reports/day03_unsw/model_parameters/logistic_unsw_packet_path_candidates_preprocessed_seed42_parameters.json` | `reports/day03_unsw/predictions/logistic_unsw_packet_path_candidates_preprocessed_seed42_train_predictions.csv`, `reports/day03_unsw/predictions/logistic_unsw_packet_path_candidates_preprocessed_seed42_test_predictions.csv` |
| `packet_path_candidates` | Tiny MLP | `reports/day03_unsw/model_parameters/mlp_unsw_packet_path_candidates_preprocessed_seed42_parameters.json` | `reports/day03_unsw/predictions/mlp_unsw_packet_path_candidates_preprocessed_seed42_train_predictions.csv`, `reports/day03_unsw/predictions/mlp_unsw_packet_path_candidates_preprocessed_seed42_test_predictions.csv` |

Detailed per-run reports:

```text
reports/day03_unsw/baseline_metrics_unsw_all_csv_preprocessed_seed42.md
reports/day03_unsw/baseline_metrics_unsw_packet_path_candidates_preprocessed_seed42.md
reports/day03_unsw/baseline_manifest_unsw_all_csv_preprocessed_seed42.json
reports/day03_unsw/baseline_manifest_unsw_packet_path_candidates_preprocessed_seed42.json
```

## Objective Interpretation

The best Day 03 software baseline is Tiny MLP on `all_csv`, with test F1 = 0.882278 and AUC = 0.973794. This is expected because the full UNSW-NB15 CSV includes many flow-derived and stateful features.

The `packet_path_candidates` Tiny MLP keeps very high test recall = 0.996691, but its false positive rate is high at 0.411162. This means the candidate subset is aggressive at catching attacks but would flag too much normal traffic. For a paper-quality system, this requires threshold calibration, more carefully designed parser-derived hybrid features, and later adaptation experiments.

The gap between `all_csv` and `packet_path_candidates` is useful rather than disappointing: it quantifies the cost of moving away from flow-heavy software features toward a more hardware-friendly feature path. This directly supports the SafeHy-TinyNID research framing.

## Risks And Limits

1. UNSW-NB15 CSV results are software/flow-feature baselines.
2. The feature subset named `packet_path_candidates` is still derived from UNSW CSV fields, not from an RTL packet parser.
3. No FPGA timing, resource, latency, or throughput result was measured in Day 03.
4. The INT8 experiment quantizes input features only; model weight and activation quantization are still pending.
5. Safe online adaptation is not evaluated yet; current results are fixed-model baselines.

## Next Recommended Step

Day 04 should convert the fixed-model baseline into a more hardware-directed experiment:

1. Calibrate decision thresholds using validation-style analysis.
2. Add model weight/activation quantization for Logistic Regression and Tiny MLP.
3. Export model parameters in a hardware-friendly format.
4. Define the first true hybrid packet feature vector separately from UNSW flow fields.
5. Start adaptation simulation only after fixed and quantized baselines are stable.
