# Formal Equivalence & PPA Comparison: NOT RUN Declaration

## 1. Formal Equivalence Proof (YosysHQ EQY)
- **Status:** `NOT RUN` / `BLOCKED`
- **Tool Required:** YosysHQ EQY (`eqy`) + SMT Solver (`z3`)
- **Blocker Reason:** The `eqy` binary is not installed in the Windows/WSL2 host environment (`which eqy` exited with code 1).
- **Integrity Rule:** In accordance with rigorous chip design verification standards, dynamic simulation pass across 3,009 vectors does **NOT** constitute formal mathematical proof. The project explicitly refuses to report a false pass for formal verification.

## 2. Modified MAC Physical Design Flow (RTL-to-GDS PPA)
- **Status:** `NOT RUN` / `BLOCKED`
- **Blocker Reason:** Gating criterion: Running physical design comparison on modified RTL without formal equivalence proof closure risks comparing unverified silicon logic.
- **Integrity Rule:** No area, timing, or power savings are claimed for the operand-isolated candidate over the golden reference without actual physical design measurements.
