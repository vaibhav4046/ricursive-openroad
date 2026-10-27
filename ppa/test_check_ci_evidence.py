#!/usr/bin/env python3
"""Synthetic fixture tests only; not OpenROAD execution or physical signoff."""
import hashlib
import pathlib
import tempfile
import unittest
from check_ci_evidence import check


def write(path, content=b"fixture"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def checksums(base):
    lines = []
    for path in sorted(p for p in base.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  ./{path.relative_to(base).as_posix()}")
    write(base / "SHA256SUMS.txt", ("\n".join(lines) + "\n").encode())


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        write(self.root / "manifest.txt", b"mac_repo_sha=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\norfs_sha=64939f3717ad7c694199ba04cb98924b98022868\nplatform=nangate45\nclock_period_ns=5\npower_activity=NO_ACTIVITY_TRACE\n")
        for variant in ("gold", "gate"):
            base = self.root / variant
            write(base / "make.log")
            write(base / "logs" / "5_route.log")
            write(base / "reports" / "6_final_timing.rpt")
            write(base / "results" / "6_final.odb")
            write(base / "results" / "6_final.def")
            write(base / "results" / "6_final.sdc")
            write(base / "reports" / "5_route_drc.rpt", b"")
            write(base / "reports" / "6_finish.rpt")
            checksums(base)

    def test_complete_synthetic_fixture_only_passes_integrity(self):
        self.assertEqual(check(self.root), [])

    def test_missing_variant_rejected(self):
        for p in (self.root / "gate").rglob("*"):
            if p.is_file():
                p.unlink()
        self.assertTrue(check(self.root))

    def test_missing_paths_marker_rejected(self):
        write(self.root / "gold" / "missing_paths.txt", b"MISSING results")
        checksums(self.root / "gold")
        self.assertTrue(any("paths were missing" in e for e in check(self.root)))

    def test_corrupted_file_rejected(self):
        write(self.root / "gold" / "results" / "6_final.odb", b"tampered")
        self.assertTrue(any("checksum mismatch" in e for e in check(self.root)))

    def test_unchecksummed_file_rejected(self):
        write(self.root / "gate" / "logs" / "extra.log")
        self.assertTrue(any("unchecksummed file" in e for e in check(self.root)))

    def test_missing_timing_rejected(self):
        (self.root / "gate" / "reports" / "6_final_timing.rpt").unlink()
        checksums(self.root / "gate")
        self.assertTrue(any("no timing" in e for e in check(self.root)))

    def test_missing_final_def_rejected(self):
        (self.root / "gate" / "results" / "6_final.def").unlink()
        checksums(self.root / "gate")
        self.assertTrue(any("final physical artifact 6_final.def" in e for e in check(self.root)))

    def test_missing_drc_report_rejected(self):
        (self.root / "gold" / "reports" / "5_route_drc.rpt").unlink()
        checksums(self.root / "gold")
        self.assertTrue(any("detailed-route DRC report" in e for e in check(self.root)))

    def test_missing_final_report_rejected(self):
        (self.root / "gate" / "reports" / "6_finish.rpt").unlink()
        checksums(self.root / "gate")
        self.assertTrue(any("final timing/area/power reporting stage" in e for e in check(self.root)))

    def test_self_referential_manifest_rejected(self):
        sums = self.root / "gold" / "SHA256SUMS.txt"
        sums.write_text(sums.read_text() + "0" * 64 + "  ./SHA256SUMS.txt\n")
        self.assertTrue(any("self-referential" in e for e in check(self.root)))

    def test_traversal_entry_rejected(self):
        sums = self.root / "gold" / "SHA256SUMS.txt"
        sums.write_text(sums.read_text() + "0" * 64 + "  ./../../outside\n")
        self.assertTrue(any("unsafe" in e for e in check(self.root)))


if __name__ == "__main__":
    unittest.main()
