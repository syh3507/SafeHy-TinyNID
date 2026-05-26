# UNSW-NB15 Preprocessing Report (packet_path_candidates)

## Command

```powershell
python python/preprocess_unsw.py --data-dir data/raw --out-dir data/processed/unsw_day03 --summary-dir reports/day03_unsw --feature-mode packet_path_candidates
```

## Outputs

- Preprocessed arrays: `data\processed\unsw_day03\unsw_packet_path_candidates_preprocessed.npz`
- Preprocessor: `data\processed\unsw_day03\unsw_packet_path_candidates_preprocessor.joblib`
- Metadata: `data\processed\unsw_day03\unsw_packet_path_candidates_metadata.json`

## Feature Set

- Raw selected features: 18
- Numerical features: 15
- Categorical features: 3
- Transformed feature dimension after one-hot encoding: 170

## Research Note

The preprocessor is fitted on the official training split only. `id`, `label`, and `attack_cat` are excluded from model inputs to avoid target leakage. UNSW-NB15 remains a software/flow-feature baseline unless later experiments replace these CSV fields with parser-derived packet-path features.
