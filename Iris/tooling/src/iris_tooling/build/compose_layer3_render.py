from __future__ import annotations

from pathlib import Path
from typing import Any

from .style_normalizer import StyleNormalizer

from .compose_layer3_blocks import derive_requeue_reason
from .compose_layer3_body_profile import (
    DEFAULT_RESOLVER_AUTHORITY_MODE,
    DIAGNOSTIC_RESOLVER_AUTHORITY_MODE,
)
from .compose_layer3_item import (
    compose_item_candidate,
    compose_item_legacy,
    compose_item_v2,
)


def compose_all_legacy(
    facts_list: list[dict[str, Any]],
    decisions_list: list[dict[str, Any]],
    overlay_map: dict[str, dict[str, Any]],
    profiles: dict[str, Any],
    *,
    allow_legacy_runtime_state: bool = False,
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
            allow_legacy_runtime_state=allow_legacy_runtime_state,
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
    resolver_authority_mode: str = DEFAULT_RESOLVER_AUTHORITY_MODE,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    facts_map = {entry["item_id"]: entry for entry in facts_list}
    decisions_map = {entry["item_id"]: entry for entry in decisions_list}
    results: dict[str, dict[str, Any]] = {}
    normalization_logs: list[dict[str, Any]] = []
    normalizer = StyleNormalizer()
    allow_legacy_runtime_state = resolver_authority_mode == DIAGNOSTIC_RESOLVER_AUTHORITY_MODE

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
            resolver_authority_mode=resolver_authority_mode,
            allow_legacy_runtime_state=allow_legacy_runtime_state,
        )
        results[item_id] = entry
        if log_entry is not None:
            normalization_logs.append(log_entry)

    return results, normalization_logs, []


def compose_all_candidate(
    facts_list: list[dict[str, Any]],
    decisions_list: list[dict[str, Any]],
    profiles: dict[str, Any],
    *,
    identity_hint_target_map: dict[str, str],
    precedence_rules: dict[str, Any],
    propositions_by_item: dict[str, list[dict[str, Any]]],
    requirements_by_item: dict[str, list[dict[str, Any]]],
    policy: dict[str, Any],
) -> tuple[
    dict[str, dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    facts_map = {str(entry["item_id"]): entry for entry in facts_list}
    decisions_map = {str(entry["item_id"]): entry for entry in decisions_list}
    results: dict[str, dict[str, Any]] = {}
    traces: list[dict[str, Any]] = []
    structural_rows: list[dict[str, Any]] = []
    resolution_rows: list[dict[str, Any]] = []
    proof_rows: list[dict[str, Any]] = []
    for item_id in sorted(decisions_map):
        decision = decisions_map[item_id]
        facts = dict(facts_map.get(item_id, {}))
        facts["item_id"] = item_id
        entry, item_traces, item_structural, item_resolutions, item_proofs = (
            compose_item_candidate(
                facts,
                decision,
                profiles,
                identity_hint_target_map=identity_hint_target_map,
                precedence_rules=precedence_rules,
                proposition_rows=propositions_by_item.get(item_id, []),
                requirement_rows=requirements_by_item.get(item_id, []),
                policy=policy,
            )
        )
        results[item_id] = entry
        traces.extend(item_traces)
        structural_rows.extend(item_structural)
        resolution_rows.extend(item_resolutions)
        proof_rows.extend(item_proofs)
    return results, traces, structural_rows, resolution_rows, proof_rows
