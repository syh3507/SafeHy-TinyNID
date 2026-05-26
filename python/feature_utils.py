from __future__ import annotations

from pathlib import Path
from typing import Iterable

LABEL_COLUMN = "label"
ATTACK_COLUMN = "attack_cat"
ID_COLUMN = "id"

REQUIRED_UNSW_FILES = {
    "train": "UNSW_NB15_training-set.csv",
    "test": "UNSW_NB15_testing-set.csv",
    "features": "UNSW-NB15_features.csv",
}

FEATURE_FILE_CANDIDATES = [
    "UNSW-NB15_features.csv",
    "NUSW-NB15_features.csv",
]

TARGET_OR_LEAKAGE_COLUMNS = {ID_COLUMN, LABEL_COLUMN, ATTACK_COLUMN}

KNOWN_CATEGORICAL_COLUMNS = {"proto", "service", "state", ATTACK_COLUMN}

DIRECT_PACKET_CANDIDATES = {
    "proto": "IP protocol field or parser-derived protocol code.",
    "service": "Can be approximated from L4 ports, but UNSW service is already decoded.",
    "state": "TCP state summary; packet-path use needs a small TCP/state parser.",
    "sttl": "Source-side TTL-like header field.",
    "dttl": "Destination-side TTL-like field; needs reverse direction context.",
    "sbytes": "Source bytes; single-packet hardware analogue is packet length.",
    "dbytes": "Destination bytes; needs reverse direction or flow-lite context.",
    "smean": "Mean source packet size; flow-lite counter/statistic.",
    "dmean": "Mean destination packet size; flow-lite counter/statistic.",
    "is_sm_ips_ports": "Simple comparison over source/destination IP and port fields.",
}

PACKET_HEADER_ONLY_FEATURES = {
    "proto": "IP protocol field or parser-derived protocol code.",
    "service": "UNSW decoded service field; useful for software analysis, but not fully parser-derived.",
    "state": "UNSW decoded TCP state field; useful for software analysis, but not fully parser-derived.",
    "sttl": "Source-side TTL-like header field.",
    "dttl": "Destination-side TTL-like field; needs reverse direction context.",
    "sbytes": "Source bytes; single-packet hardware analogue is packet length.",
    "dbytes": "Destination bytes; needs reverse direction or flow-lite context.",
    "is_sm_ips_ports": "Simple comparison over source/destination IP and port fields.",
}

FLOW_LITE_CANDIDATES = {
    "dur": "Duration requires timing state, but can be approximated in a small flow-lite window.",
    "spkts": "Source packet count needs a counter.",
    "dpkts": "Destination packet count needs a counter.",
    "rate": "Packet rate needs timing and count state.",
    "sload": "Source load needs byte and time state.",
    "dload": "Destination load needs byte and time state.",
    "sloss": "Source loss estimate is not directly available from a stateless packet parser.",
    "dloss": "Destination loss estimate is not directly available from a stateless packet parser.",
}

FEATURE_MODE_DESCRIPTIONS = {
    "all_csv": "All non-label UNSW CSV fields; software/flow-feature baseline and upper-bound input.",
    "packet_path_candidates": "Current broad hardware-oriented candidate set; still UNSW CSV-derived, not parser-derived.",
    "packet_header_only": "Closer to single-packet parser fields, but service/state are UNSW decoded fields.",
    "flow_lite_only": "Small timing/counter/load features that require light state.",
    "hybrid_v0": "packet_header_only + flow_lite_only; initial CSV-derived hybrid planning mode.",
}

STATEFUL_FLOW_FEATURES = {
    "sinpkt": "Inter-packet timing needs flow history.",
    "dinpkt": "Reverse inter-packet timing needs flow history.",
    "sjit": "Jitter needs timestamp history.",
    "djit": "Reverse jitter needs timestamp history.",
    "swin": "TCP window can be parsed, but this aggregate form is flow-derived.",
    "dwin": "Reverse TCP window aggregate needs bidirectional flow state.",
    "stcpb": "TCP base sequence value is parser-visible but dataset form is flow-derived.",
    "dtcpb": "Reverse TCP base sequence value needs bidirectional context.",
    "tcprtt": "TCP RTT requires SYN/SYN-ACK/ACK timing state.",
    "synack": "SYN-ACK timing requires handshake tracking.",
    "ackdat": "ACK-data timing requires handshake tracking.",
    "trans_depth": "HTTP transaction depth is application/stateful parsing.",
    "response_body_len": "HTTP response body length is application/stateful parsing.",
    "ct_srv_src": "Connection-count feature needs a table/window.",
    "ct_state_ttl": "Connection-count feature needs a table/window.",
    "ct_dst_ltm": "Connection-count feature needs a table/window.",
    "ct_src_dport_ltm": "Connection-count feature needs a table/window.",
    "ct_dst_sport_ltm": "Connection-count feature needs a table/window.",
    "ct_dst_src_ltm": "Connection-count feature needs a table/window.",
    "is_ftp_login": "Application-level FTP feature.",
    "ct_ftp_cmd": "Application-level FTP command count.",
    "ct_flw_http_mthd": "HTTP method count needs application parsing.",
    "ct_src_ltm": "Connection-count feature needs a table/window.",
    "ct_srv_dst": "Connection-count feature needs a table/window.",
}

