from __future__ import annotations

import json
import unittest
from urllib.parse import parse_qs, urlsplit

from noema_core.integrations import AdapterRegistry, ExecutionMode, IntegrationEngine, IntegrationGrant
from noema_core.openapi_read import OpenAPIReadAdapter, OpenAPIReadAdapterError


def make_spec():
    return {
        "openapi": "3.1.0",
        "servers": [{"url": "https://api.example.test/v1"}],
        "security": [{"BearerAuth": []}],
        "paths": {
            "/items/{itemId}": {
                "parameters": [{
                    "name": "itemId", "in": "path", "required": True,
                    "schema": {"type": "integer", "minimum": 1},
                }],
                "get": {
                    "operationId": "getItem",
                    "summary": "Read one item",
                    "security": [],
                    "parameters": [{
                        "name": "expand", "in": "query", "required": False,
                        "schema": {"type": "string", "enum": ["summary", "full"], "maxLength": 12},
                    }],
                    "responses": {
                        "200": {"description": "OK", "content": {"application/json": {"schema": {"type": "object"}}}}
                    },
                },
                "post": {
                    "operationId": "createItem",
                    "responses": {"201": {"description": "Created", "content": {"application/json": {}}}},
                },
            },
            "/private": {
                "get": {
                    "operationId": "getPrivate",
                    "responses": {"200": {"description": "OK", "content": {"application/json": {}}}},
                }
            },
            "/text": {
                "get": {
                    "operationId": "getText",
                    "security": [],
                    "responses": {"200": {"description": "OK", "content": {"text/plain": {}}}},
                }
            },
            "/legacy": {
                "get": {
                    "operationId": "getLegacy",
                    "security": [],
                    "responses": {"200": {"description": "OK", "content": {"application/problem+json": {}}}},
                }
            },
        },
    }


