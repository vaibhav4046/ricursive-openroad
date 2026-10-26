# Area & Cell-Count Terminology Corrections

This document provides the exact definition and correction of layout geometry and instance counts from the OpenROAD `nangate45/gcd` reference run.

---

## 1. Geometric Area Terminology

In standard physical design (ISPD / OpenROAD) terminology:

| Parameter | Measured Value | Definition & Correction |
|---|---|---|
| **Die Area** | $1,278.42\ \mu\text{m}^2$ | Full boundary including I/O pad ring and seal ring margins ($38.00\ \mu\text{m} \times 33.64\ \mu\text{m}$). |
| **Core Area** | $1,076.77\ \mu\text{m}^2$ | The inner area reserved for standard cell rows ($35.00\ \mu\text{m} \times 30.76\ \mu\text{m}$). **Correction:** Previous drafts incorrectly referred to $1,076.77\ \mu\text{m}^2$ as "Cell Area". |
| **Standard Cell Area (Active)** | $906.53\ \mu\text{m}^2$ | Area occupied strictly by active logical standard cells (gates, flip-flops, buffers). **Correction:** Previous drafts incorrectly referred to $907.0\ \mu\text{m}^2$ as "Core Area" or "Design Area". |
| **Physical Cell Area** | $182.48\ \mu\text{m}^2$ | Area occupied by physical non-logic cells (280 fill cells: $170.24\ \mu\text{m}^2$ + 46 tap cells: $12.24\ \mu\text{m}^2$). |
| **Core Utilization** | **84.19%** | $\frac{\text{Active Standard Cell Area}}{\text{Core Area}} = \frac{906.528}{1076.77} = 0.841897$. |

---

## 2. Cell Count Disaggregation

The OpenROAD database records **1,000 total placed instances**. This count comprises:

1. **Active Standard Cells (720 cells, 906.53 $\mu\text{m}^2$):**
   - **Sequential Logic:** 35 cells ($158.27\ \mu\text{m}^2$) — D-type flip-flops.
   - **Combinational Logic:** 377 cells ($512.32\ \mu\text{m}^2$) — NAND, NOR, XOR, multiplexers.
   - **Inverters:** 86 cells ($61.18\ \mu\text{m}^2$).
   - **Timing Repair Buffers:** 167 cells ($151.62\ \mu\text{m}^2$) — inserted during Resizer timing optimization.
   - **Timing Repair Inverters:** 1 cell ($2.39\ \mu\text{m}^2$).
   - **Clock Buffers:** 6 cells ($7.45\ \mu\text{m}^2$) — inserted by TritonCTS.
   - **Clock Inverters:** 2 cells ($1.06\ \mu\text{m}^2$) — inserted by TritonCTS.

2. **Physical Non-Functional Support Cells (326 cells, 182.48 $\mu\text{m}^2$):**
   - **Fill Cells:** 280 cells ($170.24\ \mu\text{m}^2$) — required for standard cell row density and layer continuity.
   - **Well Tap Cells:** 46 cells ($12.24\ \mu\text{m}^2$) — required to prevent CMOS latch-up.

*Note:* Total instance count ($280 + 46 + 6 + 167 + 86 + 2 + 1 + 35 + 377 = 1,000$).
