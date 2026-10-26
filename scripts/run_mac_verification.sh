#!/usr/bin/env bash
# Run from v2/ after installing Icarus Verilog and YosysHQ EQY.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p outputs
for tool in iverilog vvp eqy; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      echo "ERROR: $tool unavailable; evidence remains NOT_RUN" >&2; exit 2
    fi
done
iverilog -g2012 -s tb_prefill_mac_equiv -o outputs/prefill_sim \
    rtl/prefill_mac_tile.sv tests/tb_prefill_mac_equiv.sv
vvp outputs/prefill_sim | tee outputs/prefill_sim.log
# A passing simulation is not a formal proof. EQY must complete too.
eqy -f formal/prefill_mac.eqy | tee outputs/prefill_eqy.log
echo 'Simulation and EQY commands completed. Inspect tool status and proof coverage before claims.'
