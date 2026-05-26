# Day 03 Python Baseline Scaffold

This directory contains the first reproducible software path for SafeHy-TinyNID. It is intentionally dataset-first: inspect UNSW-NB15, document leakage and hardware-friendliness, then train small software baselines.

## Expected Data

Place the official UNSW-NB15 CSV files in `data/raw/`:

```text
data/raw/UNSW_NB15_training-set.csv
data/raw/UNSW_NB15_testing-set.csv
data/raw/UNSW-NB15_features.csv
```

Do not commit the raw dataset unless the license and repository policy allow it.

## Commands

```powershell
python python/load_unsw.py --data-dir data/raw --out-dir reports/day03_unsw
python python/preprocess_unsw.py --data-dir data/raw --out-dir data/processed/unsw_day03 --summary-dir reports/day03_unsw --feature-mode all_csv
python python/train_baselines.py --processed-npz data/processed/unsw_day03/unsw_all_csv_preprocessed.npz --out-dir reports/day03_unsw --seed 42 --models all
python python/quantize_sim.py --processed-npz data/processed/unsw_day03/unsw_all_csv_preprocessed.npz --out-dir data/processed/unsw_day03/quantized --report-dir reports/day03_unsw
```

For a smaller hardware-oriented feature sanity check:

```powershell
python python/preprocess_unsw.py --data-dir data/raw --out-dir data/processed/unsw_day03 --summary-dir reports/day03_unsw --feature-mode packet_path_candidates
```

## Research Interpretation

UNSW-NB15 is the Day 03 software baseline dataset. Most official CSV features are flow-derived, so metrics from `all_csv` should be described as software/flow-feature baselines. They should not be used to claim packet-path TinyML hardware performance. Packet-path claims require parser-derived header/payload/statistical features and later FPGA or RTL/HLS evidence.
