from __future__ import annotations

from pathlib import Path
from typing import Any

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from style.normalizer import StyleNormalizer, extract_primary_use_fact_origin

try:
    from .compose_layer3_blocks import (
        apply_compose_repairs,
        compose_facts_with_overlay_hints,
        derive_quality_flag,
        render_blocks,
    )
    from .compose_layer3_body_profile import (
        DEFAULT_RESOLVER_AUTHORITY_MODE,
        build_body_plan_sections,
        resolve_body_profile,
    )
except ImportError:
    from compose_layer3_blocks import (
        apply_compose_repairs,
        compose_facts_with_overlay_hints,
        derive_quality_flag,
        render_blocks,
    )
    from compose_layer3_body_profile import (
        DEFAULT_RESOLVER_AUTHORITY_MODE,
        build_body_plan_sections,
        resolve_body_profile,
    )


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
    resolver_authority_mode: str = DEFAULT_RESOLVER_AUTHORITY_MODE,
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
        resolver_authority_mode=resolver_authority_mode,
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
