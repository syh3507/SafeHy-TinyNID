# Feature INT8 Quantization Summary

## Command

```powershell
python python/quantize_sim.py --processed-npz data/processed/unsw_day03/unsw_packet_path_candidates_preprocessed.npz --out-dir data/processed/unsw_day03/quantized --report-dir reports/day03_unsw
```

## Scope

This script quantizes preprocessed input features to signed INT8 with one scale per transformed feature. It does not yet quantize trained model weights or activations.

## Error

| Split | MAE | Max Abs Error | MSE |
|---|---:|---:|---:|
| Train | 0.00448544 | 0.40859556 | 0.00054380 |
| Test | 0.00437863 | 7.95662689 | 0.00052140 |

## Quantization Parameters

- Feature count: 170
- Scale CSV: `data\processed\unsw_day03\quantized\unsw_packet_path_candidates_preprocessed_feature_int8_scales.csv`
- Scale min: 0.0078740157
- Scale max: 0.8178278804
- Scale mean: 0.0349716917
- Scale std: 0.1279094964
