# Technical review checklist — Ricursive Software Engineer, Chip Design

**Scope:** self-study and interview preparation, not a claim of employment readiness, chip tapeout, or MAC PPA improvement. Answer these without consulting an AI assistant; reproduce every number from the cited source reports before quoting it to a reviewer.

## 1. Explain the physical flow in 60 seconds

RTL elaboration -> logic synthesis -> floorplan/power grid -> placement and optimization -> clock-tree synthesis -> global/detailed routing -> parasitic extraction -> static timing and physical checks -> GDS generation. A completed reference RTL-to-GDS flow is **not** independent foundry signoff, LVS closure, or tapeout. This repository records a **historically reported** Nangate45 GCD reference run, but its original `Ricursive_GCD_Real_Artifacts.tar.gz` GDS/log archive is unavailable for independent validation. Do **not** claim that the public repository independently proves this physical flow completed; the GCD report is also **not** the custom MAC physical implementation.

**Reviewer drill:** distinguish the published historical commit/image/checksum claims from raw files actually inspected. Request the original archive, verify its SHA-256 and sharing permission, and only then inspect the SDC, stage-5 route log, final GDS/DEF and final timing report. Until then, do not claim those reports were independently reproduced or checked.

## 2. Setup and hold timing: what do the signs mean?

* Setup slack = required arrival time minus actual data arrival time. A negative WNS indicates at least one setup path violates its constraint; TNS is the aggregate magnitude of negative endpoint slacks under the report's conventions. Reported GCD reference setup WNS = **−0.163 ns**, TNS = **−6.995 ns** at a **0.41 ns** target. It **does not meet** that target.
* Hold slack tests whether data changes too early relative to the capture edge. Reported hold WNS = **+0.0896 ns** with no hold violations. A hold pass does not cancel a setup failure.
* A simplistic setup-only period adjustment suggests 0.41 + 0.163 = **0.573 ns** (~1.75 GHz), **not** a validated achievable Fmax. Path groups, uncertainty, latency, multicycle constraints and clocking details must be checked. Do not present the separately reported 2.41884 GHz Fmax as a closed timing result.
* Fix setup by locating worst paths and examining logic depth, fanout, wire RC, congestion, buffering, cell sizing, placement, retiming or pipelining; rerun setup and hold because improvements can introduce hold problems.

**Reviewer drill:** identify startpoint, endpoint, path group, launch/capture clocks, input/output delays, setup uncertainty, worst cell arc and wire delay in the actual STA report.

## 3. DRC, routability and power

* A detailed-route report showing zero violations and an empty antenna report are **flow-level** results, not independent DRC/LVS signoff.
* Routing failures can stem from local congestion, pin access, routing tracks, density, blockages, constraints, layer assignment or disconnected nets. Inspect overflow/congestion maps, routing log and DRC coordinates before changing utilization.
* GCD reported 1,000 placed instances = 674 functional + 326 fill/tap; reported functional category area **894.29 μm²** plus support area **182.48 μm²** = **1,076.77 μm²** of summed instance categories. **Do not label that sum as core geometry**. Reported design area ~907 μm² and utilization ~84% require native tool-definition/DEF reconciliation.
* GCD reported **6.02 mW** power is a tool estimate for the reference example, **not** a MAC power measurement. Switching-power comparisons require controlled activity, clock, library corner, voltage, frequency, and output loading. Lower logic-cell area does not automatically imply lower routed delay or dynamic power.

## 4. Understand the custom RTL rather than memorising claims

The two parameterized modules are `prefill_mac_tile_gold` and `prefill_mac_tile_gate` in `rtl/prefill_mac_tile.sv`. For valid cycles, the accumulator computes signed multiplication plus either previous accumulator or zero if `clear_acc` is asserted, with **modulo 2^ACC_W** wraparound. On invalid cycles, accumulator and overflow hold; `valid_out` follows `valid_in` at the next clock. Reset is asynchronous active-low. `overflow_flag` tests two's-complement addition overflow using the sign of the widened result.

The candidate drives multiplier operands to zero when `valid_in=0` or either operand is zero. The **internal combinational product can differ on invalid cycles** even though architectural outputs are unchanged. Therefore, an EQY partition comparing same-named internal `product` wires would produce a **real counterexample to that internal comparison**, not necessarily an output-level functional mismatch. Rename unmatched gate-only intermediates or constrain partition matching appropriately; then require every **architecturally observable output** and state to be formally proven.

**Reviewer drill:** show an invalid cycle with nonzero inputs, an active `clear_acc`, a signed −128×−128 multiplication, a wraparound case and a reset edge. Explain why a 3,009-vector simulation is not an exhaustive formal proof.

## 5. Formal-verification closure gate

Do not claim proof on the strength of a console line saying `PASS`. A valid EQY result requires successful tool exit, `prefill_mac/PASS`, no `prefill_mac/FAIL`, and no unproven/unmatched architectural outputs. Record tool versions, complete logs, partition coverage and assumptions. Run at least the default parameters (DATA_W=8, ACC_W=24); simulation exercises DATA_W=8, ACC_W=16; [hosted EQY proof](FORMAL_PROOF.md) covers DATA_W=8, ACC_W=24 and three output partitions. Explain parameter coverage and induction/engine limitations.

## 6. Controlled MAC PPA comparison gate

Build and route both designs using **identical** ORFS commit/image, Nangate45 libraries, SDC clock/IO constraints, placement density, floorplan, voltage, corner, synthesis/optimization settings and tool version. Use reproducible activity traces for both; report input data distribution and valid-cycle duty cycle. Compare the **post-route** area (definition explicit), setup/hold WNS/TNS, routed wirelength/DRCs, internal/switching/leakage power, and elapsed runtime. Include uncertainty and any negative tradeoffs. No physical MAC PPA improvement is established until both physical runs and raw reports exist.

## 7. Personal ownership drill (answer aloud)

1. Why did the first EQY run fail before proof? (Gold/gate top-module names differed.)
2. Why did the next EQY run prove 29 of 30 partitions but fail `product`? (Gating changes an unobservable intermediate on invalid cycles.)
3. What concrete log distinguishes a proven fix from a cosmetic renamed signal?
4. How do you separate flow reproducibility, formal equivalence and physical PPA?
5. What would you change first if a real MAC run misses setup by 100 ps, and how would you prevent overfitting?
6. Which artifacts and tool versions let a stranger reproduce your findings?
7. What did **you** personally implement, test, debug and review, versus what was produced by an AI coding agent?

**Pass criterion:** answer each question with the relevant code/report open and without invented measurements. Record unresolved questions as preparation tasks rather than claiming mastery.
