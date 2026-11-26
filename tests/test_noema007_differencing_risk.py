from __future__ import annotations
import copy
import unittest
from noema_core.action_readiness import validate_action_readiness_record
from test_noema007_action_readiness import synthetic_record

class CrossReleaseDifferencingRiskTests(unittest.TestCase):
    def test_individually_valid_nested_aggregates_can_reveal_a_small_difference(self):
        release_a=synthetic_record()
        release_b=copy.deepcopy(release_a)
        release_a["survey"]["received_warning_n"]=80
        release_b["survey"]["received_warning_n"]=79
        validate_action_readiness_record(release_a)
        validate_action_readiness_record(release_b)
        difference=release_a["survey"]["received_warning_n"]-release_b["survey"]["received_warning_n"]
        threshold=release_a["privacy"]["minimum_cell_size"]
        self.assertEqual(difference,1)
        self.assertGreaterEqual(release_a["survey"]["received_warning_n"],threshold)
        self.assertGreaterEqual(release_b["survey"]["received_warning_n"],threshold)
        self.assertLess(difference,threshold)

    def test_schema_does_not_claim_cohort_lineage_or_release_history(self):
        record=synthetic_record()
        self.assertNotIn("cohort_id",record)
        self.assertNotIn("query_fingerprint",record)
        self.assertNotIn("release_ledger_id",record)

if __name__=="__main__":unittest.main()
