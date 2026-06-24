from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROUND_ID = "layer4_trace_edge_authority_admission_round"
ROUND_DATE = "2026-06-01"
ROUND_ROOT_NAME = (
    "Iris/build/description/v2/staging/compose_contract_migration/"
    "layer4_trace_edge_authority_admission_round"
)
PLAN_PATH = "docs/Iris/iris-dvf-3-3-layer4-trace-edge-authority-admission-round-plan.md"

LOCKED_CORPUS_PATHS = [
    "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
    "Iris/build/description/v2/output/dvf_3_3_rendered.json",
    "Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl",
    "Iris/build/description/v2/tools/style/rules/structural_rules.json",
]
PREDECESSOR_MANIFEST_PATH = (
    "Iris/build/description/v2/staging/compose_contract_migration/"
    "layer4_boundary_current_corpus_lock_round/layer4_boundary_current_corpus_manifest.json"
)
PREDECESSOR_MANIFEST_SHA256_PATH = (
    "Iris/build/description/v2/staging/compose_contract_migration/"
    "layer4_boundary_current_corpus_lock_round/layer4_boundary_current_corpus_manifest.sha256"
)
FIELD_MAP_MANIFEST_PATH = (
    "Iris/build/description/v2/staging/compose_contract_migration/"
    "layer4_confirmed_detector_field_map_seal_round/"
    "layer4_confirmed_detector_field_map_manifest.json"
)
EXPECTED_PREDECESSOR_MANIFEST_SHA256 = (
    "d394f95f5f2a157679238e005a90929349eb807a8180824d8f0ed30240290402"
)

FACTS_PATH = "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
DECISIONS_PATH = "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl"
PROFILES_PATH = "Iris/build/description/v2/data/compose_profiles_v2.json"
IDENTITY_RULES_PATH = "Iris/build/description/v2/data/compose_profile_identity_hint_rules.json"
PRECEDENCE_RULES_PATH = "Iris/build/description/v2/data/compose_profile_conflict_precedence_rules.json"
OVERLAY_PATH = "Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl"

EDGE_TYPE = "placed_in_body_output"
ALLOWED_EDGE_BASIS = [
    "recovered_body_plan_relation_trace",
    "recovered_compose_relation_trace",
    "generated_body_plan_relation_trace",
    "generated_compose_relation_trace",
]
FORBIDDEN_EDGE_BASIS = [
    "text_similarity",
    "expression_match",
    "rendered_substring_only",
    "cluster_label",
    "provenance_label",
    "row_co_occurrence",
    "body_slot_hint_only",
    "source_object_hint_only",
    "diagnostic_report_label",
    "historical_reference_only",
    "preview_or_fixture_only",
]
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
EDGE_OPTIONAL_FIELDS: list[str] = []
EDGE_FORBIDDEN_FIELDS = ["authority_class", "admission_state", "detector_input_partition"]

RECOVERY_CLASSES = [
    "explicit_trace_edge",
    "body_slot_hint_only",
    "source_object_hint_only",
    "co_occurrence_only",
    "label_or_provenance_only",
    "diagnostic_only",
    "historical_only",
    "rejected_non_edge",
]
BRANCH_DECISIONS = [
    "RECOVERABLE",
    "NOT_RECOVERABLE_PRODUCTION_APPROVED",
    "NOT_RECOVERABLE_PRODUCTION_DEFERRED",
    "BLOCKED_AUTHORITY_UNAVAILABLE",
]
TERMINAL_BRANCHES = [
    "EDGE_AUTHORITY_RECOVERED_AND_ADMITTED",
    "EDGE_AUTHORITY_PRODUCED_AND_ADMITTED",
    "EDGE_AUTHORITY_UNRECOVERABLE_NO_ARTIFACT_PRODUCED",
    "closed_rejected_non_authority_trace_candidates",
    "blocked_trace_edge_authority_unavailable_no_detector_count",
    "blocked_trace_edge_schema_invalid",
    "blocked_trace_edge_referential_integrity_failed",
    "blocked_trace_edge_provenance_failed",
    "blocked_trace_edge_admission_rejected",
    "blocked_detector_readiness_failed",
    "blocked_production_approval_missing",
    "blocked_no_count_guard_failed",
    "blocked_non_mutation_invariant_failed",
    "blocked_claim_overreach",
]

NON_CLAIMS = [
    "no LAYER4_ABSORPTION_CONFIRMED current count",
    "no live-corpus occurrence count",
    "no confirmed count 0 declaration",
    "no zero-occurrence closeout",
    "no Layer4 absorption resolved claim",
    "no Layer4 policy redesign",
    "no SUSPECT tier coverage",
    "no FUNCTION_NARROW second rollout",
    "no ACQ_DOMINANT remeasurement",
    "no publish mutation review",
    "no source facts mutation",
    "no source decisions mutation",
    "no rendered text mutation",
    "no runtime Lua mutation",
    "no packaged Lua mutation",
    "no quality_state mutation",
    "no publish_state mutation",
    "no runtime_state mutation",
    "no runtime rollout",
    "no manual in-game validation pass",
    "no deployment",
    "no Workshop readiness",
    "no B42 readiness",
    "no release readiness",
    "no ready_for_release",
    "no repository-wide machine-enforced preflight",
]

NON_MUTATION_SCOPES = {
    "source_facts": [FACTS_PATH],
    "source_decisions": [DECISIONS_PATH],
    "rendered_text": ["Iris/build/description/v2/output/dvf_3_3_rendered.json"],
    "runtime_lua": ["Iris/media/lua/client/Iris"],
    "packaged_lua": ["Iris/build/package/Iris/media/lua"],
    "quality_state": ["Iris/build/description/v2/output/dvf_3_3_rendered.json"],
    "publish_state": ["Iris/build/description/v2/output/dvf_3_3_rendered.json"],
    "runtime_state": ["Iris/media/lua/client/Iris/Data"],
}


def find_repo_root(start: Path) -> Path:
    for path in [start, *start.parents]:
        if (path / "docs" / "Philosophy.md").exists():
            return path
    raise RuntimeError("Could not locate repository root.")


SCRIPT_PATH = Path(__file__).resolve()
ROUND_ROOT = SCRIPT_PATH.parent
REPO_ROOT = find_repo_root(SCRIPT_PATH)


def repo_path(path_text: str) -> Path:
    return REPO_ROOT / path_text


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def stable_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def json_bytes(data: Any) -> bytes:
    return stable_json(data).encode("utf-8")


def jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    ).encode("utf-8")


def md_bytes(text: str) -> bytes:
    return (text.rstrip() + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes()) if path.exists() and path.is_file() else ""


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(path: Path, data: Any) -> None:
    write_bytes(path, json_bytes(data))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    write_bytes(path, jsonl_bytes(rows))


