#!/usr/bin/env python3
"""Fail closed on missing ORFS physical evidence; do not infer timing closure."""
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
errors = []
if not (root / "manifest.txt").is_file():
    errors.append("missing manifest.txt")
for variant in ("gold", "gate"):
    base = root / variant
    for name in ("make.log", "SHA256SUMS.txt"):
        if not (base / name).is_file() or not (base / name).stat().st_size:
            errors.append(f"{variant}: missing or empty {name}")
    for kind in ("logs", "reports", "results"):
        directory = base / kind
        if not directory.is_dir() or not any(p.is_file() and p.stat().st_size for p in directory.rglob("*")):
            errors.append(f"{variant}: missing or empty {kind}")
    reports = list((base / "reports").rglob("*")) if (base / "reports").exists() else []
    logs = list((base / "logs").rglob("*")) if (base / "logs").exists() else []
    results = list((base / "results").rglob("*")) if (base / "results").exists() else []
    if not any(p.is_file() and ("route" in p.name.lower() or "route" in str(p.parent).lower()) for p in reports + logs):
        errors.append(f"{variant}: no routing report/log")
    if not any(p.is_file() and p.suffix.lower() in (".odb", ".def") for p in results):
        errors.append(f"{variant}: no routed database/DEF (stage must be checked manually)")
    if not any(p.is_file() and ("sta" in p.name.lower() or "tim" in p.name.lower()) for p in reports + logs):
        errors.append(f"{variant}: no timing-related report/log")
if errors:
    print("EVIDENCE INCOMPLETE; NO PPA CLAIM ALLOWED:", *errors, sep="\n- ", file=sys.stderr)
    sys.exit(1)
print("Evidence file-presence checks passed. NOT a timing/DRC/power PASS.")
