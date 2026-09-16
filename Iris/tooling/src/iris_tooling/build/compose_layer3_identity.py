"""Compatibility adapter for public-text composition.

Retained for existing build imports and dynamic callers.
"""
from __future__ import annotations

from iris_tooling.domains.public_text.composition.identity import (
    Any,
    _food_semantic_lead,
    _has_semantic_tokens,
    append_copula,
    append_instrumental,
    append_object_particle,
    apply_identity_zero_anaphora,
    build_candidate_lead_context,
    context_core,
    derive_context_from_primary_use,
    ensure_sentence,
    has_final_consonant,
    has_final_rieul,
    has_text,
    instrumental_phonological_tail,
    naturalize_internal_work_abstraction,
    naturalize_source_fragment,
    normalize_acquisition_enumeration,
    normalize_for_contains,
    primary_use_covers_context,
    re,
    realize_concrete_work_context,
    realize_work_use_context,
    render_acquisition_listing,
    render_candidate_lead,
    render_identity_core_text,
    select_candidate_lead_realization,
    strip_sentence_ending,
    unicodedata,
)
