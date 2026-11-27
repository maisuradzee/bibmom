import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/noema-006/georgian-drinking-water-operational-controls-2026-11-28.json"
SCHEMA = ROOT / "data/noema-006/georgian-drinking-water-operational-controls-2026-11-28.schema.json"


class GeorgianDrinkingWaterOperationalControlsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(DATA.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_record_matches_closed_schema(self):
        jsonschema.Draft202012Validator.check_schema(self.schema)
        jsonschema.validate(self.record, self.schema)

    def test_sampling_points_are_distinct_from_raw_groundwater(self):
        points = {item["supply_mode"]: item for item in self.record["sampling_points"]}
        self.assertEqual(set(points), {
            "distribution_system", "tank_or_cistern",
            "bottled_or_container", "food_production",
        })
        self.assertIn("tap normally used", points["distribution_system"]["sampling_point"])
        self.assertIn("outlet", points["tank_or_cistern"]["sampling_point"])
        self.assertIn("filling point", points["bottled_or_container"]["sampling_point"])
        self.assertFalse(self.record["scope"]["raw_groundwater_automatic_compliance"])

    def test_supplier_monitoring_recording_and_response_duties_are_explicit(self):
        duties = self.record["supplier_obligations"]
        self.assertTrue(duties["monitoring_and_compliance_control_required"])
        self.assertTrue(duties["result_recording_required"])
        self.assertTrue(duties["information_accessibility_required"])
        actions = " ".join(duties["non_compliance_actions"]).lower()
        for term in ("inform", "investigate", "restrict", "health"):
            self.assertIn(term, actions)

    def test_emergency_and_repeat_sampling_triggers_are_separate(self):
        emergency = self.record["emergency_monitoring"]
        repeat = self.record["repeat_sampling"]
        self.assertEqual(set(emergency["triggers"]), {"flood", "emergency"})
        self.assertIn("enhanced", emergency["action"].lower())
        self.assertEqual(len(repeat["trigger"]), 2)
        self.assertIn("nitrates", repeat["action"].lower())
        self.assertIn("nitrites", repeat["action"].lower())
        self.assertIn("chlorides", repeat["action"].lower())

    def test_routine_analytes_keep_nitrate_and_nitrite_separate(self):
        analytes = {item.lower() for item in self.record["routine_monitoring"]["chemical"]}
        self.assertTrue({"ammonia", "nitrate", "nitrite", "chlorides"}.issubset(analytes))

    def test_independent_lab_requirement_is_not_claimed_as_actual_test(self):
        requirement = self.record["independent_testing"]["requirement"].lower()
        self.assertIn("accredited independent laboratory", requirement)
        self.assertEqual(self.record["evidence_status"], "FACT")
        self.assertFalse(self.record["privacy"]["raw_sample_records_included"])

    def test_transition_and_legal_review_limit_are_explicit(self):
        note = self.record["transition_note"]
        self.assertIn("2027-09-01", note)
        limits = " ".join(self.record["interpretation_limits"]).lower()
        self.assertIn("not legal advice", limits)
        self.assertIn("legal review", limits)


if __name__ == "__main__":
    unittest.main()
