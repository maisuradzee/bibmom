from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ci_recovery import (
    _normalize_draft,
    _safe_public_source_url,
    recover_drafts,
)


class BoundedDraftRecoveryTests(unittest.TestCase):
    def test_normalizes_only_known_metadata_and_heading_aliases(self) -> None:
        source = """# NOEMA-2026-999 — Example

- **Date:** 2026-11-28
- **Status:** draft

## Research question
A factual statement remains byte-for-byte unchanged.

## Method and limitations
A method description remains unchanged.

## Sources
- https://example.org/source

## Next steps
- Verify.
"""
        repaired, rules = _normalize_draft(source)
        self.assertIn("- **თარიღი:** 2026-11-28", repaired)
        self.assertIn("- **სტატუსი:** draft", repaired)
        self.assertIn("## საკვლევი კითხვა", repaired)
        self.assertIn("## მეთოდი ან ექსპერიმენტის გეგმა", repaired)
        self.assertIn("## წყაროები", repaired)
        self.assertIn("A factual statement remains byte-for-byte unchanged.", repaired)
        self.assertIn("A method description remains unchanged.", repaired)
        self.assertIn("metadata.date_label", rules)
        self.assertIn("metadata.status_label", rules)

    def test_does_not_promote_next_step_demo_or_api_urls(self) -> None:
        source = """# NOEMA-2026-999 — Example

- **Date:** 2026-11-28
- **Status:** draft

## Research question
Question.

## Method and limitations
Method.

## Next steps
- Inspect the demo: https://demo.example.org/
- Query the API: https://api.example.org/v1/status
"""
        repaired, rules = _normalize_draft(source)
        self.assertNotIn("## წყაროები", repaired)
        self.assertNotIn("section.sources_from_existing_urls", rules)
        self.assertIn("https://demo.example.org/", repaired)
        self.assertIn("https://api.example.org/v1/status", repaired)

    def test_public_url_validator_accepts_plain_public_source_url(self) -> None:
        self.assertEqual(_safe_public_source_url("https://example.org/article?page=2#section-3"), (True, None))

    def test_public_url_validator_rejects_userinfo_and_invalid_port(self) -> None:
        self.assertEqual(_safe_public_source_url("https://user:password@example.org/article")[0], False)
        self.assertEqual(_safe_public_source_url("https://example.org:99999/article"), (False, "invalid_url_or_port"))

    def test_public_url_validator_rejects_credential_and_signed_query_parameters(self) -> None:
        urls = [
            "https://example.org/path?access_token=redacted",
            "https://example.org/path?X-Amz-Signature=redacted",
            "https://example.org/path?X-Goog-Credential=redacted",
            "https://example.org/path?sig=redacted",
            "https://example.org/path#access_token=redacted",
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertFalse(_safe_public_source_url(url)[0])

    def test_public_url_validator_rejects_non_public_hosts_and_ip_addresses(self) -> None:
        self.assertEqual(_safe_public_source_url("http://localhost/private")[0], False)
        self.assertEqual(_safe_public_source_url("http://127.0.0.1/private"), (False, "non_public_ip_address"))
        self.assertEqual(_safe_public_source_url("http://192.0.2.10/private"), (False, "non_public_ip_address"))

    def test_explicit_source_scan_never_echoes_unsafe_url_values(self) -> None:
        from scripts.ci_recovery import _audit_source_urls

        source = """# NOEMA-2026-999 — Example

## წყაროები
- https://example.org/article?access_token=DO_NOT_ECHO
"""
        safe_count, unsafe = _audit_source_urls(source, "research/drafts/example.md")
        self.assertEqual(safe_count, 0)
        self.assertEqual(len(unsafe), 1)
        self.assertEqual(unsafe[0]["reason"], "credential_like_query_parameter")
        self.assertNotIn("DO_NOT_ECHO", str(unsafe))

    def test_recovery_is_idempotent_and_never_promotes_source_urls(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            draft_dir = root / "research" / "drafts"
            draft_dir.mkdir(parents=True)
            draft = draft_dir / "example.md"
            draft.write_text(
                "# NOEMA-2026-999 — Example\n\n"
                "- **Date:** 2026-11-28\n"
                "- **Status:** draft\n\n"
                "## Research question\nQuestion.\n\n"
                "## Method and limitations\nMethod.\n\n"
                "## Next steps\n- Inspect https://example.org/demo\n\n"
                "## Verification status\nPending independent review.\n",
                encoding="utf-8",
            )
            first = recover_drafts(root, fix=True)
            after_first = draft.read_text(encoding="utf-8")
            second = recover_drafts(root, fix=True)
            after_second = draft.read_text(encoding="utf-8")
            self.assertEqual(after_first, after_second)
            self.assertEqual(first["remaining_validation_errors"], [])
            self.assertTrue(first["unified_patch"])
            self.assertIn("Date", first["unified_patch"])
            self.assertIn("თარიღი", first["unified_patch"])
            self.assertEqual(first["source_urls_promoted"], [])
            self.assertFalse(first["source_url_inference_enabled"])
            self.assertEqual(second["files_with_safe_repairs"], [])
            self.assertFalse(second["safe_repairs_applied"])

    def test_published_status_is_not_downgraded_or_relabelled(self) -> None:
        source = "# NOEMA-2026-999 — Example\n\n- **Status:** published\n"
        repaired, rules = _normalize_draft(source)
        self.assertIn("- **სტატუსი:** published", repaired)
        self.assertNotIn("draft", repaired)
        self.assertIn("metadata.status_label", rules)

    def test_scientific_claims_and_evidence_values_are_not_modified(self) -> None:
        source = (
            "# NOEMA-2026-999 — Example\n\n"
            "- **Date:** 2026-11-28\n"
            "- **Status:** draft\n\n"
            "## Research question\n"
            "FACT: measured result is 13% (n=99).\n\n"
            "## Method and limitations\n"
            "INFERENCE: this may warrant further work.\n\n"
            "## Sources\n- https://example.org/source\n"
        )
        repaired, _ = _normalize_draft(source)
        self.assertIn("FACT: measured result is 13% (n=99).", repaired)
        self.assertIn("INFERENCE: this may warrant further work.", repaired)


if __name__ == "__main__":
    unittest.main()
