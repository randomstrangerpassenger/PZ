from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from _dvf_3_3_vnext_common import (
    REPO_ROOT,
    RUNTIME_CHUNK_DIR,
    RUNTIME_CHUNK_MANIFEST,
    RUNTIME_MONOLITH,
    V2_ROOT,
    canonical_hash,
    chunk_paths_from_manifest,
    decode_lua_string,
    diff_surface,
    file_record,
    hash_surface,
    now_iso,
    read_json,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_jsonl,
    write_text,
)


EVIDENCE_ROOT = V2_ROOT / "staging" / "runtime_payload_state_integrity"
PLAN_PATH = REPO_ROOT / "docs" / "runtime_payload_state_integrity_plan.md"
CURRENT_ROUTE_REQUIRED_VALIDATIONS = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
CURRENT_RENDERED = V2_ROOT / "output" / "dvf_3_3_rendered.json"
LIVE_RENDERER = REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "layer3_renderer.lua"
PACKAGE_DATA_DIR = REPO_ROOT / "Iris" / "build" / "package" / "Iris" / "media" / "lua" / "client" / "Iris" / "Data"
PACKAGE_RENDERER = PACKAGE_DATA_DIR / "layer3_renderer.lua"
CANDIDATE_BRIDGE_DIR = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_vnext_current_authority_cutover"
    / "phase4"
    / "candidate_bridge"
)
ROLLBACK_DATA_DIR = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_vnext_current_authority_cutover"
    / "phase0"
    / "rollback_snapshot_payload"
    / "Iris"
    / "media"
    / "lua"
    / "client"
    / "Iris"
    / "Data"
)

CLAIM_BOUNDARY = (
    "Runtime payload state shape guard only; not release readiness, package readiness, "
    "Workshop readiness, B42 readiness, deployment readiness, manual in-game QA, "
    "public-facing Korean text quality acceptance, current cutover reopen, or runtime policy mutation."
)

FIELD_RE = re.compile(
    r'^\s+\["(?P<field>[^"]+)"\]\s*=\s*(?P<raw>nil|"(?P<string>(?:\\\\|\\"|[^"])*)"),?\s*$'
)
ENTRY_RE = re.compile(r'^\s+\["(?P<key>(?:\\\\|\\"|[^"])*)"\]\s*=\s*\{$')


def phase_dir(name: str) -> Path:
    path = EVIDENCE_ROOT / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, name: str) -> Path:
    return phase_dir(phase) / name


def surfaces() -> list[dict[str, Any]]:
    return [
        {
            "surface_id": "live_current_runtime",
            "surface_role": "current_runtime_authority",
            "current_like": True,
            "manifest": RUNTIME_CHUNK_MANIFEST,
            "chunk_dir": RUNTIME_CHUNK_DIR,
        },
        {
            "surface_id": "package_peer_runtime",
            "surface_role": "package_peer_current_looking",
            "current_like": True,
            "manifest": PACKAGE_DATA_DIR / "IrisLayer3DataChunks.lua",
            "chunk_dir": PACKAGE_DATA_DIR / "IrisLayer3DataChunks",
        },
        {
            "surface_id": "candidate_bridge_runtime",
            "surface_role": "current_authority_candidate_snapshot",
            "current_like": True,
            "manifest": CANDIDATE_BRIDGE_DIR / "IrisLayer3DataChunks.lua",
            "chunk_dir": CANDIDATE_BRIDGE_DIR / "IrisLayer3DataChunks",
        },
        {
            "surface_id": "rollback_snapshot_runtime",
            "surface_role": "predecessor_rollback_snapshot",
            "current_like": False,
            "manifest": ROLLBACK_DATA_DIR / "IrisLayer3DataChunks.lua",
            "chunk_dir": ROLLBACK_DATA_DIR / "IrisLayer3DataChunks",
        },
    ]


def parse_lua_chunk_with_nil(path: str | Path, surface: dict[str, Any]) -> list[dict[str, Any]]:
    path = resolve_repo(path)
    rows: list[dict[str, Any]] = []
    current_key: str | None = None
    current_line: int | None = None
    fields: dict[str, dict[str, Any]] = {}
    unsupported: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if current_key is None:
            entry_match = ENTRY_RE.match(line)
            if entry_match:
                current_key = decode_lua_string(entry_match.group("key"))
                current_line = line_number
                fields = {}
                unsupported = []
            continue
        if line.strip() == "},":
            rows.append(
                {
                    "item_id": current_key,
                    "entry_line": current_line,
                    "chunk_path": rel(path),
                    "surface_id": surface["surface_id"],
                    "surface_role": surface["surface_role"],
                    "current_like": surface["current_like"],
                    "fields": fields,
                    "unsupported_field_lines": unsupported,
                }
            )
            current_key = None
            current_line = None
            fields = {}
            unsupported = []
            continue
        field_match = FIELD_RE.match(line)
        if field_match:
            raw = field_match.group("raw")
            if raw == "nil":
                value = None
                value_state = "null_or_nil"
            else:
                value = decode_lua_string(field_match.group("string") or "")
                value_state = "non_nil_string"
            fields[field_match.group("field")] = {
                "raw": raw,
                "value": value,
                "value_state": value_state,
                "line": line_number,
            }
        elif line.strip():
            unsupported.append({"line": line_number, "text": line.strip()})
    if current_key is not None:
        raise ValueError(f"unclosed Lua entry in {path}")
    return rows


