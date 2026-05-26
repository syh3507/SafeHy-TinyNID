# AGENTS.md

## Project Identity

This repository is for the research project:

**SafeHy-TinyNID: A Hybrid-Feature TinyML Accelerator with Safe Bounded Online Adaptation for Packet-Path Intrusion Detection on Resource-Constrained FPGAs**

Chinese title:

**SafeHy-TinyNID：面向资源受限 FPGA Packet-Path 入侵检测的混合特征 TinyML 加速器与安全受控在线适应机制**

This is a research-code repository, not a production IDS/IPS product.

Always read `CONTEXT.md` before making non-trivial changes.

---

## Role of Codex

Act as a careful research engineering assistant for a student-led FPGA/ML/security paper project.

Your goals are:

1. Help build reproducible software baselines.
2. Help design clean RTL/HLS-style module boundaries.
3. Help maintain experiment logs and research notes.
4. Help avoid overclaiming, unsafe assumptions, and scope creep.
5. Help prepare a high-quality paper-ready artifact.

Do not behave like a generic coding assistant that only writes code. For every meaningful change, preserve the connection to the research question, evaluation plan, and paper contribution.

---

## Non-Negotiable Research Rules

1. Do **not** claim 10G/40G external line-rate performance unless it is actually measured with matching hardware.
2. Do **not** claim online retraining is safe unless the update mechanism includes guards such as gating, shadow weights, validation, and rollback.
3. Do **not** implement full neural-network backpropagation on FPGA as the first approach.
4. Do **not** use the model's own prediction as a training label without documenting pseudo-label risk.
5. Do **not** silently change the project direction from packet-path TinyML NIDS to generic FPGA IDS, generic ML, or generic Ethernet development.
6. Do **not** fabricate experimental results, hardware utilization, timing closure, accuracy, latency, throughput, or publication claims.
7. Do **not** treat Pigasus/Fidas-style FPGA IDS offload as the novelty of this project; those are prior work baselines.
8. Do **not** make the project depend on PCIe, external 40G NICs, or new FPGA boards unless explicitly requested.

---

## Current Research Position

The project is **not** “another FPGA IDS offload.”

The intended contribution is:

1. **Hybrid-feature packet-path TinyML inference** for NIDS.
2. **Runtime-reconfigurable TinyML core** on resource-constrained FPGA.
3. **Safe bounded online adaptation** using update gating, shadow weight banks, validation windows, and rollback.

The first implementation target is a small, reproducible pipeline:

```text
Dataset / Packet Trace
    -> Python preprocessing
    -> software baseline
    -> fixed-point simulation
    -> AXI-Stream-style trace replay
    -> packet parser / feature extractor
    -> TinyML inference core
    -> decision/result logger
    -> optional safe adaptation path
```

---

## Preferred Technical Strategy

### Software first

Before RTL implementation, establish:

1. Dataset loading.
2. Feature definitions.
3. Software baselines.
4. Quantization simulation.
5. Adaptation-mode simulation.
6. Evaluation metrics.

### Hardware second

First FPGA prototype should prefer:

1. BRAM/LUTRAM over DDR.
2. AXI-Stream-style replay over full external Ethernet.
3. JTAG/UART/ILA/result-buffer logging over MAC TX.
4. Fixed model before adaptive model.
5. Threshold update before prototype/last-layer update.

### Model selection order

Use this order unless project notes say otherwise:

1. Logistic Regression as minimal baseline.
2. INT8 Tiny MLP as main model candidate.
3. BNN as low-resource FPGA comparison.
4. 1D-CNN or autoencoder only as optional extensions.

---

## Repository Structure

Prefer this structure:

```text
SafeHy-TinyNID/
├── AGENTS.md
├── CONTEXT.md
├── README.md
├── docs/
│   ├── day01_project_scope.md
│   ├── day01_title_abstract.md
│   ├── day02_open_questions.md
│   ├── glossary.md
│   ├── related_work_table.md
│   ├── risk_log.md
│   ├── hardware_inventory.md
│   ├── structure.md
│   └── weekly_logs/
├── papers/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── python/
│   ├── README.md
│   ├── load_unsw.py
│   ├── preprocess_unsw.py
│   ├── train_baselines.py
│   ├── quantize_sim.py
│   ├── adaptation_sim.py
│   └── eval_metrics.py
├── rtl/
├── sim/
├── scripts/
└── reports/
```

Keep code, notes, reports, and generated outputs separated.

---

## Documentation Rules

When modifying or adding code, also update the relevant documentation:

- `docs/glossary.md` for terminology.
- `docs/risk_log.md` for new risks.
- `docs/related_work_table.md` for prior-work implications.
- `docs/hardware_inventory.md` for hardware assumptions.
- `reports/` for experiment outputs.

For each experiment, save:

1. Command used.
2. Dataset split.
3. Feature set.
4. Model.
5. Quantization mode.
6. Metrics.
7. Random seed.
8. Output artifact path.
9. Short interpretation.

---

## Coding Style

### Python

- Use clear, small scripts.
- Prefer deterministic behavior with explicit random seeds.
- Use `argparse` for experiment scripts.
- Never hard-code user-specific absolute paths.
- Save metrics as CSV/JSON/Markdown.
- Keep preprocessing, training, quantization, and evaluation separate.
- Include sanity checks for label distribution, missing values, and leakage-prone features.

### RTL

- Use explicit module interfaces.
- Prefer AXI-Stream-style valid/ready/data/last/keep conventions where appropriate.
- Keep packet parsing, feature extraction, inference, decision, adaptation, and logging as separate modules.
- Add testbenches before integration.
- Do not mix adaptation control logic into the fast packet path unless necessary.

---

## Paper-Aware Output Requirements

For any proposed implementation, explain:

1. Which contribution it supports.
2. What baseline it compares against.
3. What metric will evaluate it.
4. What risk it introduces.
5. Whether it is required for the first paper or optional.

When proposing results tables, include placeholders if data is not measured yet. Do not invent numbers.

---

## Current Hardware Constraints

The main FPGA is Xilinx UltraScale XCKU085. A secondary XC7A100T has the 1G RJ45 interface. The XCKU085 has the QSFP+ 40G interface, DDR, UART, JTAG, and ILA access. There is inter-FPGA communication between A7 and XCKU085 through GT, but lane count, clocking, and existing code details still need confirmation.

Therefore:

- Do not assume PC-to-XCKU085 1G Ethernet is direct.
- Do not assume external 40G traffic generation is available.
- Use AXI-Stream/BRAM trace replay for the first prototype.
- Treat A7-to-XCKU085 live input as an optional later integration task.

---

## Immediate Next Milestone

Build the Day 03 software baseline using UNSW-NB15:

1. Load training/testing CSV.
2. Inspect columns, labels, class balance, missing values.
3. Separate numerical and categorical features.
4. Identify which features are hardware-friendly.
5. Train Logistic Regression and Tiny MLP baselines.
6. Save metrics and notes.
7. Do not write RTL yet.

---

## Escalation / Stop Conditions

Before proceeding, stop and ask the user if:

1. A requested change would shift the project away from SafeHy-TinyNID.
2. A task requires buying hardware or changing board targets.
3. A result is needed but no measurement exists.
4. A data processing step may leak labels or future information.
5. A code change would make the first paper depend on an unverified hardware path.
