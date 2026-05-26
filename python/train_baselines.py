from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

from eval_metrics import binary_classification_metrics, write_metrics_csv, write_metrics_json


def json_default(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if hasattr(value, "item"):
        return value.item()
    return str(value)


def load_processed(path: Path):
    data = np.load(path)
    return data["X_train"], data["X_test"], data["y_train"], data["y_test"]


def metadata_path_for(processed_npz: Path) -> Path:
    name = processed_npz.name.replace("_preprocessed.npz", "_metadata.json")
    return processed_npz.with_name(name)


def load_metadata(processed_npz: Path) -> dict[str, Any]:
    path = metadata_path_for(processed_npz)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def positive_scores(model, x: np.ndarray) -> np.ndarray | None:
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(x)
        if proba.shape[1] >= 2:
            return proba[:, 1]
    if hasattr(model, "decision_function"):
        scores = model.decision_function(x)
        return np.asarray(scores)
    return None


def value_counts(values: np.ndarray) -> dict[str, int]:
    unique, counts = np.unique(values, return_counts=True)
    return {str(key): int(value) for key, value in zip(unique, counts)}


def score_summary(scores: np.ndarray | None) -> dict[str, float] | None:
    if scores is None:
        return None
    return {
        "min": float(np.min(scores)),
        "max": float(np.max(scores)),
        "mean": float(np.mean(scores)),
        "std": float(np.std(scores)),
        "p01": float(np.quantile(scores, 0.01)),
        "p05": float(np.quantile(scores, 0.05)),
        "p50": float(np.quantile(scores, 0.50)),
        "p95": float(np.quantile(scores, 0.95)),
        "p99": float(np.quantile(scores, 0.99)),
    }


def evaluate_split(model, x: np.ndarray, y: np.ndarray, split: str) -> dict[str, Any]:
    y_pred = model.predict(x)
    y_score = positive_scores(model, x)
    metrics = binary_classification_metrics(y, y_pred, y_score)
    return {
        "split": split,
        "metrics": metrics,
        "label_distribution": value_counts(y),
        "prediction_distribution": value_counts(y_pred),
        "score_summary": score_summary(y_score),
        "y_pred": y_pred,
        "y_score": y_score,
    }


def write_predictions(path: Path, y_true: np.ndarray, y_pred: np.ndarray, y_score: np.ndarray | None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["row_index", "y_true", "y_pred", "attack_score"])
        for idx, (truth, pred) in enumerate(zip(y_true, y_pred)):
            score = "" if y_score is None else float(y_score[idx])
            writer.writerow([idx, int(truth), int(pred), score])


def model_parameter_snapshot(model, transformed_features: list[str]) -> dict[str, Any]:
    if isinstance(model, LogisticRegression):
        coef = model.coef_
        intercept = model.intercept_
        return {
            "model_type": "LogisticRegression",
            "classes": model.classes_.tolist(),
            "n_iter": model.n_iter_.tolist(),
            "coefficient_shape": list(coef.shape),
            "intercept_shape": list(intercept.shape),
            "parameter_count": int(coef.size + intercept.size),
            "transformed_features": transformed_features,
            "coef": coef.tolist(),
            "intercept": intercept.tolist(),
        }

    if isinstance(model, MLPClassifier):
        parameter_count = sum(array.size for array in model.coefs_) + sum(
            array.size for array in model.intercepts_
        )
        return {
            "model_type": "MLPClassifier",
            "classes": model.classes_.tolist(),
            "n_iter": int(model.n_iter_),
            "n_layers": int(model.n_layers_),
            "n_outputs": int(model.n_outputs_),
            "out_activation": model.out_activation_,
            "loss": float(model.loss_),
            "best_loss": None if model.best_loss_ is None else float(model.best_loss_),
            "best_validation_score": getattr(model, "best_validation_score_", None),
            "coefficient_shapes": [list(array.shape) for array in model.coefs_],
            "intercept_shapes": [list(array.shape) for array in model.intercepts_],
            "parameter_count": int(parameter_count),
            "transformed_features": transformed_features,
            "coefs": [array.tolist() for array in model.coefs_],
            "intercepts": [array.tolist() for array in model.intercepts_],
        }

    return {"model_type": type(model).__name__}


def compact_model_summary(parameter_snapshot: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "model_type",
        "classes",
        "n_iter",
        "n_layers",
        "n_outputs",
        "out_activation",
        "loss",
        "best_loss",
        "best_validation_score",
        "coefficient_shape",
        "intercept_shape",
        "coefficient_shapes",
        "intercept_shapes",
        "parameter_count",
    ]
    return {key: parameter_snapshot[key] for key in keys if key in parameter_snapshot}


def metric_rows_for_csv(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for result in results:
        for split_key in ["train", "test"]:
            split_result = result[split_key]
            rows.append(
                {
                    "model": result["model"],
                    "dataset": "UNSW-NB15",
                    "split": split_key,
                    "feature_set": result["feature_set"],
                    "quantization": "FP32 software",
                    "random_seed": result["random_seed"],
                    **split_result["metrics"],
                }
            )
    return rows


def format_float(value: Any) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.6f}"


def make_model(name: str, args) -> Any:
    if name == "logistic":
        return LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=args.seed,
            n_jobs=None,
        )
    if name == "mlp":
        return MLPClassifier(
            hidden_layer_sizes=(args.mlp_hidden,),
            activation="relu",
            alpha=1e-4,
            batch_size=256,
            learning_rate_init=1e-3,
            max_iter=args.mlp_max_iter,
            early_stopping=True,
            random_state=args.seed,
        )
    raise ValueError(f"Unsupported model: {name}")


