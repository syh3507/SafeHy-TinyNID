# CONTEXT.md

## 0. Purpose of This File

This file stores the full working context for the SafeHy-TinyNID research project.

It should be read by Codex before performing project work. `AGENTS.md` contains durable working rules; this file contains the detailed research background, decisions, constraints, and roadmap.

---

# 1. Final Research Topic

## Chinese Title

**SafeHy-TinyNID：面向资源受限 FPGA Packet-Path 入侵检测的混合特征 TinyML 加速器与安全受控在线适应机制**

## English Title

**SafeHy-TinyNID: A Hybrid-Feature TinyML Accelerator with Safe Bounded Online Adaptation for Packet-Path Intrusion Detection on Resource-Constrained FPGAs**

---

# 2. One-Sentence Summary

This project studies how to deploy a lightweight TinyML intrusion detector inside an FPGA packet-processing path, using hardware-friendly hybrid features and a safe bounded online adaptation mechanism that can update selected parameters under traffic drift without full retraining or unsafe self-learning.

Chinese summary:

本项目研究如何在资源受限 FPGA 的网络数据包处理路径中部署轻量级 TinyML 入侵检测模型，并通过安全受控的在线适应机制，使模型在流量变化时可以有限度更新。

---

# 3. Core Motivation

Network traffic and attack patterns evolve over time. Traditional CPU-based NIDS may face latency and throughput challenges, while prior FPGA IDS systems have already demonstrated very strong performance for signature/rule/regex-based offload.

The project therefore should not claim novelty in simply “putting IDS on FPGA.” Instead, the research question is:

> How can a resource-constrained FPGA support packet-path TinyML intrusion detection with hardware-friendly hybrid features and safe bounded adaptation under changing traffic distributions?

---

# 4. What This Project Does

1. Parse network packet or packet-trace input.
2. Extract hardware-friendly hybrid features.
3. Run a small quantized TinyML model for intrusion detection.
4. Support runtime reconfiguration of selected parameters.
5. Explore safe bounded online adaptation.
6. Evaluate accuracy, F1, AUC, quantization loss, resource use, timing, latency, throughput, and adaptation effects.
7. Build a reproducible research artifact suitable for a paper.

---

# 5. What This Project Does Not Do

1. It does not build a complete commercial IDS/IPS.
2. It does not compete head-to-head with Pigasus/Fidas on 100Gbps production deployment.
3. It does not implement full neural-network backpropagation on FPGA in the first version.
4. It does not start with Transformer, LLM, or large CNN acceleration.
5. It does not use model predictions as training labels without protection.
6. It does not claim external 40G line-rate measurements unless actual hardware tests support them.
7. It does not depend on PCIe or new hardware in the first phase.
8. It does not make MAC TX a prerequisite for the first research prototype.

---

# 6. Main Contributions

## Contribution 1: Hybrid-Feature Packet-Path TinyML

Design a hardware-friendly hybrid feature representation for packet-path NIDS and evaluate its trade-off against raw-packet and flow-feature baselines.

Candidate hybrid features include:

- Packet length.
- EtherType.
- IP protocol.
- IP header length.
- TTL.
- Source/destination port.
- TCP flags.
- UDP length.
- `is_tcp`, `is_udp`, `is_icmp`.
- First N payload bytes, initially N = 16 or 32.
- Lightweight byte statistics:
  - payload byte sum;
  - payload byte XOR;
  - zero byte count;
  - nonzero byte count;
  - max byte;
  - min byte;
  - printable ASCII count.

Do not start with full flow tables.

---

## Contribution 2: Runtime-Reconfigurable TinyML Core

Implement a small quantized TinyML inference core whose selected parameters can be updated without resynthesizing the FPGA bitstream.

Candidate models:

1. Logistic Regression: simplest baseline.
2. INT8 Tiny MLP: main model candidate.
3. BNN: low-resource FPGA comparison.
4. 1D-CNN: optional future extension for raw byte windows.
5. Autoencoder: optional future anomaly-detection comparison.

Candidate runtime-updatable parameters:

- Detection threshold.
- Class prototype / center vector.
- Last-layer weights and bias.
- Running statistics.

---

## Contribution 3: Safe Bounded Online Adaptation

Design an online adaptation mechanism that is safer and more bounded than naive self-training.

The adaptation should include:

1. Update gating.
2. Drift-aware trigger.
3. High-confidence sample filtering.
4. Shadow weight bank.
5. Validation window.
6. Rollback.
7. Maximum update magnitude.
8. External weight update path.

