from __future__ import annotations

import re
import unicodedata
from typing import Any

from .compose_layer3_blocks import has_text


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


def has_final_rieul(text: str) -> bool:
    if not text:
        return False
    char = text[-1]
    code = ord(char)
    if not (0xAC00 <= code <= 0xD7A3):
        return False
    return ((code - 0xAC00) % 28) == 8


def instrumental_phonological_tail(text: str) -> str:
    """Return the final pronounced character used to select 으로/로."""

    for char in reversed(text):
        category = unicodedata.category(char)
        if char.isspace() or category.startswith("P"):
            continue
        return char
    return ""


def append_instrumental(noun: str) -> str:
    normalized = noun.strip().rstrip(".!?")
    if not normalized:
        return normalized
    phonological_tail = instrumental_phonological_tail(normalized)
    if has_final_consonant(phonological_tail) and not has_final_rieul(
        phonological_tail
    ):
        return f"{normalized}으로"
    return f"{normalized}로"


def strip_sentence_ending(text: str) -> str:
    return text.strip().rstrip(".!?").strip()


def naturalize_source_fragment(text: str) -> tuple[str, list[str]]:
    """Apply the closed, item-independent lexical realization rewrites."""

    normalized = strip_sentence_ending(text)
    transformations: list[str] = []
    # ``작업`` is a source-bearing noun, including when a Korean case particle
    # is attached.  Replacing it with ``과정`` without semantic context corrupts
    # compounds and parallel phrases, so lexical naturalization must preserve it.
    replacements = (
        (r"맥락에서", "상황에서"),
        (r"부품", "구성품"),
        (r"용도", "쓰임"),
        (r"사용된다$", "쓴다"),
        (r"활용된다$", "쓴다"),
        (r"다뤄진다$", "다룬다"),
    )
    for pattern, replacement in replacements:
        updated = re.sub(pattern, replacement, normalized)
        if updated != normalized:
            normalized = updated
            if "lexical_surface_naturalization" not in transformations:
                transformations.append("lexical_surface_naturalization")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized, transformations