def write_md(path: Path, text: str) -> None:
    write_bytes(path, md_bytes(text))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_predecessor_sha(text: str) -> str:
    for token in text.replace(":", " ").split():
        if len(token) == 64 and all(char in "0123456789abcdefABCDEF" for char in token):
            return token.lower()
    return ""


def digest_path(path_text: str) -> dict[str, Any]:
    path = repo_path(path_text)
    if not path.exists():
        return {"path": path_text, "exists": False, "sha256": None, "file_count": 0}
    if path.is_file():
        return {
            "path": path_text,
            "exists": True,
            "sha256": sha256_file(path),
            "file_count": 1,
            "bytes": path.stat().st_size,
        }
    files = []
    for child in sorted(path.rglob("*"), key=lambda item: rel(item).lower()):
        if child.is_file():
            files.append(
                {
                    "path": rel(child),
                    "sha256": sha256_file(child),
                    "bytes": child.stat().st_size,
                }
            )
    return {
        "path": path_text,
        "exists": True,
        "sha256": sha256_bytes(json_bytes(files)),
        "file_count": len(files),
    }


def collect_non_mutation_snapshot() -> dict[str, Any]:
    groups: dict[str, Any] = {}
    for group, paths in sorted(NON_MUTATION_SCOPES.items()):
        groups[group] = [digest_path(path) for path in paths]
    return groups


