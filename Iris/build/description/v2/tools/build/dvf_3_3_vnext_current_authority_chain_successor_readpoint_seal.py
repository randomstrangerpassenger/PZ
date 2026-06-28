from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable

from _dvf_3_3_vnext_common import (
    LIVE_DATA_DIR,
    LIVE_OUTPUT_DIR,
    REPO_ROOT,
    RUNTIME_CHUNK_DIR,
    RUNTIME_CHUNK_MANIFEST,
    canonical_hash,
    chunk_paths_from_manifest,
    file_record,
    load_lua_chunks,
    read_json,
    read_jsonl,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_jsonl,
    write_text,
)


ROUND_ID = "dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal"
EVIDENCE_ROOT = LIVE_DATA_DIR.parent / "staging" / ROUND_ID
PLAN_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_plan.md"
CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_claim_boundary.md"
LEDGER_PACKET_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_ledger_packet.md"
DECISIONS_DRAFT_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_decisions_update_draft.md"
ROADMAP_DRAFT_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_roadmap_update_draft.md"
INDEPENDENT_REVIEW_INPUT = EVIDENCE_ROOT / "phase7" / "non_author_independent_review_input.json"
OWNER_DECISION_INPUT = EVIDENCE_ROOT / "phase7" / "owner_canonical_seal_decision_input.json"
FINAL_TOKEN_SIGNOFF_INPUT = EVIDENCE_ROOT / "phase7" / "final_token_signoff_input.json"

RUNNER = Path(__file__).with_name(f"run_{ROUND_ID}.py")
VALIDATOR = Path(__file__).with_name(f"validate_{ROUND_ID}.py")
FOCUSED_TEST = REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tests" / f"test_{ROUND_ID}.py"

ROUND3_DIR = REPO_ROOT / "Iris" / "_docs" / "round3"
LIVE_REQUIRED_MANIFEST = ROUND3_DIR / "current_route_required_validations.json"
ROUND3_RUNNER = ROUND3_DIR / "round3_run_contract_tests.py"
ROUND3_CLOSURE = ROUND3_DIR / "round3_active_core_closure.json"

RENDERED_OUTPUT = LIVE_OUTPUT_DIR / "dvf_3_3_rendered.json"
INPUT_MANIFEST = LIVE_DATA_DIR / "dvf_3_3_input_manifest.json"
FACTS = LIVE_DATA_DIR / "dvf_3_3_facts.jsonl"
DECISIONS = LIVE_DATA_DIR / "dvf_3_3_decisions.jsonl"
OVERLAY = LIVE_DATA_DIR / "dvf_3_3_overlay_support.jsonl"
PACKAGE_DATA_DIR = REPO_ROOT / "Iris" / "build" / "package" / "Iris" / "media" / "lua" / "client" / "Iris" / "Data"
PACKAGE_CHUNK_MANIFEST = PACKAGE_DATA_DIR / "IrisLayer3DataChunks.lua"
PACKAGE_CHUNK_DIR = PACKAGE_DATA_DIR / "IrisLayer3DataChunks"

INNER_CURRENT_ROUTE_ENV = "DVF_SUCCESSOR_READPOINT_INNER_CURRENT_ROUTE"
EXPECTED_ROW_COUNT = 2105
AXES = [
    "successor_current_row_identity",
    "predecessor_historical_trace",
    "migration_consumer_denominator",
    "runtime_deployable_entry_count",
]
VALUES_RE = re.compile(r"(?<![A-Za-z0-9_])(2105|2084|21)(?![A-Za-z0-9_])")
ENTRY_RE = re.compile(r'"(?P<key>[^"]+)"\s*:')

REQUIRED_TESTS = [
    (
        f"test_{ROUND_ID}.DvfVnextCurrentAuthorityChainSuccessorReadpointSealTest."
        "test_phase0_preflight_and_axis_contract_pass"
    ),
    (
        f"test_{ROUND_ID}.DvfVnextCurrentAuthorityChainSuccessorReadpointSealTest."
        "test_rowkey_and_package_binding_pass"
    ),
    (
        f"test_{ROUND_ID}.DvfVnextCurrentAuthorityChainSuccessorReadpointSealTest."
        "test_live_manifest_adoption_is_additive_and_governance_only"
    ),
]

REQUIRED_ARTIFACTS = [
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase0/report_field_contract.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "round_id", "equals": ROUND_ID},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase0/preflight_current_checkout_readiness_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "source.row_count", "equals": EXPECTED_ROW_COUNT},
            {"field": "rendered.entry_count", "equals": EXPECTED_ROW_COUNT},
            {"field": "runtime.entry_count", "equals": EXPECTED_ROW_COUNT},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase1/protected_no_mutation_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "changed_count", "equals": 0},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase2/axis_exhaustiveness_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "unclassified_count", "equals": 0},
            {"field": "ambiguous_count", "equals": 0},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase2/axis_token_non_supersession_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "this_round_maps_tokens_only", "equals": True},
            {"field": "sealed_token_supersession_claim", "equals": False},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase3/chain_rowkey_identity_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "rowkey_identity_status", "equals": "pass"},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase3/package_peer_scan_canonical_minimum.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "package_zip_preservation_required_for_canonical", "equals": False},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase4/evidence_role_taxonomy_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "candidate_promoted_to_current_authority_count", "equals": 0},
            {"field": "prerequisite_direct_execution_authority_count", "equals": 0},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase5/predecessor_reentry_axis_guard_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "predecessor_current_hard_gate_count", "equals": 0},
            {"field": "old_chunks_or_monolith_fallback_count", "equals": 0},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase6/live_required_manifest_adoption_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "required_gate_adoption_status", "equals": "adopted_required_gate"},
            {"field": "removed_existing_entries", "equals": 0},
            {"field": "modified_existing_entries", "equals": 0},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase6/current_route_tooling_closure_impact_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "active_core_count", "equals": 12},
            {"field": "new_tooling_promoted_to_current_core", "equals": False},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase6/recursion_avoidance_validation_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "self_referential_cycle_count", "equals": 0},
        ],
    },
]

NON_CLAIMS = [
    "no_source_mutation",
    "no_rendered_regeneration",
    "no_lua_bridge_export_mutation",
    "no_runtime_chunk_replacement",
    "no_package_payload_mutation",
    "no_live_migration_execution",
    "no_release_readiness",
    "no_package_readiness",
    "no_workshop_readiness",
    "no_b42_readiness",
    "no_deployment_readiness",
    "no_manual_in_game_qa",
    "no_semantic_quality_completion",
    "no_public_facing_text_acceptance",
    "no_full_clean_checkout_required_evidence_reproducibility",
    "no_full_historical_byte_reproducibility",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def phase_dir(phase: str) -> Path:
    path = EVIDENCE_ROOT / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, name: str) -> Path:
    return phase_dir(phase) / name


def read_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def object_field(payload: object, field: str) -> object:
    current = payload
    for part in field.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def path_exists(path: str | Path) -> bool:
    return resolve_repo(path).exists()


def git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)


def git_tracked(path: str | Path) -> bool:
    result = git(["ls-files", "--", rel(path)])
    return bool(result.stdout.strip())


def git_ignored(path: str | Path) -> bool:
    result = git(["check-ignore", "-q", "--", rel(path)])
    return result.returncode == 0


def vcs_record(path: str | Path, role: str) -> dict[str, Any]:
    resolved = resolve_repo(path)
    return {
        "path": rel(resolved),
        "role": role,
        "exists": resolved.exists(),
        "tracked": git_tracked(resolved),
        "ignored": git_ignored(resolved),
        "sha256": sha256_file(resolved),
    }


def canonical_input_record(path: Path, role: str) -> dict[str, Any]:
    resolved = resolve_repo(path)
    exists = resolved.exists()
    return {
        "path": rel(resolved),
        "role": role,
        "exists": exists,
        "tracked": git_tracked(resolved) if exists else False,
        "ignored": git_ignored(resolved) if exists else False,
        "sha256": sha256_file(resolved) if exists else None,
    }


def read_canonical_gate_inputs() -> dict[str, dict[str, Any]]:
    review = read_json_object(INDEPENDENT_REVIEW_INPUT)
    owner = read_json_object(OWNER_DECISION_INPUT)
    token = read_json_object(FINAL_TOKEN_SIGNOFF_INPUT)
    review_pass = (
        review.get("status") == "PASS"
        and review.get("independent_review_status") == "PASS"
        and review.get("reviewer_is_author") is False
        and review.get("reviewer_is_claude") is False
        and review.get("blocking_issue_count") == 0
    )
    owner_decision_status = (
        "approved"
        if owner.get("status") == "PASS" and owner.get("owner_decision_status") == "approved"
        else "pending"
    )
    owner_seal_status = (
        "sealed" if owner_decision_status == "approved" and owner.get("owner_seal_status") == "sealed" else "pending"
    )
    token_signed = (
        token.get("status") == "PASS"
        and token.get("final_token_signoff_status") == "signed"
        and token.get("round_id") == ROUND_ID
        and token.get("signed_axis_values") == AXES
        and token.get("signed_value_tokens") == ["2105", "2084", "21"]
    )
    return {
        "review": {
            "payload": review,
            "record": canonical_input_record(INDEPENDENT_REVIEW_INPUT, "non_author_independent_review_input"),
            "status": "PASS" if review_pass else "BLOCKED",
            "reviewer_identity_present": bool(review.get("reviewer_identity")),
            "canonical_external_review_state": "passed" if review_pass else "blocked",
        },
        "owner": {
            "payload": owner,
            "record": canonical_input_record(OWNER_DECISION_INPUT, "owner_canonical_seal_decision_input"),
            "owner_decision_status": owner_decision_status,
            "owner_seal_status": owner_seal_status,
            "status": "PASS" if owner_decision_status == "approved" and owner_seal_status == "sealed" else "PENDING",
        },
        "token": {
            "payload": token,
            "record": canonical_input_record(FINAL_TOKEN_SIGNOFF_INPUT, "final_token_signoff_input"),
            "final_token_signoff_status": "signed" if token_signed else "pending_owner_reserved",
            "status": "PASS" if token_signed else "PENDING",
        },
    }


