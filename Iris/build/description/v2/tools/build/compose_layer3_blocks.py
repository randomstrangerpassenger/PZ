from __future__ import annotations

from typing import Any


def has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


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