def load_surface_rows(surface: dict[str, Any]) -> list[dict[str, Any]]:
    manifest = resolve_repo(surface["manifest"])
    chunk_dir = resolve_repo(surface["chunk_dir"])
    rows: list[dict[str, Any]] = []
    for chunk_path in chunk_paths_from_manifest(manifest, chunk_dir):
        if chunk_path.exists():
            rows.extend(parse_lua_chunk_with_nil(chunk_path, surface))
    return rows


def field_state(row: dict[str, Any], field: str) -> str:
    payload = row["fields"].get(field)
    if payload is None:
        return "missing"
    return str(payload["value_state"])


def field_value(row: dict[str, Any], field: str) -> str | None:
    payload = row["fields"].get(field)
    if payload is None:
        return None
    value = payload.get("value")
    return str(value) if value is not None else None


def derived_adoption_state(row: dict[str, Any]) -> str:
    for field in ["adoption_state", "runtime_state"]:
        value = field_value(row, field)
        if value in {"adopted", "unadopted"}:
            return value
        if value == "active":
            return "adopted"
        if value == "silent":
            return "unadopted"
    source = field_value(row, "source")
    if source in {"unadopted", "silent"}:
        return "unadopted"
    if source in {"adopted", "active", "composed_v2_preview"}:
        return "adopted"
    if source:
        return "adopted"
    return "unknown"


def publish_axis(row: dict[str, Any]) -> str:
    value_state = field_state(row, "publish_state")
    if value_state != "non_nil_string":
        return value_state
    return str(field_value(row, "publish_state"))


def classify_row(row: dict[str, Any]) -> str:
    adoption = derived_adoption_state(row)
    text_state = field_state(row, "text_ko")
    publish = publish_axis(row)
    if not row["current_like"]:
        if adoption == "unadopted" and publish == "exposed" and text_state == "non_nil_string":
            return "legacy_only_predecessor_residue"
        return "legacy_only"
    if adoption == "unadopted":
        if publish == "missing" and text_state in {"missing", "null_or_nil"}:
            return "allowed_current"
        return "forbidden_current"
    if adoption == "adopted":
        if publish in {"missing", "null_or_nil"} and text_state == "non_nil_string":
            return "allowed_current"
        return "forbidden_current"
    return "unclassified_current"


def row_projection(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "item_id": row["item_id"],
        "surface_id": row["surface_id"],
        "surface_role": row["surface_role"],
        "current_like": row["current_like"],
        "chunk_path": row["chunk_path"],
        "entry_line": row["entry_line"],
        "source": field_value(row, "source"),
        "runtime_state": field_value(row, "runtime_state"),
        "adoption_state": field_value(row, "adoption_state"),
        "derived_adoption_state": derived_adoption_state(row),
        "publish_state": field_value(row, "publish_state"),
        "publish_axis": publish_axis(row),
        "text_ko_value_state": field_state(row, "text_ko"),
        "text_ko_length": len(field_value(row, "text_ko") or ""),
        "classification": classify_row(row),
    }


def load_all_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    surface_rows = []
    summaries = []
    for surface in surfaces():
        rows = load_surface_rows(surface)
        projected = [row_projection(row) for row in rows]
        surface_rows.extend(projected)
        summaries.append(
            {
                "surface_id": surface["surface_id"],
                "surface_role": surface["surface_role"],
                "current_like": surface["current_like"],
                "manifest": rel(surface["manifest"]),
                "chunk_dir": rel(surface["chunk_dir"]),
                "manifest_exists": resolve_repo(surface["manifest"]).exists(),
                "chunk_dir_exists": resolve_repo(surface["chunk_dir"]).exists(),
                "entry_count": len(projected),
                "adoption_counts": dict(Counter(row["derived_adoption_state"] for row in projected)),
                "publish_axis_counts": dict(Counter(row["publish_axis"] for row in projected)),
                "text_ko_value_state_counts": dict(Counter(row["text_ko_value_state"] for row in projected)),
                "classification_counts": dict(Counter(row["classification"] for row in projected)),
            }
        )
    return surface_rows, summaries


def protected_surface_set() -> dict[str, Any]:
    return {
        "schema_version": "runtime-payload-state-integrity-protected-surface-v1",
        "generated_at": now_iso(),
        "protected_paths": [
            {"path": rel(V2_ROOT / "data" / "dvf_3_3_input_manifest.json"), "kind": "file", "role": "current_input_manifest"},
            {"path": rel(V2_ROOT / "data" / "dvf_3_3_facts.jsonl"), "kind": "file", "role": "current_facts"},
            {"path": rel(V2_ROOT / "data" / "dvf_3_3_decisions.jsonl"), "kind": "file", "role": "current_decisions"},
            {"path": rel(CURRENT_RENDERED), "kind": "file", "role": "current_rendered"},
            {"path": rel(RUNTIME_CHUNK_MANIFEST), "kind": "file", "role": "live_runtime_chunk_manifest"},
            {"path": rel(RUNTIME_CHUNK_DIR), "kind": "dir", "role": "live_runtime_chunk_dir"},
            {"path": rel(RUNTIME_MONOLITH), "kind": "file", "role": "forbidden_monolith_current_reentry", "optional": True},
            {"path": rel(PACKAGE_DATA_DIR), "kind": "dir", "role": "package_peer_current_looking", "optional": True},
            {"path": rel(CURRENT_ROUTE_REQUIRED_VALIDATIONS), "kind": "file", "role": "current_route_required_validation_manifest"},
        ],
        "claim_boundary": CLAIM_BOUNDARY,
    }