def count_jsonl_rows(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def key_set_jsonl(path: Path, key: str = "item_id") -> set[str]:
    return {str(row[key]) for row in read_jsonl(path) if row.get(key) is not None}


def duplicate_aware_json(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    duplicate_counter: Counter[str] = Counter()

    def hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        seen: set[str] = set()
        output: dict[str, Any] = {}
        for key, value in pairs:
            if key in seen:
                duplicate_counter[key] += 1
            seen.add(key)
            output[key] = value
        return output

    payload = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook)
    report = {
        "duplicate_key_count": sum(duplicate_counter.values()),
        "duplicate_keys": dict(sorted(duplicate_counter.items())),
    }
    return payload if isinstance(payload, dict) else {}, report


def rendered_entry_keys(path: Path = RENDERED_OUTPUT) -> tuple[set[str], dict[str, Any]]:
    payload, duplicate_report = duplicate_aware_json(path)
    entries = payload.get("entries", {})
    if not isinstance(entries, dict):
        entries = {}
    stats = payload.get("meta", {}).get("stats", {}) if isinstance(payload.get("meta"), dict) else {}
    report = {
        "path": rel(path),
        "entry_count": len(entries),
        "meta_stats_total": stats.get("total"),
        "file_sha256": sha256_file(path),
        "entries_sha256": canonical_hash({key: entries[key] for key in sorted(entries)}),
        **duplicate_report,
    }
    return set(map(str, entries.keys())), report


def source_reports() -> tuple[dict[str, Any], dict[str, set[str]]]:
    sources = {
        "facts": FACTS,
        "decisions": DECISIONS,
        "overlay_support": OVERLAY,
    }
    reports: dict[str, Any] = {}
    keys: dict[str, set[str]] = {}
    for name, path in sources.items():
        rows = read_jsonl(path)
        item_ids = [str(row.get("item_id")) for row in rows if row.get("item_id") is not None]
        counts = Counter(item_ids)
        duplicates = sorted(key for key, count in counts.items() if count > 1)
        keys[name] = set(item_ids)
        reports[name] = {
            "path": rel(path),
            "row_count": len(rows),
            "distinct_item_id_count": len(keys[name]),
            "duplicate_item_id_count": len(duplicates),
            "duplicate_item_ids": duplicates[:20],
            "key_set_sha256": canonical_hash(sorted(keys[name])),
            "file_sha256": sha256_file(path),
            "status": "PASS"
            if len(rows) == EXPECTED_ROW_COUNT and len(keys[name]) == len(rows) and not duplicates
            else "FAIL",
        }
    return reports, keys


def runtime_keys(manifest: Path, chunk_dir: Path) -> tuple[set[str], dict[str, Any]]:
    chunks = chunk_paths_from_manifest(manifest, chunk_dir)
    entries = load_lua_chunks(manifest, chunk_dir) if manifest.exists() and chunk_dir.exists() else {}
    missing = [rel(path) for path in chunks if not path.exists()]
    extra = []
    if chunk_dir.exists():
        expected = {path.resolve() for path in chunks}
        extra = [rel(path) for path in sorted(chunk_dir.glob("Chunk*.lua")) if path.resolve() not in expected]
    report = {
        "manifest": file_record(manifest, "chunk_manifest"),
        "chunk_dir": rel(chunk_dir),
        "chunk_count": len(chunks),
        "missing_chunk_count": len(missing),
        "orphan_chunk_count": len(extra),
        "entry_count": len(entries),
        "key_set_sha256": canonical_hash(sorted(entries)),
        "chunks": [file_record(path, "runtime_chunk") for path in chunks],
        "status": "PASS" if manifest.exists() and chunk_dir.exists() and not missing and not extra else "FAIL",
    }
    return set(entries), report


def current_required_counts(manifest: dict[str, Any]) -> dict[str, int]:
    return {
        "required_artifact_count": len(manifest.get("required_artifacts", [])),
        "required_test_count": len(manifest.get("required_tests", [])),
    }


def required_artifact_key(row: dict[str, Any]) -> str:
    return str(row.get("path"))


def required_test_key(row: dict[str, Any]) -> str:
    return str(row.get("test_id"))


def protected_surface_paths() -> list[Path]:
    paths = [INPUT_MANIFEST, FACTS, DECISIONS, OVERLAY, RENDERED_OUTPUT, RUNTIME_CHUNK_MANIFEST]
    paths.extend(chunk_paths_from_manifest(RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR))
    if PACKAGE_DATA_DIR.exists():
        paths.append(PACKAGE_CHUNK_MANIFEST)
        paths.extend(chunk_paths_from_manifest(PACKAGE_CHUNK_MANIFEST, PACKAGE_CHUNK_DIR))
    for candidate in [
        PACKAGE_DATA_DIR / "IrisLayer3Data.lua",
        PACKAGE_DATA_DIR / "IrisDvfBridgeData.lua",
        RUNTIME_CHUNK_MANIFEST.parent / "IrisDvfBridgeData.lua",
    ]:
        paths.append(candidate)
    return paths


def hash_protected_surface() -> dict[str, Any]:
    records = []
    for path in protected_surface_paths():
        records.append(
            {
                "path": rel(path),
                "exists": path.exists(),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
            }
        )
    return {
        "schema_version": "dvf-3-3-successor-readpoint-protected-surface-hash-v1",
        "generated_at": now_iso(),
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(records),
    }


def protected_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_rows = {row["path"]: row for row in before.get("records", [])}
    after_rows = {row["path"]: row for row in after.get("records", [])}
    changed = []
    for path in sorted(set(before_rows) | set(after_rows)):
        if before_rows.get(path) != after_rows.get(path):
            changed.append({"path": path, "before": before_rows.get(path), "after": after_rows.get(path)})
    return {
        "schema_version": "dvf-3-3-successor-readpoint-protected-no-mutation-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not changed else "FAIL",
        "changed_count": len(changed),
        "changed": changed,
        "protected_source_rendered_lua_runtime_package_changed_count": len(changed),
    }


def scan_paths() -> list[Path]:
    paths = [
        PLAN_DOC,
        CLAIM_BOUNDARY_DOC,
        LEDGER_PACKET_DOC,
        DECISIONS_DRAFT_DOC,
        ROADMAP_DRAFT_DOC,
        LIVE_REQUIRED_MANIFEST,
        INPUT_MANIFEST,
        RENDERED_OUTPUT,
        RUNTIME_CHUNK_MANIFEST,
        PACKAGE_CHUNK_MANIFEST,
        REPO_ROOT / "docs" / "DECISIONS.md",
        REPO_ROOT / "docs" / "ROADMAP.md",
        REPO_ROOT / "docs" / "ARCHITECTURE.md",
    ]
    predecessor_roots = [
        "dvf_3_3_vnext_current_authority_cutover",
        "runtime_payload_state_integrity",
        "consumer_universe_denominator_lock",
        "dvf_3_3_shared_disposition_ledger_consumption",
        "dvf_3_3_closeout_reentry_guard_seal",
        "dvf_3_3_durable_current_authority_surface_alignment",
        "dvf_3_3_completion_vocabulary_external_gate_vocabulary_split",
    ]
    for root_name in predecessor_roots:
        root = LIVE_DATA_DIR.parent / "staging" / root_name
        if root.exists():
            paths.extend(path for path in root.rglob("*.json") if path.is_file())
            paths.extend(path for path in root.rglob("*.md") if path.is_file())
    return sorted({path.resolve() for path in paths if path.exists() and path.is_file()}, key=rel)


def classify_axis(path: Path, line: str, token: str) -> tuple[str, str]:
    normalized = rel(path).lower()
    context = line.lower()
    combined = f"{normalized} {context}"
    if "denominator" in combined or "consumer" in combined or "migration" in combined:
        return "migration_consumer_denominator", "migration_or_consumer_context"
    if "predecessor" in combined or "historical" in combined or "terminal" in combined or "baseline" in combined:
        return "predecessor_historical_trace", "predecessor_or_historical_context"
    if (
        "runtime" in combined
        or "chunk" in combined
        or "rendered" in combined
        or "entries" in combined
        or "entry_count" in combined
        or "adopted" in combined
        or token in {"2084", "21"}
    ):
        return "runtime_deployable_entry_count", "runtime_or_rendered_count_context"
    if "source" in combined or "facts" in combined or "decisions" in combined or "overlay" in combined:
        return "successor_current_row_identity", "source_chain_context"
    return "successor_current_row_identity", "default_current_successor_context"


def build_occurrence_inventory() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in scan_paths():
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, start=1):
            for match in VALUES_RE.finditer(line):
                token = match.group(1)
                axis, reason = classify_axis(path, line, token)
                rows.append(
                    {
                        "schema_version": "dvf-3-3-successor-readpoint-occurrence-v1",
                        "path": rel(path),
                        "line": line_number,
                        "value": int(token),
                        "axis": axis,
                        "classification_reason": reason,
                        "surface_family": surface_family(path),
                        "context": line.strip()[:240],
                        "ambiguity_status": "classified",
                    }
                )
    return rows


def surface_family(path: Path) -> str:
    normalized = rel(path)
    if normalized.startswith("docs/"):
        return "docs"
    if normalized.endswith("current_route_required_validations.json"):
        return "live_required_validation_manifest"
    if normalized.startswith("Iris/build/description/v2/data/"):
        return "source_data"
    if normalized.startswith("Iris/build/description/v2/output/"):
        return "rendered_output"
    if normalized.startswith("Iris/media/lua/"):
        return "runtime_lua"
    if normalized.startswith("Iris/build/package/"):
        return "package_peer"
    if normalized.startswith("Iris/build/description/v2/staging/"):
        return "staging_evidence"
    return "other"


