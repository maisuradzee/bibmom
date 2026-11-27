from __future__ import annotations
import json,unittest
from scripts.validate_noema005_threaded_ci_repeat import MANIFEST,SCHEMA,load_snapshot,snapshot_paths,validate

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
if __name__=="__main__": unittest.main()
