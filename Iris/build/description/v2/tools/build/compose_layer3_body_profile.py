from __future__ import annotations

from pathlib import Path
from typing import Any

from .compose_layer3_blocks import has_text
from .compose_layer3_identity import (
    derive_context_from_primary_use,
    ensure_sentence,
    primary_use_covers_context,
    render_identity_core_text,
)
from .compose_layer3_io import load_json


LEGACY_PROFILE_FALLBACK = {
    "interaction_tool": "tool_body",
    "interaction_component": "material_body",
    "interaction_output": "output_body",
}

ADOPTED_RUNTIME_STATE = "adopted"
UNADOPTED_RUNTIME_STATE = "unadopted"
CANONICAL_RUNTIME_STATES = frozenset({ADOPTED_RUNTIME_STATE, UNADOPTED_RUNTIME_STATE})
LEGACY_RUNTIME_STATE_ALIASES = {
    "active": ADOPTED_RUNTIME_STATE,
    "silent": UNADOPTED_RUNTIME_STATE,
}
LEGACY_RUNTIME_STATES = frozenset(LEGACY_RUNTIME_STATE_ALIASES)
DEFAULT_LEGACY_RUNTIME_STATE_ERROR_CODE = "DEFAULT_RUNTIME_STATE_REJECTED_LEGACY_ENUM"
UNKNOWN_RUNTIME_STATE_ERROR_CODE = "UNKNOWN_RUNTIME_STATE_ENUM"

DEFAULT_RESOLVER_AUTHORITY_MODE = "default"
DIAGNOSTIC_RESOLVER_AUTHORITY_MODE = "diagnostic"
RESOLVER_AUTHORITY_MODES = (
    DEFAULT_RESOLVER_AUTHORITY_MODE,
    DIAGNOSTIC_RESOLVER_AUTHORITY_MODE,
)
DEFAULT_LEGACY_COMPAT_LABEL_ERROR_CODE = "DEFAULT_RESOLVER_REJECTED_LEGACY_COMPAT_LABEL"

SELECTED_ROLE_TARGET = {
    "tool": "tool_body",
    "material": "material_body",
    "output": "output_body",
}


def is_body_plan_profiles_v2(profiles: dict[str, Any]) -> bool:
    return profiles.get("schema_version") == "compose-profiles-v2" and isinstance(
        profiles.get("profiles"),
        dict,
    )


def section_participates_in_minimums(
    *,
    profile_spec: dict[str, Any],
    minimum_key: str,
    section_name: str,
) -> bool:
    minimums = list(profile_spec.get(minimum_key, []))
    return any(section_name in minimum for minimum in minimums)


def build_context_support_section(
    *,
    facts: dict[str, Any],
    overlay_row: dict[str, Any] | None,
    profile_spec: dict[str, Any],
) -> dict[str, Any] | None:
    if overlay_row is not None:
        layer2_anchor_hint = overlay_row.get("layer2_anchor_hint")
        if has_text(layer2_anchor_hint):
            hint = str(layer2_anchor_hint).strip()
            return {
                "section": "context_support",
                "slots": ["layer2_anchor_hint"],
                "source_fields": ["body_source_overlay.layer2_anchor_hint"],
                "text": ensure_sentence(f"{hint} 맥락에서 다뤄진다"),
            }

        layer4_context_hint = overlay_row.get("layer4_context_hint")
        if has_text(layer4_context_hint):
            hint = str(layer4_context_hint).strip()
            candidate = {
                "section": "context_support",
                "slots": ["layer4_context_hint"],
                "source_fields": ["body_source_overlay.layer4_context_hint"],
                "text": ensure_sentence(f"{hint} 맥락에서 쓰인다"),
            }
            if "context_support" in profile_spec.get("required_sections", []):
                return candidate
            if section_participates_in_minimums(
                profile_spec=profile_spec,
                minimum_key="adequate_minimum_any_of",
                section_name="context_support",
            ):
                return candidate
            if primary_use_covers_context(
                primary_use=facts.get("primary_use"),
                context_hint=layer4_context_hint,
            ):
                return None
            return candidate

    context = derive_context_from_primary_use(facts.get("primary_use"))
    if not context:
        return None
    return {
        "section": "context_support",
        "slots": ["primary_use_context_restatement"],
        "source_fields": ["facts.primary_use"],
        "text": ensure_sentence(f"{context} 맥락에서 쓰인다"),
    }


