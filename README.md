# Ricursive OpenROAD Reference Flow & Arithmetic Verification Evidence

[![Artifact Verification](https://img.shields.io/badge/ORFS%20Artifacts-Raw%20Archive%20Unavailable-yellow.svg)](#evidence-manifest--checksums)
[![Dynamic Simulation](https://img.shields.io/badge/Simulation-3%2C009%20Vectors%20PASS-brightgreen.svg)](#arithmetic-verification)
[![Formal Proof](https://img.shields.io/badge/Formal%20(EQY)-PASS%20(default%20parameters)-brightgreen.svg)](#formal-verification-status)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Evidence repository documenting the OpenROAD Flow Scripts (ORFS) reference flow (`nangate45/gcd`), layout metrics, and custom INT8 signed Multiply-Accumulate (MAC) verification.

---

## 1. Executive Summary

1. **Physical Design Reference:** Completed the official OpenROAD Flow Scripts RTL-to-GDS reference flow on `nangate45/gcd` under Docker with zero DRC and zero antenna violations.
2. **Timing Analysis:** Setup WNS is $-0.163\text{ ns}$ (TNS $-6.995\text{ ns}$, 50 violating endpoints) at an aggressive $0.41\text{ ns}$ target period; Hold WNS is $+0.0896\text{ ns}$ (zero hold violations).
3. **Area and count audit:** The reported cell taxonomy sums to 674 functional cells plus 326 fill/tap cells, exactly 1,000 instances. Functional area from the named categories is 894.29 square microns; the previously labelled 906.53 square microns includes 12.24 square microns of tap cells. Exact geometric core bounds and utilization definitions require native DEF/report verification.
4. **Arithmetic Dynamic Verification:** The custom signed-INT8 prefill MAC tile (`rtl/prefill_mac_tile.sv`) passed 3,009 dynamic verification vectors in Icarus Verilog (`iverilog`), covering overflow and modulo wraparound, reset recovery, and 3,000 pseudorandom transaction cycles.
5. **Formal Verification:** Hosted YosysHQ EQY formally proved the three externally observable MAC outputs equivalent for the default parameters (DATA_W=8, ACC_W=24), after a 3,009-vector dynamic simulation pass. See [GitHub Actions run #40419385442](https://github.com/vaibhav4046/ricursive-openroad/actions/runs/40419385442), [artifact #12696644253](https://github.com/vaibhav4046/ricursive-openroad/actions/runs/40419385442/artifacts/12696644253) and [proof provenance](docs/FORMAL_PROOF.md). **Custom MAC post-route PPA has NOT RUN.**

---

## 2. Verified Physical Design Metrics (`nangate45/gcd`)

Historical values attributed to OpenROAD stage 6 reports (`artifacts/logs/6_report.json` and `artifacts/reports/6_finish.rpt`), which are **not currently available as public raw files for independent inspection**:

| Metric Category | Parameter | Value | Notes |
|---|---|---|---|
| **Area** | Die Area (reported) | 1,278.42 um² | Verify native DEF boundary; the rounded dimensions shown earlier do not exactly reproduce the figure. |
| | Geometric Core Area | not independently established | The 1,076.77 um² category sum is **not** geometric core area; native DEF/ODB inspection is required. |
| | Functional Cell Area (category sum) | 894.29 um² | 674 functional instances; excludes 280 filler and 46 tap instances. |
| | Physical Support Cell Area | $182.48\ \mu\text{m}^2$ | 280 Fill cells ($170.24\ \mu\text{m}^2$) + 46 Tap cells ($12.24\ \mu\text{m}^2$) |
| | Historical Utilization Claim | 84.19% (unreconciled) | Previous calculation treated 12.24 um² of tap cells as active logic; no validated core geometry or native tool utilization is available. |
| **Instance Count** | Total Placed Instances | **1,000** | Functional cells (674) + fill/tap cells (326) |
| | Sequential Logic | 35 | D-type flip-flops ($158.27\ \mu\text{m}^2$) |
| | Combinational Logic | 377 | Multi-input gates ($512.32\ \mu\text{m}^2$) |
| | Inverters & Buffers | 262 | CTS buffers (6), CTS inv (2), Resizer buffers (167), Resizer inv (1), Inverters (86) |
| **Timing** | Clock Target Period | $0.41\text{ ns}$ | $2.439\text{ GHz}$ target in `constraint.sdc` |
| | Separately Reported Fmax | 2.41884 GHz | **Not timing closure**: setup WNS is negative; reconcile clock/path scope before quoting an achieved frequency. |
| | Setup WNS / TNS | **$-0.163\text{ ns}$ / $-6.995\text{ ns}$** | 50 violating endpoints (unpipelined 45nm datapath) |
| | Hold WNS / TNS | **$+0.0896\text{ ns}$ / $0.000\text{ ns}$** | **PASS** — Zero hold violations |
| | Clock Skew | $1.05\text{ ps}$ | Balanced clock distribution via TritonCTS |
| **Power & IR Drop** | Total Power | $6.02\text{ mW}$ | Internal: $3.30\text{ mW}$, Switching: $2.70\text{ mW}$, Leakage: $0.024\text{ mW}$ |
| | VDD Max IR Drop | $1.05\%$ ($1.15\times 10^{-2}\text{ V}$) | Flow estimate, not foundry signoff |
| | VSS Max IR Drop | $0.62\%$ ($6.83\times 10^{-3}\text{ V}$) | Flow estimate, not foundry signoff |
| **Integrity** | Detailed Route DRCs | **0 violations** | Verified via `5_route_drc.rpt` (0 bytes) |
| | Antenna Violations | **0 violations** | Verified via `drt_antennas.log` (0 bytes) |

Detailed analyses: [`docs/AREA_TERMINOLOGY.md`](docs/AREA_TERMINOLOGY.md) and [`docs/TIMING_ANALYSIS.md`](docs/TIMING_ANALYSIS.md).

---

## 3. Arithmetic Verification (Custom Signed INT8 MAC)

The custom signed-INT8 prefill MAC tile provides both a cycle-preserving golden reference (`prefill_mac_tile_gold`) and an operand-isolated candidate (`prefill_mac_tile_gate`):

```verilog
// Operand isolation gating: forces multiplier inputs to 0 when idle or zero-product
wire zero_product = (act_in == 0) || (wgt_in == 0);
wire drive_multiplier = valid_in && !zero_product;
wire signed [DATA_W-1:0] gated_act = drive_multiplier ? act_in : {DATA_W{1'b0}};
wire signed [DATA_W-1:0] gated_wgt = drive_multiplier ? wgt_in : {DATA_W{1'b0}};
```

### Running the Dynamic Simulation
```bash
# Requires Icarus Verilog (iverilog + vvp)
mkdir -p outputs
iverilog -g2012 -s tb_prefill_mac_equiv -o outputs/prefill_sim rtl/prefill_mac_tile.sv tests/tb_prefill_mac_equiv.sv
vvp outputs/prefill_sim
```

**Result:**
```
DYNAMIC_EQUIVALENCE_PASS vectors=3009 (formal proof still required)
```

---

## 4. Formal Verification Status

- **Status:** **PASS for the default RTL parameters only** (DATA_W=8, ACC_W=24), using EQY and the Z3-backed SBY strategy. The three proof partitions are `acc_out`, `overflow_flag` and `valid_out`; no architectural output was left unproven.
- **Public proof:** [GitHub Actions run #40419385442](https://github.com/vaibhav4046/ricursive-openroad/actions/runs/40419385442), [raw CI artifact #12696644253](https://github.com/vaibhav4046/ricursive-openroad/actions/runs/40419385442/artifacts/12696644253), [provenance and limitations](docs/FORMAL_PROOF.md).
- **Scope:** This proves the stated output-equivalence relation under the formal model for this parameterization. It does not prove parameter-general equivalence, physical timing closure, switching-power savings, DRC/LVS signoff, or silicon correctness.
- **Custom MAC physical design comparison:** **NOT RUN**. A reproducible paired ORFS experiment scaffold is provided in [`ppa/`](ppa/README.md). No measured MAC area, timing or power improvements are claimed.

---

## 5. Evidence Manifest & Checksums

The historical GCD reference archive was reportedly generated locally, but **its raw GDS and logs are not published in this repository**. The public MAC proof artifact is a different bundle and does not authenticate the historical GCD archive. A public hash list does not independently authenticate unavailable bytes. Original archive:
- **Archive Size:** `1,547,429 bytes`
- **Archive SHA-256:** `AAE30B530E3CF1F35ED90DE4AF1530244B53E08A4F20AC9205C8B89FC017E7D0`

Verified checksums of constituent deliverables ([`evidence/validation.json`](evidence/validation.json)):

| Artifact | Size | SHA-256 Digest |
|---|---|---|
| `artifacts/results/5_2_route.odb` | 1,262,457 B | `2f0d6495b87f969e4ab38dbb37c4fc5814dd856cd4183e1537343cf4fe7d1f13` |
| `artifacts/results/5_route.odb` | 1,328,180 B | `007c9d3e74e7fd67034a00d994779a1382985c3491143d31e1a9967c78fcf0b2` |
| `artifacts/results/6_final.gds` | 582,814 B | `133ed23dcbee31f5e950a4e65f7c73a3f69b84b02d01b6898d7c714ce860bff5` |
| `artifacts/results/6_final.def` | 430,404 B | `0cf53a1116e3aeaa4cf1f4f63309c415e9147949e2057e8c348d49dfb2454b74` |
| `artifacts/results/6_final.v` | 53,774 B | `326191b1dcb29edc1e3e9fb64028dcac39ebbdd94b85c7175b722635528ea7bc` |
| `artifacts/results/6_final.sdc` | 6,137 B | `112a077b756cada0fab67b2061733207a9cd7ac99b3e98454cabcad5aec7aa77` |
| `artifacts/logs/6_report.log` | 3,827 B | `3d14eeb98357a39c74f57d26cc40460f2c745308ceede0aa5168b02dc899054c` |
| `build.log` | 172,635 B | `1124de6a5259058c1b8ae4939dd97bfbc66cd408d8b27ed461a74adcf083a892` |

### Validating Provenance
```bash
python scripts/check_evidence.py <extracted_run_directory>
python -m unittest discover -s tests -v
```

---

## 6. PDK & IP Licensing Statement

All physical design flows utilize the open-source FreePDK45 / Nangate45 Open Cell Library from the public OpenROAD-flow-scripts project. This repository contains zero proprietary foundry intellectual property, zero closed PDK standard cell libraries, and zero commercial cell models.


### Documentation audit disclosure

The original raw build archive was not available to this GitHub documentation audit. The counts and area figures above are internally recalculated from the publicly listed cell categories, not from a new physical-design run. The machine-readable evidence/metrics.json has been corrected to distinguish recalculated category sums from unverified historical area/utilization/Fmax claims. Original GCD raw bytes are still missing. See [independent review findings](docs/REVIEW_FINDINGS.md).
