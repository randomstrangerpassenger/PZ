"""Compatibility adapter for public-text composition.

Retained for existing build imports and dynamic callers.
"""
from __future__ import annotations

from iris_tooling.domains.public_text.composition.render import (
    Any,
    DEFAULT_RESOLVER_AUTHORITY_MODE,
    DIAGNOSTIC_RESOLVER_AUTHORITY_MODE,
    Path,
    StyleNormalizer,
    compose_all_candidate,
    compose_all_legacy,
    compose_all_v2,
    compose_item_candidate,
    compose_item_legacy,
    compose_item_v2,
    derive_requeue_reason,
)
