# Area & Cell-Count Terminology Corrections

This document provides the exact definition and correction of layout geometry and instance counts from the OpenROAD `nangate45/gcd` reference run.

---

## 1. Geometric Area Terminology

In standard physical design (ISPD / OpenROAD) terminology:

| Parameter | Measured Value | Definition & Correction |
|---|---|---|
| **Die Area** | 1,278.42 um² (reported) | Exact DEF boundary must be checked; rounded dimensions in the prior draft do not produce the quoted area exactly. |
| **Core Footprint** | approximately 1,077 um² | Exact DEF/ODB row/core boundaries are not in this repository; do not infer an exact footprint from the total instance-area sum. |
| **Functional Cell Area** | 894.29 um² | Sum of logic, sequential, clock and repair-cell category areas. Earlier 906.53 um² included 12.24 um² of tap cells. |
| **Physical Cell Area** | $182.48\ \mu\text{m}^2$ | Area occupied by physical non-logic cells (280 fill cells: $170.24\ \mu\text{m}^2$ + 46 tap cells: $12.24\ \mu\text{m}^2$). |
| **Reported Utilization** | approximately 84% | Reported by the flow; the exact numerator/denominator and tap treatment require raw native report reconciliation. |

---

## 2. Cell Count Disaggregation

The OpenROAD database records **1,000 total placed instances**. This count comprises:

1. **Functional Standard Cells (674 cells, 894.29 square microns from published categories):**
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


## Independent consistency check

35 + 377 + 86 + 167 + 1 + 6 + 2 = 674 functional instances; 280 + 46 = 326 physical instances; total = 1,000. Reported category areas sum to 894.29 square microns for functional instances. No new OpenROAD run was executed for these arithmetic corrections.
