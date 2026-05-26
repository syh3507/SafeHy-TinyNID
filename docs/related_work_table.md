| Paper | Year | Venue | Main Idea | Hardware Platform | Learning/Rule-based | Difference from My Work | Risk to My Novelty |
|---|---:|---|---|---|---|---|---|
| Pigasus: Achieving 100Gbps Intrusion Prevention on a Single Server | 2020 | OSDI | 100Gbps FPGA-first IDS/IPS with CPU cooperation | FPGA + CPU server | Signature/rule-based pipeline | SafeHy-TinyNID does not claim novelty in generic FPGA IDS offload; it focuses on hybrid-feature TinyML and safe bounded adaptation on a constrained packet path. | If the paper is framed as "FPGA IDS acceleration", reviewers may see Pigasus as already solving the stronger throughput problem. |
| Fidas: Fortifying the Cloud via Comprehensive FPGA-based Offloading for Intrusion Detection | 2022 | ISCA | Cloud-scale FPGA offload for IDS functions | Cloud FPGA deployment | Regex/signature acceleration plus traffic classification | SafeHy-TinyNID is not a cloud rule/regex offload system; it studies small learning-based inference and controlled runtime adaptation. | If the project becomes rule offload or cloud-scale IDS, Fidas becomes a direct prior-work competitor. |

## Day 03 Note

UNSW-NB15 software baselines should be compared against learning-model baselines, not presented as outperforming Pigasus/Fidas. Pigasus and Fidas are prior work showing that high-throughput FPGA IDS offload already exists.
