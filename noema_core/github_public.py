"""Read-only adapter for public GitHub repositories.

The repository owner/name are fixed by trusted application configuration.
No token, write endpoint, caller-supplied URL, or redirect is accepted.
"""
from __future__ import annotations

import base64
import binascii
import json
import math
import re
from email.message import Message
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .integrations import (
    IntegrationCapability,
    IntegrationDescriptor,
    IntegrationEffect,
    IntegrationError,
)

_OWNER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")
_REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")
_API_VERSION = "2026-03-10"
_BASE_URL = "https://api.github.com"


class GitHubPublicAdapterError(IntegrationError):
    """The public GitHub API response or local adapter configuration is invalid."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        return None


class GitHubPublicRepositoryAdapter:
    """Read-only public repository adapter implementing the NOEMA adapter contract.

    A custom transport is intended for deterministic tests and must be trusted
    application code. Production use defaults to urllib with redirects disabled.
    """
    def __init__(
        self,
        owner: str,
        repository: str,
        *,
        timeout_seconds: float = 10.0,
        max_response_bytes: int = 2_000_000,
        max_file_bytes: int = 1_000_000,
        transport: Callable[[str, Mapping[str, str], float, int], tuple[int, Mapping[str, str], bytes]] | None = None,
    ) -> None:
        if not isinstance(owner, str) or not _OWNER_RE.fullmatch(owner):
            raise GitHubPublicAdapterError("Invalid GitHub owner")
        if not isinstance(repository, str) or not _REPO_RE.fullmatch(repository):
            raise GitHubPublicAdapterError("Invalid GitHub repository name")
        if not isinstance(timeout_seconds, (int, float)) or not math.isfinite(float(timeout_seconds)) or not 0.1 <= timeout_seconds <= 30:
            raise GitHubPublicAdapterError("timeout_seconds must be between 0.1 and 30")
        if not isinstance(max_response_bytes, int) or not 1024 <= max_response_bytes <= 10_000_000:
            raise GitHubPublicAdapterError("max_response_bytes must be between 1 KB and 10 MB")
        if not isinstance(max_file_bytes, int) or not 1 <= max_file_bytes <= min(max_response_bytes, 5_000_000):
            raise GitHubPublicAdapterError("Invalid max_file_bytes")
        if transport is not None and not callable(transport):
            raise GitHubPublicAdapterError("transport must be callable")
        self.owner = owner
        self.repository = repository
        self.timeout_seconds = float(timeout_seconds)
        self.max_response_bytes = max_response_bytes
        self.max_file_bytes = max_file_bytes
        self._transport = transport

    @property
    def adapter_id(self) -> str:
        return "github.public_repository"

    def discover(self) -> IntegrationDescriptor:
        return IntegrationDescriptor(
            self.adapter_id,
            "GitHub public repository (read-only)",
            "1.0.0",
            (
                IntegrationCapability(
                    "github.repo.metadata",
                    IntegrationEffect.READ,
                    "Read allowlisted metadata for the configured public repository",
                    (),
                    (),
                    source_class="public",
                ),
                IntegrationCapability(
                    "github.repo.file.read",
                    IntegrationEffect.READ,
                    "Read a UTF-8 text file from the configured public repository",
                    ("path",),
                    ("path", "ref"),
                    source_class="public",
                ),
            ),
        )

    @staticmethod
    def _validate_path(value: Any) -> str:
        if not isinstance(value, str) or not value or len(value) > 512:
            raise GitHubPublicAdapterError("path must be a non-empty string up to 512 characters")
        if value.startswith("/") or value.endswith("/") or "//" in value:
            raise GitHubPublicAdapterError("path must be a relative repository file path")
        if any(char in value for char in ("\\", "%", "?", "#", "\x00")):
            raise GitHubPublicAdapterError("path contains a forbidden character")
        segments = value.split("/")
        if any(segment in {"", ".", ".."} for segment in segments):
            raise GitHubPublicAdapterError("path contains an invalid path segment")
        if any(ord(char) < 32 or ord(char) == 127 for char in value):
            raise GitHubPublicAdapterError("path contains control characters")
        return value

    @staticmethod
    def _validate_ref(value: Any) -> str:
        if not isinstance(value, str) or not _REF_RE.fullmatch(value):
            raise GitHubPublicAdapterError("ref must be a valid branch, tag or commit ref")
        if value.startswith("/") or value.endswith("/") or "//" in value or "\\" in value:
            raise GitHubPublicAdapterError("ref contains an invalid path separator")
        if any(segment in {".", ".."} for segment in value.split("/")) or "@{" in value:
            raise GitHubPublicAdapterError("ref contains an invalid path segment")
        return value

    def validate(self, operation_id: str, payload: Mapping[str, Any]):
        if operation_id == "github.repo.metadata":
            return ()
        if operation_id == "github.repo.file.read":
            if not isinstance(payload, Mapping):
                return ("payload must be an object",)
            try:
                self._validate_path(payload.get("path"))
                if "ref" in payload:
                    self._validate_ref(payload["ref"])
            except GitHubPublicAdapterError as exc:
                return (str(exc),)
            return ()
        return ("operation is not supported by the read-only GitHub adapter",)

    def _http_get(self, url: str) -> tuple[int, Mapping[str, str], bytes]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": _API_VERSION,
            "User-Agent": "NOEMA-Adaptive-Integration/0.1",
        }
        if self._transport is not None:
            status, response_headers, body = self._transport(
                url, headers, self.timeout_seconds, self.max_response_bytes
            )
        else:
            request = Request(url, headers=headers, method="GET")
            opener = build_opener(_NoRedirect())
            try:
                with opener.open(request, timeout=self.timeout_seconds) as response:
                    status = response.status
                    response_headers = dict(response.headers.items())
                    body = response.read(self.max_response_bytes + 1)
            except HTTPError as exc:
                if exc.code in {301, 302, 303, 307, 308}:
                    raise GitHubPublicAdapterError("GitHub API redirect was blocked") from exc
                if exc.code in {403, 429}:
                    raise GitHubPublicAdapterError(
                        "GitHub API denied the request or rate limit was reached; retry after the indicated window"
                    ) from exc
                raise GitHubPublicAdapterError(f"GitHub API returned HTTP {exc.code}") from exc
            except URLError as exc:
                raise GitHubPublicAdapterError("GitHub API network request failed") from exc

        if not isinstance(status, int) or not isinstance(response_headers, Mapping) or not isinstance(body, bytes):
            raise GitHubPublicAdapterError("HTTP transport returned an invalid response")
        if status in {301, 302, 303, 307, 308}:
            raise GitHubPublicAdapterError("GitHub API redirect was blocked")
        if status in {403, 429}:
            raise GitHubPublicAdapterError("GitHub API denied the request or rate limit was reached")
        if status != 200:
            raise GitHubPublicAdapterError(f"GitHub API returned HTTP {status}")
        if len(body) > self.max_response_bytes:
            raise GitHubPublicAdapterError("GitHub API response exceeded the configured size limit")
        normalized_headers = {str(k).lower(): str(v) for k, v in response_headers.items()}
        content_type = normalized_headers.get("content-type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise GitHubPublicAdapterError("GitHub API returned an unexpected content type")
        return status, normalized_headers, body

    def _get_json(self, url: str) -> dict[str, Any]:
        _, _, body = self._http_get(url)
        try:
            result = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GitHubPublicAdapterError("GitHub API returned invalid UTF-8 JSON") from exc
        if not isinstance(result, dict):
            raise GitHubPublicAdapterError("GitHub API response must be a JSON object")
        return result

    def execute(
        self,
        operation_id: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
    ) -> Mapping[str, Any]:
        del idempotency_key  # GET is naturally idempotent; no write operations exist.
        errors = self.validate(operation_id, payload)
        if errors:
            raise GitHubPublicAdapterError("; ".join(errors))

        root = f"{_BASE_URL}/repos/{quote(self.owner, safe='')}/{quote(self.repository, safe='')}"
        if operation_id == "github.repo.metadata":
            data = self._get_json(root)
            if data.get("private") is not False:
                raise GitHubPublicAdapterError("Configured repository is not confirmed public")
            allowed = (
                "full_name", "private", "visibility", "default_branch", "archived",
                "disabled", "html_url", "description", "language", "size",
                "stargazers_count", "forks_count", "open_issues_count", "created_at",
                "updated_at", "pushed_at",
            )
            metadata = {key: data[key] for key in allowed if key in data}
            license_data = data.get("license")
            if isinstance(license_data, dict):
                metadata["license"] = {
                    key: license_data[key]
                    for key in ("name", "spdx_id")
                    if isinstance(license_data.get(key), str)
                }
            if not isinstance(metadata.get("full_name"), str):
                raise GitHubPublicAdapterError("GitHub API response has no repository identity")
            expected = f"{self.owner}/{self.repository}".casefold()
            if metadata["full_name"].casefold() != expected:
                raise GitHubPublicAdapterError("GitHub API response repository identity mismatch")
            return {"repository": metadata}

        path = self._validate_path(payload["path"])
        url = f"{root}/contents/{quote(path, safe='/-._~')}"
        if "ref" in payload:
            ref = self._validate_ref(payload["ref"])
            url += "?" + urlencode({"ref": ref})
        data = self._get_json(url)
        if data.get("type") != "file":
            raise GitHubPublicAdapterError("Requested path is not a regular repository file")
        size = data.get("size")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0 or size > self.max_file_bytes:
            raise GitHubPublicAdapterError("Repository file is outside the configured size limit")
        if data.get("encoding") != "base64" or not isinstance(data.get("content"), str):
            raise GitHubPublicAdapterError("Repository file is not available as a Base64 object")
        encoded = "".join(data["content"].split())
        try:
            raw = base64.b64decode(encoded, validate=True)
            content = raw.decode("utf-8")
        except (binascii.Error, UnicodeDecodeError) as exc:
            raise GitHubPublicAdapterError("Repository file is not valid Base64-encoded UTF-8 text") from exc
        if len(raw) > self.max_file_bytes:
            raise GitHubPublicAdapterError("Decoded repository file exceeded the configured size limit")
        return {
            "file": {
                "name": data.get("name"),
                "path": data.get("path"),
                "sha": data.get("sha"),
                "size": len(raw),
                "encoding": "utf-8",
                "content": content,
            }
        }
