from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "noema-006" / "nea-2021-2025-report-procurement-access-lead-2026-11-27.json"
SCHEMA = ROOT / "data" / "noema-006" / "nea-2021-2025-report-procurement-access-lead-2026-11-27.schema.json"


class AquaSignalNeaProcurementAccessLeadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(DATA.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_schema(self):
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema, format_checker=FormatChecker()).iter_errors(self.record))
        self.assertEqual(errors, [])

    def test_contract_metadata_is_exact_and_source_bounded(self):
        self.assertEqual(self.record["tender_id"], "NAT260019441")
        self.assertEqual(self.record["contract_number"], "T-100801")
        self.assertEqual(self.record["contract_signed_date"], "2026-10-09")
        self.assertEqual(self.record["contract_value_gel_excluding_vat"], 4200)
        self.assertEqual(len(self.record["deliverables"]), 4)

    def test_electronic_pdf_is_a_contract_deliverable_but_not_public_access_proof(self):
        pdf = next(item for item in self.record["deliverables"] if item["kind"] == "final_electronic_pdf")
        self.assertEqual(pdf["format"], "PDF")
        self.assertTrue(pdf["interactive_table_of_contents_required"])
        self.assertFalse(pdf["public_access_confirmed"])
        self.assertIn("this does not establish", self.record["interpretation"])

    def test_cd_contents_and_delivery_completion_are_not_inferred(self):
        cd = next(item for item in self.record["deliverables"] if item["kind"] == "cd_media")
        self.assertEqual(cd["copies"], 50)
        self.assertFalse(cd["public_access_confirmed"])
        self.assertIn("this does not establish", self.record["interpretation"])

    def test_nea_announcement_confirms_report_scope_but_not_sample_level_payload(self):
        announcement = self.record["official_announcement"]
        self.assertTrue(announcement["report_prepared"])
        self.assertEqual(announcement["publication_date"], "2026-11-26")
        self.assertTrue(any("quantitative and qualitative" in item for item in announcement["reported_scope"]))
        self.assertTrue(any("digitization" in item for item in announcement["reported_scope"]))
        self.assertFalse(announcement["sample_level_results_in_announcement"])
        self.assertFalse(announcement["station_level_payload_in_announcement"])

    def test_rar_archive_is_explicitly_not_retrieved_or_hashed(self):
        archive = self.record["archive_retrieval"]
        self.assertFalse(archive["retrieved"])
        self.assertFalse(archive["inspected"])
        self.assertIsNone(archive["sha256"])
        self.assertEqual(archive["evidence_status"], "NOT_RETRIEVED")

    def test_contract_delivery_window_and_nea_prepared_notice_do_not_prove_acceptance(self):
        delivery = self.record["delivery_status"]
        self.assertEqual(delivery["contract_signed_date"], "2026-10-09")
        self.assertEqual(delivery["contract_valid_through"], "2026-12-31")
        self.assertEqual(delivery["nea_announcement_says_report_prepared_on"], "2026-11-26")
        self.assertFalse(delivery["formal_acceptance_or_delivery_act_observed"])
        self.assertFalse(delivery["public_access_confirmed"])

    def test_public_record_excludes_personal_contact_and_bank_data(self):
        serialized = json.dumps(self.record, ensure_ascii=False).lower()
        for forbidden in ('"email":', '"phone":', '"bank_account":', '"iban":', '"signature":', '"personal_id":'):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
