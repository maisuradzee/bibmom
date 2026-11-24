from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / "database" / "noema_supabase_schema_proposal.sql"


class NoemaDatabaseProposalContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sql = SQL_PATH.read_text(encoding="utf-8").lower()

    def test_proposal_is_explicitly_not_executed(self) -> None:
        self.assertIn("design draft only. not executed.", self.sql)

    def test_every_exposed_table_has_rls_enabled(self) -> None:
        for table in (
            "research_entries",
            "research_sources",
            "research_artifacts",
            "research_reviews",
            "research_comments",
        ):
            with self.subTest(table=table):
                self.assertIn(
                    f"alter table public.{table} enable row level security;",
                    self.sql,
                )

    def test_private_automation_log_is_not_granted_to_client_roles(self) -> None:
        self.assertIn("create schema if not exists noema_private", self.sql)
        self.assertIn("alter table noema_private.automation_runs enable row level security;", self.sql)
        self.assertIn(
            "revoke all on noema_private.automation_runs from public, anon, authenticated;",
            self.sql,
        )
        self.assertIn("grant all on noema_private.automation_runs to service_role;", self.sql)

    def test_client_authorization_uses_trusted_app_metadata(self) -> None:
        self.assertIn("app_metadata", self.sql)
        self.assertNotIn("user_metadata", self.sql)

    def test_anonymous_role_has_no_review_record_access(self) -> None:
        self.assertIn("grant select on public.research_reviews to authenticated;", self.sql)
        self.assertNotIn(
            "grant select on public.research_reviews to anon, authenticated;",
            self.sql,
        )

    def test_publication_requires_approved_review_of_exact_version(self) -> None:
        self.assertIn("noema_private.require_approved_review_before_publish()", self.sql)
        self.assertIn("reviewed_version = new.version", self.sql)
        self.assertIn("decision = 'approve'", self.sql)
        self.assertIn("reviewer_id <> new.created_by", self.sql)
        self.assertIn("before insert or update of status, version", self.sql)

    def test_definer_function_is_private_and_search_path_is_fixed(self) -> None:
        self.assertIn("security definer", self.sql)
        self.assertIn("set search_path = ''", self.sql)
        self.assertIn(
            "revoke all on function noema_private.require_approved_review_before_publish()",
            self.sql,
        )
        self.assertNotIn("grant execute on function noema_private.require_approved_review_before_publish()", self.sql)

    def test_comments_are_authenticated_and_append_only_for_clients(self) -> None:
        self.assertIn("grant insert on public.research_reviews, public.research_comments to authenticated;", self.sql)
        self.assertNotIn("grant update on public.research_comments", self.sql)
        self.assertNotIn("grant delete on public.research_comments", self.sql)
        self.assertIn("author_id = (select auth.uid())", self.sql)


if __name__ == "__main__":
    unittest.main()
