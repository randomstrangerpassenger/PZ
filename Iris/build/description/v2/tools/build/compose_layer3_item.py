from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.style.normalizer import StyleNormalizer, extract_primary_use_fact_origin

from .compose_layer3_blocks import (
    apply_compose_repairs,
    compose_facts_with_overlay_hints,
    derive_quality_flag,
    render_blocks,
)
from .compose_layer3_body_profile import (
    DEFAULT_RESOLVER_AUTHORITY_MODE,
    UNADOPTED_RUNTIME_STATE,
    build_single_proposition_equivalence_proof,
    build_body_plan_sections,
    normalize_runtime_state,
    resolve_body_profile,
)
from .compose_layer3_identity import (
    apply_identity_zero_anaphora,
    build_candidate_lead_context,
    derive_context_from_primary_use,
    ensure_sentence,
    naturalize_source_fragment,
    select_candidate_lead_realization,
)


def compose_item_legacy(
    facts: dict[str, Any],
    decision: dict[str, Any],
    role_overlay: dict[str, Any] | None,
    profiles: dict[str, Any],
    normalizer: StyleNormalizer,
    *,
    allow_legacy_runtime_state: bool = False,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    runtime_state = normalize_runtime_state(
        decision.get("state"),
        allow_legacy=allow_legacy_runtime_state,
        item_id=facts.get("item_id"),
    )
    if runtime_state == UNADOPTED_RUNTIME_STATE:
        return {"text_ko": None, "source": UNADOPTED_RUNTIME_STATE}, None

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
        raise ValueError(f"No blocks rendered for adopted item '{facts.get('item_id', '?')}'")

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
    allow_legacy_runtime_state: bool = False,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    runtime_state = normalize_runtime_state(
        decision.get("state"),
        allow_legacy=allow_legacy_runtime_state,
        item_id=facts.get("item_id"),
    )
    if runtime_state == UNADOPTED_RUNTIME_STATE:
        return {"text_ko": None, "source": UNADOPTED_RUNTIME_STATE}, None

    if overlay_row is None:
        raise ValueError(
            f"Missing body_source_overlay row for adopted item '{facts.get('item_id', '?')}'"
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
        raise ValueError(f"No body_plan sections emitted for adopted item '{facts.get('item_id', '?')}'")

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


def _candidate_clause(
    *,
    item_id: str,
    clause_index: int,
    text: str,
    proposition_rows: list[dict[str, Any]],
    relation: str,
    ordering_reason: str,
    realization_rule_id: str,
    transformation_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "item_id": item_id,
        "clause_id": f"{item_id}#clause-{clause_index:03d}",
        "text": ensure_sentence(text),
        "proposition_ids": [
            str(row["proposition_id"]) for row in proposition_rows
        ],
        "relation": relation,
        "ordering_reason": ordering_reason,
        "merge_reason": (
            "identity_and_use_share_one_natural_lead"
            if relation == "identity_use_fusion"
            else None
        ),
        "suppression_reason": None,
        "paragraph_id": None,
        "realization_rule_id": realization_rule_id,
        "transformation_ids": list(transformation_ids or []),
    }


def compose_item_candidate(
    facts: dict[str, Any],
    decision: dict[str, Any],
    profiles: dict[str, Any],
    *,
    identity_hint_target_map: dict[str, str],
    precedence_rules: dict[str, Any],
    proposition_rows: list[dict[str, Any]],
    requirement_rows: list[dict[str, Any]],
    policy: dict[str, Any],
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    item_id = str(facts["item_id"])
    runtime_state = normalize_runtime_state(
        decision.get("state"),
        item_id=item_id,
    )
    resolved_profile, resolution_source, resolution_trace = resolve_body_profile(
        facts=facts,
        decision=decision,
        identity_hint_target_map=identity_hint_target_map,
        precedence_rules=precedence_rules,
    )
    if runtime_state == UNADOPTED_RUNTIME_STATE:
        resolutions = [
            {
                "item_id": item_id,
                "proposition_id": row["proposition_id"],
                "proposition_resolution": "not_applicable",
                "not_applicable_reason": "profile_exclusion",
                "clause_ids": [],
                "equivalence_proof_id": None,
            }
            for row in proposition_rows
        ]
        structural = [
            {
                **row,
                "status": "not_required",
                "clause_ids": [],
                "equivalence_proof_id": None,
                "missing_reason": "unadopted_item_not_in_candidate_emission_universe",
            }
            for row in requirement_rows
        ]
        return (
            {
                "text_ko": None,
                "source": UNADOPTED_RUNTIME_STATE,
                "resolved_profile": resolved_profile,
                "resolution_source": resolution_source,
                "coverage_quality_candidate": None,
                "body_plan": None,
                "profile_resolution_trace": resolution_trace,
            },
            [],
            structural,
            resolutions,
            [],
        )

    by_role: dict[str, list[dict[str, Any]]] = {}
    for row in sorted(proposition_rows, key=lambda value: str(value["proposition_id"])):
        by_role.setdefault(str(row["role"]), []).append(row)

    clauses: list[dict[str, Any]] = []
    identity_rows = by_role.get("identity", [])
    use_rows = by_role.get("use", [])
    food_semantic_rows = by_role.get("food_semantic", [])
    lead_rows = identity_rows[:1] + use_rows[:1] + food_semantic_rows
    if lead_rows:
        lead_context = build_candidate_lead_context(
            facts=facts,
            resolved_profile=resolved_profile,
            identity_row=identity_rows[0] if identity_rows else None,
            use_row=use_rows[0] if use_rows else None,
            proposition_rows=proposition_rows,
        )
        lead, transformations, lead_rule_id = select_candidate_lead_realization(
            identity_text=(
                str(identity_rows[0]["source_value"]) if identity_rows else None
            ),
            use_text=str(use_rows[0]["source_value"]) if use_rows else None,
            lead_context=lead_context,
        )
        clauses.append(
            _candidate_clause(
                item_id=item_id,
                clause_index=len(clauses) + 1,
                text=lead,
                proposition_rows=lead_rows,
                relation=(
                    "identity_use_fusion"
                    if identity_rows and use_rows
                    else "direct_realization"
                ),
                ordering_reason="profile_lead_role_priority",
                realization_rule_id=lead_rule_id,
                transformation_ids=(
                    ["paragraph_merge", *transformations]
                    if identity_rows and use_rows
                    else transformations
                ),
            )
        )

    consumed_ids = {str(row["proposition_id"]) for row in lead_rows}
    for role in ("use", "context", "limitation", "acquisition"):
        for row in by_role.get(role, []):
            if str(row["proposition_id"]) in consumed_ids:
                continue
            text, transformations = naturalize_source_fragment(
                str(row["source_value"])
            )
            antecedent = " ".join(str(clause["text"]) for clause in clauses)
            text, zero_anaphora_applied = apply_identity_zero_anaphora(
                text=text,
                identity_text=(
                    str(identity_rows[0]["source_value"])
                    if identity_rows
                    else None
                ),
                antecedent_text=antecedent,
            )
            if zero_anaphora_applied:
                transformations.append("pronoun_or_zero_anaphora")
            clauses.append(
                _candidate_clause(
                    item_id=item_id,
                    clause_index=len(clauses) + 1,
                    text=text,
                    proposition_rows=[row],
                    relation="direct_realization",
                    ordering_reason=f"profile_role_priority:{role}",
                    realization_rule_id=f"candidate_{role}_direct_v1",
                    transformation_ids=transformations,
                )
            )

    if not clauses:
        raise ValueError(f"No candidate clause emitted for adopted item '{item_id}'")

    paragraph_limit = int(
        policy.get("realization_constraints", {}).get(
            "paragraph_split_character_threshold",
            220,
        )
    )
    total_characters = sum(len(str(clause["text"])) for clause in clauses)
    acquisition_ids = {
        str(row["proposition_id"]) for row in by_role.get("acquisition", [])
    }
    split_before_acquisition = (
        total_characters > paragraph_limit and bool(acquisition_ids)
    )
    paragraph_index = 1
    for clause in clauses:
        if (
            split_before_acquisition
            and paragraph_index == 1
            and acquisition_ids.intersection(clause["proposition_ids"])
        ):
            paragraph_index = 2
        clause["paragraph_id"] = f"{item_id}#paragraph-{paragraph_index:02d}"
    paragraphs = [
        " ".join(
            str(clause["text"])
            for clause in clauses
            if clause["paragraph_id"].endswith(f"{index:02d}")
        )
        for index in range(1, paragraph_index + 1)
    ]
    text_ko = "\n\n".join(paragraphs)

    clause_by_proposition: dict[str, str] = {}
    for clause in clauses:
        for proposition_id in clause["proposition_ids"]:
            clause_by_proposition[str(proposition_id)] = str(clause["clause_id"])

    proofs: list[dict[str, Any]] = []
    structural: list[dict[str, Any]] = []
    use_proposition = use_rows[0] if use_rows else None
    use_clause_id = (
        clause_by_proposition.get(str(use_proposition["proposition_id"]))
        if use_proposition is not None
        else None
    )
    for requirement in requirement_rows:
        proposition_ids = [
            str(value) for value in requirement["applicable_proposition_ids"]
        ]
        clause_ids = sorted(
            {
                clause_by_proposition[value]
                for value in proposition_ids
                if value in clause_by_proposition
            }
        )
        status = "not_required"
        proof_id = None
        missing_reason = None
        if clause_ids:
            status = "emitted_direct"
        elif (
            requirement["role"] == "context"
            and requirement["required"]
            and use_proposition is not None
            and use_clause_id is not None
            and derive_context_from_primary_use(
                use_proposition.get("source_value")
            )
            is not None
        ):
            proof = build_single_proposition_equivalence_proof(
                item_id=item_id,
                requirement_id=str(requirement["requirement_id"]),
                proposition=use_proposition,
                surviving_clause_id=use_clause_id,
            )
            proofs.append(proof)
            proof_id = proof["equivalence_proof_id"]
            clause_ids = [use_clause_id]
            status = "satisfied_by_verified_fusion"
        elif requirement["required"]:
            status = "missing"
            missing_reason = "required_role_has_no_source_proposition"
        structural.append(
            {
                **requirement,
                "status": status,
                "clause_ids": clause_ids,
                "equivalence_proof_id": proof_id,
                "missing_reason": missing_reason,
            }
        )

    resolutions = [
        {
            "item_id": item_id,
            "proposition_id": row["proposition_id"],
            "proposition_resolution": (
                "emitted"
                if str(row["proposition_id"]) in clause_by_proposition
                else "blocked_by_source"
            ),
            "not_applicable_reason": None,
            "clause_ids": (
                [clause_by_proposition[str(row["proposition_id"])]]
                if str(row["proposition_id"]) in clause_by_proposition
                else []
            ),
            "equivalence_proof_id": None,
        }
        for row in proposition_rows
    ]
    missing_required = [
        row["section_name"]
        for row in structural
        if row["required"] and row["status"] == "missing"
    ]
    emitted_sections = [
        row["section_name"]
        for row in structural
        if row["status"]
        in {"emitted_direct", "satisfied_by_verified_fusion"}
    ]
    return (
        {
            "text_ko": text_ko,
            "source": "korean_prose_candidate_v1",
            "resolved_profile": resolved_profile,
            "resolution_source": resolution_source,
            "coverage_quality_candidate": (
                "strong" if not missing_required else "weak"
            ),
            "body_plan": {
                "resolved_profile": resolved_profile,
                "emitted_section_names": emitted_sections,
                "missing_required_sections": missing_required,
            },
            "profile_resolution_trace": resolution_trace,
        },
        clauses,
        structural,
        resolutions,
        proofs,
    )
