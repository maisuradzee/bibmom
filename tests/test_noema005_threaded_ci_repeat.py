from __future__ import annotations
import json,unittest
from scripts.validate_noema005_threaded_ci_repeat import MANIFEST,SCHEMA,_assert_public_sanitization,load_snapshot,snapshot_paths,validate

class Noema005ThreadedRepeatTests(unittest.TestCase):
    def setUp(self):
        self.schema=json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.reports={key:(load_snapshot(path),record) for key,(path,record) in snapshot_paths().items()}
    def test_all_four_frozen_reports_reproduce(self):
        for key,(doc,record) in self.reports.items():
            with self.subTest(key=key): validate(doc,self.schema,record)
    def test_compensated_state_is_correct_48_of_48_in_every_run(self):
        for key,(doc,_) in self.reports.items():
            row=next(x for x in doc["summary"]["per_method"] if x["method"]=="threaded_neumaier_state")
            with self.subTest(key=key): self.assertEqual((row["correctly_rounded_runs"],row["total_runs"]),(48,48))
    def test_naive_method_is_not_correct_for_frozen_inputs(self):
        for key,(doc,_) in self.reports.items():
            row=next(x for x in doc["summary"]["per_method"] if x["method"]=="threaded_naive_scalar")
            with self.subTest(key=key): self.assertEqual(row["correctly_rounded_runs"],0)
    def test_gil_enabled_repeats_are_close_on_same_runner_flavor(self):
        a=self.reports["run-46006107242-gil-enabled"][0]; b=self.reports["run-46007383552-gil-enabled"][0]
        ma=next(x for x in a["summary"]["per_method"] if x["method"]=="threaded_neumaier_state")
        mb=next(x for x in b["summary"]["per_method"] if x["method"]=="threaded_neumaier_state")
        self.assertLess(abs(ma["median_speedup_vs_matching_serial"]-mb["median_speedup_vs_matching_serial"]),0.01)
    def test_free_threaded_result_is_host_flavor_sensitive_not_universal(self):
        aws,am=self.reports["run-46006107242-free-threaded"]; azure,bm=self.reports["run-46007383552-free-threaded"]
        self.assertEqual(am["runner_kernel_flavor"],"aws"); self.assertEqual(bm["runner_kernel_flavor"],"azure")
        x=next(x for x in aws["summary"]["per_method"] if x["method"]=="threaded_neumaier_state")
        y=next(x for x in azure["summary"]["per_method"] if x["method"]=="threaded_neumaier_state")
        self.assertLess(x["median_speedup_vs_matching_serial"],1); self.assertGreater(y["median_speedup_vs_matching_serial"],1)
    def test_all_snapshots_exclude_native_thread_ids(self):
        for key,(doc,_) in self.reports.items():
            with self.subTest(key=key): self.assertTrue(all("native_thread_ids_by_run" not in c for c in doc["threaded_cases"]))

    def test_public_boundary_rejects_identity_keys_at_every_nesting_depth(self):
        unsafe_documents = (
            {"protocol": {"nested": {"hostname": "private-host"}}},
            {"inputs": [{"details": {"native_thread_ids_by_run": [[101, 102]]}}]},
            {"serial_baselines": [{"runner_id": "runner-1"}]},
            {"summary": {"kernel_release": "private-build-string"}},
            {"manifest": {"records": [{"device_id": "device-1"}]}},
        )
        for document in unsafe_documents:
            with self.subTest(document=document), self.assertRaises(ValueError):
                _assert_public_sanitization(document)

    def test_public_boundary_allows_coarse_non_identity_environment_metadata(self):
        _assert_public_sanitization({
            "environment": {
                "machine_architecture": "x86_64",
                "cpu_count_os": 4,
                "cpu_affinity_count": 4,
                "python_version": "3.14.4",
            },
            "source": {
                "workflow_run_id": 123,
                "artifact_id": 456,
                "artifact_name": "noema005-threaded-gil-enabled.zip",
            },
        })


    def test_validator_rejects_identity_keys_in_unclosed_nested_objects(self):
        doc, record = next(iter(self.reports.values()))
        mutations = (
            lambda candidate: candidate["protocol"].update({"runner-id": "private-runner"}),
            lambda candidate: candidate["inputs"][0].update({"details": {"hostname": "private-host"}}),
            lambda candidate: candidate["serial_baselines"][0].update({"native_thread_ids": [101, 102]}),
            lambda candidate: candidate["summary"].update({"kernel_release": "private-build"}),
        )
        for mutate in mutations:
            candidate = json.loads(json.dumps(doc))
            mutate(candidate)
            with self.assertRaises(ValueError):
                validate(candidate, self.schema, record)

    def test_manifest_and_all_records_pass_recursive_public_boundary(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        _assert_public_sanitization(manifest)
        for record in manifest["records"]:
            _assert_public_sanitization(record)

if __name__=="__main__": unittest.main()
