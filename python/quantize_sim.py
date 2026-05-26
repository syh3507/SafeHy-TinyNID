from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np


def symmetric_int8_quantize(train: np.ndarray, test: np.ndarray):
    max_abs = np.maximum(np.max(np.abs(train), axis=0), 1e-8)
    scale = max_abs / 127.0
    train_q = np.clip(np.round(train / scale), -127, 127).astype(np.int8)
    test_q = np.clip(np.round(test / scale), -127, 127).astype(np.int8)
    train_deq = train_q.astype(np.float32) * scale
    test_deq = test_q.astype(np.float32) * scale
    return train_q, test_q, train_deq, test_deq, scale.astype(np.float32)


def quant_error(original: np.ndarray, dequantized: np.ndarray) -> dict[str, float]:
    error = original - dequantized
    return {
        "mean_absolute_error": float(np.mean(np.abs(error))),
        "max_absolute_error": float(np.max(np.abs(error))),
        "mean_squared_error": float(np.mean(error**2)),
    }


def metadata_path_for(processed_npz: Path) -> Path:
    return processed_npz.with_name(processed_npz.name.replace("_preprocessed.npz", "_metadata.json"))


def load_feature_names(processed_npz: Path, feature_count: int) -> list[str]:
    path = metadata_path_for(processed_npz)
    if path.exists():
        metadata = json.loads(path.read_text(encoding="utf-8"))
        names = metadata.get("transformed_features", [])
        if len(names) == feature_count:
            return names
    return [f"feature_{idx}" for idx in range(feature_count)]


def write_scales(path: Path, feature_names: list[str], scales: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["feature_index", "feature_name", "scale"])
        for idx, (name, scale) in enumerate(zip(feature_names, scales)):
            writer.writerow([idx, name, float(scale)])


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a simple INT8 feature quantization simulation.")
    parser.add_argument(
        "--processed-npz",
        type=Path,
        default=Path("data/processed/unsw_day03/unsw_all_csv_preprocessed.npz"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("data/processed/unsw_day03/quantized"))
    parser.add_argument("--report-dir", type=Path, default=Path("reports/day03_unsw"))
    args = parser.parse_args()

    if not args.processed_npz.exists():
        print(
            f"{args.processed_npz} does not exist. Run python/preprocess_unsw.py first.",
            file=sys.stderr,
        )
        return 2

    data = np.load(args.processed_npz)
    x_train = data["X_train"].astype(np.float32)
    x_test = data["X_test"].astype(np.float32)
    y_train = data["y_train"]
    y_test = data["y_test"]

    train_q, test_q, train_deq, test_deq, scale = symmetric_int8_quantize(x_train, x_test)
    feature_names = load_feature_names(args.processed_npz, x_train.shape[1])

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)

    out_path = args.out_dir / f"{args.processed_npz.stem}_feature_int8.npz"
    np.savez_compressed(
        out_path,
        X_train_int8=train_q,
        X_test_int8=test_q,
        X_train_dequant=train_deq,
        X_test_dequant=test_deq,
        y_train=y_train,
        y_test=y_test,
        scale=scale,
    )

    scale_path = args.out_dir / f"{args.processed_npz.stem}_feature_int8_scales.csv"
    write_scales(scale_path, feature_names, scale)

    summary = {
        "input": str(args.processed_npz),
        "output": str(out_path),
        "scale_csv": str(scale_path),
        "feature_count": int(x_train.shape[1]),
        "quantization": "symmetric per-feature signed INT8 for preprocessed features",
        "train_error": quant_error(x_train, train_deq),
        "test_error": quant_error(x_test, test_deq),
        "scale_summary": {
            "min": float(np.min(scale)),
            "max": float(np.max(scale)),
            "mean": float(np.mean(scale)),
            "std": float(np.std(scale)),
        },
        "note": "This is feature quantization only. Model weight/activation quantization comes after baseline training.",
    }

    json_path = args.report_dir / f"{args.processed_npz.stem}_feature_int8_summary.json"
    md_path = args.report_dir / f"{args.processed_npz.stem}_feature_int8_summary.md"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# Feature INT8 Quantization Summary",
        "",
        "## Command",
        "",
        "```powershell",
        (
            f"python python/quantize_sim.py --processed-npz {args.processed_npz.as_posix()} "
            f"--out-dir {args.out_dir.as_posix()} --report-dir {args.report_dir.as_posix()}"
        ),
        "```",
        "",
        "## Scope",
        "",
        "This script quantizes preprocessed input features to signed INT8 with one scale per transformed feature. "
        "It does not yet quantize trained model weights or activations.",
        "",
        "## Error",
        "",
        "| Split | MAE | Max Abs Error | MSE |",
        "|---|---:|---:|---:|",
        (
            f"| Train | {summary['train_error']['mean_absolute_error']:.8f} | "
            f"{summary['train_error']['max_absolute_error']:.8f} | "
            f"{summary['train_error']['mean_squared_error']:.8f} |"
        ),
        (
            f"| Test | {summary['test_error']['mean_absolute_error']:.8f} | "
            f"{summary['test_error']['max_absolute_error']:.8f} | "
            f"{summary['test_error']['mean_squared_error']:.8f} |"
        ),
        "",
        "## Quantization Parameters",
        "",
        f"- Feature count: {summary['feature_count']}",
        f"- Scale CSV: `{scale_path}`",
        f"- Scale min: {summary['scale_summary']['min']:.10f}",
        f"- Scale max: {summary['scale_summary']['max']:.10f}",
        f"- Scale mean: {summary['scale_summary']['mean']:.10f}",
        f"- Scale std: {summary['scale_summary']['std']:.10f}",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {out_path}")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
