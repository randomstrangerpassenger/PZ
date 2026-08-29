from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .layer2_contract import (
    CLASSIFICATIONS,
    SUPPORT_PREDICATE,
    parse_classifications,
    parse_primary_overrides,
    support_sha256,
    support_universe,
)


def _normalized_collisions(values: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    buckets: dict[str, list[str]] = {}
    for value in values:
        buckets.setdefault(value.lower(), []).append(value)
    return {
        key: tuple(sorted(rows, key=lambda value: value.encode("utf-8")))
        for key, rows in buckets.items()
        if len(set(rows)) > 1
    }


def census(repository_root: Path) -> dict[str, Any]:
    support = support_universe(repository_root)
    memberships = parse_classifications(repository_root / CLASSIFICATIONS)
    primary = parse_primary_overrides(repository_root / CLASSIFICATIONS)
    states: Counter[str] = Counter()
    rows: list[dict[str, Any]] = []
    for full_type in support:
        tags = memberships.get(full_type, ())
        explicit_primary = primary.get(full_type)
        if not tags:
            state = "no_membership_record"
            reason = "CLASSIFICATION_RESOLVED_IDENTITY_MISSING"
        elif "Misc.9-A" in tags:
            state = "fallback_derived"
            reason = "CLASSIFICATION_FALLBACK_NOT_ADMISSIBLE"
        elif len(tags) == 1 or explicit_primary in tags:
            state = "owner_resolved"
            reason = None
        else:
            state = "unclassified"
            reason = "CLASSIFICATION_RESOLVED_IDENTITY_MISSING"
        states[state] += 1
        rows.append({
            "full_type": full_type,
            "memberships": list(tags),
            "explicit_primary_subcategory_id": explicit_primary,
            "pre_resolution_state": state,
            "remaining_reason_code": reason,
        })

    membership_sets = {full_type: tags for full_type, tags in memberships.items()}
    multi = {full_type for full_type, tags in membership_sets.items() if len(tags) > 1}
    overrides = set(primary)
    collisions = _normalized_collisions(support)
    return {
        "schema_version": "iris-classification-layer2-census-v1",
        "support_predicate": SUPPORT_PREDICATE,
        "frozen_support_count": len(support),
        "frozen_support_sha256": support_sha256(support),
        "raw_membership_count": len(memberships),
        "state_distribution": dict(sorted(states.items())),
        "multi_membership_count": len(multi),
        "explicit_primary_count": len(overrides),
        "multi_explicit_primary_intersection_count": len(multi & overrides),
        "multi_without_explicit_primary_count": len(multi - overrides),
        "single_explicit_primary_intersection": sorted(
            overrides - multi, key=lambda value: value.encode("utf-8")
        ),
        "normalized_collisions": {key: list(value) for key, value in sorted(collisions.items())},
        "rows": rows,
    }
