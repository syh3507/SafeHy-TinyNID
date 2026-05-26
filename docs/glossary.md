FPGA：Field-Programmable Gate Array，现场可编程门阵列。它是一种可以通过硬件描述语言重新配置内部逻辑的芯片，既可以用于芯片原型验证，也可以作为低延迟、高并行的硬件加速平台。

RTL：寄存器传输级，用于编写硬件描述语言（Verilog/VHDL）的一种方式。

Packet：包，在这项工作中可以视为网络包，应该具体指以太网 MAC 帧或从以太网帧中解析出的网络层/传输层 packet。

Packet-Path：网络数据包在 FPGA 或网络设备内部经过的流式处理路径，包括接收、缓存、解析、特征提取、模型推理、决策和输出等环节。

NIDS：网络入侵检测系统，Network Intrusion Detection System。

TinyML：面向资源受限设备的小型机器学习推理方法，强调低功耗、低存储、低计算量和实时性。在本项目中，TinyML 指适合部署在 FPGA packet path 中的小型定点模型，例如 Logistic Regression、Tiny MLP、BNN 或轻量 Autoencoder。

Hybrid Feature：混合特征，指同时使用多类输入信息，例如 packet header 字段、包长度、协议类型、端口号、TCP flags、payload 前若干字节和轻量统计量，而不是只使用 flow feature 或 raw packet。

Flow Feature：流特征，指根据一段连接或一组同五元组 packet 统计出来的特征，例如持续时间、包数、字节数、速率、抖动、连接次数等。它通常需要 flow table、计数器、时间戳或应用层解析。

Raw Packet Feature：原始包特征，指直接使用 packet 的字节内容或固定长度 byte window 作为模型输入，不依赖复杂人工统计。

Hardware-Friendly Feature：硬件友好特征，指可以由 FPGA packet path 低成本提取的字段或统计量，例如包长、协议号、端口、TCP flags、有限 payload 字节、简单 byte sum/xor/count 等。

Online Learning：在线学习，指模型在数据流不断到来时持续学习，可能涉及较完整的参数更新，例如增量训练、梯度更新或在线分类器更新。

Online Adaptation：在线适应，范围更窄、更保守，通常不是完整重新训练，而是对阈值、统计量、类别中心、最后一层权重等少量参数进行受控调整。

Concept Drift：概念漂移，指数据分布或输入和标签之间的关系随时间发生变化。例如某段时间正常流量模式改变，或者攻击方式变化，导致原来训练好的模型检测效果下降。

Pseudo Label：伪标签，指模型自己预测出来的标签，被临时当作训练或更新依据。例如模型判断某个包是 attack，这个 attack 标签不一定是真的，只是模型自己的判断。

Data Poisoning：数据投毒，指攻击者故意构造或注入样本，影响模型的训练或在线更新过程，使模型学到错误规则，降低检测效果，甚至把攻击流量学成正常流量。

Shadow Weight Bank：影子权重区。系统保留两套权重：Active Weights 用于当前推理，Shadow Weights 用于存放候选更新结果。新权重先进入 Shadow Bank，通过验证后才切换为 Active Weights。

Validation Window：验证窗口，指最近一小段缓存样本或统计窗口，用来评估新权重是否比旧权重更稳定。只有新权重在验证窗口上表现可接受，才允许切换。

Rollback：回滚。如果在线更新后的候选权重导致检测效果下降或触发异常风险，系统恢复到旧权重。

AXI-Stream：AXI 协议的一种变体，有 valid/ready/data/keep/last 等信号。

BRAM：Block RAM，FPGA 的片上 RAM。

INT8 Quantization：8 位整数量化，把模型中的权重、激活值或中间结果从 FP32 浮点数转换为 8-bit integer 或定点数，以减少硬件资源和计算开销。

BNN：Binarized Neural Network，二值神经网络，通常把权重或激活值限制为 +1/-1 或 0/1，从而用 XNOR、popcount 等简单逻辑替代乘法，适合 FPGA 低资源实现。

MLP：Multi-Layer Perceptron，多层感知机，由多层全连接层和激活函数组成。训练时通常使用反向传播更新权重；推理时只做前向计算。

Label Leakage：标签泄漏，指训练输入中包含了目标标签或与目标几乎等价的信息，导致离线准确率虚高，但真实部署中不可用。例如把 `attack_cat` 用作二分类入侵检测输入就是泄漏。

Feature Quantization：特征量化，指把 FP32 或软件预处理后的连续特征映射为 INT8/fixed-point 表示，用于估计定点误差并靠近 FPGA 实现。