The fast packet path should not be blocked by the slow adaptation path.

---

# 7. Proposed System Architecture

Use this architecture as the default mental model:

```text
Packet / Trace Input
        |
        v
AXI-Stream Replay / Ethernet RX
        |
        v
Packet Parser
        |
        v
Hybrid Feature Extractor
        |
        v
TinyML Inference Core
        |
        v
Decision Unit
        |
        v
Result Logger
```

Slow adaptation path:

```text
Selected Samples
        |
        v
Drift Detector
        |
        v
Bounded Update Engine
        |
        v
Shadow Weight Bank
        |
        v
Validation / Rollback
```

Important principle:

> Fast path = low-latency inference.  
> Slow path = selected adaptation/control logic.

---

# 8. Hardware Inventory

## FPGA Board

- Board: custom idle engineering board from research group.
- FPGA1: Xilinx XCKU085.
- FPGA1 family: UltraScale.
- FPGA1 resources:
  - Logic cells: about 1,088K.
  - DSP: 4100 slices.
  - BRAM: 56.9Mb.
- DDR: 4 × 8G available.
- Vivado version: 2018.3.

## Secondary FPGA

- FPGA2: XC7A100T.
- Family: Xilinx Artix-7.
- Approximate resources:
  - Logic cells: 101,440.
  - DSP: 240 slices.
  - Memory: 4860 units as recorded in the user inventory.

## Network Interfaces

- QSFP+:
  - Quantity: 1.
  - Connected to XCKU085.
  - Supports 40G.
  - DAC/optical module can be purchased later.
- RJ45:
  - Quantity: 1.
  - Connected to XC7A100T, not directly to XCKU085.
  - Supports 1G.
- PC network interface:
  - Currently standard 1G RJ45.

## Debug Interfaces

- JTAG: available.
- UART: available, connected to XCKU085.
- ILA: available.
- LED: one status LED.
- PCIe: not available on current board.
- Board has optical port / RJ45 / UART only.

## Existing Modules

- 10G PCS: completed.
- MAC RX: completed.
- MAC TX: not completed.
- AXI FIFO: status needs clarification; earlier discussion mentioned CDC FIFO, current inventory says AXI FIFO not completed.
- CRC: not completed.
- UDP/IP: not completed.
- ARP: not completed.
- Simulation testbench: not completed.

## Inter-FPGA Communication

- A7 and XCKU085 can communicate.
- They are connected through GT.
- Lane width: unknown.
- Clocking: unknown.
- Existing code: partial.
- It may be possible to transmit packet or feature data.

## Hardware Strategy

First paper should not depend on external 10G/40G traffic generation.

Priority order:

1. Python software baseline.
2. Feature trace generation.
3. AXI-Stream simulation.
4. XCKU085 BRAM/AXI-Stream trace replay.
5. UART/JTAG/ILA result logging.
6. Optional A7 1G live demo.
7. Optional QSFP+ loopback.
8. Optional external 10G/40G NIC only if necessary and available.

Do not buy a new PCIe FPGA board at this stage unless the user explicitly decides to change hardware strategy.

---

# 9. Dataset Strategy

## First Dataset: UNSW-NB15

Use UNSW-NB15 first because it provides CSV-based features and labels, allowing rapid software baseline construction.

Initial files to use:

- `UNSW_NB15_training-set.csv`
- `UNSW_NB15_testing-set.csv`
- `UNSW-NB15_features.csv`

Initial tasks:

1. Load train/test CSVs.
2. Inspect columns.
3. Identify `label` and `attack_cat`.
4. Separate numerical and categorical features.
5. Check missing values.
6. Check class imbalance.
7. Identify hardware-friendly and non-hardware-friendly features.
8. Train baseline models.

## Second Dataset: CICIDS2017

Use CICIDS2017 later for packet/PCAP and generalization experiments.

Potential uses:

- PCAP replay.
- Flow feature vs packet feature comparison.
- Dataset-shift evaluation.
- Cross-dataset robustness.

## Optional Dataset

Possible later datasets:

- TON_IoT.
- Edge-IIoT.
- In-vehicle or industrial IDS datasets if the paper shifts toward IoT/edge/industrial security.

---

# 10. Packet-Level vs Flow-Level Decision

## Packet-Level

A decision is made per packet.

Example:

```text
One packet arrives -> extract header/payload/statistics -> classify.
```

This is the first target.

## Flow-Level

