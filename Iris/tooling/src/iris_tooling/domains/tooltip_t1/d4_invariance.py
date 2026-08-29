from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

from .contract import canonical_bytes, sha256_bytes
from .models import TooltipContractError


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise TooltipContractError(f"cannot read D4 invariance input {path}: {exc}") from exc
    for index, line in enumerate(lines, 1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TooltipContractError(f"{path}:{index}: malformed JSONL") from exc
        if not isinstance(value, dict):
            raise TooltipContractError(f"{path}:{index}: expected object")
        rows.append(value)
    return rows


def normalized_selected_tuples(audit_root: Path) -> list[dict[str, Any]]:
    rows = _jsonl(audit_root / "tooltip_readiness_manifest.jsonl")
    selected: list[dict[str, Any]] = []
    for row in rows:
        full_type = row.get("full_type")
        layer4 = row.get("layer4_selected")
        if not isinstance(full_type, str) or not isinstance(layer4, list):
            raise TooltipContractError("D4 selected tuple source is malformed")
        for result_index, item in enumerate(layer4):
            if not isinstance(item, dict):
                raise TooltipContractError("D4 selected tuple row is malformed")
            selected.append(
                {
                    "full_type": full_type,
                    "slot_id": item.get("slot_id"),
                    "source_type": item.get("source"),
                    "selected_identity": item.get("interaction_id"),
                    "selection_result_index": result_index,
                }
            )
    selected.sort(
        key=lambda row: (
            row["full_type"],
            row["slot_id"],
            row["source_type"],
            row["selected_identity"],
            row["selection_result_index"],
        )
    )
    return selected


def source_distribution(audit_root: Path) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in _jsonl(audit_root / "tooltip_readiness_manifest.jsonl"):
        relation = row.get("layer4_source_equivalence")
        if not isinstance(relation, dict):
            raise TooltipContractError("D4 source distribution row is malformed")
        shape = relation.get("selected_shape")
        if shape not in {"both", "recipe_only", "rightclick_only", "none"}:
            raise TooltipContractError("D4 selected source shape is invalid")
        counts[shape] += 1
    return dict(sorted(counts.items()))


def compare_audit_roots(pre_root: Path, post_root: Path) -> dict[str, Any]:
    pre = normalized_selected_tuples(pre_root)
    post = normalized_selected_tuples(post_root)
    pre_bytes = canonical_bytes(pre)
    post_bytes = canonical_bytes(post)
    pre_recipe = [row for row in pre if row["source_type"] == "recipe"]
    post_recipe = [row for row in post if row["source_type"] == "recipe"]
    pre_rightclick = [row for row in pre if row["source_type"] == "rightclick"]
    post_rightclick = [row for row in post if row["source_type"] == "rightclick"]
    pre_distribution = source_distribution(pre_root)
    post_distribution = source_distribution(post_root)
    verdict = {
        "schema_version": "iris-tooltip-t1-d4-selected-tuple-comparison-v1",
        "pre_selected_tuple_count": len(pre),
        "post_selected_tuple_count": len(post),
        "pre_selected_tuple_sha256": sha256_bytes(pre_bytes),
        "post_selected_tuple_sha256": sha256_bytes(post_bytes),
        "selected_tuple_delta": int(pre_bytes != post_bytes),
        "selected_recipe_identity_delta": int(
            canonical_bytes(pre_recipe) != canonical_bytes(post_recipe)
        ),
        "selected_rightclick_identity_delta": int(
            canonical_bytes(pre_rightclick) != canonical_bytes(post_rightclick)
        ),
        "slot_source_order_identity_delta": int(pre_bytes != post_bytes),
        "pre_source_distribution": pre_distribution,
        "post_source_distribution": post_distribution,
        "source_distribution_delta": int(pre_distribution != post_distribution),
    }
    if any(
        verdict[key]
        for key in (
            "selected_tuple_delta",
            "selected_recipe_identity_delta",
            "selected_rightclick_identity_delta",
            "slot_source_order_identity_delta",
            "source_distribution_delta",
        )
    ):
        raise TooltipContractError(f"D4 selected tuple invariance failure: {verdict}")
    return verdict