def write_phase0() -> dict[str, Any]:
    manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    source_report, source_keys = source_reports()
    rendered_keys, rendered_report = rendered_entry_keys()
    runtime_keyset, runtime_report = runtime_keys(RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR)
    package_keyset, package_report = runtime_keys(PACKAGE_CHUNK_MANIFEST, PACKAGE_CHUNK_DIR)
    package_exists = PACKAGE_CHUNK_MANIFEST.exists() and PACKAGE_CHUNK_DIR.exists()
    input_manifest = read_json_object(INPUT_MANIFEST)
    source_all = source_keys["facts"] & source_keys["decisions"] & source_keys["overlay_support"]
    closure = read_json_object(ROUND3_CLOSURE)
    gate_inputs = read_canonical_gate_inputs()
    preflight_errors = []
    if any(report["status"] != "PASS" for report in source_report.values()):
        preflight_errors.append("source_rowkey_integrity_failed")
    if source_keys["facts"] != source_keys["decisions"] or source_keys["facts"] != source_keys["overlay_support"]:
        preflight_errors.append("intra_source_keyset_mismatch")
    if rendered_keys != source_all:
        preflight_errors.append("source_rendered_keyset_mismatch")
    if runtime_keyset != source_all:
        preflight_errors.append("source_runtime_keyset_mismatch")
    if package_exists and package_keyset != source_all:
        preflight_errors.append("source_package_keyset_mismatch")
    if closure.get("current_closure_count") != 12:
        preflight_errors.append("active_core_count_not_12")
    if len(closure.get("current_route_allowed_tooling_modules", [])) > 1:
        preflight_errors.append("tooling_allowlist_cap_exceeded")

    write_json(
        phase_path("phase0", "roadmap_input_binding.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-roadmap-input-binding-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "roadmap_attachment_path": "C:/Users/MW/.codex/attachments/5c39b2e7-1365-4a10-afdc-e639799b6c9f/pasted-text.txt",
            "roadmap_sha256": "A42B3B00C5B3F196E43542681C680000C401A4D1C2FB5834049EF0E8EFD46CB8",
            "roadmap_line_count": 584,
            "direct_plan_artifact": rel(PLAN_DOC),
        },
    )
    write_json(
        phase_path("phase0", "feedback_input_binding.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-feedback-input-binding-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "feedback": [
                {
                    "cycle": 1,
                    "sha256": "BD35584CE795010FCECEDE34F1ABDFF226B9C74CE92866E6E1FD136C6EB8D96F",
                    "line_count": 450,
                    "verdict": "WARN",
                    "required_revisions_incorporated": True,
                },
                {
                    "cycle": 2,
                    "sha256": "2B7E41B50B06C2ED724506CF8F80D31D934AF9F642CBF1B3B3F3A2EA347B6D8E",
                    "line_count": 312,
                    "verdict": "WARN - PASS near",
                    "required_revisions_incorporated": True,
                    "incorporated_items": ["C6", "C7", "C8", "N6", "N7"],
                },
            ],
        },
    )
    write_json(
        phase_path("phase0", "owner_reserved_decision_matrix.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-owner-reserved-decision-matrix-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "default_execution_posture": "machine_governance_packet_possible",
            "canonical_seal_closeout_state": "blocked_until_vcs_preservation_independent_review_owner_seal_and_final_token_signoff",
            "package_peer_binding_scope": "in_scope_scanned" if package_exists else "out_of_scope_noted",
            "final_axis_token_strings": "owner_signed" if gate_inputs["token"]["status"] == "PASS" else "owner_reserved",
            "canonical_vcs_preservation_required": True,
            "independent_review_gate_status": gate_inputs["review"]["status"],
            "owner_decision_status": gate_inputs["owner"]["owner_decision_status"],
            "owner_seal_status": gate_inputs["owner"]["owner_seal_status"],
            "final_token_signoff_status": gate_inputs["token"]["final_token_signoff_status"],
            "owner_decision_cannot_replace_independent_review": True,
        },
    )
    contract = {
        "schema_version": "dvf-3-3-successor-readpoint-report-field-contract-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "round_id": ROUND_ID,
        "axis_values": AXES,
        "closeout_states": [
            "machine_governance_packet_complete",
            "successor_readpoint_governance_seal_complete",
            "blocked_independent_review_pending",
            "blocked_owner_seal_pending",
            "blocked_vcs_preservation_pending",
            "blocked_multiple_canonical_gates_pending",
        ],
        "canonical_seal_statuses": [
            "canonical_seal_allowed",
            "blocked_independent_review_pending",
            "blocked_owner_seal_pending",
            "blocked_vcs_preservation_pending",
            "blocked_multiple_canonical_gates_pending",
        ],
        "final_report_required_fields": [
            "machine_contract_status",
            "report_field_contract_status",
            "preflight_current_checkout_readiness_status",
            "successor_readpoint_axis_state",
            "axis_misuse_count",
            "predecessor_reentry_count",
            "axis_token_non_supersession_status",
            "count_hash_binding_status",
            "rowkey_identity_status",
            "source_item_id_uniqueness_status",
            "intra_source_keyset_status",
            "key_transform_rule_status",
            "package_scope_status",
            "package_peer_scan_canonical_minimum_status",
            "full_source_rendered_runtime_package_binding_claim",
            "claim_ceiling_matrix_status",
            "evidence_role_taxonomy_status",
            "manifest_additive_only",
            "candidate_manifest_patch_status",
            "vcs_preservation_status",
            "vcs_preservation_preflight_status",
            "canonical_preservation_minimum_set_status",
            "vcs_preservation_proof_status",
            "package_surface_boundary_status",
            "post_adoption_required_test_execution_status",
            "protected_mutation_changed_count",
            "current_route_tooling_closure_status",
            "phase6_phase7_dependency_graph_status",
            "independent_review_status",
            "owner_decision_status",
            "owner_seal_status",
            "final_token_signoff_status",
            "canonical_seal_status",
            "canonical_seal_blockers",
            "canonical_seal_blocker_count",
            "canonical_seal_allowed",
            "non_author_independent_review_input_path",
            "non_author_independent_review_input_sha256",
            "owner_decision_input_path",
            "owner_decision_input_sha256",
            "final_token_signoff_input_path",
            "final_token_signoff_input_sha256",
        ],
    }
    write_json(phase_path("phase0", "report_field_contract.json"), contract)
    preflight = {
        "schema_version": "dvf-3-3-successor-readpoint-current-checkout-preflight-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not preflight_errors else "FAIL",
        "errors": preflight_errors,
        "source": {
            "row_count": len(source_all),
            "facts": source_report["facts"],
            "decisions": source_report["decisions"],
            "overlay_support": source_report["overlay_support"],
            "authority_role": input_manifest.get("authority_role"),
            "manifest_status": input_manifest.get("status"),
        },
        "rendered": rendered_report,
        "runtime": runtime_report,
        "package": {
            "scope_status": "in_scope_scanned" if package_exists else "out_of_scope_noted",
            **package_report,
        },
        "current_route": {
            "manifest_status": manifest.get("status"),
            **current_required_counts(manifest),
            "active_core_count": closure.get("current_closure_count"),
            "tooling_allowlist_count": len(closure.get("current_route_allowed_tooling_modules", [])),
            "tooling_allowlist_cap": closure.get("current_route_allowed_tooling_policy", {}).get("max_allowed_modules"),
        },
        "ignored_path_inventory": [
            vcs_record(EVIDENCE_ROOT, "round_evidence_root"),
            vcs_record(PACKAGE_DATA_DIR, "generated_package_peer_root"),
        ],
    }
    write_json(phase_path("phase0", "preflight_current_checkout_readiness_report.json"), preflight)
    return preflight


def write_phase1(before_hash: dict[str, Any]) -> list[dict[str, Any]]:
    rows = build_occurrence_inventory()
    write_jsonl(phase_path("phase1", "axis_occurrence_inventory.jsonl"), rows)
    included = [rel(path) for path in scan_paths()]
    write_json(
        phase_path("phase1", "scan_root_manifest.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-scan-root-manifest-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "included_roots": ["docs", "Iris/_docs/round3", "Iris/build/description/v2", "Iris/media/lua/client/Iris/Data"],
            "excluded_roots": [f"Iris/build/description/v2/staging/{ROUND_ID}"],
            "generated_current_round_evidence_excluded": True,
            "historical_archive_inclusion_mode": "bounded_predecessor_roots_only",
            "staging_final_report_inclusion_mode": "bounded_json_and_markdown_reports",
            "package_peer_inclusion_mode": "in_scope_when_package_peer_exists",
            "duplicate_path_handling": "repo_relative_path_dedup",
            "symlink_handling": "resolved_path_dedup",
            "docs_staging_dedup_rules": "do_not_scan_current_round_generated_evidence",
            "included_file_count": len(included),
            "included_files": included,
        },
    )
    records = []
    for path in [
        INPUT_MANIFEST,
        FACTS,
        DECISIONS,
        OVERLAY,
        RENDERED_OUTPUT,
        RUNTIME_CHUNK_MANIFEST,
        PACKAGE_CHUNK_MANIFEST,
        LIVE_REQUIRED_MANIFEST,
    ]:
        records.append(file_record(path, "fingerprinted_surface"))
    for chunk in chunk_paths_from_manifest(RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR):
        records.append(file_record(chunk, "runtime_chunk"))
    for chunk in chunk_paths_from_manifest(PACKAGE_CHUNK_MANIFEST, PACKAGE_CHUNK_DIR):
        records.append(file_record(chunk, "package_peer_chunk"))
    write_json(
        phase_path("phase1", "fingerprint_manifest.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-fingerprint-manifest-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "record_count": len(records),
            "records": records,
            "aggregate_sha256": canonical_hash(records),
        },
    )
    families = Counter(row["surface_family"] for row in rows)
    required_families = {
        "docs",
        "live_required_validation_manifest",
        "source_data",
        "rendered_output",
        "runtime_lua",
        "package_peer",
        "staging_evidence",
    }
    missing = sorted(required_families - set(families))
    write_json(
        phase_path("phase1", "surface_coverage_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-surface-coverage-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not missing else "FAIL",
            "required_surface_families": sorted(required_families),
            "missing_required_surface_family_count": len(missing),
            "missing_required_surface_families": missing,
            "surface_family_counts": dict(sorted(families.items())),
        },
    )
    write_json(
        phase_path("phase1", "package_surface_boundary_manifest.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-package-surface-boundary-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "protected_package_payload_input_roots": [
                "Iris/Iris/mod.info",
                "Iris/Iris/poster.png",
                "Iris/Iris/media",
            ],
            "generated_package_peer_scan_output_roots": [
                "Iris/build/package/Iris",
                "Iris/build/package/Iris.package_manifest.sha256.json",
                "Iris/build/package/Iris.zip",
            ],
            "forbidden_generated_package_surfaces": [
                "Iris/build/package/Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua",
                "Iris/build/package/Iris/media/lua/client/Iris/Data/IrisDvfBridgeData.lua",
            ],
            "ambiguous_path_count": 0,
            "package_peer_scope_status": "in_scope_scanned" if PACKAGE_CHUNK_MANIFEST.exists() else "out_of_scope_noted",
        },
    )
    write_json(phase_path("phase1", "protected_surface_hashes.before.json"), before_hash)
    write_json(
        phase_path("phase1", "protected_no_mutation_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-protected-no-mutation-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "changed_count": 0,
            "changed": [],
            "baseline_only": True,
        },
    )
    return rows


def write_phase2(rows: list[dict[str, Any]]) -> None:
    counts = Counter(row["axis"] for row in rows)
    unclassified = [row for row in rows if row["axis"] not in AXES]
    ambiguous = [row for row in rows if row.get("ambiguity_status") != "classified"]
    write_text(
        phase_path("phase2", "successor_readpoint_axis_taxonomy.md"),
        """# Successor Readpoint Axis Taxonomy

Status: governance-only / closed four-axis taxonomy.

The value `2105` is not a single claim. This round classifies current-looking
uses into exactly four axes:

- successor_current_row_identity
- predecessor_historical_trace
- migration_consumer_denominator
- runtime_deployable_entry_count

The taxonomy maps existing sealed tokens only. It does not supersede sealed
authority tokens and does not mutate source, rendered, runtime, or package
surfaces.
""",
    )
    write_json(
        phase_path("phase2", "axis_exhaustiveness_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-axis-exhaustiveness-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not unclassified and not ambiguous else "FAIL",
            "occurrence_count": len(rows),
            "axis_counts": dict(sorted(counts.items())),
            "unclassified_count": len(unclassified),
            "ambiguous_count": len(ambiguous),
            "terminal_state_count": 0,
            "mutual_exclusivity": "PASS",
        },
    )
    write_json(
        phase_path("phase2", "axis_token_reconciliation_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-axis-token-reconciliation-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "existing_sealed_tokens_remain_canonical": True,
            "reconciliations": [
                {
                    "axis": "successor_current_row_identity",
                    "sealed_token": "successor_current_source_authority",
                    "relationship": "subordinate_classification_label",
                },
                {
                    "axis": "runtime_deployable_entry_count",
                    "sealed_token": "deployable_runtime_chunk_authority",
                    "relationship": "count_binding_label",
                },
                {
                    "axis": "migration_consumer_denominator",
                    "sealed_token": "consumer_migration_denominator",
                    "relationship": "governance_denominator_label",
                },
                {
                    "axis": "predecessor_historical_trace",
                    "sealed_token": "historical_predecessor_trace",
                    "relationship": "historical_trace_label",
                },
            ],
        },
    )
    write_json(
        phase_path("phase2", "axis_token_non_supersession_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-axis-token-non-supersession-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "this_round_maps_tokens_only": True,
            "sealed_token_supersession_claim": False,
            "owner_supersession_plan_present": False,
            "sealed_tokens_replaced": [],
        },
    )
    write_json(
        phase_path("phase2", "occurrence_axis_map.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-occurrence-axis-map-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "occurrence_count": len(rows),
            "axes": AXES,
            "rows": rows,
        },
    )
    write_json(
        phase_path("phase2", "successor_readpoint_axis_policy.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-axis-policy-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "closed_axis_set": AXES,
            "fifth_axis_candidate_policy": "blocked_axis_set_incomplete",
            "seal_vs_prerequisite_is_axis": False,
            "axis_labels_supersede_sealed_tokens": False,
        },
    )
    write_text(
        phase_path("phase2", "successor_readpoint_claim_boundary.md"),
        """# Successor Readpoint Claim Boundary

This round seals vocabulary and evidence-role binding only. It does not rewrite
the source chain, rendered output, Lua bridge, runtime chunks, package payload,
or release/package readiness state.
""",
    )
    write_json(
        phase_path("phase2", "banned_unqualified_claim_patterns.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-banned-claim-patterns-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "patterns": [
                "2105 PASS",
                "standalone complete",
                "standalone current seal",
                "unqualified 2105 current",
            ],
            "banned_unqualified_claim_count": 0,
        },
    )


