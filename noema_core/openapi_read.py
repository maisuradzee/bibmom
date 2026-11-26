"""OpenAPI-driven read-only REST adapter for NOEMA.

Derives safe GET capabilities from a trusted OpenAPI 3.0/3.1 JSON document.
It never executes secured or non-GET operations and never accepts caller URLs.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import math
import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .integrations import IntegrationCapability, IntegrationDescriptor, IntegrationEffect, IntegrationError

_ID_RE = re.compile(r"^[a-z][a-z0-9_.-]{1,63}$")
_PARAM_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,63}$")
_TEMPLATE_RE = re.compile(r"\{([A-Za-z][A-Za-z0-9_]*)\}")
_ALLOWED_TYPES = {"string", "integer", "number", "boolean"}
_SECRET_KEYS = {
    "password", "passwd", "token", "access_token", "refresh_token",
    "api_key", "apikey", "secret", "client_secret", "authorization",
    "private_key",
}


class OpenAPIReadAdapterError(IntegrationError):
    """Invalid OpenAPI document, unsafe operation, or REST API response."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        return None


@dataclass(frozen=True)
class _Parameter:
    name: str
    location: str
    required: bool
    schema_type: str
    enum: tuple[Any, ...] | None = None
    min_length: int | None = None
    max_length: int | None = None
    minimum: float | None = None
    maximum: float | None = None


@dataclass(frozen=True)
class _Operation:
    operation_id: str
    raw_operation_id: str
    path_template: str
    parameters: tuple[_Parameter, ...]
    description: str


