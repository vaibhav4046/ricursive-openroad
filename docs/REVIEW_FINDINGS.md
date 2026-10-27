# Independent audit of published claims (26 October 2026)

Scope: reviewed the public README, reported metrics, RTL and testbench. This audit did not rerun OpenROAD, Docker, EQY or Icarus Verilog, and the original artifact archive is not present in this public GitHub repository.

## Correctable arithmetic and scope

- The seven functional instance classes total 674, not 720. The 326 fill and tap instances bring the total to 1,000.
- Functional cell area sums to 894.29 square microns. The 906.53 square micron figure includes 12.24 square microns of tap cells, so it should not be called functional-only area.
- Reported setup WNS (-0.163422 ns) at a 0.41 ns clock means setup timing is not closed. The quoted separate Fmax (2.41884 GHz) remains unreconciled as to path and clock scope.
- The published MAC RTL implements modulo-two's-complement accumulation with overflow indication; it does not saturate.
- Published SHA-256 digests and an output manifest cannot establish independent verification of absent raw archive bytes.

## Next evidence gate

Verify area/row bounds against original DEF/ODB; report the original worst setup path and time corner; publish rights-cleared raw logs/layout bundle or a verifiable link; obtain EQY proof for the custom MAC; then run both MAC variants through the same physical flow. No PPA improvements or formal proof claimed here.

## Update: 27 October 2026

Actual hosted EQY proof [run #40419385442](https://github.com/vaibhav4046/ricursive-openroad/actions/runs/40419385442) completed successfully on the default parameterization, proving all three architectural output partitions. See [FORMAL_PROOF.md](FORMAL_PROOF.md). The previous `NOT RUN` statement is historical and is no longer current. The independent GCD raw-archive audit and paired post-route MAC PPA experiment remain outstanding.