A decision is made over a group of packets belonging to the same flow.

Example:

```text
Same 5-tuple packets -> maintain duration/count/bytes/statistics -> classify.
```

This requires flow table, hashing, collision handling, timeout logic, and state management.

## Current Decision

First version uses:

> Packet-level hybrid features.

Flow-lite statistics may be explored later, but full flow-level detection is not the first hardware target.

---

# 11. Feature Strategy

Three input representations should eventually be compared:

## 1. Flow Feature Only

Use pre-extracted dataset features.

Pros:
- Easy baseline.
- Often good accuracy.

Cons:
- May be difficult to extract in real packet path.
- Requires stateful flow tracking.

## 2. Raw Packet / Raw Byte Only

Use raw packet byte windows.

Pros:
- Less manual feature engineering.
- Direct packet-path interpretation.

Cons:
- Larger input dimension.
- Less interpretable.
- Risk of dataset-specific overfitting.

## 3. Hybrid Feature

Use a combination of header, limited payload bytes, and lightweight statistics.

Pros:
- More hardware-friendly than full flow features.
- More informative than header-only.
- More interpretable than raw-only.

This is the intended main feature representation.

---

# 12. Model Strategy

Start simple. Do not over-engineer.

## Software Baselines

1. Logistic Regression.
2. Tiny MLP FP32.
3. Tiny MLP INT8 simulation.
4. BNN or binarized model.
5. Optional Random Forest / XGBoost as accuracy upper-bound, not hardware target.

## Hardware Target

First hardware implementation:

- INT8 Tiny MLP.
- Input dimension determined after feature analysis.
- Example architecture:
  - input_dim -> 32 -> 2
  - or input_dim -> 32 -> 16 -> 2.
- Inference only on fast path.
- Runtime reconfiguration for threshold or last-layer parameters.

## Why Not Start with BNN

BNN is resource-efficient but online adaptation is more complicated due to binary weights and sign flipping. INT8 MLP is more suitable for controlled last-layer updates.

---

# 13. Online Adaptation Strategy

Do not implement naive self-training.

## Modes to Compare

### Mode 0: Fixed Model

No online update. Baseline.

### Mode 1: Threshold Update

Only update the detection threshold.

Pros:
- Very simple.
- Hardware-friendly.
- Good first adaptation baseline.

### Mode 2: Prototype Update

Maintain class centers:

```text
normal_center
attack_center
```

Update high-confidence class center using:

```text
center_new = (1 - alpha) * center_old + alpha * x
```

### Mode 3: Last-Layer Update

Freeze feature extraction and hidden layers. Update final linear classifier only.

Pros:
- Stronger adaptation.
- More publishable.

Cons:
- More complex hardware and stability risks.

## Safe Adaptation Guards

Required guards:

1. Do not update on every packet.
2. Require confidence threshold.
3. Trigger only under drift or window-level evidence.
4. Limit update magnitude.
5. Write to shadow weights first.
6. Validate before activation.
7. Roll back on degradation or risk signal.
8. Preserve external update entry.

---

# 14. Baseline Strategy

The paper needs multiple baseline groups.

## A. Software Model Baselines

- Logistic Regression.
- Random Forest / XGBoost, optional accuracy upper-bound.
- Tiny MLP FP32.
- Tiny MLP INT8 simulation.
- BNN / binarized model.

## B. Input Feature Baselines

- Flow feature only.
- Raw packet / raw byte only.
- Header feature only.
- Hybrid feature.

## C. Adaptation Baselines

- No adaptation.
- Threshold update.
- Prototype update.
- Last-layer update.
- Unsafe self-training without guard, optional risk demonstration.
- Safe bounded adaptation.

## D. Hardware Baselines

- CPU software inference latency.
- FPGA fixed model.
- FPGA runtime-reconfigurable model.
- FPGA adaptation-enabled model.
- Optional FINN/hls4ml-generated baseline.

---

# 15. Evaluation Metrics

## ML Metrics

- Accuracy.
- Precision.
- Recall.
- F1-score.
- AUC.
- False positive rate.
- False negative rate.
- Per-attack-class metrics if multiclass is used.

## Quantization Metrics

- FP32 vs INT8 accuracy difference.
- INT8 vs BNN accuracy difference.
- Quantization-induced error distribution.

## Hardware Metrics

- LUT.
- FF.
- DSP.
- BRAM.
- Fmax.
- Latency in cycles.
- Latency in ns/us.
- Throughput.
- Initiation interval, if pipelined.
- Power estimate, optional.

