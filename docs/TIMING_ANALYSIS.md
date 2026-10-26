# Static Timing Analysis & Engineering Assumptions

Extracted directly from OpenROAD stage 6 reports (`6_finish.rpt` and `6_report.json`).

---

## 1. Static Timing Analysis (STA) Metrics

| Parameter | Value | Verdict | Physical Interpretation |
|---|---|---|---|
| **Clock Name** | `core_clock` | Defined | Primary design clock defined in `constraint.sdc`. |
| **Clock Period Constraint** | $0.41\text{ ns}$ | Applied | Equivalent to a target frequency of $2.439\text{ GHz}$. |
| **Separately reported Fmax** | 2.41884 GHz | **Unreconciled** | Setup WNS remains negative at 0.41 ns. Do not interpret this figure as timing closure without native timing-path and clock-scope evidence. |
| **Setup WNS (Worst Negative Slack)** | **$-0.1634\text{ ns}$** | **Violation** | The longest path exceeds the target clock period by $163.4\text{ ps}$. |
| **Setup TNS (Total Negative Slack)** | **$-6.9946\text{ ns}$** | **Violation** | Cumulative negative slack summed across all 50 violating endpoints. |
| **Setup Violating Endpoints** | $50$ | Identified | Concentrated in data path subtraction/shift logic (`dpath.a_reg` to `dpath.b_reg`). |
| **Hold WNS** | **$+0.0896\text{ ns}$** | **PASS** | Minimum slack is positive ($+89.6\text{ ps}$). **Zero hold violations.** |
| **Hold TNS** | **$0.0000\text{ ns}$** | **PASS** | No hold timing violations exist on any path. |
| **Clock Skew (Setup / Hold)** | $1.05\text{ ps}$ | **PASS** | TritonCTS balanced clock tree across all flip-flop clock pins. |
| **Max Slew Violations** | $0$ | **PASS** | Slew limit: $0.71\text{ ns}$; max measured: $0.00\text{ ns}$ violation. |
| **Max Capacitance Violations** | $0$ | **PASS** | Cap limit: $0.68\text{ pF}$; max measured: $0.00\text{ pF}$ violation. |

---

## 2. Documented Engineering Assumptions & Limitations

1. **Aggressive Clock Period:**
2. **Hypothesis, not tested:** A looser clock such as 0.58 ns might resolve the reported setup failures, but timing must be rerun at that constraint before any positive slack is claimed.

2. **Virtual Clock Warning (`STA-0450`):**
   OpenSTA reported `[WARNING STA-0450] virtual clock vclk_core_clock can not be propagated`. The virtual clock is used to model input/output delay constraints at core boundaries; it is unpropagated by design and does not degrade internal core path analysis.

3. **PDK Technology Boundary:**
   The design was synthesized and laid out using the Nangate $45\text{ nm}$ Open Cell Library (FreePDK45). This is an academic predictive technology node, not a commercial tapeout foundry process (TSMC/Intel/Samsung).

4. **Power & IR Drop Corner:**
   All power figures ($6.02\text{ mW}$) and IR drop calculations ($1.05\%\text{ VDD}$, $0.62\%\text{ VSS}$) reflect the typical process corner at $1.10\text{ V}$ and $25^\circ\text{C}$.


### Review limitation

The reported setup WNS of -0.1634 ns at a 0.41 ns constraint establishes that the run failed this setup check. A separately reported minimum period of 0.4134 ns needs interpretation from native timing reports; it cannot be presented as an achieved clock independently of the violating paths. Original raw timing reports were not available in this documentation audit.