class OpenAPIReadAdapter:
    """Expose public JSON GET operations from one pinned OpenAPI 3.x API.

    The OpenAPI document and base_url are trusted host configuration. Only
    inline primitive parameter schemas are supported. Secured operations,
    non-GET methods, request bodies, external references and non-JSON success
    responses are not exposed.
    """
    def __init__(
        self,
        adapter_id: str,
        display_name: str,
        base_url: str,
        openapi_document: Mapping[str, Any],
        *,
        timeout_seconds: float = 10.0,
        max_response_bytes: int = 500_000,
        transport: Callable[[str, Mapping[str, str], float, int], tuple[int, Mapping[str, str], bytes]] | None = None,
    ) -> None:
        if not isinstance(adapter_id, str) or not _ID_RE.fullmatch(adapter_id):
            raise OpenAPIReadAdapterError("adapter_id must be a lowercase identifier")
        if not isinstance(display_name, str) or not display_name.strip() or len(display_name) > 120:
            raise OpenAPIReadAdapterError("display_name must be 1-120 characters")
        self.adapter_id = adapter_id
        self.display_name = display_name.strip()
        self.base_url = self._validate_base_url(base_url)
        if not isinstance(openapi_document, Mapping):
            raise OpenAPIReadAdapterError("openapi_document must be a JSON object")
        try:
            serialized_document = json.dumps(
                dict(openapi_document), ensure_ascii=False, allow_nan=False
            )
            if len(serialized_document.encode("utf-8")) > 2_000_000:
                raise OpenAPIReadAdapterError("OpenAPI document exceeds the 2 MB size limit")
            copied = json.loads(serialized_document)
        except (TypeError, ValueError) as exc:
            raise OpenAPIReadAdapterError("OpenAPI document must be JSON-compatible") from exc
        if not isinstance(copied, dict):
            raise OpenAPIReadAdapterError("OpenAPI document root must be an object")
        self.document = copied
        self._validate_document_version()
        self._validate_servers()
        if (
            not isinstance(timeout_seconds, (int, float))
            or isinstance(timeout_seconds, bool)
            or not math.isfinite(float(timeout_seconds))
            or not 0.1 <= timeout_seconds <= 30
        ):
            raise OpenAPIReadAdapterError("timeout_seconds must be between 0.1 and 30")
        if (
            not isinstance(max_response_bytes, int)
            or isinstance(max_response_bytes, bool)
            or not 1024 <= max_response_bytes <= 5_000_000
        ):
            raise OpenAPIReadAdapterError("max_response_bytes must be between 1 KB and 5 MB")
        if transport is not None and not callable(transport):
            raise OpenAPIReadAdapterError("transport must be callable")
        self.timeout_seconds = float(timeout_seconds)
        self.max_response_bytes = max_response_bytes
        self._transport = transport
        self._operations = self._discover_operations()
        if not self._operations:
            raise OpenAPIReadAdapterError("No safe, public JSON GET operations were found")

    @staticmethod
    def _validate_base_url(value: Any) -> str:
        if not isinstance(value, str) or not value or len(value) > 512:
            raise OpenAPIReadAdapterError("base_url must be a non-empty HTTPS URL")
        parsed = urlsplit(value)
        if parsed.scheme.lower() != "https" or not parsed.hostname:
            raise OpenAPIReadAdapterError("Only HTTPS API base URLs are supported")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise OpenAPIReadAdapterError("base_url must not include credentials, query or fragment")
        if parsed.port not in (None, 443):
            raise OpenAPIReadAdapterError("Only the default HTTPS port is supported")
        host = parsed.hostname.lower()
        if host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
            raise OpenAPIReadAdapterError("Local hostnames are not allowed")
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            address = None
        if address is not None and not address.is_global:
            raise OpenAPIReadAdapterError("Non-public IP literals are not allowed")
        path = parsed.path.rstrip("/")
        if (
            "%" in path or "\\" in path or "//" in path
            or any(x in {".", ".."} for x in path.split("/") if x)
            or (path and not re.fullmatch(r"/[A-Za-z0-9._~/-]*", path))
        ):
            raise OpenAPIReadAdapterError("base_url contains an unsafe path")
        return f"https://{parsed.netloc}{path}"

    def _validate_document_version(self) -> None:
        version = self.document.get("openapi")
        if not isinstance(version, str) or not (
            version.startswith("3.0.") or version.startswith("3.1.")
        ):
            raise OpenAPIReadAdapterError("Only OpenAPI 3.0.x and 3.1.x documents are supported")

    def _validate_servers(self) -> None:
        servers = self.document.get("servers")
        if servers is None:
            return
        if not isinstance(servers, list) or len(servers) != 1 or not isinstance(servers[0], Mapping):
            raise OpenAPIReadAdapterError("Exactly one fixed root server is supported")
        server_url = servers[0].get("url")
        if not isinstance(server_url, str) or "{" in server_url or "}" in server_url:
            raise OpenAPIReadAdapterError("Server variables are not supported")
        if self._validate_base_url(server_url) != self.base_url:
            raise OpenAPIReadAdapterError("OpenAPI server URL must match the trusted configured base_url")

    @staticmethod
    def _safe_path_template(value: Any) -> str:
        if not isinstance(value, str) or not value.startswith("/") or len(value) > 512:
            raise OpenAPIReadAdapterError("OpenAPI path must begin with '/' and be at most 512 characters")
        if value.startswith("//") or any(ch in value for ch in ("?", "#", "\\", "%", "\x00")):
            raise OpenAPIReadAdapterError("OpenAPI path contains a forbidden character")
        if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
            raise OpenAPIReadAdapterError("OpenAPI path contains control characters")
        stripped = value[1:]
        if stripped and any(segment in {"", ".", ".."} for segment in stripped.split("/")):
            raise OpenAPIReadAdapterError("OpenAPI path contains an invalid segment")
        remainder = _TEMPLATE_RE.sub("PARAM", value)
        if "{" in remainder or "}" in remainder:
            raise OpenAPIReadAdapterError("OpenAPI path contains an invalid template expression")
        if not re.fullmatch(r"/[A-Za-z0-9{}._~/-]*", value):
            raise OpenAPIReadAdapterError("OpenAPI path contains unsupported characters")
        return value

    @staticmethod
    def _schema_parameter(parameter: Mapping[str, Any]) -> _Parameter:
        name = parameter.get("name")
        location = parameter.get("in")
        required = parameter.get("required", False)
        schema = parameter.get("schema")
        if not isinstance(name, str) or not _PARAM_RE.fullmatch(name):
            raise OpenAPIReadAdapterError("parameter name is invalid")
        normalized_name = name.strip().lower().replace("-", "_")
        if normalized_name in _SECRET_KEYS or normalized_name.replace("_", "") in {
            key.replace("_", "") for key in _SECRET_KEYS
        }:
            raise OpenAPIReadAdapterError("credential-like parameters are not supported")
        if location not in {"path", "query"}:
            raise OpenAPIReadAdapterError("only path and query parameters are supported")
        if not isinstance(required, bool) or (location == "path" and not required):
            raise OpenAPIReadAdapterError("path parameters must be required")
        if not isinstance(schema, Mapping) or "$ref" in schema:
            raise OpenAPIReadAdapterError("parameters require an inline schema")
        schema_type = schema.get("type")
        if schema_type not in _ALLOWED_TYPES:
            raise OpenAPIReadAdapterError("only string, integer, number and boolean parameters are supported")
        enum_raw = schema.get("enum")
        enum = None
        if enum_raw is not None:
            if not isinstance(enum_raw, list) or not enum_raw or len(enum_raw) > 100:
                raise OpenAPIReadAdapterError("parameter enum must be a non-empty list of at most 100 values")
            enum = tuple(enum_raw)
        min_length = schema.get("minLength")
        max_length = schema.get("maxLength")
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        for label, value in (("minLength", min_length), ("maxLength", max_length)):
            if value is not None and (
                not isinstance(value, int) or isinstance(value, bool) or value < 0
            ):
                raise OpenAPIReadAdapterError(f"{label} must be a non-negative integer")
        if min_length is not None and max_length is not None and min_length > max_length:
            raise OpenAPIReadAdapterError("minLength cannot exceed maxLength")
        for label, value in (("minimum", minimum), ("maximum", maximum)):
            if value is not None and (
                not isinstance(value, (int, float)) or isinstance(value, bool)
                or not math.isfinite(float(value))
            ):
                raise OpenAPIReadAdapterError(f"{label} must be a finite number")
        if minimum is not None and maximum is not None and minimum > maximum:
            raise OpenAPIReadAdapterError("minimum cannot exceed maximum")
        if schema_type != "string" and any(x is not None for x in (min_length, max_length)):
            raise OpenAPIReadAdapterError("length constraints are supported only for strings")
        if schema_type not in {"integer", "number"} and any(x is not None for x in (minimum, maximum)):
            raise OpenAPIReadAdapterError("numeric constraints require an integer or number parameter")
        return _Parameter(name, location, required, schema_type, enum, min_length, max_length, minimum, maximum)

    @staticmethod
    def _is_json_success_response(operation: Mapping[str, Any]) -> bool:
        responses = operation.get("responses")
        if not isinstance(responses, Mapping):
            return False
        for status, response in responses.items():
            if not isinstance(status, str) or not (
                re.fullmatch(r"2\d\d", status) or status == "2XX"
            ):
                continue
            if not isinstance(response, Mapping) or "$ref" in response:
                continue
            content = response.get("content")
            if not isinstance(content, Mapping):
                continue
            for media_type in content:
                if isinstance(media_type, str):
                    normalized = media_type.split(";", 1)[0].strip().lower()
                    if normalized == "application/json" or (
                        normalized.startswith("application/") and normalized.endswith("+json")
                    ):
                        return True
        return False

    @staticmethod
    def _normalize_operation_id(raw_id: str) -> str:
        operation_id = re.sub(r"[^a-z0-9_.-]+", "-", raw_id.strip().lower()).strip("-.")
        if not operation_id or not operation_id[0].isalpha():
            operation_id = "op-" + operation_id
        if len(operation_id) < 2:
            operation_id = "op-" + operation_id
        if len(operation_id) > 64:
            operation_id = operation_id[:55].rstrip("-.") + "-" + hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:8]
        return operation_id

    def _discover_operations(self) -> dict[str, _Operation]:
        paths = self.document.get("paths")
        if not isinstance(paths, Mapping):
            raise OpenAPIReadAdapterError("OpenAPI document must contain a paths object")
        if len(paths) > 1_000:
            raise OpenAPIReadAdapterError("OpenAPI document contains more than 1,000 paths")
        root_security = self.document.get("security", [])
        if not isinstance(root_security, list):
            raise OpenAPIReadAdapterError("OpenAPI security must be an array")
        discovered: dict[str, _Operation] = {}
        for path_template, path_item in sorted(paths.items(), key=lambda item: str(item[0])):
            try:
                safe_path = self._safe_path_template(path_template)
            except OpenAPIReadAdapterError:
                continue
            if not isinstance(path_item, Mapping) or "$ref" in path_item:
                continue
            if "servers" in path_item:
                servers = path_item.get("servers")
                if (
                    not isinstance(servers, list) or len(servers) != 1
                    or not isinstance(servers[0], Mapping)
                    or servers[0].get("url") != self.base_url
                ):
                    continue
            get_operation = path_item.get("get")
            if not isinstance(get_operation, Mapping):
                continue
            if get_operation.get("deprecated") is True or "requestBody" in get_operation:
                continue
            if "servers" in get_operation:
                servers = get_operation.get("servers")
                if (
                    not isinstance(servers, list) or len(servers) != 1
                    or not isinstance(servers[0], Mapping)
                    or servers[0].get("url") != self.base_url
                ):
                    continue
            security = get_operation.get("security", root_security)
            if not isinstance(security, list) or security:
                continue
            if not self._is_json_success_response(get_operation):
                continue
            raw_id = get_operation.get("operationId")
            if not isinstance(raw_id, str) or not raw_id.strip() or len(raw_id) > 160:
                continue
            operation_id = self._normalize_operation_id(raw_id)
            if not _ID_RE.fullmatch(operation_id) or operation_id in discovered:
                continue
            path_parameters = path_item.get("parameters", [])
            operation_parameters = get_operation.get("parameters", [])
            if not isinstance(path_parameters, list) or not isinstance(operation_parameters, list):
                continue
            combined: dict[tuple[str, str], Mapping[str, Any]] = {}
            unsupported = False
            for parameter in path_parameters + operation_parameters:
                if not isinstance(parameter, Mapping) or "$ref" in parameter:
                    unsupported = True
                    break
                combined[(str(parameter.get("name")), str(parameter.get("in")))] = parameter
            if unsupported:
                continue
            parsed_parameters: list[_Parameter] = []
            names: set[str] = set()
            try:
                for parameter in combined.values():
                    parsed = self._schema_parameter(parameter)
                    if parsed.name in names:
                        raise OpenAPIReadAdapterError("duplicate parameter names across path/query are not supported")
                    if parsed.location == "query":
                        style = parameter.get("style", "form")
                        explode = parameter.get("explode", style == "form")
                        if style != "form" or explode is not True:
                            raise OpenAPIReadAdapterError("only form/explode query parameters are supported")
                    else:
                        if parameter.get("style", "simple") != "simple" or parameter.get("explode", False) is not False:
                            raise OpenAPIReadAdapterError("only simple/non-exploded path parameters are supported")
                    names.add(parsed.name)
                    parsed_parameters.append(parsed)
            except OpenAPIReadAdapterError:
                continue
            path_parameters_used = {match.group(1) for match in _TEMPLATE_RE.finditer(safe_path)}
            declared_path_parameters = {item.name for item in parsed_parameters if item.location == "path"}
            if path_parameters_used != declared_path_parameters:
                continue
            description = get_operation.get("summary") or get_operation.get("description") or raw_id
            if not isinstance(description, str):
                description = raw_id
            description = f"{raw_id}: {description.strip()}"[:300]
            if len(discovered) >= 250:
                break
            discovered[operation_id] = _Operation(
                operation_id, raw_id, safe_path, tuple(parsed_parameters), description
            )
        return discovered

    def discover(self) -> IntegrationDescriptor:
        capabilities = []
        for operation_id, operation in sorted(self._operations.items()):
            required = tuple(item.name for item in operation.parameters if item.required)
            allowed = tuple(item.name for item in operation.parameters)
            capabilities.append(
                IntegrationCapability(
                    operation_id, IntegrationEffect.READ, operation.description,
                    required, allowed, source_class="public",
                )
            )
        return IntegrationDescriptor(
            self.adapter_id, self.display_name, "openapi-3.x", tuple(capabilities)
        )

    @staticmethod
    def _validate_value(parameter: _Parameter, value: Any) -> str | None:
        if parameter.schema_type == "string":
            if not isinstance(value, str):
                return f"{parameter.name} must be a string"
            if len(value) > 2_048:
                return f"{parameter.name} exceeds the hard 2,048-character limit"
            if parameter.min_length is not None and len(value) < parameter.min_length:
                return f"{parameter.name} is shorter than minLength"
            if parameter.max_length is not None and len(value) > parameter.max_length:
                return f"{parameter.name} exceeds maxLength"
        elif parameter.schema_type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                return f"{parameter.name} must be an integer"
        elif parameter.schema_type == "number":
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
                return f"{parameter.name} must be a finite number"
        elif parameter.schema_type == "boolean":
            if not isinstance(value, bool):
                return f"{parameter.name} must be a boolean"
        if parameter.enum is not None and value not in parameter.enum:
            return f"{parameter.name} is not an allowed enum value"
        if parameter.minimum is not None and value < parameter.minimum:
            return f"{parameter.name} is below minimum"
        if parameter.maximum is not None and value > parameter.maximum:
            return f"{parameter.name} exceeds maximum"
        return None

    def validate(self, operation_id: str, payload: Mapping[str, Any]):
        operation = self._operations.get(operation_id)
        if operation is None:
            return ("operation is not declared as a safe public GET operation",)
        if not isinstance(payload, Mapping):
            return ("payload must be an object",)
        allowed = {item.name for item in operation.parameters}
        unexpected = set(payload) - allowed
        if unexpected:
            return ("unexpected parameters: " + ", ".join(sorted(str(x) for x in unexpected)),)
        errors = []
        for parameter in operation.parameters:
            if parameter.required and parameter.name not in payload:
                errors.append(f"missing required parameter: {parameter.name}")
            elif parameter.name in payload:
                message = self._validate_value(parameter, payload[parameter.name])
                if message:
                    errors.append(message)
        return tuple(errors)

    @staticmethod
    def _scalar_to_string(value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    @staticmethod
    def _contains_secret_key(value: Any) -> bool:
        if isinstance(value, Mapping):
            for key, child in value.items():
                normalized = str(key).strip().lower().replace("-", "_")
                if (
                    normalized in _SECRET_KEYS
                    or normalized.replace("_", "") in {item.replace("_", "") for item in _SECRET_KEYS}
                    or OpenAPIReadAdapter._contains_secret_key(child)
                ):
                    return True
        elif isinstance(value, list):
            return any(OpenAPIReadAdapter._contains_secret_key(child) for child in value)
        return False

    def _http_get(self, url: str) -> bytes:
        headers = {"Accept": "application/json", "User-Agent": "NOEMA-OpenAPI-Read-Adapter/0.1"}
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
                    raise OpenAPIReadAdapterError("API redirect was blocked") from exc
                if exc.code in {403, 429}:
                    raise OpenAPIReadAdapterError("API denied the request or its rate limit was reached") from exc
                raise OpenAPIReadAdapterError(f"API returned HTTP {exc.code}") from exc
            except URLError as exc:
                raise OpenAPIReadAdapterError("API network request failed") from exc
        if not isinstance(status, int) or not isinstance(response_headers, Mapping) or not isinstance(body, bytes):
            raise OpenAPIReadAdapterError("HTTP transport returned an invalid response")
        if status in {301, 302, 303, 307, 308}:
            raise OpenAPIReadAdapterError("API redirect was blocked")
        if status in {403, 429}:
            raise OpenAPIReadAdapterError("API denied the request or its rate limit was reached")
        if status != 200:
            raise OpenAPIReadAdapterError(f"API returned HTTP {status}")
        if len(body) > self.max_response_bytes:
            raise OpenAPIReadAdapterError("API response exceeded the configured size limit")
        normalized_headers = {str(key).lower(): str(value) for key, value in response_headers.items()}
        content_type = normalized_headers.get("content-type", "").split(";", 1)[0].strip().lower()
        if not (
            content_type == "application/json"
            or (content_type.startswith("application/") and content_type.endswith("+json"))
        ):
            raise OpenAPIReadAdapterError("API returned an unexpected content type")
        return body

    def execute(self, operation_id: str, payload: Mapping[str, Any], *, idempotency_key: str) -> Mapping[str, Any]:
        del idempotency_key
        errors = self.validate(operation_id, payload)
        if errors:
            raise OpenAPIReadAdapterError("; ".join(errors))
        operation = self._operations[operation_id]
        endpoint_path = operation.path_template
        query: list[tuple[str, str]] = []
        for parameter in operation.parameters:
            if parameter.name not in payload:
                continue
            value = self._scalar_to_string(payload[parameter.name])
            if parameter.location == "path":
                endpoint_path = endpoint_path.replace("{" + parameter.name + "}", quote(value, safe=""))
            else:
                query.append((parameter.name, value))
        url = self.base_url + endpoint_path
        if query:
            url += "?" + urlencode(query)
        if len(url) > 8_192:
            raise OpenAPIReadAdapterError("Constructed API URL exceeds the 8,192-character limit")
        body = self._http_get(url)
        try:
            data = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise OpenAPIReadAdapterError("API returned invalid UTF-8 JSON") from exc
        if self._contains_secret_key(data):
            raise OpenAPIReadAdapterError("API response contains a credential-like field; result was blocked")
        return data if isinstance(data, Mapping) else {"data": data}
