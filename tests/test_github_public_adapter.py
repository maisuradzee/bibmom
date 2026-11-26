from __future__ import annotations

import base64
import json
import unittest
from urllib.parse import urlsplit, parse_qs

from noema_core.github_public import (
    GitHubPublicAdapterError,
    GitHubPublicRepositoryAdapter,
)
from noema_core.integrations import (
    AdapterRegistry, ExecutionMode, IntegrationEngine, IntegrationGrant,
)


class GitHubPublicAdapterTests(unittest.TestCase):
    def setUp(self):
        self.responses = []
        self.requests = []

        def transport(url, headers, timeout, max_bytes):
            self.requests.append((url, dict(headers), timeout, max_bytes))
            if not self.responses:
                raise AssertionError("No mock response configured")
            return self.responses.pop(0)

        self.transport = transport
        self.adapter = GitHubPublicRepositoryAdapter(
            "maisuradzee", "bibmom", transport=transport
        )
        self.adapters = AdapterRegistry()
        self.adapters.register(self.adapter.adapter_id, self.adapter)
        self.engine = IntegrationEngine(self.adapters)

    @staticmethod
    def response(data, *, status=200, content_type="application/json; charset=utf-8"):
        body = data if isinstance(data, bytes) else json.dumps(data).encode("utf-8")
        return status, {"Content-Type": content_type}, body

    def test_discovery_exposes_read_only_operations(self):
        descriptor = self.adapter.discover()
        self.assertEqual(descriptor.adapter_id, "github.public_repository")
        self.assertEqual(
            {item.operation_id for item in descriptor.capabilities},
            {"github.repo.metadata", "github.repo.file.read"},
        )
        self.assertTrue(all(item.effect.value == "read" for item in descriptor.capabilities))

    def test_repository_metadata_is_allowlisted_and_never_exposes_tokens(self):
        self.responses.append(self.response({
            "full_name": "maisuradzee/bibmom",
            "private": False,
            "visibility": "public",
            "default_branch": "main",
            "html_url": "https://github.com/maisuradzee/bibmom",
            "temp_clone_token": "must-not-escape",
            "owner": {"login": "maisuradzee"},
        }))
        plan = self.engine.prepare(
            self.adapter.adapter_id, "github.repo.metadata", {},
            idempotency_key="repo-metadata",
            mode=ExecutionMode.LIVE,
        )
        grant = IntegrationGrant(
            self.adapter.adapter_id, frozenset({"github.repo.metadata"})
        )
        result = self.engine.execute(plan, grant=grant)
        self.assertEqual(result.status, "succeeded")
        self.assertEqual(result.result["repository"]["full_name"], "maisuradzee/bibmom")
        self.assertNotIn("temp_clone_token", result.result["repository"])
        url, headers, timeout, max_bytes = self.requests[0]
        self.assertEqual(url, "https://api.github.com/repos/maisuradzee/bibmom")
        self.assertEqual(headers["X-GitHub-Api-Version"], "2026-03-10")
        self.assertTrue(headers["User-Agent"].startswith("NOEMA-"))
        self.assertGreater(timeout, 0)
        self.assertGreater(max_bytes, 0)

    def test_file_read_decodes_utf8_and_encodes_ref_safely(self):
        text = "# NOEMA\nინტეგრაციის ტესტი\n"
        encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
        self.responses.append(self.response({
            "type": "file", "name": "README.md", "path": "docs/README.md",
            "sha": "blob-sha", "size": len(text.encode("utf-8")),
            "encoding": "base64", "content": encoded,
        }))
        plan = self.engine.prepare(
            self.adapter.adapter_id, "github.repo.file.read",
            {"path": "docs/README.md", "ref": "feature/test-branch"},
            idempotency_key="read-readme", mode=ExecutionMode.LIVE,
        )
        grant = IntegrationGrant(
            self.adapter.adapter_id, frozenset({"github.repo.file.read"})
        )
        result = self.engine.execute(plan, grant=grant)
        self.assertEqual(result.status, "succeeded")
        self.assertEqual(result.result["file"]["content"], text)
        parsed = urlsplit(self.requests[0][0])
        self.assertEqual(parsed.path, "/repos/maisuradzee/bibmom/contents/docs/README.md")
        self.assertEqual(parse_qs(parsed.query), {"ref": ["feature/test-branch"]})

    def test_dry_run_does_not_contact_github(self):
        plan = self.engine.prepare(
            self.adapter.adapter_id, "github.repo.metadata", {},
            idempotency_key="dry-run",
        )
        result = self.engine.execute(plan)
        self.assertEqual(result.status, "simulated")
        self.assertEqual(self.requests, [])

    def test_wrong_or_missing_scope_blocks_live_request_before_transport(self):
        plan = self.engine.prepare(
            self.adapter.adapter_id, "github.repo.metadata", {},
            idempotency_key="scope-test", mode=ExecutionMode.LIVE,
        )
        wrong = IntegrationGrant("another.adapter", frozenset({"github.repo.metadata"}))
        self.assertEqual(self.engine.execute(plan, grant=wrong).status, "blocked")
        self.assertEqual(self.requests, [])

    def test_path_traversal_and_encoded_path_are_rejected(self):
        for path in ("../README.md", "docs/../../README.md", "/README.md", "README%2emd", "a//b"):
            with self.subTest(path=path):
                errors = self.adapter.validate("github.repo.file.read", {"path": path})
                self.assertTrue(errors)

    def test_invalid_ref_is_rejected(self):
        for ref in ("../main", "/main", "main//branch", "main?query", "feature/@{bad}"):
            with self.subTest(ref=ref):
                self.assertTrue(self.adapter.validate(
                    "github.repo.file.read", {"path": "README.md", "ref": ref}
                ))

    def test_redirects_and_non_200_responses_are_blocked(self):
        self.responses.append(self.response({"location": "https://evil.example/"}, status=302))
        with self.assertRaisesRegex(GitHubPublicAdapterError, "redirect"):
            self.adapter.execute("github.repo.metadata", {}, idempotency_key="redirect")
        self.responses.append(self.response({"message": "not found"}, status=404))
        with self.assertRaisesRegex(GitHubPublicAdapterError, "HTTP 404"):
            self.adapter.execute("github.repo.metadata", {}, idempotency_key="404")

    def test_unexpected_content_type_and_oversized_responses_are_blocked(self):
        self.responses.append(self.response({"x": 1}, content_type="text/html"))
        with self.assertRaisesRegex(GitHubPublicAdapterError, "content type"):
            self.adapter.execute("github.repo.metadata", {}, idempotency_key="html")
        self.responses.append((
            200, {"Content-Type": "application/json"}, b"x" * (self.adapter.max_response_bytes + 1)
        ))
        with self.assertRaisesRegex(GitHubPublicAdapterError, "size limit"):
            self.adapter.execute("github.repo.metadata", {}, idempotency_key="large")

    def test_private_repo_is_never_returned_as_public(self):
        self.responses.append(self.response({"full_name": "maisuradzee/bibmom", "private": True}))
        with self.assertRaisesRegex(GitHubPublicAdapterError, "not confirmed public"):
            self.adapter.execute("github.repo.metadata", {}, idempotency_key="private")

    def test_invalid_file_type_and_binary_content_are_blocked(self):
        self.responses.append(self.response({"type": "dir"}))
        with self.assertRaisesRegex(GitHubPublicAdapterError, "regular repository file"):
            self.adapter.execute(
                "github.repo.file.read", {"path": "docs"}, idempotency_key="directory"
            )
        self.responses.append(self.response({
            "type": "file", "name": "image.bin", "path": "image.bin", "sha": "x",
            "size": 3, "encoding": "base64", "content": base64.b64encode(b"\xff\xfe\xfd").decode(),
        }))
        with self.assertRaisesRegex(GitHubPublicAdapterError, "UTF-8"):
            self.adapter.execute(
                "github.repo.file.read", {"path": "image.bin"}, idempotency_key="binary"
            )

    def test_invalid_configuration_is_rejected(self):
        with self.assertRaises(GitHubPublicAdapterError):
            GitHubPublicRepositoryAdapter("../owner", "repo")
        with self.assertRaises(GitHubPublicAdapterError):
            GitHubPublicRepositoryAdapter("owner", "repo", timeout_seconds=100)
        with self.assertRaises(GitHubPublicAdapterError):
            GitHubPublicRepositoryAdapter("owner", "repo", max_response_bytes=100)


if __name__ == "__main__":
    unittest.main()
