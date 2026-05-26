# Risk Log

## Risk 1: Topic Novelty Risk

FPGA IDS 已有 Pigasus、Fidas 等强工作。如果题目只是“FPGA 入侵检测卸载”，创新不足。

Mitigation:

把论文定位为 hybrid-feature packet-path TinyML、runtime-reconfigurable core 和 safe bounded online adaptation，而不是通用 FPGA IDS offload。

## Risk 2: Online Learning Risk

如果直接使用模型预测标签进行训练，可能导致错误自强化。

Mitigation:

在线适应必须有 gating、confidence threshold、shadow weight bank、validation window 和 rollback。

## Risk 3: Data Poisoning Risk

攻击者可能构造流量污染在线更新过程。

Mitigation:

限制更新幅度，使用窗口级证据和验证逻辑，并在实验中设计 poisoned update sample 场景。

## Risk 4: Hardware Complexity Risk

完整神经网络训练在 FPGA 上成本高，第一阶段不做完整反向传播。

Mitigation:

第一阶段只考虑 threshold update、prototype update 或 last-layer update。

## Risk 5: Platform Limitation Risk

当前主机可能只有 1G 以太网接口，不能直接做 10G/40G 外部实测。

Mitigation:

第一阶段使用 AXI-Stream/BRAM trace replay、JTAG/UART/ILA/result-buffer logging，不声称外部 line-rate。

## Risk 6: Evaluation Risk

如果只有仿真，没有综合、时序、资源和板上验证，论文说服力不足。

Mitigation:

后续硬件阶段至少提供核心模块的 synthesis、implementation、timing、resource 和 board-level evidence。

## Risk 7: Dataset Risk

NIDS 数据集可能存在泄漏、过拟合或分布偏差，需要注意官方划分和跨数据集测试。

Mitigation:

Day 03 使用官方 train/test split，并记录 label distribution、missing values、feature set 和 seed。

## Risk 8: Inter-FPGA Communication Risk

RJ45 接口连接在 A7 FPGA 上，而主要计算资源和 QSFP+ 接口连接在 XCKU085 上。如果 A7 与 XCKU085 之间缺少稳定数据通路，1G live demo 和主 TinyML pipeline 的集成会变复杂。

Mitigation:

不让第一篇论文依赖 A7-to-XCKU085 live input。优先做 XCKU085 内部 trace replay。

## Risk 9: Label Availability Risk

真实在线更新时，FPGA 通常不知道一个 packet 的真实标签。如果只依赖模型自身预测作为伪标签，更新可信度不足。

Mitigation:

把在线更新表述为 bounded/pseudo-label-based adaptation，并明确讨论标签不确定性。

## Risk 10: Baseline Selection Risk

如果没有合理 baseline，例如 fixed model、threshold update、prototype update、last-layer update、raw packet baseline、flow feature baseline，论文实验说服力会不足。

Mitigation:

软件阶段先建立 Logistic Regression、Tiny MLP、INT8 simulation 和 feature-subset baseline。

## Risk 11: Scope Creep Risk

如果同时做 10G MAC、完整 NIDS、TinyML、在线更新、跨数据集、外部通信，项目会失控。必须按阶段推进。

Mitigation:

Day 03 只做数据集理解、软件 baseline 脚手架和报告，不写 RTL。

## Risk 12: Feature Leakage Risk

UNSW-NB15 中 `label` 和 `attack_cat` 是目标字段，`id` 也可能带有顺序或划分信息。训练脚本必须排除这些字段，报告中必须说明使用的 feature set。

Mitigation:

预处理脚本默认删除 `id`、`label`、`attack_cat`，并保存 feature metadata。

## Risk 13: Flow-Feature Overclaim Risk

UNSW-NB15 官方 CSV 多数是 flow-derived feature。如果直接把这些结果说成 packet-path FPGA 检测效果，会造成论文表述过度。

Mitigation:

Day 03 结果只作为 software/flow-feature baseline。packet-path 结论必须来自后续 parser-derived hybrid features、trace replay、仿真或硬件测量。
