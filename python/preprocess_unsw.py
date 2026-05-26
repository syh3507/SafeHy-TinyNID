from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from feature_utils import (
    ATTACK_COLUMN,
    FEATURE_MODE_DESCRIPTIONS,
    LABEL_COLUMN,
    feature_catalog,
    feature_mode_columns,
    infer_feature_types,
    normalize_missing_values,
    resolve_unsw_files,
)


def _make_one_hot_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def _json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    return str(value)


def choose_columns(df: pd.DataFrame, feature_mode: str) -> list[str]:
    return feature_mode_columns(df.columns, feature_mode)


def get_feature_names(transformer: ColumnTransformer, numerical: list[str], categorical: list[str]) -> list[str]:
    try:
        return list(transformer.get_feature_names_out())
    except Exception:
        names = [f"num__{name}" for name in numerical]
        cat_transformer = transformer.named_transformers_.get("cat")
        if categorical and cat_transformer is not None:
            encoder = cat_transformer.named_steps.get("onehot")
            if hasattr(encoder, "get_feature_names_out"):
                names.extend(list(encoder.get_feature_names_out(categorical)))
            else:
                names.extend([f"cat__{name}" for name in categorical])
        return names


def main() -> int:
    parser = argparse.ArgumentParser(description="Preprocess UNSW-NB15 CSV files for software baselines.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--out-dir", type=Path, default=Path("data/processed/unsw_day03"))
    parser.add_argument("--summary-dir", type=Path, default=Path("reports/day03_unsw"))
    parser.add_argument("--feature-mode", choices=list(FEATURE_MODE_DESCRIPTIONS), default="all_csv")
    args = parser.parse_args()

    paths, missing = resolve_unsw_files(args.data_dir)
    if missing:
        print("Missing UNSW-NB15 files:", file=sys.stderr)
        for path in missing:
            print(f"  - {path}", file=sys.stderr)
        return 2

    train = normalize_missing_values(pd.read_csv(paths["train"]))
    test = normalize_missing_values(pd.read_csv(paths["test"]))

    if LABEL_COLUMN not in train.columns or LABEL_COLUMN not in test.columns:
        print("Cannot preprocess: `label` column is missing.", file=sys.stderr)
        return 3

    selected_columns = choose_columns(train, args.feature_mode)
    numerical_features, categorical_features = infer_feature_types(train, selected_columns)

    for column in numerical_features:
        train[column] = pd.to_numeric(train[column], errors="coerce")
        test[column] = pd.to_numeric(test[column], errors="coerce")

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", _make_one_hot_encoder()),
        ]
    )

    transformers = []
    if numerical_features:
        transformers.append(("num", numeric_pipeline, numerical_features))
    if categorical_features:
        transformers.append(("cat", categorical_pipeline, categorical_features))

    preprocessor = ColumnTransformer(transformers=transformers, remainder="drop")
    x_train = preprocessor.fit_transform(train[selected_columns]).astype(np.float32)
    x_test = preprocessor.transform(test[selected_columns]).astype(np.float32)
    y_train = train[LABEL_COLUMN].astype(int).to_numpy()
    y_test = test[LABEL_COLUMN].astype(int).to_numpy()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.summary_dir.mkdir(parents=True, exist_ok=True)

    npz_path = args.out_dir / f"unsw_{args.feature_mode}_preprocessed.npz"
    np.savez_compressed(npz_path, X_train=x_train, X_test=x_test, y_train=y_train, y_test=y_test)

    preprocessor_path = args.out_dir / f"unsw_{args.feature_mode}_preprocessor.joblib"
    joblib.dump(preprocessor, preprocessor_path)

    transformed_features = get_feature_names(preprocessor, numerical_features, categorical_features)
    metadata = {
        "dataset": "UNSW-NB15",
        "feature_mode": args.feature_mode,
        "feature_mode_description": FEATURE_MODE_DESCRIPTIONS[args.feature_mode],
        "selected_raw_features": selected_columns,
        "numerical_features": numerical_features,
        "categorical_features": categorical_features,
        "transformed_features": transformed_features,
        "transformed_feature_count": int(x_train.shape[1]),
        "train_rows": int(x_train.shape[0]),
        "test_rows": int(x_test.shape[0]),
        "label_column": LABEL_COLUMN,
        "attack_category_column_excluded": ATTACK_COLUMN,
        "feature_catalog": feature_catalog(train.columns),
        "artifacts": {
            "preprocessed_npz": str(npz_path),
            "preprocessor": str(preprocessor_path),
        },
    }

    metadata_path = args.out_dir / f"unsw_{args.feature_mode}_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, default=_json_default), encoding="utf-8")

    report_path = args.summary_dir / f"unsw_{args.feature_mode}_preprocess.md"
    report_lines = [
        f"# UNSW-NB15 Preprocessing Report ({args.feature_mode})",
        "",
        "## Command",
        "",
        "```powershell",
        (
            "python python/preprocess_unsw.py --data-dir data/raw "
            f"--out-dir {args.out_dir.as_posix()} --summary-dir {args.summary_dir.as_posix()} "
            f"--feature-mode {args.feature_mode}"
        ),
        "```",
        "",
        "## Outputs",
        "",
        f"- Preprocessed arrays: `{npz_path}`",
        f"- Preprocessor: `{preprocessor_path}`",
        f"- Metadata: `{metadata_path}`",
        "",
        "## Feature Set",
        "",
        f"- Feature mode description: {FEATURE_MODE_DESCRIPTIONS[args.feature_mode]}",
        f"- Raw selected features: {len(selected_columns)}",
        f"- Numerical features: {len(numerical_features)}",
        f"- Categorical features: {len(categorical_features)}",
        f"- Transformed feature dimension after one-hot encoding: {x_train.shape[1]}",
        "",
        "## Research Note",
        "",
        "The preprocessor is fitted on the official training split only. `id`, `label`, and `attack_cat` are excluded "
        "from model inputs to avoid target leakage. UNSW-NB15 remains a software/flow-feature baseline unless "
        "later experiments replace these CSV fields with parser-derived packet-path features.",
        "",
        "## Hardware Caution",
        "",
        "`service` and `state` are UNSW decoded CSV fields. They are useful for software analysis but should not be "
        "overclaimed as directly parser-derived packet features until a real parser-derived feature path exists.",
    ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"Wrote {npz_path}")
    print(f"Wrote {metadata_path}")
    print(f"Wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
