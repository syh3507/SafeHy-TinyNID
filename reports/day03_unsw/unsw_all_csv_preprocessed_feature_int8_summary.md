# Feature INT8 Quantization Summary

## Command

```powershell
python python/quantize_sim.py --processed-npz data/processed/unsw_day03/unsw_all_csv_preprocessed.npz --out-dir data/processed/unsw_day03/quantized --report-dir reports/day03_unsw
```

## Scope

This script quantizes preprocessed input features to signed INT8 with one scale per transformed feature. It does not yet quantize trained model weights or activations.

## Error

| Split | MAE | Max Abs Error | MSE |
|---|---:|---:|---:|
| Train | 0.01041760 | 0.76641846 | 0.00130501 |
| Test | 0.01029579 | 42.79971313 | 0.00178100 |

## Quantization Parameters

- Feature count: 194
- Scale CSV: `data\processed\unsw_day03\quantized\unsw_all_csv_preprocessed_feature_int8_scales.csv`
- Scale min: 0.0078740157
- Scale max: 1.7421563864
- Scale mean: 0.0626481995
- Scale std: 0.1940026283
