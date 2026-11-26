"""Runtime validation for the future NOEMA off-host backup manifest.

Schema validation is deliberately separate from cryptographic verification,
decryption, provider retention checks and SQLite restore validation.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "data" / "noema-backup-manifest.schema.json"


def validate_backup_manifest(document: Any, schema_path: str | Path = DEFAULT_SCHEMA) -> None:
    """Validate one metadata document against the closed Draft 2020-12 contract."""
    path = Path(schema_path)
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    if errors:
        details = []
        for error in errors:
            location = "/".join(str(part) for part in error.absolute_path) or "$"
            details.append(f"{location}: {error.message}")
        raise ValueError("backup manifest schema validation failed: " + "; ".join(details))