def build_candidate_lead_context(
    *,
    facts: dict[str, Any],
    resolved_profile: str,
    identity_row: dict[str, Any] | None,
    use_row: dict[str, Any] | None,
    proposition_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    interaction_cluster = (
        facts.get("slot_meta", {}).get("interaction_cluster", {})
        if isinstance(facts.get("slot_meta"), dict)
        else {}
    )
    roles = sorted({str(row["role"]) for row in proposition_rows})
    food_semantic_rows = [
        row
        for row in proposition_rows
        if row.get("role") == "food_semantic"
    ]
    food_semantic_values: dict[str, list[str]] = {}
    for row in food_semantic_rows:
        axis = str(row.get("food_semantic_axis") or "")
        value = str(row.get("food_semantic_value") or "")
        if axis and value:
            food_semantic_values.setdefault(axis, []).append(value)
    food_semantic_values = {
        axis: sorted(set(values))
        for axis, values in sorted(food_semantic_values.items())
    }
    return {
        "resolved_profile": resolved_profile,
        "identity_semantic_key": (
            str(identity_row["semantic_key"]) if identity_row is not None else None
        ),
        "use_semantic_key": (
            str(use_row["semantic_key"]) if use_row is not None else None
        ),
        "identity_source_field": (
            str(identity_row["source_field"]) if identity_row is not None else None
        ),
        "use_source_field": (
            str(use_row["source_field"]) if use_row is not None else None
        ),
        "identity_fact_origin": (
            list(identity_row.get("fact_origin", []))
            if identity_row is not None
            else []
        ),
        "use_fact_origin": (
            list(use_row.get("fact_origin", [])) if use_row is not None else []
        ),
        "item_family": interaction_cluster.get("selected_cluster"),
        "item_subtype": (
            facts.get("item_subtype")
            or interaction_cluster.get("selected_subtype")
            or interaction_cluster.get("item_subtype")
        ),
        "acquisition_present": "acquisition" in roles,
        "limitation_present": "limitation" in roles,
        "role_combination": roles,
        "food_semantic_values": food_semantic_values,
        "food_semantic_proposition_ids": sorted(
            str(row["proposition_id"]) for row in food_semantic_rows
        ),
    }


def _has_semantic_tokens(text: str, *tokens: str) -> bool:
    return all(token in text for token in tokens)


def _food_semantic_lead(
    values_by_axis: dict[str, list[str]],
) -> tuple[str, str] | None:
    """Realize exact approved semantic combinations without item-specific routing."""

    semantic_pairs = frozenset(
        (axis, value)
        for axis, values in values_by_axis.items()
        for value in values
    )
    if not semantic_pairs:
        return None
    exact_realizations: dict[
        frozenset[tuple[str, str]],
        tuple[str, str],
    ] = {
        frozenset(
            {
                ("consumption_form", "solid_food"),
                ("meal_role", "snack"),
            }
        ): (
            "간식으로 먹고 나눌 수 있는 식품이다.",
            "candidate_lead_food_solid_snack_v1",
        ),
        frozenset(
            {
                ("consumption_form", "solid_food"),
                ("meal_role", "component"),
            }
        ): (
            "식사의 한 부분으로 먹는 식품이다.",
            "candidate_lead_food_solid_component_v1",
        ),
        frozenset(
            {
                ("consumption_form", "ingredient_component"),
                ("meal_role", "ingredient"),
            }
        ): (
            "음식에 넣어 쓰는 재료다.",
            "candidate_lead_food_ingredient_v1",
        ),
        frozenset(
            {
                ("consumption_form", "ingredient_component"),
                ("meal_role", "ingredient"),
                ("preparation_requirement", "cooking_declared"),
            }
        ): (
            "조리 과정에서 음식에 넣는 재료다.",
            "candidate_lead_food_cooked_ingredient_v1",
        ),
        frozenset(
            {
                ("consumption_form", "solid_food"),
                ("meal_role", "meal"),
            }
        ): (
            "한 끼 식사로 먹을 수 있는 식품이다.",
            "candidate_lead_food_solid_meal_v1",
        ),
        frozenset(
            {
                ("consumption_form", "solid_food"),
                ("meal_role", "component"),
                ("preparation_requirement", "cooking_declared"),
            }
        ): (
            "조리해 식사의 한 부분으로 먹는 식품이다.",
            "candidate_lead_food_cooked_component_v1",
        ),
        frozenset(
            {
                ("consumption_form", "ingredient_component"),
                ("culinary_role", "herbal_infusion_component"),
                ("meal_role", "ingredient"),
            }
        ): (
            "우려서 음료를 만들 때 쓰는 재료다.",
            "candidate_lead_food_infusion_ingredient_v1",
        ),
        frozenset(
            {
                ("consumption_form", "ingredient_component"),
                ("meal_role", "ingredient"),
                ("preservation_form", "dried"),
            }
        ): (
            "말린 상태로 음식에 넣어 쓰는 재료다.",
            "candidate_lead_food_dried_ingredient_v1",
        ),
        frozenset(
            {
                ("consumption_form", "ingredient_component"),
                ("culinary_role", "baking_fat"),
                ("meal_role", "ingredient"),
            }
        ): (
            "제과나 제빵에 지방 재료로 넣어 쓴다.",
            "candidate_lead_food_baking_fat_v1",
        ),
        frozenset(
            {
                ("consumption_form", "ingredient_component"),
                ("culinary_role", "sweetener"),
                ("meal_role", "ingredient"),
            }
        ): (
            "음식에 단맛을 더하는 재료다.",
            "candidate_lead_food_sweetener_v1",
        ),
        frozenset(
            {
                ("consumption_form", "ingredient_component"),
                ("culinary_role", "baking_fat"),
                ("culinary_role", "minor_ingredient"),
                ("meal_role", "ingredient"),
            }
        ): (
            "제과나 제빵에 지방 부재료로 넣어 쓴다.",
            "candidate_lead_food_baking_fat_minor_v1",
        ),
        frozenset(
            {
                ("consumption_form", "solid_food"),
                ("meal_role", "meal"),
                ("preparation_requirement", "cooking_declared"),
            }
        ): (
            "조리해 한 끼 식사로 먹는 식품이다.",
            "candidate_lead_food_cooked_meal_v1",
        ),
        frozenset(
            {
                ("consumption_form", "ingredient_component"),
                ("culinary_role", "minor_ingredient"),
                ("meal_role", "ingredient"),
            }
        ): (
            "음식에 부재료로 넣어 쓴다.",
            "candidate_lead_food_minor_ingredient_v1",
        ),
        frozenset(
            {
                ("consumption_form", "solid_food"),
                ("meal_role", "component"),
                ("preparation_requirement", "cooking_declared"),
                ("preparation_state", "already_cooked"),
            }
        ): (
            "이미 조리되어 식사의 한 부분으로 먹는 식품이다.",
            "candidate_lead_food_already_cooked_component_v1",
        ),
        frozenset(
            {
                ("consumption_form", "beverage"),
                ("meal_role", "snack"),
            }
        ): (
            "간식으로 마시는 음료다.",
            "candidate_lead_food_beverage_snack_v1",
        ),
        frozenset(
            {
                ("consumption_form", "solid_food"),
                ("meal_role", "snack"),
                ("preservation_form", "freezing_supported"),
            }
        ): (
            "얼려 보관할 수 있고 간식으로 먹는 식품이다.",
            "candidate_lead_food_freezable_snack_v1",
        ),
        frozenset(
            {
                ("consumption_form", "ingredient_component"),
                ("culinary_role", "herb"),
                ("culinary_role", "herbal_infusion_component"),
                ("culinary_role", "spice"),
                ("meal_role", "ingredient"),
            }
        ): (
            "허브와 향신료로 우려 마시는 데 쓰는 재료다.",
            "candidate_lead_food_herb_spice_infusion_v1",
        ),
    }
    exact = exact_realizations.get(semantic_pairs)
    if exact is not None:
        return exact
    forms = set(values_by_axis.get("consumption_form", []))
    meal_roles = set(values_by_axis.get("meal_role", []))
    if "beverage" in forms:
        return (
            "마실 수 있는 음료다.",
            "candidate_lead_food_beverage_generic_v1",
        )
    if "ingredient_component" in forms or "ingredient" in meal_roles:
        return (
            "음식에 재료로 넣어 쓴다.",
            "candidate_lead_food_ingredient_generic_v1",
        )
    if "meal" in meal_roles:
        return (
            "식사로 먹을 수 있는 식품이다.",
            "candidate_lead_food_meal_generic_v1",
        )
    if "component" in meal_roles:
        return (
            "식사의 한 부분으로 먹는 식품이다.",
            "candidate_lead_food_component_generic_v1",
        )
    return (
        "먹을 수 있는 식품이다.",
        "candidate_lead_food_solid_generic_v1",
    )


def select_candidate_lead_realization(
    *,
    identity_text: str | None,
    use_text: str | None,
    lead_context: dict[str, Any] | None = None,
) -> tuple[str, list[str], str]:
    identity, identity_transformations = naturalize_source_fragment(
        identity_text or ""
    )
    use, transformations = naturalize_source_fragment(use_text or "")
    transformations = list(dict.fromkeys([*identity_transformations, *transformations]))
    context = lead_context or {}
    profile = str(context.get("resolved_profile") or "")
    family = str(context.get("item_family") or "")
    semantic_transformations = [
        *transformations,
        "reorder",
        "copula_adjustment",
    ]
    food_realization = _food_semantic_lead(
        context.get("food_semantic_values", {})
        if isinstance(context.get("food_semantic_values"), dict)
        else {}
    )
    if (
        food_realization is not None
        and identity == "식품"
        and profile == "consumable_body"
        and family == "food_consumption"
    ):
        text, rule_id = food_realization
        return (
            text,
            list(dict.fromkeys(semantic_transformations)),
            rule_id,
        )
    if (
        identity == "식품"
        and profile == "consumable_body"
        and family == "food_consumption"
        and _has_semantic_tokens(use, "조리", "식사 준비", "먹", "나눠")
    ):
        return (
            "조리하거나 식사를 준비할 때 먹고 나눌 수 있는 식품이다.",
            list(dict.fromkeys(semantic_transformations)),
            "candidate_lead_food_consumption_nominal_v1",
        )
    if _has_semantic_tokens(use, "착용", "몸에 장식", "시야 보조"):
        return (
            ensure_sentence(
                f"몸을 장식하거나 시야를 보조하려고 착용하는 {append_copula(identity)}"
            ),
            list(dict.fromkeys(semantic_transformations)),
            "candidate_lead_wearable_purpose_nominal_v1",
        )
    if _has_semantic_tokens(use, "조리 준비", "재료를 담거나", "섞고", "익히기 전"):
        return (
            ensure_sentence(
                f"재료를 담거나 섞고 익히기 전에 다루는 {append_copula(identity)}"
            ),
            list(dict.fromkeys(semantic_transformations)),
            "candidate_lead_cooking_preparation_nominal_v1",
        )
    if _has_semantic_tokens(use, "차량 정비", "좌석이나 적재 모듈", "분리", "다시 끼"):
        return (
            ensure_sentence(
                "차량을 정비하며 좌석이나 적재 모듈을 분리하거나 "
                f"다시 끼울 때 다루는 {append_copula(identity)}"
            ),
            list(dict.fromkeys(semantic_transformations)),
            "candidate_lead_vehicle_seat_storage_nominal_v1",
        )
    if _has_semantic_tokens(use, "차량 정비", "차체 패널이나 유리", "떼어내", "다시 끼"):
        return (
            ensure_sentence(
                "차량을 정비하며 차체 패널이나 유리를 떼어내거나 "
                f"다시 끼울 때 다루는 {append_copula(identity)}"
            ),
            list(dict.fromkeys(semantic_transformations)),
            "candidate_lead_vehicle_panel_glass_nominal_v1",
        )
    if _has_semantic_tokens(use, "차량 정비", "배터리", "전기 계통", "복구"):
        return (
            ensure_sentence(
                "차량을 정비하며 배터리를 연결하거나 교체해 전기 계통을 "
                f"복구할 때 다루는 {append_copula(identity)}"
            ),
            list(dict.fromkeys(semantic_transformations)),
            "candidate_lead_vehicle_battery_nominal_v1",
        )
    if _has_semantic_tokens(use, "설비 배치", "기기나 고정 설비", "떼어내", "다시 설치"):
        return (
            ensure_sentence(
                "기기나 고정 설비를 떼어내거나 다시 설치할 때 "
                f"다루는 {append_copula(identity)}"
            ),
            list(dict.fromkeys(semantic_transformations)),
            "candidate_lead_equipment_placement_nominal_v1",
        )
    if _has_semantic_tokens(use, "손목", "시간을 확인", "알람"):
        return (
            ensure_sentence(
                "손목에 차고 시간을 확인하거나 알람을 맞출 때 "
                f"다루는 {append_copula(identity)}"
            ),
            list(dict.fromkeys(semantic_transformations)),
            "candidate_lead_wristwatch_nominal_v1",
        )
    if _has_semantic_tokens(use, "즉석 폭발물", "내용물을 담거나", "분사성 재료", "조합"):
        return (
            ensure_sentence(
                "즉석 폭발물을 만들며 내용물을 담거나 분사성 재료를 "
                f"조합할 때 쓰는 {append_copula(identity)}"
            ),
            list(dict.fromkeys(semantic_transformations)),
            "candidate_lead_improvised_explosive_material_nominal_v1",
        )
    if use:
        if (
            identity
            and use.replace(" ", "").count(identity.replace(" ", "")) > 1
        ):
            reduced = re.sub(
                rf"^{re.escape(identity)}\s+",
                "",
                use,
                count=1,
            ).strip()
            if reduced and reduced != use:
                use = reduced
                transformations.append("pronoun_or_zero_anaphora")
        if identity and normalize_for_contains(identity) not in normalize_for_contains(use):
            transformations.append("particle_adjustment")
            return (
                ensure_sentence(f"{append_instrumental(identity)}, {use}"),
                transformations,
                "candidate_lead_identity_use_instrumental_v1",
            )
        if identity:
            transformations.append("pronoun_or_zero_anaphora")
        return ensure_sentence(use), transformations, "candidate_lead_use_direct_v1"
    return (
        render_identity_core_text(identity),
        transformations,
        "candidate_lead_identity_direct_v1",
    )


def render_candidate_lead(
    *,
    identity_text: str | None,
    use_text: str | None,
    lead_context: dict[str, Any] | None = None,
) -> tuple[str, list[str]]:
    text, transformations, _ = select_candidate_lead_realization(
        identity_text=identity_text,
        use_text=use_text,
        lead_context=lead_context,
    )
    return text, transformations


def apply_identity_zero_anaphora(
    *,
    text: str,
    identity_text: str | None,
    antecedent_text: str,
) -> tuple[str, bool]:
    identity, _ = naturalize_source_fragment(identity_text or "")
    if not identity or identity not in antecedent_text or identity not in text:
        return text, False
    updated = re.sub(
        rf"^{re.escape(identity)}(?:을|를|은|는|이|가)?\s*",
        "",
        text,
        count=1,
    ).strip()
    if updated == text or not updated:
        return text, False
    return updated, True


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
