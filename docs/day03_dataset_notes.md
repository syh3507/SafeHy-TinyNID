# Day 03 Dataset Notes

## Objective

Day 03 focuses on the UNSW-NB15 software baseline. The purpose is to understand the dataset, define safe preprocessing, separate numerical and categorical features, identify hardware-friendly candidates, and prepare Logistic Regression / Tiny MLP baselines.

No RTL is part of Day 03.

## Current Local Status

The UNSW-NB15 CSV files are present in `data/raw/`, and Day 03 has been executed.

Generated summary and final report:

```text
reports/day03_unsw/unsw_dataset_summary.md
reports/day03_unsw/day03_final_report.md
```

Dataset size:

| Split | Rows | Columns |
|---|---:|---:|
| Train | 175341 | 45 |
| Test | 82332 | 45 |

Best Day 03 software baseline:

| Feature Mode | Model | Test Accuracy | Test F1 | Test AUC |
|---|---|---:|---:|---:|
| `all_csv` | Tiny MLP | 0.856957 | 0.882278 | 0.973794 |

## Dataset Role

UNSW-NB15 is useful because it has official training/testing CSV files and labels. It is the right first dataset for building deterministic software baselines quickly.

Important limitation: the official CSV columns are mostly flow-derived features. They are not the same as packet-path features extracted directly from Ethernet/IP/TCP/UDP headers and limited payload bytes. Results on these CSV fields should be described as software/flow-feature baselines.

## Columns To Exclude From Model Input

| Column | Reason |
|---|---|
| `id` | Row identifier; may encode split/order artifacts. |
| `label` | Binary target label. |
| `attack_cat` | Attack category target; using it for binary detection would leak label information. |

## Feature Groups

| Group | Examples | Packet-Path Meaning |
|---|---|---|
| Direct packet/header candidates | `proto`, `sttl`, `service`, `state`, `sbytes`, `is_sm_ips_ports` | Some can be approximated by a parser or simple header checks, but `service` and `state` may already be decoded by software in UNSW. |
| Flow-lite candidates | `dur`, `spkts`, `dpkts`, `rate`, `sload`, `dload` | Need counters and timing windows; possible later but not stateless first-packet logic. |
| Stateful flow/application features | `ct_*`, `sinpkt`, `sjit`, `tcprtt`, `trans_depth`, `response_body_len` | Need flow tables, timing history, or application parsing; not first packet-path target. |
| Target/leakage fields | `id`, `label`, `attack_cat` | Excluded from training inputs. |

## Baselines

| Baseline | Day 03 Status | Purpose |
|---|---|---|
| Logistic Regression | Script prepared | Minimal reproducible software baseline and later hardware-friendly linear reference. |
| Tiny MLP FP32 | Script prepared | Main software candidate before INT8 simulation. |
| INT8 feature quantization | Script prepared | First fixed-point sanity check; model quantization comes after baseline training. |
| Packet-path candidate feature subset | Preprocessing mode prepared | Early check of how much accuracy may be lost when moving away from all flow features. |

## Experiment Log Template

Each generated report should include:

1. Command used.
2. Dataset split.
3. Feature set.
4. Model.
5. Quantization mode.
6. Metrics.
7. Random seed.
8. Output artifact path.
9. Short interpretation.

## Day 03 Completion Criteria

Day 03 is complete when the scripts can run on the official CSV files and produce:

- `reports/day03_unsw/unsw_dataset_summary.md`
- `data/processed/unsw_day03/unsw_all_csv_preprocessed.npz`
- `reports/day03_unsw/baseline_metrics_unsw_all_csv_preprocessed_seed42.md`
- A short interpretation that does not overclaim packet-path or FPGA performance.
