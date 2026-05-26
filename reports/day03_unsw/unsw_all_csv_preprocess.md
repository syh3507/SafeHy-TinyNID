# UNSW-NB15 Preprocessing Report (all_csv)

## Command

```powershell
python python/preprocess_unsw.py --data-dir data/raw --out-dir data/processed/unsw_day03 --summary-dir reports/day03_unsw --feature-mode all_csv
```

## Outputs

- Preprocessed arrays: `data\processed\unsw_day03\unsw_all_csv_preprocessed.npz`
- Preprocessor: `data\processed\unsw_day03\unsw_all_csv_preprocessor.joblib`
- Metadata: `data\processed\unsw_day03\unsw_all_csv_metadata.json`

## Feature Set

- Raw selected features: 42
- Numerical features: 39
- Categorical features: 3
- Transformed feature dimension after one-hot encoding: 194

## Research Note

The preprocessor is fitted on the official training split only. `id`, `label`, and `attack_cat` are excluded from model inputs to avoid target leakage. UNSW-NB15 remains a software/flow-feature baseline unless later experiments replace these CSV fields with parser-derived packet-path features.
