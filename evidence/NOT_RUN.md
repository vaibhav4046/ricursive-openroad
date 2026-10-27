# Formal EQY PASS; custom MAC physical PPA NOT RUN (updated 27 October 2026)

This file was originally a historical `NOT RUN` declaration. The formal gate has since been resolved by an actual hosted EQY proof; the filename is retained so existing references do not break.

## 1. Formal equivalence — PASS (default parameters only)

- Gold: `prefill_mac_tile_gold`; gate: `prefill_mac_tile_gate`.
- DATA_W=8, ACC_W=24; asynchronous active-low reset; externally observable outputs: `acc_out`, `overflow_flag`, `valid_out`.
- [CI run #40419385442](https://github.com/vaibhav4046/ricursive-openroad/actions/runs/40419385442): EQY `DONE (PASS, rc=0)`, all 3 output partitions proved, ~19m02s elapsed.
- [Archived raw proof logs #12696644253](https://github.com/vaibhav4046/ricursive-openroad/actions/runs/40419385442/artifacts/12696644253), [proof limitations](../docs/FORMAL_PROOF.md).
- The 3,009-vector simulation is separate supporting evidence, not the formal proof. No claim of parameter-general proof, signoff, or power reduction.

## 2. Modified MAC physical design (RTL-to-GDS PPA) — NOT RUN

- No post-route MAC area, setup/hold timing, DRC, switching power or runtime measurements exist yet.
- The historical Nangate45 GCD reference metrics are **not** MAC measurements.
- Use the paired [ORFS experiment scaffold](../ppa/README.md) under identical settings. Raw physical runs and activity-controlled power reports are required before claiming improvements.