## Adaptation Metrics

- Accuracy/F1 before and after drift.
- Adaptation latency.
- Number of updates.
- Rollback count.
- False update rate.
- Robustness under poisoned or mislabeled update samples.
- Resource overhead of adaptation logic.

---

# 16. Major Risks

## Risk 1: Topic Novelty

FPGA IDS has strong prior work such as Pigasus and Fidas. If this project is framed as generic FPGA IDS offload, novelty is weak.

Mitigation:
Frame as hybrid-feature TinyML + safe bounded online adaptation on resource-constrained FPGA packet path.

## Risk 2: Online Learning

Using model predictions directly as labels can cause error self-reinforcement.

Mitigation:
Use gated adaptation, confidence thresholds, shadow weights, validation, rollback, and external update path.

## Risk 3: Data Poisoning

Attackers may construct traffic that corrupts the online update process.

Mitigation:
Limit update magnitude, require window-level evidence, use validation, and test poisoning scenarios.

## Risk 4: Hardware Complexity

Full neural network training on FPGA is too complex for the first paper.

Mitigation:
Update thresholds, prototypes, or final layer only.

## Risk 5: Platform Limitation

Host currently has only 1G RJ45; current board has RJ45 on A7 and QSFP+ on XCKU085.

Mitigation:
Use trace replay and XCKU085 internal pipeline first.

## Risk 6: Evaluation Weakness

Only simulation or only software results will not be convincing.

Mitigation:
Provide at least synthesis, implementation, timing, resource, and board-level evidence for core modules.

## Risk 7: Dataset Bias

NIDS datasets can contain leakage, imbalance, and distribution bias.

Mitigation:
Use official splits, report class distribution, avoid leakage-prone features, and test on a second dataset later.

## Risk 8: Inter-FPGA Integration

A7-XCKU085 communication may become a separate engineering project.

Mitigation:
Do not make it required for the first paper.

## Risk 9: Label Availability

True labels are not available in real-time deployment.

Mitigation:
Treat online adaptation as bounded/pseudo-label-based and discuss label uncertainty explicitly.

## Risk 10: Baseline Selection

Without good baselines, experiments will not support novelty.

Mitigation:
Use fixed model, threshold update, prototype update, last-layer update, raw/flow/hybrid feature baselines.

## Risk 11: Scope Creep

Doing Ethernet stack, TinyML, online adaptation, cross-dataset evaluation, and live traffic all at once may fail.

Mitigation:
Follow staged milestones strictly.

---

# 17. Related Work Map

The table below should be expanded as papers are read.

| Paper | Year | Venue | Main Idea | Hardware Platform | Type | Relation to This Project | Novelty Risk |
|---|---:|---|---|---|---|---|---|
| Pigasus: Achieving 100Gbps Intrusion Prevention on a Single Server | 2020 | OSDI | 100Gbps FPGA-first IDS/IPS | FPGA + CPU server | Signature/rule pipeline | Demonstrates high-end FPGA IDS already exists | If we claim generic FPGA IDS offload, novelty is weak |
| Fidas: Fortifying the Cloud via Comprehensive FPGA-based Offloading for Intrusion Detection | 2022 | ISCA | Cloud-scale FPGA IDS offload | Cloud FPGA deployment | Regex + traffic classification | Shows industrial FPGA IDS offload is strong prior art | Avoid rule/regex/cloud offload framing |
| High Throughput Low Latency Network Intrusion Detection on FPGAs: A Raw Packet Approach | 2025 | TBD | Raw packet classification on FPGA | Virtex UltraScale+ reported in prior discussion | Learning-based | Close to raw-packet FPGA NIDS | Need hybrid feature + safe adaptation to differentiate |
| A High-Throughput Network Intrusion Detection System Using On-Device Learning on FPGA | 2024 | MCSoC | FPGA NIDS with on-device learning | TBD | Learning/adaptation | Close to online learning idea | Need safe bounded adaptation and packet-path framing |
| OS-ELM-FPGA: An FPGA-Based Online Sequential Unsupervised Anomaly Detector | 2018 | TBD | FPGA online sequential anomaly detection | TBD | Online anomaly detection | Prior work on FPGA online learning | Need NIDS packet-path context |
| DWOIDS: Dual Adaptive Windows toward Concept-Drift in Online Network Intrusion Detection | 2025 | ICCS | Online NIDS under concept drift | Software | Online NIDS | Supports adaptation motivation | Need hardware simplification |
| FINN | 2017 | FPGA | Fast scalable binarized neural network inference | FPGA | QNN framework | Useful for QNN/dataflow ideas | Do not reimplement generic FINN |
| hls4ml | ongoing | project/papers | Ultra-low-latency ML inference on FPGA | FPGA | HLS ML | Useful baseline/tooling reference | Do not only run hls4ml demo |

