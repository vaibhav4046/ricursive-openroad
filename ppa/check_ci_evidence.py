#!/usr/bin/env python3
"""Validate paired ORFS evidence integrity, not PPA correctness or signoff."""
import hashlib
import pathlib
import re
import sys


def file_digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_hashes(base, errors, variant):
    sums = base / "SHA256SUMS.txt"
    if not sums.is_file() or not sums.stat().st_size:
        errors.append(f"{variant}: missing or empty SHA256SUMS.txt")
        return
    entries = {}
    for line_no, line in enumerate(sums.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (\./[^\n]+)", line)
        if not match:
            errors.append(f"{variant}: invalid checksum entry on line {line_no}")
            continue
        expected, relative = match.groups()
        target = (base / relative).resolve()
        if not target.is_relative_to(base.resolve()) or target == sums.resolve():
            errors.append(f"{variant}: unsafe or self-referential checksum entry {relative}")
            continue
        if target in entries:
            errors.append(f"{variant}: duplicate checksum entry {relative}")
            continue
        entries[target] = expected
        if not target.is_file():
            errors.append(f"{variant}: checksummed file missing {relative}")
        elif file_digest(target) != expected:
            errors.append(f"{variant}: checksum mismatch {relative}")
    actual = {p.resolve() for p in base.rglob("*") if p.is_file() and not p.is_symlink() and p.resolve() != sums.resolve()}
    for link in (p for p in base.rglob("*") if p.is_symlink()):
        errors.append(f"{variant}: symlink requires explicit resolution/review: {link.relative_to(base)}")
    if not entries:
        errors.append(f"{variant}: checksum manifest contains no valid files")
    for missing in sorted(actual - entries.keys()):
        errors.append(f"{variant}: unchecksummed file {missing.relative_to(base.resolve())}")


def check(root):
    errors = []
    manifest = root / "manifest.txt"
    if not manifest.is_file() or not manifest.stat().st_size:
        errors.append("missing or empty manifest.txt")
    else:
        contents = manifest.read_text(encoding="utf-8")
        for field in ("platform=nangate45", "clock_period_ns=", "power_activity=NO_ACTIVITY_TRACE"):
            if field not in contents:
                errors.append(f"manifest missing {field}")
        for field in ("mac_repo_sha", "orfs_sha"):
            if not re.search(rf"(?m)^{field}=[0-9a-f]{{40}}$", contents):
                errors.append(f"manifest missing valid 40-hex {field}")
    for variant in ("gold", "gate"):
        base = root / variant
        if not (base / "make.log").is_file() or not (base / "make.log").stat().st_size:
            errors.append(f"{variant}: missing or empty make.log")
        missing_paths = base / "missing_paths.txt"
        if missing_paths.exists() and missing_paths.stat().st_size:
            errors.append(f"{variant}: flow output paths were missing (see missing_paths.txt)")
        for kind in ("logs", "reports", "results"):
            directory = base / kind
            if not directory.is_dir() or not any(p.is_file() and p.stat().st_size for p in directory.rglob("*")):
                errors.append(f"{variant}: missing or empty {kind}")
        reports = list((base / "reports").rglob("*")) if (base / "reports").is_dir() else []
        logs = list((base / "logs").rglob("*")) if (base / "logs").is_dir() else []
        results = list((base / "results").rglob("*")) if (base / "results").is_dir() else []
        if not any(p.is_file() and ("route" in p.name.lower() or "route" in str(p.parent).lower()) for p in reports + logs):
            errors.append(f"{variant}: no routing report/log")
        if not any(p.is_file() and p.stat().st_size and p.suffix.lower() in (".odb", ".def") for p in results):
            errors.append(f"{variant}: no physical database/DEF (final stage not established)")
        if not any(p.is_file() and ("sta" in p.name.lower() or "tim" in p.name.lower()) for p in reports + logs):
            errors.append(f"{variant}: no timing-related report/log")
        verify_hashes(base, errors, variant)
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_ci_evidence.py /absolute/evidence-root", file=sys.stderr)
        sys.exit(2)
    problems = check(pathlib.Path(sys.argv[1]).resolve())
    if problems:
        print("EVIDENCE INCOMPLETE OR CORRUPT; NO PPA CLAIM ALLOWED:", *problems, sep="\n- ", file=sys.stderr)
        sys.exit(1)
    print("Evidence presence and checksums verified. NOT a final-route, timing, DRC, or power PASS.")
