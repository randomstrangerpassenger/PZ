from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .layer2_census import census
from .layer2_contract import (
    ABSENCE_REGISTRY,
    CATEGORY_INDEX,
    CLASSIFICATIONS,
    EN_TRANSLATION,
    KO_TRANSLATION,
    OWNER_OUTPUT,
    OUTPUT_SCHEMA,
    RESOLUTION_CONTRACT,
    RESOLUTION_REGISTRY,
    SURFACE_CATALOG,
    SUPPORT_PREDICATE,
    Layer2ContractError,
    load_json_object,
    parse_taxonomy,
    parse_translation,
    parse_classifications,
    sha256_file,
)


FORBIDDEN_FIELDS = {
    "tooltip_rank", "menu_rank", "importance", "frequency", "external_mod_status",
    "audit_verdict", "menu_consumer_identity_ref", "menu_parity_status",
}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def validate_owner_output(repository_root: Path, output_path: Path | None = None) -> dict[str, Any]:
    output_path = output_path or repository_root / OWNER_OUTPUT
    output = load_json_object(output_path)
    loaded: dict[Path, dict[str, Any]] = {}
    for relative, schema in (
        (RESOLUTION_CONTRACT, "iris-classification-layer2-resolution-contract-v1"),
        (ABSENCE_REGISTRY, "iris-classification-layer2-absence-reason-registry-v1"),
        (OUTPUT_SCHEMA, "https://json-schema.org/draft/2020-12/schema"),
        (RESOLUTION_REGISTRY, "iris-classification-layer2-resolution-registry-v1"),
        (SURFACE_CATALOG, "iris-classification-layer2-surface-catalog-v1"),
    ):
        value = load_json_object(repository_root / relative)
        loaded[relative] = value
        actual = value.get("schema_version") or value.get("$schema")
        if actual != schema:
            raise Layer2ContractError(f"schema mismatch: {relative}")

    if output.get("schema_version") != "iris-classification-layer2-owner-output-v1":
        raise Layer2ContractError("Layer 2 owner output schema mismatch")
    if output.get("support_predicate") != SUPPORT_PREDICATE:
        raise Layer2ContractError("Layer 2 owner output support predicate mismatch")
    registry = loaded[RESOLUTION_REGISTRY]
    if output.get("source_subject_binding") != registry.get("source_subject_binding"):
        raise Layer2ContractError("Layer 2 owner output source subject binding mismatch")
    input_hashes = registry.get("input_sha256")
    if not isinstance(input_hashes, dict) or not input_hashes:
        raise Layer2ContractError("Layer 2 resolution registry input binding is missing")
    for relative, expected in input_hashes.items():
        path = repository_root / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise Layer2ContractError(f"stale Layer 2 semantic input: {relative}")
    report = census(repository_root)
    if output.get("frozen_support_count") != report["frozen_support_count"]:
        raise Layer2ContractError("Layer 2 owner output support count mismatch")
    if output.get("frozen_support_sha256") != report["frozen_support_sha256"]:
        raise Layer2ContractError("Layer 2 owner output support hash mismatch")

    rows = output.get("rows")
    remaining = output.get("remaining_entries")
    if not isinstance(rows, list) or not isinstance(remaining, list):
        raise Layer2ContractError("Layer 2 owner output row partitions are missing")
    memberships = parse_classifications(repository_root / CLASSIFICATIONS)
    categories, subcategories = parse_taxonomy(repository_root / CATEGORY_INDEX)
    ko = parse_translation(repository_root / KO_TRANSLATION)
    en = parse_translation(repository_root / EN_TRANSLATION)
    surface_overrides = loaded[SURFACE_CATALOG].get("owner_approved_surface_overrides")
    if not isinstance(surface_overrides, dict):
        raise Layer2ContractError("Layer 2 surface override map is missing")
    absence_reasons = {
        row.get("code")
        for row in loaded[ABSENCE_REGISTRY].get("reasons", [])
        if isinstance(row, dict)
    }
    seen: set[str] = set()
    state_counts: Counter[str] = Counter()
    for row in rows:
        if not isinstance(row, dict) or FORBIDDEN_FIELDS & set(row):
            raise Layer2ContractError("Layer 2 owner output contains a malformed or consumer-owned field")
        full_type = row.get("full_type")
        if not _nonempty_string(full_type) or full_type in seen:
            raise Layer2ContractError("Layer 2 owner output exact FullType identity is missing or duplicated")
        seen.add(full_type)
        state = row.get("terminal_state")
        state_counts[state] += 1
        if state == "resolved":
            tags = row.get("memberships")
            primary = row.get("primary_subcategory_id")
            if tags != list(memberships.get(full_type, ())) or not tags:
                raise Layer2ContractError(f"membership mismatch: {full_type}")
            if primary not in tags or primary == "Misc.9-A":
                raise Layer2ContractError(f"primary membership mismatch: {full_type}")
            if row.get("category_id") != primary.split(".", 1)[0]:
                raise Layer2ContractError(f"category identity mismatch: {full_type}")
            category_id = row["category_id"]
            subcategory_code = primary.split(".", 1)[1]
            for surface_name in ("category_surface", "primary_subcategory_surface"):
                surface = row.get(surface_name)
                if not isinstance(surface, dict) or set(surface) != {"key", "ko", "en", "authority_ref", "provenance_ref"}:
                    raise Layer2ContractError(f"surface binding malformed: {full_type}")
                if not all(_nonempty_string(surface[key]) for key in ("key", "ko", "en", "authority_ref", "provenance_ref")):
                    raise Layer2ContractError(f"surface value missing: {full_type}")
                if any("\n" in surface[key] or "\r" in surface[key] for key in ("ko", "en")):
                    raise Layer2ContractError(f"multiline surface value: {full_type}")
            category_surface = row["category_surface"]
            if (
                category_surface["key"] != categories.get(category_id)
                or category_surface["ko"] != ko.get(category_surface["key"])
                or category_surface["en"] != en.get(category_surface["key"])
            ):
                raise Layer2ContractError(f"category surface authority mismatch: {full_type}")
            primary_surface = row["primary_subcategory_surface"]
            override = surface_overrides.get(primary)
            expected_ko = override.get("ko") if isinstance(override, dict) else ko.get(primary_surface["key"])
            expected_en = override.get("en") if isinstance(override, dict) else en.get(primary_surface["key"])
            if (
                primary_surface["key"] != subcategories.get(subcategory_code)
                or primary_surface["ko"] != expected_ko
                or primary_surface["en"] != expected_en
            ):
                raise Layer2ContractError(f"subcategory surface authority mismatch: {full_type}")
            if not _nonempty_string(row.get("classification_authority_ref")) or not _nonempty_string(row.get("classification_provenance_ref")):
                raise Layer2ContractError(f"authority/provenance missing: {full_type}")
        elif state == "owner_approved_absence":
            if any(key in row for key in ("memberships", "category_id", "primary_subcategory_id", "category_surface", "primary_subcategory_surface")):
                raise Layer2ContractError(f"absence carries classification values: {full_type}")
            if not all(_nonempty_string(row.get(key)) for key in ("absence_reason", "classification_authority_ref", "classification_provenance_ref")):
                raise Layer2ContractError(f"positive absence proof missing: {full_type}")
            if row.get("absence_reason") not in absence_reasons:
                raise Layer2ContractError(f"absence reason is not owner-approved: {full_type}")
        else:
            raise Layer2ContractError(f"non-terminal owner output row: {full_type}")

    remaining_seen: set[str] = set()
    allowed_reasons = {"CLASSIFICATION_RESOLVED_IDENTITY_MISSING", "CLASSIFICATION_FALLBACK_NOT_ADMISSIBLE"}
    for row in remaining:
        if not isinstance(row, dict) or set(row) != {"full_type", "reason_code", "pre_resolution_state"}:
            raise Layer2ContractError("remaining Layer 2 entry is malformed")
        full_type = row.get("full_type")
        if not _nonempty_string(full_type) or full_type in seen or full_type in remaining_seen:
            raise Layer2ContractError("remaining Layer 2 exact FullType is duplicated")
        if row.get("reason_code") not in allowed_reasons:
            raise Layer2ContractError(f"remaining Layer 2 reason is invalid: {full_type}")
        remaining_seen.add(full_type)

    support = {row["full_type"] for row in report["rows"]}
    if seen | remaining_seen != support:
        raise Layer2ContractError("Layer 2 owner output does not partition the frozen support universe")
    if output.get("resolved_entry_count") != len(rows) or output.get("remaining_entry_count") != len(remaining):
        raise Layer2ContractError("Layer 2 owner output count fields mismatch")
    expected_status = "complete" if not remaining else "partial"
    if output.get("status") != expected_status:
        raise Layer2ContractError("Layer 2 owner output status mismatch")
    if output.get("current_ecosystem_adoption") != "pending_T1_D6":
        raise Layer2ContractError("Layer 2 owner output improperly claims current adoption")
    if output.get("T2_FULL_DATA_PROGRESSION") != "BLOCKED_BY_UPSTREAM_CORRECTIONS" or output.get("production_t2_handoff") != "absent":
        raise Layer2ContractError("Layer 2 owner output improperly advances T2")
    return {
        "status": expected_status,
        "frozen_support_count": len(support),
        "frozen_support_sha256": report["frozen_support_sha256"],
        "resolved_entry_count": len(rows),
        "remaining_entry_count": len(remaining),
        "terminal_state_distribution": dict(sorted(state_counts.items())),
        "duplicate_exact_fulltype_count": 0,
        "support_universe_enumeration_mismatch_count": 0,
        "primary_not_in_membership_count": 0,
        "consumer_specific_semantic_field_count": 0,
    }
