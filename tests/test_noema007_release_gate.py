from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from noema_core.noema007_release_gate import (
    AggregateReleaseGateError,
    preflight_aggregate_batch,
    release_scope_sha256,
)

ROOT = Path(__file__).resolve().parents[1]


def synthetic_plan():
    plan = {
        "schema_version": 1,
        "release_batch_id": "batch_20261127_01",
        "protected_population_family_id": "family_georgia_01",
        "source_snapshot_sha256": "1" * 64,
        "query_manifest_sha256": "2" * 64,
        "cohort_manifest_sha256": "3" * 64,
        "output_manifest_sha256": "4" * 64,
        "privacy_unit": "person",
        "privacy_unit_rationale": "The same resident may contribute across multiple events and windows.",
        "contribution_bound": 3,
        "adjacency": "add_remove",
        "differential_privacy_claimed": False,
        "approval": {
            "data_controller_approved": True,
            "privacy_reviewer_approved": True,
            "approval_reference": "SYNTHETIC-REVIEW-001",
            "policy_version": "NOEMA-007-DRAFT-1",
            "approved_scope_sha256": "0" * 64,
        },
    }
    plan["approval"]["approved_scope_sha256"] = release_scope_sha256(plan)
    return plan


class AggregateReleaseGateTests(unittest.TestCase):
    def test_empty_ledger_is_only_ready_for_atomic_commit_not_published(self):
        result = preflight_aggregate_batch(synthetic_plan(), [])
        self.assertEqual(result["decision"], "READY_FOR_ATOMIC_LEDGER_COMMIT")
        self.assertNotIn("published", result)
        self.assertEqual(result["ledger_entry"]["protected_population_family_id"], "family_georgia_01")

    def test_exact_retry_is_idempotent(self):
        plan = synthetic_plan()
        first = preflight_aggregate_batch(plan, [])
        retry = preflight_aggregate_batch(plan, [first["ledger_entry"]])
        self.assertEqual(retry["decision"], "IDEMPOTENT_RETRY")
        self.assertEqual(retry["ledger_entry"], first["ledger_entry"])

    def test_second_batch_for_same_population_family_is_blocked(self):
        first = preflight_aggregate_batch(synthetic_plan(), [])
        second = synthetic_plan()
        second["release_batch_id"] = "batch_20261127_02"
        second["source_snapshot_sha256"] = "5" * 64
        second["output_manifest_sha256"] = "6" * 64
        second["approval"]["approved_scope_sha256"] = release_scope_sha256(second)
        with self.assertRaisesRegex(AggregateReleaseGateError, "second batch is blocked"):
            preflight_aggregate_batch(second, [first["ledger_entry"]])

    def test_approval_is_bound_to_exact_query_and_cohort(self):
        plan = synthetic_plan()
        plan["cohort_manifest_sha256"] = "7" * 64
        with self.assertRaisesRegex(AggregateReleaseGateError, "not bound"):
            preflight_aggregate_batch(plan, [])

    def test_unapproved_release_fails_closed(self):
        plan = synthetic_plan()
        plan["approval"]["privacy_reviewer_approved"] = False
        plan["approval"]["approved_scope_sha256"] = release_scope_sha256(plan)
        with self.assertRaisesRegex(AggregateReleaseGateError, "independent privacy-review"):
            preflight_aggregate_batch(plan, [])

    def test_differential_privacy_claim_is_rejected_until_mechanism_exists(self):
        plan = synthetic_plan()
        plan["differential_privacy_claimed"] = True
        plan["approval"]["approved_scope_sha256"] = release_scope_sha256(plan)
        with self.assertRaisesRegex(AggregateReleaseGateError, "no DP mechanism/accountant"):
            preflight_aggregate_batch(plan, [])

    def test_event_level_privacy_requires_explicit_rationale(self):
        plan = synthetic_plan()
        plan["privacy_unit"] = "event"
        plan["privacy_unit_rationale"] = ""
        plan["approval"]["approved_scope_sha256"] = release_scope_sha256(plan)
        with self.assertRaisesRegex(AggregateReleaseGateError, "privacy_unit_rationale"):
            preflight_aggregate_batch(plan, [])

    def test_missing_or_untrusted_ledger_fails_closed(self):
        with self.assertRaisesRegex(AggregateReleaseGateError, "complete trusted release ledger"):
            preflight_aggregate_batch(synthetic_plan(), None)

    def test_malformed_ledger_fails_closed(self):
        malformed = {
            "release_batch_id": "batch_20261127_02",
            "protected_population_family_id": "family_georgia_01",
            "plan_sha256": "9" * 64,
            "secret": "no",
        }
        with self.assertRaisesRegex(AggregateReleaseGateError, "unapproved fields"):
            preflight_aggregate_batch(synthetic_plan(), [malformed])

    def test_duplicate_ledger_entries_fail_closed_before_retry(self):
        first = preflight_aggregate_batch(synthetic_plan(), [])
        duplicate_family = {
            "release_batch_id": "batch_20261127_02",
            "protected_population_family_id": first["ledger_entry"]["protected_population_family_id"],
            "plan_sha256": "a" * 64,
        }
        with self.assertRaisesRegex(AggregateReleaseGateError, "duplicate protected population family"):
            preflight_aggregate_batch(synthetic_plan(), [first["ledger_entry"], duplicate_family])

        duplicate_batch = {
            "release_batch_id": first["ledger_entry"]["release_batch_id"],
            "protected_population_family_id": "family_other_01",
            "plan_sha256": "b" * 64,
        }
        with self.assertRaisesRegex(AggregateReleaseGateError, "duplicate release_batch_id"):
            preflight_aggregate_batch(synthetic_plan(), [first["ledger_entry"], duplicate_batch])

    def test_release_batch_id_cannot_be_reused_for_another_family(self):
        plan = synthetic_plan()
        ledger = [{
            "release_batch_id": plan["release_batch_id"],
            "protected_population_family_id": "family_other_01",
            "plan_sha256": "8" * 64,
        }]
        with self.assertRaisesRegex(AggregateReleaseGateError, "different plan or family"):
            preflight_aggregate_batch(plan, ledger)

    def test_schema_is_closed_and_dp_claim_is_forbidden(self):
        schema = json.loads((ROOT / "data/noema-007/release-batch.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIs(schema["additionalProperties"], False)
        self.assertIs(schema["properties"]["differential_privacy_claimed"]["const"], False)
        self.assertIs(schema["properties"]["approval"]["additionalProperties"], False)


if __name__ == "__main__":
    unittest.main()