MISSING_TOKENS = ["", " ", "NaN", "nan", "None", "none", "NULL", "null"]


def resolve_unsw_files(data_dir: Path) -> tuple[dict[str, Path], list[str]]:
    paths = {key: data_dir / name for key, name in REQUIRED_UNSW_FILES.items()}
    if not paths["features"].exists():
        for candidate in FEATURE_FILE_CANDIDATES:
            candidate_path = data_dir / candidate
            if candidate_path.exists():
                paths["features"] = candidate_path
                break
    missing = [str(path) for path in paths.values() if not path.exists()]
    return paths, missing


def feature_path_category(column: str) -> tuple[str, str]:
    if column in TARGET_OR_LEAKAGE_COLUMNS:
        return "target_or_leakage", "Do not use as an input feature."
    if column in DIRECT_PACKET_CANDIDATES:
        return "packet_path_candidate", DIRECT_PACKET_CANDIDATES[column]
    if column in FLOW_LITE_CANDIDATES:
        return "flow_lite_candidate", FLOW_LITE_CANDIDATES[column]
    if column in STATEFUL_FLOW_FEATURES or column.startswith("ct_"):
        reason = STATEFUL_FLOW_FEATURES.get(column, "Connection-count feature needs a table/window.")
        return "stateful_flow_feature", reason
    return "review_required", "Not classified yet; inspect before using in a hardware claim."


def selected_packet_path_columns(columns: Iterable[str]) -> list[str]:
    allowed = set(DIRECT_PACKET_CANDIDATES) | set(FLOW_LITE_CANDIDATES)
    return [column for column in columns if column in allowed and column not in TARGET_OR_LEAKAGE_COLUMNS]


def selected_packet_header_columns(columns: Iterable[str]) -> list[str]:
    allowed = set(PACKET_HEADER_ONLY_FEATURES)
    return [column for column in columns if column in allowed and column not in TARGET_OR_LEAKAGE_COLUMNS]


def selected_flow_lite_columns(columns: Iterable[str]) -> list[str]:
    allowed = set(FLOW_LITE_CANDIDATES)
    return [column for column in columns if column in allowed and column not in TARGET_OR_LEAKAGE_COLUMNS]


def selected_hybrid_v0_columns(columns: Iterable[str]) -> list[str]:
    allowed = set(PACKET_HEADER_ONLY_FEATURES) | set(FLOW_LITE_CANDIDATES)
    return [column for column in columns if column in allowed and column not in TARGET_OR_LEAKAGE_COLUMNS]


def feature_mode_columns(columns: Iterable[str], feature_mode: str) -> list[str]:
    columns = list(columns)
    if feature_mode == "all_csv":
        return input_feature_columns(columns)
    if feature_mode == "packet_path_candidates":
        return selected_packet_path_columns(columns)
    if feature_mode == "packet_header_only":
        return selected_packet_header_columns(columns)
    if feature_mode == "flow_lite_only":
        return selected_flow_lite_columns(columns)
    if feature_mode == "hybrid_v0":
        return selected_hybrid_v0_columns(columns)
    raise ValueError(f"Unsupported feature mode: {feature_mode}")


def input_feature_columns(columns: Iterable[str]) -> list[str]:
    return [column for column in columns if column not in TARGET_OR_LEAKAGE_COLUMNS]


def normalize_missing_values(df):
    return df.replace(MISSING_TOKENS, value=None)


def infer_feature_types(df, columns: Iterable[str]) -> tuple[list[str], list[str]]:
    categorical: list[str] = []
    numerical: list[str] = []

    for column in columns:
        if column in KNOWN_CATEGORICAL_COLUMNS:
            categorical.append(column)
            continue

        series = df[column]
        if str(series.dtype) in {"object", "category", "bool"}:
            non_null = series.dropna()
            if len(non_null) == 0:
                categorical.append(column)
                continue
            coerced = non_null.astype(str).str.strip()
            converted = coerced.str.replace(",", "", regex=False)
            numeric_ratio = converted.str.fullmatch(r"[-+]?\d+(\.\d+)?").mean()
            if numeric_ratio >= 0.95:
                numerical.append(column)
            else:
                categorical.append(column)
        else:
            numerical.append(column)

    return numerical, categorical


def feature_catalog(columns: Iterable[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for column in columns:
        category, reason = feature_path_category(column)
        rows.append({"feature": column, "packet_path_category": category, "note": reason})
    return rows
