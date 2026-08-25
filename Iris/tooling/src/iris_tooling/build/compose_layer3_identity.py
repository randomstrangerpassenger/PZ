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


def normalize_acquisition_enumeration(text: str) -> str:
    normalized = text.strip().rstrip(".!?")
    normalized = re.sub(r"이나\s+", "/", normalized)
    normalized = re.sub(r"(?<!거)나\s+", "/", normalized)
    normalized = re.sub(r"\s+(?:또는|혹은)\s+", "/", normalized)
    normalized = re.sub(r"(?:와|과)\s+", ", ", normalized)
    normalized = re.sub(r"\s*,\s*", ", ", normalized)
    normalized = re.sub(r",(?:\s*,)+", ",", normalized)
    return re.sub(r"\s+", " ", normalized).strip(" ,")


def render_acquisition_listing(text: str) -> tuple[str, list[str], str]:
    """Render one approved acquisition fact as a non-sentence DVF listing.

    The transformation is deliberately lexical: it preserves the approved
    source fact and only changes its presentation from a sentence to a
    labelled list fragment. Tooltip concerns do not participate in this
    compiler rule; runtime consumes the emitted DVF text unchanged.
    """

    normalized = text.strip().rstrip(".!?")
    if not normalized:
        raise ValueError("acquisition listing source must not be empty")

    discovery_suffix = "에서 발견된다"
    if normalized.endswith(discovery_suffix):
        values = normalize_acquisition_enumeration(
            normalized[: -len(discovery_suffix)]
        )
        if not values:
            raise ValueError("acquisition location listing must not be empty")
        return (
            f"획득 장소: {values}",
            ["lexical_surface_naturalization"],
            "candidate_acquisition_location_list_v1",
        )

    forage_suffix = "으로 구할 수 있다"
    if normalized.endswith(forage_suffix):
        values = normalize_acquisition_enumeration(
            normalized[: -len(forage_suffix)]
        )
        if not values:
            raise ValueError("mixed acquisition listing must not be empty")
        return (
            f"획득: {values}",
            ["lexical_surface_naturalization"],
            "candidate_acquisition_mixed_list_v1",
        )

    method_terminals = (
        ("제작한다", "제작"),
        ("만든다", "제작"),
        ("얻는다", "획득"),
        ("준비한다", "준비"),
        ("구한다", "획득"),
        ("수리한다", "수리"),
    )
    for terminal, nominal in method_terminals:
        if normalized.endswith(terminal):
            method = normalize_acquisition_enumeration(
                normalized[: -len(terminal)] + nominal
            )
            if not method:
                raise ValueError("acquisition method listing must not be empty")
            return (
                f"획득 방법: {method}",
                ["lexical_surface_naturalization"],
                "candidate_acquisition_method_list_v1",
            )

    raise ValueError(f"unsupported acquisition listing source: {text!r}")


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


def append_object_particle(noun: str) -> str:
    normalized = noun.strip()
    if not normalized:
        return normalized
    return f"{normalized}{'을' if has_final_consonant(normalized) else '를'}"


def realize_concrete_work_context(context: str, body: str) -> str:
    """Bind a source work-context noun to the concrete action that follows."""

    normalized_context = context.strip()
    normalized_body = body.strip()
    if normalized_context == "전자":
        if normalized_body.startswith("기기를 "):
            return f"전자 {normalized_body}"
        if normalized_body.startswith("분해하는 대상"):
            return f"전자 기기 중 {normalized_body}"
    if normalized_context == "주방":
        return f"주방에서 {normalized_body}"
    if normalized_context == "전력":
        return f"전력 공급을 위해 {normalized_body}"
    if normalized_context == "여가":
        return f"여가를 보내며 {normalized_body}"
    return f"{normalized_context}하며 {normalized_body}"


def realize_work_use_context(context: str) -> str:
    """Return a grammatical use adjunct without emitting the internal noun 작업."""

    normalized = context.strip()
    if re.search(r"(?:는|은|ㄴ)$", normalized):
        return f"{normalized} 데"
    coordination = re.fullmatch(r"(.+?)와\s+(.+)", normalized)
    if coordination:
        first, second = coordination.groups()
        if second == "흙":
            return f"{first}하거나 흙을 다룰 때"
        return f"{first}하거나 {second}할 때"
    return normalized


