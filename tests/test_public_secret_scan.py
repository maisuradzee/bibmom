from __future__ import annotations
import unittest
from scripts.scan_public_secrets import scan_text


class PublicSecretPatternScanTests(unittest.TestCase):
    def test_detects_common_provider_tokens_without_echoing_values(self):
        secret = "ghp_" + "A" * 36
        findings = scan_text("sample.md", f"token: {secret}")
        self.assertTrue(any(item[2] == "github-token" for item in findings))
        self.assertNotIn(secret, repr(findings))

    def test_detects_private_key_header(self):
        key = ("-----BEGIN OPENSSH " + "PRIVATE KEY-----\n" + "A" * 64 +
               "\n-----END OPENSSH " + "PRIVATE KEY-----")
        findings = scan_text("sample.txt", key)
        self.assertTrue(any(item[2] == "private-key-block" for item in findings))

    def test_detects_encrypted_pkcs8_key_with_short_final_base64_line(self):
        key = (
            "-----BEGIN ENCRYPTED PRIVATE KEY-----\\n"
            + "A" * 64
            + "\\n"
            + "B" * 32
            + "\\n-----END ENCRYPTED PRIVATE KEY-----"
        )
        findings = scan_text("encrypted-key.txt", key)
        self.assertTrue(any(item[2] == "private-key-block" for item in findings))

    def test_detects_url_userinfo_query_and_path_credentials(self):
        findings = scan_text(
            "sources.md",
            "https://user:password@example.org/data\n"
            "https://example.org/feed?" + "access%255ftoken=opaque\n"
            "https://example.org/api/token/" + "AbCdEf0123456789GhIjKlMnOpQrStUv",
        )
        rules = {item[2] for item in findings}
        self.assertIn("url-credential-like-path-segment", rules)
        self.assertNotIn("url-userinfo-credentials", rules)
        self.assertNotIn("url-sensitive-parameter-name", rules)

    def test_placeholder_values_are_not_suppressed_on_non_example_hosts(self):
        findings = scan_text(
            "sources.md",
            "https://user:password@api.acme-water.io/data\\n"
            "https://api.acme-water.io/feed?access_token=opaque",
        )
        rules = {item[2] for item in findings}
        self.assertIn("url-userinfo-credentials", rules)
        self.assertIn("url-sensitive-parameter-name", rules)

    def test_known_hash_and_safe_public_source_urls_are_not_path_token_findings(self):
        findings = scan_text(
            "sources.md",
            "https://github.com/example/project/commit/" + "a" * 40 + "\n"
            "https://doi.org/10.1000/example.123",
        )
        self.assertFalse(any("path" in item[2] for item in findings))

    def test_placeholder_assignment_is_not_reported(self):
        findings = scan_text("config.md", "api_key: your-api-key-here")
        self.assertFalse(any(item[2] == "credential-assignment" for item in findings))


if __name__ == "__main__":
    unittest.main()