---

# 18. Current Paper Abstract Draft

## Chinese Abstract

随着网络流量规模和攻击形态的持续演化，传统基于 CPU 的网络入侵检测系统在高吞吐、低延迟和实时适应方面面临挑战。已有 FPGA 入侵检测系统主要聚焦于规则匹配、正则表达式匹配或高吞吐卸载，已经在 100Gbps IDS/IPS 和云数据中心入侵检测卸载等场景中取得重要进展。然而，对于资源受限 FPGA 平台而言，如何在数据包处理路径中部署轻量级学习模型，并在流量分布变化时进行安全、低成本、可控的在线适应，仍然是一个值得研究的问题。

本文提出 SafeHy-TinyNID，一种面向资源受限 FPGA 的 Packet-Path TinyML 网络入侵检测架构。该架构将轻量级 packet 解析、混合特征提取、定点 TinyML 推理和安全受控在线适应机制整合为流式硬件流水线。不同于完全依赖离线 flow feature 的方法，SafeHy-TinyNID 设计硬件友好的混合特征表示，结合 packet header、基础统计量与有限 payload 信息，在检测准确率、资源占用和处理延迟之间进行权衡。为应对网络流量中的概念漂移，本文进一步设计一种 bounded online adaptation 机制，仅对检测阈值、类别原型或最后一层模型参数进行受控更新，并引入 shadow weight bank、更新门控、验证窗口和回滚机制，以降低伪标签错误累积和数据投毒风险。

本文将在公开入侵检测数据集上建立软件基线，并在 [FPGA 平台型号待填] 上实现原型系统。实验将评估 SafeHy-TinyNID 在 [数据集待填] 上的检测准确率、F1-score、AUC、量化损失、资源占用、时序频率、端到端推理延迟、吞吐能力以及在线适应前后的性能变化。预期结果将展示该架构在资源受限 FPGA 上实现低延迟、可重配置、具备受控自适应能力的 packet-path 入侵检测的可行性。

## English Abstract

Network intrusion detection systems face increasing challenges in sustaining high throughput, low latency, and adaptability under evolving traffic distributions and attack patterns. Existing FPGA-based intrusion detection systems have achieved substantial progress in signature matching, regular expression acceleration, and high-throughput IDS/IPS offloading. However, for resource-constrained FPGA platforms, it remains challenging to integrate lightweight learning-based detection directly into the packet-processing path while enabling safe and low-cost adaptation to concept drift.

This paper proposes SafeHy-TinyNID, a hybrid-feature TinyML accelerator with safe bounded online adaptation for packet-path intrusion detection on resource-constrained FPGAs. SafeHy-TinyNID integrates packet parsing, hardware-friendly hybrid feature extraction, quantized TinyML inference, and controlled online adaptation into a streaming FPGA datapath. Instead of relying solely on pre-extracted flow-level features or raw packet classification, the proposed architecture uses a hybrid feature representation combining packet headers, lightweight statistics, and limited payload information to balance detection accuracy, hardware cost, and latency. To address evolving traffic distributions, SafeHy-TinyNID introduces a bounded adaptation mechanism that updates only selected parameters, such as detection thresholds, class prototypes, or the final-layer weights. The adaptation path is protected by update gating, shadow weight banks, validation windows, and rollback mechanisms to mitigate pseudo-label error accumulation and poisoning risks.

We plan to implement SafeHy-TinyNID on [FPGA platform to be specified] and evaluate it on [datasets to be specified]. The evaluation will include detection accuracy, F1-score, AUC, quantization loss, FPGA resource utilization, timing frequency, packet-path inference latency, throughput, and the performance impact of online adaptation. The expected contribution is a reproducible FPGA packet-path TinyML architecture that supports low-latency intrusion detection with runtime reconfigurability and safe bounded adaptation.

---

# 19. Day-by-Day Progress So Far

## Day 01

Completed:

- Project scope.
- Final title.
- Initial abstract.
- Glossary.
- Hardware inventory.
- Related work table.
- Risk log.

Key decision:

> Do not build generic FPGA IDS. Build SafeHy-TinyNID with hybrid features and safe bounded adaptation.

