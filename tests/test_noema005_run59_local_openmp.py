from __future__ import annotations
import base64, copy, gzip, json, unittest, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from verify_noema005_run59_local_openmp import verify_report, validate_raw_layout_metrics
RAW=ROOT/"data/noema-005/raw/run59-local-openmp-2026-11-28.jsonl.gz.b64"

class Run59OpenMPTests(unittest.TestCase):
 def raw_layout(self,index=0):
  compressed=base64.b64decode(RAW.read_text(encoding="ascii").strip(),validate=True)
  rows=gzip.decompress(compressed).decode("utf-8").splitlines()
  return copy.deepcopy(json.loads(rows[index]))
 def test_frozen_raw_artifact_hashes_schema_and_summary_reproduce(self):
  self.assertEqual(verify_report(),{"valid":True,"layouts":2,"cases":48,"measured_runs":960})
 def test_neumaier_full_state_is_correct_in_every_worker_cell(self):
  for index in (0,1):
   cells=[c for c in self.raw_layout(index)["cases"] if c["method"]=="openmp_neumaier_full_state"]
   self.assertEqual({c["requested_workers"] for c in cells},{1,2,4,5,8})
   self.assertTrue(all(c["correct_runs"]==20 for c in cells))
   self.assertTrue(all(c["actual_threads_min"]==c["requested_workers"] for c in cells))
 def test_grouped_long_double_partials_fail_this_fixture(self):
  cells=[c for c in self.raw_layout(1)["cases"] if c["method"]=="openmp_long_double_partials"]
  self.assertEqual({c["correct_runs"] for c in cells},{0})
 def test_corrupted_speedup_is_rejected(self):
  layout=self.raw_layout()
  cell=next(c for c in layout["cases"] if c["method"]=="openmp_neumaier_full_state" and c["requested_workers"]==4)
  cell["speedup_vs_serial_method"]+=0.1
  with self.assertRaisesRegex(ValueError,"speedup_vs_serial_method"):
   validate_raw_layout_metrics(layout)
 def test_missing_timing_sample_is_rejected(self):
  layout=self.raw_layout()
  cell=next(c for c in layout["cases"] if c["method"]=="openmp_neumaier_full_state" and c["requested_workers"]==4)
  cell["wall_samples_ns"].pop()
  with self.assertRaisesRegex(ValueError,"wall-time sample count"):
   validate_raw_layout_metrics(layout)
 def test_duplicate_method_worker_cell_is_rejected(self):
  layout=self.raw_layout()
  layout["cases"].append(copy.deepcopy(layout["cases"][0]))
  with self.assertRaisesRegex(ValueError,"case count"):
   validate_raw_layout_metrics(layout)

if __name__=="__main__":
 unittest.main()
