#!/usr/bin/env bash
# Reproducible LOCAL command; intentionally NOT executed by GitHub Actions.
set -euo pipefail
if [[ $# -lt 2 ]]; then
  echo "Usage: bash ppa/run_pair.sh /absolute/OpenROAD-flow-scripts /absolute/output-dir" >&2
  exit 2
fi
ORFS_ROOT="$(cd "$1" && pwd)"
OUT_DIR="$2"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FLOW_DIR="$ORFS_ROOT/flow"
EXPECTED_ORFS_COMMIT="${ORFS_EXPECTED_COMMIT:-64939f3717ad7c694199ba04cb98924b98022868}"
[[ -f "$FLOW_DIR/Makefile" ]] || { echo "OpenROAD-flow-scripts/flow/Makefile missing" >&2; exit 2; }
[[ "$(git -C "$ORFS_ROOT" rev-parse HEAD)" == "$EXPECTED_ORFS_COMMIT" ]] || {
  echo "ORFS SHA mismatch. Expected $EXPECTED_ORFS_COMMIT; got $(git -C "$ORFS_ROOT" rev-parse HEAD)" >&2; exit 2;
}
[[ -z "$(git -C "$ORFS_ROOT" status --porcelain --untracked-files=no)" ]] || {
  echo "ORFS tracked files modified; cannot guarantee a pinned flow" >&2; exit 2;
}
[[ -z "$(git -C "$REPO_ROOT" status --porcelain --untracked-files=no)" ]] || {
  echo "MAC repository tracked files modified; commit or revert before experiment" >&2; exit 2;
}
mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"
{
  echo "mac_repo_sha=$(git -C "$REPO_ROOT" rev-parse HEAD)"
  echo "orfs_sha=$EXPECTED_ORFS_COMMIT"
  echo "platform=nangate45"
  echo "clock_period_ns=5.000"
  echo "die_area=0 0 100 100"
  echo "core_area=10 10 90 90"
  echo "place_density=0.45"
  echo "power_activity=NO_ACTIVITY_TRACE; vectorless estimates are not controlled dynamic-power evidence"
  sha256sum "$REPO_ROOT/rtl/prefill_mac_tile.sv" "$REPO_ROOT/ppa/config.mk" "$REPO_ROOT/ppa/constraint.sdc" "$REPO_ROOT"/ppa/rtl/*.v
} > "$OUT_DIR/manifest.txt"
for variant in gold gate; do
  dest="$OUT_DIR/$variant"
  mkdir -p "$dest"
  design="mac_${variant}_top"
  echo "Running $variant ($design)"
  (
    cd "$FLOW_DIR"
    make DESIGN_CONFIG="$REPO_ROOT/ppa/config.mk" MAC_REPO_ROOT="$REPO_ROOT" MAC_VARIANT="$variant" FLOW_VARIANT=base clean_all
    make DESIGN_CONFIG="$REPO_ROOT/ppa/config.mk" MAC_REPO_ROOT="$REPO_ROOT" MAC_VARIANT="$variant" FLOW_VARIANT=base 2>&1 | tee "$dest/make.log"
  )
  for kind in logs reports results; do
    source_dir="$FLOW_DIR/$kind/nangate45/$design/base"
    if [[ -d "$source_dir" ]]; then
      mkdir -p "$dest/$kind"
      cp -a "$source_dir/." "$dest/$kind/"
    else
      echo "MISSING $source_dir" >> "$dest/missing_paths.txt"
    fi
  done
  (cd "$dest" && find . -type f -print0 | sort -z | xargs -0 -r sha256sum) > "$dest/SHA256SUMS.txt"
done
echo "Both ORFS invocations exited successfully. Review post-route timing/DRC and power caveats before claims."
echo "Evidence directory: $OUT_DIR"
