"""Validated mission, source-access and autonomy policies for NOEMA.

This module intentionally has no network access and no secret-handling code.
Connectors must enforce these decisions at their own boundaries.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


DEFAULT_MISSION_PATH = Path(__file__).with_name("mission.json")


class MissionConfigurationError(ValueError):
    """Raised when the foundational mission configuration is invalid."""


@dataclass(frozen=True)
class AccessDecision:
    allowed: bool
    reuse_allowed: bool
    reason: str


@dataclass(frozen=True)
class AutonomyDecision:
    mode: str
    reason: str


def _string_list(value: Any, field_name: str) -> set[str]:
    if not isinstance(value, list) or not value:
        raise MissionConfigurationError(f"{field_name} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise MissionConfigurationError(f"{field_name} must contain non-empty strings")
    if len(value) != len(set(value)):
        raise MissionConfigurationError(f"{field_name} must not contain duplicates")
    return set(value)


def validate_mission_config(config: Mapping[str, Any]) -> None:
    """Validate the machine-readable charter and safety policy."""
    if config.get("schema_version") != 1:
        raise MissionConfigurationError("Unsupported mission schema_version")

    identity = config.get("identity")
    mission = config.get("mission")
    if not isinstance(identity, Mapping) or identity.get("name") != "NOEMA":
        raise MissionConfigurationError("identity.name must be NOEMA")
    if not isinstance(mission, Mapping):
        raise MissionConfigurationError("mission must be an object")
    for key in ("declaration_ka", "purpose", "vision"):
        value = mission.get(key)
        if not isinstance(value, str) or not value.strip():
            raise MissionConfigurationError(f"mission.{key} must be a non-empty string")

    access = config.get("knowledge_access")
    if not isinstance(access, Mapping):
        raise MissionConfigurationError("knowledge_access must be an object")
    allowed_classes = _string_list(
        access.get("allowed_retrieval_classes"),
        "knowledge_access.allowed_retrieval_classes",
    )
    permission_classes = _string_list(
        access.get("permission_required_classes"),
        "knowledge_access.permission_required_classes",
    )
    denied_classes = _string_list(
        access.get("denied_classes"),
        "knowledge_access.denied_classes",
    )
    if allowed_classes & denied_classes:
        raise MissionConfigurationError("source classes cannot be both allowed and denied")
    if not permission_classes <= allowed_classes:
        raise MissionConfigurationError("permission-required classes must be allowed classes")
    if not {"public", "licensed", "user_authorized"} <= allowed_classes:
        raise MissionConfigurationError("required lawful source classes are missing")
    if not {"restricted", "unknown", "unauthorized"} <= denied_classes:
        raise MissionConfigurationError("denied source classes are missing")

    autonomy = config.get("autonomy")
    if not isinstance(autonomy, Mapping):
        raise MissionConfigurationError("autonomy must be an object")
    autonomous = _string_list(
        autonomy.get("autonomous_actions"),
        "autonomy.autonomous_actions",
    )
    conditional = autonomy.get("conditional_actions")
    if not isinstance(conditional, Mapping) or not conditional:
        raise MissionConfigurationError("autonomy.conditional_actions must be a non-empty object")
    conditional_actions = set(conditional)
    if any(not isinstance(item, str) or not item for item in conditional_actions):
        raise MissionConfigurationError("conditional action names must be non-empty strings")
    review_required = _string_list(
        autonomy.get("review_required_actions"),
        "autonomy.review_required_actions",
    )
    if autonomous & review_required or autonomous & conditional_actions or review_required & conditional_actions:
        raise MissionConfigurationError("autonomy action classes must be mutually exclusive")
    if autonomy.get("unknown_action_default") != "blocked":
        raise MissionConfigurationError("unknown actions must default to blocked")

    stages = _string_list(config.get("innovation_cycle"), "innovation_cycle")
    if len(stages) < 5:
        raise MissionConfigurationError("innovation_cycle must contain at least five stages")
    _string_list(config.get("claim_classes"), "claim_classes")


def load_mission(path: str | Path | None = None) -> dict[str, Any]:
    """Load and validate the mission configuration."""
    mission_path = Path(path) if path is not None else DEFAULT_MISSION_PATH
    try:
        config = json.loads(mission_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MissionConfigurationError(f"Cannot load mission configuration: {exc}") from exc
    if not isinstance(config, dict):
        raise MissionConfigurationError("Mission configuration root must be an object")
    validate_mission_config(config)
    return config


def source_access_decision(
    source_class: str,
    *,
    permission_verified: bool = False,
    reuse_permitted: bool = False,
    mission: Mapping[str, Any] | None = None,
) -> AccessDecision:
    """Decide whether a connector may retrieve and/or reuse a source.

    Public availability is not treated as blanket permission to republish.
    Licensed and user-authorized sources require verified permission.
    Unknown and restricted sources fail closed.
    """
    config = mission if mission is not None else load_mission()
    validate_mission_config(config)
    access = config["knowledge_access"]
    source_class = source_class.strip().lower() if isinstance(source_class, str) else ""

    if source_class in access["denied_classes"]:
        return AccessDecision(False, False, f"Source class '{source_class}' is denied by policy.")
    if source_class not in access["allowed_retrieval_classes"]:
        return AccessDecision(False, False, "Unknown source class; access is denied by default.")

    permission_required = source_class in access["permission_required_classes"]
    if permission_required and not permission_verified:
        return AccessDecision(False, False, "Verified permission is required before retrieval.")

    if reuse_permitted and not permission_verified:
        return AccessDecision(
            True,
            False,
            "Retrieval is allowed, but reuse is denied because reuse rights are not verified.",
        )
    return AccessDecision(
        True,
        bool(reuse_permitted),
        "Retrieval is allowed; reuse is allowed only when separate reuse permission is verified."
        if not reuse_permitted
        else "Retrieval and reuse are allowed under the verified source permission.",
    )


def autonomy_decision(
    action_class: str,
    *,
    all_quality_gates_passed: bool = False,
    mission: Mapping[str, Any] | None = None,
) -> AutonomyDecision:
    """Return the permitted autonomy level; unknown operations fail closed."""
    config = mission if mission is not None else load_mission()
    validate_mission_config(config)
    autonomy = config["autonomy"]
    action = action_class.strip() if isinstance(action_class, str) else ""

    if action in autonomy["review_required_actions"]:
        return AutonomyDecision(
            "review_required",
            "This action requires an independent or authorized review before execution.",
        )

    conditional = autonomy["conditional_actions"]
    if action in conditional:
        required_gate = conditional[action]
        if required_gate == "all_quality_gates_passed" and all_quality_gates_passed:
            return AutonomyDecision(
                "autonomous",
                "The conditional action is permitted because all required quality gates passed.",
            )
        return AutonomyDecision(
            "blocked",
            "The conditional action is blocked until every required quality gate passes.",
        )

    if action in autonomy["autonomous_actions"]:
        return AutonomyDecision("autonomous", "This is an approved internal autonomous action.")

    return AutonomyDecision(
        "blocked",
        "Unknown action; the default policy is to block rather than guess.",
    )