def select_limitation_source(facts: dict[str, Any]) -> tuple[str | None, str | None]:
    for slot_name in ("limitation_hint", "processing_hint", "special_context", "notes"):
        value = facts.get(slot_name)
        if has_text(value):
            return str(value).strip(), slot_name
    return None, None


def derive_coverage_quality_candidate(
    profile_spec: dict[str, Any],
    emitted_section_names: list[str],
    missing_required_sections: list[str],
) -> str:
    emitted_set = set(emitted_section_names)
    if not emitted_set or emitted_set == {"identity_core"}:
        return "weak"
    if not missing_required_sections:
        for candidate in profile_spec.get("strong_minimum_any_of", []):
            if set(candidate).issubset(emitted_set):
                return "strong"
    if "identity_core" in emitted_set:
        for candidate in profile_spec.get("adequate_minimum_any_of", []):
            if set(candidate).issubset(emitted_set):
                return "adequate"
    return "weak"


def load_profile_resolution_rules(
    *,
    identity_rules_path: Path,
    precedence_rules_path: Path,
) -> tuple[dict[str, str], dict[str, Any]]:
    identity_rules = load_json(identity_rules_path)
    precedence_rules = load_json(precedence_rules_path)
    identity_hint_target_map = {
        str(key): str(value)
        for key, value in (identity_rules.get("identity_hint_profile_targets") or {}).items()
    }
    return identity_hint_target_map, precedence_rules


def is_legacy_compat_profile_label(value: Any) -> bool:
    if value is None:
        return False
    profile_name = str(value)
    return profile_name in LEGACY_PROFILE_FALLBACK or profile_name.startswith("interaction_")


def build_default_legacy_compat_label_error(*, item_id: Any, compose_profile: Any) -> ValueError:
    return ValueError(
        f"{DEFAULT_LEGACY_COMPAT_LABEL_ERROR_CODE}: item '{item_id or '?'}' "
        f"cannot resolve default body_plan authority from legacy compose_profile "
        f"'{compose_profile}'. Use diagnostic resolver mode for legacy compatibility mapping."
    )


def normalize_runtime_state(
    value: Any,
    *,
    allow_legacy: bool = False,
    item_id: Any = None,
    field_name: str = "state",
) -> str:
    state = None if value is None else str(value)
    if state in CANONICAL_RUNTIME_STATES:
        return state
    if state in LEGACY_RUNTIME_STATE_ALIASES:
        if allow_legacy:
            return LEGACY_RUNTIME_STATE_ALIASES[state]
        raise ValueError(
            f"{DEFAULT_LEGACY_RUNTIME_STATE_ERROR_CODE}: item '{item_id or '?'}' "
            f"cannot use legacy {field_name} '{state}' on the default runtime_state path"
        )
    raise ValueError(
        f"{UNKNOWN_RUNTIME_STATE_ERROR_CODE}: item '{item_id or '?'}' "
        f"has unsupported {field_name} '{state}'"
    )