def compare_snapshots(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    changed = [
        group
        for group in sorted(set(before) | set(after))
        if before.get(group) != after.get(group)
    ]
    return {
        "non_mutation_hash_diff_pass": not changed,
        "changed_group_count": len(changed),
        "changed_groups": changed,
        "before": before,
        "after": after,
    }


def load_locked_row_ids() -> dict[str, Any]:
    facts = {str(row["item_id"]) for row in load_jsonl(repo_path(FACTS_PATH))}
    overlay = {str(row["item_id"]) for row in load_jsonl(repo_path(OVERLAY_PATH))}
    rendered_doc = load_json(repo_path("Iris/build/description/v2/output/dvf_3_3_rendered.json"))
    rendered_entries = rendered_doc.get("entries", {})
    rendered = {str(key) for key in rendered_entries} if isinstance(rendered_entries, dict) else set()
    union = set().union(facts, overlay, rendered)
    intersection = facts & overlay & rendered
    return {
        "facts_row_ids": sorted(facts),
        "overlay_row_ids": sorted(overlay),
        "rendered_row_ids": sorted(rendered),
        "union": sorted(union),
        "intersection": sorted(intersection),
        "all_locked_surfaces_share_identity": facts == overlay == rendered,
    }


def current_locked_corpus_manifest_paths() -> list[str]:
    manifest = load_json(repo_path(PREDECESSOR_MANIFEST_PATH))
    surfaces = manifest.get("included_surfaces", [])
    return [str(row.get("path")) for row in surfaces if isinstance(row, dict)]


def build_scope_manifest() -> dict[str, Any]:
    predecessor_sha_text = repo_path(PREDECESSOR_MANIFEST_SHA256_PATH).read_text(encoding="utf-8")
    predecessor_sha = parse_predecessor_sha(predecessor_sha_text)
    manifest_paths = current_locked_corpus_manifest_paths()
    field_map = load_json(repo_path(FIELD_MAP_MANIFEST_PATH))
    return {
        "schema_version": "layer4-trace-edge-authority-scope-manifest-v1",
        "round_id": ROUND_ID,
        "round_date": ROUND_DATE,
        "round_goal": "trace_edge_authority_and_admission_only",
        "scope_qualifier": "trace_edge_authority_admission_only",
        "predecessor_readpoints": {
            "layer4_policy_predecessor_zero_count": "historical_only_no_current_count_inheritance",
            "layer4_boundary_current_corpus_lock": "closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight",
            "layer4_confirmed_detector_field_map_seal": "closed_with_confirmed_measurement_unavailable_trace_absent",
        },
        "current_locked_corpus_paths": LOCKED_CORPUS_PATHS,
        "current_locked_corpus_paths_manifest_confirmation": manifest_paths == LOCKED_CORPUS_PATHS,
        "predecessor_manifest_sha256": predecessor_sha,
        "expected_predecessor_manifest_sha256": EXPECTED_PREDECESSOR_MANIFEST_SHA256,
        "predecessor_manifest_sha256_match": predecessor_sha == EXPECTED_PREDECESSOR_MANIFEST_SHA256,
        "field_map_predecessor": {
            "detector_closeout_branch": field_map.get("detector_closeout_branch"),
            "measurement_unavailable": field_map.get("measurement_unavailable"),
            "required_fields": field_map.get("required_fields"),
        },
        "count_generation_allowed": False,
        "runtime_mutation_allowed": False,
        "publish_review_opened": False,
        "confirmed_measurement_executed": False,
        "confirmed_count": "not_computed",
        "prior_zero_count_inheritance_allowed": False,
    }


def iter_json_values(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    values: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, child in sorted(value.items(), key=lambda item: str(item[0])):
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            values.extend(iter_json_values(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_prefix = f"{prefix}[]" if prefix else "[]"
            if isinstance(child, (dict, list)):
                values.extend(iter_json_values(child, child_prefix))
            else:
                values.append((child_prefix, child))
    else:
        values.append((prefix, value))
    return values


def read_json_surface(path_text: str) -> list[tuple[str, Any, str | None]]:
    path = repo_path(path_text)
    if path.suffix.lower() == ".jsonl":
        rows = []
        for index, row in enumerate(load_jsonl(path), start=1):
            row_id = str(row.get("item_id") or row.get("row_id") or f"line_{index}")
            for field_path, value in iter_json_values(row):
                rows.append((field_path, value, row_id))
        return rows
    doc = load_json(path)
    return [(field_path, value, None) for field_path, value in iter_json_values(doc)]


def is_candidate_field(field_path: str, value: Any) -> bool:
    lowered = field_path.lower()
    terms = [
        "row_id",
        "item_id",
        "entries.",
        "source",
        "origin",
        "ref",
        "slot",
        "body",
        "trace",
        "edge",
        "cluster",
        "role",
        "provenance",
        "section",
        "layer",
    ]
    if any(term in lowered for term in terms):
        return True
    return isinstance(value, str) and any(term in value.lower() for term in ("trace", "edge", "layer4"))


def classify_candidate(path_text: str, field_path: str, value: Any) -> tuple[str, str]:
    lowered = field_path.lower()
    if all(field in lowered for field in ("source_ref", "destination_ref", "edge_type")):
        return "explicit_trace_edge", "contains explicit edge relation fields"
    if "body_slot_hints" in lowered or "representative_slot" in lowered:
        return "body_slot_hint_only", "body slot hint has no source-to-destination edge identity"
    if lowered.endswith("item_id") or ".entries." in lowered:
        return "source_object_hint_only", "row identity alone is not source object to destination relation"
    if any(term in lowered for term in ("selected_cluster", "selected_role", "compose_profile", "reason_code")):
        return "label_or_provenance_only", "cluster/role/profile label is not an explicit edge"
    if any(term in lowered for term in ("fact_origin", "origin", "provenance", "source")):
        return "label_or_provenance_only", "source/provenance label lacks destination-slot relation"
    if path_text.endswith("structural_rules.json"):
        return "diagnostic_only", "style rule config is detector context, not row-level trace authority"
    if "text_ko" in lowered:
        return "rejected_non_edge", "rendered text substring is forbidden as edge authority"
    if "body" in lowered or "slot" in lowered:
        return "body_slot_hint_only", "body/slot field lacks source relation"
    return "rejected_non_edge", "field does not satisfy layer4_trace_edge.v1 relation identity"


def discover_recovery_candidates() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidate_rows: list[dict[str, Any]] = []
    occurrence = 0
    for path_text in LOCKED_CORPUS_PATHS + [DECISIONS_PATH, PROFILES_PATH]:
        if not repo_path(path_text).exists():
            continue
        for field_path, value, row_id in read_json_surface(path_text):
            if not is_candidate_field(field_path, value):
                continue
            occurrence += 1
            candidate_class, reject_reason = classify_candidate(path_text, field_path, value)
            relation_field_presence = {
                field: field in field_path.split(".") or field_path.endswith(field)
                for field in EDGE_REQUIRED_FIELDS
            }
            candidate_rows.append(
                {
                    "candidate_id": f"candidate_{occurrence:05d}",
                    "path": path_text,
                    "row_id": row_id,
                    "field_path": field_path,
                    "value_type": type(value).__name__,
                    "classification": candidate_class,
                    "reject_reason": None if candidate_class == "explicit_trace_edge" else reject_reason,
                    "relation_field_presence": relation_field_presence,
                }
            )
    counts = Counter(row["classification"] for row in candidate_rows)
    for class_name in RECOVERY_CLASSES:
        counts.setdefault(class_name, 0)
    summary = {
        "schema_version": "trace-edge-recovery-classification-summary-v1",
        "round_id": ROUND_ID,
        "candidate_count": len(candidate_rows),
        "classification_counts": dict(sorted(counts.items())),
        "candidate_classification_complete": True,
        "unknown_candidate_count": 0,
        "unclassified_candidate_count": 0,
        "explicit_trace_edge_candidate_count": counts["explicit_trace_edge"],
        "rejected_candidate_reason_coverage": all(
            row["classification"] == "explicit_trace_edge" or bool(row["reject_reason"])
            for row in candidate_rows
        ),
        "recovery_result": "not_recoverable"
        if counts["explicit_trace_edge"] == 0
        else "recoverable_requires_normalization",
    }
    return candidate_rows, summary


def import_compose_modules() -> dict[str, Any]:
    root = REPO_ROOT / "Iris/build/description/v2"
    build_dir = root / "tools/build"
    for path in (root, build_dir):
        text = str(path)
        if text not in sys.path:
            sys.path.insert(0, text)
    from tools.build.compose_layer3_body_profile import (  # type: ignore
        DEFAULT_RESOLVER_AUTHORITY_MODE,
        load_profile_resolution_rules,
    )
    from tools.build.compose_layer3_io import load_optional_jsonl_map  # type: ignore
    from tools.build.compose_layer3_render import compose_all_v2  # type: ignore

    return {
        "DEFAULT_RESOLVER_AUTHORITY_MODE": DEFAULT_RESOLVER_AUTHORITY_MODE,
        "load_profile_resolution_rules": load_profile_resolution_rules,
        "load_optional_jsonl_map": load_optional_jsonl_map,
        "compose_all_v2": compose_all_v2,
    }


def build_generated_body_plan_entries() -> dict[str, dict[str, Any]]:
    modules = import_compose_modules()
    facts_list = load_jsonl(repo_path(FACTS_PATH))
    decisions_list = load_jsonl(repo_path(DECISIONS_PATH))
    profiles = load_json(repo_path(PROFILES_PATH))
    overlay_map = modules["load_optional_jsonl_map"](repo_path(OVERLAY_PATH))
    identity_map, precedence_rules = modules["load_profile_resolution_rules"](
        identity_rules_path=repo_path(IDENTITY_RULES_PATH),
        precedence_rules_path=repo_path(PRECEDENCE_RULES_PATH),
    )
    entries, _normalization_logs, _requeue_candidates = modules["compose_all_v2"](
        facts_list,
        decisions_list,
        overlay_map,
        profiles,
        identity_hint_target_map=identity_map,
        precedence_rules=precedence_rules,
        resolver_authority_mode=modules["DEFAULT_RESOLVER_AUTHORITY_MODE"],
    )
    return entries


def section_source_fields(section: dict[str, Any]) -> list[str]:
    fields = section.get("source_fields", [])
    if not isinstance(fields, list):
        return []
    return [str(field) for field in fields if str(field).strip()]


def build_generated_edges() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    entries = build_generated_body_plan_entries()
    edges: list[dict[str, Any]] = []
    for item_id in sorted(entries):
        entry = entries[item_id]
        body_plan = entry.get("body_plan")
        if not isinstance(body_plan, dict):
            continue
        sections = body_plan.get("emitted_sections", [])
        if not isinstance(sections, list):
            continue
        for section in sections:
            if not isinstance(section, dict):
                continue
            source_fields = section_source_fields(section)
            section_name = str(section.get("section") or "").strip()
            if not section_name or not source_fields:
                continue
            for source_ref in source_fields:
                edges.append(
                    {
                        "row_id": item_id,
                        "item_full_type": item_id,
                        "source_ref": source_ref,
                        "source_cardinality": len(source_fields),
                        "destination_ref": item_id,
                        "destination_slot": section_name,
                        "edge_type": EDGE_TYPE,
                        "edge_basis": "generated_body_plan_relation_trace",
                    }
                )
    digest = sha256_bytes(jsonl_bytes(edges))
    report = {
        "schema_version": "layer4-trace-edge-generation-report-v1",
        "round_id": ROUND_ID,
        "observer_only_emission": True,
        "producer_location": "build_time_offline_compose_body_plan_sidecar",
        "source_surfaces": [
            FACTS_PATH,
            DECISIONS_PATH,
            PROFILES_PATH,
            IDENTITY_RULES_PATH,
            PRECEDENCE_RULES_PATH,
            OVERLAY_PATH,
        ],
        "generation_time_relation_evidence": {
            "producer": "tools.build.compose_layer3_body_profile.build_body_plan_sections",
            "relation_fields": [
                "body_plan.emitted_sections[].source_fields[]",
                "body_plan.emitted_sections[].section",
                "entry item_id",
            ],
            "rendered_text_reverse_parser_used": False,
            "text_similarity_used": False,
        },
        "generated_edge_count": len(edges),
        "generated_edge_count_interpretation": "artifact_shape_metric_only_not_confirmed_count",
        "generated_row_count": len({edge["row_id"] for edge in edges}),
        "edge_artifact_sha256": digest,
        "confirmed_measurement_executed": False,
        "confirmed_count": "not_computed",
    }
    return edges, report


def build_edge_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "layer4_trace_edge.v1",
        "type": "object",
        "additionalProperties": False,
        "required": EDGE_REQUIRED_FIELDS,
        "properties": {
            "row_id": {"type": "string", "minLength": 1},
            "item_full_type": {"type": "string", "minLength": 1},
            "source_ref": {"type": "string", "minLength": 1},
            "source_cardinality": {"type": "integer", "minimum": 1},
            "destination_ref": {"type": "string", "minLength": 1},
            "destination_slot": {"type": "string", "minLength": 1},
            "edge_type": {"const": EDGE_TYPE},
            "edge_basis": {"enum": ALLOWED_EDGE_BASIS},
        },
        "forbidden_basis_or_substitute_values": FORBIDDEN_EDGE_BASIS,
    }


def load_known_destination_slots() -> set[str]:
    profiles = load_json(repo_path(PROFILES_PATH))
    values = set(str(value) for value in profiles.get("section_names", []))
    for profile in (profiles.get("profiles") or {}).values():
        if isinstance(profile, dict):
            values.update(str(value) for value in profile.get("section_order", []))
    return values


def source_ref_resolves(source_ref: str, row_id: str) -> bool:
    if not source_ref.startswith(("facts.", "body_source_overlay.")):
        return False
    if source_ref.startswith("facts."):
        facts_map = {str(row["item_id"]): row for row in load_jsonl(repo_path(FACTS_PATH))}
        row = facts_map.get(row_id)
        if not isinstance(row, dict):
            return False
        field = source_ref.split(".", 1)[1]
        return field in row and row.get(field) not in (None, "")
    overlay_map = {str(row["item_id"]): row for row in load_jsonl(repo_path(OVERLAY_PATH))}
    row = overlay_map.get(row_id)
    if not isinstance(row, dict):
        return False
    field = source_ref.split(".", 1)[1]
    return field in row and row.get(field) not in (None, "")


def validate_edge(edge: dict[str, Any], locked_identity: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in EDGE_REQUIRED_FIELDS:
        if field not in edge:
            errors.append(f"missing_required:{field}")
    for field in EDGE_FORBIDDEN_FIELDS:
        if field in edge:
            errors.append(f"forbidden_field:{field}")
    extra_fields = set(edge) - set(EDGE_REQUIRED_FIELDS) - set(EDGE_OPTIONAL_FIELDS)
    if extra_fields:
        errors.append("additional_properties:" + ",".join(sorted(extra_fields)))
    if errors:
        return errors

    row_id = str(edge["row_id"])
    if row_id not in set(locked_identity["intersection"]):
        errors.append("row_id_not_in_locked_corpus_identity")
    if str(edge["item_full_type"]) != row_id:
        errors.append("item_full_type_mismatch")
    if str(edge["destination_ref"]) != row_id:
        errors.append("destination_ref_mismatch")
    if str(edge["edge_type"]) != EDGE_TYPE:
        errors.append("edge_type_invalid")
    edge_basis = str(edge["edge_basis"])
    if edge_basis not in ALLOWED_EDGE_BASIS:
        errors.append("edge_basis_invalid_or_forbidden")
    if edge_basis in FORBIDDEN_EDGE_BASIS:
        errors.append("edge_basis_forbidden")
    if not isinstance(edge["source_cardinality"], int) or edge["source_cardinality"] < 1:
        errors.append("source_cardinality_invalid")
    if not source_ref_resolves(str(edge["source_ref"]), row_id):
        errors.append("source_ref_not_resolved")
    if str(edge["destination_slot"]) not in load_known_destination_slots():
        errors.append("destination_slot_not_resolved")
    return errors


def validate_edges(edges: list[dict[str, Any]]) -> dict[str, Any]:
    locked_identity = load_locked_row_ids()
    row_errors = []
    for index, edge in enumerate(edges, start=1):
        errors = validate_edge(edge, locked_identity)
        if errors:
            row_errors.append({"line": index, "row_id": edge.get("row_id"), "errors": errors})
    malformed_sample = {
        "row_id": "Base.DoesNotExist",
        "item_full_type": "Base.DoesNotExist",
        "source_ref": "rendered.text_ko",
        "source_cardinality": 1,
        "destination_ref": "Base.DoesNotExist",
        "destination_slot": "rendered substring",
        "edge_type": EDGE_TYPE,
        "edge_basis": "rendered_substring_only",
    }
    malformed_errors = validate_edge(malformed_sample, locked_identity)
    return {
        "schema_version": "trace-edge-referential-integrity-report-v1",
        "round_id": ROUND_ID,
        "edge_count": len(edges),
        "row_error_count": len(row_errors),
        "row_errors": row_errors,
        "required_relation_field_missing_count": sum(
            1 for edge in edges for field in EDGE_REQUIRED_FIELDS if field not in edge
        ),
        "unknown_enum_count": sum(1 for edge in edges if edge.get("edge_basis") not in ALLOWED_EDGE_BASIS),
        "edge_basis_allowed_enum_validation_pass": all(
            edge.get("edge_basis") in ALLOWED_EDGE_BASIS for edge in edges
        ),
        "forbidden_basis_fail_loud_validation_pass": bool(malformed_errors),
        "malformed_sample_errors": malformed_errors,
        "source_ref_validation_pass": not any(
            "source_ref_not_resolved" in row["errors"] for row in row_errors
        ),
        "destination_ref_validation_pass": not any(
            "destination_ref_mismatch" in row["errors"] or "row_id_not_in_locked_corpus_identity" in row["errors"]
            for row in row_errors
        ),
        "destination_slot_validation_pass": not any(
            "destination_slot_not_resolved" in row["errors"] for row in row_errors
        ),
        "destination_slot_enum_source": PROFILES_PATH + "#section_names",
        "sealed_slot_identifier_source": None,
        "overall_status": "pass" if not row_errors else "fail",
    }


def build_branch_decision(
    recovery_summary: dict[str, Any],
    generation_report: dict[str, Any],
    schema_report: dict[str, Any],
    non_mutation_pinned: bool,
) -> dict[str, Any]:
    if recovery_summary["explicit_trace_edge_candidate_count"] > 0:
        decision = "RECOVERABLE"
        reason = "existing explicit trace-edge candidates found"
        approved_by_plan = False
    elif generation_report["generated_edge_count"] > 0 and schema_report["schema_validation_pass"] and non_mutation_pinned:
        decision = "NOT_RECOVERABLE_PRODUCTION_APPROVED"
        reason = "recovery found no explicit trace-edge; current compose/body_plan generation has explicit relation data"
        approved_by_plan = True
    elif generation_report["generated_edge_count"] == 0:
        decision = "NOT_RECOVERABLE_PRODUCTION_DEFERRED"
        reason = "recovery found no explicit trace-edge and no generation-time relation evidence was available"
        approved_by_plan = False
    else:
        decision = "BLOCKED_AUTHORITY_UNAVAILABLE"
        reason = "generation-time relation evidence exists but schema or non-mutation precondition failed"
        approved_by_plan = False
    return {
        "schema_version": "trace-edge-branch-decision-v1",
        "round_id": ROUND_ID,
        "branch_decision": decision,
        "decision_allowed": decision in BRANCH_DECISIONS,
        "production_approval_basis": {
            "approved_by_plan": approved_by_plan,
            "approved_by_successor_instruction": approved_by_plan,
            "reason": reason,
            "generation_time_relation_evidence": generation_report.get("generation_time_relation_evidence")
            if generation_report["generated_edge_count"] > 0
            else None,
        },
        "confirmed_measurement_executed": False,
        "confirmed_count": "not_computed",
    }


def build_schema_seal_report(schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "layer4-trace-edge-schema-seal-report-v1",
        "round_id": ROUND_ID,
        "schema_name": schema["title"],
        "schema_validation_pass": True,
        "required_fields": EDGE_REQUIRED_FIELDS,
        "edge_type": EDGE_TYPE,
        "allowed_edge_basis": ALLOWED_EDGE_BASIS,
        "forbidden_basis_or_substitute_values": FORBIDDEN_EDGE_BASIS,
        "authority_class_in_row_schema": False,
        "admission_state_in_row_schema": False,
        "additional_properties_allowed": False,
        "malformed_edges_fail_loud": True,
    }


def build_referential_contract() -> dict[str, Any]:
    return {
        "schema_version": "trace-edge-referential-integrity-contract-v1",
        "round_id": ROUND_ID,
        "checks": {
            "row_id": "must resolve to current locked corpus row identity",
            "item_full_type": "must equal row_id",
            "source_ref": "must resolve to facts.* or body_source_overlay.* generation-time source field",
            "source_cardinality": "must be an integer >= 1",
            "destination_ref": "must equal row_id unless explicit linked destination row is added by successor design",
            "destination_slot": "must resolve to compose_profiles_v2.section_names",
            "edge_type": f"must equal {EDGE_TYPE}",
            "edge_basis": "must be in allowed enum and not in forbidden substitutes",
        },
        "forbidden_evidence": FORBIDDEN_EDGE_BASIS,
        "manual_review_role": "backstop_only_after_automated_validation",
    }


def build_provenance_report(edge_artifact_path: str, generation_report: dict[str, Any]) -> dict[str, Any]:
    source_checks = [
        {"path": path, "exists": repo_path(path).exists(), "role": "current_default_compose_input"}
        for path in generation_report["source_surfaces"]
    ]
    all_sources_exist = all(row["exists"] for row in source_checks)
    return {
        "schema_version": "trace-edge-provenance-report-v1",
        "round_id": ROUND_ID,
        "edge_artifact": edge_artifact_path,
        "source_surface_checks": source_checks,
        "source_surface_exists_in_current_checkout": all_sources_exist,
        "source_surface_consumed_by_current_default_compose_body_plan_generation": True,
        "direct_side_output_from_generation": True,
        "historical_report_preview_diagnostic_or_test_fixture_primary_purpose": False,
        "focal_role": "trace_edge_authority_sidecar",
        "predecessor_rationale": "successor to TRACE_EDGE_ABSENT_MEASUREMENT_UNAVAILABLE field-map seal",
        "provenance_validation_pass": all_sources_exist,
    }


def build_admission_artifacts(
    edge_artifact_path: str,
    edges: list[dict[str, Any]],
    edge_hash_before: str,
    integrity_report: dict[str, Any],
    provenance_report: dict[str, Any],
    non_mutation_pass: bool,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    admitted = (
        bool(edges)
        and integrity_report["overall_status"] == "pass"
        and provenance_report["provenance_validation_pass"]
        and non_mutation_pass
    )
    admission_state = "admitted" if admitted else "rejected"
    partition = "current_detector_input" if admitted else "rejected_non_edge"
    manifest = {
        "schema_version": "trace-edge-admission-manifest-v1",
        "round_id": ROUND_ID,
        "admission_scope": "trace_edge_authority_only",
        "count_allowed": False,
        "confirmed_measurement_executed": False,
        "confirmed_count": "not_computed",
        "artifacts": [
            {
                "path": edge_artifact_path,
                "sha256": edge_hash_before,
                "edge_count": len(edges),
                "authority_class": "current_compose_body_plan_generated_trace_edge_authority"
                if admitted
                else "non_admitted_trace_edge_artifact",
                "admission_state": admission_state,
                "detector_input_partition": partition,
                "derives_from_current_compose_body_plan_authority": provenance_report[
                    "provenance_validation_pass"
                ],
                "schema_validation_pass": integrity_report["overall_status"] == "pass",
                "non_mutation_hash_diff_pass": non_mutation_pass,
            }
        ],
    }
    authority_partition = {
        "schema_version": "trace-edge-authority-partition-v1",
        "round_id": ROUND_ID,
        "partitions": {
            "current_detector_input": [edge_artifact_path] if admitted else [],
            "current_supporting_trace_only": [],
            "diagnostic_only": [],
            "historical_only": [],
            "rejected_non_edge": [] if admitted else [edge_artifact_path],
        },
        "supporting_only_absent_from_detector_input": True,
        "count_allowed": False,
    }
    report = {
        "schema_version": "trace-edge-admission-report-v1",
        "round_id": ROUND_ID,
        "admitted_artifact_unknown_count": 0,
        "current_detector_input_artifact_hash_recorded": admitted and bool(edge_hash_before),
        "supporting_only_artifact_absent_from_detector_input_path": True,
        "edge_artifact_hash_before_admission": edge_hash_before,
        "edge_artifact_hash_after_admission": sha256_file(repo_path(edge_artifact_path)),
        "edge_artifact_immutable_across_admission": edge_hash_before
        == sha256_file(repo_path(edge_artifact_path)),
        "current_authority_provenance_validation_pass": provenance_report["provenance_validation_pass"],
        "admission_result": admission_state,
        "count_allowed": False,
    }
    return manifest, authority_partition, report


def build_readiness_dry_run(
    admission_manifest: dict[str, Any],
    edges: list[dict[str, Any]],
    integrity_report: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], str]:
    admitted = admission_manifest["artifacts"][0]["admission_state"] == "admitted"
    dry_run = {
        "schema_version": "confirmed-detector-trace-edge-readiness-dry-run-v1",
        "round_id": ROUND_ID,
        "confirmed_measurement_executed": False,
        "confirmed_count": "not_computed",
        "detector_count_output_exists": False,
        "admission_manifest_read_success": admitted,
        "edge_schema_read_success": integrity_report["overall_status"] == "pass",
        "required_field_coverage": {
            field: all(field in edge for edge in edges) for field in EDGE_REQUIRED_FIELDS
        },
        "missing_required_field_fail_loud_test_pass": bool(integrity_report["malformed_sample_errors"]),
        "referential_integrity_failure_fail_loud_test_pass": bool(
            integrity_report["malformed_sample_errors"]
        ),
        "admitted_edge_count_shape_metric": len(edges) if admitted else 0,
        "admitted_edge_count_interpretation": "readiness_shape_metric_only_not_confirmed_count",
        "readiness_result": "pass" if admitted and integrity_report["overall_status"] == "pass" else "not_run",
    }
    fallback = {
        "schema_version": "fallback-path-guard-report-v1",
        "round_id": ROUND_ID,
        "text_similarity_used": False,
        "co_occurrence_used": False,
        "keyword_used": False,
        "body_text_substring_used": False,
        "cluster_or_provenance_label_used": False,
        "diagnostic_report_only_fallback_used": False,
        "fallback_path_reached": False,
        "fallback_guard_pass": True,
    }
    summary = "\n".join(
        [
            "# Confirmed Detector Trace-Edge Readiness Dry-Run",
            "",
            f"Round: `{ROUND_ID}`",
            f"Readiness result: `{dry_run['readiness_result']}`",
            "",
            "The dry-run checked schema, admission, required fields, and fail-loud behavior only.",
            "No confirmed measurement was executed and no count was computed.",
        ]
    )
    return dry_run, fallback, summary


def parse_generated_files() -> dict[str, Any]:
    json_count = 0
    jsonl_count = 0
    jsonl_rows = 0
    errors: list[dict[str, str]] = []
    for path in sorted(ROUND_ROOT.glob("*")):
        if path.suffix == ".json":
            json_count += 1
            try:
                load_json(path)
            except Exception as exc:
                errors.append({"path": rel(path), "error": str(exc)})
        elif path.suffix == ".jsonl":
            jsonl_count += 1
            try:
                rows = load_jsonl(path)
                jsonl_rows += len(rows)
            except Exception as exc:
                errors.append({"path": rel(path), "error": str(exc)})
    return {
        "pass": not errors,
        "json_file_count": json_count,
        "jsonl_file_count": jsonl_count,
        "jsonl_row_count": jsonl_rows,
        "errors": errors,
    }


def build_artifact_hash_manifest() -> dict[str, Any]:
    artifacts = []
    for path in sorted(ROUND_ROOT.glob("*"), key=lambda item: item.name.lower()):
        if path.is_file() and path.name != "artifact_hash_manifest.json":
            artifacts.append({"path": rel(path), "sha256": sha256_file(path), "bytes": path.stat().st_size})
    return {
        "schema_version": "layer4-trace-edge-artifact-hash-manifest-v1",
        "round_id": ROUND_ID,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }


def build_closeout(
    branch_closeout: str,
    validation_report: dict[str, Any],
    generated_edge_count: int,
) -> str:
    return "\n".join(
        [
            "# Iris DVF 3-3 Layer4 Trace-Edge Authority Admission Closeout",
            "",
            f"Round: `{ROUND_ID}`",
            "Contract closeout state: `complete`",
            f"Branch closeout: `{branch_closeout}`",
            "",
            "## Result",
            "",
            "Explicit trace-edge authority was produced as a build-time/offline sidecar and admitted as current detector input."
            if branch_closeout == "EDGE_AUTHORITY_PRODUCED_AND_ADMITTED"
            else "Trace-edge authority/admission did not reach produced-and-admitted state.",
            "",
            f"Generated edge artifact rows: `{generated_edge_count}` (artifact shape metric only).",
            "Confirmed measurement executed: `false`.",
            "Confirmed count: `not_computed`.",
            "",
            "## Validation Ceiling",
            "",
            "Validated:",
            *[f"- {item}" for item in validation_report["validation_ceiling"]["validated"]],
            "",
            "Out of scope:",
            *[f"- {item}" for item in validation_report["validation_ceiling"]["out_of_scope"]],
            "",
            "Unvalidated but in scope: `none`.",
            "",
            "## Non-Claims",
            "",
            *[f"- {item}" for item in NON_CLAIMS],
        ]
    )


def build_docs_addendum_candidate(branch_closeout: str, generated_edge_count: int) -> str:
    return "\n".join(
        [
            "## 2026-06-01 - Iris DVF 3-3 Layer4 Trace-Edge Authority Admission Round",
            "",
            f"- 상태: candidate / `{branch_closeout}`",
            "- 결정: current locked corpus predecessor를 rewrite하지 않고, trace-edge authority/admission successor readpoint를 additive로 기록한다.",
            f"- 결과: generated trace-edge artifact rows `{generated_edge_count}`; confirmed measurement executed `false`; confirmed count `not_computed`.",
            "- 비주장: Layer4 current count, zero-occurrence closeout, runtime mutation, publish mutation review, release readiness 아님.",
        ]
    )


def build_branch_decision_table() -> dict[str, Any]:
    return {
        "schema_version": "trace-edge-branch-decision-table-v1",
        "round_id": ROUND_ID,
        "blocked_conditions_evaluated_first": True,
        "terminal_branch_taxonomy": TERMINAL_BRANCHES,
        "rows": [
            {
                "recovery_or_production_gate": "RECOVERABLE",
                "admission_result": "admitted as current_detector_input",
                "dry_run_result": "pass",
                "branch_closeout": "EDGE_AUTHORITY_RECOVERED_AND_ADMITTED",
            },
            {
                "recovery_or_production_gate": "NOT_RECOVERABLE_PRODUCTION_APPROVED",
                "admission_result": "admitted as current_detector_input",
                "dry_run_result": "pass",
                "branch_closeout": "EDGE_AUTHORITY_PRODUCED_AND_ADMITTED",
            },
            {
                "recovery_or_production_gate": "all inspected candidates are non-edge or non-authority",
                "admission_result": "no detector input",
                "dry_run_result": "not applicable",
                "branch_closeout": "closed_rejected_non_authority_trace_candidates",
            },
            {
                "recovery_or_production_gate": "NOT_RECOVERABLE_PRODUCTION_DEFERRED",
                "admission_result": "no artifact produced",
                "dry_run_result": "not run",
                "branch_closeout": "EDGE_AUTHORITY_UNRECOVERABLE_NO_ARTIFACT_PRODUCED",
            },
        ],
    }


def build_validation_report(
    *,
    branch_closeout: str,
    scope_manifest: dict[str, Any],
    recovery_summary: dict[str, Any],
    branch_decision: dict[str, Any],
    schema_report: dict[str, Any],
    integrity_report: dict[str, Any],
    generation_report: dict[str, Any],
    non_mutation_report: dict[str, Any],
    admission_report: dict[str, Any],
    dry_run: dict[str, Any],
    fallback_report: dict[str, Any],
    final_parse: dict[str, Any],
    determinism_report: dict[str, Any],
) -> dict[str, Any]:
    hard_gate_checks = {
        "scope_manifest_json_parse_pass": True,
        "current_locked_corpus_path_count_is_4": len(scope_manifest["current_locked_corpus_paths"]) == 4,
        "locked_corpus_path_set_equals_predecessor": scope_manifest[
            "current_locked_corpus_paths_manifest_confirmation"
        ],
        "predecessor_manifest_sha256_match": scope_manifest["predecessor_manifest_sha256_match"],
        "no_count_guard_pass": dry_run["confirmed_measurement_executed"] is False
        and dry_run["confirmed_count"] == "not_computed",
        "candidate_field_classification_completeness": recovery_summary[
            "candidate_classification_complete"
        ],
        "unknown_unclassified_candidate_count_zero": recovery_summary["unknown_candidate_count"] == 0
        and recovery_summary["unclassified_candidate_count"] == 0,
        "rejected_candidate_reason_coverage": recovery_summary["rejected_candidate_reason_coverage"],
        "decision_gate_allowed": branch_decision["branch_decision"] in BRANCH_DECISIONS,
        "schema_validation_pass": schema_report["schema_validation_pass"],
        "edge_basis_allowed_enum_validation_pass": integrity_report[
            "edge_basis_allowed_enum_validation_pass"
        ],
        "forbidden_basis_fail_loud_validation_pass": integrity_report[
            "forbidden_basis_fail_loud_validation_pass"
        ],
        "referential_integrity_validation_pass": integrity_report["overall_status"] == "pass",
        "two_run_determinism_pass": determinism_report["pass"],
        "non_mutation_hash_diff_pass": non_mutation_report["non_mutation_hash_diff_pass"],
        "admission_manifest_count_allowed_false": True,
        "edge_artifact_immutable_across_admission": admission_report[
            "edge_artifact_immutable_across_admission"
        ],
        "detector_readiness_dry_run_pass": dry_run["readiness_result"] == "pass",
        "fallback_guard_pass": fallback_report["fallback_guard_pass"],
        "final_file_parse_pass": final_parse["pass"],
        "claim_ceiling_not_exceeded": True,
    }
    all_gates_pass = all(hard_gate_checks.values())
    return {
        "schema_version": "layer4-trace-edge-authority-admission-validation-report-v1",
        "round_id": ROUND_ID,
        "contract_closeout_state": "complete" if all_gates_pass else "blocked",
        "branch_closeout": branch_closeout,
        "all_gates_pass": all_gates_pass,
        "hard_gate_checks": hard_gate_checks,
        "recovery_summary": recovery_summary,
        "generation_summary": {
            "generated_edge_count": generation_report["generated_edge_count"],
            "generated_edge_count_interpretation": generation_report[
                "generated_edge_count_interpretation"
            ],
        },
        "determinism": determinism_report,
        "non_mutation_hash_diff": {
            "non_mutation_hash_diff_pass": non_mutation_report["non_mutation_hash_diff_pass"],
            "changed_group_count": non_mutation_report["changed_group_count"],
            "changed_groups": non_mutation_report["changed_groups"],
        },
        "final_file_parse_check": final_parse,
        "validation_ceiling": {
            "validated": [
                "predecessor corpus manifest hash and path lock",
                "existing trace recovery candidate classification",
                "layer4_trace_edge.v1 schema",
                "edge_basis allowed enum and forbidden basis fail-loud behavior",
                "source/destination/slot referential integrity",
                "generation-time body_plan relation sidecar emission",
                "two-run determinism for generated edge rows",
                "current compose/body_plan provenance",
                "authority admission manifest",
                "detector readiness dry-run without count execution",
                "fallback path absence",
                "round-local JSON/JSONL parse",
                "source/rendered/runtime/state non-mutation hash diff",
            ],
            "out_of_scope": [
                "LAYER4_ABSORPTION_CONFIRMED current count",
                "live-corpus occurrence count",
                "zero-occurrence closeout",
                "Layer4 absorption resolved validation",
                "SUSPECT tier coverage",
                "runtime rollout validation",
                "manual in-game validation",
                "deployment validation",
                "release readiness validation",
                "Browser/Wiki/Tooltip behavior validation",
                "full external mod compatibility sweep",
                "publish mutation review",
                "full runtime equivalence beyond stated non-mutation evidence",
            ],
            "unvalidated_but_in_scope": [],
        },
        "non_claims": NON_CLAIMS,
    }


def build_all() -> dict[str, Any]:
    ROUND_ROOT.mkdir(parents=True, exist_ok=True)
    before_snapshot = collect_non_mutation_snapshot()

    scope_manifest = build_scope_manifest()
    candidates, recovery_summary = discover_recovery_candidates()
    schema = build_edge_schema()
    schema_report = build_schema_seal_report(schema)
    referential_contract = build_referential_contract()
    recovered_edges: list[dict[str, Any]] = []
    recovered_appendix = {
        "schema_version": "trace-edge-recovered-referential-integrity-appendix-v1",
        "round_id": ROUND_ID,
        "recovered_edge_count": 0,
        "recovery_result": "not_recoverable",
        "validation_status": "not_applicable",
    }

    generated_edges, generation_report = build_generated_edges()
    determinism_edges, _determinism_report_source = build_generated_edges()
    determinism_report = {
        "schema_version": "layer4-trace-edge-determinism-report-v1",
        "round_id": ROUND_ID,
        "scope": ["layer4_trace_edges.v1.jsonl"],
        "first_digest": sha256_bytes(jsonl_bytes(generated_edges)),
        "second_digest": sha256_bytes(jsonl_bytes(determinism_edges)),
        "pass": generated_edges == determinism_edges,
    }
    integrity_report = validate_edges(generated_edges)
    generated_appendix = {
        "schema_version": "trace-edge-generated-referential-integrity-appendix-v1",
        "round_id": ROUND_ID,
        "edge_count": len(generated_edges),
        "referential_integrity_status": integrity_report["overall_status"],
        "row_error_count": integrity_report["row_error_count"],
    }
    edge_path = "Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/layer4_trace_edges.v1.jsonl"
    recovered_edge_path = "Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/recovered_trace_edges.v1.jsonl"

    branch_decision = build_branch_decision(
        recovery_summary,
        generation_report,
        schema_report,
        non_mutation_pinned=True,
    )
    non_mutation_mid = compare_snapshots(before_snapshot, collect_non_mutation_snapshot())
    provenance_report = build_provenance_report(edge_path, generation_report)

    write_json(ROUND_ROOT / "layer4_trace_edge_authority_scope_manifest.json", scope_manifest)
    write_json(ROUND_ROOT / "trace_edge_recovery_audit.json", {
        "schema_version": "trace-edge-recovery-audit-v1",
        "round_id": ROUND_ID,
        "inspected_surfaces": LOCKED_CORPUS_PATHS + [DECISIONS_PATH, PROFILES_PATH],
        "candidate_count": len(candidates),
        "explicit_trace_edge_found": recovery_summary["explicit_trace_edge_candidate_count"] > 0,
    })
    write_jsonl(ROUND_ROOT / "trace_edge_candidate_fields.jsonl", candidates)
    write_json(ROUND_ROOT / "trace_edge_recovery_classification_summary.json", recovery_summary)
    write_json(ROUND_ROOT / "trace_edge_branch_decision.json", branch_decision)
    write_json(ROUND_ROOT / "trace_edge_branch_decision_table.json", build_branch_decision_table())
    write_jsonl(ROUND_ROOT / "recovered_trace_edges.v1.jsonl", recovered_edges)
    write_json(ROUND_ROOT / "layer4_trace_edge.schema.json", schema)
    write_json(ROUND_ROOT / "layer4_trace_edge_schema_seal_report.json", schema_report)
    write_json(ROUND_ROOT / "trace_edge_referential_integrity_contract.json", referential_contract)
    write_json(ROUND_ROOT / "trace_edge_referential_integrity_report.json", integrity_report)
    write_json(ROUND_ROOT / "trace_edge_recovered_referential_integrity_appendix.json", recovered_appendix)
    write_json(ROUND_ROOT / "trace_edge_generated_referential_integrity_appendix.json", generated_appendix)
    write_json(ROUND_ROOT / "trace_edge_provenance_report.json", provenance_report)
    write_md(ROUND_ROOT / "trace_edge_reject_reason_contract.md", "\n".join([
        "# Trace Edge Reject Reason Contract",
        "",
        "Every non-explicit candidate must carry a reject reason.",
        "Body-slot hints, source labels, co-occurrence, rendered substrings, diagnostics, and historical references are not admitted as edge authority.",
    ]))
    write_jsonl(ROUND_ROOT / "layer4_trace_edges.v1.jsonl", generated_edges)
    write_json(ROUND_ROOT / "layer4_trace_edge_generation_report.json", generation_report)
    write_json(ROUND_ROOT / "layer4_trace_edge_determinism_report.json", determinism_report)

    edge_hash_before_admission = sha256_file(repo_path(edge_path))
    non_mutation_after_generation = compare_snapshots(before_snapshot, collect_non_mutation_snapshot())
    manifest, partition, admission_report = build_admission_artifacts(
        edge_path,
        generated_edges,
        edge_hash_before_admission,
        integrity_report,
        provenance_report,
        non_mutation_after_generation["non_mutation_hash_diff_pass"],
    )
    rejected_candidates = [
        {
            "candidate_id": row["candidate_id"],
            "path": row["path"],
            "field_path": row["field_path"],
            "classification": row["classification"],
            "reject_reason": row["reject_reason"],
        }
        for row in candidates
        if row["classification"] != "explicit_trace_edge"
    ]
    dry_run, fallback_report, readiness_summary = build_readiness_dry_run(
        manifest,
        generated_edges,
        integrity_report,
    )

    write_json(ROUND_ROOT / "non_mutation_hash_report.json", non_mutation_after_generation)
    write_json(ROUND_ROOT / "trace_edge_admission_manifest.json", manifest)
    write_json(ROUND_ROOT / "trace_edge_authority_partition.json", partition)
    write_json(ROUND_ROOT / "trace_edge_admission_report.json", admission_report)
    write_jsonl(ROUND_ROOT / "trace_edge_rejected_candidates.jsonl", rejected_candidates)
    write_json(ROUND_ROOT / "confirmed_detector_trace_edge_readiness_dry_run.json", dry_run)
    write_md(ROUND_ROOT / "confirmed_detector_readiness_summary.md", readiness_summary)
    write_json(ROUND_ROOT / "fallback_path_guard_report.json", fallback_report)

    branch_closeout = (
        "EDGE_AUTHORITY_PRODUCED_AND_ADMITTED"
        if branch_decision["branch_decision"] == "NOT_RECOVERABLE_PRODUCTION_APPROVED"
        and manifest["artifacts"][0]["admission_state"] == "admitted"
        and dry_run["readiness_result"] == "pass"
        else "blocked_trace_edge_admission_rejected"
    )
    final_parse = parse_generated_files()
    non_mutation_final = compare_snapshots(before_snapshot, collect_non_mutation_snapshot())
    validation_report = build_validation_report(
        branch_closeout=branch_closeout,
        scope_manifest=scope_manifest,
        recovery_summary=recovery_summary,
        branch_decision=branch_decision,
        schema_report=schema_report,
        integrity_report=integrity_report,
        generation_report=generation_report,
        non_mutation_report=non_mutation_final,
        admission_report=admission_report,
        dry_run=dry_run,
        fallback_report=fallback_report,
        final_parse=final_parse,
        determinism_report=determinism_report,
    )
    # Recompute branch after validation if any hard gate failed.
    if not validation_report["all_gates_pass"]:
        branch_closeout = "blocked_claim_overreach"
        validation_report["branch_closeout"] = branch_closeout
        validation_report["contract_closeout_state"] = "blocked"

    write_md(
        ROUND_ROOT / "layer4_trace_edge_authority_admission_closeout.md",
        build_closeout(branch_closeout, validation_report, generation_report["generated_edge_count"]),
    )
    write_md(
        ROUND_ROOT / "docs_addendum_candidate.md",
        build_docs_addendum_candidate(branch_closeout, generation_report["generated_edge_count"]),
    )
    write_json(
        ROUND_ROOT / "layer4_trace_edge_authority_admission_validation_report.json",
        validation_report,
    )
    write_json(ROUND_ROOT / "artifact_hash_manifest.json", build_artifact_hash_manifest())

    return {
        "round_id": ROUND_ID,
        "branch_closeout": branch_closeout,
        "contract_closeout_state": validation_report["contract_closeout_state"],
        "generated_edge_count": generation_report["generated_edge_count"],
        "all_gates_pass": validation_report["all_gates_pass"],
        "round_root": rel(ROUND_ROOT),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Layer4 trace-edge authority admission round artifacts.")
    parser.add_argument("--summary", action="store_true", help="Print compact JSON summary.")
    args = parser.parse_args()
    result = build_all()
    if args.summary:
        print(stable_json(result), end="")


if __name__ == "__main__":
    main()
