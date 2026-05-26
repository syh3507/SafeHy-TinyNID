## 1. Final Topic
中文题目：
SafeHy-TinyNID：面向资源受限 FPGA Packet-Path 入侵检测的混合特征 TinyML 加速器与安全受控在线适应机制

English Title:
SafeHy-TinyNID: A Hybrid-Feature TinyML Accelerator with Safe Bounded Online Adaptation for Packet-Path Intrusion Detection on Resource-Constrained FPGAs

# My Current Understanding
我目前理解这个工作不是仅仅做 FPGA 对网络流量的入侵检测，而是在 FPGA 的 Packet path中加入一个非常轻量化的机器学习/深度学习模型，让网络数据流量在Datapath中“飞”过的时候就进入模型进行识别。当然这也不是仅仅把整个数据包（row data）或者仅仅针对流特征（flow feature）作为输入给这个TinyML，而是对row data/flow feature/混合数据特征进行对比和验证，来达到研究效果。同时由于多变的网络攻击，计划设计一个自适应调整功能，根据网络攻击包的置信程度、平均流量变化等特征决定在 FPGA 上进行在线更新权重，同时受限于硬件的资源和可能的投毒攻击，不是更新所有的权重，而是只更新最后一层的权重这样的设想。要先实现python的验证，之后部署到 FPGA 上，进行仿真、板级的测试。同时要在多个数据集，多种参数的环境下进行比较和总结，最后产出一篇高质量的论文。

## 目前还不懂的问题
1. 什么是 concept drift？
2. 什么是 shadow weight bank？
3. Hybrid Feature到底是什么意思？怎么提取？
4. 这里所谓的TinyML应该用什么模型，这个挑选的过程是否需要体现在论文中？