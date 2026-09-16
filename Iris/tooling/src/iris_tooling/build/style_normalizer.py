"""Compatibility adapter for public-text composition.

Retained for existing build imports and dynamic callers.
"""
from __future__ import annotations

from iris_tooling.domains.public_text.composition.style import (
    Any,
    NormalizationResult,
    Path,
    StyleNormalizer,
    _default_rules_dir,
    _load_json,
    _matches_selected_cluster_contains,
    _postprocess_ko,
    dataclass,
    extract_primary_use_fact_origin,
    json,
    re,
    require_repository_context,
)