def resolve_body_profile(
    *,
    facts: dict[str, Any],
    decision: dict[str, Any],
    identity_hint_target_map: dict[str, str],
    precedence_rules: dict[str, Any],
    resolver_authority_mode: str = DEFAULT_RESOLVER_AUTHORITY_MODE,
) -> tuple[str, str, dict[str, Any]]:
    if resolver_authority_mode not in RESOLVER_AUTHORITY_MODES:
        raise ValueError(f"Unknown resolver authority mode: {resolver_authority_mode}")

    identity_hint = facts.get("identity_hint")
    selected_role = decision.get("selected_role")
    compose_profile = decision.get("compose_profile")
    legacy_fallback_target = LEGACY_PROFILE_FALLBACK.get(str(compose_profile))
    identity_family_target = identity_hint_target_map.get(str(identity_hint))
    selected_role_target = SELECTED_ROLE_TARGET.get(str(selected_role))
    trace = {
        "resolver_authority_mode": resolver_authority_mode,
        "identity_hint": identity_hint,
        "identity_family_target": identity_family_target,
        "selected_role": selected_role,
        "selected_role_target": selected_role_target,
        "legacy_fallback_target": legacy_fallback_target,
        "legacy_compat_profile_label_present": is_legacy_compat_profile_label(compose_profile),
    }

    if identity_family_target and selected_role_target:
        if identity_family_target == selected_role_target:
            return identity_family_target, "identity_role_aligned", trace

        default_resolution = str(precedence_rules.get("default_resolution", "identity_family_target"))
        eligible_identity_family_targets = {
            str(value) for value in (precedence_rules.get("eligible_identity_family_targets") or [])
        }
        if (
            default_resolution == "identity_family_target"
            and identity_family_target in eligible_identity_family_targets
        ):
            return identity_family_target, "identity_family_precedence", trace
        return selected_role_target, "selected_role_precedence", trace

    if identity_family_target:
        return identity_family_target, "identity_family_target", trace
    if selected_role_target:
        return selected_role_target, "selected_role_target", trace

    if (
        resolver_authority_mode == DEFAULT_RESOLVER_AUTHORITY_MODE
        and is_legacy_compat_profile_label(compose_profile)
    ):
        raise build_default_legacy_compat_label_error(
            item_id=facts.get("item_id"),
            compose_profile=compose_profile,
        )

    if legacy_fallback_target:
        return legacy_fallback_target, "legacy_fallback_target", trace

    raise ValueError(f"Unable to resolve a body_plan profile for item '{facts.get('item_id', '?')}'")


def build_body_plan_sections(
    *,
    facts: dict[str, Any],
    overlay_row: dict[str, Any] | None,
    profile_name: str,
    profile_spec: dict[str, Any],
) -> dict[str, Any]:
    section_candidates: dict[str, dict[str, Any]] = {}

    identity_source_value = None
    identity_source_fields: list[str] = []
    if overlay_row and has_text(overlay_row.get("layer1_identity_hint")):
        identity_source_value = str(overlay_row["layer1_identity_hint"]).strip()
        identity_source_fields = ["body_source_overlay.layer1_identity_hint"]
    elif has_text(facts.get("identity_hint")):
        identity_source_value = str(facts["identity_hint"]).strip()
        identity_source_fields = ["facts.identity_hint"]
    if identity_source_value is not None:
        section_candidates["identity_core"] = {
            "section": "identity_core",
            "slots": ["identity_hint"],
            "source_fields": identity_source_fields,
            "text": render_identity_core_text(identity_source_value),
        }

    if has_text(facts.get("primary_use")):
        section_candidates["use_core"] = {
            "section": "use_core",
            "slots": ["primary_use"],
            "source_fields": ["facts.primary_use"],
            "text": ensure_sentence(str(facts["primary_use"])),
        }

    context_section = build_context_support_section(
        facts=facts,
        overlay_row=overlay_row,
        profile_spec=profile_spec,
    )
    if context_section is not None:
        section_candidates["context_support"] = context_section

    if has_text(facts.get("acquisition_hint")):
        section_candidates["acquisition_support"] = {
            "section": "acquisition_support",
            "slots": ["acquisition_hint"],
            "source_fields": ["facts.acquisition_hint"],
            "text": ensure_sentence(str(facts["acquisition_hint"])),
        }

    limitation_text, limitation_source_key = select_limitation_source(facts)
    if limitation_text is not None and limitation_source_key is not None:
        section_candidates["limitation_tail"] = {
            "section": "limitation_tail",
            "slots": [limitation_source_key],
            "source_fields": [f"facts.{limitation_source_key}"],
            "text": ensure_sentence(limitation_text),
        }

    emitted_sections: list[dict[str, Any]] = []
    for section_name in profile_spec.get("section_order", []):
        candidate = section_candidates.get(section_name)
        if candidate is not None:
            emitted_sections.append(candidate)

    emitted_section_names = [section["section"] for section in emitted_sections]
    missing_required_sections = [
        section_name
        for section_name in profile_spec.get("required_sections", [])
        if section_name not in emitted_section_names
    ]
    coverage_quality_candidate = derive_coverage_quality_candidate(
        profile_spec,
        emitted_section_names,
        missing_required_sections,
    )
    return {
        "resolved_profile": profile_name,
        "emitted_sections": emitted_sections,
        "emitted_section_names": emitted_section_names,
        "missing_required_sections": missing_required_sections,
        "coverage_quality_candidate": coverage_quality_candidate,
    }
