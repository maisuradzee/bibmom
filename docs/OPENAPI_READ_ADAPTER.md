# OpenAPI Read Adapter

## Purpose

The OpenAPIReadAdapter converts an inline OpenAPI 3.0.x or 3.1.x JSON document into a set of read-only NOEMA capabilities. It is the schema-driven path for connecting REST APIs that publish an OpenAPI contract.

The OpenAPI Specification is a language-agnostic description of HTTP APIs. It defines path templates, parameters, operations and security requirements. This adapter uses that description to discover a conservative subset of safe operations rather than generating or executing arbitrary code.

## Discovery behavior

At initialization, the adapter inspects the trusted JSON document and derives:

- operation IDs (normalized to lowercase NOEMA identifiers);
- HTTP path templates;
- required path and query parameters;
- primitive parameter types: string, integer, number and boolean;
- enum, minLength, maxLength, minimum and maximum constraints;
- declared JSON success responses.

Only public GET operations are exposed. An operation must explicitly override inherited security with an empty security array when the document declares global security. A declared JSON success response is also required.

## Example

The JSON document and base URL must be loaded from trusted deployment configuration. Do not accept either value from a queue payload or arbitrary user input.

    from noema_core.integrations import (
        AdapterRegistry, IntegrationEngine, IntegrationGrant, ExecutionMode,
    )
    from noema_core.openapi_read import OpenAPIReadAdapter

    spec = {
        "openapi": "3.1.0",
        "servers": [{"url": "https://api.example.com/v1"}],
        "paths": {
            "/items/{itemId}": {
                "parameters": [{
                    "name": "itemId", "in": "path", "required": True,
                    "schema": {"type": "integer"},
                }],
                "get": {
                    "operationId": "getItem",
                    "security": [],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {"application/json": {"schema": {"type": "object"}}},
                        }
                    },
                },
            }
        },
    }

    adapter = OpenAPIReadAdapter(
        "catalog.api", "Catalog API", "https://api.example.com/v1", spec
    )
    registry = AdapterRegistry()
    registry.register(adapter.adapter_id, adapter)
    engine = IntegrationEngine(registry)

    # The OpenAPI operationId getItem is normalized to getitem.
    plan = engine.prepare(
        "catalog.api", "getitem", {"itemId": 42},
        idempotency_key="catalog-item-42",
        mode=ExecutionMode.LIVE,
    )
    grant = IntegrationGrant("catalog.api", frozenset({"getitem"}))
    result = engine.execute(plan, grant=grant)

DRY_RUN remains the default. Live operations require a trusted host-issued, operation-scoped grant.

## Supported scope and limitations

- Only OpenAPI 3.0.x and 3.1.x JSON documents are supported; YAML parsing is intentionally not included.
- Only GET operations with JSON success responses are exposed.
- Only inline scalar path/query parameter schemas are supported.
- External references, server variables, request bodies, arrays, objects, cookies, headers, form parameters, secured operations and non-GET methods are skipped.
- Exactly one fixed HTTPS server URL is supported and it must match the trusted base URL.
- Redirects are blocked. Request timeout and response size are bounded.
- Credential-like keys in API responses cause the result to be blocked.
- No API key, bearer token, cookie or other credential is accepted by this adapter version.

A domain name is still a trust decision. Configure only endpoints the NOEMA operator is authorized to query and apply outbound network controls at deployment level. The adapter does not bypass authentication; secured operations remain unavailable until a separately reviewed, secret-provider-backed adapter is designed.

This is a schema-driven read adapter, not a universal connector for every proprietary or undocumented system. Systems without an OpenAPI document still need a reviewed adapter implementing the common NOEMA integration contract.
