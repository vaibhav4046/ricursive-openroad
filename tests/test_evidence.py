"""Unit tests using SYNTHETIC fixtures; never treated as physical-design results."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import json

SPEC = importlib.util.spec_from_file_location('check_evidence', Path(__file__).parents[1] / 'scripts' / 'check_evidence.py')
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class EvidenceUnitTests(unittest.TestCase):
    def setUp(self):
        self.dirctx = tempfile.TemporaryDirectory()
        self.root = Path(self.dirctx.name)
    def tearDown(self):
        self.dirctx.cleanup()
    def make_fixture(self):
        (self.root / 'run_manifest.json').write_text(json.dumps({
            'platform': 'nangate45', 'design': 'gcd',
            'orfs_commit': 'a' * 40, 'docker_image_id': 'sha256:' + 'b' * 64,
            'make_exit_code': 0,
        }))
        for name, rel in mod.REQUIRED.items():
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            if name == 'gds':
                p.write_bytes(b'\x00\x06\x00\x02' + b'\x00' * 512)
            else:
                p.write_bytes(b'FAKE_DATA_UNIT_TEST_ONLY')
    def test_empty_directory_fails(self):
        self.assertFalse(mod.inspect_run(self.root)['artifact_checks_passed'])
    def test_fixture_shape_checks_only_not_signoff(self):
        self.make_fixture()
        obj = mod.inspect_run(self.root)
        self.assertTrue(obj['artifact_checks_passed'])
        self.assertEqual(obj['status'], 'REFERENCE_GDS_ARTIFACTS_PRESENT_NOT_SIGNOFF')
        self.assertIn('NOT DRC/LVS independently verified', obj['explicit_nonclaims'])
    def test_bad_gds_signature_rejected(self):
        self.make_fixture()
        (self.root / mod.REQUIRED['gds']).write_bytes(b'Not a GDS stream' * 100)
        self.assertFalse(mod.inspect_run(self.root)['artifact_checks_passed'])
    def test_no_route_stage_rejected(self):
        self.make_fixture()
        (self.root / mod.REQUIRED['routed_db']).unlink()
        self.assertFalse(mod.inspect_run(self.root)['artifact_checks_passed'])
    def test_missing_image_pin_rejected(self):
        self.make_fixture()
        path = self.root / 'run_manifest.json'
        m = json.loads(path.read_text())
        m['docker_image_id'] = 'openroad/orfs:latest'
        path.write_text(json.dumps(m))
        self.assertFalse(mod.inspect_run(self.root)['artifact_checks_passed'])
    def test_nonzero_build_exit_rejected(self):
        self.make_fixture()
        path = self.root / 'run_manifest.json'
        m = json.loads(path.read_text())
        m['make_exit_code'] = 1
        path.write_text(json.dumps(m))
        self.assertFalse(mod.inspect_run(self.root)['artifact_checks_passed'])
if __name__ == '__main__':
    unittest.main()
