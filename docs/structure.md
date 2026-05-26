# System Structure

## Fast Packet Path

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

The first prototype should use AXI-Stream-style trace replay or BRAM-fed feature replay before relying on live Ethernet input. This keeps the research focus on packet-path TinyML inference instead of turning Day 03 into Ethernet-stack development.

## Slow Adaptation Path

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
Validation Window
        |
        v
Commit or Rollback
```

The fast path performs inference. The slow path may update thresholds, prototypes, or a final layer only after gating and validation. Full neural-network backpropagation on FPGA is not part of the first approach.
