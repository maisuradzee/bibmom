from __future__ import annotations
import hashlib,json,tempfile,zipfile
from pathlib import Path
import unittest
from scripts.reproduce_noema005_memory_bandwidth_frozen import DEFAULT_ARCHIVE,DEFAULT_PROVENANCE,verify_frozen

class FrozenMemoryBandwidthTests(unittest.TestCase):
    def test_repository_artifact_reproduces(self):
        result=verify_frozen()
        self.assertEqual(result["cases"],15)
        self.assertEqual(result["tested_head_sha"],"6720fbdf57f33d28c6d1030ccd1d399d5aec1462")

    def test_archive_digest_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"artifact.zip"
            p.write_bytes(DEFAULT_ARCHIVE.read_bytes()+b"x")
            with self.assertRaisesRegex(ValueError,"archive SHA-256"):
                verify_frozen(p,DEFAULT_PROVENANCE)

    def test_report_digest_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"artifact.zip"
            with zipfile.ZipFile(DEFAULT_ARCHIVE) as src:
                report=src.read("noema005-memory-report.json")+b" "
            with zipfile.ZipFile(p,"w",compression=zipfile.ZIP_DEFLATED) as dst:
                dst.writestr("noema005-memory-report.json",report)
            provenance=json.loads(DEFAULT_PROVENANCE.read_text(encoding="utf-8"))
            archive_sha=hashlib.sha256(p.read_bytes()).hexdigest()
            provenance["artifact_sha256"]=archive_sha
            provenance["artifact_digest"]="sha256:"+archive_sha
            provenance_path=Path(d)/"provenance.json"
            provenance_path.write_text(json.dumps(provenance),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"frozen report SHA-256"):
                verify_frozen(p,provenance_path)

    def test_exact_head_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"provenance.json"
            data=json.loads(DEFAULT_PROVENANCE.read_text(encoding="utf-8"))
            data["tested_head_sha"]="0"*40
            p.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"tested_head_sha"):
                verify_frozen(DEFAULT_ARCHIVE,p)

if __name__=="__main__":
    unittest.main()
