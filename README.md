# SafeHy-TinyNID

SafeHy-TinyNID is a research-code repository for a hybrid-feature TinyML accelerator with safe bounded online adaptation for packet-path intrusion detection on resource-constrained FPGAs.

The current milestone is Day 03: build the UNSW-NB15 software baseline before writing RTL.

## Day 03 Quick Start

Place the official UNSW-NB15 CSV files in `data/raw/`:

```text
UNSW_NB15_training-set.csv
UNSW_NB15_testing-set.csv
UNSW-NB15_features.csv
```

Then run:

```powershell
python python/load_unsw.py --data-dir data/raw --out-dir reports/day03_unsw
python python/preprocess_unsw.py --data-dir data/raw --out-dir data/processed/unsw_day03 --summary-dir reports/day03_unsw --feature-mode all_csv
python python/train_baselines.py --processed-npz data/processed/unsw_day03/unsw_all_csv_preprocessed.npz --out-dir reports/day03_unsw --seed 42 --models all
```

UNSW-NB15 CSV results are software/flow-feature baselines. Packet-path FPGA claims require later parser-derived features, trace replay, simulation, and hardware evidence.