## Day 02

Completed:

- Revised glossary.
- Open questions.
- Updated hardware inventory.
- Related work table extension.
- Risk log extension.
- System structure draft.

Important findings:

- A7 and XCKU085 can communicate.
- Board schematic exists.
- XCKU085 DDR controller exists.
- MAC TX is not required for the first prototype.
- Dataset, feature, model, baseline choices are still open and should be settled through Day 03 software exploration.

---

# 20. Immediate Day 03 Plan

Day 03 should focus on dataset/software, not RTL.

## Tasks

1. Fix documentation:
   - Repair arrow encoding in `structure.md`.
   - Complete Pigasus/Fidas venue/platform/novelty-risk fields.
   - Add `Board Schematic Findings` to hardware inventory.

2. Create Python directory:

```text
python/
├── README.md
├── load_unsw.py
├── preprocess_unsw.py
├── train_baselines.py
├── quantize_sim.py
└── eval_metrics.py
```

3. Prepare UNSW-NB15 files:

```text
UNSW_NB15_training-set.csv
UNSW_NB15_testing-set.csv
UNSW-NB15_features.csv
```

4. Create `docs/day03_dataset_notes.md` and answer:
   - Number of rows and columns.
   - Label column.
   - Attack category column.
   - Numerical features.
   - Categorical features.
   - Missing values.
   - Class distribution.
   - Which features are hardware-friendly.
   - Which features are not packet-path-friendly.

5. Do not train complex models yet unless the dataset inspection is complete.

---

# 21. Glossary

## FPGA

Field-Programmable Gate Array. A reconfigurable hardware chip that can be used for both chip prototyping and low-latency/high-parallelism acceleration.

## RTL

Register Transfer Level. A hardware design abstraction used in Verilog/VHDL.

## Packet

A network packet. In this project, often an Ethernet MAC frame or packet-derived record.

## Packet-Path

The complete streaming path a network packet follows inside FPGA/network hardware: receive, buffer, parse, extract features, infer, decide, and output.

## NIDS

Network Intrusion Detection System.

## TinyML

Small machine learning inference designed for resource-constrained devices. In this project: Logistic Regression, Tiny MLP, BNN, or lightweight autoencoder deployed in FPGA packet path.

## Hybrid Feature

A mixture of multiple feature types, such as packet header fields, packet length, ports, protocol, TCP flags, limited payload bytes, and lightweight byte statistics.

## Inference

Forward computation using a trained model to classify or score input.

## Online Learning

Continuous learning from streaming data, possibly including full or partial parameter updates.

## Online Adaptation

A narrower and safer form of online update, usually limited to thresholds, statistics, prototypes, or final-layer weights.

## Concept Drift

Change in data distribution or input-label relationship over time.

## Pseudo Label

A model-generated label treated as if it were true. Risk: it may be wrong.

## Data Poisoning

An attack where adversarial data corrupts model training or online update.

## Shadow Weight Bank

A candidate weight storage area separate from active inference weights. Updates are first written to shadow weights and only activated after validation.

## Validation Window

A recent sample/statistics window used to evaluate whether a candidate update is safe and beneficial.

## Rollback

Reverting to previous active weights after a bad or risky update.

## AXI-Stream

Streaming AXI-style interface with signals such as valid, ready, data, keep, and last.

## BRAM

Block RAM on FPGA.

## INT8 Quantization

Converting FP32 weights/activations/intermediate values to 8-bit integer/fixed-point representation.

## BNN

Binarized Neural Network. A neural network whose weights or activations are usually constrained to +1/-1 or 0/1.

## MLP

Multi-Layer Perceptron. A feed-forward neural network with fully connected layers. Training uses backpropagation; inference uses only forward computation.

---

# 22. Operating Principle

The project should proceed in this order:

```text
Research scope
    -> dataset understanding
    -> software baseline
    -> quantization simulation
    -> feature representation comparison
    -> adaptation simulation
    -> hardware interface design
    -> RTL/HLS module prototypes
    -> simulation
    -> synthesis/implementation
    -> board-level validation
    -> paper writing
```

Do not skip directly to RTL.

---

# 23. Current Recommended Next Action

The next concrete action is:

> Build the UNSW-NB15 dataset inspection and baseline scaffold.

Minimum deliverable:

```text
docs/day03_dataset_notes.md
python/load_unsw.py
python/preprocess_unsw.py
reports/unsw_dataset_summary.md
```

No RTL yet.
