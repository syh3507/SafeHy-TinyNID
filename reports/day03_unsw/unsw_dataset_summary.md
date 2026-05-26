# UNSW-NB15 Dataset Summary

Generated from local CSV files. This report is a dataset inspection artifact, not a model result.

## Command

```powershell
python python/load_unsw.py --data-dir data/raw --out-dir reports/day03_unsw
```

## Split Size

| Split | Rows | Columns |
|---|---:|---:|
| Train | 175341 | 45 |
| Test | 82332 | 45 |

## Label Columns

- Label column: `label`
- Attack category column: `attack_cat`

## Feature Types

- Input feature count after dropping `id`, `label`, and `attack_cat`: 42
- Numerical features (39): `dur`, `spkts`, `dpkts`, `sbytes`, `dbytes`, `rate`, `sttl`, `dttl`, `sload`, `dload`, `sloss`, `dloss`, `sinpkt`, `dinpkt`, `sjit`, `djit`, `swin`, `stcpb`, `dtcpb`, `dwin`, `tcprtt`, `synack`, `ackdat`, `smean`, `dmean`, `trans_depth`, `response_body_len`, `ct_srv_src`, `ct_state_ttl`, `ct_dst_ltm`, `ct_src_dport_ltm`, `ct_dst_sport_ltm`, `ct_dst_src_ltm`, `is_ftp_login`, `ct_ftp_cmd`, `ct_flw_http_mthd`, `ct_src_ltm`, `ct_srv_dst`, `is_sm_ips_ports`
- Categorical features (3): `proto`, `service`, `state`

## Binary Label Distribution

| Split | Label | Count |
|---|---:|---:|
| Train | 0 | 56000 |
| Train | 1 | 119341 |
| Test | 0 | 37000 |
| Test | 1 | 45332 |

## Missing Values

No missing values were detected after normalizing common blank tokens.

## Packet-Path Feature Review

| Feature | Category | Note |
|---|---|---|
| `id` | target_or_leakage | Do not use as an input feature. |
| `dur` | flow_lite_candidate | Duration requires timing state, but can be approximated in a small flow-lite window. |
| `proto` | packet_path_candidate | IP protocol field or parser-derived protocol code. |
| `service` | packet_path_candidate | Can be approximated from L4 ports, but UNSW service is already decoded. |
| `state` | packet_path_candidate | TCP state summary; packet-path use needs a small TCP/state parser. |
| `spkts` | flow_lite_candidate | Source packet count needs a counter. |
| `dpkts` | flow_lite_candidate | Destination packet count needs a counter. |
| `sbytes` | packet_path_candidate | Source bytes; single-packet hardware analogue is packet length. |
| `dbytes` | packet_path_candidate | Destination bytes; needs reverse direction or flow-lite context. |
| `rate` | flow_lite_candidate | Packet rate needs timing and count state. |
| `sttl` | packet_path_candidate | Source-side TTL-like header field. |
| `dttl` | packet_path_candidate | Destination-side TTL-like field; needs reverse direction context. |
| `sload` | flow_lite_candidate | Source load needs byte and time state. |
| `dload` | flow_lite_candidate | Destination load needs byte and time state. |
| `sloss` | flow_lite_candidate | Source loss estimate is not directly available from a stateless packet parser. |
| `dloss` | flow_lite_candidate | Destination loss estimate is not directly available from a stateless packet parser. |
| `sinpkt` | stateful_flow_feature | Inter-packet timing needs flow history. |
| `dinpkt` | stateful_flow_feature | Reverse inter-packet timing needs flow history. |
| `sjit` | stateful_flow_feature | Jitter needs timestamp history. |
| `djit` | stateful_flow_feature | Reverse jitter needs timestamp history. |
| `swin` | stateful_flow_feature | TCP window can be parsed, but this aggregate form is flow-derived. |
| `stcpb` | stateful_flow_feature | TCP base sequence value is parser-visible but dataset form is flow-derived. |
| `dtcpb` | stateful_flow_feature | Reverse TCP base sequence value needs bidirectional context. |
| `dwin` | stateful_flow_feature | Reverse TCP window aggregate needs bidirectional flow state. |
| `tcprtt` | stateful_flow_feature | TCP RTT requires SYN/SYN-ACK/ACK timing state. |
| `synack` | stateful_flow_feature | SYN-ACK timing requires handshake tracking. |
| `ackdat` | stateful_flow_feature | ACK-data timing requires handshake tracking. |
| `smean` | packet_path_candidate | Mean source packet size; flow-lite counter/statistic. |
| `dmean` | packet_path_candidate | Mean destination packet size; flow-lite counter/statistic. |
| `trans_depth` | stateful_flow_feature | HTTP transaction depth is application/stateful parsing. |
| `response_body_len` | stateful_flow_feature | HTTP response body length is application/stateful parsing. |
| `ct_srv_src` | stateful_flow_feature | Connection-count feature needs a table/window. |
| `ct_state_ttl` | stateful_flow_feature | Connection-count feature needs a table/window. |
| `ct_dst_ltm` | stateful_flow_feature | Connection-count feature needs a table/window. |
| `ct_src_dport_ltm` | stateful_flow_feature | Connection-count feature needs a table/window. |
| `ct_dst_sport_ltm` | stateful_flow_feature | Connection-count feature needs a table/window. |
| `ct_dst_src_ltm` | stateful_flow_feature | Connection-count feature needs a table/window. |
| `is_ftp_login` | stateful_flow_feature | Application-level FTP feature. |
| `ct_ftp_cmd` | stateful_flow_feature | Application-level FTP command count. |
| `ct_flw_http_mthd` | stateful_flow_feature | HTTP method count needs application parsing. |
| `ct_src_ltm` | stateful_flow_feature | Connection-count feature needs a table/window. |
| `ct_srv_dst` | stateful_flow_feature | Connection-count feature needs a table/window. |
| `is_sm_ips_ports` | packet_path_candidate | Simple comparison over source/destination IP and port fields. |
| `attack_cat` | target_or_leakage | Do not use as an input feature. |
| `label` | target_or_leakage | Do not use as an input feature. |

## Interpretation

UNSW-NB15 is useful for Day 03 software baselines because it provides official CSV splits and labels. Most fields are flow-derived, so results from this dataset should be described as software/flow-feature baselines unless later packet-trace or parser-derived hybrid features are added.