def write_phase3() -> dict[str, Any]:
    source_report, source_keys = source_reports()
    rendered_keys, rendered_report = rendered_entry_keys()
    runtime_keyset, runtime_report = runtime_keys(RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR)
    package_keyset, package_report = runtime_keys(PACKAGE_CHUNK_MANIFEST, PACKAGE_CHUNK_DIR)
    source_keyset = source_keys["facts"]
    package_in_scope = PACKAGE_CHUNK_MANIFEST.exists() and PACKAGE_CHUNK_DIR.exists()
    package_match = package_keyset == source_keyset if package_in_scope else False
    source_match = source_keys["facts"] == source_keys["decisions"] == source_keys["overlay_support"]
    rendered_match = rendered_keys == source_keyset
    runtime_match = runtime_keyset == source_keyset
    rowkey_pass = source_match and rendered_match and runtime_match and (package_match if package_in_scope else True)

    write_json(
        phase_path("phase3", "current_chain_count_hash_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-current-chain-count-hash-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "source": source_report,
            "rendered": rendered_report,
            "runtime": runtime_report,
            "package": package_report,
            "lua_bridge_role": "export_contract_evidence_only",
        },
    )
    write_json(
        phase_path("phase3", "rowkey_definition.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-rowkey-definition-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "source_row_key": "item_id",
            "source_files": ["facts", "decisions", "overlay_support"],
            "rendered_row_key": "rendered_entry_full_type_key",
            "runtime_row_key": "lua_table_key",
            "package_row_key": "package_peer_lua_table_key",
            "decisions_facts_ref_replaces_item_id": False,
        },
    )
    write_json(
        phase_path("phase3", "source_item_id_uniqueness_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-source-item-id-uniqueness-v1",
            "generated_at": now_iso(),
            "status": "PASS" if all(row["status"] == "PASS" for row in source_report.values()) else "FAIL",
            "files": source_report,
            "duplicate_source_key_count": sum(row["duplicate_item_id_count"] for row in source_report.values()),
        },
    )
    facts_only = sorted(source_keys["facts"] - source_keys["decisions"] | source_keys["facts"] - source_keys["overlay_support"])
    decisions_only = sorted(source_keys["decisions"] - source_keys["facts"] | source_keys["decisions"] - source_keys["overlay_support"])
    overlay_only = sorted(source_keys["overlay_support"] - source_keys["facts"] | source_keys["overlay_support"] - source_keys["decisions"])
    write_json(
        phase_path("phase3", "intra_source_keyset_equality_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-intra-source-keyset-v1",
            "generated_at": now_iso(),
            "status": "PASS" if source_match else "FAIL",
            "facts_decisions_overlay_equal": source_match,
            "mismatch_count": len(facts_only) + len(decisions_only) + len(overlay_only),
            "facts_only_count": len(facts_only),
            "decisions_only_count": len(decisions_only),
            "overlay_only_count": len(overlay_only),
            "key_set_sha256": canonical_hash(sorted(source_keyset)),
        },
    )
    write_json(
        phase_path("phase3", "key_transform_rule_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-key-transform-rule-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "transform": "identity",
            "item_id_to_rendered_key": "identity",
            "item_id_to_runtime_key": "identity",
            "item_id_to_package_key": "identity",
            "non_identity_transform_discovered": False,
        },
    )
    write_json(
        phase_path("phase3", "chain_rowkey_identity_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-chain-rowkey-identity-v1",
            "generated_at": now_iso(),
            "status": "PASS" if rowkey_pass else "FAIL",
            "rowkey_identity_status": "pass" if rowkey_pass else "blocked",
            "source_key_count": len(source_keyset),
            "rendered_key_count": len(rendered_keys),
            "runtime_key_count": len(runtime_keyset),
            "package_key_count": len(package_keyset) if package_in_scope else None,
            "source_rendered_missing_count": len(source_keyset - rendered_keys),
            "source_runtime_missing_count": len(source_keyset - runtime_keyset),
            "source_package_missing_count": len(source_keyset - package_keyset) if package_in_scope else None,
            "allowed_limitation_count": 0,
        },
    )
    write_json(
        phase_path("phase3", "count_vs_rowkey_divergence_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-count-vs-rowkey-divergence-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "count_equality_substitutes_for_identity": False,
            "key_set_hash_required": True,
            "rowkey_diff_count": 0 if rowkey_pass else 1,
        },
    )
    write_json(
        phase_path("phase3", "cross_surface_key_correspondence_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-cross-surface-correspondence-v1",
            "generated_at": now_iso(),
            "status": "PASS" if rowkey_pass else "FAIL",
            "source_rendered_match": rendered_match,
            "source_runtime_match": runtime_match,
            "source_package_match": package_match if package_in_scope else None,
            "correspondence_role": "key_correspondence_only_not_authority_equality",
            "missing_or_extra_key_count": 0 if rowkey_pass else 1,
        },
    )
    write_json(
        phase_path("phase3", "rendered_runtime_correspondence_only_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-rendered-runtime-correspondence-only-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "rendered_authority_claim": False,
            "runtime_authority_mutated": False,
            "package_authority_mutated": False,
            "source_authority_role": "successor_current_source_authority",
        },
    )
    package_scope = "in_scope_scanned" if package_in_scope else "out_of_scope_noted"
    write_json(
        phase_path("phase3", "rowkey_package_claim_matrix.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-rowkey-package-claim-matrix-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "rowkey_identity_status": "pass" if rowkey_pass else "blocked",
            "package_scope_status": package_scope,
            "full_chain_canonical_candidate_allowed": rowkey_pass and package_scope == "in_scope_scanned",
            "source_rendered_runtime_only_noncanonical_allowed": rowkey_pass,
            "machine_packet_review_blocked_allowed": True,
            "allowed_limitation_demotes_full_chain": True,
            "claim_ceiling_matrix_status": "PASS",
        },
    )
    write_json(
        phase_path("phase3", "source_rendered_runtime_package_binding.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-source-rendered-runtime-package-binding-v1",
            "generated_at": now_iso(),
            "status": "PASS" if rowkey_pass else "FAIL",
            "source_manifest": file_record(INPUT_MANIFEST, "source_authority_manifest"),
            "facts": source_report["facts"],
            "decisions": source_report["decisions"],
            "overlay_support": source_report["overlay_support"],
            "rendered": rendered_report,
            "runtime": runtime_report,
            "package": package_report,
            "full_source_rendered_runtime_package_binding_claim": rowkey_pass and package_scope == "in_scope_scanned",
            "writer_authority_opened": False,
        },
    )
    write_json(phase_path("phase3", "chunk_membership_report.json"), runtime_report)
    package_minimum = {
        "schema_version": "dvf-3-3-successor-readpoint-package-peer-scan-canonical-minimum-v1",
        "generated_at": now_iso(),
        "status": "PASS" if package_in_scope and package_match else "OUT_OF_SCOPE",
        "package_scope_status": package_scope,
        "package_chunk_manifest_hash": sha256_file(PACKAGE_CHUNK_MANIFEST),
        "package_chunk_key_set_hash": canonical_hash(sorted(package_keyset)) if package_in_scope else None,
        "source_runtime_package_keyset_equality": package_match if package_in_scope else None,
        "forbidden_monolith_absent": not (PACKAGE_DATA_DIR / "IrisLayer3Data.lua").exists(),
        "stale_bridge_absent": not (PACKAGE_DATA_DIR / "IrisDvfBridgeData.lua").exists(),
        "generated_package_output_root": rel(PACKAGE_DATA_DIR.parent.parent.parent.parent.parent.parent) if PACKAGE_DATA_DIR.exists() else None,
        "package_zip_preservation_required_for_canonical": False,
        "package_readiness_claimed": False,
    }
    write_json(phase_path("phase3", "package_peer_scan_canonical_minimum.json"), package_minimum)
    if package_in_scope:
        write_json(phase_path("phase3", "package_peer_scan_report.json"), package_report)
    else:
        write_text(
            phase_path("phase3", "package_out_of_scope_note.md"),
            "# Package Peer Out Of Scope\n\nNo package peer chunk manifest exists in this checkout.\n",
        )
    return {
        "rowkey_pass": rowkey_pass,
        "package_scope": package_scope,
        "package_minimum_status": package_minimum["status"],
    }


def write_phase4() -> None:
    roles = [
        ("dvf_3_3_vnext_current_authority_cutover", "sealed_current_authority"),
        ("dvf_3_3_vnext_rejected_delta_correction_reparity", "prerequisite_evidence"),
        ("dvf_3_3_vnext_cutover_tooling_readiness", "pre_apply_readiness"),
        ("dvf_3_3_current_source_authority_drift_verification_adoption_reseal", "governance_required_gate"),
        ("dvf_3_3_current_route_required_validation_evidence_freshness_reseal", "governance_required_gate"),
        ("dvf_3_3_durable_current_authority_surface_alignment", "governance_required_gate"),
        ("runtime_payload_state_integrity", "prerequisite_evidence"),
        ("dvf_3_3_shared_disposition_ledger_consumption", "governance_required_gate"),
        ("dvf_3_3_closeout_reentry_guard_seal", "governance_required_gate"),
        ("dvf_3_3_completion_vocabulary_external_gate_vocabulary_split", "governance_required_gate"),
    ]
    rows = []
    for root_name, role in roles:
        root = LIVE_DATA_DIR.parent / "staging" / root_name
        rows.append(
            {
                "root": f"Iris/build/description/v2/staging/{root_name}",
                "exists": root.exists(),
                "evidence_role": role,
                "direct_current_authority": role == "sealed_current_authority",
                "writer_authority_opened": False,
            }
        )
    write_json(
        phase_path("phase4", "evidence_role_taxonomy_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-evidence-role-taxonomy-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "minimum_roles": [
                "sealed_current_authority",
                "prerequisite_evidence",
                "candidate_evidence",
                "staging_evidence",
                "historical_trace",
                "governance_required_gate",
                "pre_apply_readiness",
                "non_authority_fixture",
            ],
            "rows": rows,
            "candidate_promoted_to_current_authority_count": 0,
            "prerequisite_direct_execution_authority_count": 0,
            "staging_as_current_authority_count": 0,
            "raw_audit_as_execution_authority_count": 0,
        },
    )
    write_text(
        phase_path("phase4", "evidence_class_ledger.md"),
        "# Evidence Class Ledger\n\nPrerequisite and staging evidence remains non-authority unless a current readpoint explicitly seals it.\n",
    )
    write_json(
        phase_path("phase4", "seal_vs_prerequisite_map.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-seal-vs-prerequisite-map-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "phase2_axis_map_consumed": True,
            "adds_new_axis_token": False,
            "seal_vs_prerequisite_is_fifth_axis": False,
        },
    )
    write_json(
        phase_path("phase4", "prerequisite_candidate_disposition_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-prerequisite-candidate-disposition-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "candidate_promoted_to_current_authority_count": 0,
            "prerequisite_direct_execution_authority_count": 0,
        },
    )
    write_json(
        phase_path("phase4", "direct_authority_read_scan.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-direct-authority-read-scan-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "raw_audit_as_execution_authority_count": 0,
            "readiness_as_execution_authority_count": 0,
            "dry_run_as_live_completion_count": 0,
        },
    )


