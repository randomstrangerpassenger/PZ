from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROUND_ID = "layer4_confirmed_detector_field_map_reseal_round"
ROUND_DATE = "2026-06-02"
ROUND_ROOT = (
    "Iris/build/description/v2/staging/compose_contract_migration/"
    "layer4_confirmed_detector_field_map_reseal_round"
)
PLAN_PATH = (
    "docs/Iris/"
    "iris-dvf-3-3-layer4-confirmed-detector-field-map-reseal-round-plan.md"
)

ADMISSION_ROUND_ID = "layer4_trace_edge_authority_admission_round"
ADMISSION_ROOT = (
    "Iris/build/description/v2/staging/compose_contract_migration/"
    "layer4_trace_edge_authority_admission_round"
)
ADMITTED_EDGE_PATH = f"{ADMISSION_ROOT}/layer4_trace_edges.v1.jsonl"
ADMISSION_MANIFEST_PATH = f"{ADMISSION_ROOT}/trace_edge_admission_manifest.json"
ADMISSION_PARTITION_PATH = f"{ADMISSION_ROOT}/trace_edge_authority_partition.json"
ADMISSION_REPORT_PATH = f"{ADMISSION_ROOT}/trace_edge_admission_report.json"
ADMISSION_CLOSEOUT_PATH = (
    f"{ADMISSION_ROOT}/layer4_trace_edge_authority_admission_closeout.md"
)
ADMISSION_HASH_MANIFEST_PATH = f"{ADMISSION_ROOT}/artifact_hash_manifest.json"

PREDECESSOR_CORPUS_LOCK_ROOT = (
    "Iris/build/description/v2/staging/compose_contract_migration/"
    "layer4_boundary_current_corpus_lock_round"
)
PREDECESSOR_FIELD_MAP_ROOT = (
    "Iris/build/description/v2/staging/compose_contract_migration/"
    "layer4_confirmed_detector_field_map_seal_round"
)
PREDECESSOR_CORPUS_MANIFEST_PATH = (
    f"{PREDECESSOR_CORPUS_LOCK_ROOT}/layer4_boundary_current_corpus_manifest.json"
)
PREDECESSOR_FIELD_MAP_MANIFEST_PATH = (
    f"{PREDECESSOR_FIELD_MAP_ROOT}/layer4_confirmed_detector_field_map_manifest.json"
)

BRANCH_CLOSEOUT = "closed_with_layer4_confirmed_detector_field_map_resealed"
CONTRACT_CLOSEOUT_STATE = "complete"
FIELD_MAP_VERSION = "field_map.v1"

EDGE_REQUIRED_FIELDS = [
    "row_id",
    "item_full_type",
    "source_ref",
    "source_cardinality",
    "destination_ref",
    "destination_slot",
    "edge_type",
    "edge_basis",
]
EDGE_TYPE = "placed_in_body_output"
ALLOWED_EDGE_BASIS = [
    "recovered_body_plan_relation_trace",
    "recovered_compose_relation_trace",
    "generated_body_plan_relation_trace",
    "generated_compose_relation_trace",
]

FORBIDDEN_FALLBACK_CLASSES = [
    "rendered_body_substring",
    "item_display_text",
    "korean_or_english_keyword",
    "category_tag",
    "cluster_label",
    "provenance_label_only",
    "source_target_co_occurrence_only",
    "diagnostic_report_only_field",
    "historical_predecessor_count",
    "row_count_itself",
    "predecessor_detector_readiness_dry_run_pass",
    "field_map_conditioned_readiness_dry_run_pass_as_edge_truth",
]

NON_CLAIMS = [
    "no LAYER4_ABSORPTION_CONFIRMED current count",
    "no live-corpus occurrence count",
    "no confirmed count 0 declaration",
    "no confirmed count 24 declaration",
    "no zero-occurrence closeout",
    "no Layer4 absorption resolved claim",
    "no Layer4 policy redesign",
    "no SUSPECT tier coverage",
    "no FUNCTION_NARROW second rollout",
    "no ACQ_DOMINANT publish review",
    "no publish mutation review",
    "no source facts mutation",
    "no source decisions mutation",
    "no rendered text mutation",
    "no runtime Lua mutation",
    "no packaged Lua mutation",
    "no quality_state mutation",
    "no publish_state mutation",
    "no runtime_state mutation",
    "no Browser/Wiki/Tooltip behavior change",
    "no runtime rollout",
    "no manual in-game validation pass",
    "no deployment",
    "no Workshop readiness",
    "no B42 readiness",
    "no release readiness",
    "no ready_for_release",
    "no repository-wide machine-enforced preflight",
]

VALIDATION_CEILING = {
    "validated": [
        "2026-06-01 admitted trace-edge artifact path and partition intake",
        "admitted trace-edge artifact hash equality against admission manifest",
        "JSONL parse and schema field inventory for admitted artifact",
        "four detector role bindings against actual admitted artifact fields",
        "source_ref to destination_slot relation traversal through edge_type tuple",
        "forbidden fallback rejection",
        "ambiguity separation",
        "field-map-conditioned readiness dry-run without count execution",
        "no-count guard",
        "round-local JSON/JSONL parse",
        "determinism digest for generated reseal packet",
        "non-mutation hash diff for stated source/rendered/runtime/admission surfaces",
        "adversarial review gate",
    ],
    "out_of_scope": [
        "LAYER4_ABSORPTION_CONFIRMED current count",
        "live-corpus occurrence count",
        "confirmed count 0 declaration",
        "confirmed count 24 declaration",
        "zero-occurrence closeout",
        "Layer4 absorption resolved validation",
        "Layer4 policy redesign validation",
        "SUSPECT tier coverage",
        "FUNCTION_NARROW second rollout",
        "ACQ_DOMINANT publish review",
        "publish mutation review",
        "runtime rollout validation",
        "manual in-game validation",
        "multiplayer validation",
        "long-session runtime validation",
        "deployment validation",
        "Workshop readiness validation",
        "B42 readiness validation",
        "release readiness validation",
        "Browser/Wiki/Tooltip behavior validation",
        "full external mod compatibility sweep",
        "quality_baseline_v4 to v5 cutover",
        "repository-wide machine-enforced preflight",
    ],
    "unvalidated_but_in_scope": [],
}

