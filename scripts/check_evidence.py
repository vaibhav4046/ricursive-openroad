#!/usr/bin/env python3
"""Fail-closed minimal artifact check for an ORFS Nangate45/GCD reference run.

Does NOT certify formal correctness, DRC, LVS, timing closure, or tapeout readiness.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

REQUIRED = {
    'routed_db': 'artifacts/results/5_2_route.odb',
    'route_db': 'artifacts/results/5_route.odb',
    'gds': 'artifacts/results/6_final.gds',
    'def': 'artifacts/results/6_final.def',
    'netlist': 'artifacts/results/6_final.v',
    'sdc': 'artifacts/results/6_final.sdc',
    'final_report_log': 'artifacts/logs/6_report.log',
    'build_log': 'build.log',
    'design_config': 'artifacts/inputs/config.mk',
    'design_rtl': 'artifacts/inputs/gcd.v',
    'design_constraints': 'artifacts/inputs/constraint.sdc',
}
SHA40 = re.compile(r'[0-9a-f]{40}\Z')
IMAGE_ID = re.compile(r'sha256:[0-9a-f]{64}\Z')

def filehash(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while data := f.read(2**20):
            h.update(data)
    return h.hexdigest()

def inspect_run(root):
    root = Path(root)
    errors = []
    manifest_path = root / 'run_manifest.json'
    if not manifest_path.is_file():
        errors.append('MISSING run_manifest.json')
        manifest = {}
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            errors.append(f'INVALID run_manifest.json: {exc}')
            manifest = {}
    if manifest.get('platform') != 'nangate45' or manifest.get('design') != 'gcd':
        errors.append('WRONG design/platform; expected nangate45/gcd')
    if not SHA40.fullmatch(str(manifest.get('orfs_commit',''))):
        errors.append('MISSING/INVALID pinned ORFS Git SHA')
    if not IMAGE_ID.fullmatch(str(manifest.get('docker_image_id',''))):
        errors.append('MISSING/INVALID pinned Docker image ID')
    if manifest.get('make_exit_code') != 0:
        errors.append('NO recorded successful make exit code')
    hashes = {}
    sizes = {}
    for name, rel in REQUIRED.items():
        p = root / rel
        if not p.is_file() or p.stat().st_size == 0:
            errors.append(f'MISSING/EMPTY {name}: {rel}')
            continue
        hashes[rel] = filehash(p)
        sizes[rel] = p.stat().st_size
    gds = root / REQUIRED['gds']
    if gds.is_file():
        with gds.open('rb') as f:
            if f.read(4) != b'\x00\x06\x00\x02':
                errors.append('GDS STREAM HEADER INCORRECT (expected length=6, HEADER record)')
        if gds.stat().st_size < 128:
            errors.append('GDS suspiciously small (<128 bytes)')
    # This is an artifact and provenance gate only. Do not infer zero-DRC etc.
    ok = not errors
    return {
        'status': 'REFERENCE_GDS_ARTIFACTS_PRESENT_NOT_SIGNOFF' if ok else 'INCOMPLETE_OR_INVALID',
        'artifact_checks_passed': ok,
        'design': 'gcd', 'platform': 'nangate45',
        'source_commit': manifest.get('orfs_commit'),
        'image_id': manifest.get('docker_image_id'),
        'files_sha256': hashes, 'files_bytes': sizes,
        'errors': errors,
        'explicit_nonclaims': [
            'NOT formal equivalence',
            'NOT DRC/LVS independently verified',
            'NOT signoff or taped-out silicon',
            'NOT a custom MAC or AI accelerator',
            'NOT a PPA improvement claim',
        ],
    }

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('run_directory')
    ns = ap.parse_args()
    d = Path(ns.run_directory)
    result = inspect_run(d)
    print(json.dumps(result, indent=2))
    (d / 'validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return 0 if result['artifact_checks_passed'] else 1

if __name__ == '__main__':
    sys.exit(main())