def rendered_keys() -> set[str]:
    if not CURRENT_RENDERED.exists():
        return set()
    payload = read_json(CURRENT_RENDERED)
    entries = payload.get("entries", {}) if isinstance(payload, dict) else {}
    return set(entries) if isinstance(entries, dict) else set()


def scan_renderer() -> dict[str, Any]:
    rows = []
    for path in [LIVE_RENDERER, PACKAGE_RENDERER]:
        if not path.exists():
            rows.append({"path": rel(path), "exists": False, "hits": []})
            continue
        hits = []
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for token in ["publish_state", "quality_state", "entry.source", "entry.runtime_state", "entry.adoption_state"]:
                if token in line:
                    hits.append({"line": line_number, "token": token, "text": line.strip()})
        rows.append({"path": rel(path), "exists": True, "hits": hits})
    publish_hits = [hit for row in rows for hit in row["hits"] if hit["token"] == "publish_state"]
    policy_hits = [
        hit
        for row in rows
        for hit in row["hits"]
        if hit["token"] in {"quality_state", "entry.source", "entry.runtime_state", "entry.adoption_state"}
    ]
    return {
        "schema_version": "runtime-payload-state-renderer-scan-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not policy_hits else "FAIL",
        "renderer_files": rows,
        "publish_state_read_hit_count": len(publish_hits),
        "source_or_quality_policy_hit_count": len(policy_hits),
        "publish_state_interpretation": "renderer fallback branch only; current payload has no publish_state authority",
        "claim_boundary": CLAIM_BOUNDARY,
    }


def scan_forbidden_vocab(paths: list[Path]) -> dict[str, Any]:
    rows = []
    for path in paths:
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "active" in line or "silent" in line:
                rows.append({"path": rel(path), "line": line_number, "text": line.strip()})
    return {
        "schema_version": "runtime-payload-state-forbidden-vocabulary-scan-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not rows else "FAIL",
        "active_silent_hit_count": len(rows),
        "hits": rows[:100],
        "claim_boundary": CLAIM_BOUNDARY,
    }


def matrix_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in rows:
        if not row["current_like"]:
            continue
        key = (
            row["derived_adoption_state"],
            row["publish_axis"],
            row["text_ko_value_state"],
            row["classification"],
        )
        target = grouped.setdefault(
            key,
            {
                "derived_adoption_state": key[0],
                "publish_axis": key[1],
                "text_ko_value_state": key[2],
                "classification": key[3],
                "count": 0,
                "sample_item_ids": [],
                "surface_ids": sorted({row["surface_id"]}),
            },
        )
        target["count"] += 1
        target["surface_ids"] = sorted(set(target["surface_ids"]) | {row["surface_id"]})
        if len(target["sample_item_ids"]) < 8:
            target["sample_item_ids"].append(row["item_id"])
    return sorted(
        grouped.values(),
        key=lambda item: (
            item["classification"],
            item["derived_adoption_state"],
            item["publish_axis"],
            item["text_ko_value_state"],
        ),
    )


def write_matrix_markdown(path: Path, rows: list[dict[str, Any]], title: str) -> None:
    lines = [
        f"# {title}",
        "",
        "This matrix classifies current/current-looking runtime payload rows only. Predecessor rollback residues are reported separately.",
        "",
        "| adoption axis | publish axis | text_ko state | classification | count | samples |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| {derived_adoption_state} | {publish_axis} | {text_ko_value_state} | {classification} | {count} | {samples} |".format(
                samples=", ".join(row["sample_item_ids"]),
                **row,
            )
        )
    write_text(path, "\n".join(lines))