def naturalize_internal_work_abstraction(text: str) -> str:
    """Realize source ``작업`` through its grammatical role and concrete action."""

    normalized = text

    # Acquisition surfaces use concrete place/vehicle nouns.  ``작업장`` is a
    # public place noun and is intentionally distinct from the banned bare
    # internal abstraction ``작업``.
    normalized = re.sub(r"(?<![가-힣])작업 차량", "현장 차량", normalized)
    normalized = re.sub(r"(?<![가-힣])작업 현장", "현장", normalized)
    normalized = re.sub(r"\s+작업 구역", " 구역", normalized)
    normalized = re.sub(r"\s+작업 장소와", " 작업장과", normalized)
    normalized = re.sub(r"\s+작업 장소에서", " 작업장에서", normalized)
    normalized = re.sub(r"\s+작업 장소", " 작업장", normalized)

    # A coordinated ``A나 작업`` source means the identity serves the named
    # context and other uses.  Keep both meanings without a vague synonym.
    normalized = re.sub(
        r"^(.+?)나 작업에 함께 쓰는 (.+)$",
        r"\1에서뿐 아니라 다른 쓰임으로도 쓰는 \2",
        normalized,
    )

    # Bind a context directly to the already-declared concrete action.
    match = re.fullmatch(r"(.+?) 작업에서 (.+)", normalized)
    if match:
        normalized = realize_concrete_work_context(*match.groups())

    # A relative action followed by ``작업에 쓰는`` is naturally a ``데``
    # adjunct.  Nominal contexts retain their source label without the
    # implementation-facing abstraction.
    match = re.fullmatch(r"(.+?) 작업에 쓰는 (.+)", normalized)
    if match:
        context, body = match.groups()
        use_context = realize_work_use_context(context)
        particle = "" if use_context.endswith(("데", "때")) else "에"
        normalized = f"{use_context}{particle} 쓰는 {body}"

    match = re.fullmatch(r"(.+?) 작업에 들어가는 (.+)", normalized)
    if match:
        context, body = match.groups()
        normalized = f"{context.strip()}에 들어가는 {body.strip()}"

    match = re.fullmatch(r"(.+?) 작업에 필요한 (.+)", normalized)
    if match:
        context, body = match.groups()
        normalized = f"{context.strip()}에 필요한 {body.strip()}"

    match = re.fullmatch(r"(.+?) 작업 중 (.+)", normalized)
    if match:
        context, body = match.groups()
        normalized = f"{context.strip()} 중 {body.strip()}"

    match = re.fullmatch(r"(.+?) 작업을 준비할 때 (.+)", normalized)
    if match:
        context, body = match.groups()
        normalized = (
            f"{append_object_particle(context.strip())} 준비할 때 {body.strip()}"
        )

    match = re.fullmatch(r"(.+?) 작업으로 (.+)", normalized)
    if match:
        context, body = match.groups()
        normalized = f"{append_instrumental(context.strip())} {body.strip()}"

    match = re.fullmatch(r"(.+?) 작업에도 (.+)", normalized)
    if match:
        context, body = match.groups()
        normalized = f"{context.strip()}에도 {body.strip()}"

    match = re.fullmatch(r"(.+?) 작업을 지원한다", normalized)
    if match:
        context = match.group(1).strip()
        if context == "주방":
            normalized = "주방에서 쓴다"
        elif context == "전자":
            normalized = "전자 기기를 다룰 때 쓴다"
        else:
            normalized = f"{append_object_particle(context)} 할 때 돕는다"

    return normalized


def naturalize_source_fragment(text: str) -> tuple[str, list[str]]:
    """Apply the closed, item-independent lexical realization rewrites."""

    normalized = strip_sentence_ending(text)
    transformations: list[str] = []
    work_naturalized = naturalize_internal_work_abstraction(normalized)
    if work_naturalized != normalized:
        normalized = work_naturalized
        transformations.append("lexical_surface_naturalization")
    replacements = (
        (r"맥락에서", "상황에서"),
        (r"부품", "구성품"),
        (r"용도", "쓰임"),
        (r"^(.+?)\s+형태의\s+(.+다)$", r"\1 형태로 된 \2"),
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
            terminal_identity = re.fullmatch(
                rf"(.+?)\s+쓰는\s+{re.escape(identity)}(?:이)?다",
                use,
            )
            if terminal_identity and (
                normalize_for_contains(identity)
                in normalize_for_contains(terminal_identity.group(1))
            ):
                use = f"{terminal_identity.group(1).strip()} 쓴다"
                transformations.extend(
                    ["suppress_duplicate", "pronoun_or_zero_anaphora"]
                )
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
