from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from scripts.ci_recovery import (
    _extract_source_urls,
    _normalize_draft,
    _safe_public_source_url,
    recover_drafts,
    summarize_step_outcomes,
)
from scripts.validate_ci_workflow_contract import validate_workflow_contract

ROOT = Path(__file__).resolve().parents[1]


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
- Inspect the source.
"""
        repaired, rules = _normalize_draft(source)
        self.assertIn("- **თარიღი:** 2026-11-28", repaired)
        self.assertIn("- **სტატუსი:** draft", repaired)
        self.assertIn("## საკვლევი კითხვა", repaired)
        self.assertIn("## მეთოდი ან ექსპერიმენტის გეგმა", repaired)
        self.assertIn("## წყაროები", repaired)
        self.assertIn("## შემდეგი ნაბიჯები", repaired)
        self.assertIn("A factual statement remains byte-for-byte unchanged.", repaired)
        self.assertIn("A method description remains unchanged.", repaired)
        self.assertIn("metadata.date_label", rules)
        self.assertIn("metadata.status_label", rules)

    def test_never_promotes_a_narrative_url_into_sources(self) -> None:
        source = """# NOEMA-2026-999 — Example

- **თარიღი:** 2026-11-28
- **სტატუსი:** draft

## წყაროები

## შემდეგი ნაბიჯები
- Verify the claim at https://example.org/narrative-only
"""
        repaired, rules = _normalize_draft(source)
        self.assertEqual(_extract_source_urls(repaired), [])
        self.assertNotIn("- https://example.org/narrative-only", repaired)
        self.assertNotIn("section.sources_from_existing_urls", rules)

    def test_source_extractor_reads_only_the_explicit_sources_section(self) -> None:
        source = """## წყაროები
- NEA: https://nea.gov.ge/En/News/3457

