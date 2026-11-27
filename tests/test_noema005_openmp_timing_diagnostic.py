from __future__ import annotations
import copy
import unittest
from pathlib import Path
from scripts.run_noema005_openmp_timing_diagnostic import parse_cpu_list, parse_cpu_max, validate_report
from scripts.reproduce_noema005_openmp_timing_diagnostic import load_frozen_report

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "data/noema-005/openmp-timing-diagnostic.schema.json"

def sample_report_v2():
    report = sample_report()
    report["schema_version"] = 2
    env = report["environment"]
    env["cgroup_cpu_quota_ancestor_levels"] = 2
    env["cgroup_cpu_quota_constrained_levels"] = [0, 1]
    env["cgroup_cpu_quota_chain_complete"] = True
    report["runs"][0]["threads"][0]["thread_cgroup_matches_process"] = True
    report["runs"][0]["thread_cgroup_mismatch_count"] = 0
    report["runs"][0]["thread_cgroup_unverified_count"] = 0
    report["summary"]["thread_cgroup_mismatch_count"] = 0
    report["summary"]["thread_cgroup_unverified_count"] = 0
    return report

def sample_report():
    thread = {"thread_index":0,"cpu_ns":80,"rusage_thread_ns":80000,"affinity_cpu_count":2,"affinity_cpus":"0,1","cpu_start":0,"cpu_end":1,"checksum":1.25}
    run = {"requested_workers":1,"actual_threads":1,"repetition":1,"work_items":1000,"wall_ns":100,"process_cpu_ns":180,
           "omp_wall_ns":100,"process_cpu_wall_ratio":1.8,"thread_cpu_sum_ns":80,"checksum":1.25,"threads":[thread],
           "observed_affinity_union_cpus":[0,1],"observed_affinity_union_count":2,"effective_cpu_capacity":2.0,
           "cpu_wall_anomaly_threshold":2.25,"cpu_wall_anomaly":False,"thread_cpu_sum_to_process_cpu_ratio":round(80/180,9)}
    return {"schema_version":1,"study_id":"NOEMA-2026-005","experiment_id":"NOEMA-2026-005-OPENMP-TIMING-DIAG-001",
            "status":"completed_no_cpu_wall_anomalies","captured_at_utc":"2026-11-27T06:00:00Z","source_sha256":"a"*64,
            "compiler_version":"gcc (Ubuntu) 13.3.0","compile_flags":["-std=c11","-O2","-fopenmp"],
            "parameters":{"workers":[1],"repetitions":1,"warmups":1,"work_items":1000},
            "environment":{"cgroup_v2_detected":True,"cgroup_membership_resolved":True,"cgroup_cpuset_cpus_effective":[0,1],
             "cgroup_cpu_max":"200000 100000","cgroup_cpu_quota_cores":2.0,"process_affinity_cpus":[0,1],"process_affinity_count":2,
             "cpu_stat_before":{"usage_usec":100},"cpu_stat_after":{"usage_usec":200},"cpu_stat_delta":{"usage_usec":100},
             "machine_architecture":"x86_64","kernel_release":"6.x","python_version":"3.12",
             "openmp_environment":{"OMP_NUM_THREADS":None,"OMP_DYNAMIC":None,"OMP_PROC_BIND":None,"OMP_PLACES":None}},
            "runs":[run],"summary":{"run_count":1,"cpu_wall_anomaly_count":0,"max_process_cpu_wall_ratio":1.8,
             "per_worker":[{"requested_workers":1,"median_process_cpu_wall_ratio":1.8,"anomaly_count":0}]},
            "limitations":["Synthetic test fixture; not an experimental result."]}