def write_markdown_report(
    path: Path,
    args,
    x_train: np.ndarray,
    x_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    metadata: dict[str, Any],
    results: list[dict[str, Any]],
    json_path: Path,
    csv_path: Path,
    manifest_path: Path,
) -> None:
    lines = [
        "# Day 03 Baseline Metrics",
        "",
        "## Command",
        "",
        "```powershell",
        (
            f"python python/train_baselines.py --processed-npz {args.processed_npz.as_posix()} "
            f"--out-dir {args.out_dir.as_posix()} --model-dir {args.model_dir.as_posix()} "
            f"--seed {args.seed} --models {args.models} --mlp-hidden {args.mlp_hidden} "
            f"--mlp-max-iter {args.mlp_max_iter}"
        ),
        "```",
        "",
        "## Dataset And Feature Shape",
        "",
        "| Item | Value |",
        "|---|---:|",
        f"| Train rows | {x_train.shape[0]} |",
        f"| Test rows | {x_test.shape[0]} |",
        f"| Transformed feature dimension | {x_train.shape[1]} |",
        f"| Raw selected features | {len(metadata.get('selected_raw_features', []))} |",
        "",
        "## Label Distribution",
        "",
        "| Split | Normal label 0 | Attack label 1 |",
        "|---|---:|---:|",
        f"| Train | {value_counts(y_train).get('0', 0)} | {value_counts(y_train).get('1', 0)} |",
        f"| Test | {value_counts(y_test).get('0', 0)} | {value_counts(y_test).get('1', 0)} |",
        "",
        "## Model Hyperparameters",
        "",
        "| Model | Hyperparameters |",
        "|---|---|",
    ]

    for result in results:
        lines.append(f"| {result['model']} | `{json.dumps(result['hyperparameters'], default=json_default)}` |")

    lines.extend(
        [
            "",
            "## Train/Test Metrics",
            "",
            "| Model | Split | Accuracy | Precision | Recall | F1 | AUC | FPR | FNR | TN | FP | FN | TP |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )

    for result in results:
        for split_key in ["train", "test"]:
            metrics = result[split_key]["metrics"]
            lines.append(
                f"| {result['model']} | {split_key} | {format_float(metrics['accuracy'])} | "
                f"{format_float(metrics['precision'])} | {format_float(metrics['recall'])} | "
                f"{format_float(metrics['f1'])} | {format_float(metrics['auc'])} | "
                f"{format_float(metrics['false_positive_rate'])} | "
                f"{format_float(metrics['false_negative_rate'])} | {metrics['true_negative']} | "
                f"{metrics['false_positive']} | {metrics['false_negative']} | {metrics['true_positive']} |"
            )

    lines.extend(
        [
            "",
            "## Score Distribution",
            "",
            "| Model | Split | Min | Mean | Std | P01 | P05 | P50 | P95 | P99 | Max |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for result in results:
        for split_key in ["train", "test"]:
            summary = result[split_key]["score_summary"]
            if summary is None:
                continue
            lines.append(
                f"| {result['model']} | {split_key} | {format_float(summary['min'])} | "
                f"{format_float(summary['mean'])} | {format_float(summary['std'])} | "
                f"{format_float(summary['p01'])} | {format_float(summary['p05'])} | "
                f"{format_float(summary['p50'])} | {format_float(summary['p95'])} | "
                f"{format_float(summary['p99'])} | {format_float(summary['max'])} |"
            )

    lines.extend(
        [
            "",
            "## Parameter Artifacts",
            "",
            "| Model | Saved model | Full parameter JSON | Train predictions | Test predictions |",
            "|---|---|---|---|---|",
        ]
    )
    for result in results:
        lines.append(
            f"| {result['model']} | `{result['model_path']}` | `{result['parameter_path']}` | "
            f"`{result['train_prediction_path']}` | `{result['test_prediction_path']}` |"
        )

    lines.extend(
        [
            "",
            "## Model Parameter Summary",
            "",
            "Full trained parameters are stored in the JSON artifacts above. This section records shapes and counts for quick review.",
            "",
            "| Model | Parameter count | Shape summary |",
            "|---|---:|---|",
        ]
    )
    for result in results:
        summary = result["parameter_summary"]
        shape_bits = []
        if "coefficient_shape" in summary:
            shape_bits.append(f"coef={summary['coefficient_shape']}")
        if "coefficient_shapes" in summary:
            shape_bits.append(f"coefs={summary['coefficient_shapes']}")
        if "intercept_shape" in summary:
            shape_bits.append(f"intercept={summary['intercept_shape']}")
        if "intercept_shapes" in summary:
            shape_bits.append(f"intercepts={summary['intercept_shapes']}")
        lines.append(
            f"| {result['model']} | {summary.get('parameter_count', 'NA')} | `{'; '.join(shape_bits)}` |"
        )

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            f"- Detailed JSON: `{json_path}`",
            f"- Metrics CSV: `{csv_path}`",
            f"- Manifest: `{manifest_path}`",
            f"- Markdown report: `{path}`",
            "",
            "## Paper-Aware Interpretation",
            "",
            "These are Day 03 software baselines on UNSW-NB15 CSV features. They support the software-baseline and model-selection part of SafeHy-TinyNID. They do not measure FPGA resource use, timing, latency, throughput, or real packet-path feature extraction. The main research novelty remains hybrid-feature packet-path TinyML plus safe bounded online adaptation; these results are the controlled starting point, not the final hardware claim.",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Train Day 03 UNSW-NB15 software baselines.")
    parser.add_argument(
        "--processed-npz",
        type=Path,
        default=Path("data/processed/unsw_day03/unsw_all_csv_preprocessed.npz"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("reports/day03_unsw"))
    parser.add_argument("--model-dir", type=Path, default=Path("data/processed/unsw_day03/models"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--models", choices=["all", "logistic", "mlp"], default="all")
    parser.add_argument("--mlp-hidden", type=int, default=32)
    parser.add_argument("--mlp-max-iter", type=int, default=100)
    args = parser.parse_args()

    if not args.processed_npz.exists():
        print(
            f"{args.processed_npz} does not exist. Run python/preprocess_unsw.py first.",
            file=sys.stderr,
        )
        return 2

    x_train, x_test, y_train, y_test = load_processed(args.processed_npz)
    metadata = load_metadata(args.processed_npz)
    transformed_features = metadata.get("transformed_features", [])

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.model_dir.mkdir(parents=True, exist_ok=True)
    prediction_dir = args.out_dir / "predictions"
    parameter_dir = args.out_dir / "model_parameters"
    prediction_dir.mkdir(parents=True, exist_ok=True)
    parameter_dir.mkdir(parents=True, exist_ok=True)

    requested = ["logistic", "mlp"] if args.models == "all" else [args.models]
    results: list[dict[str, Any]] = []

    for name in requested:
        model = make_model(name, args)
        started = time.perf_counter()
        model.fit(x_train, y_train)
        fit_seconds = time.perf_counter() - started

        train_eval = evaluate_split(model, x_train, y_train, "train")
        test_eval = evaluate_split(model, x_test, y_test, "test")

        model_path = args.model_dir / f"{name}_{args.processed_npz.stem}_seed{args.seed}.joblib"
        joblib.dump(model, model_path)

        parameter_snapshot = model_parameter_snapshot(model, transformed_features)
        parameter_path = parameter_dir / f"{name}_{args.processed_npz.stem}_seed{args.seed}_parameters.json"
        parameter_path.write_text(json.dumps(parameter_snapshot, indent=2, default=json_default), encoding="utf-8")

        train_prediction_path = prediction_dir / f"{name}_{args.processed_npz.stem}_seed{args.seed}_train_predictions.csv"
        test_prediction_path = prediction_dir / f"{name}_{args.processed_npz.stem}_seed{args.seed}_test_predictions.csv"
        write_predictions(train_prediction_path, y_train, train_eval["y_pred"], train_eval["y_score"])
        write_predictions(test_prediction_path, y_test, test_eval["y_pred"], test_eval["y_score"])

        result = {
            "model": name,
            "feature_set": args.processed_npz.stem,
            "random_seed": args.seed,
            "fit_seconds": fit_seconds,
            "hyperparameters": model.get_params(deep=False),
            "train": {key: value for key, value in train_eval.items() if key not in {"y_pred", "y_score"}},
            "test": {key: value for key, value in test_eval.items() if key not in {"y_pred", "y_score"}},
            "model_path": str(model_path),
            "parameter_path": str(parameter_path),
            "train_prediction_path": str(train_prediction_path),
            "test_prediction_path": str(test_prediction_path),
            "parameter_summary": compact_model_summary(parameter_snapshot),
        }
        results.append(result)

    json_path = args.out_dir / f"baseline_metrics_{args.processed_npz.stem}_seed{args.seed}.json"
    csv_path = args.out_dir / f"baseline_metrics_{args.processed_npz.stem}_seed{args.seed}.csv"
    md_path = args.out_dir / f"baseline_metrics_{args.processed_npz.stem}_seed{args.seed}.md"
    manifest_path = args.out_dir / f"baseline_manifest_{args.processed_npz.stem}_seed{args.seed}.json"

    metric_rows = metric_rows_for_csv(results)
    write_metrics_json(results, json_path)
    write_metrics_csv(metric_rows, csv_path)

    manifest = {
        "command": " ".join(
            [
                "python",
                "python/train_baselines.py",
                "--processed-npz",
                str(args.processed_npz),
                "--out-dir",
                str(args.out_dir),
                "--model-dir",
                str(args.model_dir),
                "--seed",
                str(args.seed),
                "--models",
                args.models,
                "--mlp-hidden",
                str(args.mlp_hidden),
                "--mlp-max-iter",
                str(args.mlp_max_iter),
            ]
        ),
        "dataset_split": "UNSW-NB15 official train/test",
        "feature_set": args.processed_npz.stem,
        "models": requested,
        "quantization_mode": "FP32 software",
        "random_seed": args.seed,
        "train_shape": list(x_train.shape),
        "test_shape": list(x_test.shape),
        "metadata": metadata,
        "outputs": {
            "detailed_json": str(json_path),
            "metrics_csv": str(csv_path),
            "markdown": str(md_path),
            "models_dir": str(args.model_dir),
            "prediction_dir": str(prediction_dir),
            "parameter_dir": str(parameter_dir),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, default=json_default), encoding="utf-8")

    write_markdown_report(
        md_path,
        args,
        x_train,
        x_test,
        y_train,
        y_test,
        metadata,
        results,
        json_path,
        csv_path,
        manifest_path,
    )

    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")
    print(f"Wrote {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
