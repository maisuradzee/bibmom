import json
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/noema-006/public-information-gap-evidence-2026-11-27.json"
SCHEMA = ROOT / "data/noema-006/public-information-gap-evidence.schema.json"


class AquaSignalPublicInformationEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_snapshot_matches_closed_schema(self):
        jsonschema.Draft202012Validator.check_schema(self.schema)
        jsonschema.validate(self.data, self.schema)

    def test_all_fact_sources_are_resolvable(self):
        source_ids = {source["id"] for source in self.data["sources"]}
        for finding in self.data["findings"]:
            self.assertTrue(set(finding["source_ids"]).issubset(source_ids))

    def test_claim_types_remain_separate(self):
        statuses = {finding["status"] for finding in self.data["findings"]}
        self.assertTrue({"FACT", "INFERENCE", "HYPOTHESIS", "UNTESTED_IDEA"}.issubset(statuses))
        self.assertFalse(any(f["status"] == "REPRODUCED_RESULT" for f in self.data["findings"]))

    def test_2023_discrepancy_is_preserved_not_averaged(self):
        statements = " ".join(f["statement"] for f in self.data["findings"])
        self.assertIn("49.5%", statements)
        self.assertIn("44.5%", statements)
        self.assertIn("unreconciled", " ".join(self.data["limitations"]).lower())

    def test_public_defender_sample_is_not_generalized_nationally(self):
        f002 = next(f for f in self.data["findings"] if f["id"] == "F-002")
        self.assertIn("not a probability sample", f002["limitation"])

    def test_publication_design_does_not_authorize_safety_labels(self):
        requirements = " ".join(r["requirement"] for r in self.data["design_requirements"])
        privacy = " ".join(r["privacy_boundary"] for r in self.data["design_requirements"])
        self.assertIn("never convert missing data into a safe/normal status", requirements)
        self.assertIn("No autonomous declaration of safe/unsafe water", privacy)

    def test_private_and_personal_records_are_out_of_scope(self):
        forbidden_keys = {"personal_name", "phone_number", "email", "gps_track", "private_key", "household_id"}
        def walk(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    self.assertNotIn(key.lower(), forbidden_keys)
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)
        walk(self.data)


if __name__ == "__main__":
    unittest.main()
