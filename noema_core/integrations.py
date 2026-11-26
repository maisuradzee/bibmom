"""Policy-gated adaptive integrations for NOEMA.

Adapters are trusted application code registered explicitly by the host.
Manifests and job payloads are data only; the default mode is DRY_RUN.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import time
import unicodedata
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, Sequence

from .worker import HandlerRegistry, JobContext, NonRetryableJobError

_ID = re.compile(r"^[a-z][a-z0-9_.-]{1,63}$")
_FIELD = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,63}$")
_SECRET_FIELD_NAMES = frozenset({
    "password", "passwd", "pwd",
    "token", "accesstoken", "refreshtoken", "authtoken", "xauthtoken",
    "bearertoken", "sessiontoken", "idtoken", "oauth2token",
    "apikey", "xapikey",
    "secret", "clientsecret", "secretkey", "secretaccesskey", "privatekey",
    "authorization", "proxyauthorization",
    "cookie", "setcookie",
})


def _normalized_field_name(value: str) -> str:
    """Normalize punctuation/case/Unicode compatibility forms before secret matching."""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^a-z0-9]", "", normalized)


def _is_credential_field(value: str) -> bool:
    return _normalized_field_name(value) in _SECRET_FIELD_NAMES


_MAX_INTEGRATION_RESULT_BYTES = 900_000


class IntegrationError(ValueError):
    """Invalid adapter, capability, payload, plan, or grant."""


class AdapterNotFound(IntegrationError):
    """No trusted adapter is registered for the requested ID."""


class IntegrationEffect(str, Enum):
    READ = "read"
    WRITE = "write"
    EXTERNAL = "external_side_effect"
    DESTRUCTIVE = "destructive"


class ExecutionMode(str, Enum):
    DRY_RUN = "dry_run"
    LIVE = "live"


@dataclass(frozen=True)
class IntegrationCapability:
    operation_id: str
    effect: IntegrationEffect
    description: str
    required_fields: tuple[str, ...] = ()
    allowed_fields: tuple[str, ...] = ()
    source_class: str | None = None
    requires_reuse_permission: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.operation_id, str) or not _ID.fullmatch(self.operation_id):
            raise IntegrationError("Invalid operation_id")
        if not isinstance(self.effect, IntegrationEffect):
            raise IntegrationError("effect must be an IntegrationEffect")
        if not isinstance(self.description, str) or not self.description.strip() or len(self.description) > 300:
            raise IntegrationError("description must be 1-300 characters")
        for label, fields in (("required_fields", self.required_fields), ("allowed_fields", self.allowed_fields)):
            if not isinstance(fields, tuple) or any(not isinstance(x, str) or not _FIELD.fullmatch(x) for x in fields):
                raise IntegrationError(f"{label} must be a tuple of valid field names")
            if len(fields) != len(set(fields)):
                raise IntegrationError(f"{label} contains duplicate fields")
        if not set(self.required_fields) <= set(self.allowed_fields):
            raise IntegrationError("required_fields must be included in allowed_fields")
        if self.effect == IntegrationEffect.READ and not self.source_class:
            raise IntegrationError("READ capabilities must declare a source_class")
        if self.source_class is not None and not isinstance(self.source_class, str):
            raise IntegrationError("source_class must be a string")
        if not isinstance(self.requires_reuse_permission, bool):
            raise IntegrationError("requires_reuse_permission must be boolean")


@dataclass(frozen=True)
class IntegrationDescriptor:
    adapter_id: str
    display_name: str
    version: str
    capabilities: tuple[IntegrationCapability, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.adapter_id, str) or not _ID.fullmatch(self.adapter_id):
            raise IntegrationError("Invalid adapter_id")
        if not isinstance(self.display_name, str) or not self.display_name.strip() or len(self.display_name) > 120:
            raise IntegrationError("display_name must be 1-120 characters")
        if not isinstance(self.version, str) or not self.version.strip() or len(self.version) > 40:
            raise IntegrationError("version must be 1-40 characters")
        if not isinstance(self.capabilities, tuple) or not self.capabilities:
            raise IntegrationError("At least one capability is required")
        if any(not isinstance(x, IntegrationCapability) for x in self.capabilities):
            raise IntegrationError("Invalid capability entry")
        ids = [x.operation_id for x in self.capabilities]
        if len(ids) != len(set(ids)):
            raise IntegrationError("Duplicate capability operation_id")


class IntegrationAdapter(Protocol):
    """Trusted adapter contract. discover/validate must be side-effect-free.

    Credentials are resolved by the adapter through a trusted secret provider.
    execute() must honor idempotency_key for side effects: the job queue is
    at-least-once, not exactly-once.
    """
    def discover(self) -> IntegrationDescriptor: ...
    def validate(self, operation_id: str, payload: Mapping[str, Any]) -> Sequence[str]: ...
    def execute(self, operation_id: str, payload: Mapping[str, Any], *, idempotency_key: str) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class IntegrationGrant:
    adapter_id: str
    allowed_operations: frozenset[str]
    expires_at: float | None = None
    allow_write: bool = False
    allow_external: bool = False
    allow_destructive: bool = False
    approval_reference: str | None = None
    permission_verified: bool = False
    reuse_permitted: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.adapter_id, str) or not _ID.fullmatch(self.adapter_id):
            raise IntegrationError("Invalid grant adapter_id")
        if not isinstance(self.allowed_operations, frozenset) or not self.allowed_operations:
            raise IntegrationError("Grant must contain allowed operation IDs")
        if any(not isinstance(x, str) or not _ID.fullmatch(x) for x in self.allowed_operations):
            raise IntegrationError("Grant contains an invalid operation ID")
        if self.expires_at is not None and (
            not isinstance(self.expires_at, (int, float))
            or not math.isfinite(float(self.expires_at)) or self.expires_at <= 0
        ):
            raise IntegrationError("expires_at must be a finite positive timestamp")
        flags = (self.allow_write, self.allow_external, self.allow_destructive, self.permission_verified, self.reuse_permitted)
        if any(not isinstance(x, bool) for x in flags):
            raise IntegrationError("Grant permission flags must be booleans")
        if self.approval_reference is not None and (
            not isinstance(self.approval_reference, str) or len(self.approval_reference) > 160
        ):
            raise IntegrationError("Invalid approval_reference")


def _capability_fingerprint(capability: IntegrationCapability) -> str:
    """Fingerprint every capability field that can affect authorization or payload shape."""
    document = {
        "operation_id": capability.operation_id,
        "effect": capability.effect.value,
        "required_fields": list(capability.required_fields),
        "allowed_fields": list(capability.allowed_fields),
        "source_class": capability.source_class,
        "requires_reuse_permission": capability.requires_reuse_permission,
    }
    encoded = json.dumps(document, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class IntegrationPlan:
    plan_id: str
    adapter_id: str
    adapter_version: str
    operation_id: str
    effect: IntegrationEffect
    source_class: str | None
    requires_reuse_permission: bool
    mode: ExecutionMode
    idempotency_key: str
    payload_sha256: str
    capability_sha256: str
    validation_errors: tuple[str, ...]
    created_at: float
    _payload: Mapping[str, Any] = field(repr=False, compare=False)


@dataclass(frozen=True)
class IntegrationResult:
    status: str
    adapter_id: str
    operation_id: str
    plan_id: str
    payload_sha256: str
    result: Mapping[str, Any] | None = None
    reason: str | None = None


class AdapterRegistry:
    """Explicit adapter allowlist; no dynamic imports from data or manifests."""
    def __init__(self) -> None:
        self._items: dict[str, IntegrationAdapter] = {}

    def register(self, adapter_id: str, adapter: IntegrationAdapter) -> None:
        if not isinstance(adapter_id, str) or not _ID.fullmatch(adapter_id):
            raise IntegrationError("Invalid adapter_id")
        if adapter_id in self._items:
            raise IntegrationError(f"Adapter already registered: {adapter_id}")
        if not all(callable(getattr(adapter, name, None)) for name in ("discover", "validate", "execute")):
            raise IntegrationError("Adapter must implement discover, validate and execute")
        self._items[adapter_id] = adapter

    def get(self, adapter_id: str) -> IntegrationAdapter:
        try:
            return self._items[adapter_id]
        except (KeyError, TypeError) as exc:
            raise AdapterNotFound(f"No trusted adapter registered for {adapter_id!r}") from exc

    @property
    def adapter_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._items))


def _canonical_payload(payload: Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    if not isinstance(payload, Mapping):
        raise IntegrationError("payload must be a JSON object")

    def reject_secrets(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if not isinstance(key, str):
                    raise IntegrationError("Object field names must be strings")
                if _is_credential_field(key):
                    raise IntegrationError(f"Credential-like field {key!r} is not allowed")
                reject_secrets(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                reject_secrets(child)

    reject_secrets(payload)
    try:
        encoded = json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
        normalized = json.loads(encoded)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise IntegrationError(f"payload must contain JSON-compatible values: {exc}") from exc
    if not isinstance(normalized, dict):
        raise IntegrationError("payload must normalize to a JSON object")
    return normalized, hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class IntegrationEngine:
    def __init__(self, adapters: AdapterRegistry) -> None:
        if not isinstance(adapters, AdapterRegistry):
            raise IntegrationError("adapters must be an AdapterRegistry")
        self.adapters = adapters

    def discover(self, adapter_id: str) -> IntegrationDescriptor:
        descriptor = self.adapters.get(adapter_id).discover()
        if not isinstance(descriptor, IntegrationDescriptor) or descriptor.adapter_id != adapter_id:
            raise IntegrationError("Adapter returned an invalid or mismatched descriptor")
        return descriptor

    def prepare(
        self, adapter_id: str, operation_id: str, payload: Mapping[str, Any], *,
        idempotency_key: str, mode: ExecutionMode = ExecutionMode.DRY_RUN,
    ) -> IntegrationPlan:
        if not isinstance(mode, ExecutionMode):
            raise IntegrationError("mode must be an ExecutionMode")
        if not isinstance(idempotency_key, str) or not idempotency_key.strip() or len(idempotency_key) > 200:
            raise IntegrationError("idempotency_key must be non-empty and at most 200 characters")
        descriptor = self.discover(adapter_id)
        capability = next((x for x in descriptor.capabilities if x.operation_id == operation_id), None)
        if capability is None:
            raise IntegrationError(f"Undeclared operation: {operation_id!r}")
        normalized, digest = _canonical_payload(payload)
        supplied = set(normalized)
        missing = sorted(set(capability.required_fields) - supplied)
        unexpected = sorted(supplied - set(capability.allowed_fields))
        errors = []
        if missing:
            errors.append("Missing required fields: " + ", ".join(missing))
        if unexpected:
            errors.append("Unexpected fields: " + ", ".join(unexpected))
        if not missing and not unexpected:
            extra = self.adapters.get(adapter_id).validate(operation_id, normalized)
            if not isinstance(extra, Sequence) or isinstance(extra, (str, bytes)):
                raise IntegrationError("adapter.validate() must return a sequence of error strings")
            if any(not isinstance(x, str) or not x.strip() for x in extra):
                raise IntegrationError("adapter.validate() returned an invalid error")
            errors.extend(extra)
        return IntegrationPlan(
            str(uuid.uuid4()), adapter_id, descriptor.version, operation_id, capability.effect,
            capability.source_class, capability.requires_reuse_permission, mode, idempotency_key,
            digest, _capability_fingerprint(capability), tuple(errors), time.time(), normalized,
        )

    @staticmethod
    def _authorization_error(plan: IntegrationPlan, grant: IntegrationGrant | None, now: float) -> str | None:
        if grant is None:
            return "Live execution requires an explicit IntegrationGrant"
        if grant.adapter_id != plan.adapter_id:
            return "Grant is scoped to a different adapter"
        if plan.operation_id not in grant.allowed_operations:
            return "Grant does not allow this operation"
        if grant.expires_at is not None and now >= grant.expires_at:
            return "Integration grant has expired"
        if plan.effect in {IntegrationEffect.WRITE, IntegrationEffect.DESTRUCTIVE} and not grant.allow_write:
            return "Grant does not allow write operations"
        if plan.effect == IntegrationEffect.EXTERNAL and not grant.allow_external:
            return "Grant does not allow external side effects"
        if plan.effect == IntegrationEffect.READ:
            from .mission import source_access_decision
            decision = source_access_decision(
                plan.source_class or "unknown",
                permission_verified=grant.permission_verified,
                reuse_permitted=plan.requires_reuse_permission and grant.reuse_permitted,
            )
            if not decision.allowed:
                return decision.reason
            if plan.requires_reuse_permission and not decision.reuse_allowed:
                return "Source reuse permission is not verified"
        if plan.effect == IntegrationEffect.DESTRUCTIVE:
            if not grant.allow_destructive:
                return "Grant does not allow destructive operations"
            if not grant.approval_reference or not grant.approval_reference.strip():
                return "Destructive operations require an approval reference"
        return None

    def execute(
        self, plan: IntegrationPlan, *, grant: IntegrationGrant | None = None,
        now: float | None = None,
    ) -> IntegrationResult:
        if not isinstance(plan, IntegrationPlan):
            raise IntegrationError("plan must be an IntegrationPlan")
        if plan.validation_errors:
            return IntegrationResult("blocked", plan.adapter_id, plan.operation_id, plan.plan_id,
                                     plan.payload_sha256, reason="; ".join(plan.validation_errors))
        if plan.mode == ExecutionMode.DRY_RUN:
            return IntegrationResult("simulated", plan.adapter_id, plan.operation_id, plan.plan_id,
                                     plan.payload_sha256, reason="Dry run: adapter.execute() was not called")
        if plan.mode != ExecutionMode.LIVE:
            return IntegrationResult("blocked", plan.adapter_id, plan.operation_id, plan.plan_id,
                                     plan.payload_sha256, reason="Unknown execution mode")
        reason = self._authorization_error(plan, grant, time.time() if now is None else now)
        if reason:
            return IntegrationResult("blocked", plan.adapter_id, plan.operation_id, plan.plan_id,
                                     plan.payload_sha256, reason=reason)
        adapter = self.adapters.get(plan.adapter_id)
        current = self.discover(plan.adapter_id)
        capability = next((x for x in current.capabilities if x.operation_id == plan.operation_id), None)
        if current.version != plan.adapter_version or capability is None:
            return IntegrationResult("blocked", plan.adapter_id, plan.operation_id, plan.plan_id,
                                     plan.payload_sha256, reason="Adapter manifest changed; prepare again")
        if _capability_fingerprint(capability) != plan.capability_sha256:
            return IntegrationResult("blocked", plan.adapter_id, plan.operation_id, plan.plan_id,
                                     plan.payload_sha256, reason="Capability policy changed; prepare again")
        if (
            capability.effect != plan.effect
            or capability.source_class != plan.source_class
            or capability.requires_reuse_permission != plan.requires_reuse_permission
        ):
            return IntegrationResult("blocked", plan.adapter_id, plan.operation_id, plan.plan_id,
                                     plan.payload_sha256, reason="Prepared authorization metadata changed")
        payload, digest = _canonical_payload(plan._payload)
        if digest != plan.payload_sha256:
            return IntegrationResult("blocked", plan.adapter_id, plan.operation_id, plan.plan_id,
                                     plan.payload_sha256, reason="Prepared payload integrity check failed")
        supplied = set(payload)
        missing = sorted(set(capability.required_fields) - supplied)
        unexpected = sorted(supplied - set(capability.allowed_fields))
        if missing or unexpected:
            return IntegrationResult("blocked", plan.adapter_id, plan.operation_id, plan.plan_id,
                                     plan.payload_sha256, reason="Prepared payload no longer matches capability fields")
        extra = adapter.validate(plan.operation_id, payload)
        if not isinstance(extra, Sequence) or isinstance(extra, (str, bytes)):
            raise IntegrationError("adapter.validate() must return a sequence of error strings")
        if any(not isinstance(x, str) or not x.strip() for x in extra):
            raise IntegrationError("adapter.validate() returned an invalid error")
        if extra:
            return IntegrationResult("blocked", plan.adapter_id, plan.operation_id, plan.plan_id,
                                     plan.payload_sha256, reason="; ".join(extra))
        value = adapter.execute(plan.operation_id, payload, idempotency_key=plan.idempotency_key)
        if not isinstance(value, Mapping):
            raise IntegrationError("adapter.execute() must return a JSON object")
        safe_result, _ = _canonical_payload(value)
        encoded_result = json.dumps(
            safe_result, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
        if len(encoded_result) > _MAX_INTEGRATION_RESULT_BYTES:
            raise IntegrationError("Adapter result exceeds the safe integration-result size limit")
        return IntegrationResult("succeeded", plan.adapter_id, plan.operation_id, plan.plan_id,
                                 plan.payload_sha256, result=safe_result)

    def register_job_handlers(
        self,
        registry: HandlerRegistry,
        *,
        live_grants: Mapping[str, IntegrationGrant] | None = None,
    ) -> None:
        """Register discovery/planning plus optionally grant-scoped READ jobs.

        live_grants must be supplied by trusted host code, never from a job
        payload or manifest. The optional live handler refuses every operation
        that is not explicitly declared with the READ effect.
        """
        if not isinstance(registry, HandlerRegistry):
            raise IntegrationError("registry must be a HandlerRegistry")

        trusted_grants: dict[str, IntegrationGrant] = {}
        if live_grants is not None:
            if not isinstance(live_grants, Mapping):
                raise IntegrationError("live_grants must be a trusted mapping")
            for adapter_id, grant in live_grants.items():
                if (
                    not isinstance(adapter_id, str)
                    or not _ID.fullmatch(adapter_id)
                    or not isinstance(grant, IntegrationGrant)
                    or grant.adapter_id != adapter_id
                ):
                    raise IntegrationError("live_grants contains an invalid or mismatched grant")
                trusted_grants[adapter_id] = grant

        def discover_job(payload: Mapping[str, Any], context: JobContext) -> dict[str, Any]:
            try:
                descriptor = self.discover(payload.get("adapter_id"))
            except IntegrationError as exc:
                raise NonRetryableJobError(str(exc)) from exc
            return {
                "adapter_id": descriptor.adapter_id, "display_name": descriptor.display_name,
                "version": descriptor.version,
                "capabilities": [{
                    "operation_id": item.operation_id, "effect": item.effect.value,
                    "description": item.description, "required_fields": list(item.required_fields),
                    "allowed_fields": list(item.allowed_fields), "source_class": item.source_class,
                    "requires_reuse_permission": item.requires_reuse_permission,
                } for item in descriptor.capabilities],
            }

        def plan_job(payload: Mapping[str, Any], context: JobContext) -> dict[str, Any]:
            try:
                plan = self.prepare(
                    payload.get("adapter_id"), payload.get("operation_id"), payload.get("payload", {}),
                    idempotency_key=payload.get("idempotency_key", ""), mode=ExecutionMode.DRY_RUN,
                )
            except IntegrationError as exc:
                raise NonRetryableJobError(str(exc)) from exc
            result = self.execute(plan)
            return {
                "status": result.status, "adapter_id": plan.adapter_id,
                "operation_id": plan.operation_id, "payload_sha256": plan.payload_sha256,
                "validation_errors": list(plan.validation_errors), "reason": result.reason,
            }

        registry.register("integration.discover", discover_job)
        registry.register("integration.plan", plan_job)

        if trusted_grants:
            def execute_read_job(payload: Mapping[str, Any], context: JobContext) -> dict[str, Any]:
                adapter_id = payload.get("adapter_id")
                operation_id = payload.get("operation_id")
                grant = trusted_grants.get(adapter_id) if isinstance(adapter_id, str) else None
                if grant is None:
                    raise NonRetryableJobError("No trusted live-read grant is configured for this adapter")
                if not isinstance(operation_id, str):
                    raise NonRetryableJobError("operation_id must be a string")
                try:
                    descriptor = self.discover(adapter_id)
                except IntegrationError as exc:
                    raise NonRetryableJobError(str(exc)) from exc
                capability = next(
                    (item for item in descriptor.capabilities if item.operation_id == operation_id),
                    None,
                )
                if capability is None or capability.effect != IntegrationEffect.READ:
                    raise NonRetryableJobError("Live job handler permits READ capabilities only")
                operation_payload = payload.get("payload", {})
                try:
                    plan = self.prepare(
                        adapter_id,
                        operation_id,
                        operation_payload,
                        idempotency_key=context.job_id,
                        mode=ExecutionMode.LIVE,
                    )
                    outcome = self.execute(plan, grant=grant)
                except IntegrationError as exc:
                    raise NonRetryableJobError(str(exc)) from exc
                if outcome.status != "succeeded" or not isinstance(outcome.result, Mapping):
                    raise NonRetryableJobError(outcome.reason or "Read operation was blocked")
                try:
                    safe_result, _ = _canonical_payload(outcome.result)
                    encoded_result = json.dumps(
                        safe_result, ensure_ascii=False, sort_keys=True,
                        separators=(",", ":"), allow_nan=False,
                    ).encode("utf-8")
                except (IntegrationError, TypeError, ValueError) as exc:
                    raise NonRetryableJobError(f"Read result failed safe serialization: {exc}") from exc
                # Leave headroom below JobQueue.MAX_JSON_BYTES for the wrapper.
                if len(encoded_result) > 900_000:
                    raise NonRetryableJobError("Read result exceeds the safe queue-result size limit")
                return {
                    "status": outcome.status,
                    "adapter_id": adapter_id,
                    "operation_id": operation_id,
                    "payload_sha256": plan.payload_sha256,
                    "data": safe_result,
                }

            registry.register("integration.execute_read", execute_read_job)
