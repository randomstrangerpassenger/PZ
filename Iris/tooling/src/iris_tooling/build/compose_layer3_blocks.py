"""Compatibility adapter for public-text composition.

Retained for existing build imports and dynamic callers.
"""
from __future__ import annotations

from iris_tooling.domains.public_text.composition.blocks import (
    Any,
    apply_compose_repairs,
    build_partial_key,
    compose_facts_with_overlay_hints,
    derive_quality_flag,
    derive_requeue_reason,
    find_block_index,
    has_text,
    is_generic_identity_echo,
    move_block,
    overlay_semantic_quality,
    remove_block,
    render_block,
    render_blocks,
    select_distinctive_mechanic_hint,
)
