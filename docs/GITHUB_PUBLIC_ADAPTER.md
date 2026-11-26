# GitHub Public Repository Adapter

`noema_core.github_public.GitHubPublicRepositoryAdapter` is the first concrete example adapter for the NOEMA Adaptive Integration Engine.

## Scope

- Read-only access to one explicitly configured public GitHub repository.
- Operations: `github.repo.metadata` and `github.repo.file.read`.
- HTTPS is fixed to `https://api.github.com`; owner/repository are trusted constructor configuration, never payload URLs.
- No authentication token is accepted or stored.
- Redirects, non-200 responses, unexpected content types, oversized responses, private repositories and binary/non-UTF-8 files are rejected.
- Repository metadata is filtered through an allowlist so unexpected or sensitive API fields cannot leak into NOEMA results.
- File paths and refs are checked before URL encoding; path traversal and encoded separators are rejected.
- Network timeout and response/file-size bounds are configurable within enforced maximums.

## Example

\`\`\`python
from noema_core.github_public import GitHubPublicRepositoryAdapter
from noema_core.integrations import (
    AdapterRegistry, ExecutionMode, IntegrationEngine, IntegrationGrant,
)

adapters = AdapterRegistry()
adapters.register(
    "github.public_repository",
    GitHubPublicRepositoryAdapter("maisuradzee", "bibmom"),
)
engine = IntegrationEngine(adapters)

plan = engine.prepare(
    "github.public_repository",
    "github.repo.metadata",
    {},
    idempotency_key="noema-bibmom-metadata-v1",
    mode=ExecutionMode.LIVE,
)
grant = IntegrationGrant(
    "github.public_repository",
    frozenset({"github.repo.metadata"}),
)
result = engine.execute(plan, grant=grant)
\`\`\`

`DRY_RUN` remains the default. Live access must be enabled by trusted host code with an operation-scoped grant. This adapter performs GET requests only; it cannot create branches, commits, issues, pull requests or modify files.

GitHub documents unauthenticated access for public repository metadata and content. Unauthenticated REST API requests are subject to a primary limit of 60 requests per hour per originating IP address. The adapter does not automatically retry rate-limit responses; the caller should respect GitHub's Retry-After and X-RateLimit-Reset guidance.

This adapter is a bounded public-data connector, not a general-purpose GitHub client and not an authorization to reuse or republish repository content.