## შემდეგი ნაბიჯები
- Do not promote https://example.org/next-step
"""
        self.assertEqual(_extract_source_urls(source), ["https://nea.gov.ge/En/News/3457"])

    def test_safe_https_public_url_is_accepted(self) -> None:
        self.assertEqual(_safe_public_source_url("https://example.org/source")[0], True)

    def test_rejects_http_userinfo_private_hosts_and_invalid_ports(self) -> None:
        cases = [
            ("http://example.org/source", "https_absolute_url_required"),
            ("https://user:pass@example.org/source", "userinfo_forbidden"),
            ("https://127.0.0.1/source", "non_public_ip_literal"),
            ("https://localhost/source", "non_public_hostname"),
            ("https://example.org:99999/source", "malformed_url_or_port"),
        ]
        for url, expected in cases:
            with self.subTest(url=url):
                self.assertEqual(_safe_public_source_url(url)[1], expected)

    def test_rejects_overlong_url(self) -> None:
        url = "https://example.org/" + ("a" * 2048)
        self.assertEqual(_safe_public_source_url(url)[1], "url_too_long")

    def test_rejects_excess_query_and_fragment_fields(self) -> None:
        query = "&".join(f"p{i}=x" for i in range(33))
        fragment = "&".join(f"p{i}=x" for i in range(17))
        self.assertEqual(_safe_public_source_url(f"https://example.org/?{query}")[1], "query_too_many_fields")
        self.assertEqual(_safe_public_source_url(f"https://example.org/#{fragment}")[1], "fragment_too_many_fields")

    def test_rejects_semicolon_and_nested_encoded_credential_names(self) -> None:
        self.assertEqual(
            _safe_public_source_url("https://example.org/?page=1;api_key=secret")[1],
            "query_credential_like_parameter",
        )
        self.assertEqual(
            _safe_public_source_url("https://example.org/?%2561ccess_token=secret")[1],
            "query_credential_like_parameter",
        )
        self.assertEqual(
            _safe_public_source_url("https://example.org/#auth_token=secret")[1],
            "fragment_credential_like_parameter",
        )

    def test_recovery_report_does_not_echo_unsafe_url_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            drafts = root / "research" / "drafts"
            drafts.mkdir(parents=True)
            draft = drafts / "example.md"
            draft.write_text(
                "# NOEMA-2026-999 — Example\n\n"
                "- **თარიღი:** 2026-11-28\n"
                "- **სტატუსი:** draft\n\n"
                "## საკვლევი კითხვა\nQuestion.\n\n"
                "## მეთოდი ან ექსპერიმენტის გეგმა\nMethod.\n\n"
                "## წყაროები\n- https://example.org/?api_key=supersecret\n\n"
                "## შემდეგი ნაბიჯები\nVerify.\n\n"
                "## შემოწმების სტატუსი\nDraft.\n",
                encoding="utf-8",
            )
            report = recover_drafts(root, fix=True)
            serialized = json.dumps(report, ensure_ascii=False)
            self.assertTrue(report["source_url_issues"])
            self.assertNotIn("supersecret", serialized)
            self.assertNotIn("api_key", serialized)

    def test_required_step_aggregate_fails_closed(self) -> None:
        required = ["checkout", "dependencies", "validate_a", "validate_b"]
        all_success = {step: {"outcome": "success", "conclusion": "success"} for step in required}
        self.assertTrue(summarize_step_outcomes(all_success, required)["ok"])

        missing = dict(all_success)
        missing.pop("validate_b")
        result = summarize_step_outcomes(missing, required)
        self.assertFalse(result["ok"])
        self.assertIn("validate_b", result["missing_required_steps"])

        skipped = dict(all_success)
        skipped["validate_b"] = {"outcome": "skipped", "conclusion": "skipped"}
        self.assertFalse(summarize_step_outcomes(skipped, required)["ok"])

        failed = dict(all_success)
        failed["validate_a"] = {"outcome": "failure", "conclusion": "success"}
        self.assertFalse(summarize_step_outcomes(failed, required)["ok"])

        unknown = dict(all_success)
        unknown["validate_a"] = {}
        self.assertFalse(summarize_step_outcomes(unknown, required)["ok"])

    def test_manifest_schema_and_workflow_contract(self) -> None:
        manifest_path = ROOT / "data" / "ci-required-step-ids.json"
        schema_path = ROOT / "data" / "ci-required-step-ids.schema.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(manifest))
        self.assertEqual(errors, [])
        self.assertEqual(validate_workflow_contract(ROOT), [])

    def test_workflow_contract_fails_when_a_required_step_is_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workflow_dir = root / ".github" / "workflows"
            data_dir = root / "data"
            workflow_dir.mkdir(parents=True)
            data_dir.mkdir(parents=True)
            workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
            manifest = (ROOT / "data" / "ci-required-step-ids.json").read_text(encoding="utf-8")
            import re
            workflow = re.sub(
                r"(?ms)^      - name: Validate required files\n.*?(?=^      - name: |\Z)",
                "",
                workflow,
                count=1,
            )
            (workflow_dir / "ci.yml").write_text(workflow, encoding="utf-8")
            (data_dir / "ci-required-step-ids.json").write_text(manifest, encoding="utf-8")
            self.assertIn("workflow_step_ids_do_not_match_required_manifest", validate_workflow_contract(root))

    def test_workflow_contract_fails_when_continue_on_error_is_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workflow_dir = root / ".github" / "workflows"
            data_dir = root / "data"
            workflow_dir.mkdir(parents=True)
            data_dir.mkdir(parents=True)
            workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
            manifest = (ROOT / "data" / "ci-required-step-ids.json").read_text(encoding="utf-8")
            workflow = workflow.replace(
                "        id: check_01_validate_required_files\n        continue-on-error: true",
                "        id: check_01_validate_required_files",
                1,
            )
            (workflow_dir / "ci.yml").write_text(workflow, encoding="utf-8")
            (data_dir / "ci-required-step-ids.json").write_text(manifest, encoding="utf-8")
            self.assertIn(
                "validation_step_not_continue_on_error:check_01_validate_required_files",
                validate_workflow_contract(root),
            )


if __name__ == "__main__":
    unittest.main()