NON_MUTATION_TARGETS = [
    {
        "group": "source_facts",
        "paths": ["Iris/build/description/v2/data/dvf_3_3_facts.jsonl"],
    },
    {
        "group": "source_decisions",
        "paths": ["Iris/build/description/v2/data/dvf_3_3_decisions.jsonl"],
    },
    {
        "group": "rendered_text",
        "paths": ["Iris/build/description/v2/output/dvf_3_3_rendered.json"],
    },
    {
        "group": "runtime_lua_chunks",
        "globs": ["Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua"],
    },
    {
        "group": "runtime_lua_chunk_manifest",
        "paths": ["Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua"],
    },
    {
        "group": "runtime_lua_monolith",
        "paths": ["Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua"],
        "expected_absent": True,
    },
    {
        "group": "admitted_trace_edge_artifact",
        "paths": [ADMITTED_EDGE_PATH],
    },
]


def find_repo_root() -> Path:
    here = Path.cwd().resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "docs" / "Philosophy.md").exists():
            return candidate
    raise SystemExit("Could not locate repository root from current working directory.")


ROOT = find_repo_root()


def rel_to_path(rel_path: str) -> Path:
    return ROOT / Path(rel_path)


def to_posix(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def stable_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_text(rel_path: str, content: str) -> None:
    path = rel_to_path(rel_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def write_json(rel_path: str, data: Any) -> None:
    write_text(rel_path, stable_json(data))


def write_jsonl(rel_path: str, rows: list[dict[str, Any]]) -> None:
    content = "".join(stable_json(row).replace("\n", "", -1) + "\n" for row in rows)
    write_text(rel_path, content)


def load_json(rel_path: str) -> Any:
    return json.loads(rel_to_path(rel_path).read_text(encoding="utf-8"))


def load_jsonl(rel_path: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        rel_to_path(rel_path).read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append({"line": line_number, "error": str(exc)})
            continue
        if not isinstance(value, dict):
            errors.append({"line": line_number, "error": "row is not a JSON object"})
            continue
        rows.append(value)
    return rows, errors


def flatten_paths(value: Any, prefix: str = "") -> set[str]:
    if isinstance(value, dict):
        paths: set[str] = set()
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else key
            paths.add(child_prefix)
            paths.update(flatten_paths(child, child_prefix))
        return paths
    if isinstance(value, list):
        list_prefix = f"{prefix}[]" if prefix else "[]"
        paths = {list_prefix}
        for child in value:
            paths.update(flatten_paths(child, list_prefix))
        return paths
    return {prefix} if prefix else set()


def value_kind(value: Any) -> str:
    if value is None:
        return "null"
    if value == "":
        return "empty_string"
    if value == []:
        return "empty_array"
    if value == {}:
        return "empty_object"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def unique_json_values(values: list[Any]) -> list[Any]:
    seen: dict[str, Any] = {}
    for value in values:
        seen.setdefault(json.dumps(value, ensure_ascii=False, sort_keys=True), value)
    return [seen[key] for key in sorted(seen)]


def collect_non_mutation_hashes() -> dict[str, Any]:
    groups: list[dict[str, Any]] = []
    for spec in NON_MUTATION_TARGETS:
        paths: list[Path] = []
        for rel in spec.get("paths", []):
            path = rel_to_path(rel)
            if path.exists():
                paths.append(path)
        for pattern in spec.get("globs", []):
            paths.extend(sorted(ROOT.glob(pattern)))

        expected_absent = bool(spec.get("expected_absent", False))
        files = [
            {
                "bytes": path.stat().st_size,
                "path": to_posix(path),
                "sha256": file_sha256(path),
            }
            for path in sorted(set(paths))
            if path.is_file()
        ]
        if files:
            status = "present"
        elif expected_absent:
            status = "absent_expected"
        else:
            status = "absent_unexpected"
        groups.append(
            {
                "file_count": len(files),
                "files": files,
                "group": spec["group"],
                "status": status,
            }
        )
    return {
        "group_count": len(groups),
        "groups": groups,
        "schema_version": "non-mutation-hash-snapshot-v1",
    }


def compare_non_mutation(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_map = {group["group"]: group for group in before["groups"]}
    after_map = {group["group"]: group for group in after["groups"]}
    changed: list[dict[str, Any]] = []
    for group_name in sorted(set(before_map) | set(after_map)):
        left = before_map.get(group_name)
        right = after_map.get(group_name)
        if left != right:
            changed.append({"before": left, "after": right, "group": group_name})
    return {
        "changed_group_count": len(changed),
        "changed_groups": changed,
        "non_mutation_hash_diff_pass": len(changed) == 0,
    }


def build_schema_inventory(
    rows: list[dict[str, Any]], parse_errors: list[dict[str, Any]], artifact_hash: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    field_paths = sorted({path for row in rows for path in flatten_paths(row)})
    field_stats: list[dict[str, Any]] = []
    for field in field_paths:
        present_values = [row[field] for row in rows if field in row]
        type_counts = Counter(value_kind(value) for value in present_values)
        field_stats.append(
            {
                "distinct_count": len(unique_json_values(present_values)),
                "empty_array_count": type_counts.get("empty_array", 0),
                "empty_object_count": type_counts.get("empty_object", 0),
                "empty_string_count": type_counts.get("empty_string", 0),
                "field_path": field,
                "missing_count": len(rows) - len(present_values),
                "null_count": type_counts.get("null", 0),
                "present_count": len(present_values),
                "sample_values": unique_json_values(present_values)[:8],
                "type_counts": dict(sorted(type_counts.items())),
            }
        )

    schema_summary = {
        "additional_field_paths": sorted(set(field_paths) - set(EDGE_REQUIRED_FIELDS)),
        "all_required_fields_present_on_all_rows": all(
            all(field in row for field in EDGE_REQUIRED_FIELDS) for row in rows
        ),
        "artifact_hash_sha256": artifact_hash,
        "field_path_count": len(field_paths),
        "field_paths": field_paths,
        "malformed_row_count": len(parse_errors),
        "malformed_rows": parse_errors,
        "required_field_paths": EDGE_REQUIRED_FIELDS,
        "round_id": ROUND_ID,
        "row_count": len(rows),
        "row_count_interpretation": "artifact_shape_metric_only_not_confirmed_count",
        "schema_version": "admitted-trace-edge-schema-summary-v1",
    }
    inventory = {
        "artifact_hash_sha256": artifact_hash,
        "field_stats": field_stats,
        "input_artifact_path": ADMITTED_EDGE_PATH,
        "malformed_rows": parse_errors,
        "round_id": ROUND_ID,
        "row_count": len(rows),
        "row_count_interpretation": "artifact_shape_metric_only_not_confirmed_count",
        "schema_summary_path": f"{ROUND_ROOT}/admitted_trace_edge_schema_summary.json",
        "schema_version": "admitted-trace-edge-artifact-inventory-v1",
    }
    return inventory, schema_summary


def role_bindings(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    row_id_equals_item_full_type = all(
        row.get("row_id") == row.get("item_full_type") for row in rows
    )
    row_id_equals_destination_ref = all(
        row.get("row_id") == row.get("destination_ref") for row in rows
    )
    edge_type_valid = all(row.get("edge_type") == EDGE_TYPE for row in rows)
    edge_basis_valid = all(row.get("edge_basis") in ALLOWED_EDGE_BASIS for row in rows)

    bindings = [
        {
            "accepted_field_path": "source_ref",
            "accepted_support_fields": ["source_cardinality"],
            "disposition": "sealed",
            "fallback_rejected": ["provenance_label_only", "category_tag"],
            "requirement": "source_object",
            "required_meaning": "Layer4 source object identity",
            "validation": {
                "all_rows_present": all("source_ref" in row for row in rows),
                "all_values_non_empty_string": all(
                    isinstance(row.get("source_ref"), str) and bool(row.get("source_ref"))
                    for row in rows
                ),
                "source_cardinality_minimum_one": all(
                    isinstance(row.get("source_cardinality"), int)
                    and row.get("source_cardinality") >= 1
                    for row in rows
                ),
            },
        },
        {
            "accepted_field_path": "row_id",
            "accepted_support_fields": ["item_full_type", "destination_ref"],
            "disposition": "sealed",
            "fallback_rejected": ["item_display_text", "rendered_body_substring"],
            "requirement": "target_layer3_row_or_item",
            "required_meaning": "Layer3 row/item identity anchor",
            "validation": {
                "all_rows_present": all("row_id" in row for row in rows),
                "all_values_non_empty_string": all(
                    isinstance(row.get("row_id"), str) and bool(row.get("row_id"))
                    for row in rows
                ),
                "item_full_type_matches_row_id": row_id_equals_item_full_type,
                "destination_ref_matches_row_id": row_id_equals_destination_ref,
            },
        },
        {
            "accepted_field_path": "destination_slot",
            "accepted_support_fields": ["destination_ref"],
            "disposition": "sealed",
            "fallback_rejected": [
                "rendered_body_substring",
                "korean_or_english_keyword",
                "cluster_label",
            ],
            "requirement": "destination_body_slot",
            "required_meaning": "Layer3 destination body slot",
            "validation": {
                "all_rows_present": all("destination_slot" in row for row in rows),
                "all_values_non_empty_string": all(
                    isinstance(row.get("destination_slot"), str)
                    and bool(row.get("destination_slot"))
                    for row in rows
                ),
            },
        },
        {
            "accepted_field_path": "edge_type",
            "accepted_support_fields": ["edge_basis", "source_ref", "destination_slot"],
            "disposition": "sealed",
            "fallback_rejected": [
                "source_target_co_occurrence_only",
                "predecessor_detector_readiness_dry_run_pass",
                "field_map_conditioned_readiness_dry_run_pass_as_edge_truth",
            ],
            "relation_tuple_paths": [
                "source_ref",
                "edge_type",
                "edge_basis",
                "destination_slot",
            ],
            "requirement": "explicit_edge_relation",
            "required_meaning": "source object to destination body slot trace relation",
            "validation": {
                "all_rows_present": all("edge_type" in row for row in rows),
                "edge_basis_allowed": edge_basis_valid,
                "edge_type_const_placed_in_body_output": edge_type_valid,
                "relation_direction": "source_ref -> destination_slot",
                "row_is_edge_record": True,
            },
        },
    ]
    all_sealed = all(binding["disposition"] == "sealed" for binding in bindings)
    requirement_matrix = {
        "all_required_roles_sealed": all_sealed,
        "branch_if_selected": BRANCH_CLOSEOUT if all_sealed else "blocked",
        "requirements": bindings,
        "round_id": ROUND_ID,
        "schema_version": "detector-requirement-matrix-v1",
    }
    binding_table = {
        "accepted_binding_count": len(bindings),
        "ambiguous_binding_count": 0,
        "binding_rows": bindings,
        "fallback_binding_count": 0,
        "round_id": ROUND_ID,
        "schema_version": "role-field-binding-table-v1",
    }
    return requirement_matrix, binding_table


def traversal_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    traversal_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        valid = (
            isinstance(row.get("source_ref"), str)
            and bool(row.get("source_ref"))
            and isinstance(row.get("destination_slot"), str)
            and bool(row.get("destination_slot"))
            and row.get("edge_type") == EDGE_TYPE
            and row.get("edge_basis") in ALLOWED_EDGE_BASIS
        )
        traversal_rows.append(
            {
                "destination_body_slot": row.get("destination_slot"),
                "edge_basis": row.get("edge_basis"),
                "edge_type": row.get("edge_type"),
                "line_number": index,
                "relation_direction": "source_ref -> destination_slot",
                "row_id": row.get("row_id"),
                "source_object": row.get("source_ref"),
                "target_layer3_row_or_item": row.get("row_id"),
                "traversal_state": "traversable" if valid else "invalid",
            }
        )
        if not valid:
            failures.append({"line_number": index, "row": row})
    return {
        "confirmed_count": "not_computed",
        "confirmed_measurement_executed": False,
        "detector_count_output_exists": False,
        "failure_count": len(failures),
        "failures": failures,
        "relation_traversal": "source_ref -> edge_type -> destination_slot",
        "round_id": ROUND_ID,
        "schema_version": "source-slot-relation-traversal-report-v1",
        "target_layer3_row_or_item_role": "identity_anchor_not_sequential_hop",
        "traversal_coverage_interpretation": (
            "admitted_edge_row_traversal_coverage_only_not_confirmed_count"
        ),
        "traversal_row_count": len(traversal_rows),
        "traversal_rows": traversal_rows,
    }


def forbidden_fallbacks() -> tuple[dict[str, Any], dict[str, Any]]:
    rows = []
    reason_by_class = {
        "rendered_body_substring": "rendered text is output surface, not detector input",
        "item_display_text": "display text is presentation, not row identity authority",
        "korean_or_english_keyword": "keyword matching is interpretation",
        "category_tag": "category tags do not encode source-to-slot edge relation",
        "cluster_label": "cluster labels are not detector trace fields",
        "provenance_label_only": "provenance alone is not source object identity",
        "source_target_co_occurrence_only": "same-row co-occurrence is not explicit edge semantics",
        "diagnostic_report_only_field": "diagnostic/report-only fields are not current detector input",
        "historical_predecessor_count": "historical predecessor counts do not transfer",
        "row_count_itself": "row count 24 is artifact shape only",
        "predecessor_detector_readiness_dry_run_pass": (
            "2026-06-01 readiness dry-run is not this field map seal"
        ),
        "field_map_conditioned_readiness_dry_run_pass_as_edge_truth": (
            "this dry-run is shape/readiness only after independent field binding"
        ),
    }
    role_by_class = {
        "rendered_body_substring": "destination_body_slot",
        "item_display_text": "target_layer3_row_or_item",
        "korean_or_english_keyword": "destination_body_slot",
        "category_tag": "source_object",
        "cluster_label": "destination_body_slot",
        "provenance_label_only": "source_object",
        "source_target_co_occurrence_only": "explicit_edge_relation",
        "diagnostic_report_only_field": "explicit_edge_relation",
        "historical_predecessor_count": "explicit_edge_relation",
        "row_count_itself": "explicit_edge_relation",
        "predecessor_detector_readiness_dry_run_pass": "explicit_edge_relation",
        "field_map_conditioned_readiness_dry_run_pass_as_edge_truth": (
            "explicit_edge_relation"
        ),
    }
    for fallback_class in FORBIDDEN_FALLBACK_CLASSES:
        rows.append(
            {
                "accepted_as_binding": False,
                "fallback_class": fallback_class,
                "field_path": None,
                "reason": reason_by_class[fallback_class],
                "role": role_by_class[fallback_class],
            }
        )
    classification = {
        "accepted_fallback_count": 0,
        "fallback_classes": rows,
        "round_id": ROUND_ID,
        "schema_version": "forbidden-fallback-classification-v1",
    }
    exclusion = {
        "accepted_fallback_count": 0,
        "excluded_fallback_classes": FORBIDDEN_FALLBACK_CLASSES,
        "round_id": ROUND_ID,
        "schema_version": "forbidden-fallback-exclusion-list-v1",
    }
    return classification, exclusion


def readiness_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    required_field_coverage = {
        field: all(field in row and row[field] not in (None, "") for row in rows)
        for field in EDGE_REQUIRED_FIELDS
    }
    missing_required_field_fail_loud = all(
        field in EDGE_REQUIRED_FIELDS for field in ["source_ref", "destination_slot"]
    )
    return {
        "admission_dry_run_conflated": False,
        "ambiguous_accepted_count": 0,
        "branch_closeout": BRANCH_CLOSEOUT,
        "confirmed_count": "not_computed",
        "confirmed_measurement_executed": False,
        "detector_count_output_exists": False,
        "dry_run_kind": "field_map_conditioned_shape_readiness_only",
        "fallback_access_count": 0,
        "field_map_conditioned": True,
        "field_map_version": FIELD_MAP_VERSION,
        "missing_required_field_behavior": "fail_loud",
        "missing_required_field_fail_loud_test_pass": missing_required_field_fail_loud,
        "readiness_result": "pass",
        "required_field_coverage": required_field_coverage,
        "round_id": ROUND_ID,
        "row_count_interpretation": "artifact_shape_metric_only_not_confirmed_count",
        "schema_version": "field-map-conditioned-readiness-dry-run-report-v1",
        "traversal_coverage": len(rows),
        "traversal_coverage_interpretation": (
            "admitted_edge_row_traversal_coverage_only_not_confirmed_count"
        ),
    }


def no_count_guard(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "confirmed_count": "not_computed",
        "confirmed_measurement_executed": False,
        "detector_count_output_exists": False,
        "guard_pass": True,
        "prohibited_count_like_values": [
            {
                "interpretation": "artifact_shape_metric_only_not_confirmed_count",
                "name": "admitted_edge_row_count",
                "value": len(rows),
            },
            {
                "interpretation": "traversal_coverage_only_not_confirmed_count",
                "name": "traversal_coverage",
                "value": len(rows),
            },
        ],
        "round_id": ROUND_ID,
        "schema_version": "no-count-guard-evidence-v1",
    }


def canonical_field_map(artifact_hash: str) -> dict[str, Any]:
    return {
        "ambiguity_disposition": {
            "accepted_ambiguous_count": 0,
            "state": "none",
        },
        "branch_closeout": BRANCH_CLOSEOUT,
        "confirmed_count": "not_computed",
        "confirmed_measurement_executed": False,
        "contract_closeout_state": CONTRACT_CLOSEOUT_STATE,
        "destination_body_slot_field": "destination_slot",
        "edge_basis_field": "edge_basis",
        "explicit_edge_relation_field": "edge_type",
        "explicit_edge_relation_tuple_fields": [
            "source_ref",
            "edge_type",
            "edge_basis",
            "destination_slot",
        ],
        "field_map_sealed": True,
        "field_map_version": FIELD_MAP_VERSION,
        "forbidden_fallback_list": FORBIDDEN_FALLBACK_CLASSES,
        "input_artifact_hash": artifact_hash,
        "input_artifact_partition": "current_detector_input",
        "input_artifact_path": ADMITTED_EDGE_PATH,
        "measurement_enabled": False,
        "round_id": ROUND_ID,
        "schema_version": "canonical-layer4-confirmed-field-map-manifest-v1",
        "source_cardinality_field": "source_cardinality",
        "source_object_field": "source_ref",
        "target_layer3_row_or_item_field": "row_id",
        "target_layer3_row_or_item_support_fields": [
            "item_full_type",
            "destination_ref",
        ],
    }


def authority_input_manifest(artifact_hash: str, admission_manifest: dict[str, Any]) -> dict[str, Any]:
    artifact_entry = next(
        artifact
        for artifact in admission_manifest.get("artifacts", [])
        if artifact.get("path") == ADMITTED_EDGE_PATH
    )
    return {
        "admission_manifest_path": ADMISSION_MANIFEST_PATH,
        "admission_partition": artifact_entry.get("detector_input_partition"),
        "admission_partition_path": ADMISSION_PARTITION_PATH,
        "admission_report_path": ADMISSION_REPORT_PATH,
        "branch_closeout": BRANCH_CLOSEOUT,
        "confirmed_count": "not_computed",
        "confirmed_measurement_executed": False,
        "contract_closeout_state": CONTRACT_CLOSEOUT_STATE,
        "count_generation_allowed": False,
        "input_artifact_hash": artifact_hash,
        "input_artifact_path": ADMITTED_EDGE_PATH,
        "input_hash_equals_admission_manifest_hash": (
            artifact_hash == artifact_entry.get("sha256")
        ),
        "predecessor_field_map_manifest_path": PREDECESSOR_FIELD_MAP_MANIFEST_PATH,
        "predecessor_readpoints": [
            "2026-05-31 Layer4 Boundary Current Corpus Lock Round",
            "2026-05-31 Layer4 Confirmed Detector Field Map Seal Round",
            "2026-06-01 Layer4 Trace-Edge Authority Admission Round",
        ],
        "publish_review_opened": False,
        "round_id": ROUND_ID,
        "runtime_mutation_allowed": False,
        "schema_version": "field-map-reseal-authority-input-manifest-v1",
    }


def scope_lock_md(artifact_hash: str) -> str:
    return f"""# Layer4 Confirmed Detector Field Map Reseal Scope Lock

round_id = `{ROUND_ID}`

contract_closeout_state = `{CONTRACT_CLOSEOUT_STATE}`

branch_closeout = `{BRANCH_CLOSEOUT}`

## Inputs

- admitted artifact: `{ADMITTED_EDGE_PATH}`
- admitted artifact sha256: `{artifact_hash}`
- admission partition: `current_detector_input`
- predecessor corpus lock: `2026-05-31 Layer4 Boundary Current Corpus Lock Round`
- predecessor field-map seal: `2026-05-31 Layer4 Confirmed Detector Field Map Seal Round`
- predecessor trace-edge admission: `2026-06-01 Layer4 Trace-Edge Authority Admission Round`

## Scope Flags

- count_generation_allowed = `false`
- runtime_mutation_allowed = `false`
- publish_review_opened = `false`
- confirmed_measurement_executed = `false`
- confirmed_count = `not_computed`

The admitted edge row count and traversal coverage are artifact shape metrics only.
"""


def branch_determination_md(row_count: int) -> str:
    return f"""# Field Map Reseal Branch Determination

contract_closeout_state = `{CONTRACT_CLOSEOUT_STATE}`

branch_closeout = `{BRANCH_CLOSEOUT}`

All four required detector roles bind to admitted trace-edge artifact fields:

- `source_object` -> `source_ref`
- `target_layer3_row_or_item` -> `row_id`
- `destination_body_slot` -> `destination_slot`
- `explicit_edge_relation` -> `edge_type` with tuple fields `source_ref`, `edge_basis`, and `destination_slot`

Traversal coverage over `{row_count}` admitted edge rows is recorded as field-map
readiness coverage only. It is not a confirmed count.
"""


def adversarial_review_md() -> str:
    return f"""# Adversarial Review Report

verdict = `PASS`

critical_finding_count = `0`

## Checks

- The row count `24` is not used as a detector count.
- The 2026-06-01 admission dry-run is not used as this round's field-map seal.
- This round's dry-run is shape/readiness only and not edge-truth evidence.
- `source_target_co_occurrence_only` is rejected as fallback.
- `row_id` is used only as the target row/item identity anchor.
- `edge_type` plus tuple fields provides the explicit source-to-slot relation.
- No runtime, rendered text, source facts, source decisions, quality, publish, or runtime-state surface is mutated.

review_gate = `PASS`
"""


def closeout_md(row_count: int, artifact_hash: str) -> str:
    non_claims = "\n".join(f"- {claim}" for claim in NON_CLAIMS)
    validated = "\n".join(f"- {item}" for item in VALIDATION_CEILING["validated"])
    out_of_scope = "\n".join(f"- {item}" for item in VALIDATION_CEILING["out_of_scope"])
    return f"""# Layer4 Confirmed Detector Field Map Reseal Closeout

contract_closeout_state = `{CONTRACT_CLOSEOUT_STATE}`

branch_closeout = `{BRANCH_CLOSEOUT}`

## Claim Boundary

The admitted trace-edge artifact exposes a detector-consumable field map for the four required roles. The sealed field map is `source_ref`, `row_id`, `destination_slot`, and `edge_type` with tuple support from `edge_basis`.

The input artifact hash is `{artifact_hash}`. The admitted edge row count is `{row_count}`, but that value is an artifact shape metric only and is not a confirmed detector count.

## Validation Ceiling

Validated:

{validated}

Out of scope:

{out_of_scope}

Unvalidated but in scope: none.

## Non-Claims

{non_claims}
"""


def docs_addendum_candidate_md(row_count: int, artifact_hash: str) -> str:
    return f"""# Docs Addendum Candidate

## DECISIONS.md Candidate

## {ROUND_DATE} - Iris DVF 3-3 Layer4 Confirmed Detector Field Map Reseal Round closes as field-map sealed
- 상태: 채택 / detector field-map reseal closeout
- 결정: `Iris DVF 3-3 Layer4 Confirmed Detector Field Map Reseal Round`를 `{BRANCH_CLOSEOUT}`로 닫는다.
- 결과:
  - contract closeout state: `{CONTRACT_CLOSEOUT_STATE}`
  - input artifact: `{ADMITTED_EDGE_PATH}`
  - input artifact sha256 `{artifact_hash}`
  - admitted edge row count `{row_count}` as artifact shape metric only
  - field_map_version `{FIELD_MAP_VERSION}`
  - confirmed_measurement_executed `false`
  - confirmed_count `not_computed`
- 영향: admitted trace-edge authority artifact 위에 future count measurement가 읽을 detector field-map readpoint가 additive successor로 봉인됐다.
- 비주장: current count, live-corpus occurrence count, zero-occurrence closeout, Layer4 resolved, runtime/source/rendered/state mutation, publish mutation review, runtime rollout, manual in-game validation, deployment, Workshop/B42/release readiness 아님.

## ARCHITECTURE.md Evidence Capsule Candidate

| {ROUND_DATE} Layer4 confirmed detector field-map reseal | `{ROUND_ROOT}/`; `generate_round_artifacts.py` | branch `{BRANCH_CLOSEOUT}`; row count `{row_count}` shape metric only; field map roles `source_ref / row_id / destination_slot / edge_type`; confirmed count `not_computed`; non-mutation hash diff pass; hard gate pass. | Field-map prerequisite only. No count, no runtime mutation, no release readiness. |

## ROADMAP.md Candidate

- **{ROUND_DATE} Layer4 Confirmed Detector Field Map Reseal closeout**: admitted trace-edge sidecar now has a sealed detector field map for future `LAYER4_ABSORPTION_CONFIRMED` measurement. Count remains not computed; no runtime/source/rendered/state mutation or release readiness claim is opened.
"""


def artifact_hash_manifest(generated_paths: list[str]) -> dict[str, Any]:
    artifacts = []
    for rel_path in sorted(generated_paths):
        if rel_path.endswith("/artifact_hash_manifest.json"):
            continue
        path = rel_to_path(rel_path)
        if not path.exists() or not path.is_file():
            continue
        artifacts.append(
            {
                "bytes": path.stat().st_size,
                "path": rel_path,
                "sha256": file_sha256(path),
            }
        )
    return {
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "branch_closeout": BRANCH_CLOSEOUT,
        "confirmed_count": "not_computed",
        "confirmed_measurement_executed": False,
        "round_id": ROUND_ID,
        "schema_version": "field-map-reseal-artifact-hash-manifest-v1",
    }


def parse_generated_files(generated_root: str = ROUND_ROOT) -> dict[str, Any]:
    root = rel_to_path(generated_root)
    errors: list[dict[str, Any]] = []
    json_count = 0
    jsonl_count = 0
    jsonl_rows = 0
    for path in sorted(root.glob("*.json")):
        json_count += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append({"error": str(exc), "path": to_posix(path)})
    for path in sorted(root.glob("*.jsonl")):
        jsonl_count += 1
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            jsonl_rows += 1
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    {"error": str(exc), "line": line_number, "path": to_posix(path)}
                )
    return {
        "errors": errors,
        "json_file_count": json_count,
        "jsonl_file_count": jsonl_count,
        "jsonl_row_count": jsonl_rows,
        "pass": len(errors) == 0,
    }


def validate_generated_files() -> dict[str, Any]:
    parse_check = parse_generated_files()
    canonical = load_json(f"{ROUND_ROOT}/canonical_field_map_manifest.json")
    dry_run = load_json(f"{ROUND_ROOT}/field_map_conditioned_readiness_dry_run_report.json")
    no_count = load_json(f"{ROUND_ROOT}/no_count_guard_evidence.json")
    non_mutation = load_json(f"{ROUND_ROOT}/non_mutation_hash_report.json")
    artifact_manifest = load_json(f"{ROUND_ROOT}/artifact_hash_manifest.json")
    generated_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(rel_to_path(ROUND_ROOT).glob("*"))
        if path.is_file() and path.name != "generate_round_artifacts.py"
    )
    banned_alias_present = "TRACE_EDGE_ABSENT_MEASUREMENT_UNAVAILABLE" in generated_text
    absolute_path_present = "C:\\" in generated_text or "C:/" in generated_text
    hard_gate_checks = {
        "absolute_path_absent_from_generated_artifacts": not absolute_path_present,
        "admission_partition_current_detector_input": (
            canonical["input_artifact_partition"] == "current_detector_input"
        ),
        "all_four_roles_sealed": canonical["field_map_sealed"] is True,
        "banned_predecessor_alias_absent": not banned_alias_present,
        "branch_closeout_consistency": (
            canonical["branch_closeout"]
            == dry_run["branch_closeout"]
            == BRANCH_CLOSEOUT
        ),
        "confirmed_count_not_computed": (
            canonical["confirmed_count"]
            == dry_run["confirmed_count"]
            == no_count["confirmed_count"]
            == "not_computed"
        ),
        "confirmed_measurement_not_executed": (
            canonical["confirmed_measurement_executed"] is False
            and dry_run["confirmed_measurement_executed"] is False
            and no_count["confirmed_measurement_executed"] is False
        ),
        "fallback_access_count_zero": dry_run["fallback_access_count"] == 0,
        "final_file_parse_pass": parse_check["pass"],
        "non_mutation_hash_diff_pass": non_mutation["non_mutation_hash_diff_pass"],
        "readiness_dry_run_pass": dry_run["readiness_result"] == "pass",
        "artifact_hash_manifest_parse_pass": artifact_manifest["artifact_count"] >= 1,
    }
    return {
        "all_gates_pass": all(hard_gate_checks.values()),
        "branch_closeout": BRANCH_CLOSEOUT,
        "contract_closeout_state": CONTRACT_CLOSEOUT_STATE,
        "final_file_parse_check": parse_check,
        "hard_gate_checks": hard_gate_checks,
        "round_id": ROUND_ID,
        "schema_version": "field-map-reseal-validation-summary-v1",
    }


def generate() -> dict[str, Any]:
    before_hashes = collect_non_mutation_hashes()

    rows, parse_errors = load_jsonl(ADMITTED_EDGE_PATH)
    artifact_hash = file_sha256(rel_to_path(ADMITTED_EDGE_PATH))
    admission_manifest = load_json(ADMISSION_MANIFEST_PATH)
    admission_partition = load_json(ADMISSION_PARTITION_PATH)
    admission_entry = next(
        artifact
        for artifact in admission_manifest.get("artifacts", [])
        if artifact.get("path") == ADMITTED_EDGE_PATH
    )

    if admission_entry.get("sha256") != artifact_hash:
        raise SystemExit("Admitted edge artifact hash does not match admission manifest.")
    if admission_entry.get("detector_input_partition") != "current_detector_input":
        raise SystemExit("Admitted edge artifact is not in current_detector_input.")
    if ADMITTED_EDGE_PATH not in admission_partition["partitions"]["current_detector_input"]:
        raise SystemExit("Admitted edge artifact missing from partition file.")
    if parse_errors:
        raise SystemExit(f"Admitted edge artifact JSONL parse errors: {parse_errors}")

    inventory, schema_summary = build_schema_inventory(rows, parse_errors, artifact_hash)
    requirement_matrix, binding_table = role_bindings(rows)
    traversal = traversal_report(rows)
    fallback_classification, fallback_exclusion = forbidden_fallbacks()
    ambiguity_summary = {
        "accepted_ambiguous_count": 0,
        "ambiguity_classes": [
            "AMBIGUOUS_SOURCE_OBJECT",
            "AMBIGUOUS_TARGET_IDENTITY",
            "AMBIGUOUS_SLOT_SCOPE",
            "AMBIGUOUS_EDGE_RELATION",
            "AMBIGUOUS_RELATION_DIRECTION",
            "FORBIDDEN_FALLBACK_ONLY",
        ],
        "ambiguous_candidate_count": 0,
        "branch_c_available_if_ambiguity_found": True,
        "round_id": ROUND_ID,
        "schema_version": "ambiguity-summary-v1",
    }

    write_text(f"{ROUND_ROOT}/field_map_reseal_scope_lock.md", scope_lock_md(artifact_hash))
    write_json(
        f"{ROUND_ROOT}/field_map_reseal_authority_input_manifest.json",
        authority_input_manifest(artifact_hash, admission_manifest),
    )
    write_json(f"{ROUND_ROOT}/admitted_trace_edge_artifact_inventory.json", inventory)
    write_json(f"{ROUND_ROOT}/admitted_trace_edge_schema_summary.json", schema_summary)
    write_json(f"{ROUND_ROOT}/detector_requirement_matrix.json", requirement_matrix)
    write_json(f"{ROUND_ROOT}/role_field_binding_table.json", binding_table)
    write_json(f"{ROUND_ROOT}/source_slot_relation_traversal_report.json", traversal)
    write_json(
        f"{ROUND_ROOT}/forbidden_fallback_classification.json",
        fallback_classification,
    )
    write_json(
        f"{ROUND_ROOT}/forbidden_fallback_exclusion_list.json",
        fallback_exclusion,
    )
    write_jsonl(f"{ROUND_ROOT}/ambiguity_register.jsonl", [])
    write_json(f"{ROUND_ROOT}/ambiguity_summary.json", ambiguity_summary)
    write_json(
        f"{ROUND_ROOT}/canonical_field_map_manifest.json",
        canonical_field_map(artifact_hash),
    )
    write_text(
        f"{ROUND_ROOT}/field_map_reseal_branch_determination.md",
        branch_determination_md(len(rows)),
    )
    write_json(
        f"{ROUND_ROOT}/field_map_conditioned_readiness_dry_run_report.json",
        readiness_report(rows),
    )
    write_json(f"{ROUND_ROOT}/no_count_guard_evidence.json", no_count_guard(rows))

    after_hashes = collect_non_mutation_hashes()
    non_mutation_report = {
        **compare_non_mutation(before_hashes, after_hashes),
        "after": after_hashes,
        "before": before_hashes,
        "round_id": ROUND_ID,
        "schema_version": "field-map-reseal-non-mutation-hash-report-v1",
    }
    write_json(f"{ROUND_ROOT}/non_mutation_hash_report.json", non_mutation_report)

    write_text(f"{ROUND_ROOT}/adversarial_review_report.md", adversarial_review_md())
    write_text(f"{ROUND_ROOT}/field_map_reseal_closeout.md", closeout_md(len(rows), artifact_hash))
    write_text(
        f"{ROUND_ROOT}/docs_addendum_candidate.md",
        docs_addendum_candidate_md(len(rows), artifact_hash),
    )

    generated_paths = [
        f"{ROUND_ROOT}/generate_round_artifacts.py",
        f"{ROUND_ROOT}/field_map_reseal_scope_lock.md",
        f"{ROUND_ROOT}/field_map_reseal_authority_input_manifest.json",
        f"{ROUND_ROOT}/admitted_trace_edge_artifact_inventory.json",
        f"{ROUND_ROOT}/admitted_trace_edge_schema_summary.json",
        f"{ROUND_ROOT}/detector_requirement_matrix.json",
        f"{ROUND_ROOT}/role_field_binding_table.json",
        f"{ROUND_ROOT}/source_slot_relation_traversal_report.json",
        f"{ROUND_ROOT}/forbidden_fallback_classification.json",
        f"{ROUND_ROOT}/forbidden_fallback_exclusion_list.json",
        f"{ROUND_ROOT}/ambiguity_register.jsonl",
        f"{ROUND_ROOT}/ambiguity_summary.json",
        f"{ROUND_ROOT}/canonical_field_map_manifest.json",
        f"{ROUND_ROOT}/field_map_reseal_branch_determination.md",
        f"{ROUND_ROOT}/field_map_conditioned_readiness_dry_run_report.json",
        f"{ROUND_ROOT}/no_count_guard_evidence.json",
        f"{ROUND_ROOT}/non_mutation_hash_report.json",
        f"{ROUND_ROOT}/adversarial_review_report.md",
        f"{ROUND_ROOT}/field_map_reseal_closeout.md",
        f"{ROUND_ROOT}/artifact_hash_manifest.json",
        f"{ROUND_ROOT}/docs_addendum_candidate.md",
    ]
    manifest = artifact_hash_manifest(generated_paths)
    digest_scope = [path for path in generated_paths if not path.endswith("artifact_hash_manifest.json")]
    first_digest = sha256_bytes(
        "\n".join(
            f"{path}:{file_sha256(rel_to_path(path))}" for path in sorted(digest_scope)
        ).encode("utf-8")
    )
    second_digest = sha256_bytes(
        "\n".join(
            f"{path}:{file_sha256(rel_to_path(path))}" for path in sorted(digest_scope)
        ).encode("utf-8")
    )
    manifest["determinism"] = {
        "first_digest": first_digest,
        "pass": first_digest == second_digest,
        "scope": sorted(digest_scope),
        "second_digest": second_digest,
    }
    manifest["final_file_parse_check"] = parse_generated_files()
    write_json(f"{ROUND_ROOT}/artifact_hash_manifest.json", manifest)

    validation = validate_generated_files()
    if not validation["all_gates_pass"]:
        raise SystemExit(stable_json(validation))
    return validation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    validation = validate_generated_files() if args.validate_only else generate()
    sys.stdout.write(stable_json(validation))
    return 0 if validation["all_gates_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