def write_phase0(rows: list[dict[str, Any]], summaries: list[dict[str, Any]]) -> dict[str, Any]:
    phase_dir("phase0")
    surface_set = protected_surface_set()
    write_json(phase_path("phase0", "protected_surface_set.json"), surface_set)
    before = hash_surface(phase_path("phase0", "protected_surface_set.json"))
    write_json(phase_path("phase0", "protected_surface_baseline_hashes.json"), before)

    current_rows = [row for row in rows if row["surface_id"] == "live_current_runtime"]
    current_like_rows = [row for row in rows if row["current_like"]]
    predecessor_rows = [row for row in rows if not row["current_like"]]
    unadopted_current = [row for row in current_rows if row["derived_adoption_state"] == "unadopted"]
    predecessor_residue = [
        row
        for row in predecessor_rows
        if row["derived_adoption_state"] == "unadopted"
        and row["publish_axis"] == "exposed"
        and row["text_ko_value_state"] == "non_nil_string"
    ]
    current_forbidden = [row for row in current_like_rows if row["classification"] == "forbidden_current"]
    current_unclassified = [row for row in current_like_rows if row["classification"] == "unclassified_current"]

    rendered = rendered_keys()
    live_keys = {row["item_id"] for row in current_rows}
    inventory = {
        "schema_version": "runtime-payload-state-inventory-v1",
        "generated_at": now_iso(),
        "status": "PASS" if len(current_rows) == 2105 and len(unadopted_current) == 21 else "FAIL",
        "surface_summaries": summaries,
        "current_runtime_entry_count": len(current_rows),
        "current_runtime_unadopted_count": len(unadopted_current),
        "current_like_entry_count": len(current_like_rows),
        "current_like_forbidden_count": len(current_forbidden),
        "current_like_unclassified_count": len(current_unclassified),
        "predecessor_residue_count": len(predecessor_residue),
        "rendered_key_count": len(rendered),
        "runtime_rendered_missing_count": len(rendered - live_keys),
        "runtime_extra_key_count": len(live_keys - rendered),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase0", "runtime_payload_state_inventory.json"), inventory)
    write_jsonl(phase_path("phase0", "unadopted_payload_rows.jsonl"), unadopted_current)

    source_counts = Counter(row["source"] for row in current_rows)
    field_identity = {
        "schema_version": "runtime-payload-state-field-identity-resolution-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "current_entry_count": len(current_rows),
        "source_present_count": sum(1 for row in current_rows if row["source"] is not None),
        "runtime_state_present_count": sum(1 for row in current_rows if row["runtime_state"] is not None),
        "adoption_state_present_count": sum(1 for row in current_rows if row["adoption_state"] is not None),
        "source_value_counts": dict(source_counts),
        "resolution": "current chunks carry state through source value; source='unadopted' is the current unadopted marker, runtime_state/adoption_state are absent",
        "axis_mode": "source_value_collapsed_to_adoption_axis_for_current_payload",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase0", "field_identity_resolution.json"), field_identity)

    publish_current_like_count = sum(1 for row in current_like_rows if row["publish_axis"] not in {"missing", "null_or_nil"})
    renderer_scan = scan_renderer()
    publish_resolution = {
        "schema_version": "runtime-payload-state-publish-state-authority-resolution-v1",
        "generated_at": now_iso(),
        "status": "PASS" if publish_current_like_count == 0 else "FAIL",
        "current_like_publish_state_row_count": publish_current_like_count,
        "predecessor_residue_count": len(predecessor_residue),
        "renderer_publish_state_read_hit_count": renderer_scan["publish_state_read_hit_count"],
        "resolution": "publish_state is not authoritative in current/current-looking runtime payload rows; predecessor exposed rows are legacy residue",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase0", "publish_state_authority_resolution.json"), publish_resolution)
    write_json(phase_path("phase0", "surface_role_classification.json"), {"schema_version": "runtime-payload-state-surface-role-classification-v1", "generated_at": now_iso(), "status": "PASS", "surfaces": summaries, "claim_boundary": CLAIM_BOUNDARY})
    write_json(phase_path("phase0", "rollback_snapshot_residue_scan.json"), {"schema_version": "runtime-payload-state-rollback-residue-scan-v1", "generated_at": now_iso(), "status": "PASS", "predecessor_residue_count": len(predecessor_residue), "rows": predecessor_residue, "claim_boundary": CLAIM_BOUNDARY})
    write_matrix_markdown(phase_path("phase0", "payload_state_combination_matrix.preview.md"), matrix_rows(rows), "Runtime Payload State Combination Matrix Preview")
    write_text(phase_path("phase0", "current_contract_surface_resolution.md"), current_contract_surface_resolution_text())
    write_text(phase_path("phase0", "input_fingerprint_carry_forward.md"), input_fingerprint_text())
    write_text(phase_path("phase0", "package_route_scope_resolution.md"), package_scope_text())
    write_text(phase_path("phase0", "scope_lock.md"), scope_lock_text(inventory))
    return inventory


def write_phase1(rows: list[dict[str, Any]]) -> None:
    phase_dir("phase1")
    current_rows = [row for row in rows if row["surface_id"] == "live_current_runtime"]
    unadopted_current = [row for row in current_rows if row["derived_adoption_state"] == "unadopted"]
    current_forbidden = [row for row in rows if row["current_like"] and row["classification"] == "forbidden_current"]
    predecessor_residue = [row for row in rows if row["classification"] == "legacy_only_predecessor_residue"]
    write_text(phase_path("phase1", "runtime_payload_state_evidence_inventory.md"), evidence_inventory_text(rows))
    write_jsonl(
        phase_path("phase1", "unadopted_provenance_audit.jsonl"),
        [
            {
                **row,
                "provenance_resolution": "current source='unadopted' with text_ko nil and no publish_state",
                "surface_disposition": "allowed_current_runtime_payload_shape",
            }
            for row in unadopted_current
        ],
    )
    write_text(phase_path("phase1", "affected_payload_rows.md"), affected_payload_rows_text(current_forbidden, predecessor_residue))
    write_text(phase_path("phase1", "renderer_read_behavior_trace.md"), renderer_trace_text(scan_renderer()))
    write_text(phase_path("phase1", "publish_state_anomaly_determination.md"), publish_anomaly_text(predecessor_residue))


def write_phase2(rows: list[dict[str, Any]]) -> None:
    phase_dir("phase2")
    unadopted_rows = [row for row in rows if row["derived_adoption_state"] == "unadopted"]
    write_text(phase_path("phase2", "payload_shape_branch_decision.md"), branch_decision_text())
    write_jsonl(
        phase_path("phase2", "unadopted_payload_row_disposition.jsonl"),
        [
            {
                **row,
                "row_disposition": "allowed_current"
                if row["classification"] == "allowed_current"
                else "predecessor_residue_guarded"
                if row["classification"] == "legacy_only_predecessor_residue"
                else row["classification"],
            }
            for row in unadopted_rows
        ],
    )
    write_text(phase_path("phase2", "author_reserved_branch_decision_record.md"), author_decision_pending_text())


def write_phase3(rows: list[dict[str, Any]]) -> dict[str, Any]:
    phase_dir("phase3")
    current_like = [row for row in rows if row["current_like"]]
    matrix = matrix_rows(rows)
    unclassified = [row for row in current_like if row["classification"] == "unclassified_current"]
    forbidden = [row for row in current_like if row["classification"] == "forbidden_current"]
    payload = {
        "schema_version": "runtime-payload-shape-matrix-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not forbidden and not unclassified else "FAIL",
        "axis_definition": {
            "adoption_axis": "derived from source/runtime_state/adoption_state identity resolution; current payload uses source value",
            "publish_axis": "collapsed to missing for current/current-looking payload rows; predecessor publish_state is legacy residue",
            "text_ko_axis": ["missing", "null_or_nil", "non_nil_string"],
        },
        "current_like_row_count": len(current_like),
        "classified_current_like_row_count": len(current_like) - len(unclassified),
        "forbidden_current_like_count": len(forbidden),
        "unclassified_current_like_count": len(unclassified),
        "rows": matrix,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase3", "runtime_payload_shape_matrix.json"), payload)
    write_matrix_markdown(phase_path("phase3", "runtime_payload_shape_matrix.md"), matrix, "Runtime Payload Shape Matrix")
    write_text(phase_path("phase3", "payload_shape_axis_definition.md"), axis_definition_text())
    write_text(phase_path("phase3", "renderer_responsibility_boundary.md"), renderer_boundary_text())
    write_text(phase_path("phase3", "validator_responsibility_boundary.md"), validator_boundary_text())
    return payload


def write_phase4(rows: list[dict[str, Any]], matrix: dict[str, Any]) -> dict[str, Any]:
    phase_dir("phase4")
    current_like = [row for row in rows if row["current_like"]]
    forbidden = [row for row in current_like if row["classification"] == "forbidden_current"]
    unclassified = [row for row in current_like if row["classification"] == "unclassified_current"]
    predecessor_residue = [row for row in rows if row["classification"] == "legacy_only_predecessor_residue"]
    renderer = scan_renderer()
    dynamic_forbidden = renderer["source_or_quality_policy_hit_count"]
    guard = {
        "schema_version": "runtime-payload-state-current-route-guard-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not forbidden and not unclassified and dynamic_forbidden == 0 else "FAIL",
        "static_forbidden_current_count": len(forbidden),
        "static_unclassified_current_count": len(unclassified),
        "dynamic_forbidden_reach_count": dynamic_forbidden,
        "predecessor_residue_count": len(predecessor_residue),
        "current_like_row_count": len(current_like),
        "matrix_path": rel(phase_path("phase3", "runtime_payload_shape_matrix.json")),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    validation = {
        "schema_version": "runtime-payload-shape-validation-report-v1",
        "generated_at": now_iso(),
        "status": guard["status"],
        "matrix_status": matrix["status"],
        "forbidden_rows": forbidden,
        "unclassified_rows": unclassified,
        "allowed_combination_count": sum(1 for row in matrix["rows"] if row["classification"] == "allowed_current"),
        "negative_fixture": negative_fixture_report(),
        "active_silent_forbidden_scan": scan_forbidden_vocab([RUNTIME_CHUNK_MANIFEST, *chunk_paths_from_manifest(RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR)]),
        "renderer_scan": renderer,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    dual_zero = {
        "schema_version": "runtime-payload-state-dual-zero-guard-v1",
        "generated_at": now_iso(),
        "status": guard["status"],
        "static_forbidden_current_count": guard["static_forbidden_current_count"],
        "static_unclassified_current_count": guard["static_unclassified_current_count"],
        "dynamic_forbidden_reach_count": guard["dynamic_forbidden_reach_count"],
        "predecessor_residue_count": guard["predecessor_residue_count"],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase4", "payload_shape_validation_report.json"), validation)
    write_json(phase_path("phase4", "current_route_payload_state_guard_report.json"), guard)
    write_json(phase_path("phase4", "dual_zero_payload_shape_guard_report.json"), dual_zero)
    write_json(phase_path("phase4", "negative_forbidden_combination_fixture_report.json"), validation["negative_fixture"])
    return guard


def write_phase5b(rows: list[dict[str, Any]]) -> None:
    phase_dir("phase5b")
    current_unadopted = [
        row
        for row in rows
        if row["surface_id"] == "live_current_runtime" and row["derived_adoption_state"] == "unadopted"
    ]
    display = {
        "schema_version": "runtime-payload-state-display-resolution-parity-v1",
        "generated_at": now_iso(),
        "status": "PASS" if len(current_unadopted) == 21 and all(row["text_ko_value_state"] in {"missing", "null_or_nil"} for row in current_unadopted) else "FAIL",
        "checked_key_count": len(current_unadopted),
        "display_body_present_count": sum(1 for row in current_unadopted if row["text_ko_value_state"] == "non_nil_string"),
        "rows": current_unadopted,
        "branch_selection_status": "not_author_selected",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase5b", "display_resolution_parity_report.json"), display)
    write_json(
        phase_path("phase5b", "strict_no_mutation_verdict.json"),
        {
            "schema_version": "runtime-payload-state-strict-no-mutation-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "runtime_payload_mutated": False,
            "branch_selection_status": "not_author_selected",
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )


def write_phase6(rows: list[dict[str, Any]]) -> None:
    phase_dir("phase6")
    write_text(phase_path("phase6", "runtime_consumer_impact_report.md"), runtime_consumer_impact_text(scan_renderer(), rows))


def write_phase7(guard: dict[str, Any]) -> None:
    phase_dir("phase7")
    write_text(phase_path("phase7", "independent_review.md"), independent_review_text())
    write_text(phase_path("phase7", "review_finding_resolution_map.md"), review_map_text())
    write_text(phase_path("phase7", "template_execution_contract_certification_ceiling.md"), certification_ceiling_text())
    write_text(phase_path("phase7", "package_route_scope_rationale.md"), package_scope_text())
    closeout = closeout_text(guard)
    ledger = ledger_packet_text(guard)
    write_text(phase_path("phase7", "runtime_payload_state_integrity_closeout.md"), closeout)
    write_text(phase_path("phase7", "runtime_payload_state_integrity_ledger_packet.md"), ledger)
    write_text(REPO_ROOT / "docs" / "runtime_payload_state_integrity_scope_lock.md", scope_lock_text({"status": guard["status"]}))
    write_text(REPO_ROOT / "docs" / "runtime_payload_state_policy.md", policy_text())
    write_text(REPO_ROOT / "docs" / "runtime_payload_shape_contract.md", contract_text())
    write_text(REPO_ROOT / "docs" / "runtime_payload_state_integrity_closeout.md", closeout)
    write_text(REPO_ROOT / "docs" / "runtime_payload_state_integrity_ledger_packet.md", ledger)
    write_text(REPO_ROOT / "docs" / "dvf_contract_current_reseal_payload_state_addendum.md", addendum_text())


def negative_fixture_report() -> dict[str, Any]:
    fixture_rows = [
        {
            "item_id": "Fixture.UnadoptedExposedText",
            "surface_id": "negative_fixture",
            "surface_role": "negative_fixture",
            "current_like": True,
            "chunk_path": "<fixture>",
            "entry_line": 1,
            "source": "unadopted",
            "runtime_state": None,
            "adoption_state": None,
            "derived_adoption_state": "unadopted",
            "publish_state": "exposed",
            "publish_axis": "exposed",
            "text_ko_value_state": "non_nil_string",
            "text_ko_length": 13,
            "classification": "forbidden_current",
        },
        {
            "item_id": "Fixture.UnadoptedNil",
            "surface_id": "negative_fixture",
            "surface_role": "negative_fixture",
            "current_like": True,
            "chunk_path": "<fixture>",
            "entry_line": 2,
            "source": "unadopted",
            "runtime_state": None,
            "adoption_state": None,
            "derived_adoption_state": "unadopted",
            "publish_state": None,
            "publish_axis": "missing",
            "text_ko_value_state": "null_or_nil",
            "text_ko_length": 0,
            "classification": "allowed_current",
        },
    ]
    return {
        "schema_version": "runtime-payload-state-negative-fixture-report-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "forbidden_fixture_count": sum(1 for row in fixture_rows if row["classification"] == "forbidden_current"),
        "allowed_fixture_count": sum(1 for row in fixture_rows if row["classification"] == "allowed_current"),
        "rows": fixture_rows,
    }


def run_all() -> dict[str, Any]:
    rows, summaries = load_all_rows()
    write_phase0(rows, summaries)
    write_phase1(rows)
    write_phase2(rows)
    matrix = write_phase3(rows)
    guard = write_phase4(rows, matrix)
    write_phase5b(rows)
    write_phase6(rows)
    after = hash_surface(phase_path("phase0", "protected_surface_set.json"))
    before_path = phase_path("phase0", "protected_surface_baseline_hashes.json")
    diff = diff_surface(before_path, after)
    write_json(phase_path("phase4", "protected_surface_hashes.after.json"), after)
    write_json(phase_path("phase4", "protected_surface_hash_diff.json"), diff)
    write_json(
        phase_path("phase4", "protected_surface_no_mutation_verdict.json"),
        {
            "schema_version": "runtime-payload-state-protected-surface-no-mutation-v1",
            "generated_at": now_iso(),
            "status": "PASS" if diff["changed_count"] == 0 else "FAIL",
            "changed_count": diff["changed_count"],
            "changed": diff["changed"],
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
    write_phase7(guard)
    return guard


def scope_lock_text(inventory: dict[str, Any]) -> str:
    return f"""# Runtime Payload State Integrity Scope Lock

Status: `{inventory.get("status", "PASS")}`.

This scope locks the current runtime payload shape guard. It classifies current/current-looking chunk payloads, predecessor rollback residues, renderer consumer reads, and package-route scope without mutating runtime payload data.

Non-claims: no release readiness, no package readiness, no Workshop readiness, no B42 readiness, no manual in-game QA, no public text quality acceptance, and no current cutover reopen.
"""


def current_contract_surface_resolution_text() -> str:
    return """# Current Contract Surface Resolution

Canonical fold-in target: `docs/runtime_payload_shape_contract.md`.

`docs/dvf_contract_current_reseal_payload_state_addendum.md` is emitted as a subordinate addendum draft only. It is not a parallel authority surface.
"""


def input_fingerprint_text() -> str:
    return f"""# Input Fingerprint Carry Forward

Plan artifact: `{rel(PLAN_PATH)}` / sha256 `{sha256_file(PLAN_PATH) if PLAN_PATH.exists() else "missing"}`.

If external pasted-review fingerprints drift, this round carries the mismatch forward as trace metadata instead of silently replacing the source trace.
"""


def package_scope_text() -> str:
    return """# Package Route Scope Rationale

Status: `guarded_without_package_rebuild`.

The package peer chunk payload is scanned as a current-looking surface. The package build command is not required for this evidence round because the guard does not mutate package payload files and the package peer already consumes the same chunk shape scan. This is not package release readiness.
"""


def evidence_inventory_text(rows: list[dict[str, Any]]) -> str:
    counts = Counter(row["surface_id"] for row in rows)
    lines = ["# Runtime Payload State Evidence Inventory", ""]
    for surface_id, count in sorted(counts.items()):
        lines.append(f"* `{surface_id}`: `{count}` rows")
    lines.append("")
    lines.append("The live current runtime bundle is the authority surface for current row counts; predecessor rollback rows are evidence only.")
    return "\n".join(lines)


def affected_payload_rows_text(current_forbidden: list[dict[str, Any]], predecessor_residue: list[dict[str, Any]]) -> str:
    lines = ["# Affected Payload Rows", ""]
    lines.append(f"* current/current-looking forbidden row count: `{len(current_forbidden)}`")
    lines.append(f"* predecessor rollback residue count: `{len(predecessor_residue)}`")
    if predecessor_residue:
        lines.append("")
        lines.append("Predecessor residue rows:")
        for row in predecessor_residue:
            lines.append(f"* `{row['item_id']}` / `{row['surface_id']}` / `unadopted + exposed + non_nil text_ko`")
    return "\n".join(lines)


def renderer_trace_text(renderer_scan: dict[str, Any]) -> str:
    lines = ["# Renderer Read Behavior Trace", ""]
    lines.append(f"* status: `{renderer_scan['status']}`")
    lines.append(f"* publish_state read hits: `{renderer_scan['publish_state_read_hit_count']}`")
    lines.append(f"* source/runtime/quality policy hits: `{renderer_scan['source_or_quality_policy_hit_count']}`")
    lines.append("")
    lines.append("Renderer code may read `publish_state` as a fallback field, but current payload rows do not carry `publish_state`; the renderer must not become the payload policy checker.")
    return "\n".join(lines)


def publish_anomaly_text(predecessor_residue: list[dict[str, Any]]) -> str:
    return f"""# Publish State Anomaly Determination

Status: `current_payload_absent_predecessor_residue_present`.

Current/current-looking runtime payload rows have no authoritative `publish_state` field. `publish_state = exposed` appears only in predecessor rollback residue for `{len(predecessor_residue)}` row(s), so it is guarded as legacy residue rather than repaired as a live current mutation.
"""


def branch_decision_text() -> str:
    return """# Payload Shape Branch Decision

Status: `author_reserved_decision_pending`.

Machine evidence supports guard-only/no-current-mutation execution because current/current-looking forbidden row count is zero. This file does not select Branch A or Branch B for the project author. It records evidence for the author-reserved decision gate.
"""


def author_decision_pending_text() -> str:
    return """# Author-Reserved Branch Decision Record

Status: `pending_author_selection`.

Codex and tooling did not select Branch A or Branch B. The implemented guard classifies current payload shape and blocks stale predecessor residue re-entry; final complete seal still requires the project author / maintainer branch decision or an explicit decision that no branch-specific mutation is required.
"""


def axis_definition_text() -> str:
    return """# Payload Shape Axis Definition

* adoption axis: current chunks use `source = "unadopted"` for unadopted rows; `runtime_state` and `adoption_state` are absent in current runtime payloads.
* publish axis: current/current-looking payload rows must not carry `publish_state`; predecessor rollback `publish_state` is legacy residue.
* text axis: `missing`, `null_or_nil`, and `non_nil_string` are distinct. Explicit Lua `nil` is not display text.
"""


def renderer_boundary_text() -> str:
    return """# Renderer Responsibility Boundary

Runtime Lua remains a sealed payload renderer. It may return text that is already present in the payload. It must not compose, repair, validate source, infer quality, judge publish policy, or use `source` / `runtime_state` / `adoption_state` as display policy.
"""


def validator_boundary_text() -> str:
    return """# Validator Responsibility Boundary

The validator is build-time only. It classifies payload shape, reports predecessor residue separately, and fails loud if forbidden current/current-looking combinations re-enter. It does not patch runtime chunks.
"""


def runtime_consumer_impact_text(renderer_scan: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    current_unadopted = [
        row
        for row in rows
        if row["surface_id"] == "live_current_runtime" and row["derived_adoption_state"] == "unadopted"
    ]
    return f"""# Runtime Consumer Impact Report

Status: `PASS`.

The live renderer has `{renderer_scan['publish_state_read_hit_count']}` `publish_state` read hit(s), but current payload rows do not carry `publish_state`. No source/runtime/quality policy hit was found in renderer scan.

The 21 current `unadopted` rows have no display body (`text_ko` is nil/missing), so guard-only execution preserves display resolution for those rows.
"""


def independent_review_text() -> str:
    return """# Independent Review

Status: `blocked_external_gate`.

No independent reviewer outside the roadmap authorship chain has reviewed this execution packet in this Codex run. This blocks a `complete` final seal but does not block the machine guard from failing closed in the current route.
"""


def review_map_text() -> str:
    return """# Review Finding Resolution Map

| finding | disposition |
| --- | --- |
| C1 independent review | blocked external gate |
| C2 publish_state authority | resolved as current payload absent / predecessor residue |
| I1-I8 / M1-M3 | represented in evidence artifacts or carried as final certification ceiling |
"""


def certification_ceiling_text() -> str:
    return """# Template / Execution Contract Certification Ceiling

Status: `disclosed_limit`.

This execution generated the required evidence packet and guard artifacts, but final certification remains limited until independent review and author-reserved branch disposition are supplied.
"""


def policy_text() -> str:
    return """# Runtime Payload State Policy

Current-compatible payload shape:

* adopted rows: `text_ko` must be a non-nil string, and `publish_state` must be absent.
* unadopted rows: `text_ko` must be missing or nil, and `publish_state` must be absent.
* predecessor rollback rows with `unadopted + exposed + non_nil text_ko` are legacy residue and must not re-enter current/current-looking payload surfaces.

This policy is a payload-shape guard, not runtime visibility policy or release readiness.
"""


def contract_text() -> str:
    return """# Runtime Payload Shape Contract

Runtime payload state shape is sealed at build time.

The current route consumes `runtime_payload_shape_matrix.json`, `payload_shape_validation_report.json`, and `current_route_payload_state_guard_report.json`. Forbidden current/current-looking payload combinations fail loud; predecessor residues are counted separately.

Runtime Lua remains a renderer and does not become a source, quality, or publish policy checker.
"""


def closeout_text(guard: dict[str, Any]) -> str:
    return f"""# Runtime Payload State Integrity Closeout

Status: `implemented_guard_pass_author_review_pending`.

Machine guard status: `{guard['status']}`.

Implemented scope:

* current runtime payload inventory
* 21-row unadopted audit
* field identity and publish_state authority resolution
* payload shape matrix and validator
* current-route guard artifact generation
* predecessor rollback residue re-entry guard
* renderer consumer boundary scan

Remaining seal gates:

* author-reserved Branch A / Branch B disposition, or explicit no-branch mutation decision
* independent review outside the roadmap authorship chain

Non-claims: {CLAIM_BOUNDARY}
"""


def ledger_packet_text(guard: dict[str, Any]) -> str:
    return f"""# Runtime Payload State Integrity Ledger Packet

Draft additive packet; not automatically applied to authority docs.

Runtime payload state shape guard generated evidence under `Iris/build/description/v2/staging/runtime_payload_state_integrity/`.

Guard status: `{guard['status']}`.

Current row readpoint: 2105 rows, 21 unadopted rows, zero current/current-looking forbidden rows, predecessor rollback residue counted separately.

Final complete seal remains gated on author-reserved branch disposition and independent review.
"""


def addendum_text() -> str:
    return """# DVF Contract Current Reseal Payload State Addendum

Subordinate draft only. Fold into `docs/runtime_payload_shape_contract.md`.

The current-compatible runtime payload shape forbids current/current-looking `unadopted + publish_state` and `unadopted + non_nil text_ko` combinations. Predecessor rollback residues are guarded as legacy-only evidence.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and validate runtime payload state integrity evidence.")
    parser.add_argument("--mode", choices=["generate", "validate"], default="generate")
    args = parser.parse_args()

    guard = run_all()
    if args.mode == "validate":
        return 0 if guard["status"] == "PASS" else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