class Noema005OpenMPTimingDiagnosticTests(unittest.TestCase):
    def test_cpu_list_parser(self):
        self.assertEqual(parse_cpu_list("0-3,6,8-9"),[0,1,2,3,6,8,9])
        self.assertEqual(parse_cpu_list(None),[])
        with self.assertRaises(ValueError): parse_cpu_list("0-3,x")
    def test_cpu_quota_parser(self):
        self.assertEqual(parse_cpu_max("400000 100000"),4.0)
        self.assertIsNone(parse_cpu_max("max 100000"))
        with self.assertRaises(ValueError): parse_cpu_max("400000")
    def test_schema_and_derived_metrics_validate(self):
        validate_report(sample_report(),SCHEMA)

    def test_v2_ancestor_quota_and_thread_cgroup_evidence_validate(self):
        validate_report(sample_report_v2(), SCHEMA)

    def test_v2_withholds_capacity_when_worker_cgroup_differs(self):
        report = sample_report_v2()
        report["runs"][0]["threads"][0]["thread_cgroup_matches_process"] = False
        report["runs"][0]["effective_cpu_capacity"] = None
        report["runs"][0]["cpu_wall_anomaly_threshold"] = None
        report["runs"][0]["cpu_wall_anomaly"] = False
        report["runs"][0]["thread_cgroup_mismatch_count"] = 1
        report["summary"]["thread_cgroup_mismatch_count"] = 1
        validate_report(report, SCHEMA)

    def test_v2_withholds_capacity_when_quota_ancestor_chain_is_incomplete(self):
        report = sample_report_v2()
        report["environment"]["cgroup_cpu_quota_chain_complete"] = False
        report["runs"][0]["effective_cpu_capacity"] = None
        report["runs"][0]["cpu_wall_anomaly_threshold"] = None
        report["runs"][0]["cpu_wall_anomaly"] = False
        validate_report(report, SCHEMA)

    def test_v2_rejects_capacity_claim_with_incomplete_quota_chain(self):
        report = sample_report_v2()
        report["environment"]["cgroup_cpu_quota_chain_complete"] = False
        with self.assertRaises(ValueError):
            validate_report(report, SCHEMA)
    def test_cpu_wall_anomaly_is_retained_not_suppressed(self):
        report=sample_report()
        report["runs"][0]["process_cpu_ns"]=400
        report["runs"][0]["process_cpu_wall_ratio"]=4.0
        report["runs"][0]["cpu_wall_anomaly"]=True
        report["summary"]["cpu_wall_anomaly_count"]=1
        report["summary"]["max_process_cpu_wall_ratio"]=4.0
        validate_report(report,SCHEMA)
    def test_missing_worker_sample_is_rejected(self):
        report=sample_report()
        report["runs"][0]["threads"]=[]
        with self.assertRaises(Exception): validate_report(report,SCHEMA)
    def test_host_identity_fields_are_rejected(self):
        report=sample_report()
        report["environment"]["hostname"]="not-public"
        with self.assertRaises(ValueError): validate_report(report,SCHEMA)

    def test_frozen_source_archive_matches_original_report_source(self):
        import hashlib, json
        from scripts.reproduce_noema005_openmp_timing_diagnostic import FROZEN_SOURCE, MANIFEST
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256(FROZEN_SOURCE.read_bytes()).hexdigest(), manifest["source_sha256"])

    def test_frozen_hosted_artifact_reproduces(self):
        report = load_frozen_report()
        self.assertEqual(len(report["runs"]), 80)
        self.assertEqual(report["summary"]["cpu_wall_anomaly_count"], 0)
        self.assertEqual(report["summary"]["max_process_cpu_wall_ratio"], 4.008956678)

    def test_frozen_worker_counts_and_medians(self):
        report = load_frozen_report()
        self.assertEqual([entry["requested_workers"] for entry in report["summary"]["per_worker"]], [1, 2, 4, 8])
        self.assertEqual([entry["median_process_cpu_wall_ratio"] for entry in report["summary"]["per_worker"]],
                         [0.999966709, 2.000455849, 4.001551167, 3.946946747])

if __name__=="__main__":
    unittest.main()
