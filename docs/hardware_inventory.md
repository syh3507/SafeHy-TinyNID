# Hardware Inventory

## FPGA Board

板卡型号：课题组自制闲置工程板卡

FPGA1 芯片型号：XCKU085

FPGA1 系列：UltraScale

LUT/FF/DSP/BRAM 资源：逻辑单元 1,088K / DSP 4100 Slice / BRAM 56.9Mb

板载 DDR：有，容量 4 * 8G

Vivado 版本：2018.3

## Secondary FPGA

FPGA2 芯片型号：XC7A100T

FPGA2 系列：Xilinx Artix-7

LUT/FF/DSP/BRAM 资源：逻辑单元 101,440 / DSP 240 Slice / 内存 4860

## Network Interfaces

QSFP+ 数量：1，连接在 XCKU085 上

QSFP+ 支持速率：40G，连接在 XCKU085 上

是否有 DAC 线/光模块：可后续购买

RJ45 数量：1，连接在 XC7A100T 上

RJ45 支持速率：1G

电脑网口速率：目前只有一个普通 RJ45 网口，为 1G

## Debug Interfaces

JTAG：具备

UART：具备，连接在 XCKU085 上

ILA 是否可用：可以

板上 LED/按键：有一个用于指示设备状态的 LED

是否能通过 PCIe 通信：否，板上只有光口/RJ45/UART

## 已完成模块

10G PCS：已完成

MAC RX：已完成

MAC TX：暂未完成

AXI FIFO：暂未完成

CRC：暂未完成

UDP/IP：暂未完成

ARP：暂未完成

仿真 testbench：暂未完成

## 当前限制

1. 虽然有 QSFP+ 光口，但是电脑主机只有 1G RJ45 网口，不能直接假设具备 10G/40G 外部实测条件。
2. 主机有 PCIe 3.0 x16 和 PCIe 3.0 x1 插槽，但第一阶段不应让论文依赖购买 PCIe 网卡或新 FPGA 板卡。
3. 板上 RJ45 网口接在 A7 FPGA 上，而光口只接在 UltraScale XCKU085 上，需要注意数据路径。

## Board Schematic Findings

目前已确认有板卡原理图。根据当前记录：

1. RJ45 1G 接口连接在 XC7A100T 上，不应假设 PC 可以直接通过 RJ45 进入 XCKU085。
2. QSFP+ 40G 接口连接在 XCKU085 上，但目前没有外部 40G 流量发生和测量条件。
3. UART、JTAG、ILA 可用于 XCKU085 调试和结果读取。
4. A7 与 XCKU085 之间存在 GT 互联，但 lane 数、时钟、协议和已有代码细节仍需确认。
5. 第一阶段论文原型应优先使用 AXI-Stream/BRAM trace replay，不应依赖购买新 PCIe 板卡或完成外部 40G 链路。

## Inter-FPGA Communication

A7 与 XCKU085 是否有互联：有

互联位宽：暂未知

互联时钟：暂未知

是否已有代码：有部分

是否可以传输 packet 或 feature：可以，两个 FPGA 通过 GT 连接

## 补充问题

后续是否购买 PCIe 网卡、光模块或新板卡，需要在软件 baseline、trace replay 和 XCKU085 内部原型之后再决定。当前阶段优先使用现有硬件资源。
