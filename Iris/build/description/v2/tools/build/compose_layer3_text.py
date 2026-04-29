from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from style.normalizer import StyleNormalizer, extract_primary_use_fact_origin


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
STAGING_DIR = ROOT / "staging" / "body_role" / "phase2"
EDPAS_DIAGNOSTIC_DIR = ROOT / "staging" / "entrypoint_drift_patch_authority_seal_round" / "diagnostic"
STYLE_LOG_PATH = OUTPUT_DIR / "style_normalization_changes.jsonl"
OVERLAY_PATH = STAGING_DIR / "layer3_role_check_overlay.jsonl"
BODY_SOURCE_OVERLAY_PATH = ROOT / "staging" / "compose_contract_migration" / "layer3_body_source_overlay.jsonl"
IDENTITY_RULES_PATH = DATA_DIR / "compose_profile_identity_hint_rules.json"
PRECEDENCE_RULES_PATH = DATA_DIR / "compose_profile_conflict_precedence_rules.json"
LEGACY_PROFILES_PATH = DATA_DIR / "compose_profiles.json"
BODY_PLAN_PROFILES_PATH = DATA_DIR / "compose_profiles_v2.json"

DEFAULT_MODE = "default"
COMPAT_LEGACY_MODE = "compat_legacy"
DIAGNOSTIC_LEGACY_MODE = "diagnostic_legacy"
ENTRYPOINT_MODES = (DEFAULT_MODE, COMPAT_LEGACY_MODE, DIAGNOSTIC_LEGACY_MODE)

LEGACY_PROFILE_FALLBACK = {
    "interaction_tool": "tool_body",
    "interaction_component": "material_body",
    "interaction_output": "output_body",
}