class OpenAPIReadAdapterTests(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.responses = []

        def transport(url, headers, timeout, max_bytes):
            self.requests.append((url, dict(headers), timeout, max_bytes))
            if not self.responses:
                raise AssertionError("No mock response configured")
            return self.responses.pop(0)

        self.transport = transport
        self.adapter = OpenAPIReadAdapter(
            "example.catalog", "Example Catalog API", "https://api.example.test/v1",
            make_spec(), transport=transport,
        )
        self.registry = AdapterRegistry()
        self.registry.register(self.adapter.adapter_id, self.adapter)
        self.engine = IntegrationEngine(self.registry)

    @staticmethod
    def response(data, *, status=200, content_type="application/json; charset=utf-8"):
        body = data if isinstance(data, bytes) else json.dumps(data).encode("utf-8")
        return status, {"Content-Type": content_type}, body

    def test_discovery_derives_only_public_json_get_capabilities(self):
        descriptor = self.adapter.discover()
        self.assertEqual(descriptor.adapter_id, "example.catalog")
        self.assertEqual(
            [item.operation_id for item in descriptor.capabilities],
            ["getitem", "getlegacy"],
        )
        self.assertTrue(all(item.effect.value == "read" for item in descriptor.capabilities))
        self.assertEqual(descriptor.capabilities[0].required_fields, ("itemId",))

    def test_live_get_builds_path_and_query_from_openapi_parameters(self):
        self.responses.append(self.response({"id": 42, "name": "sample"}))
        plan = self.engine.prepare(
            self.adapter.adapter_id, "getitem",
            {"itemId": 42, "expand": "full"},
            idempotency_key="item-read-42", mode=ExecutionMode.LIVE,
        )
        grant = IntegrationGrant(self.adapter.adapter_id, frozenset({"getitem"}))
        result = self.engine.execute(plan, grant=grant)
        self.assertEqual(result.status, "succeeded")
        self.assertEqual(result.result["name"], "sample")
        url, headers, timeout, max_bytes = self.requests[0]
        parsed = urlsplit(url)
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "api.example.test")
        self.assertEqual(parsed.path, "/v1/items/42")
        self.assertEqual(parse_qs(parsed.query), {"expand": ["full"]})
        self.assertEqual(headers["Accept"], "application/json")
        self.assertGreater(timeout, 0)
        self.assertGreater(max_bytes, 0)

    def test_dry_run_is_default_and_does_not_contact_api(self):
        plan = self.engine.prepare(
            self.adapter.adapter_id, "getitem",
            {"itemId": 7}, idempotency_key="dry-7",
        )
        self.assertEqual(self.engine.execute(plan).status, "simulated")
        self.assertEqual(self.requests, [])

    def test_parameter_types_enum_and_required_fields_are_enforced(self):
        invalid_payloads = (
            {},
            {"itemId": "seven"},
            {"itemId": 7, "expand": "all"},
            {"itemId": 0},
            {"itemId": 7, "unknown": "field"},
        )
        for index, payload in enumerate(invalid_payloads):
            with self.subTest(payload=payload):
                plan = self.engine.prepare(
                    self.adapter.adapter_id, "getitem", payload,
                    idempotency_key=f"invalid-{index}",
                )
                self.assertEqual(self.engine.execute(plan).status, "blocked")
        self.assertEqual(self.requests, [])

    def test_undeclared_secured_and_non_get_operations_are_not_executable(self):
        for operation in ("createitem", "getprivate", "gettext", "unknown"):
            with self.subTest(operation=operation):
                with self.assertRaises(OpenAPIReadAdapterError):
                    self.adapter.execute(operation, {}, idempotency_key="nope")
        self.assertEqual(self.requests, [])

    def test_path_parameter_values_are_percent_encoded(self):
        spec = make_spec()
        spec["paths"] = {
            "/items/{itemId}": {
                "parameters": [{
                    "name": "itemId", "in": "path", "required": True,
                    "schema": {"type": "string"},
                }],
                "get": {
                    "operationId": "getItem",
                    "security": [],
                    "responses": {"200": {"description": "OK", "content": {"application/json": {}}}},
                },
            }
        }
        adapter = OpenAPIReadAdapter(
            "example.catalog", "Example Catalog API", "https://api.example.test/v1",
            spec, transport=self.transport,
        )
        self.responses.append(self.response({"ok": True}))
        adapter.execute("getitem", {"itemId": "a/b?#"}, idempotency_key="encoded")
        self.assertEqual(urlsplit(self.requests[0][0]).path, "/v1/items/a%2Fb%3F%23")

    def test_redirect_and_non_success_statuses_are_blocked(self):
        self.responses.append(self.response({"location": "https://elsewhere.invalid/"}, status=302))
        with self.assertRaisesRegex(OpenAPIReadAdapterError, "redirect"):
            self.adapter.execute("getitem", {"itemId": 3}, idempotency_key="redirect")
        self.responses.append(self.response({"message": "not found"}, status=404))
        with self.assertRaisesRegex(OpenAPIReadAdapterError, "HTTP 404"):
            self.adapter.execute("getitem", {"itemId": 3}, idempotency_key="404")

    def test_rate_limit_and_unexpected_content_type_are_blocked(self):
        self.responses.append(self.response({"message": "limited"}, status=429))
        with self.assertRaisesRegex(OpenAPIReadAdapterError, "rate limit"):
            self.adapter.execute("getitem", {"itemId": 3}, idempotency_key="limited")
        self.responses.append(self.response({"html": True}, content_type="text/html"))
        with self.assertRaisesRegex(OpenAPIReadAdapterError, "content type"):
            self.adapter.execute("getitem", {"itemId": 3}, idempotency_key="html")

    def test_response_size_utf8_and_sensitive_keys_are_checked(self):
        self.responses.append((200, {"Content-Type": "application/json"}, b"x" * (self.adapter.max_response_bytes + 1)))
        with self.assertRaisesRegex(OpenAPIReadAdapterError, "size limit"):
            self.adapter.execute("getitem", {"itemId": 3}, idempotency_key="large")
        self.responses.append((200, {"Content-Type": "application/json"}, b"\xff"))
        with self.assertRaisesRegex(OpenAPIReadAdapterError, "UTF-8"):
            self.adapter.execute("getitem", {"itemId": 3}, idempotency_key="binary")
        self.responses.append(self.response({"data": [{"access_token": "secret"}]}))
        with self.assertRaisesRegex(OpenAPIReadAdapterError, "credential-like"):
            self.adapter.execute("getitem", {"itemId": 3}, idempotency_key="sensitive")

    def test_server_and_base_url_are_pinned_and_https_only(self):
        with self.assertRaisesRegex(OpenAPIReadAdapterError, "HTTPS"):
            OpenAPIReadAdapter("example.api", "Example", "http://api.example.test", make_spec())
        with self.assertRaisesRegex(OpenAPIReadAdapterError, "match"):
            OpenAPIReadAdapter(
                "example.api", "Example", "https://other.example.test/v1", make_spec()
            )
        with self.assertRaisesRegex(OpenAPIReadAdapterError, "credentials"):
            OpenAPIReadAdapter(
                "example.api", "Example", "https://user:pass@api.example.test/v1", make_spec()
            )

    def test_invalid_or_unsupported_documents_are_rejected(self):
        with self.assertRaisesRegex(OpenAPIReadAdapterError, "OpenAPI 3.0"):
            OpenAPIReadAdapter(
                "example.api", "Example", "https://api.example.test/v1",
                {"openapi": "2.0", "paths": {}},
            )
        bad = make_spec()
        bad["servers"] = [{"url": "https://attacker.example.test/v1"}]
        with self.assertRaisesRegex(OpenAPIReadAdapterError, "match"):
            OpenAPIReadAdapter(
                "example.api", "Example", "https://api.example.test/v1", bad
            )

    def test_unsafe_paths_and_external_refs_are_not_discovered(self):
        spec = {
            "openapi": "3.1.0",
            "servers": [{"url": "https://api.example.test"}],
            "paths": {
                "/../admin": {
                    "get": {"operationId": "badPath", "security": [],
                            "responses": {"200": {"description": "OK", "content": {"application/json": {}}}}}
                },
                "/safe": {"$ref": "https://attacker.example/openapi.json#/paths/~1safe"},
            },
        }
        with self.assertRaisesRegex(OpenAPIReadAdapterError, "No safe"):
            OpenAPIReadAdapter("example.safe", "Example", "https://api.example.test", spec)

    def test_non_object_json_responses_are_wrapped(self):
        self.responses.append(self.response([{"id": 1}, {"id": 2}]))
        plan = self.engine.prepare(
            self.adapter.adapter_id, "getlegacy", {},
            idempotency_key="list-items", mode=ExecutionMode.LIVE,
        )
        grant = IntegrationGrant(self.adapter.adapter_id, frozenset({"getlegacy"}))
        result = self.engine.execute(plan, grant=grant)
        self.assertEqual(result.status, "succeeded")
        self.assertEqual(result.result["data"], [{"id": 1}, {"id": 2}])


if __name__ == "__main__":
    unittest.main()
