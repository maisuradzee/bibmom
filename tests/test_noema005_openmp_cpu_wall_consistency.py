from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator
from scripts.audit_noema005_openmp_cpu_wall_consistency import audit_reports, parse_cpu_list

ROOT=Path(__file__).resolve().parents[1]
RAW_PATH=ROOT/"data/noema-005/native-openmp-raw-report-2026-11-26.json"
SUMMARY_PATH=ROOT/"data/noema-005/native-openmp-ci-summary-2026-11-26.json"
EXPECTED_PATH=ROOT/"data/noema-005/native-openmp-cpu-wall-consistency-audit-2026-11-27.json"
SCHEMA_PATH=ROOT/"data/noema-005/native-openmp-cpu-wall-consistency-audit.schema.json"

class Noema005CpuWallConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=json.loads(RAW_PATH.read_text(encoding="utf-8"))
        cls.summary=json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        cls.expected=json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))
        cls.schema=json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def audit(self,raw=None):
        return audit_reports(self.raw if raw is None else raw,self.summary,
            self.expected["source_raw_git_blob_sha"],self.expected["source_summary_git_blob_sha"])

    def test_cpu_list_parser(self):
        self.assertEqual(parse_cpu_list("0-3"),4)
        self.assertEqual(parse_cpu_list("0-1,4,6-7"),6)
        self.assertIsNone(parse_cpu_list(None))
        with self.assertRaises(ValueError):
            parse_cpu_list("0-3,x")

    def test_frozen_audit_reproduces(self):
        self.assertEqual(self.audit(),self.expected)

    def test_audit_schema_is_valid(self):
        Draft202012Validator.check_schema(self.schema)
        self.assertEqual(list(Draft202012Validator(self.schema).iter_errors(self.expected)),[])

    def test_five_openmp_cases_have_cpu_time_ceiling_outliers(self):
        result=self.audit()
        self.assertEqual(result["flagged_case_count"],5)
        self.assertEqual(result["outlier_measurement_count"],9)
        self.assertEqual(result["max_observed_process_cpu_to_wall_ratio"],13.287713)

    def test_neumaier_accuracy_is_separate_from_timing_anomaly(self):
        accuracy=self.audit()["accuracy"]
        self.assertEqual(accuracy["openmp_neumaier_correct_runs"],40)
        self.assertEqual(accuracy["openmp_neumaier_expected_runs"],40)
        self.assertEqual(accuracy["openmp_naive_correct_runs"],0)
        self.assertEqual(accuracy["openmp_naive_expected_runs"],40)

    def test_missing_sample_is_rejected(self):
        raw=copy.deepcopy(self.raw)
        raw["cases"][4]["wall_samples_ns"].pop()
        with self.assertRaises(ValueError):
            self.audit(raw)

if __name__=="__main__":
    unittest.main()