SELECTED_ROLE_TARGET = {
    "tool": "tool_body",
    "material": "material_body",
    "output": "output_body",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_optional_jsonl_map(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    return {entry["item_id"]: entry for entry in load_jsonl(path)}


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_partial_key(non_null_slot_names: list[str]) -> str:
    if len(non_null_slot_names) == 1:
        return f"{non_null_slot_names[0]}_only"
    return "+".join(non_null_slot_names)


def render_block(block: dict[str, Any], facts: dict[str, Any]) -> str | None:
    slots = block["slots"]
    required = block["required"]

    non_null = []
    for slot_name in slots:
        value = facts.get(slot_name)
        if value is not None and str(value).strip():
            non_null.append(slot_name)

    if not non_null:
        if required:
            raise ValueError(
                f"Required block slots {slots} are all null for item '{facts.get('item_id', '?')}'"
            )
        return None

    if len(slots) == 1:
        template = block["template"]
        return template.replace(f"{{{slots[0]}}}", str(facts[slots[0]]))

    if len(non_null) == len(slots):
        template = block["template_full"]
    else:
        partial_key = build_partial_key(non_null)
        partial_templates = block.get("template_partial", {})
        if partial_key not in partial_templates:
            raise ValueError(
                f"Missing partial template key '{partial_key}' for item '{facts.get('item_id', '?')}'"
            )
        template = partial_templates[partial_key]

    rendered = template
    for slot_name in slots:
        value = facts.get(slot_name)
        if value is not None:
            rendered = rendered.replace(f"{{{slot_name}}}", str(value))
    return rendered


def has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_body_plan_profiles_v2(profiles: dict[str, Any]) -> bool:
    return profiles.get("schema_version") == "compose-profiles-v2" and isinstance(
        profiles.get("profiles"),
        dict,
    )


def overlay_semantic_quality(role_overlay: dict[str, Any] | None) -> str | None:
    if not role_overlay:
        return None
    value = role_overlay.get("semantic_quality")
    if value in {"strong", "adequate", "weak"}:
        return str(value)
    return None


def select_distinctive_mechanic_hint(facts: dict[str, Any]) -> str | None:
    for slot_name in ("processing_hint", "special_context", "limitation_hint", "notes"):
        value = facts.get(slot_name)
        if has_text(value):
            return str(value).strip()
    return None


def compose_facts_with_overlay_hints(
    *,
    facts: dict[str, Any],
    role_overlay: dict[str, Any] | None,
) -> dict[str, Any]:
    composed_facts = dict(facts)
    composed_facts["distinctive_mechanic_hint"] = None

    if not role_overlay:
        composed_facts["distinctive_mechanic_hint"] = select_distinctive_mechanic_hint(facts)
        return composed_facts

    role_check = role_overlay.get("layer3_role_check")
    body_slot_hints = role_overlay.get("body_slot_hints") or {}

    if role_check == "IDENTITY_ONLY":
        composed_facts["secondary_use"] = None
        composed_facts["distinctive_mechanic_hint"] = None
        return composed_facts

    if not body_slot_hints.get("secondary_use_present"):
        composed_facts["secondary_use"] = None

    if body_slot_hints.get("distinctive_mechanic_present"):
        composed_facts["distinctive_mechanic_hint"] = select_distinctive_mechanic_hint(facts)

    return composed_facts


def render_blocks(
    profile_blocks: list[dict[str, Any]],
    facts: dict[str, Any],
) -> list[dict[str, Any]]:
    rendered_blocks: list[dict[str, Any]] = []
    for block in profile_blocks:
        rendered = render_block(block, facts)
        if rendered is None:
            continue
        rendered_blocks.append(
            {
                "slots": tuple(block.get("slots", [])),
                "text": rendered,
            }
        )
    return rendered_blocks


def find_block_index(rendered_blocks: list[dict[str, Any]], slot_name: str) -> int | None:
    for index, block in enumerate(rendered_blocks):
        if slot_name in block["slots"]:
            return index
    return None


def move_block(rendered_blocks: list[dict[str, Any]], slot_name: str, target_index: int) -> bool:
    current_index = find_block_index(rendered_blocks, slot_name)
    if current_index is None or current_index == target_index:
        return False
    block = rendered_blocks.pop(current_index)
    rendered_blocks.insert(target_index, block)
    return True


def remove_block(rendered_blocks: list[dict[str, Any]], slot_name: str) -> bool:
    current_index = find_block_index(rendered_blocks, slot_name)
    if current_index is None:
        return False
    rendered_blocks.pop(current_index)
    return True


def is_generic_identity_echo(*, identity_hint: Any, primary_use: Any) -> bool:
    if not has_text(identity_hint) or not has_text(primary_use):
        return False
    identity = str(identity_hint).strip()
    primary = str(primary_use).strip().rstrip(".")
    return primary in {identity, f"{identity}다", f"{identity}이다"}


def apply_compose_repairs(
    *,
    rendered_blocks: list[dict[str, Any]],
    facts: dict[str, Any],
    role_overlay: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], bool]:
    repaired_blocks = list(rendered_blocks)
    acquisition_reordered = False

    if not role_overlay:
        return repaired_blocks, acquisition_reordered

    role_check = role_overlay.get("layer3_role_check")
    representative_slot = role_overlay.get("representative_slot")
    body_slot_hints = role_overlay.get("body_slot_hints") or {}
    representative_slot_override = bool(role_overlay.get("representative_slot_override"))
    semantic_quality = overlay_semantic_quality(role_overlay)

    if role_check == "IDENTITY_ONLY" and is_generic_identity_echo(
        identity_hint=facts.get("identity_hint"),
        primary_use=facts.get("primary_use"),
    ):
        remove_block(repaired_blocks, "primary_use")

    if (
        role_check == "FUNCTION_NARROW"
        and semantic_quality == "strong"
        and representative_slot == "primary_use"
    ):
        # strong + FUNCTION_NARROW rows keep semantic strong, but still repair representative focus.
        move_block(repaired_blocks, "primary_use", 0)
        remove_block(repaired_blocks, "identity_hint")

    if representative_slot_override and representative_slot == "primary_use":
        move_block(repaired_blocks, "primary_use", 0)
        remove_block(repaired_blocks, "identity_hint")

    if body_slot_hints.get("acquisition_should_trail"):
        acquisition_index = find_block_index(repaired_blocks, "acquisition_hint")
        if acquisition_index is not None and acquisition_index != len(repaired_blocks) - 1:
            acquisition_reordered = move_block(
                repaired_blocks,
                "acquisition_hint",
                len(repaired_blocks) - 1,
            )

    return repaired_blocks, acquisition_reordered


def derive_quality_flag(
    *,
    role_overlay: dict[str, Any] | None,
    acquisition_reordered: bool,
) -> str | None:
    if not role_overlay:
        return None
    role_check = role_overlay.get("layer3_role_check")
    semantic_quality = overlay_semantic_quality(role_overlay)
    if role_check == "FUNCTION_NARROW" and semantic_quality != "strong":
        return "function_narrow"
    if role_check == "IDENTITY_ONLY":
        return "identity_only"
    if role_check == "ACQ_DOMINANT" and acquisition_reordered:
        return "acq_dominant_reordered"
    return None


def derive_requeue_reason(
    *,
    role_overlay: dict[str, Any] | None,
    quality_flag: str | None,
) -> str | None:
    if not role_overlay or quality_flag is None:
        return None
    role_check = role_overlay.get("layer3_role_check")
    if quality_flag == "identity_only":
        return "NEEDS_SOURCE_EXPANSION"
    if quality_flag == "function_narrow":
        return "NEEDS_CLUSTER_REDESIGN"
    if quality_flag == "acq_dominant_reordered" or role_check == "ACQ_DOMINANT":
        return "NEEDS_COMPOSE_TUNING"
    return None


def ensure_sentence(text: str) -> str:
    normalized = text.strip()
    if not normalized:
        return normalized
    if normalized[-1] in {".", "!", "?"}:
        return normalized
    return f"{normalized}."


def has_final_consonant(text: str) -> bool:
    if not text:
        return False
    char = text[-1]
    code = ord(char)
    if not (0xAC00 <= code <= 0xD7A3):
        return False
    return ((code - 0xAC00) % 28) != 0


def append_copula(noun: str) -> str:
    normalized = noun.strip()
    if not normalized:
        return normalized
    if normalized.endswith(("다", "이다")):
        return normalized
    if has_final_consonant(normalized):
        return f"{normalized}이다"
    return f"{normalized}다"


def render_identity_core_text(identity_hint: str) -> str:
    normalized = identity_hint.strip().rstrip(".!?")
    return ensure_sentence(append_copula(normalized))


def normalize_for_contains(text: str) -> str:
    return text.replace(" ", "").strip()


def context_core(context_hint: str) -> str:
    normalized = context_hint.strip()
    if normalized.endswith(" 작업"):
        return normalized[:-3].strip()
    return normalized


def derive_context_from_primary_use(primary_use: Any) -> str | None:
    if not has_text(primary_use):
        return None
    normalized = str(primary_use).strip()
    patterns = (
        r"^(.+?)에 쓰는 .+$",
        r"^(.+?)에 함께 쓰는 .+$",
        r"^(.+?)에 들어가는 .+$",
    )
    for pattern in patterns:
        match = re.match(pattern, normalized)
        if match:
            context = match.group(1).strip()
            if context:
                return context
    return None


def primary_use_covers_context(*, primary_use: Any, context_hint: Any) -> bool:
    if not has_text(primary_use) or not has_text(context_hint):
        return False
    haystack = normalize_for_contains(str(primary_use))
    needles = {
        normalize_for_contains(str(context_hint)),
        normalize_for_contains(context_core(str(context_hint))),
    }
    return any(needle and needle in haystack for needle in needles)


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
    identity_rules_path: Path = IDENTITY_RULES_PATH,
    precedence_rules_path: Path = PRECEDENCE_RULES_PATH,
) -> tuple[dict[str, str], dict[str, Any]]:
    identity_rules = load_json(identity_rules_path)
    precedence_rules = load_json(precedence_rules_path)
    identity_hint_target_map = {
        str(key): str(value)
        for key, value in (identity_rules.get("identity_hint_profile_targets") or {}).items()
    }
    return identity_hint_target_map, precedence_rules


