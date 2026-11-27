from __future__ import annotations
import json,unittest
from scripts.validate_noema005_threaded_ci_repeat import SNAPSHOTS,SCHEMA,load,validate

class Noema005ThreadedRepeatTests(unittest.TestCase):
    def test_frozen_reports_reproduce(self):
        schema=json.loads(SCHEMA.read_text(encoding="utf-8"))
        for mode,path in SNAPSHOTS.items():
            with self.subTest(mode=mode): validate(load(path),schema,mode)
    def test_compensated_state_is_correct_48_of_48(self):
        for path in SNAPSHOTS.values():
            d=load(path); row=next(x for x in d["summary"]["per_method"] if x["method"]=="threaded_neumaier_state")
            self.assertEqual((row["correctly_rounded_runs"],row["total_runs"]),(48,48))
    def test_naive_is_not_correct_for_frozen_inputs(self):
        for path in SNAPSHOTS.values():
            d=load(path); row=next(x for x in d["summary"]["per_method"] if x["method"]=="threaded_naive_scalar")
            self.assertEqual(row["correctly_rounded_runs"],0)
    def test_no_configuration_has_wall_speedup(self):
        for path in SNAPSHOTS.values():
            self.assertTrue(all(c["speedup_vs_matching_serial_baseline"]<1 for c in load(path)["threaded_cases"]))
    def test_free_threaded_four_workers_use_cpu_concurrently_but_not_faster(self):
        d=load(SNAPSHOTS["free-threaded"]); row=next(x for x in d["summary"]["per_worker"] if x["worker_count"]==4)
        self.assertGreater(row["median_process_cpu_wall_ratio"],3.5)
        self.assertLess(row["median_speedup_vs_matching_serial"],1)
if __name__=="__main__": unittest.main()
