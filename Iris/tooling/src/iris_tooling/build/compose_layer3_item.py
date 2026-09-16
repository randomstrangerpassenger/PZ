"""Compatibility adapter for public-text composition.

Retained for existing build imports and dynamic callers.
"""
from __future__ import annotations

from iris_tooling.domains.public_text.composition.item import (
    Any,
    DEFAULT_RESOLVER_AUTHORITY_MODE,
    Path,
    StyleNormalizer,
    UNADOPTED_RUNTIME_STATE,
    _candidate_clause,
    apply_compose_repairs,
    apply_identity_zero_anaphora,
    build_body_plan_sections,
    build_candidate_lead_context,
    build_single_proposition_equivalence_proof,
    compose_facts_with_overlay_hints,
    compose_item_candidate,
    compose_item_legacy,
    compose_item_v2,
    derive_context_from_primary_use,
    derive_quality_flag,
    ensure_sentence,
    extract_primary_use_fact_origin,
    naturalize_source_fragment,
    normalize_runtime_state,
    render_acquisition_listing,
    render_blocks,
    resolve_body_profile,
    select_candidate_lead_realization,
)
