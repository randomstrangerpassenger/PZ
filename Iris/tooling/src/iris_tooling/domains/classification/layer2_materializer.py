from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .layer2_census import census
from .layer2_contract import (
    CLASSIFICATIONS,
    EN_TRANSLATION,
    KO_TRANSLATION,
    RESOLUTION_REGISTRY,
    SURFACE_CATALOG,
    SUPPORT_PREDICATE,
    canonical_bytes,
    load_json_object,
    parse_primary_overrides,
    parse_classifications,
    parse_taxonomy,
    parse_translation,
    sha256_file,
    support_sha256,
    CATEGORY_INDEX,
    Layer2ContractError,
)


def _surface_bindings(repository_root: Path) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    catalog = load_json_object(repository_root / SURFACE_CATALOG)
    if catalog.get("schema_version") != "iris-classification-layer2-surface-catalog-v1":
        raise Layer2ContractError("Layer 2 surface catalog schema mismatch")
    categories, subcategories = parse_taxonomy(repository_root / CATEGORY_INDEX)
    ko = parse_translation(repository_root / KO_TRANSLATION)
    en = parse_translation(repository_root / EN_TRANSLATION)
    overrides = catalog.get("owner_approved_surface_overrides")
    if not isinstance(overrides, dict):
        raise Layer2ContractError("owner-approved surface overrides are missing")

    category_bindings: dict[str, dict[str, str]] = {}
    for category_id, key in categories.items():
        if not ko.get(key) or not en.get(key):
            raise Layer2ContractError(f"category surface missing: {category_id}")
        category_bindings[category_id] = {
            "key": key,
            "ko": ko[key],
            "en": en[key],
            "authority_ref": f"{CATEGORY_INDEX.as_posix()}#category/{category_id}",
            "provenance_ref": f"{KO_TRANSLATION.as_posix()}#{key};{EN_TRANSLATION.as_posix()}#{key}",
        }

    subcategory_bindings: dict[str, dict[str, str]] = {}
    category_by_number = {
        "1": "Tool", "2": "Combat", "3": "Consumable", "4": "Resource",
        "5": "Literature", "6": "Wearable", "7": "Furniture", "8": "Vehicle", "9": "Misc",
    }
    for subcategory_code, key in subcategories.items():
        identity = f"{category_by_number[subcategory_code[0]]}.{subcategory_code}"
        override = overrides.get(identity)
        if override is not None:
            if not isinstance(override, dict) or set(override) != {"ko", "en", "authority_ref", "provenance_ref"}:
                raise Layer2ContractError(f"surface override malformed: {identity}")
            ko_text, en_text = override.get("ko"), override.get("en")
        else:
            ko_text, en_text = ko.get(key), en.get(key)
        if not isinstance(ko_text, str) or not ko_text or not isinstance(en_text, str) or not en_text:
            raise Layer2ContractError(f"subcategory surface missing: {identity}")
        subcategory_bindings[identity] = {
            "key": key,
            "ko": ko_text,
            "en": en_text,
            "authority_ref": override["authority_ref"] if isinstance(override, dict) else f"{CATEGORY_INDEX.as_posix()}#subcategory/{subcategory_code}",
            "provenance_ref": override["provenance_ref"] if isinstance(override, dict) else f"{KO_TRANSLATION.as_posix()}#{key};{EN_TRANSLATION.as_posix()}#{key}",
        }
    return category_bindings, subcategory_bindings


