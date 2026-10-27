# Hosted EQY formal-equivalence proof — 27 October 2026

## Proven claim (limited scope)

The two modules in [`rtl/prefill_mac_tile.sv`](../rtl/prefill_mac_tile.sv), `prefill_mac_tile_gold` and `prefill_mac_tile_gate`, were proved equivalent at **the externally observable outputs** `acc_out`, `overflow_flag`, and `valid_out`, for default parameters **DATA_W=8, ACC_W=24** and the semantics of the supplied RTL/formal model. This is not a parameter-general theorem or a physical implementation result.

- [PR #2 (merged)](https://github.com/vaibhav4046/ricursive-openroad/pull/2), merge commit `2df08999c2b495424b7623aa032c2b3807af6b20`.
- Verified source PR HEAD: `66123c6c4ed2e252bde4886b99fd035edf7fa660`; CI tested synthetic merge of that head into its base (`ac31ec2...`).
- [Actions run #40419385442](https://github.com/vaibhav4046/ricursive-openroad/actions/runs/40419385442), job `121909710943`, **conclusion: success**.
- [Original logs and proof partitions (artifact #12696644253)](https://github.com/vaibhav4046/ricursive-openroad/actions/runs/40419385442/artifacts/12696644253); hosted artifact retention was configured for 14 days. Download/preserve these bytes independently before expiration. The console logs remain linked to the run.
- `eqy` stdout: `Successfully proved designs equivalent`, `DONE (PASS, rc=0)`, 19m02s elapsed. All three partitions `prefill_mac_tile.acc_out`, `prefill_mac_tile.overflow_flag`, `prefill_mac_tile.valid_out` were reported proven; none failed.
- Dynamic Icarus simulation: `DYNAMIC_EQUIVALENCE_PASS vectors=3009` in the same CI run, a separate, non-exhaustive check.
- Hosted tools: Yosys `0.70+221` (git `33177a407`), EQY `v0.70-1-gfb8b211`, SBY `v0.70-9-g79fc9ed`, Z3 in OSS CAD Suite 2026-10-26. Exact versions and commit are captured in the artifact.
- Formal configuration: [`formal/prefill_mac.eqy`](../formal/prefill_mac.eqy): `[collect *]`, SBY `depth 20`, `engine smtbmc z3`. EQY top module names are normalized for comparison.

## Diagnosed failures and resolution

1. [Run #40418930383](https://github.com/vaibhav4046/ricursive-openroad/actions/runs/40418930383) failed during combine: `Top modules of gold and gate do not have the same name`. The EQY configuration now renames both selected tops to the same comparison name.
2. [Run #40419217802](https://github.com/vaibhav4046/ricursive-openroad/actions/runs/40419217802) proved 29 of 30 partitions but failed the *internal* `product` partition. Operand isolation intentionally changes the internal multiplier product on invalid cycles, when the accumulator does not update. Matching that internal wire was an invalid equivalence requirement for this output-level specification. The candidate's gate-only intermediates were renamed; the final proof had **three architectural-output partitions**, all proved. Renaming alone is not a proof: the successful run's output-level proof is the evidence.

## Limitations

This establishes equivalence of the stated outputs under the EQY model and solver settings; it does not certify unrestricted parameter values, X/unknown semantics in silicon, metastability, clock-domain crossings, PDK mapping, routing, setup/hold timing, DRC/LVS, power savings, or tapeout. Review the exact RTL, reset handling, formal assumptions and generated proof files before extrapolating. A 20-step strategy configuration is not the same as claiming every reachable physical state was exhaustively simulated.

The historical Nangate45 **GCD** reference GDS archive is unrelated to this MAC proof and is still unavailable for independent raw-byte validation. The paired custom MAC physical-design experiment has **not been run**.
