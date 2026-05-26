from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from feature_utils import (
    ATTACK_COLUMN,
    LABEL_COLUMN,
    feature_catalog,
    infer_feature_types,
    input_feature_columns,
    normalize_missing_values,
    resolve_unsw_files,
)


def _json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    return str(value)


def _value_counts(series: pd.Series) -> dict[str, int]:
    counts = series.value_counts(dropna=False).sort_index()
    return {str(key): int(value) for key, value in counts.items()}


def build_summary(train: pd.DataFrame, test: pd.DataFrame, feature_dict: pd.DataFrame | None) -> dict[str, Any]:
    train = normalize_missing_values(train)
    test = normalize_missing_values(test)

    feature_columns = input_feature_columns(train.columns)
    numerical_features, categorical_features = infer_feature_types(train, feature_columns)

    train_missing = train.isna().sum()
    test_missing = test.isna().sum()
    missing_rows = []
    for column in train.columns:
        train_count = int(train_missing.get(column, 0))
        test_count = int(test_missing.get(column, 0))
        if train_count or test_count:
            missing_rows.append(
                {"column": column, "train_missing": train_count, "test_missing": test_count}
            )

    summary: dict[str, Any] = {
        "dataset": "UNSW-NB15 official training/testing CSV",
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_columns": int(train.shape[1]),
        "test_columns": int(test.shape[1]),
        "columns": list(train.columns),
        "label_column": LABEL_COLUMN if LABEL_COLUMN in train.columns else None,
        "attack_category_column": ATTACK_COLUMN if ATTACK_COLUMN in train.columns else None,
        "input_feature_count": len(feature_columns),
        "numerical_features": numerical_features,
        "categorical_features": categorical_features,
        "missing_values": missing_rows,
        "feature_catalog": feature_catalog(train.columns),
        "feature_dictionary_columns": list(feature_dict.columns) if feature_dict is not None else [],
    }

    if LABEL_COLUMN in train.columns and LABEL_COLUMN in test.columns:
        summary["train_label_distribution"] = _value_counts(train[LABEL_COLUMN])
        summary["test_label_distribution"] = _value_counts(test[LABEL_COLUMN])

    if ATTACK_COLUMN in train.columns and ATTACK_COLUMN in test.columns:
        summary["train_attack_category_distribution"] = _value_counts(train[ATTACK_COLUMN])
        summary["test_attack_category_distribution"] = _value_counts(test[ATTACK_COLUMN])

    return summary


def write_markdown(summary: dict[str, Any], path: Path, command: str) -> None:
    lines: list[str] = [
        "# UNSW-NB15 Dataset Summary",
        "",
        "Generated from local CSV files. This report is a dataset inspection artifact, not a model result.",
        "",
        "## Command",
        "",
        "```powershell",
        command,
        "```",
        "",
        "## Split Size",
        "",
        "| Split | Rows | Columns |",
        "|---|---:|---:|",
        f"| Train | {summary['train_rows']} | {summary['train_columns']} |",
        f"| Test | {summary['test_rows']} | {summary['test_columns']} |",
        "",
        "## Label Columns",
        "",
        f"- Label column: `{summary['label_column']}`",
        f"- Attack category column: `{summary['attack_category_column']}`",
        "",
        "## Feature Types",
        "",
        f"- Input feature count after dropping `id`, `label`, and `attack_cat`: {summary['input_feature_count']}",
        f"- Numerical features ({len(summary['numerical_features'])}): "
        + ", ".join(f"`{name}`" for name in summary["numerical_features"]),
        f"- Categorical features ({len(summary['categorical_features'])}): "
        + ", ".join(f"`{name}`" for name in summary["categorical_features"]),
        "",
        "## Binary Label Distribution",
        "",
        "| Split | Label | Count |",
        "|---|---:|---:|",
    ]

    for split_key, split_name in [
        ("train_label_distribution", "Train"),
        ("test_label_distribution", "Test"),
    ]:
        for label, count in summary.get(split_key, {}).items():
            lines.append(f"| {split_name} | {label} | {count} |")

    lines.extend(["", "## Missing Values", ""])
    if summary["missing_values"]:
        lines.extend(["| Column | Train missing | Test missing |", "|---|---:|---:|"])
        for row in summary["missing_values"]:
            lines.append(f"| `{row['column']}` | {row['train_missing']} | {row['test_missing']} |")
    else:
        lines.append("No missing values were detected after normalizing common blank tokens.")

    lines.extend(
        [
            "",
            "## Packet-Path Feature Review",
            "",
            "| Feature | Category | Note |",
            "|---|---|---|",
        ]
    )
    for row in summary["feature_catalog"]:
        lines.append(f"| `{row['feature']}` | {row['packet_path_category']} | {row['note']} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "UNSW-NB15 is useful for Day 03 software baselines because it provides official CSV splits and labels. "
            "Most fields are flow-derived, so results from this dataset should be described as software/flow-feature "
            "baselines unless later packet-trace or parser-derived hybrid features are added.",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect UNSW-NB15 training/testing CSV files.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--out-dir", type=Path, default=Path("reports/day03_unsw"))
    args = parser.parse_args()

    paths, missing = resolve_unsw_files(args.data_dir)
    if missing:
        print("Missing UNSW-NB15 files:", file=sys.stderr)
        for path in missing:
            print(f"  - {path}", file=sys.stderr)
        print("Place the official CSV files in data/raw/ and rerun this script.", file=sys.stderr)
        return 2

    train = pd.read_csv(paths["train"])
    test = pd.read_csv(paths["test"])
    feature_dict = pd.read_csv(paths["features"], encoding_errors="ignore")

    for required in [LABEL_COLUMN, ATTACK_COLUMN]:
        if required not in train.columns or required not in test.columns:
            print(f"Required column `{required}` is missing from train or test CSV.", file=sys.stderr)
            return 3

    summary = build_summary(train, test, feature_dict)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    json_path = args.out_dir / "unsw_dataset_summary.json"
    md_path = args.out_dir / "unsw_dataset_summary.md"
    json_path.write_text(json.dumps(summary, indent=2, default=_json_default), encoding="utf-8")
    write_markdown(summary, md_path, "python python/load_unsw.py --data-dir data/raw --out-dir reports/day03_unsw")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