def resolve_body_profile(
    *,
    facts: dict[str, Any],
    decision: dict[str, Any],
    identity_hint_target_map: dict[str, str],
    precedence_rules: dict[str, Any],
) -> tuple[str, str, dict[str, Any]]:
    identity_hint = facts.get("identity_hint")
    selected_role = decision.get("selected_role")
    legacy_fallback_target = LEGACY_PROFILE_FALLBACK.get(str(decision.get("compose_profile")))
    identity_family_target = identity_hint_target_map.get(str(identity_hint))
    selected_role_target = SELECTED_ROLE_TARGET.get(str(selected_role))
    trace = {
        "identity_hint": identity_hint,
        "identity_family_target": identity_family_target,
        "selected_role": selected_role,
        "selected_role_target": selected_role_target,
        "legacy_fallback_target": legacy_fallback_target,
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


def compose_item_legacy(
    facts: dict[str, Any],
    decision: dict[str, Any],
    role_overlay: dict[str, Any] | None,
    profiles: dict[str, Any],
    normalizer: StyleNormalizer,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if decision["state"] == "silent":
        return {"text_ko": None, "source": "silent"}, None

    if decision.get("override_mode") == "text_ko":
        normalized = normalizer.normalize(
            item_id=facts["item_id"],
            text=decision["manual_override_text_ko"],
            fact_origin=extract_primary_use_fact_origin(facts),
            selected_cluster=decision.get("selected_cluster"),
            manual_override=True,
        )
        return {
            "text_ko": normalized.normalized_text,
            "source": "override",
        }, normalized.log_entry

    profile_name = decision["compose_profile"]
    if profile_name not in profiles:
        raise ValueError(f"Unknown profile '{profile_name}' for item '{facts.get('item_id', '?')}'")

    compose_facts = compose_facts_with_overlay_hints(
        facts=facts,
        role_overlay=role_overlay,
    )
    rendered_blocks = render_blocks(
        profiles[profile_name]["sentence_plan"],
        compose_facts,
    )
    repaired_blocks, acquisition_reordered = apply_compose_repairs(
        rendered_blocks=rendered_blocks,
        facts=compose_facts,
        role_overlay=role_overlay,
    )

    if not repaired_blocks:
        raise ValueError(f"No blocks rendered for active item '{facts.get('item_id', '?')}'")

    normalized = normalizer.normalize(
        item_id=facts["item_id"],
        text=" ".join(block["text"] for block in repaired_blocks),
        fact_origin=extract_primary_use_fact_origin(facts),
        selected_cluster=decision.get("selected_cluster"),
        manual_override=False,
    )
    entry = {"text_ko": normalized.normalized_text, "source": "composed"}
    quality_flag = derive_quality_flag(
        role_overlay=role_overlay,
        acquisition_reordered=acquisition_reordered,
    )
    if quality_flag is not None:
        entry["quality_flag"] = quality_flag
    return entry, normalized.log_entry


def compose_item_v2(
    facts: dict[str, Any],
    decision: dict[str, Any],
    overlay_row: dict[str, Any] | None,
    profiles: dict[str, Any],
    normalizer: StyleNormalizer,
    *,
    identity_hint_target_map: dict[str, str],
    precedence_rules: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if decision["state"] == "silent":
        return {"text_ko": None, "source": "silent"}, None

    if overlay_row is None:
        raise ValueError(
            f"Missing body_source_overlay row for active item '{facts.get('item_id', '?')}'"
        )

    if decision.get("override_mode") == "text_ko":
        normalized = normalizer.normalize(
            item_id=facts["item_id"],
            text=decision["manual_override_text_ko"],
            fact_origin=extract_primary_use_fact_origin(facts),
            selected_cluster=decision.get("selected_cluster"),
            manual_override=True,
        )
        return {
            "text_ko": normalized.normalized_text,
            "source": "override",
            "resolved_profile": None,
            "resolution_source": "manual_override",
            "coverage_quality_candidate": None,
            "body_plan": None,
        }, normalized.log_entry

    resolved_profile, resolution_source, resolution_trace = resolve_body_profile(
        facts=facts,
        decision=decision,
        identity_hint_target_map=identity_hint_target_map,
        precedence_rules=precedence_rules,
    )

    profile_spec = profiles["profiles"].get(resolved_profile)
    if profile_spec is None:
        raise ValueError(
            f"Unknown body_plan profile '{resolved_profile}' for item '{facts.get('item_id', '?')}'"
        )

    body_plan = build_body_plan_sections(
        facts=facts,
        overlay_row=overlay_row,
        profile_name=resolved_profile,
        profile_spec=profile_spec,
    )
    if not body_plan["emitted_sections"]:
        raise ValueError(f"No body_plan sections emitted for active item '{facts.get('item_id', '?')}'")

    render_rules = profiles.get("render_rules", {})
    paragraph_separator = str(render_rules.get("paragraph_separator", "\n\n"))
    emitted_texts = [section["text"] for section in body_plan["emitted_sections"]]
    if len(emitted_texts) >= int(render_rules.get("insert_when_emitted_section_count_at_least", 2)):
        text = paragraph_separator.join(emitted_texts)
    else:
        text = " ".join(emitted_texts)

    normalized = normalizer.normalize(
        item_id=facts["item_id"],
        text=text,
        fact_origin=extract_primary_use_fact_origin(facts),
        selected_cluster=decision.get("selected_cluster"),
        manual_override=False,
    )
    return {
        "text_ko": normalized.normalized_text,
        "source": "composed_v2_preview",
        "resolved_profile": resolved_profile,
        "resolution_source": resolution_source,
        "coverage_quality_candidate": body_plan["coverage_quality_candidate"],
        "body_plan": {
            "resolved_profile": body_plan["resolved_profile"],
            "emitted_sections": body_plan["emitted_sections"],
            "emitted_section_names": body_plan["emitted_section_names"],
            "missing_required_sections": body_plan["missing_required_sections"],
        },
        "profile_resolution_trace": resolution_trace,
    }, normalized.log_entry


def compose_all_legacy(
    facts_list: list[dict[str, Any]],
    decisions_list: list[dict[str, Any]],
    overlay_map: dict[str, dict[str, Any]],
    profiles: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    facts_map = {entry["item_id"]: entry for entry in facts_list}
    decisions_map = {entry["item_id"]: entry for entry in decisions_list}
    results: dict[str, dict[str, Any]] = {}
    normalization_logs: list[dict[str, Any]] = []
    requeue_candidates: list[dict[str, Any]] = []
    normalizer = StyleNormalizer()

    for item_id, decision in decisions_map.items():
        facts = dict(facts_map.get(item_id, {}))
        facts["item_id"] = item_id
        role_overlay = overlay_map.get(item_id)
        entry, log_entry = compose_item_legacy(
            facts,
            decision,
            role_overlay,
            profiles,
            normalizer,
        )
        results[item_id] = entry
        if log_entry is not None:
            normalization_logs.append(log_entry)
        quality_flag = entry.get("quality_flag")
        requeue_reason = derive_requeue_reason(
            role_overlay=role_overlay,
            quality_flag=quality_flag,
        )
        if requeue_reason is not None:
            requeue_candidates.append(
                {
                    "item_id": item_id,
                    "layer3_role_check": role_overlay["layer3_role_check"],
                    "quality_flag": quality_flag,
                    "requeue_reason": requeue_reason,
                }
            )

    return results, normalization_logs, requeue_candidates


def compose_all_v2(
    facts_list: list[dict[str, Any]],
    decisions_list: list[dict[str, Any]],
    overlay_map: dict[str, dict[str, Any]],
    profiles: dict[str, Any],
    *,
    identity_hint_target_map: dict[str, str],
    precedence_rules: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    facts_map = {entry["item_id"]: entry for entry in facts_list}
    decisions_map = {entry["item_id"]: entry for entry in decisions_list}
    results: dict[str, dict[str, Any]] = {}
    normalization_logs: list[dict[str, Any]] = []
    normalizer = StyleNormalizer()

    for item_id, decision in decisions_map.items():
        facts = dict(facts_map.get(item_id, {}))
        facts["item_id"] = item_id
        overlay_row = overlay_map.get(item_id)
        entry, log_entry = compose_item_v2(
            facts,
            decision,
            overlay_row,
            profiles,
            normalizer,
            identity_hint_target_map=identity_hint_target_map,
            precedence_rules=precedence_rules,
        )
        results[item_id] = entry
        if log_entry is not None:
            normalization_logs.append(log_entry)

    return results, normalization_logs, []


def entries_sha256(entries: dict[str, Any]) -> str:
    canonical = json.dumps(entries, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_rendered(
    facts_path: Path,
    decisions_path: Path,
    profiles_path: Path,
    output_path: Path,
    overlay_path: Path | None = OVERLAY_PATH,
    style_log_path: Path = STYLE_LOG_PATH,
    requeue_candidates_path: Path | None = None,
    identity_rules_path: Path = IDENTITY_RULES_PATH,
    precedence_rules_path: Path = PRECEDENCE_RULES_PATH,
) -> dict[str, Any]:
    facts_list = load_jsonl(facts_path)
    decisions_list = load_jsonl(decisions_path)
    profiles = load_json(profiles_path)
    overlay_map = load_optional_jsonl_map(overlay_path)
    is_v2 = is_body_plan_profiles_v2(profiles)

    if is_v2:
        identity_hint_target_map, precedence_rules = load_profile_resolution_rules(
            identity_rules_path=identity_rules_path,
            precedence_rules_path=precedence_rules_path,
        )
        entries, normalization_logs, requeue_candidates = compose_all_v2(
            facts_list,
            decisions_list,
            overlay_map,
            profiles,
            identity_hint_target_map=identity_hint_target_map,
            precedence_rules=precedence_rules,
        )
    else:
        entries, normalization_logs, requeue_candidates = compose_all_legacy(
            facts_list,
            decisions_list,
            overlay_map,
            profiles,
        )

    stats = {
        "total": len(entries),
        "active_override": sum(1 for entry in entries.values() if entry["source"] == "override"),
        "silent": sum(1 for entry in entries.values() if entry["source"] == "silent"),
    }
    if is_v2:
        resolved_profile_counts = Counter(
            entry.get("resolved_profile")
            for entry in entries.values()
            if entry.get("resolved_profile") is not None
        )
        resolution_source_counts = Counter(
            entry.get("resolution_source")
            for entry in entries.values()
            if entry.get("resolution_source") is not None
        )
        coverage_quality_candidate_counts = Counter(
            entry.get("coverage_quality_candidate")
            for entry in entries.values()
            if entry.get("coverage_quality_candidate") is not None
        )
        missing_required_section_counts = Counter()
        for entry in entries.values():
            for section_name in entry.get("body_plan", {}).get("missing_required_sections", []):
                missing_required_section_counts[str(section_name)] += 1
        stats.update(
            {
                "active_composed_v2_preview": sum(
                    1 for entry in entries.values() if entry["source"] == "composed_v2_preview"
                ),
                "resolved_profile_counts": dict(resolved_profile_counts),
                "resolution_source_counts": dict(resolution_source_counts),
                "coverage_quality_candidate_counts": dict(coverage_quality_candidate_counts),
                "missing_required_section_counts": dict(missing_required_section_counts),
            }
        )
    else:
        stats.update(
            {
                "active_composed": sum(
                    1 for entry in entries.values() if entry["source"] == "composed"
                ),
                "quality_flagged": sum(
                    1 for entry in entries.values() if entry.get("quality_flag") is not None
                ),
                "requeue_candidates": len(requeue_candidates),
            }
        )

    rendered = {
        "meta": {
            "version": "dvf-3-3-body-plan-v2-preview-v0" if is_v2 else "interaction-cluster-rendered-v0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "facts_sha256": file_sha256(facts_path),
            "decisions_sha256": file_sha256(decisions_path),
            "profiles_sha256": file_sha256(profiles_path),
            "overlay_path": str(overlay_path) if overlay_path is not None else None,
            "overlay_sha256": file_sha256(overlay_path) if overlay_path is not None and overlay_path.exists() else None,
            "entries_sha256": entries_sha256(entries),
            "stats": stats,
        },
        "entries": entries,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(rendered, handle, ensure_ascii=False, indent=2)

    style_log_path.parent.mkdir(parents=True, exist_ok=True)
    with style_log_path.open("w", encoding="utf-8") as handle:
        for log_entry in normalization_logs:
            handle.write(json.dumps(log_entry, ensure_ascii=False))
            handle.write("\n")

    if requeue_candidates_path is not None:
        write_jsonl(requeue_candidates_path, requeue_candidates)
    return rendered


def default_entrypoint_paths(mode: str) -> dict[str, Path | None]:
    if mode == DEFAULT_MODE:
        return {
            "profiles_path": BODY_PLAN_PROFILES_PATH,
            "overlay_path": BODY_SOURCE_OVERLAY_PATH,
            "output_path": OUTPUT_DIR / "dvf_3_3_rendered.json",
            "style_log_path": STYLE_LOG_PATH,
            "requeue_candidates_path": None,
        }
    if mode == COMPAT_LEGACY_MODE:
        return {
            "profiles_path": LEGACY_PROFILES_PATH,
            "overlay_path": OVERLAY_PATH,
            "output_path": OUTPUT_DIR / "dvf_3_3_rendered.json",
            "style_log_path": STYLE_LOG_PATH,
            "requeue_candidates_path": None,
        }
    if mode == DIAGNOSTIC_LEGACY_MODE:
        return {
            "profiles_path": LEGACY_PROFILES_PATH,
            "overlay_path": OVERLAY_PATH,
            "output_path": EDPAS_DIAGNOSTIC_DIR / "diagnostic_legacy_dvf_3_3_rendered.json",
            "style_log_path": EDPAS_DIAGNOSTIC_DIR / "diagnostic_legacy_style_log.jsonl",
            "requeue_candidates_path": EDPAS_DIAGNOSTIC_DIR / "diagnostic_legacy_requeue_candidates.jsonl",
        }
    raise ValueError(f"Unknown entrypoint mode: {mode}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compose Iris DVF 3-3 layer3 text.")
    parser.add_argument("--mode", choices=ENTRYPOINT_MODES, default=DEFAULT_MODE)
    parser.add_argument("--facts-path", type=Path, default=DATA_DIR / "dvf_3_3_facts.jsonl")
    parser.add_argument("--decisions-path", type=Path, default=DATA_DIR / "dvf_3_3_decisions.jsonl")
    parser.add_argument("--profiles-path", type=Path, default=None)
    parser.add_argument("--output-path", type=Path, default=None)
    parser.add_argument("--overlay-path", type=Path, default=None)
    parser.add_argument("--style-log-path", type=Path, default=None)
    parser.add_argument("--requeue-candidates-path", type=Path, default=None)
    parser.add_argument("--identity-rules-path", type=Path, default=IDENTITY_RULES_PATH)
    parser.add_argument("--precedence-rules-path", type=Path, default=PRECEDENCE_RULES_PATH)
    return parser.parse_args(argv)


def resolve_entrypoint_paths(args: argparse.Namespace) -> dict[str, Path | None]:
    defaults = default_entrypoint_paths(args.mode)
    return {
        "facts_path": args.facts_path,
        "decisions_path": args.decisions_path,
        "profiles_path": args.profiles_path or defaults["profiles_path"],
        "output_path": args.output_path or defaults["output_path"],
        "overlay_path": args.overlay_path or defaults["overlay_path"],
        "style_log_path": args.style_log_path or defaults["style_log_path"],
        "requeue_candidates_path": args.requeue_candidates_path or defaults["requeue_candidates_path"],
        "identity_rules_path": args.identity_rules_path,
        "precedence_rules_path": args.precedence_rules_path,
    }


def is_under_path(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def enforce_entrypoint_mode_contract(mode: str, paths: dict[str, Path | None]) -> None:
    profiles_path = paths["profiles_path"]
    if profiles_path is None:
        raise ValueError("profiles_path is required")
    profiles = load_json(profiles_path)
    is_v2 = is_body_plan_profiles_v2(profiles)

    if mode == DEFAULT_MODE and not is_v2:
        raise ValueError("default mode requires compose_profiles_v2.json / schema compose-profiles-v2")

    if mode in {COMPAT_LEGACY_MODE, DIAGNOSTIC_LEGACY_MODE} and is_v2:
        raise ValueError(f"{mode} mode requires an explicit legacy profile source")

    if mode == DIAGNOSTIC_LEGACY_MODE:
        for key in ("output_path", "style_log_path", "requeue_candidates_path"):
            value = paths.get(key)
            if value is not None and not is_under_path(value, EDPAS_DIAGNOSTIC_DIR):
                raise ValueError(f"diagnostic_legacy {key} must stay under {EDPAS_DIAGNOSTIC_DIR}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    paths = resolve_entrypoint_paths(args)
    enforce_entrypoint_mode_contract(args.mode, paths)
    build_rendered(
        paths["facts_path"],
        paths["decisions_path"],
        paths["profiles_path"],
        paths["output_path"],
        paths["overlay_path"],
        paths["style_log_path"],
        paths["requeue_candidates_path"],
        paths["identity_rules_path"],
        paths["precedence_rules_path"],
    )
    print("rendered written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