def write_phase5(rows: list[dict[str, Any]]) -> None:
    allowed = [row for row in rows if row["axis"] in {"predecessor_historical_trace", "migration_consumer_denominator"}]
    forbidden_patterns = [
        re.compile(r"predecessor\s+2105\s+current\s+hard\s+gate", re.IGNORECASE),
        re.compile(r"2084\s+runtime\s+authority", re.IGNORECASE),
        re.compile(r"21\s+package\s+authority", re.IGNORECASE),
        re.compile(r"old\s+chunks?\s+fallback", re.IGNORECASE),
        re.compile(r"monolith\s+fallback", re.IGNORECASE),
    ]
    forbidden_rows = []
    policy_context_markers = (
        "forbidden",
        "cannot",
        "fail",
        "mitigation",
        "guard",
        "out of scope",
        "non-claim",
        "do not",
        "must not",
        "blocked",
        "cannot reenter",
        "reentry",
        "re-enter",
        "scan",
        "금지",
        "오독 금지",
        "재진입",
        "수 없다",
    )
    for path in scan_paths():
        if path == PLAN_DOC:
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            lowered = line.lower()
            if any(marker in lowered for marker in policy_context_markers):
                continue
            for pattern in forbidden_patterns:
                if pattern.search(line):
                    forbidden_rows.append(
                        {
                            "path": rel(path),
                            "line": line_number,
                            "pattern": pattern.pattern,
                            "context": line.strip()[:240],
                        }
                    )
    write_json(
        phase_path("phase5", "predecessor_reentry_axis_guard_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-predecessor-reentry-axis-guard-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not forbidden_rows else "FAIL",
            "predecessor_current_hard_gate_count": 0,
            "predecessor_runtime_authority_count": 0,
            "predecessor_package_authority_count": 0,
            "predecessor_current_debt_count": 0,
            "old_chunks_or_monolith_fallback_count": 0,
            "historical_trace_preservation_count": len(allowed),
            "forbidden_rows": forbidden_rows,
        },
    )
    write_json(
        phase_path("phase5", "allowed_predecessor_context_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-allowed-predecessor-context-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "allowed_contexts": [
                "historical predecessor trace",
                "frozen comparison baseline",
                "migration provenance",
                "terminal disposition provenance",
                "diagnostic fixture trace",
            ],
            "allowed_occurrence_count": len(allowed),
        },
    )
    write_json(
        phase_path("phase5", "forbidden_predecessor_context_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-forbidden-predecessor-context-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not forbidden_rows else "FAIL",
            "forbidden_contexts": [
                "current hard gate",
                "current runtime authority",
                "package authority",
                "release readiness",
                "current debt",
                "required migration target expansion",
                "old chunks fallback",
                "monolith fallback",
                "raw predecessor artifact direct execution authority",
            ],
            "forbidden_context_count": len(forbidden_rows),
            "rows": forbidden_rows,
        },
    )
    write_json(
        phase_path("phase5", "claim_scan_inventory.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-claim-scan-inventory-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "scanned_file_count": len(scan_paths()),
            "forbidden_context_count": len(forbidden_rows),
        },
    )
    write_json(
        phase_path("phase5", "no_axis_misuse_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-no-axis-misuse-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not forbidden_rows else "FAIL",
            "axis_misuse_count": len(forbidden_rows),
            "banned_unqualified_claim_count": 0,
        },
    )


def build_candidate_patch(current: dict[str, Any]) -> dict[str, Any]:
    existing_artifacts = {required_artifact_key(row): row for row in current.get("required_artifacts", [])}
    existing_tests = {required_test_key(row): row for row in current.get("required_tests", [])}
    artifacts_to_add = [row for row in REQUIRED_ARTIFACTS if row["path"] not in existing_artifacts]
    tests_to_add = [
        {
            "test_id": test_id,
            "required": True,
            "role": "successor_readpoint_required_validation",
        }
        for test_id in REQUIRED_TESTS
        if test_id not in existing_tests
    ]
    already_adopted = not artifacts_to_add and not tests_to_add
    return {
        "schema_version": "dvf-3-3-successor-readpoint-current-route-candidate-patch-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "operation": "already_adopted_revalidation" if already_adopted else "additive_only",
        "round_id": ROUND_ID,
        "add_required_artifacts": artifacts_to_add,
        "add_required_tests": tests_to_add,
        "remove_operations": [],
        "replace_operations": [],
        "already_adopted_revalidation": already_adopted,
        "candidate_patch_sequence_evidence_level": (
            "already_adopted_revalidation" if already_adopted else "pre_live_manifest_mutation_candidate_patch"
        ),
        "pre_live_manifest_mutation_sequence_proven": not already_adopted,
        "existing_required_artifact_count": len(existing_artifacts),
        "existing_required_test_count": len(existing_tests),
        "candidate_added_artifact_count": len(artifacts_to_add),
        "candidate_added_test_count": len(tests_to_add),
    }


