from __future__ import annotations

import copy
import unittest

from noema_core import (
    MissionConfigurationError,
    autonomy_decision,
    load_mission,
    source_access_decision,
    validate_mission_config,
)


class NoemaMissionCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mission = load_mission()

    def test_mission_configuration_is_valid(self) -> None:
        validate_mission_config(self.mission)
        self.assertEqual(self.mission["identity"]["name"], "NOEMA")
        self.assertGreaterEqual(len(self.mission["innovation_cycle"]), 5)
        self.assertIn("without ongoing human assistance", self.mission["operational_independence"]["target"])

    def test_public_source_can_be_retrieved_without_granting_reuse(self) -> None:
        decision = source_access_decision("public")
        self.assertTrue(decision.allowed)
        self.assertFalse(decision.reuse_allowed)

    def test_public_source_reuse_requires_separate_permission(self) -> None:
        decision = source_access_decision(
            "public",
            permission_verified=True,
            reuse_permitted=True,
        )
        self.assertTrue(decision.allowed)
        self.assertTrue(decision.reuse_allowed)

    def test_licensed_source_requires_verified_permission(self) -> None:
        denied = source_access_decision("licensed")
        allowed = source_access_decision("licensed", permission_verified=True)
        self.assertFalse(denied.allowed)
        self.assertTrue(allowed.allowed)
        self.assertFalse(allowed.reuse_allowed)

    def test_user_authorized_source_requires_verified_permission(self) -> None:
        self.assertFalse(source_access_decision("user_authorized").allowed)
        self.assertTrue(
            source_access_decision(
                "user_authorized",
                permission_verified=True,
            ).allowed
        )

    def test_restricted_unknown_and_unauthorized_sources_are_denied(self) -> None:
        for source_class in ("restricted", "unknown", "unauthorized", "made_up"):
            with self.subTest(source_class=source_class):
                decision = source_access_decision(source_class, permission_verified=True, reuse_permitted=True)
                self.assertFalse(decision.allowed)
                self.assertFalse(decision.reuse_allowed)

    def test_internal_analysis_is_autonomous(self) -> None:
        decision = autonomy_decision("analyze_data")
        self.assertEqual(decision.mode, "autonomous")

    def test_internal_job_orchestration_is_autonomous(self) -> None:
        for action in (
            "enqueue_internal_jobs",
            "record_job_state",
            "recover_expired_jobs",
            "verify_job_audit_log",
        ):
            with self.subTest(action=action):
                self.assertEqual(autonomy_decision(action).mode, "autonomous")

    def test_interval_scheduler_operations_are_autonomous(self) -> None:
        for action in (
            "create_interval_schedules",
            "run_due_schedules",
            "recover_pending_schedule_fires",
            "apply_schedule_misfire_policy",
        ):
            with self.subTest(action=action):
                self.assertEqual(autonomy_decision(action).mode, "autonomous")

    def test_internal_workflow_orchestration_is_autonomous(self) -> None:
        for action in (
            "create_internal_workflows",
            "advance_workflows",
            "validate_workflow_dependencies",
            "block_failed_workflow_branches",
        ):
            with self.subTest(action=action):
                self.assertEqual(autonomy_decision(action).mode, "autonomous")

    def test_preliminary_publication_requires_all_quality_gates(self) -> None:
        self.assertEqual(autonomy_decision("publish_preliminary").mode, "blocked")
        self.assertEqual(
            autonomy_decision("publish_preliminary", all_quality_gates_passed=True).mode,
            "autonomous",
        )

    def test_final_publication_and_high_impact_actions_require_review(self) -> None:
        for action in ("publish_final", "make_high_impact_decision", "execute_financial_transaction"):
            with self.subTest(action=action):
                self.assertEqual(autonomy_decision(action).mode, "review_required")

    def test_unknown_actions_are_blocked(self) -> None:
        self.assertEqual(autonomy_decision("invent_new_permission").mode, "blocked")

    def test_invalid_configuration_with_overlapping_action_classes_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.mission)
        invalid["autonomy"]["review_required_actions"].append("analyze_data")
        with self.assertRaises(MissionConfigurationError):
            validate_mission_config(invalid)


if __name__ == "__main__":
    unittest.main()