def materialize(repository_root: Path) -> dict[str, Any]:
    registry = load_json_object(repository_root / RESOLUTION_REGISTRY)
    if registry.get("schema_version") != "iris-classification-layer2-resolution-registry-v1":
        raise Layer2ContractError("Layer 2 resolution registry schema mismatch")
    binding = registry.get("source_subject_binding")
    if not isinstance(binding, dict) or not all(isinstance(binding.get(key), str) for key in ("commit", "tree")):
        raise Layer2ContractError("resolution registry source binding is missing")
    if registry.get("support_predicate") != SUPPORT_PREDICATE:
        raise Layer2ContractError("resolution registry support predicate mismatch")
    input_sha256 = registry.get("input_sha256")
    if not isinstance(input_sha256, dict) or not input_sha256:
        raise Layer2ContractError("resolution registry input hash binding is missing")
    for relative, expected in input_sha256.items():
        if not isinstance(relative, str) or not isinstance(expected, str):
            raise Layer2ContractError("resolution registry input hash row is malformed")
        path = repository_root / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise Layer2ContractError(f"stale Layer 2 semantic input: {relative}")

    report = census(repository_root)
    memberships = parse_classifications(repository_root / CLASSIFICATIONS)
    primary_overrides = parse_primary_overrides(repository_root / CLASSIFICATIONS)
    category_surfaces, subcategory_surfaces = _surface_bindings(repository_root)
    explicit = registry.get("owner_resolved_rows")
    absences = registry.get("owner_approved_absence_rows")
    if not isinstance(explicit, dict) or not isinstance(absences, dict):
        raise Layer2ContractError("resolution registry row maps are missing")

    resolved: list[dict[str, Any]] = []
    display_silence: list[dict[str, str]] = []
    support_rows = report["rows"]
    for source_row in support_rows:
        full_type = source_row["full_type"]
        tags = tuple(memberships.get(full_type, ()))
        explicit_row = explicit.get(full_type)
        absence_row = absences.get(full_type)
        if explicit_row is not None and absence_row is not None:
            raise Layer2ContractError(f"conflicting owner dispositions: {full_type}")
        if absence_row is not None:
            if not isinstance(absence_row, dict):
                raise Layer2ContractError(f"absence row malformed: {full_type}")
            display_silence.append({
                "full_type": full_type,
                "source_state": "owner_approved_absence",
                "display_silence_reason": "owner_approved_absence",
            })
            continue

        primary: str | None = None
        resolution_rule: str | None = None
        if explicit_row is not None:
            if not isinstance(explicit_row, dict):
                raise Layer2ContractError(f"owner resolution row malformed: {full_type}")
            primary = explicit_row.get("primary_subcategory_id")
            resolution_rule = "exact_owner_decision"
        elif source_row["pre_resolution_state"] == "owner_resolved":
            if len(tags) == 1:
                primary = tags[0]
                resolution_rule = "single_non_fallback_membership"
            else:
                primary = primary_overrides.get(full_type)
                resolution_rule = "current_explicit_primary"

        if primary is None:
            display_silence.append({
                "full_type": full_type,
                "source_state": source_row["pre_resolution_state"],
                "display_silence_reason": source_row["display_silence_reason"],
            })
            continue
        if primary not in tags or primary == "Misc.9-A":
            raise Layer2ContractError(f"inadmissible primary for {full_type}: {primary}")
        category_id = primary.split(".", 1)[0]
        category_surface = category_surfaces.get(category_id)
        primary_surface = subcategory_surfaces.get(primary)
        if category_surface is None or primary_surface is None:
            raise Layer2ContractError(f"surface binding missing for {full_type}: {primary}")
        authority_ref = f"{CLASSIFICATIONS.as_posix()}#classification/{full_type}"
        provenance_ref = f"{CLASSIFICATIONS.as_posix()}#classification/{full_type};rule={resolution_rule}"
        resolved.append({
            "full_type": full_type,
            "terminal_state": "resolved",
            "classification_identity": f"{category_id}|{primary}",
            "memberships": list(tags),
            "category_id": category_id,
            "primary_subcategory_id": primary,
            "category_surface": category_surface,
            "primary_subcategory_surface": primary_surface,
            "classification_authority_ref": authority_ref,
            "classification_provenance_ref": provenance_ref,
            "source_subject_binding": binding,
        })

    resolved.sort(key=lambda row: row["full_type"].encode("utf-8"))
    display_silence.sort(key=lambda row: row["full_type"].encode("utf-8"))
    applicable_full_types = tuple(row["full_type"] for row in resolved)
    silence_full_types = tuple(row["full_type"] for row in display_silence)
    return {
        "schema_version": "iris-classification-layer2-owner-output-v2",
        "status": "complete",
        "source_subject_binding": binding,
        "support_predicate": SUPPORT_PREDICATE,
        "frozen_support_count": report["frozen_support_count"],
        "frozen_support_sha256": report["frozen_support_sha256"],
        "resolved_entry_count": len(resolved),
        "remaining_entry_count": 0,
        "classification_correction_count": 0,
        "rows": resolved,
        "remaining_entries": [],
        "layer2_applicability_rule": "admissible_current_owner_category_and_primary_v1",
        "layer2_display_silence_entries": display_silence,
        "d2_handoff_partition": {
            "schema_version": "iris-classification-layer2-d2-handoff-partition-v1",
            "support": {
                "count": report["frozen_support_count"],
                "exact_fulltype_sha256": report["frozen_support_sha256"],
            },
            "layer2_applicable": {
                "count": len(applicable_full_types),
                "exact_fulltype_sha256": support_sha256(applicable_full_types),
                "artifact_ref": "#rows",
            },
            "layer2_display_silence": {
                "count": len(silence_full_types),
                "exact_fulltype_sha256": support_sha256(silence_full_types),
                "artifact_ref": "#layer2_display_silence_entries",
            },
            "partition_complete": True,
            "menu_consumer_relation_owner": "T1-D2/Menu consumer owner",
        },
        "current_ecosystem_adoption": "pending_T1_D6",
        "T2_FULL_DATA_PROGRESSION": "BLOCKED_BY_UPSTREAM_CORRECTIONS",
        "production_t2_handoff": "absent",
    }


def write_output(repository_root: Path, output_path: Path) -> dict[str, Any]:
    value = materialize(repository_root)
    output_path.write_bytes(canonical_bytes(value))
    return value
