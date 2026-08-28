from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import random
from typing import Any, Iterable

from .models import TooltipContractError


@dataclass(frozen=True, slots=True)
class Layer4Candidate:
    interaction_id: str
    source: str
    public_state: str = "public"
    line_kind: str = "evidence"
    requirement_only: bool = False
    stable_order_key: str | None = None
    localized_surfaces: dict[str, str | None] | None = None
    menu_consumer_identity_ref: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateResult:
    candidate: Layer4Candidate
    disposition: str


def _identity_order_key(candidate: Layer4Candidate) -> str:
    if candidate.stable_order_key:
        return candidate.stable_order_key
    # P-6: versioned identity-derived presentation tie-break.  It carries no
    # importance/frequency/quality meaning and never reads locale readiness.
    payload = f"iris-tooltip-l4-order-v1\0{candidate.source}\0{candidate.interaction_id}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _eligibility(candidate: Layer4Candidate) -> str | None:
    if not candidate.interaction_id:
        return "correction_missing_identity"
    if candidate.source not in {"recipe", "rightclick"}:
        return "ineligible_not_public"
    if candidate.public_state == "review":
        return "ineligible_review"
    if candidate.public_state != "public":
        return "ineligible_not_public"
    if candidate.line_kind == "exclusion" or candidate.interaction_id.startswith("uc.exclusion."):
        return "ineligible_exclusion"
    if candidate.line_kind != "evidence":
        return "ineligible_not_public"
    if candidate.requirement_only:
        return "ineligible_requirement_only"
    return None


def select_layer4(candidates: Iterable[Layer4Candidate]) -> tuple[tuple[Layer4Candidate, ...], tuple[CandidateResult, ...]]:
    results: list[CandidateResult] = []
    eligible: list[Layer4Candidate] = []
    seen: set[str] = set()
    for candidate in sorted(candidates, key=lambda row: (_identity_order_key(row), row.source, row.interaction_id)):
        disposition = _eligibility(candidate)
        if disposition is not None:
            results.append(CandidateResult(candidate, disposition))
            continue
        if candidate.interaction_id in seen:
            results.append(CandidateResult(candidate, "excluded_exact_duplicate_identity"))
            continue
        seen.add(candidate.interaction_id)
        eligible.append(candidate)

    by_source = {
        source: [candidate for candidate in eligible if candidate.source == source]
        for source in ("recipe", "rightclick")
    }
    if by_source["recipe"] and by_source["rightclick"]:
        selected = (by_source["recipe"][0], by_source["rightclick"][0])
    else:
        single = by_source["recipe"] or by_source["rightclick"]
        selected = tuple(single[:2])
    selected_ids = {candidate.interaction_id for candidate in selected}
    for candidate in eligible:
        disposition = "selected" if candidate.interaction_id in selected_ids else "excluded_capacity"
        results.append(CandidateResult(candidate, disposition))
    selected = tuple(sorted(selected, key=lambda row: (_identity_order_key(row), row.source, row.interaction_id)))
    return selected, tuple(results)


def selection_identity(selected: Iterable[Layer4Candidate]) -> str:
    payload = [
        {"interaction_id": row.interaction_id, "source": row.source, "order_key": _identity_order_key(row)}
        for row in selected
    ]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_invariants(candidates: list[Layer4Candidate]) -> dict[str, Any]:
    base, _ = select_layer4(candidates)
    permuted = list(candidates)
    random.Random(0).shuffle(permuted)
    permutation_selected, _ = select_layer4(permuted)
    masked = [replace(row, localized_surfaces=None, menu_consumer_identity_ref=None) for row in candidates]
    masked_selected, _ = select_layer4(masked)
    restored = [replace(row) for row in candidates]
    restored_selected, _ = select_layer4(restored)
    identities = {
        "base": selection_identity(base),
        "permuted": selection_identity(permutation_selected),
        "masked": selection_identity(masked_selected),
        "restored": selection_identity(restored_selected),
    }
    if len(set(identities.values())) != 1:
        raise TooltipContractError("IDENTITY_READINESS_FEEDBACK_VIOLATION")
    return {
        "schema_version": "iris-tooltip-layer4-invariance-v1",
        "permutation": {
            "base_selected_identity_sha256": identities["base"],
            "permuted_selected_identity_sha256": identities["permuted"],
            "changed": False,
        },
        "readiness_masking": {
            "base_selected_identity_sha256": identities["base"],
            "masked_selected_identity_sha256": identities["masked"],
            "restored_selected_identity_sha256": identities["restored"],
            "locale_readiness_changed_selection": False,
            "menu_evidence_changed_selection": False,
        },
    }