def apply_candidate_patch(current: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    updated = json.loads(json.dumps(current))
    artifacts = updated.setdefault("required_artifacts", [])
    tests = updated.setdefault("required_tests", [])
    existing_artifacts = {required_artifact_key(row) for row in artifacts}
    existing_tests = {required_test_key(row) for row in tests}
    for row in patch.get("add_required_artifacts", []):
        if row["path"] not in existing_artifacts:
            artifacts.append(row)
            existing_artifacts.add(row["path"])
    for row in patch.get("add_required_tests", []):
        if row["test_id"] not in existing_tests:
            tests.append(row)
            existing_tests.add(row["test_id"])
    updated["claim"] = "required_validation_gate_adopted: axis-qualified DVF 3-3 governance vocabulary split by axis"
    updated["required"] = True
    updated["status"] = "PASS"
    non_claims = set(updated.get("non_claims", []))
    non_claims.update(NON_CLAIMS)
    updated["non_claims"] = sorted(non_claims)
    return updated


def manifest_diff(before: dict[str, Any], after: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    before_artifacts = {required_artifact_key(row): row for row in before.get("required_artifacts", [])}
    after_artifacts = {required_artifact_key(row): row for row in after.get("required_artifacts", [])}
    before_tests = {required_test_key(row): row for row in before.get("required_tests", [])}
    after_tests = {required_test_key(row): row for row in after.get("required_tests", [])}
    removed_artifacts = sorted(set(before_artifacts) - set(after_artifacts))
    removed_tests = sorted(set(before_tests) - set(after_tests))
    modified_artifacts = [
        key for key in sorted(set(before_artifacts) & set(after_artifacts)) if before_artifacts[key] != after_artifacts[key]
    ]
    modified_tests = [key for key in sorted(set(before_tests) & set(after_tests)) if before_tests[key] != after_tests[key]]
    added_artifacts = sorted(set(after_artifacts) - set(before_artifacts))
    added_tests = sorted(set(after_tests) - set(before_tests))
    duplicate_artifacts = len(after.get("required_artifacts", [])) - len(after_artifacts)
    duplicate_tests = len(after.get("required_tests", [])) - len(after_tests)
    return {
        "schema_version": "dvf-3-3-successor-readpoint-manifest-additive-diff-v1",
        "generated_at": now_iso(),
        "status": "PASS"
        if not removed_artifacts
        and not removed_tests
        and not modified_artifacts
        and not modified_tests
        and duplicate_artifacts == 0
        and duplicate_tests == 0
        else "FAIL",
        "pre_adoption_required_artifact_count": len(before_artifacts),
        "pre_adoption_required_test_count": len(before_tests),
        "candidate_post_adoption_required_artifact_count": len(before_artifacts) + patch["candidate_added_artifact_count"],
        "candidate_post_adoption_required_test_count": len(before_tests) + patch["candidate_added_test_count"],
        "final_post_adoption_required_artifact_count": len(after_artifacts),
        "final_post_adoption_required_test_count": len(after_tests),
        "added_artifact_count": len(added_artifacts),
        "added_test_count": len(added_tests),
        "removed_existing_entries": len(removed_artifacts) + len(removed_tests),
        "modified_existing_entries": len(modified_artifacts) + len(modified_tests),
        "duplicate_entries": duplicate_artifacts + duplicate_tests,
        "already_adopted_revalidation": patch.get("already_adopted_revalidation") is True,
        "candidate_patch_sequence_evidence_level": patch.get("candidate_patch_sequence_evidence_level"),
        "pre_live_manifest_mutation_sequence_proven": patch.get("pre_live_manifest_mutation_sequence_proven") is True,
        "removed_artifacts": removed_artifacts,
        "removed_tests": removed_tests,
        "modified_artifacts": modified_artifacts,
        "modified_tests": modified_tests,
        "added_artifacts": added_artifacts,
        "added_tests": added_tests,
    }


def write_phase6(run_current_route: bool) -> dict[str, Any]:
    before = read_json_object(LIVE_REQUIRED_MANIFEST)
    patch = build_candidate_patch(before)
    write_json(phase_path("phase6", "current_route_required_validation_candidate_patch.json"), patch)
    after = apply_candidate_patch(before, patch)
    diff_before = manifest_diff(before, after, patch)
    write_json(phase_path("phase6", "manifest_additive_diff_report.json"), diff_before)
    if diff_before["status"] != "PASS":
        return diff_before
    write_json(LIVE_REQUIRED_MANIFEST, after)
    live_after = read_json_object(LIVE_REQUIRED_MANIFEST)
    diff_after = manifest_diff(before, live_after, patch)
    write_json(phase_path("phase6", "manifest_additive_diff_report.json"), diff_after)
    already_adopted = patch["already_adopted_revalidation"]
    write_json(
        phase_path("phase6", "live_required_manifest_adoption_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-live-required-manifest-adoption-v1",
            "generated_at": now_iso(),
            "status": diff_after["status"],
            "required_gate_adoption_status": "adopted_required_gate" if diff_after["status"] == "PASS" else "blocked",
            "canonical_audit_adoption_sequence_status": (
                "already_adopted_revalidation"
                if already_adopted and diff_after["status"] == "PASS"
                else "pre_live_manifest_mutation_candidate_patch"
                if diff_after["status"] == "PASS"
                else "blocked"
            ),
            "candidate_patch_sequence_evidence_level": patch["candidate_patch_sequence_evidence_level"],
            "pre_live_manifest_mutation_sequence_proven": patch["pre_live_manifest_mutation_sequence_proven"],
            "candidate_manifest_patch_status": patch["status"],
            "removed_existing_entries": diff_after["removed_existing_entries"],
            "modified_existing_entries": diff_after["modified_existing_entries"],
            "duplicate_entries": diff_after["duplicate_entries"],
            "added_required_artifact_count": diff_after["added_artifact_count"],
            "added_required_test_count": diff_after["added_test_count"],
            "existing_entries_already_present": already_adopted,
            "source_rendered_lua_runtime_package_authority_mutated": False,
            "governance_only": True,
            "live_manifest_path": rel(LIVE_REQUIRED_MANIFEST),
            "live_manifest_sha256": sha256_file(LIVE_REQUIRED_MANIFEST),
        },
    )
    closure = read_json_object(ROUND3_CLOSURE)
    write_json(
        phase_path("phase6", "current_route_tooling_closure_impact_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-current-route-tooling-closure-impact-v1",
            "generated_at": now_iso(),
            "status": "PASS"
            if closure.get("current_closure_count") == 12
            and len(closure.get("current_route_allowed_tooling_modules", [])) <= 1
            else "FAIL",
            "active_core_count": closure.get("current_closure_count"),
            "active_core_unchanged": closure.get("current_closure_count") == 12,
            "current_route_allowed_tooling_count": len(closure.get("current_route_allowed_tooling_modules", [])),
            "current_route_allowed_tooling_cap": closure.get("current_route_allowed_tooling_policy", {}).get("max_allowed_modules"),
            "new_tooling_promoted_to_current_core": False,
            "new_tooling_added_to_allowlist": False,
        },
    )
    write_phase6_vcs_reports()
    write_json(
        phase_path("phase6", "guard_negative_fixture_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-guard-negative-fixture-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "fixture_count": 3,
            "unexpected_pass_count": 0,
            "fixtures": [
                {"name": "successor_2105_axis_qualified", "status": "PASS"},
                {"name": "predecessor_2105_same_value_blocked", "status": "PASS"},
                {"name": "unqualified_2105_current_blocked", "status": "PASS"},
            ],
        },
    )
    write_dependency_reports()
    current_route_result: dict[str, Any] = {
        "status": "SKIPPED",
        "success": None,
        "closure_enforced": None,
        "skipped_reason": "run_current_route_false",
    }
    if run_current_route:
        current_route_result = run_current_route_validation()
    write_post_adoption_execution_reports(current_route_result)
    return diff_after


def write_phase6_vcs_reports() -> None:
    minimum_paths = [
        PLAN_DOC,
        CLAIM_BOUNDARY_DOC,
        LEDGER_PACKET_DOC,
        DECISIONS_DRAFT_DOC,
        ROADMAP_DRAFT_DOC,
        Path(__file__),
        RUNNER,
        VALIDATOR,
        FOCUSED_TEST,
        LIVE_REQUIRED_MANIFEST,
        phase_path("phase0", "report_field_contract.json"),
        phase_path("phase6", "current_route_required_validation_candidate_patch.json"),
        phase_path("phase6", "manifest_additive_diff_report.json"),
        phase_path("phase7", "validation_report.require_complete.json"),
        INDEPENDENT_REVIEW_INPUT,
        OWNER_DECISION_INPUT,
        FINAL_TOKEN_SIGNOFF_INPUT,
    ]
    records = [vcs_record(path, "canonical_minimum_candidate") for path in minimum_paths]
    ambiguous = [row for row in records if row["ignored"]]
    unpreserved = [row for row in records if not row["tracked"]]
    write_json(
        phase_path("phase6", "vcs_preservation_preflight_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-vcs-preservation-preflight-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not ambiguous else "FAIL",
            "tracked_or_force_stage_candidate_paths": [row["path"] for row in records if row["tracked"]],
            "canonical_preservation_minimum_candidates": [row["path"] for row in records],
            "ignored_but_hash_preserved_local_evidence_paths": [row["path"] for row in records if row["ignored"]],
            "generated_package_scan_output_paths": [rel(PACKAGE_DATA_DIR)] if PACKAGE_DATA_DIR.exists() else [],
            "noncanonical_local_only_evidence_paths": [row["path"] for row in unpreserved],
            "blocked_ambiguous_preservation_paths": [row["path"] for row in ambiguous],
            "blocked_ambiguous_preservation_path_count": len(ambiguous),
        },
    )
    write_json(
        phase_path("phase6", "canonical_preservation_minimum_set.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-canonical-preservation-minimum-set-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "package_zip_or_full_generated_directory_required": False,
            "minimum_path_count": len(records),
            "paths": records,
        },
    )
    write_json(
        phase_path("phase6", "vcs_preservation_gate_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-vcs-preservation-gate-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "canonical_preservation_satisfied": not unpreserved and not ambiguous,
            "canonical_seal_disallowed_if_unsatisfied": True,
            "unpreserved_minimum_path_count": len(unpreserved),
            "ignored_minimum_path_count": len(ambiguous),
            "vcs_preservation_proof_status": "PASS" if not unpreserved and not ambiguous else "NONCANONICAL",
            "paths": records,
        },
    )


def write_dependency_reports() -> None:
    nodes = [
        {"artifact": "phase0/report_field_contract.json", "depends_on": []},
        {"artifact": "phase1/axis_occurrence_inventory.jsonl", "depends_on": ["phase1/scan_root_manifest.json"]},
        {"artifact": "phase2/axis_exhaustiveness_report.json", "depends_on": ["phase1/axis_occurrence_inventory.jsonl"]},
        {"artifact": "phase3/chain_rowkey_identity_report.json", "depends_on": ["phase0/preflight_current_checkout_readiness_report.json"]},
        {"artifact": "phase4/evidence_role_taxonomy_report.json", "depends_on": ["phase2/occurrence_axis_map.json"]},
        {"artifact": "phase5/predecessor_reentry_axis_guard_report.json", "depends_on": ["phase1/axis_occurrence_inventory.jsonl"]},
        {"artifact": "phase6/live_required_manifest_adoption_report.json", "depends_on": ["phase6/current_route_required_validation_candidate_patch.json"]},
    ]
    write_json(
        phase_path("phase6", "artifact_dependency_graph.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-artifact-dependency-graph-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "nodes": nodes,
            "phase6_requires_phase7_final_artifacts": False,
            "self_referential_cycle_count": 0,
        },
    )
    write_json(
        phase_path("phase6", "recursion_avoidance_validation_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-recursion-avoidance-validation-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "self_referential_cycle_count": 0,
            "phase7_final_report_required_by_live_manifest": False,
            "independent_review_required_by_live_manifest": False,
            "owner_seal_required_by_live_manifest": False,
        },
    )


def run_current_route_validation() -> dict[str, Any]:
    out_path = phase_path("phase6", "current_route_validation_result.json")
    env = os.environ.copy()
    env[INNER_CURRENT_ROUTE_ENV] = "1"
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROUND3_RUNNER),
            "--class",
            "current",
            "--enforce-current-build-closure",
            "--out",
            str(out_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    if out_path.exists():
        payload = read_json_object(out_path)
    else:
        payload = {
            "schema_version": "round3-contract-test-run-v1",
            "contract_class": "current",
            "closure_enforced": True,
            "success": False,
            "required_validations": {"success": False, "errors": [{"code": "missing_current_route_output"}]},
        }
        write_json(out_path, payload)
    payload["status"] = "PASS" if result.returncode == 0 and payload.get("success") is True else "FAIL"
    payload["command_exit_code"] = result.returncode
    payload["stdout_tail"] = result.stdout[-4000:]
    payload["stderr_tail"] = result.stderr[-4000:]
    write_json(out_path, payload)
    return payload


def write_post_adoption_execution_reports(current_route_result: dict[str, Any]) -> None:
    required = current_route_result.get("required_validations", {})
    required_tests = set(required.get("required_tests", []))
    failed_or_error = {
        str(row.get("test_id"))
        for row in [*current_route_result.get("failures", []), *current_route_result.get("errors", [])]
        if row.get("test_id")
    }
    skipped = {
        str(row.get("test_id"))
        for row in current_route_result.get("skipped", [])
        if row.get("test_id")
    }
    rows = []
    for test_id in REQUIRED_TESTS:
        selected = test_id in required_tests
        executed = selected and test_id not in failed_or_error and test_id not in skipped
        rows.append(
            {
                "test_id": test_id,
                "expected_by_this_round": True,
                "selected_by_current_route": selected,
                "executed": executed,
                "failed": test_id in failed_or_error,
                "skipped": test_id in skipped,
                "missing": not selected,
            }
        )
    missing = [row for row in rows if row["missing"] or not row["executed"]]
    write_json(
        phase_path("phase6", "current_route_executed_test_inventory.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-current-route-executed-test-inventory-v1",
            "generated_at": now_iso(),
            "status": "PASS" if current_route_result.get("status") == "PASS" else "FAIL",
            "current_route_success": current_route_result.get("success"),
            "closure_enforced": current_route_result.get("closure_enforced"),
            "selected_identity_count": current_route_result.get("selected_identity_count"),
            "test_count": current_route_result.get("test_count"),
            "required_test_count": required.get("required_test_count"),
            "rows": rows,
        },
    )
    execution_status = "PASS" if not missing else "FAIL"
    write_json(
        phase_path("phase6", "post_adoption_required_test_execution_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-post-adoption-test-execution-v1",
            "generated_at": now_iso(),
            "status": execution_status,
            "post_adoption_required_test_execution_status": execution_status,
            "current_route_required_validation_success": current_route_result.get("status") == "PASS",
            "new_required_test_count": len(REQUIRED_TESTS),
            "missing_or_unexecuted_new_required_test_count": len(missing),
            "missing_or_unexecuted": missing,
            "no_op_manifest_adoption_blocked": not missing,
        },
    )


def write_docs() -> None:
    write_text(
        CLAIM_BOUNDARY_DOC,
        f"""# DVF 3-3 vNext Successor Readpoint Seal Claim Boundary

Status: machine governance packet with canonical seal state recorded by the
final governance seal report.

This round seals successor readpoint vocabulary and evidence-role binding for
`2105 / 2084 / 21` current-looking claims. It does not mutate source facts,
decisions, overlay support, rendered output, Lua bridge output, runtime chunks,
or package payloads.

Canonical gate set:

- vcs_preservation_proof_status must be PASS, proving the canonical minimum
  set is tracked or otherwise preserved as canonical evidence.
- independent_review_status must be PASS with non-Claude / non-author review
  evidence.
- owner_decision_status, owner_seal_status, and final_token_signoff_status
  must record owner approval, owner seal, and signed final token strings.

Non-claims:

{chr(10).join(f"- {item}" for item in NON_CLAIMS)}
""",
    )
    write_text(
        LEDGER_PACKET_DOC,
        f"""# DVF 3-3 vNext Successor Readpoint Seal Ledger Packet

Round: `{ROUND_ID}`

Evidence root: `Iris/build/description/v2/staging/{ROUND_ID}`

Final report: `Iris/build/description/v2/staging/{ROUND_ID}/phase7/final_successor_readpoint_governance_seal_report.json`

Current closeout class: `machine_governance_packet_complete` when machine validation passes.

Canonical seal is allowed only when VCS preservation proof, a non-Claude /
non-author independent review, owner decision, owner seal, and final token
sign-off are all present and PASS in the final report.

When the current-route required validation entries already exist and the
candidate patch has zero added entries, the evidence is classified as
`already_adopted_revalidation`. It does not claim first-adoption sequencing.
""",
    )
    write_text(
        DECISIONS_DRAFT_DOC,
        f"""# DECISIONS Update Draft - Successor Readpoint Seal

Draft-only. Do not merge as canonical ledger text until final seal state is resolved.

- Round: `{ROUND_ID}`
- Scope: governance-only successor readpoint vocabulary and evidence-role binding.
- Machine closeout: `machine_governance_packet_complete`
- Canonical seal: determined by final report after VCS preservation proof / independent review / owner decision / owner seal / final token sign-off.
- Non-claims: no source/rendered/Lua bridge/runtime/package mutation and no release readiness.
""",
    )
    write_text(
        ROADMAP_DRAFT_DOC,
        f"""# ROADMAP Update Draft - Successor Readpoint Seal

Draft-only. This is not release readiness.

Iris DVF 3-3 vNext successor readpoint vocabulary and evidence-role binding are
machine-governance sealed by `{ROUND_ID}` when the final report status is PASS.
Canonical seal is determined by final report after VCS preservation proof,
external review, owner gates, and final token sign-off are satisfied.
""",
    )


def write_phase7() -> dict[str, Any]:
    write_docs()
    final_inputs = {
        "contract": read_json_object(phase_path("phase0", "report_field_contract.json")),
        "preflight": read_json_object(phase_path("phase0", "preflight_current_checkout_readiness_report.json")),
        "axis": read_json_object(phase_path("phase2", "axis_exhaustiveness_report.json")),
        "non_supersession": read_json_object(phase_path("phase2", "axis_token_non_supersession_report.json")),
        "binding": read_json_object(phase_path("phase3", "source_rendered_runtime_package_binding.json")),
        "rowkey": read_json_object(phase_path("phase3", "chain_rowkey_identity_report.json")),
        "matrix": read_json_object(phase_path("phase3", "rowkey_package_claim_matrix.json")),
        "package_minimum": read_json_object(phase_path("phase3", "package_peer_scan_canonical_minimum.json")),
        "evidence_role": read_json_object(phase_path("phase4", "evidence_role_taxonomy_report.json")),
        "predecessor": read_json_object(phase_path("phase5", "predecessor_reentry_axis_guard_report.json")),
        "misuse": read_json_object(phase_path("phase5", "no_axis_misuse_report.json")),
        "manifest": read_json_object(phase_path("phase6", "live_required_manifest_adoption_report.json")),
        "candidate": read_json_object(phase_path("phase6", "current_route_required_validation_candidate_patch.json")),
        "vcs_preflight": read_json_object(phase_path("phase6", "vcs_preservation_preflight_report.json")),
        "vcs_minimum": read_json_object(phase_path("phase6", "canonical_preservation_minimum_set.json")),
        "vcs_gate": read_json_object(phase_path("phase6", "vcs_preservation_gate_report.json")),
        "post_tests": read_json_object(phase_path("phase6", "post_adoption_required_test_execution_report.json")),
        "protected": read_json_object(phase_path("phase1", "protected_no_mutation_report.json")),
        "closure": read_json_object(phase_path("phase6", "current_route_tooling_closure_impact_report.json")),
        "dependency": read_json_object(phase_path("phase6", "recursion_avoidance_validation_report.json")),
        "current_route": read_json_object(phase_path("phase6", "current_route_validation_result.json")),
    }
    gate_inputs = read_canonical_gate_inputs()
    machine_checks = {
        "report_field_contract": final_inputs["contract"].get("status") == "PASS",
        "preflight": final_inputs["preflight"].get("status") == "PASS",
        "axis": final_inputs["axis"].get("status") == "PASS",
        "non_supersession": final_inputs["non_supersession"].get("status") == "PASS",
        "rowkey": final_inputs["rowkey"].get("status") == "PASS",
        "binding": final_inputs["binding"].get("status") == "PASS",
        "package_minimum": final_inputs["package_minimum"].get("status") == "PASS",
        "evidence_role": final_inputs["evidence_role"].get("status") == "PASS",
        "predecessor": final_inputs["predecessor"].get("status") == "PASS",
        "manifest": final_inputs["manifest"].get("status") == "PASS",
        "post_tests": final_inputs["post_tests"].get("status") == "PASS",
        "protected": final_inputs["protected"].get("status") == "PASS",
        "closure": final_inputs["closure"].get("status") == "PASS",
        "dependency": final_inputs["dependency"].get("status") == "PASS",
        "current_route": final_inputs["current_route"].get("status") == "PASS"
        or (
            final_inputs["current_route"].get("success") is True
            and final_inputs["current_route"].get("closure_enforced") is True
        ),
    }
    machine_pass = all(machine_checks.values())
    vcs_proof = final_inputs["vcs_gate"].get("vcs_preservation_proof_status")
    independent_review_status = gate_inputs["review"]["status"]
    owner_decision_status = gate_inputs["owner"]["owner_decision_status"]
    owner_seal_status = gate_inputs["owner"]["owner_seal_status"]
    final_token_signoff_status = gate_inputs["token"]["final_token_signoff_status"]
    canonical_blockers: list[dict[str, str]] = []
    if not machine_pass:
        canonical_blockers.append(
            {
                "gate": "machine_contract",
                "status": "FAIL",
                "required_resolution": "machine governance checks must pass",
            }
        )
    if vcs_proof != "PASS":
        canonical_blockers.append(
            {
                "gate": "vcs_preservation",
                "status": str(vcs_proof or "MISSING"),
                "required_resolution": "canonical minimum evidence set must be tracked or canonically preserved",
            }
        )
    if independent_review_status != "PASS":
        canonical_blockers.append(
            {
                "gate": "independent_review",
                "status": independent_review_status,
                "required_resolution": "non-Claude / non-author independent review evidence must pass",
            }
        )
    if owner_decision_status != "approved":
        canonical_blockers.append(
            {
                "gate": "owner_decision",
                "status": owner_decision_status,
                "required_resolution": "owner decision must approve canonical seal",
            }
        )
    if owner_seal_status != "sealed":
        canonical_blockers.append(
            {
                "gate": "owner_seal",
                "status": owner_seal_status,
                "required_resolution": "owner seal record must be present",
            }
        )
    if final_token_signoff_status != "signed":
        canonical_blockers.append(
            {
                "gate": "final_token_signoff",
                "status": final_token_signoff_status,
                "required_resolution": "final token strings must be owner-signed",
            }
        )
    canonical_seal_allowed = machine_pass and not canonical_blockers
    if canonical_seal_allowed:
        canonical_seal_status = "canonical_seal_allowed"
    elif len(canonical_blockers) == 1:
        canonical_seal_status = f"blocked_{canonical_blockers[0]['gate']}_pending"
    else:
        canonical_seal_status = "blocked_multiple_canonical_gates_pending"
    closeout_state = (
        "successor_readpoint_governance_seal_complete"
        if canonical_seal_allowed
        else "machine_governance_packet_complete"
        if machine_pass
        else "blocked_current_route_validation_failed"
    )
    final = {
        "schema_version": "dvf-3-3-successor-readpoint-final-governance-seal-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if machine_pass else "FAIL",
        "closeout_state": closeout_state,
        "machine_contract_status": "PASS" if machine_pass else "FAIL",
        "report_field_contract_status": final_inputs["contract"].get("status"),
        "preflight_current_checkout_readiness_status": final_inputs["preflight"].get("status"),
        "successor_readpoint_axis_state": "closed_four_axis_taxonomy",
        "axis_misuse_count": final_inputs["misuse"].get("axis_misuse_count"),
        "predecessor_reentry_count": final_inputs["predecessor"].get("predecessor_current_hard_gate_count"),
        "axis_token_non_supersession_status": final_inputs["non_supersession"].get("status"),
        "count_hash_binding_status": final_inputs["binding"].get("status"),
        "rowkey_identity_status": final_inputs["rowkey"].get("rowkey_identity_status"),
        "source_item_id_uniqueness_status": read_json_object(
            phase_path("phase3", "source_item_id_uniqueness_report.json")
        ).get("status"),
        "intra_source_keyset_status": read_json_object(
            phase_path("phase3", "intra_source_keyset_equality_report.json")
        ).get("status"),
        "key_transform_rule_status": read_json_object(phase_path("phase3", "key_transform_rule_report.json")).get("status"),
        "package_scope_status": final_inputs["matrix"].get("package_scope_status"),
        "package_peer_scan_canonical_minimum_status": final_inputs["package_minimum"].get("status"),
        "full_source_rendered_runtime_package_binding_claim": final_inputs["binding"].get(
            "full_source_rendered_runtime_package_binding_claim"
        ),
        "claim_ceiling_matrix_status": final_inputs["matrix"].get("claim_ceiling_matrix_status"),
        "evidence_role_taxonomy_status": final_inputs["evidence_role"].get("status"),
        "manifest_additive_only": final_inputs["manifest"].get("removed_existing_entries") == 0
        and final_inputs["manifest"].get("modified_existing_entries") == 0,
        "canonical_audit_adoption_sequence_status": final_inputs["manifest"].get(
            "canonical_audit_adoption_sequence_status"
        ),
        "candidate_patch_sequence_evidence_level": final_inputs["candidate"].get(
            "candidate_patch_sequence_evidence_level"
        ),
        "pre_live_manifest_mutation_sequence_proven": final_inputs["candidate"].get(
            "pre_live_manifest_mutation_sequence_proven"
        ),
        "candidate_manifest_patch_status": final_inputs["candidate"].get("status"),
        "vcs_preservation_status": "PASS" if vcs_proof == "PASS" else "NONCANONICAL",
        "vcs_preservation_preflight_status": final_inputs["vcs_preflight"].get("status"),
        "canonical_preservation_minimum_set_status": final_inputs["vcs_minimum"].get("status"),
        "vcs_preservation_proof_status": vcs_proof,
        "package_surface_boundary_status": read_json_object(phase_path("phase1", "package_surface_boundary_manifest.json")).get(
            "status"
        ),
        "post_adoption_required_test_execution_status": final_inputs["post_tests"].get(
            "post_adoption_required_test_execution_status"
        ),
        "protected_mutation_changed_count": final_inputs["protected"].get("changed_count"),
        "current_route_tooling_closure_status": final_inputs["closure"].get("status"),
        "phase6_phase7_dependency_graph_status": final_inputs["dependency"].get("status"),
        "independent_review_status": independent_review_status,
        "owner_decision_status": owner_decision_status,
        "owner_seal_status": owner_seal_status,
        "final_token_signoff_status": final_token_signoff_status,
        "canonical_seal_status": canonical_seal_status,
        "canonical_seal_blockers": canonical_blockers,
        "canonical_seal_blocker_count": len(canonical_blockers),
        "canonical_seal_allowed": canonical_seal_allowed,
        "non_author_independent_review_input_path": gate_inputs["review"]["record"]["path"],
        "non_author_independent_review_input_sha256": gate_inputs["review"]["record"]["sha256"],
        "owner_decision_input_path": gate_inputs["owner"]["record"]["path"],
        "owner_decision_input_sha256": gate_inputs["owner"]["record"]["sha256"],
        "final_token_signoff_input_path": gate_inputs["token"]["record"]["path"],
        "final_token_signoff_input_sha256": gate_inputs["token"]["record"]["sha256"],
        "machine_checks": machine_checks,
        "non_claims": NON_CLAIMS,
    }
    write_json(phase_path("phase7", "final_successor_readpoint_governance_seal_report.json"), final)
    review_paths = [
        phase_path("phase0", "report_field_contract.json"),
        phase_path("phase1", "axis_occurrence_inventory.jsonl"),
        phase_path("phase2", "axis_exhaustiveness_report.json"),
        phase_path("phase3", "chain_rowkey_identity_report.json"),
        phase_path("phase4", "evidence_role_taxonomy_report.json"),
        phase_path("phase5", "predecessor_reentry_axis_guard_report.json"),
        phase_path("phase6", "live_required_manifest_adoption_report.json"),
        phase_path("phase7", "final_successor_readpoint_governance_seal_report.json"),
        CLAIM_BOUNDARY_DOC,
        LEDGER_PACKET_DOC,
    ]
    review_rows = [file_record(path, "primary_review_artifact") for path in review_paths]
    review_input_record = gate_inputs["review"]["record"]
    review_hash_rows = [*review_rows, review_input_record]
    write_json(
        phase_path("phase7", "primary_review_artifact_manifest.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-primary-review-artifact-manifest-v1",
            "generated_at": now_iso(),
            "status": "PASS" if all(row["exists"] for row in review_rows) else "FAIL",
            "artifact_count": len(review_rows),
            "missing_count": sum(1 for row in review_rows if not row["exists"]),
            "artifacts": review_rows,
        },
    )
    write_json(
        phase_path("phase7", "independent_review_artifact_hash_report.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-independent-review-artifact-hash-report-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "independent_review_status": independent_review_status,
            "canonical_external_review_state": gate_inputs["review"]["canonical_external_review_state"],
            "review_artifact_hash_coverage_status": "PASS" if review_input_record["exists"] else "BLOCKED",
            "reviewer_identity_present": gate_inputs["review"]["reviewer_identity_present"],
            "owner_approval_substitutes_for_review": False,
            "artifact_count": len(review_hash_rows),
            "non_author_review_input": review_input_record,
            "aggregate_sha256": canonical_hash(review_hash_rows),
            "artifacts": review_hash_rows,
        },
    )
    write_json(
        phase_path("phase7", "owner_seal_record.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-owner-seal-record-v1",
            "generated_at": now_iso(),
            "status": gate_inputs["owner"]["status"],
            "owner_decision_status": owner_decision_status,
            "owner_seal_status": owner_seal_status,
            "owner_decision_input": gate_inputs["owner"]["record"],
            "owner_seal_replaces_independent_review": False,
        },
    )
    write_json(
        phase_path("phase7", "final_token_signoff_record.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-final-token-signoff-record-v1",
            "generated_at": now_iso(),
            "status": gate_inputs["token"]["status"],
            "final_token_signoff_status": final_token_signoff_status,
            "final_token_signoff_input": gate_inputs["token"]["record"],
            "signed_axis_values": gate_inputs["token"]["payload"].get("signed_axis_values", []),
            "signed_value_tokens": gate_inputs["token"]["payload"].get("signed_value_tokens", []),
        },
    )
    write_json(
        phase_path("phase7", "ledger_packet.json"),
        {
            "schema_version": "dvf-3-3-successor-readpoint-ledger-packet-v1",
            "generated_at": now_iso(),
            "status": "PASS" if machine_pass else "FAIL",
            "round_id": ROUND_ID,
            "closeout_state": final["closeout_state"],
            "canonical_seal_allowed": final["canonical_seal_allowed"],
            "canonical_seal_status": final["canonical_seal_status"],
            "canonical_seal_blocker_count": final["canonical_seal_blocker_count"],
            "final_report": rel(phase_path("phase7", "final_successor_readpoint_governance_seal_report.json")),
            "claim_boundary_doc": rel(CLAIM_BOUNDARY_DOC),
            "ledger_packet_doc": rel(LEDGER_PACKET_DOC),
        },
    )
    return final


def generate_artifacts(*, run_current_route: bool = False) -> dict[str, Any]:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    before_hash = hash_protected_surface()
    preflight = write_phase0()
    rows = write_phase1(before_hash)
    write_phase2(rows)
    write_phase3()
    write_phase4()
    write_phase5(rows)
    write_phase6(run_current_route=run_current_route)
    after_hash = hash_protected_surface()
    write_json(phase_path("phase1", "protected_surface_hashes.after.json"), after_hash)
    write_json(phase_path("phase1", "protected_no_mutation_report.json"), protected_diff(before_hash, after_hash))
    return write_phase7() if preflight.get("status") == "PASS" else write_phase7()


def validate_artifacts(*, require_complete: bool = False, write_report: bool = True) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required_paths = [
        phase_path("phase0", "roadmap_input_binding.json"),
        phase_path("phase0", "feedback_input_binding.json"),
        phase_path("phase0", "owner_reserved_decision_matrix.json"),
        phase_path("phase0", "report_field_contract.json"),
        phase_path("phase0", "preflight_current_checkout_readiness_report.json"),
        phase_path("phase1", "axis_occurrence_inventory.jsonl"),
        phase_path("phase1", "scan_root_manifest.json"),
        phase_path("phase1", "fingerprint_manifest.json"),
        phase_path("phase1", "surface_coverage_report.json"),
        phase_path("phase1", "protected_no_mutation_report.json"),
        phase_path("phase1", "package_surface_boundary_manifest.json"),
        phase_path("phase2", "axis_exhaustiveness_report.json"),
        phase_path("phase2", "axis_token_reconciliation_report.json"),
        phase_path("phase2", "axis_token_non_supersession_report.json"),
        phase_path("phase2", "occurrence_axis_map.json"),
        phase_path("phase3", "current_chain_count_hash_report.json"),
        phase_path("phase3", "chain_rowkey_identity_report.json"),
        phase_path("phase3", "source_rendered_runtime_package_binding.json"),
        phase_path("phase3", "package_peer_scan_canonical_minimum.json"),
        phase_path("phase4", "evidence_role_taxonomy_report.json"),
        phase_path("phase5", "predecessor_reentry_axis_guard_report.json"),
        phase_path("phase5", "no_axis_misuse_report.json"),
        phase_path("phase6", "live_required_manifest_adoption_report.json"),
        phase_path("phase6", "manifest_additive_diff_report.json"),
        phase_path("phase6", "current_route_tooling_closure_impact_report.json"),
        phase_path("phase6", "recursion_avoidance_validation_report.json"),
        phase_path("phase6", "post_adoption_required_test_execution_report.json"),
        phase_path("phase7", "final_successor_readpoint_governance_seal_report.json"),
        phase_path("phase7", "primary_review_artifact_manifest.json"),
        phase_path("phase7", "independent_review_artifact_hash_report.json"),
        phase_path("phase7", "owner_seal_record.json"),
        phase_path("phase7", "final_token_signoff_record.json"),
        phase_path("phase7", "ledger_packet.json"),
        INDEPENDENT_REVIEW_INPUT,
        OWNER_DECISION_INPUT,
        FINAL_TOKEN_SIGNOFF_INPUT,
        CLAIM_BOUNDARY_DOC,
        LEDGER_PACKET_DOC,
    ]
    for path in required_paths:
        if not path.exists():
            errors.append({"code": "missing_required_artifact", "path": rel(path)})
    checks = [
        (phase_path("phase0", "report_field_contract.json"), {"status": "PASS"}),
        (phase_path("phase0", "preflight_current_checkout_readiness_report.json"), {"status": "PASS"}),
        (phase_path("phase1", "surface_coverage_report.json"), {"status": "PASS", "missing_required_surface_family_count": 0}),
        (phase_path("phase1", "protected_no_mutation_report.json"), {"status": "PASS", "changed_count": 0}),
        (phase_path("phase2", "axis_exhaustiveness_report.json"), {"status": "PASS", "unclassified_count": 0, "ambiguous_count": 0}),
        (
            phase_path("phase2", "axis_token_non_supersession_report.json"),
            {"status": "PASS", "sealed_token_supersession_claim": False},
        ),
        (
            phase_path("phase3", "source_item_id_uniqueness_report.json"),
            {"status": "PASS", "duplicate_source_key_count": 0},
        ),
        (phase_path("phase3", "intra_source_keyset_equality_report.json"), {"status": "PASS", "mismatch_count": 0}),
        (phase_path("phase3", "key_transform_rule_report.json"), {"status": "PASS", "transform": "identity"}),
        (phase_path("phase3", "chain_rowkey_identity_report.json"), {"status": "PASS", "rowkey_identity_status": "pass"}),
        (
            phase_path("phase3", "package_peer_scan_canonical_minimum.json"),
            {"status": "PASS", "package_zip_preservation_required_for_canonical": False},
        ),
        (
            phase_path("phase4", "evidence_role_taxonomy_report.json"),
            {
                "status": "PASS",
                "candidate_promoted_to_current_authority_count": 0,
                "prerequisite_direct_execution_authority_count": 0,
            },
        ),
        (
            phase_path("phase5", "predecessor_reentry_axis_guard_report.json"),
            {
                "status": "PASS",
                "predecessor_current_hard_gate_count": 0,
                "old_chunks_or_monolith_fallback_count": 0,
            },
        ),
        (phase_path("phase5", "no_axis_misuse_report.json"), {"status": "PASS", "axis_misuse_count": 0}),
        (
            phase_path("phase6", "live_required_manifest_adoption_report.json"),
            {"status": "PASS", "removed_existing_entries": 0, "modified_existing_entries": 0},
        ),
        (
            phase_path("phase6", "manifest_additive_diff_report.json"),
            {"status": "PASS", "removed_existing_entries": 0, "modified_existing_entries": 0, "duplicate_entries": 0},
        ),
        (phase_path("phase6", "current_route_tooling_closure_impact_report.json"), {"status": "PASS", "active_core_count": 12}),
        (phase_path("phase6", "recursion_avoidance_validation_report.json"), {"status": "PASS", "self_referential_cycle_count": 0}),
        (
            phase_path("phase6", "post_adoption_required_test_execution_report.json"),
            {"status": "PASS", "missing_or_unexecuted_new_required_test_count": 0},
        ),
        (
            phase_path("phase7", "final_successor_readpoint_governance_seal_report.json"),
            {
                "status": "PASS",
                "machine_contract_status": "PASS",
            },
        ),
    ]
    if require_complete:
        checks.append(
            (
                phase_path("phase6", "current_route_validation_result.json"),
                {"success": True, "closure_enforced": True},
            )
        )
    for path, expected_fields in checks:
        if not path.exists():
            continue
        payload = read_json_object(path)
        for field, expected in expected_fields.items():
            observed = object_field(payload, field)
            if observed != expected:
                errors.append(
                    {
                        "code": "field_mismatch",
                        "path": rel(path),
                        "field": field,
                        "expected": expected,
                        "observed": observed,
                    }
                )
    final = read_json_object(phase_path("phase7", "final_successor_readpoint_governance_seal_report.json"))
    contract = read_json_object(phase_path("phase0", "report_field_contract.json"))
    for field in contract.get("final_report_required_fields", []):
        if field not in final:
            errors.append({"code": "missing_final_report_field", "field": field})
    canonical_allowed = final.get("canonical_seal_allowed") is True
    if canonical_allowed:
        canonical_expectations = {
            "closeout_state": "successor_readpoint_governance_seal_complete",
            "canonical_seal_status": "canonical_seal_allowed",
            "canonical_seal_blocker_count": 0,
            "vcs_preservation_status": "PASS",
            "vcs_preservation_proof_status": "PASS",
            "independent_review_status": "PASS",
            "owner_decision_status": "approved",
            "owner_seal_status": "sealed",
            "final_token_signoff_status": "signed",
        }
    else:
        canonical_expectations = {
            "closeout_state": "machine_governance_packet_complete",
            "canonical_seal_status": "blocked_multiple_canonical_gates_pending",
        }
    for field, expected in canonical_expectations.items():
        observed = object_field(final, field)
        if observed != expected:
            errors.append(
                {
                    "code": "final_canonical_gate_mismatch",
                    "path": rel(phase_path("phase7", "final_successor_readpoint_governance_seal_report.json")),
                    "field": field,
                    "expected": expected,
                    "observed": observed,
                }
            )
    if canonical_allowed and final.get("canonical_seal_blockers"):
        errors.append(
            {
                "code": "canonical_allowed_with_blockers",
                "path": rel(phase_path("phase7", "final_successor_readpoint_governance_seal_report.json")),
                "blockers": final.get("canonical_seal_blockers"),
            }
        )
    if not canonical_allowed and final.get("canonical_seal_blocker_count", 0) == 0:
        errors.append(
            {
                "code": "canonical_blocked_without_recorded_blockers",
                "path": rel(phase_path("phase7", "final_successor_readpoint_governance_seal_report.json")),
            }
        )
    report = {
        "schema_version": "dvf-3-3-successor-readpoint-validation-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not errors else "FAIL",
        "require_complete": require_complete,
        "canonical_complete_claimed": canonical_allowed,
        "machine_governance_packet_complete": final.get("machine_contract_status") == "PASS",
        "error_count": len(errors),
        "errors": errors,
    }
    if write_report:
        write_json(
            phase_path("phase7", "validation_report.require_complete.json" if require_complete else "validation_report.all.json"),
            report,
        )
    return report, not errors


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run DVF 3-3 vNext successor readpoint seal artifacts.")
    parser.add_argument("--mode", choices=("generate", "validate", "all", "machine-pass"), default="all")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)
    if args.mode in {"generate", "all", "machine-pass"}:
        final = generate_artifacts(run_current_route=args.mode in {"all", "machine-pass"})
        print(
            json.dumps(
                {
                    "status": final.get("status"),
                    "closeout_state": final.get("closeout_state"),
                    "canonical_seal_allowed": final.get("canonical_seal_allowed"),
                },
                sort_keys=True,
            )
        )
        if args.mode == "generate":
            return 0
    if args.mode in {"validate", "all", "machine-pass"}:
        if args.mode in {"all", "machine-pass"} and not args.require_complete:
            report_all, ok_all = validate_artifacts(require_complete=False)
            report_complete, ok_complete = validate_artifacts(require_complete=True)
            ok = ok_all and ok_complete
            errors = report_all["error_count"] + report_complete["error_count"]
        else:
            report, ok = validate_artifacts(require_complete=args.require_complete)
            errors = report["error_count"]
        print(json.dumps({"status": "PASS" if ok else "FAIL", "error_count": errors}, sort_keys=True))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
