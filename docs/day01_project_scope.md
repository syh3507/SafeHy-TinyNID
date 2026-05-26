# Day 01 Project Scope

## 1. Final Topic

中文题目：
SafeHy-TinyNID：面向资源受限 FPGA Packet-Path 入侵检测的混合特征 TinyML 加速器与安全受控在线适应机制

English Title:
SafeHy-TinyNID: A Hybrid-Feature TinyML Accelerator with Safe Bounded Online Adaptation for Packet-Path Intrusion Detection on Resource-Constrained FPGAs

## 2. One-Sentence Summary
本项目研究如何在资源受限 FPGA 的网络数据包处理路径中部署轻量级 TinyML 检测模型，并通过安全受控的在线适应机制，使模型在流量变化时可以有限度更新。

## 3. What This Project Does
1. 解析网络 packet；
2. 提取硬件友好的混合特征；
3. 使用小型定点 TinyML 模型进行入侵检测；
4. 支持运行时更新部分参数；
5. 设计安全受控的在线适应机制；
6. 在 FPGA 上评估资源、时序、延迟和吞吐。

## 4. What This Project Does Not Do
1. 不做完整商业级 IDS/IPS；
2. 不和 Pigasus/Fidas 正面拼 100Gbps 生产部署；
3. 不做完整深度神经网络反向传播训练；
4. 不一开始做 Transformer/LLM；
5. 不把模型预测结果无保护地直接当标签训练；
6. 不虚假声称 40G 外部实测，除非后续真的具备对应硬件条件。

## 5. Core Contributions
Contribution 1:
We design a hardware-friendly hybrid feature representation for packet-path NIDS and evaluate its accuracy-resource-latency trade-off against raw-packet and flow-feature baselines.

Contribution 2:
We implement a runtime-reconfigurable quantized TinyML inference core on a resource-constrained UltraScale FPGA.

Contribution 3:
We propose a safe bounded online adaptation mechanism that updates selected parameters under drift-aware gating and rollback protection.
