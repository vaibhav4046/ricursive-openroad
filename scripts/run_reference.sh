#!/usr/bin/env bash
# Requires: WSL2 Ubuntu (or Linux), Git, Docker Desktop Docker CLI, and an existing
# CLEAN checkout of official OpenROAD-flow-scripts (ORFS_HOME).
# Usage: ORFS_HOME="$HOME/chip-lab/OpenROAD-flow-scripts" bash scripts/run_reference.sh
# This script does NOT run on Windows PowerShell or without an available Docker daemon.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for dep in git docker python3 xauth tee cp find; do
  command -v "$dep" >/dev/null 2>&1 || { echo "ERROR: $dep is unavailable" >&2; exit 2; }
done
: "${ORFS_HOME:?Set ORFS_HOME to the absolute directory of a CLEAN ORFS git checkout}"
ORFS_HOME="$(realpath "$ORFS_HOME")"
[[ -d "$ORFS_HOME/.git" || -f "$ORFS_HOME/.git" ]] || { echo 'ERROR: not an ORFS git checkout' >&2; exit 2; }
[[ -f "$ORFS_HOME/flow/util/docker_shell" && -f "$ORFS_HOME/flow/designs/nangate45/gcd/config.mk" ]] || { echo 'ERROR: ORFS files missing' >&2; exit 2; }
[[ -z "$(git -C "$ORFS_HOME" status --porcelain --untracked-files=no)" ]] || { echo 'ERROR: tracked ORFS worktree modified' >&2; exit 2; }
ORFS_SHA="$(git -C "$ORFS_HOME" rev-parse HEAD)"
[[ "$ORFS_SHA" =~ ^[a-f0-9]{40}$ ]] || { echo 'ERROR: invalid Git commit hash' >&2; exit 2; }
if [[ -n "${ORFS_EXPECTED_SHA:-}" && "$ORFS_SHA" != "$ORFS_EXPECTED_SHA" ]]; then
   echo "ERROR: Git SHA mismatch; expected $ORFS_EXPECTED_SHA, got $ORFS_SHA" >&2; exit 2
fi
docker info >/dev/null || { echo 'ERROR: Docker daemon unavailable; start Docker Desktop / enable WSL integration' >&2; exit 2; }
IMAGE_REF="${ORFS_IMAGE_REF:-openroad/orfs:latest}"
if [[ "${PULL_IMAGE:-1}" == 1 ]]; then
    docker pull "$IMAGE_REF"
fi
IMAGE_ID="$(docker image inspect "$IMAGE_REF" --format '{{.Id}}')" || { echo 'ERROR: Docker image not found' >&2; exit 2; }
[[ "$IMAGE_ID" =~ ^sha256:[a-f0-9]{64}$ ]] || { echo 'ERROR: unrecognized image ID' >&2; exit 2; }
REL='nangate45/gcd/base'
# Reject stale data. We must not accidentally certify an earlier build.
for d in "$ORFS_HOME/flow/results/$REL" "$ORFS_HOME/flow/logs/$REL" "$ORFS_HOME/flow/reports/$REL"; do
  [[ ! -e "$d" ]] || { echo "ERROR: prior build directory present: $d ; use a fresh clone" >&2; exit 2; }
done
OUT="$ROOT/evidence/gcd_$(date -u +%Y%m%dT%H%M%SZ)_${ORFS_SHA:0:12}"
mkdir -p "$OUT/artifacts"/{results,logs,reports,inputs}
echo "$ORFS_SHA" > "$OUT/orfs_commit.txt"
printf '%s\n' "$IMAGE_ID" > "$OUT/docker_image_id.txt"
cp "$ORFS_HOME/flow/designs/nangate45/gcd/config.mk" "$OUT/artifacts/inputs/config.mk"
cp "$ORFS_HOME/flow/designs/nangate45/gcd/constraint.sdc" "$OUT/artifacts/inputs/constraint.sdc"
cp "$ORFS_HOME/flow/designs/src/gcd/gcd.v" "$OUT/artifacts/inputs/gcd.v"
# Note: this intentionally does not run formal equivalence of our separate MAC RTL.
cd "$ORFS_HOME/flow"
printf 'Starting official ORFS nangate45/gcd with Git SHA %s and Docker image ID %s\n' "$ORFS_SHA" "$IMAGE_ID"
# Pipefail ensures a failing make cannot be hidden by tee's success.
OR_IMAGE="$IMAGE_ID" util/docker_shell make DESIGN_CONFIG=./designs/nangate45/gcd/config.mk 2>&1 | tee "$OUT/build.log"
# Stage 5_2_route.odb is made only after detailed routing in current ORFS.
for stage in 5_2_route.odb 5_route.odb 6_final.gds 6_final.def 6_final.v 6_final.sdc; do
    test -s "$ORFS_HOME/flow/results/$REL/$stage" || { echo "ERROR: routing/final artifact missing: $stage" >&2; exit 3; }
    cp "$ORFS_HOME/flow/results/$REL/$stage" "$OUT/artifacts/results/$stage"
done
[[ -s "$ORFS_HOME/flow/logs/$REL/6_report.log" ]] || { echo 'ERROR: missing final-report log' >&2; exit 3; }
# Save ALL stage logs/reports, including JSON and tool warnings, without inventing metric values.
cp -a "$ORFS_HOME/flow/logs/$REL/." "$OUT/artifacts/logs/"
if [[ -d "$ORFS_HOME/flow/reports/$REL" ]]; then cp -a "$ORFS_HOME/flow/reports/$REL/." "$OUT/artifacts/reports/"; fi
# Only here is an exit_code=0 recorded. Lack of this record fails validation.
export OUT ORFS_SHA IMAGE_ID
python3 - <<'PY'
import json, os, pathlib, datetime
out = pathlib.Path(os.environ['OUT'])
manifest = {
    'schema_version': 1,
    'experiment': 'OFFICIAL_REFERENCE_FLOW',
    'design': 'gcd', 'platform': 'nangate45', 'variant': 'base',
    'orfs_commit': os.environ['ORFS_SHA'],
    'docker_image_id': os.environ['IMAGE_ID'],
    'make_command': 'OR_IMAGE=<recorded Docker image ID> util/docker_shell make DESIGN_CONFIG=./designs/nangate45/gcd/config.mk',
    'make_exit_code': 0,
    'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'disclaimer': 'Successful reference flow does not establish DRC/LVS signoff, MAC verification or PPA optimisation.'
}
(out / 'run_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
PY
python3 "$ROOT/scripts/check_evidence.py" "$OUT" | tee "$OUT/check_console.log"
printf '\nArtifact gate completed; evidence directory: %s\n' "$OUT"
printf 'Do not claim DRC-clean, timing met, equivalence, PPA improvement, or tapeout without separate checks.\n'
