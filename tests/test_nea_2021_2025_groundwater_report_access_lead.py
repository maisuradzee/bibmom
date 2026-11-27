import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/noema-006/nea-2021-2025-groundwater-report-access-lead.json"
SCHEMA = ROOT / "data/noema-006/nea-2021-2025-groundwater-report-access-lead.schema.json"


class NeaGroundwaterReportAccessLeadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(DATA.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_metadata_record_matches_closed_schema(self):
        jsonschema.Draft202012Validator.check_schema(self.schema)
        jsonschema.validate(self.record, self.schema)

    def test_archive_is_metadata_only_and_unverified(self):
        source = self.record["source"]
        self.assertEqual(source["archive_format"], "RAR")
        self.assertEqual(source["archive_retrieval_status"], "not_retrieved")
        self.assertIsNone(source["archive_sha256"])
        self.assertFalse(source["archive_contents_inspected"])
        self.assertFalse(self.record["report_scope"]["archive_contents_inspected"])

    def test_sample_and_site_denominators_remain_unknown(self):
        scope = self.record["report_scope"]
        for field in ("sample_count", "station_count", "analyte_denominators",
                      "result_rows", "site_coordinates", "time_series_rows"):
            self.assertIsNone(scope[field])

    def test_statutory_deadline_is_not_marked_complete(self):
        regulatory = self.record["regulatory_context"]
        self.assertEqual(regulatory["law_date"], "2026-06-24")
        self.assertEqual(regulatory["groundwater_nitrate_risk_zone_identification_due"], "2027-09-01")
        self.assertEqual(regulatory["relevant_methodology_approval_due"], "2027-09-01")
        self.assertFalse(regulatory["approval_or_completion_verified"])

    def test_no_personal_or_raw_records_are_included(self):
        self.assertEqual(self.record["privacy"], {
            "personal_data_included": False,
            "business_identifiers_included": False,
            "exact_site_coordinates_included": False,
            "raw_sample_records_included": False,
            "restricted_archive_bytes_included": False,
        })


if __name__ == "__main__":
    unittest.main()
