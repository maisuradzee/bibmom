from __future__ import annotations
import json,unittest
from scripts.validate_noema005_threaded_ci_repeat import MANIFEST,SCHEMA,_assert_public_sanitization,load_snapshot,snapshot_paths,validate

class Noema005ThreadedRepeatTests(unittest.TestCase):
    def setUp(self):
        self.schema=json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.reports={key:(load_snapshot(path),record) for key,(path,record) in snapshot_paths().items()}
    def test_all_eight_frozen_reports_validate(self):
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
        keys=("run-46006107242-gil-enabled","run-46007383552-gil-enabled","run-46011557117-gil-enabled","run-46025216574-gil-enabled")
        values=[]
        for key in keys:
            doc,record=self.reports[key]
            self.assertEqual(record["runner_kernel_flavor"],"azure")
            row=next(x for x in doc["summary"]["per_method"] if x["method"]=="threaded_neumaier_state")
            values.append(row["median_speedup_vs_matching_serial"])
        self.assertLess(max(values)-min(values),0.02)
    def test_free_threaded_result_is_host_flavor_sensitive_not_universal(self):
        aws_a,ma=self.reports["run-46006107242-free-threaded"]
        azure_a,ba=self.reports["run-46007383552-free-threaded"]
        azure_b,bb=self.reports["run-46011557117-free-threaded"]
        aws_b,mb=self.reports["run-46025216574-free-threaded"]
        self.assertEqual(ma["runner_kernel_flavor"],"aws")
        self.assertEqual(mb["runner_kernel_flavor"],"aws")
        self.assertEqual(ba["runner_kernel_flavor"],"azure")
        self.assertEqual(bb["runner_kernel_flavor"],"azure")
        state=lambda doc: next(x for x in doc["summary"]["per_method"] if x["method"]=="threaded_neumaier_state")
        self.assertLess(state(aws_a)["median_speedup_vs_matching_serial"],1)
        self.assertLess(state(aws_b)["median_speedup_vs_matching_serial"],1)
        self.assertLess(abs(state(aws_a)["median_speedup_vs_matching_serial"]-state(aws_b)["median_speedup_vs_matching_serial"]),0.02)
        self.assertGreater(state(azure_a)["median_speedup_vs_matching_serial"],1)
        self.assertGreater(state(azure_b)["median_speedup_vs_matching_serial"],1)
    def test_all_snapshots_exclude_native_thread_ids(self):
        for key,(doc,_) in self.reports.items():
            with self.subTest(key=key): self.assertTrue(all("native_thread_ids_by_run" not in c for c in doc["threaded_cases"]))

    def test_third_azure_pair_has_complete_thread_evidence_and_precision(self):
        gil, gil_record = self.reports["run-46011557117-gil-enabled"]
        free, free_record = self.reports["run-46011557117-free-threaded"]
        self.assertEqual(gil_record["runner_kernel_flavor"], "azure")
        self.assertEqual(free_record["runner_kernel_flavor"], "azure")
        for doc in (gil, free):
            self.assertEqual(len(doc["threaded_cases"]), 48)
            self.assertEqual(sum(case["runs"] for case in doc["threaded_cases"]), 144)
            state = next(x for x in doc["summary"]["per_method"] if x["method"] == "threaded_neumaier_state")
            self.assertEqual((state["correctly_rounded_runs"], state["total_runs"]), (48, 48))
        gil_state = next(x for x in gil["summary"]["per_method"] if x["method"] == "threaded_neumaier_state")
        free_state = next(x for x in free["summary"]["per_method"] if x["method"] == "threaded_neumaier_state")
        self.assertLess(gil_state["median_speedup_vs_matching_serial"], 1.0)
        self.assertGreater(free_state["median_speedup_vs_matching_serial"], 1.0)


    def test_fourth_pair_reproduces_accuracy_and_cpu_concurrency_without_wall_speedup(self):
        gil,_=self.reports["run-46025216574-gil-enabled"]
        free,_=self.reports["run-46025216574-free-threaded"]
        for doc in (gil,free):
            self.assertEqual(len(doc["threaded_cases"]),48)
            self.assertEqual(sum(c["runs"] for c in doc["threaded_cases"]),144)
            state=next(x for x in doc["summary"]["per_method"] if x["method"]=="threaded_neumaier_state")
            self.assertEqual((state["correctly_rounded_runs"],state["total_runs"]),(48,48))
            self.assertLess(state["median_speedup_vs_matching_serial"],1.0)
        gil_flags=sum(sum(c["cpu_parallelism_ratio_above_1_05"]) for c in gil["threaded_cases"])
        free_flags=sum(sum(c["cpu_parallelism_ratio_above_1_05"]) for c in free["threaded_cases"])
        self.assertEqual(gil_flags,0)
        self.assertEqual(free_flags,108)
        free_ratios=[cpu/wall for c in free["threaded_cases"] for cpu,wall in zip(c["process_cpu_samples_ns"],c["wall_samples_ns"],strict=True)]
        self.assertGreater(max(free_ratios),3.0)
        self.assertLess(max(free_ratios),4.0)

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
