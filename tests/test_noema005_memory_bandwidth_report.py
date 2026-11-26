from __future__ import annotations
import unittest
from scripts.validate_noema005_memory_bandwidth_report import validate_report
def fixture():
    repeat=8;size=repeat*3*8;serial={"serial_naive":1000.0,"serial_long_double":1200.0,"serial_neumaier":1500.0};cases=[]
    for method,wall in serial.items():
        cases.append({"method":method,"requested_workers":1,"actual_threads_min":1,"actual_threads_max":1,"correct_runs":0 if method=="serial_naive" else 3,"runs":3,"median_wall_ns":wall,"median_process_cpu_ns":wall,"speedup_vs_matching_serial":1.0,"effective_read_gb_s":size/wall,"bytes_read_per_run":size,"wall_samples_ns":[wall-1,wall,wall+1],"process_cpu_samples_ns":[wall-1,wall,wall+1]})
    for w in (1,2,4,8):
        for m,b,c in (("openmp_naive_partials","serial_naive",0),("openmp_long_double","serial_long_double",3),("openmp_neumaier_state","serial_neumaier",3)):
            wall=serial[b]/w;cpu=wall*w
            cases.append({"method":m,"requested_workers":w,"actual_threads_min":w,"actual_threads_max":w,"correct_runs":c,"runs":3,"median_wall_ns":wall,"median_process_cpu_ns":cpu,"speedup_vs_matching_serial":serial[b]/wall,"effective_read_gb_s":size/wall,"bytes_read_per_run":size,"wall_samples_ns":[wall-1,wall,wall+1],"process_cpu_samples_ns":[cpu-1,cpu,cpu+1]})
    return {"study_id":"NOEMA-2026-005","experiment_id":"NOEMA-2026-005-MEMORY-001","status":"synthetic_memory_backed_reduction","input":{"pattern":["2^53","1","-2^53"],"repeat_count":repeat,"elements":repeat*3,"bytes":size,"exact_sum":repeat},"workers":[1,2,4,8],"warmups":1,"repetitions":3,"cases_expected":15,"cases":cases,"provenance":{"source_sha256":"a"*64,"tested_head_sha":"b"*40}}
class MemoryBackedReportTests(unittest.TestCase):
    def test_valid_fixture(self):validate_report(fixture())
    def test_incomplete_matrix_rejected(self):
        r=fixture();r["cases"].pop()
        with self.assertRaisesRegex(ValueError,"case matrix"):validate_report(r)
    def test_naive_accuracy_claim_rejected(self):
        r=fixture();r["cases"][0]["correct_runs"]=1
        with self.assertRaisesRegex(ValueError,"naive method"):validate_report(r)
    def test_compensated_failure_rejected(self):
        r=fixture();r["cases"][1]["correct_runs"]=2
        with self.assertRaisesRegex(ValueError,"failed frozen"):validate_report(r)
    def test_input_byte_count_rejected(self):
        r=fixture();r["cases"][0]["bytes_read_per_run"]+=8
        with self.assertRaisesRegex(ValueError,"bytes_read_per_run"):validate_report(r)
    def test_raw_median_reproduced(self):
        r=fixture();r["cases"][0]["median_wall_ns"]+=20
        with self.assertRaisesRegex(ValueError,"wall median"):validate_report(r)
    def test_speedup_uses_matching_baseline(self):
        r=fixture();r["cases"][3]["speedup_vs_matching_serial"]=99.0
        with self.assertRaisesRegex(ValueError,"speedup does not reproduce"):validate_report(r)
    def test_exact_head_sha_required(self):
        r=fixture();r["provenance"].pop("tested_head_sha")
        with self.assertRaisesRegex(ValueError,"exact tested head SHA"):validate_report(r)
    def test_source_digest_required(self):
        r=fixture();r["provenance"].pop("source_sha256")
        with self.assertRaisesRegex(ValueError,"source SHA-256"):validate_report(r)
if __name__=="__main__":unittest.main()
