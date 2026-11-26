from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from scripts.reproduce_noema005_memory_bandwidth_frozen import DEFAULT_PROVENANCE,DEFAULT_REPORT,verify_frozen

class FrozenMemoryBandwidthTests(unittest.TestCase):
    def test_repository_snapshot_reproduces(self):
        result=verify_frozen()
        self.assertEqual(result["cases"],15)
        self.assertEqual(result["tested_head_sha"],"6720fbdf57f33d28c6d1030ccd1d399d5aec1462")
    def test_report_digest_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            report=Path(directory)/"report.json"
            report.write_bytes(DEFAULT_REPORT.read_bytes()+b" ")
            with self.assertRaisesRegex(ValueError,"report SHA-256"):
                verify_frozen(report,DEFAULT_PROVENANCE)
    def test_tested_head_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            provenance=Path(directory)/"provenance.json"
            data=json.loads(DEFAULT_PROVENANCE.read_text(encoding="utf-8"))
            data["tested_head_sha"]="0"*40
            provenance.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"tested_head_sha"):
                verify_frozen(DEFAULT_REPORT,provenance)
    def test_artifact_digest_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            provenance=Path(directory)/"provenance.json"
            data=json.loads(DEFAULT_PROVENANCE.read_text(encoding="utf-8"))
            data["artifact_digest"]="sha256:"+"0"*64
            provenance.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"artifact digest"):
                verify_frozen(DEFAULT_REPORT,provenance)

if __name__=="__main__":unittest.main()
