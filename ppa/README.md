# Paired custom MAC physical-design experiment — NOT RUN

This is a **reproducible experiment scaffold**, not post-route results. The goal is to compare the default-parameter GOLD and operand-isolated GATE MACs, both [formally equivalent at their architectural outputs](../docs/FORMAL_PROOF.md), using one pinned ORFS build, Nangate45, fixed floorplan and SDC. The [OpenROAD flow guide](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts/blob/master/docs/index.md) supports external `DESIGN_CONFIG` and Nangate45.

## Controlled variables

- RTL variants: `mac_gold_top` and `mac_gate_top`; wrappers have identical top-level port names, widths and parameters (DATA_W=8, ACC_W=24).
- Same `ppa/config.mk` and `ppa/constraint.sdc`; the **only variant** is the instantiated MAC module.
- Nangate45 typical library, period **5.000 ns**, input/output delay **0.200 ns**, setup uncertainty **0.100 ns**, load **0.010 pF**; fixed die **100×100 µm**, core **80×80 µm** (from 10 to 90), placement density **0.45**. These are *experiment settings*, not measured design results.
- Pin ORFS commit `64939f3717ad7c694199ba04cb98924b98022868` (historical reference commit) and capture `git rev-parse HEAD`, source SHA-256, tool versions, synthesis logs, all route reports and output database/GDS. If a different ORFS SHA is deliberately selected, set `ORFS_EXPECTED_COMMIT` to that immutable SHA for **both** runs and disclose the change.
- Run the same variant-independent `make` targets, separate output namespaces and identical `FLOW_VARIANT=base`. Do not compare this MAC to the earlier GCD reference.

## Running manually on a machine with ORFS installed

```bash
# Check out a pinned OpenROAD-flow-scripts commit in a clean working tree.
git -C /path/OpenROAD-flow-scripts checkout 64939f3717ad7c694199ba04cb98924b98022868
# From this MAC repository:
bash ppa/run_pair.sh /path/OpenROAD-flow-scripts /absolute/path/mac-ppa-evidence
```

The script fails if the ORFS SHA differs, tracked source is dirty, or either `make` exits nonzero. It preserves raw logs, reports, routed results and hashes. It **has not been executed** here; compatibility with that historical ORFS commit must be tested before treating the scaffold as a validated recipe. A successful `make` alone does not imply timing closure or zero DRC.

## Required evaluation before a PPA claim

| Metric | GOLD | GATE | Acceptance rule |
|---|---|---|---|
| ORFS SHA / Nangate45 Liberty and voltage | not run | not run | Same exact SHA/corner/voltage |
| Die/core and clock/IO constraints | fixed in config | fixed in config | Confirm actual generated SDC/DEF |
| Placed standard-cell area (exclude fill/tap, report definition) | not run | not run | Native post-route report |
| Setup WNS/TNS, violating endpoints | not run | not run | STA with same constraints/corner |
| Hold WNS/TNS, violating endpoints | not run | not run | STA with same constraints/corner |
| Detailed-route DRC / antenna / route overflow | not run | not run | Raw tool logs and route status |
| Total wirelength / buffers / congestion | not run | not run | Native reports, same definitions |
| Leakage, internal, switching power | not run | not run | Same activity, frequency, voltage, corner |
| Runtime / memory | not run | not run | Capture resource logs and hardware |

**Power limitation:** ORFS vectorless estimates are not an apples-to-apples workload-specific switching-power comparison. Before claiming dynamic-power benefit, generate a deterministic testbench activity trace (VCD/SAIF) covering the **same stimulus** for both designs, including idle/valid ratios, zero operand frequency, input toggles and reset, and propagate the activity to the same post-route power-analysis method. State vectorless vs activity-based estimates separately. If one variant has a negative WNS or fails routing, report that trade-off rather than hiding it.

**Missing execution dependency:** access to a working ORFS Nangate45 installation (local Docker/WSL or an explicitly approved CI runner with sufficient resources). This scaffold does not trigger hosted EDA runs or paid compute by itself.
