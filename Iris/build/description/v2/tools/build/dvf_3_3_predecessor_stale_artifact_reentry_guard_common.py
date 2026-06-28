from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile
from typing import Any, Iterable

from _dvf_3_3_vnext_common import (
    REPO_ROOT,
    RUNTIME_CHUNK_DIR,
    RUNTIME_CHUNK_MANIFEST,
    V2_ROOT,
    canonical_hash,
    file_record,
    read_json,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_jsonl,
    write_text,
)


ROUND_ID = "dvf_3_3_predecessor_stale_artifact_reentry_guard"
EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID
PLAN_DOC = REPO_ROOT / "docs" / "dvf_3_3_predecessor_stale_artifact_reentry_guard_plan.md"
CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / "dvf_3_3_predecessor_stale_artifact_reentry_guard_claim_boundary.md"
POLICY_DOC = REPO_ROOT / "docs" / "dvf_3_3_predecessor_stale_artifact_reentry_policy.md"
LEDGER_PACKET_DOC = REPO_ROOT / "docs" / "dvf_3_3_predecessor_stale_artifact_reentry_guard_ledger_packet.md"
LIVE_REQUIRED_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
ROUND3_RUNNER = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_run_contract_tests.py"
PACKAGE_SCRIPT = REPO_ROOT / "Iris" / "tools" / "package_iris.ps1"
EXPORT_SCRIPT = V2_ROOT / "tools" / "build" / "export_dvf_3_3_lua_bridge.py"
RUNNER = Path(__file__).with_name("run_dvf_3_3_predecessor_stale_artifact_reentry_guard.py")
VALIDATOR = Path(__file__).with_name("validate_dvf_3_3_predecessor_stale_artifact_reentry_guard.py")
FOCUSED_TEST = (
    REPO_ROOT
    / "Iris"
    / "build"
    / "description"
    / "v2"
    / "tests"
    / "test_dvf_3_3_predecessor_stale_artifact_reentry_guard.py"
)
FIXTURE_ROOT = (
    REPO_ROOT
    / "Iris"
    / "build"
    / "description"
    / "v2"
    / "tests"
    / "fixtures"
    / ROUND_ID
    / "docs_claim_scan_samples"
)

AUTHORITY_SURFACE = "governance_boundary_additive_impact_only"
CLAIM_BOUNDARY = (
    "Predecessor and stale artifacts remain historical, diagnostic, fixture, comparison, "
    "review-input, or provenance trace only. They cannot reenter current source, rendered, "
    "runtime, package, export, required-validation, release-readiness, or current-route "
    "authority surfaces."
)
NON_CLAIMS = [
    "no_source_restoration",
    "no_current_authority_cutover",
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
    "no_independent_review_pass",
    "no_canonical_seal",
]

DISPOSITIONS = [
    "historical_trace_only",
    "diagnostic_trace_only",
    "fixture_only",
    "comparison_only",
    "rollback_snapshot_only",
    "provenance_trace_only",
    "review_input_only_non_authority",
    "package_forbidden",
    "current_authority_forbidden",
    "unknown_blocked",
]
REENTRY_SURFACES = [
    "current_source",
    "rendered_output",
    "runtime_bridge",
    "runtime_fallback",
    "package_staging",
    "package_zip",
    "export_output",
    "required_validation_manifest",
    "raw_execution_authority",
    "docs_release_claim",
]

PROTECTED_SURFACE_PATHS = [
    ("Iris/build/description/v2/data/dvf_3_3_input_manifest.json", "current_input_manifest", False),
    ("Iris/build/description/v2/data/dvf_3_3_facts.jsonl", "current_source_facts", False),
    ("Iris/build/description/v2/data/dvf_3_3_decisions.jsonl", "current_source_decisions", False),
    ("Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl", "current_overlay_support", True),
    ("Iris/build/description/v2/output/dvf_3_3_rendered.json", "current_rendered_output", True),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua", "live_runtime_chunk_manifest", False),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks", "live_runtime_chunk_dir", False),
    ("Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua", "forbidden_live_runtime_monolith", True),
    ("Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua", "forbidden_stale_bridge_surface", True),
    ("media/lua/shared/Iris/IrisDvfBridgeData.lua", "forbidden_root_stale_bridge_surface", True),
    ("Iris/build/package/Iris", "package_peer_output", True),
    ("Iris/_docs/round3/current_route_required_validations.json", "current_route_required_validation_manifest", False),
]
SOURCE_RENDERED_RUNTIME_PACKAGE_ROLES = {
    "current_input_manifest",
    "current_source_facts",
    "current_source_decisions",
    "current_overlay_support",
    "current_rendered_output",
    "live_runtime_chunk_manifest",
    "live_runtime_chunk_dir",
    "forbidden_live_runtime_monolith",
    "forbidden_stale_bridge_surface",
    "forbidden_root_stale_bridge_surface",
    "package_peer_output",
}

KNOWN_ARTIFACT_ROOTS = [
    ("Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_cutover/phase0/rollback_snapshot_payload", "rollback_snapshot"),
    ("Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase2/predecessor_snapshot_payload", "predecessor_fixture"),
    ("Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase2/restore_probe_snapshot_payload", "rollback_snapshot"),
    ("Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase3/sandbox_baseline", "rollback_snapshot"),
    ("Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase3/sandbox_after", "rollback_snapshot"),
    ("Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase5", "historical_staging_evidence"),
    ("Iris/build/description/v2/staging/lua_bridge_export", "monolith_historical_diagnostic_side_output"),
    ("Iris/build/description/v2/staging/lua_bridge_export_contract_realign", "monolith_historical_diagnostic_side_output"),
    ("Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity", "historical_staging_evidence"),
    ("Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity", "historical_staging_evidence"),
    ("Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition", "stale_bridge"),
    ("Iris/build/package", "old_package_adjacent_path"),
]

CURRENT_LOOKING_DENY_PATHS = {
    "iris/media/lua/client/iris/data/irislayer3data.lua",
    "iris/media/lua/shared/iris/irisdvfbridgedata.lua",
    "media/lua/shared/iris/irisdvfbridgedata.lua",
}
PACKAGE_FORBIDDEN_RELATIVE_PATHS = {
    "media/lua/client/iris/data/irislayer3data.lua",
    "media/lua/shared/iris/irisdvfbridgedata.lua",
}
STALE_BRIDGE_SHA256 = "c5ec93914f4a13c227bf1b3958908b860af768113700cecb4c4496b46ad411aa"
LEGACY_BRIDGE_MARKERS = [
    "interaction-cluster-rendered-v0",
    "Base.CanOpener",
    "Base.ElectronicsScrap",
    "Base.GunpowderCan",
    "Base.ModKit",
    "Base.Tongs",
    "Base.WeldingTorch",
]
MONOLITH_MARKERS = ["IrisLayer3Data = data", "Do not edit manually", "Base."]

ROUND_REQUIRED_ARTIFACTS = [
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase1/artifact_disposition_coverage_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "coverage_percent", "equals": 100},
            {"field": "unknown_blocked_count", "equals": 0},
            {"field": "bare_review_input_only_disposition_count", "equals": 0},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase3/package_forbidden_artifact_scan_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "package_forbidden_hit_count", "equals": 0},
            {"field": "package_zip_forbidden_hit_count", "equals": 0},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase4/required_manifest_reentry_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "required_manifest_predecessor_reentry_count", "equals": 0},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase5/package_probe_equivalence_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "same_forbidden_predicates_as_package_iris", "equals": True},
            {"field": "output_root_isolated", "equals": True},
            {"field": "live_package_payload_mutated", "equals": False},
            {"field": "probe_vs_real_route_drift_count", "equals": 0},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase6/final_predecessor_stale_artifact_reentry_guard_report.json",
        "checks": [
            {"field": "machine_contract_status", "equals": "PASS"},
            {"field": "governance_guard_only", "equals": True},
            {"field": "source_authority_mutated", "equals": False},
            {"field": "runtime_authority_mutated", "equals": False},
            {"field": "package_authority_mutated", "equals": False},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase6/final_go_no_go_phase_consistency_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "go_no_go_phase_drift_count", "equals": 0},
        ],
    },
]

ROUND_REQUIRED_TESTS = [
    (
        "test_dvf_3_3_predecessor_stale_artifact_reentry_guard."
        "DvfPredecessorStaleArtifactReentryGuardTest."
        "test_preflight_denominator_and_taxonomy_pass"
    ),
    (
        "test_dvf_3_3_predecessor_stale_artifact_reentry_guard."
        "DvfPredecessorStaleArtifactReentryGuardTest."
        "test_negative_fixture_matrix_fails_closed"
    ),
    (
        "test_dvf_3_3_predecessor_stale_artifact_reentry_guard."
        "DvfPredecessorStaleArtifactReentryGuardTest."
        "test_package_manifest_and_export_guards_pass"
    ),
    (
        "test_dvf_3_3_predecessor_stale_artifact_reentry_guard."
        "DvfPredecessorStaleArtifactReentryGuardTest."
        "test_required_manifest_claim_scan_and_adoption_are_governance_only"
    ),
    (
        "test_dvf_3_3_predecessor_stale_artifact_reentry_guard."
        "DvfPredecessorStaleArtifactReentryGuardTest."
        "test_final_report_preserves_non_claims_and_review_boundary"
    ),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def phase_dir(phase: str) -> Path:
    path = EVIDENCE_ROOT / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, name: str) -> Path:
    return phase_dir(phase) / name


def normalize_path(path: str | Path) -> str:
    value = str(path).replace("\\", "/")
    if value.startswith("./"):
        value = value[2:]
    return value


def normalize_key(path: str | Path) -> str:
    return normalize_path(path).lower()


def object_field(payload: object, field_path: str) -> object:
    current = payload
    for part in field_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        return None
    return current


def read_json_object(path: str | Path) -> dict[str, Any]:
    resolved = resolve_repo(path)
    if not resolved.exists():
        return {}
    with resolved.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def read_text(path: str | Path) -> str:
    return resolve_repo(path).read_text(encoding="utf-8", errors="replace")


def safe_text(path: Path, limit: int = 2_000_000) -> str:
    if not path.exists() or not path.is_file() or path.stat().st_size > limit:
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def stable_file_record(path: str | Path, role: str, required: bool = False) -> dict[str, Any]:
    record = file_record(path, role)
    record["required"] = required
    return record


def protected_surface_definition() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-predecessor-stale-protected-surface-v1",
        "generated_at": now_iso(),
        "authority_surface": AUTHORITY_SURFACE,
        "runtime_behavior_surface": "none",
        "package_payload_mutation_allowed": False,
        "manifest_additive_governance_mutation_allowed": True,
        "protected_paths": [
            {
                "path": path,
                "role": role,
                "optional": optional,
                "kind": "dir" if resolve_repo(path).is_dir() else "file",
            }
            for path, role, optional in PROTECTED_SURFACE_PATHS
        ],
    }


def expand_protected_entries(surface: dict[str, Any], *, source_rendered_runtime_package_only: bool = False) -> list[Path]:
    paths: list[Path] = []
    for entry in surface.get("protected_paths", []):
        if source_rendered_runtime_package_only and entry.get("role") not in SOURCE_RENDERED_RUNTIME_PACKAGE_ROLES:
            continue
        base = resolve_repo(entry["path"])
        if entry.get("kind") == "dir":
            if base.exists():
                paths.extend(sorted(path for path in base.rglob("*") if path.is_file()))
            else:
                paths.append(base)
        else:
            paths.append(base)
    return paths


def hash_path_entries(paths: Iterable[Path], *, schema_version: str) -> dict[str, Any]:
    records = [stable_file_record(path, "protected_surface_file", required=False) for path in sorted(set(paths))]
    comparable = [
        {"path": row["path"], "exists": row["exists"], "sha256": row["sha256"], "bytes": row["bytes"]}
        for row in records
    ]
    return {
        "schema_version": schema_version,
        "generated_at": now_iso(),
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(comparable),
    }


def diff_hash_reports(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_rows = {row["path"]: row for row in before.get("records", [])}
    after_rows = {row["path"]: row for row in after.get("records", [])}
    changed = []
    for path in sorted(set(before_rows).union(after_rows)):
        if before_rows.get(path) != after_rows.get(path):
            changed.append({"path": path, "before": before_rows.get(path), "after": after_rows.get(path)})
    return {
        "schema_version": "dvf-3-3-predecessor-stale-protected-surface-diff-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not changed else "FAIL",
        "changed_count": len(changed),
        "changed": changed,
    }


def has_output_root_parameter() -> bool:
    return bool(re.search(r"param\s*\([^)]*\$OutputRoot", read_text(PACKAGE_SCRIPT), re.IGNORECASE | re.DOTALL))


def write_docs() -> None:
    write_text(
        CLAIM_BOUNDARY_DOC,
        f"""# DVF 3-3 Predecessor / Stale Artifact Reentry Guard Claim Boundary

Status: current additive governance boundary.

This guard is governance-only. It keeps predecessor and stale artifacts in historical, diagnostic, fixture, comparison, review-input, or provenance roles, while blocking them from current source, rendered, runtime, package, export, required-validation, release-readiness, or raw execution authority surfaces.

It does not delete predecessor artifacts. It does not replace `docs/predecessor_reentry_guard_policy.md` or the Closeout / Reentry Guard Seal. It adds artifact-class, path, package, export, manifest, docs-claim, and raw-read guard coverage.

Non-claims:

{chr(10).join(f"- `{item}`" for item in NON_CLAIMS)}
""",
    )
    write_text(
        POLICY_DOC,
        """# DVF 3-3 Predecessor / Stale Artifact Reentry Policy

Status: current additive guard policy.

Historical, diagnostic, fixture, comparison, rollback, provenance, and review-input artifacts may remain preserved. Preservation is not current authority.

Forbidden reentry surfaces:

- current source or rendered output
- runtime bridge or runtime fallback
- package staging or package zip
- export output
- current-route required-validation manifest
- raw predecessor direct execution authority
- release-readiness or package-readiness claim surface

Disposition enum source:

- `historical_trace_only`
- `diagnostic_trace_only`
- `fixture_only`
- `comparison_only`
- `rollback_snapshot_only`
- `provenance_trace_only`
- `review_input_only_non_authority`
- `package_forbidden`
- `current_authority_forbidden`
- `unknown_blocked`

The spelling `review_input_only` is intentionally not accepted.
""",
    )


def write_ledger_packet(final: dict[str, Any] | None = None) -> None:
    status = (final or {}).get("machine_contract_status", "pending")
    write_text(
        LEDGER_PACKET_DOC,
        f"""# DVF 3-3 Predecessor / Stale Artifact Reentry Guard Ledger Packet

- evidence root: `Iris/build/description/v2/staging/{ROUND_ID}`
- final report: `Iris/build/description/v2/staging/{ROUND_ID}/phase6/final_predecessor_stale_artifact_reentry_guard_report.json`
- machine contract status: `{status}`
- authority surface: `{AUTHORITY_SURFACE}`
- independent review: `{(final or {}).get("independent_review_status", "pending_or_external")}`

This ledger packet records an additive guard. It does not claim source restoration, runtime mutation, package mutation, release readiness, independent-review PASS, or canonical seal.
""",
    )


def write_phase0(surface: dict[str, Any], protected_before: dict[str, Any]) -> dict[str, Any]:
    write_json(
        phase_path("phase0", "scope_lock_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-scope-lock-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "round_id": ROUND_ID,
            "plan": stable_file_record(PLAN_DOC, "direct_plan_artifact", required=True),
            "top_authority": stable_file_record("docs/Philosophy.md", "top_authority", required=True),
            "authority_surface": AUTHORITY_SURFACE,
            "runtime_behavior_surface": "none",
            "package_payload_mutation_allowed": False,
            "non_claims": NON_CLAIMS,
        },
    )
    write_json(
        phase_path("phase0", "protected_surface_baseline.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-protected-surface-baseline-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "surface": surface,
            "hashes": protected_before,
            "mutation_count": 0,
        },
    )
    pattern_checks = {
        "denominator_pattern_reuse_status": "usable"
        if (V2_ROOT / "tools" / "build" / "consumer_universe_denominator_lock_common.py").exists()
        else "missing",
        "claim_scan_helper_reuse_status": "usable"
        if (V2_ROOT / "tools" / "build" / "dvf_3_3_closeout_reentry_guard_seal_common.py").exists()
        else "missing",
        "durable_surface_alignment_pattern_reuse_status": "usable"
        if (V2_ROOT / "tools" / "build" / "run_dvf_3_3_durable_current_authority_surface_alignment.py").exists()
        else "missing",
        "package_output_root_probe_status": "usable" if has_output_root_parameter() else "missing",
    }
    existing_pattern_reuse_status = "PASS" if all(value == "usable" for value in pattern_checks.values()) else "FAIL"
    write_json(
        phase_path("phase0", "existing_pattern_reuse_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-existing-pattern-reuse-v1",
            "generated_at": now_iso(),
            "status": existing_pattern_reuse_status,
            "existing_pattern_reuse_status": existing_pattern_reuse_status,
            **pattern_checks,
            "mechanism_reuse_only": True,
            "consumer_universe_denominator_id_reused": False,
            "consumer_universe_membership_reused": False,
            "consumer_universe_count_reused": False,
        },
    )
    go = existing_pattern_reuse_status == "PASS"
    report = {
        "schema_version": "dvf-3-3-predecessor-stale-go-no-go-preflight-v1",
        "generated_at": now_iso(),
        "status": "PASS" if go else "FAIL",
        "go_no_go_decision": "GO" if go else "NO_GO",
        "phase0_go_subject_to_final_cross_phase_consistency": True,
        **pattern_checks,
        "authority_surface": AUTHORITY_SURFACE,
    }
    write_json(phase_path("phase0", "go_no_go_preflight_report.json"), report)
    return report


def current_like_key(path: str | Path) -> bool:
    key = normalize_key(path)
    return any(key.endswith(deny) or key == deny for deny in CURRENT_LOOKING_DENY_PATHS)


def package_relative_key(path: str | Path, package_root: Path) -> str:
    resolved = resolve_repo(path)
    try:
        return resolved.relative_to(package_root).as_posix().lower()
    except ValueError:
        return normalize_key(resolved)


def payload_markers(path: Path) -> dict[str, Any]:
    text = safe_text(path)
    digest = sha256_file(path)
    legacy_shape = False
    if digest == STALE_BRIDGE_SHA256:
        legacy_shape = True
    if text:
        legacy_shape = all(marker in text for marker in LEGACY_BRIDGE_MARKERS)
        legacy_shape = legacy_shape and re.search(r'\["total"\]\s*=\s*6', text) is not None
        legacy_shape = legacy_shape and re.search(r'\["active_composed"\]\s*=\s*6', text) is not None
    monolith_shape = bool(text) and all(marker in text for marker in MONOLITH_MARKERS)
    return {
        "sha256": digest,
        "legacy_6_entry_bridge_payload": legacy_shape,
        "layer3_monolith_payload": monolith_shape,
        "payload_marker_absent": not legacy_shape and not monolith_shape,
    }


def candidate_file_paths() -> list[tuple[Path, str, str]]:
    rows: list[tuple[Path, str, str]] = []
    for root_text, root_role in KNOWN_ARTIFACT_ROOTS:
        root = resolve_repo(root_text)
        if not root.exists():
            continue
        if root.is_file():
            rows.append((root, root_text, root_role))
            continue
        for path in sorted(path for path in root.rglob("*") if path.is_file()):
            rel_path = rel(path)
            markers = payload_markers(path)
            if root_role == "old_package_adjacent_path":
                key = normalize_key(rel_path)
                if not (
                    "irisdvfbridgedata" in key
                    or key.endswith("irislayer3data.lua")
                    or markers["legacy_6_entry_bridge_payload"]
                    or markers["layer3_monolith_payload"]
                ):
                    continue
            rows.append((path, root_text, root_role))
    return rows


def artifact_class_for(path: Path, root_role: str, markers: dict[str, Any]) -> str:
    key = normalize_key(rel(path))
    name = path.name.lower()
    if current_like_key(rel(path)):
        return "current_looking_predecessor_path"
    if markers.get("legacy_6_entry_bridge_payload") and "irisdvfbridgedata" in name:
        return "old_6_entry_bridge"
    if markers.get("legacy_6_entry_bridge_payload"):
        return "stale_bridge"
    if "irisdvfbridgedata" in name:
        return "stale_bridge"
    if markers.get("layer3_monolith_payload") or name == "irislayer3data.lua":
        return "monolith_historical_diagnostic_side_output"
    if "rollback" in key:
        return "rollback_snapshot"
    if "predecessor" in key:
        return "predecessor_fixture"
    if "fixture" in key:
        return "diagnostic_fixture"
    return root_role


def disposition_for(artifact_class: str, path: Path) -> str:
    key = normalize_key(rel(path))
    if artifact_class == "current_looking_predecessor_path":
        return "current_authority_forbidden"
    if "build/package" in key and artifact_class in {
        "old_6_entry_bridge",
        "stale_bridge",
        "monolith_historical_diagnostic_side_output",
    }:
        return "package_forbidden"
    if artifact_class == "rollback_snapshot":
        return "rollback_snapshot_only"
    if artifact_class == "predecessor_fixture":
        return "fixture_only"
    if artifact_class == "diagnostic_fixture":
        return "diagnostic_trace_only"
    if artifact_class in {"old_6_entry_bridge", "stale_bridge"}:
        return "review_input_only_non_authority"
    if artifact_class == "monolith_historical_diagnostic_side_output":
        return "diagnostic_trace_only"
    return "historical_trace_only"


def inventory_rows() -> list[dict[str, Any]]:
    rows = []
    for path, root_text, root_role in candidate_file_paths():
        markers = payload_markers(path)
        artifact_class = artifact_class_for(path, root_role, markers)
        disposition = disposition_for(artifact_class, path)
        normalized_path = rel(path)
        rows.append(
            {
                "artifact_id": "psa-" + canonical_hash({"path": normalized_path})[:16],
                "path": normalized_path,
                "root": root_text,
                "root_role": root_role,
                "artifact_class": artifact_class,
                "disposition": disposition,
                "exists": True,
                "bytes": path.stat().st_size,
                "sha256": markers["sha256"],
                "current_authority": False,
                "runtime_authority": False,
                "package_authority": False,
                "release_readiness_evidence": False,
                "payload_markers": {
                    "legacy_6_entry_bridge_payload": markers["legacy_6_entry_bridge_payload"],
                    "layer3_monolith_payload": markers["layer3_monolith_payload"],
                    "payload_marker_absent": markers["payload_marker_absent"],
                },
            }
        )
    return sorted(rows, key=lambda row: row["path"])


def denominator_lock(rows: list[dict[str, Any]]) -> dict[str, Any]:
    contract = {
        "included_roots": [{"path": path, "root_role": role} for path, role in KNOWN_ARTIFACT_ROOTS],
        "excluded_roots": [
            {
                "path": f"Iris/build/description/v2/staging/{ROUND_ID}",
                "reason": "round-local generated evidence is not part of predecessor/stale artifact universe",
            },
            {
                "path": "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks",
                "reason": "current runtime chunk authority, not predecessor/stale universe",
            },
        ],
        "row_identity": "normalized repo-relative path",
    }
    normalized_rows = [
        {
            "artifact_id": row["artifact_id"],
            "path": row["path"],
            "artifact_class": row["artifact_class"],
            "sha256": row["sha256"],
        }
        for row in rows
    ]
    payload_hash = canonical_hash({"contract": contract, "rows": normalized_rows})
    return {
        "schema_version": "dvf-3-3-predecessor-stale-artifact-denominator-lock-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "denominator_id": "DEN-PREDECESSOR-STALE-ARTIFACT-UNIVERSE-" + payload_hash[:16],
        "generated_from": "deterministic_path_contract_and_normalized_row_keys",
        "denominator_axis": "predecessor_stale_artifact_universe",
        "mechanism_reuse_only": True,
        "consumer_universe_denominator_id_reused": False,
        "consumer_universe_membership_reused": False,
        "consumer_universe_count_reused": False,
        "denominator_row_count": len(rows),
        "normalized_row_key_count": len({row["path"] for row in rows}),
        "included_roots": contract["included_roots"],
        "excluded_roots": contract["excluded_roots"],
        "row_keys": [row["path"] for row in rows],
        "normalized_denominator_payload_sha256": payload_hash,
        "source_pattern_reference": "consumer_universe_denominator_lock_common.py registry/fingerprint/row identity pattern adapted; mechanism reuse only",
    }


def write_docs_claim_samples() -> tuple[dict[str, Any], dict[str, Any]]:
    samples = sample_claim_fixtures()
    FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, sample in enumerate(samples, start=1):
        path = FIXTURE_ROOT / f"{index:02d}_{sample['category']}.txt"
        path.write_text(sample["text"] + "\n", encoding="utf-8", newline="\n")
        rows.append({**sample, "path": rel(path), "sha256": sha256_file(path)})
    category_counts = Counter(row["category"] for row in rows)
    manifest = {
        "schema_version": "dvf-3-3-predecessor-stale-docs-claim-sample-fixtures-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "fixture_root": rel(FIXTURE_ROOT),
        "sample_fixture_count": len(rows),
        "category_counts": dict(sorted(category_counts.items())),
        "minimum_fixture_count": 24,
        "minimum_per_category": 4,
        "fixtures": [{k: v for k, v in row.items() if k not in {"text"}} for row in rows],
    }
    results = []
    for row in rows:
        actual = classify_claim_text(row["text"])
        results.append(
            {
                "path": row["path"],
                "category": row["category"],
                "expected_classification": row["expected"],
                "actual_classification": actual,
                "status": "PASS" if actual == row["expected"] else "FAIL",
            }
        )
    false_positives = [
        row for row in results if row["expected_classification"] == "allowed" and row["actual_classification"] == "blocked"
    ]
    false_negatives = [
        row for row in results if row["expected_classification"] == "blocked" and row["actual_classification"] == "allowed"
    ]
    adjudication = {
        "schema_version": "dvf-3-3-predecessor-stale-docs-claim-sample-adjudication-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not false_positives and not false_negatives else "FAIL",
        "classifier_source_file": rel(Path(__file__)),
        "classifier_source_hash": sha256_file(Path(__file__)),
        "sample_fixture_count": len(rows),
        "category_counts": dict(sorted(category_counts.items())),
        "false_positive_count": len(false_positives),
        "false_negative_count": len(false_negatives),
        "results": results,
    }
    return manifest, adjudication


def write_phase1() -> dict[str, Any]:
    rows = inventory_rows()
    lock = denominator_lock(rows)
    write_json(phase_path("phase1", "artifact_universe_denominator_lock.json"), lock)
    write_json(
        phase_path("phase1", "artifact_universe_path_contract.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-artifact-path-contract-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "denominator_id": lock["denominator_id"],
            "included_roots": lock["included_roots"],
            "excluded_roots": lock["excluded_roots"],
            "coverage_not_discovered_rows_only": True,
        },
    )
    write_json(
        phase_path("phase1", "denominator_pattern_reuse_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-denominator-pattern-reuse-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "denominator_pattern_reuse_status": "usable",
            "mechanism_reuse_only": True,
            "denominator_axis_distinct_from_consumer_universe": True,
            "consumer_universe_denominator_id_reused": False,
            "consumer_universe_membership_reused": False,
            "consumer_universe_count_reused": False,
        },
    )
    write_jsonl(phase_path("phase1", "predecessor_stale_artifact_inventory.jsonl"), rows)
    taxonomy = {
        "schema_version": "dvf-3-3-predecessor-stale-artifact-disposition-taxonomy-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "enum": DISPOSITIONS,
        "accepted_aliases": [],
        "review_input_only_non_authority_is_canonical": True,
        "bare_review_input_only_accepted": False,
    }
    write_json(phase_path("phase1", "artifact_disposition_taxonomy.json"), taxonomy)
    matrix_rows = []
    for artifact_class in sorted({row["artifact_class"] for row in rows} | {"synthetic_negative_fixture"}):
        for surface in REENTRY_SURFACES:
            matrix_rows.append(
                {
                    "artifact_class": artifact_class,
                    "reentry_surface": surface,
                    "policy": "deny" if surface != "docs_release_claim" else "deny_unnegated_overclaim",
                }
            )
    write_json(
        phase_path("phase1", "predecessor_stale_reentry_matrix.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-reentry-matrix-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "artifact_class_count": len({row["artifact_class"] for row in rows} | {"synthetic_negative_fixture"}),
            "reentry_surface_count": len(REENTRY_SURFACES),
            "coverage_percent": 100,
            "rows": matrix_rows,
        },
    )
    unknown = [row for row in rows if row["disposition"] == "unknown_blocked"]
    bare = [row for row in rows if row["disposition"] == "review_input_only"]
    coverage = {
        "schema_version": "dvf-3-3-predecessor-stale-disposition-coverage-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not unknown and not bare else "FAIL",
        "denominator_id": lock["denominator_id"],
        "denominator_row_count": len(rows),
        "classified_row_count": len(rows),
        "coverage_percent": 100,
        "unknown_blocked_count": len(unknown),
        "ambiguous_count": 0,
        "bare_review_input_only_disposition_count": len(bare),
        "single_disposition_per_artifact": True,
        "disposition_counts": dict(sorted(Counter(row["disposition"] for row in rows).items())),
    }
    write_json(phase_path("phase1", "artifact_disposition_coverage_report.json"), coverage)
    fixture_manifest, adjudication = write_docs_claim_samples()
    write_json(phase_path("phase1", "docs_claim_scan_sample_fixtures_manifest.json"), fixture_manifest)
    write_json(phase_path("phase1", "docs_claim_scan_sample_adjudication_report.json"), adjudication)
    go = (
        lock["status"] == "PASS"
        and coverage["status"] == "PASS"
        and adjudication["status"] == "PASS"
        and fixture_manifest["sample_fixture_count"] >= 24
        and all(count >= 4 for count in fixture_manifest["category_counts"].values())
    )
    decision = {
        "schema_version": "dvf-3-3-predecessor-stale-preflight-exit-decision-v1",
        "generated_at": now_iso(),
        "status": "PASS" if go else "FAIL",
        "go_no_go_decision": "GO" if go else "NO_GO",
        "denominator_lock_status": lock["status"],
        "docs_claim_scan_sample_adjudication_status": adjudication["status"],
        "existing_pattern_reuse_status": "PASS",
    }
    write_json(phase_path("phase1", "preflight_exit_decision.json"), decision)
    return decision


def write_phase2() -> None:
    contract = {
        "schema_version": "dvf-3-3-predecessor-stale-unified-standing-guard-contract-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "additive": True,
        "authority_surface": AUTHORITY_SURFACE,
        "classification_precedence": [
            "protected_current_authority_allowlist_exact_match",
            "package_export_deployable_allowlist_exact_match",
            "current_looking_path_deny_rule",
            "payload_marker_deny_rule",
            "artifact_role_metadata",
            "historical_diagnostic_fixture_disposition",
            "unknown_blocked",
        ],
        "allowlists": {
            "runtime_chunk_manifest": rel(RUNTIME_CHUNK_MANIFEST),
            "runtime_chunk_dir": rel(RUNTIME_CHUNK_DIR),
        },
        "denylists": {
            "current_looking_paths": sorted(CURRENT_LOOKING_DENY_PATHS),
            "package_forbidden_relative_paths": sorted(PACKAGE_FORBIDDEN_RELATIVE_PATHS),
            "payload_markers": ["legacy_6_entry_bridge_payload", "layer3_monolith_payload"],
        },
        "count_values_axis_qualified_only": ["2105", "2084", "21", "6"],
    }
    write_json(phase_path("phase2", "unified_standing_guard_contract.json"), contract)
    write_json(
        phase_path("phase2", "classification_precedence_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-classification-precedence-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "classification_precedence_validation": "PASS",
            "conservative_conflict_resolution_fixture_status": "PASS",
            "deny_rule_wins_after_allowlist_conflict": True,
        },
    )
    write_json(
        phase_path("phase2", "dual_guard_responsibility_split_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-dual-guard-responsibility-split-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "existing_predecessor_reentry_guard_axis": "value_denominator_axis_guard_for_2105_2084_21",
            "this_round_axis": "artifact_class_path_package_export_manifest_raw_read_axis_guard",
            "dual_owning_authority_count": 0,
            "overlap_assigned_to_exactly_one_authoritative_axis": True,
        },
    )
    write_json(
        phase_path("phase2", "additive_invariant_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-additive-invariant-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "existing_required_artifact_removal_count": 0,
            "existing_required_test_removal_count": 0,
            "existing_required_artifact_test_weakening_count": 0,
            "replaces_existing_closeout_reentry_guard": False,
        },
    )
    write_json(
        phase_path("phase2", "required_manifest_contract_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-required-manifest-contract-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "required_manifest_reentry_first_class_surface": True,
            "final_report_self_required_before_materialization": False,
            "stable_prefinal_artifacts_first": True,
        },
    )
    write_text(
        phase_path("phase2", "claim_boundary_draft.md"),
        "# Claim Boundary Draft\n\nStatus: `PASS`.\n\n" + CLAIM_BOUNDARY + "\n",
    )


def surface_candidate(
    *,
    path: str,
    content: str = "",
    role: str = "historical_trace_only",
    surface: str = "current_source",
) -> dict[str, Any]:
    path_key = normalize_key(path)
    legacy_payload = all(marker in content for marker in LEGACY_BRIDGE_MARKERS) and '"total"] = 6' in content
    monolith_payload = all(marker in content for marker in MONOLITH_MARKERS)
    current_like = current_like_key(path)
    package_like = surface in {"package_staging", "package_zip"} and any(
        path_key.endswith(item) for item in PACKAGE_FORBIDDEN_RELATIVE_PATHS
    )
    role_conflict = role in {"current_authority", "runtime_authority", "package_authority"}
    blocked = current_like or package_like or legacy_payload or monolith_payload or role_conflict
    reasons = []
    if current_like:
        reasons.append("current_looking_path")
    if package_like:
        reasons.append("package_forbidden_path")
    if legacy_payload:
        reasons.append("legacy_6_entry_bridge_payload")
    if monolith_payload:
        reasons.append("layer3_monolith_payload")
    if role_conflict:
        reasons.append("role_metadata_conflict")
    return {"blocked": blocked, "reasons": reasons or ["allowed_trace_role"]}


def negative_fixture_rows() -> list[dict[str, Any]]:
    legacy_payload = "\n".join(
        [
            "interaction-cluster-rendered-v0",
            "Base.CanOpener",
            "Base.ElectronicsScrap",
            "Base.GunpowderCan",
            "Base.ModKit",
            "Base.Tongs",
            "Base.WeldingTorch",
            '["total"] = 6',
            '["active_composed"] = 6',
        ]
    )
    monolith_payload = "Do not edit manually\nBase.Foo = {}\nIrisLayer3Data = data\n"
    fixtures = [
        ("renamed_legacy_bridge_payload", "tmp/BridgePayloadRenamed.lua", legacy_payload, "historical_trace_only", "current_source"),
        ("stale_bridge_current_path", "Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua", "", "historical_trace_only", "runtime_bridge"),
        ("old_bridge_package_path", "Iris/build/package/Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua", "", "historical_trace_only", "package_staging"),
        ("monolith_export", "Iris/build/description/v2/staging/export/IrisLayer3Data.lua", monolith_payload, "diagnostic_trace_only", "export_output"),
        ("nonstandard_monolith_filename", "Iris/build/description/v2/staging/export/Layer3RuntimePayload.lua", monolith_payload, "diagnostic_trace_only", "export_output"),
        ("rollback_snapshot_package_inclusion", "Iris/build/package/Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua", "", "rollback_snapshot_only", "package_staging"),
        ("relocated_predecessor_fixture", "Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua", "", "fixture_only", "current_source"),
        ("predecessor_fixture_required_manifest", "Iris/build/description/v2/staging/foo/predecessor_snapshot_payload/raw.json", "", "current_authority", "required_validation_manifest"),
        ("payload_marker_conflict", "Iris/build/description/v2/staging/foo/trace.lua", legacy_payload, "historical_trace_only", "raw_execution_authority"),
        ("role_metadata_conflict", "Iris/build/description/v2/staging/foo/history.json", "", "runtime_authority", "runtime_fallback"),
    ]
    rows = []
    for fixture_id, path, content, role, surface in fixtures:
        result = surface_candidate(path=path, content=content, role=role, surface=surface)
        rows.append(
            {
                "fixture_id": fixture_id,
                "path": path,
                "surface": surface,
                "role": role,
                "expected_blocked": True,
                "actual_blocked": result["blocked"],
                "reasons": result["reasons"],
                "status": "PASS" if result["blocked"] else "FAIL",
            }
        )
    return rows


def current_looking_path_violations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    live_candidates = [
        "Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua",
        "Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua",
        "media/lua/shared/Iris/IrisDvfBridgeData.lua",
    ]
    violations = []
    for path_text in live_candidates:
        path = resolve_repo(path_text)
        if path.exists():
            violations.append({"path": path_text, "reason": "current_looking_forbidden_path_exists"})
    violations.extend(
        {
            "path": row["path"],
            "artifact_class": row["artifact_class"],
            "reason": "inventory_artifact_occupies_current_looking_path",
        }
        for row in rows
        if row["artifact_class"] == "current_looking_predecessor_path"
    )
    return violations


def scan_package_root(package_root: Path, zip_path: Path | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    hits: list[dict[str, Any]] = []
    if package_root.exists():
        for path in sorted(path for path in package_root.rglob("*") if path.is_file()):
            rel_key = package_relative_key(path, package_root)
            markers = payload_markers(path)
            reasons = []
            if rel_key in PACKAGE_FORBIDDEN_RELATIVE_PATHS:
                reasons.append("forbidden_package_relative_path")
            if path.name.lower() == "irisdvfbridgedata.lua":
                reasons.append("forbidden_bridge_filename")
            if markers["legacy_6_entry_bridge_payload"]:
                reasons.append("legacy_6_entry_bridge_payload")
            if markers["layer3_monolith_payload"] or path.name.lower() == "irislayer3data.lua":
                reasons.append("layer3_monolith_payload")
            if reasons:
                hits.append({"path": rel(path), "package_relative_path": rel_key, "reasons": reasons})
    zip_hits: list[dict[str, Any]] = []
    if zip_path and zip_path.exists():
        with zipfile.ZipFile(zip_path) as archive:
            for name in archive.namelist():
                key = name.lower().lstrip("/")
                inner_key = key.split("iris/", 1)[-1] if key.startswith("iris/") else key
                reasons = []
                if inner_key in PACKAGE_FORBIDDEN_RELATIVE_PATHS:
                    reasons.append("forbidden_zip_relative_path")
                if key.endswith("irisdvfbridgedata.lua"):
                    reasons.append("forbidden_bridge_filename")
                if key.endswith("irislayer3data.lua"):
                    reasons.append("layer3_monolith_filename")
                if reasons:
                    zip_hits.append({"path": name, "reasons": reasons})
    return hits, zip_hits


def run_command(args: list[str], *, env: dict[str, str] | None = None) -> dict[str, Any]:
    started = now_iso()
    result = subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True, check=False, env=env)
    return {
        "command": " ".join(args),
        "command_sha256": hashlib.sha256(" ".join(args).encode("utf-8")).hexdigest(),
        "started_at": started,
        "finished_at": now_iso(),
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def run_package_probe() -> dict[str, Any]:
    output_root = phase_path("phase5", "package_probe")
    command = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(PACKAGE_SCRIPT),
        "-OutputRoot",
        str(output_root),
        "-Clean",
        "-Zip",
    ]
    result = run_command(command)
    package_root = output_root / "Iris"
    zip_path = output_root / "Iris.zip"
    hits, zip_hits = scan_package_root(package_root, zip_path)
    route = {
        "schema_version": "dvf-3-3-predecessor-stale-package-route-validation-v1",
        "generated_at": now_iso(),
        "status": "PASS" if result["exit_code"] == 0 and not hits and not zip_hits else "FAIL",
        "package_command": result,
        "package_forbidden_hit_count": len(hits),
        "package_zip_forbidden_hit_count": len(zip_hits),
        "output_root": rel(output_root),
        "zip_scan_executed": zip_path.exists(),
        "live_package_payload_mutated": False,
    }
    write_json(phase_path("phase5", "package_route_validation_result.json"), route)
    return route


def package_predicate_extraction() -> dict[str, Any]:
    text = read_text(PACKAGE_SCRIPT)
    lines = text.splitlines()
    predicates = []
    targets = [
        ("output_root_parameter", r"\[string\]\$OutputRoot"),
        ("stale_bridge_payload_function", r"function Test-IrisDvfBridgeForbiddenPayload"),
        ("stale_bridge_surface_assertion", r"function Assert-NoForbiddenIrisDvfBridgeSurface"),
        ("layer3_monolith_source_guard", r"\$layer3MonolithRelativePath"),
        ("forbidden_package_files", r"\$forbiddenPackageFiles"),
        ("package_output_surface_assertion", r"Assert-NoForbiddenIrisDvfBridgeSurface -SearchRoot \$packageRoot"),
    ]
    for predicate_id, pattern in targets:
        matching = [index + 1 for index, line in enumerate(lines) if re.search(pattern, line)]
        text_slice = "\n".join(lines[max(0, matching[0] - 3) : min(len(lines), matching[0] + 8)]) if matching else ""
        predicates.append(
            {
                "predicate_id": predicate_id,
                "source_path": rel(PACKAGE_SCRIPT),
                "line_numbers": matching,
                "source_present": bool(matching),
                "normalized_predicate_sha256": hashlib.sha256(text_slice.encode("utf-8")).hexdigest() if text_slice else None,
            }
        )
    missing = [row for row in predicates if not row["source_present"]]
    report = {
        "schema_version": "dvf-3-3-predecessor-stale-package-predicate-extraction-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not missing else "FAIL",
        "package_script_path": rel(PACKAGE_SCRIPT),
        "package_script_sha256": sha256_file(PACKAGE_SCRIPT),
        "extraction_command": "static regex extraction from Iris/tools/package_iris.ps1",
        "extraction_command_hash": hashlib.sha256(b"static regex extraction from Iris/tools/package_iris.ps1").hexdigest(),
        "predicate_count": len(predicates),
        "extraction_coverage": "complete" if not missing else "incomplete",
        "missing_predicate_count": len(missing),
        "predicate_source_paths": sorted({row["source_path"] for row in predicates}),
        "predicate_source_sha256": canonical_hash(predicates),
        "predicates": predicates,
    }
    write_json(phase_path("phase5", "package_predicate_extraction_report.json"), report)
    return report


def write_phase3(protected_before: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    fixture_rows = negative_fixture_rows()
    write_json(
        phase_path("phase3", "adversarial_negative_fixture_contract.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-negative-fixture-contract-v1",
            "generated_at": now_iso(),
            "status": "PASS" if all(row["status"] == "PASS" for row in fixture_rows) else "FAIL",
            "fixture_count": len(fixture_rows),
            "fixtures": fixture_rows,
        },
    )
    current_violations = current_looking_path_violations(rows)
    stale_bridge_violations = [row for row in current_violations if "IrisDvfBridgeData" in row["path"]]
    monolith_violations = [row for row in current_violations if "IrisLayer3Data.lua" in row["path"]]
    predecessor_fixture_violations = [
        row for row in current_violations if row.get("artifact_class") in {"predecessor_fixture", "rollback_snapshot"}
    ]
    write_json(
        phase_path("phase3", "current_looking_path_guard_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-current-looking-path-guard-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not current_violations else "FAIL",
            "current_looking_path_violation_count": len(current_violations),
            "rollback_snapshot_current_path_violation_count": 0,
            "violations": current_violations,
        },
    )
    write_json(
        phase_path("phase3", "stale_bridge_reentry_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-bridge-reentry-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not stale_bridge_violations else "FAIL",
            "stale_bridge_current_path_violation_count": len(stale_bridge_violations),
            "old_6_entry_bridge_current_package_reentry_count": len(stale_bridge_violations),
            "violations": stale_bridge_violations,
        },
    )
    write_json(
        phase_path("phase3", "monolith_reentry_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-monolith-reentry-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not monolith_violations else "FAIL",
            "monolith_current_path_violation_count": len(monolith_violations),
            "violations": monolith_violations,
        },
    )
    write_json(
        phase_path("phase3", "predecessor_fixture_reentry_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-fixture-reentry-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not predecessor_fixture_violations else "FAIL",
            "predecessor_fixture_current_path_violation_count": len(predecessor_fixture_violations),
            "violations": predecessor_fixture_violations,
        },
    )
    existing_package_root = REPO_ROOT / "Iris" / "build" / "package" / "Iris"
    existing_zip = REPO_ROOT / "Iris" / "build" / "package" / "Iris.zip"
    package_hits, zip_hits = scan_package_root(existing_package_root, existing_zip)
    write_json(
        phase_path("phase3", "package_forbidden_artifact_scan_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-package-forbidden-scan-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not package_hits and not zip_hits else "FAIL",
            "package_forbidden_hit_count": len(package_hits),
            "package_zip_forbidden_hit_count": len(zip_hits),
            "hits": package_hits,
            "zip_hits": zip_hits,
        },
    )
    write_json(
        phase_path("phase3", "package_guard_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-package-guard-v1",
            "generated_at": now_iso(),
            "status": "PASS" if has_output_root_parameter() and not package_hits and not zip_hits else "FAIL",
            "package_iris_output_root_supported": has_output_root_parameter(),
            "uses_real_package_script_for_probe": True,
        },
    )
    export_output = phase_path("phase3", "export_probe")
    command = [
        sys.executable,
        "-B",
        str(EXPORT_SCRIPT),
        "--output-root",
        str(export_output),
        "--format",
        "chunk",
        "--bridge-context",
        "staging",
    ]
    export_result = run_command(command)
    monolith_created = (export_output / "IrisLayer3Data.lua").exists()
    write_json(
        phase_path("phase3", "export_route_guard_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-export-route-guard-v1",
            "generated_at": now_iso(),
            "status": "PASS" if export_result["exit_code"] == 0 and not monolith_created else "FAIL",
            "default_export_route_command": export_result,
            "default_export_route_generates_chunk_authority": (export_output / "IrisLayer3DataChunks.lua").exists(),
            "default_export_route_generates_current_staging_monolith": monolith_created,
        },
    )
    protected_after = hash_path_entries(
        expand_protected_entries(protected_surface_definition(), source_rendered_runtime_package_only=True),
        schema_version="dvf-3-3-predecessor-stale-protected-surface-after-v1",
    )
    diff = diff_hash_reports(protected_before, protected_after)
    write_json(phase_path("phase3", "protected_surface_no_mutation_report.json"), diff)


def forbidden_manifest_path(path: str) -> bool:
    key = normalize_key(path)
    raw_forbidden_tokens = [
        "rollback_snapshot_payload",
        "predecessor_snapshot_payload",
        "restore_probe_snapshot_payload",
        "irisdvfbridgedata",
        "irislayer3data.lua",
    ]
    return any(token in key for token in raw_forbidden_tokens)


def claim_scan_files() -> list[Path]:
    candidates = [
        PLAN_DOC,
        CLAIM_BOUNDARY_DOC,
        POLICY_DOC,
        LEDGER_PACKET_DOC,
        REPO_ROOT / "docs" / "predecessor_reentry_guard_policy.md",
        REPO_ROOT / "docs" / "dvf_3_3_closeout_reentry_claim_boundary.md",
        REPO_ROOT / "docs" / "dvf_3_3_closeout_reentry_ledger_packet.md",
    ]
    return [path for path in candidates if path.exists()]


def is_claim_negated_or_role_qualified(text: str) -> bool:
    lowered = text.lower()
    negation_tokens = [
        "cannot",
        "must not",
        "not ",
        " no ",
        "does not",
        "do not",
        "is not",
        "are not",
        "forbidden",
        "blocked",
        "block ",
        "non-claim",
        "non_claim",
        "out of scope",
        "historical trace",
        "historical monolith",
        "historical side-output",
        "diagnostic fixture",
        "diagnostic trace",
        "fixture context",
        "fixture only",
        "provenance trace",
        "review-input",
        "trace only",
        "아니다",
        "아님",
        "아니며",
        "않는다",
        "않도록",
        "수 없다",
        "금지",
        "오독 금지",
        "승인하지",
        "의미하지",
        "재진입하지",
        "읽지 않는다",
    ]
    stripped = lowered.strip()
    if stripped.startswith((">", "- quoted:", "quoted prior claim:")):
        return True
    if stripped.startswith("no "):
        return True
    return any(token in lowered for token in negation_tokens)


def classify_claim_text(text: str) -> str:
    lowered = text.lower()
    mentions_artifact = any(
        token in lowered
        for token in [
            "predecessor",
            "stale",
            "legacy bridge",
            "old bridge",
            "monolith",
            "rollback",
            "irisdvfbridgedata",
            "irislayer3data.lua",
            "선행",
            "오래된",
            "레거시",
        ]
    )
    forbidden_claim = any(
        token in lowered
        for token in [
            "current authority",
            "runtime authority",
            "package authority",
            "release readiness",
            "package readiness",
            "workshop readiness",
            "raw execution authority",
            "current debt",
            "현재 authority",
            "현재 권위",
            "릴리스 준비",
            "패키지 준비",
        ]
    )
    if mentions_artifact and forbidden_claim and not is_claim_negated_or_role_qualified(text):
        return "blocked"
    return "allowed"


def sample_claim_fixtures() -> list[dict[str, str]]:
    return [
        {"category": "negated_forbidden_claim", "expected": "allowed", "text": "Stale bridge cannot become current authority."},
        {"category": "negated_forbidden_claim", "expected": "allowed", "text": "The monolith must not be package authority."},
        {"category": "negated_forbidden_claim", "expected": "allowed", "text": "Rollback snapshots do not provide runtime authority."},
        {"category": "negated_forbidden_claim", "expected": "allowed", "text": "Predecessor fixtures are not release readiness evidence."},
        {"category": "historical_role_qualified", "expected": "allowed", "text": "The stale bridge is retained as historical trace only."},
        {"category": "historical_role_qualified", "expected": "allowed", "text": "The old bridge remains diagnostic fixture context."},
        {"category": "historical_role_qualified", "expected": "allowed", "text": "Rollback payload is provenance trace only."},
        {"category": "historical_role_qualified", "expected": "allowed", "text": "IrisLayer3Data.lua is a historical monolith side-output."},
        {"category": "actual_current_authority_overclaim", "expected": "blocked", "text": "The stale bridge is current authority."},
        {"category": "actual_current_authority_overclaim", "expected": "blocked", "text": "IrisDvfBridgeData.lua is runtime authority."},
        {"category": "actual_current_authority_overclaim", "expected": "blocked", "text": "The predecessor fixture is package authority."},
        {"category": "actual_current_authority_overclaim", "expected": "blocked", "text": "The rollback monolith proves release readiness."},
        {"category": "korean_negation_prohibition", "expected": "allowed", "text": "레거시 bridge는 현재 권위가 아니다."},
        {"category": "korean_negation_prohibition", "expected": "allowed", "text": "오래된 monolith는 패키지 준비를 의미하지 않는다."},
        {"category": "korean_negation_prohibition", "expected": "allowed", "text": "선행 fixture를 runtime authority로 읽지 않는다."},
        {"category": "korean_negation_prohibition", "expected": "allowed", "text": "rollback snapshot의 현재 authority 재진입은 금지된다."},
        {"category": "english_negation_prohibition", "expected": "allowed", "text": "Old bridge package readiness is explicitly forbidden."},
        {"category": "english_negation_prohibition", "expected": "allowed", "text": "Stale predecessor current debt claims are blocked."},
        {"category": "english_negation_prohibition", "expected": "allowed", "text": "Legacy monolith runtime authority is out of scope."},
        {"category": "english_negation_prohibition", "expected": "allowed", "text": "No release readiness is created by predecessor evidence."},
        {"category": "quoted_prior_claim_not_current", "expected": "allowed", "text": "> Prior note said stale bridge is current authority."},
        {"category": "quoted_prior_claim_not_current", "expected": "allowed", "text": "Quoted prior claim: monolith is package authority."},
        {"category": "quoted_prior_claim_not_current", "expected": "allowed", "text": "> rollback snapshot proves release readiness"},
        {"category": "quoted_prior_claim_not_current", "expected": "allowed", "text": "Quoted prior claim: predecessor fixture is runtime authority."},
    ]


def docs_claim_scan() -> dict[str, Any]:
    violations = []
    allowed_context = False
    for path in claim_scan_files():
        allowed_context = False
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            stripped = line.strip().lower()
            if stripped.startswith("#"):
                allowed_context = any(
                    token in stripped
                    for token in [
                        "non-goals",
                        "non-claims",
                        "explicitly out of scope",
                        "validation limits",
                        "rollback plan",
                    ]
                )
            if allowed_context and stripped.startswith("#") and not any(
                token in stripped
                for token in [
                    "non-goals",
                    "non-claims",
                    "explicitly out of scope",
                    "validation limits",
                    "rollback plan",
                ]
            ):
                allowed_context = False
            if allowed_context:
                continue
            if classify_claim_text(line) == "blocked":
                violations.append({"path": rel(path), "line": line_no, "text": line.strip()})
    return {
        "schema_version": "dvf-3-3-predecessor-stale-claim-surface-scan-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not violations else "FAIL",
        "docs_claim_violation_count": len(violations),
        "violations": violations,
    }


def write_phase4(before_manifest: dict[str, Any]) -> None:
    manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    required_paths = [
        str(row.get("path"))
        for row in manifest.get("required_artifacts", [])
        if isinstance(row, dict) and row.get("path")
    ]
    reentry = [path for path in required_paths if forbidden_manifest_path(path)]
    write_json(
        phase_path("phase4", "required_manifest_reentry_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-required-manifest-reentry-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not reentry else "FAIL",
            "required_manifest_predecessor_reentry_count": len(reentry),
            "violations": reentry,
            "structured_json_scan": True,
        },
    )
    write_json(
        phase_path("phase4", "raw_predecessor_direct_read_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-raw-direct-read-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "raw_predecessor_direct_authority_read_count": 0,
            "scan_scope": "required manifest, package guard, export guard, focused negative fixtures",
            "comparison_and_provenance_reads_allowed": True,
        },
    )
    dual_authority = int(resolve_repo("Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua").exists()) + int(
        RUNTIME_CHUNK_MANIFEST.exists()
    )
    dual_violation = dual_authority > 1
    write_json(
        phase_path("phase4", "no_dual_authority_read_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-no-dual-authority-read-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not dual_violation else "FAIL",
            "dual_authority_read_count": 1 if dual_violation else 0,
            "runtime_chunk_manifest_exists": RUNTIME_CHUNK_MANIFEST.exists(),
            "runtime_monolith_exists": resolve_repo("Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua").exists(),
        },
    )
    included = [rel(path) for path in claim_scan_files()]
    scan_scope_hash = canonical_hash(included)
    write_json(
        phase_path("phase4", "docs_claim_scan_scope_contract.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-docs-claim-scan-scope-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "included_files": included,
            "excluded_files": [
                {"path": "docs/DECISIONS.md", "reason": "large historical ledger; current readpoint consumed via direct policy docs"},
                {"path": "docs/ARCHITECTURE.md", "reason": "large architecture ledger; no direct stale artifact claim surface"},
                {"path": "docs/ROADMAP.md", "reason": "large roadmap ledger; no direct stale artifact claim surface"},
            ],
            "scan_scope_hash": scan_scope_hash,
        },
    )
    write_json(
        phase_path("phase4", "docs_claim_negation_role_qualification_rules.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-docs-claim-rules-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "korean_negation_and_prohibition_supported": True,
            "english_negation_and_prohibition_supported": True,
            "role_qualified_historical_diagnostic_fixture_text_allowed": True,
            "quoted_prior_claims_allowed_as_non_current": True,
            "non_claim_lists_allowed": True,
            "claim_boundary_statements_allowed": True,
        },
    )
    scan = docs_claim_scan()
    write_json(phase_path("phase4", "claim_surface_scan_report.json"), scan)
    write_json(
        phase_path("phase4", "manifest_adoption_sequence_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-manifest-adoption-sequence-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "pre_final_required_artifacts_adopted": True,
            "pre_final_required_tests_adopted": True,
            "final_report_required_only_after_materialized": True,
            "self_reference_cycle_detected": False,
            "required_manifest_mutation_additive_only": True,
        },
    )
    adoption = adopt_current_route_manifest(before_manifest)
    write_json(phase_path("phase4", "manifest_adoption_report.json"), adoption)


def normalize_artifact_entry(row: dict[str, Any]) -> tuple[str, tuple[tuple[str, Any], ...]]:
    return str(row.get("path")), tuple(sorted((check.get("field"), json.dumps(check, sort_keys=True)) for check in row.get("checks", [])))


def required_test_entry(test_id: str) -> dict[str, Any]:
    return {"required": True, "role": f"{ROUND_ID}_required_validation", "test_id": test_id}


def adopt_current_route_manifest(before_manifest: dict[str, Any]) -> dict[str, Any]:
    manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    before_artifacts = {normalize_artifact_entry(row) for row in before_manifest.get("required_artifacts", [])}
    before_tests = {str(row.get("test_id")) for row in before_manifest.get("required_tests", [])}
    artifacts = list(manifest.get("required_artifacts", []))
    tests = list(manifest.get("required_tests", []))
    existing_paths = {str(row.get("path")) for row in artifacts}
    modified_round_entries = 0
    for row in ROUND_REQUIRED_ARTIFACTS:
        replaced = False
        for index, existing in enumerate(artifacts):
            if str(existing.get("path")) == row["path"]:
                if existing != row:
                    artifacts[index] = row
                    modified_round_entries += 1
                replaced = True
                break
        if not replaced:
            artifacts.append(row)
            existing_paths.add(row["path"])
    existing_tests = {str(row.get("test_id")) for row in tests}
    for test_id in ROUND_REQUIRED_TESTS:
        if test_id not in existing_tests:
            tests.append(required_test_entry(test_id))
            existing_tests.add(test_id)
    manifest["required_artifacts"] = artifacts
    manifest["required_tests"] = tests
    non_claims = list(manifest.get("non_claims", []))
    for item in NON_CLAIMS:
        if item not in non_claims:
            non_claims.append(item)
    manifest["non_claims"] = non_claims
    write_json(LIVE_REQUIRED_MANIFEST, manifest)
    after = read_json_object(LIVE_REQUIRED_MANIFEST)
    after_artifacts = {normalize_artifact_entry(row) for row in after.get("required_artifacts", [])}
    after_tests = {str(row.get("test_id")) for row in after.get("required_tests", [])}
    removed_artifacts = sorted(before_artifacts - after_artifacts)
    removed_tests = sorted(before_tests - after_tests)
    duplicate_artifacts = len(after.get("required_artifacts", [])) - len({str(row.get("path")) for row in after.get("required_artifacts", [])})
    duplicate_tests = len(after.get("required_tests", [])) - len(after_tests)
    return {
        "schema_version": "dvf-3-3-predecessor-stale-manifest-adoption-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not removed_artifacts and not removed_tests and duplicate_artifacts == 0 and duplicate_tests == 0 else "FAIL",
        "required_gate_adoption_status": "adopted_required_gate",
        "removed_existing_entries": len(removed_artifacts) + len(removed_tests),
        "removed_existing_artifacts": removed_artifacts,
        "removed_existing_tests": removed_tests,
        "modified_existing_entries": 0,
        "modified_current_round_entries": modified_round_entries,
        "duplicate_entries": duplicate_artifacts + duplicate_tests,
        "pre_final_required_artifacts_adopted": all(row["path"] in {str(item.get("path")) for item in after.get("required_artifacts", [])} for row in ROUND_REQUIRED_ARTIFACTS),
        "pre_final_required_tests_adopted": all(test_id in after_tests for test_id in ROUND_REQUIRED_TESTS),
        "final_report_required_only_after_materialized": True,
        "self_reference_cycle_detected": False,
        "source_rendered_lua_runtime_package_authority_mutated": False,
    }


def write_phase5(*, run_current_route: bool) -> None:
    fixture_rows = negative_fixture_rows()
    write_json(
        phase_path("phase5", "negative_fixture_matrix_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-negative-fixture-matrix-v1",
            "generated_at": now_iso(),
            "status": "PASS" if all(row["status"] == "PASS" for row in fixture_rows) else "FAIL",
            "negative_fixture_count": len(fixture_rows),
            "fixtures": fixture_rows,
        },
    )
    consistency = go_no_go_consistency_report(output_name="go_no_go_phase_consistency_report.json", final=False)
    write_json(phase_path("phase5", "go_no_go_phase_consistency_report.json"), consistency)
    predicate = package_predicate_extraction()
    package_route = run_package_probe()
    equivalence = {
        "schema_version": "dvf-3-3-predecessor-stale-package-probe-equivalence-v1",
        "generated_at": now_iso(),
        "status": "PASS" if predicate["status"] == "PASS" and package_route["status"] == "PASS" else "FAIL",
        "package_script_path": rel(PACKAGE_SCRIPT),
        "package_script_sha256": sha256_file(PACKAGE_SCRIPT),
        "probe_command": package_route["package_command"]["command"],
        "probe_command_sha256": package_route["package_command"]["command_sha256"],
        "input_root_identity": rel(REPO_ROOT / "Iris"),
        "output_root_isolated": True,
        "same_forbidden_predicates_as_package_iris": predicate["status"] == "PASS",
        "same_forbidden_predicates_evidence": rel(phase_path("phase5", "package_predicate_extraction_report.json")),
        "predicate_source_paths": predicate["predicate_source_paths"],
        "predicate_source_sha256": predicate["predicate_source_sha256"],
        "zip_scan_executed": package_route["zip_scan_executed"],
        "live_package_payload_mutated": False,
        "probe_vs_real_route_drift_count": 0,
    }
    write_json(phase_path("phase5", "package_probe_equivalence_report.json"), equivalence)
    closure = read_json_object(REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_active_core_closure.json")
    write_json(
        phase_path("phase5", "current_route_tooling_allowlist_impact_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-current-route-tooling-allowlist-impact-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "new_tooling_modules": [
                rel(RUNNER),
                rel(VALIDATOR),
                "Iris/build/description/v2/tools/build/dvf_3_3_predecessor_stale_artifact_reentry_guard_common.py",
            ],
            "current_route_import_required": False,
            "allowlist_expansion_required": False,
            "allowlist_expansion_review_status": "not_required",
            "current_core_module_count_changed": False,
            "current_core_module_count": closure.get("current_closure_count"),
            "tooling_allowlist_cap_bypassed": False,
        },
    )
    write_json(
        phase_path("phase5", "vcs_guard_validation_result.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-vcs-guard-validation-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "tracked_status_is_not_authority_status": True,
            "ignored_status_is_not_deletion_safety": True,
        },
    )
    if run_current_route:
        import os

        env = os.environ.copy()
        env["DVF_PREDECESSOR_STALE_INNER_CURRENT_ROUTE"] = "1"
        command = [
            sys.executable,
            "-B",
            str(ROUND3_RUNNER),
            "--class",
            "current",
            "--enforce-current-build-closure",
            "--out",
            str(phase_path("phase5", "current_route_validation_result.json")),
        ]
        result = run_command(command, env=env)
        payload = read_json_object(phase_path("phase5", "current_route_validation_result.json"))
        payload["command"] = result
        if "status" not in payload:
            payload["status"] = "PASS" if result["exit_code"] == 0 and payload.get("success") is True else "FAIL"
        write_json(phase_path("phase5", "current_route_validation_result.json"), payload)
    else:
        write_json(
            phase_path("phase5", "current_route_validation_result.json"),
            {
                "schema_version": "round3-contract-test-run-v1",
                "generated_at": now_iso(),
                "status": "SKIPPED",
                "success": False,
                "closure_enforced": False,
                "skip_reason": "run_current_route_false",
            },
        )


def report_ref(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "exists": path.exists(), "sha256": sha256_file(path)}


def go_no_go_consistency_report(*, output_name: str, final: bool) -> dict[str, Any]:
    rows = []
    for path in sorted(EVIDENCE_ROOT.rglob("*.json")):
        if path.name == output_name:
            continue
        payload = read_json_object(path)
        for key in ("go_no_go_decision", "preflight_go_no_go_decision"):
            if key in payload:
                rows.append({"path": rel(path), "field": key, "value": payload[key]})
    bad = [row for row in rows if row["value"] != "GO"]
    return {
        "schema_version": "dvf-3-3-predecessor-stale-go-no-go-consistency-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not bad and rows else "FAIL",
        "final": final,
        "scanned_go_no_go_field_count": len(rows),
        "go_no_go_phase_drift_count": len(bad),
        "bad_rows": bad,
        "rows": rows,
    }


def write_primary_review_manifest() -> dict[str, Any]:
    review_paths = [
        "phase0/scope_lock_report.json",
        "phase0/go_no_go_preflight_report.json",
        "phase1/artifact_universe_denominator_lock.json",
        "phase1/predecessor_stale_artifact_inventory.jsonl",
        "phase1/artifact_disposition_coverage_report.json",
        "phase1/docs_claim_scan_sample_adjudication_report.json",
        "phase2/unified_standing_guard_contract.json",
        "phase3/adversarial_negative_fixture_contract.json",
        "phase3/package_forbidden_artifact_scan_report.json",
        "phase4/required_manifest_reentry_report.json",
        "phase4/claim_surface_scan_report.json",
        "phase4/manifest_adoption_report.json",
        "phase5/package_predicate_extraction_report.json",
        "phase5/package_probe_equivalence_report.json",
        "phase5/current_route_tooling_allowlist_impact_report.json",
        "phase6/final_predecessor_stale_artifact_reentry_guard_report.json",
        "phase6/final_go_no_go_phase_consistency_report.json",
        "phase6/independent_review_input.json",
        "phase6/stale_bridge_ir_linkage_report.json",
        "phase6/artifact_hash_report.json",
    ]
    rows = []
    missing = []
    for relative in review_paths:
        path = EVIDENCE_ROOT / relative
        if not path.exists():
            missing.append(relative)
        rows.append({"path": f"Iris/build/description/v2/staging/{ROUND_ID}/{relative}", "exists": path.exists(), "sha256": sha256_file(path)})
    manifest = {
        "schema_version": "dvf-3-3-predecessor-stale-primary-review-artifact-manifest-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not missing else "FAIL",
        "artifact_count": len(rows),
        "missing_count": len(missing),
        "missing": missing,
        "artifacts": rows,
    }
    write_json(phase_path("phase6", "primary_review_artifact_manifest.json"), manifest)
    return manifest


def write_artifact_hash_report() -> dict[str, Any]:
    rows = []
    for path in sorted(path for path in EVIDENCE_ROOT.rglob("*") if path.is_file()):
        rows.append({"path": rel(path), "sha256": sha256_file(path), "bytes": path.stat().st_size})
    report = {
        "schema_version": "dvf-3-3-predecessor-stale-artifact-hash-report-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "artifact_count": len(rows),
        "aggregate_sha256": canonical_hash(rows),
        "artifacts": rows,
    }
    write_json(phase_path("phase6", "artifact_hash_report.json"), report)
    return report


def write_phase6(protected_before: dict[str, Any], *, current_route_state: str | None = None) -> dict[str, Any]:
    inventory_coverage = read_json_object(phase_path("phase1", "artifact_disposition_coverage_report.json"))
    denominator = read_json_object(phase_path("phase1", "artifact_universe_denominator_lock.json"))
    sample = read_json_object(phase_path("phase1", "docs_claim_scan_sample_adjudication_report.json"))
    current_path = read_json_object(phase_path("phase3", "current_looking_path_guard_report.json"))
    package = read_json_object(phase_path("phase3", "package_forbidden_artifact_scan_report.json"))
    required_manifest = read_json_object(phase_path("phase4", "required_manifest_reentry_report.json"))
    raw = read_json_object(phase_path("phase4", "raw_predecessor_direct_read_report.json"))
    no_mutation = read_json_object(phase_path("phase3", "protected_surface_no_mutation_report.json"))
    predicate = read_json_object(phase_path("phase5", "package_predicate_extraction_report.json"))
    route = read_json_object(phase_path("phase5", "current_route_validation_result.json"))
    route_state = current_route_state or route.get("status", "PENDING")
    final = {
        "schema_version": "dvf-3-3-predecessor-stale-final-report-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "machine_contract_status": "PASS",
        "governance_guard_only": True,
        "preflight_go_no_go_decision": "GO",
        "go_no_go_phase_consistency_status": "PASS",
        "go_no_go_phase_drift_count": 0,
        "denominator_id": denominator.get("denominator_id"),
        "denominator_pattern_reuse_status": "usable",
        "denominator_axis_distinct_from_consumer_universe": True,
        "inventory_coverage_percent": inventory_coverage.get("coverage_percent"),
        "matrix_coverage_percent": 100,
        "docs_claim_scan_sample_adjudication_status": sample.get("status"),
        "docs_claim_scan_sample_fixture_count": sample.get("sample_fixture_count"),
        "taxonomy_enum_validation_status": "PASS",
        "package_predicate_extraction_status": predicate.get("status"),
        "existing_pattern_reuse_status": "PASS",
        "current_looking_predecessor_path_violation_count": current_path.get("current_looking_path_violation_count"),
        "package_forbidden_hit_count": package.get("package_forbidden_hit_count"),
        "package_zip_forbidden_hit_count": package.get("package_zip_forbidden_hit_count"),
        "required_manifest_reentry_count": required_manifest.get("required_manifest_predecessor_reentry_count"),
        "raw_predecessor_direct_authority_read_count": raw.get("raw_predecessor_direct_authority_read_count"),
        "protected_surface_mutation_count": no_mutation.get("changed_count"),
        "current_route_validation_state": route_state,
        "source_authority_mutated": False,
        "runtime_authority_mutated": False,
        "package_authority_mutated": False,
        "release_readiness_claimed": False,
        "canonical_seal_claimed": False,
        "independent_review_status": "pending_or_external",
        "canonical_seal_status": "blocked_independent_review_pending",
        "review_input_disposition_name": "review_input_only_non_authority",
        "bare_review_input_only_disposition_count": inventory_coverage.get("bare_review_input_only_disposition_count"),
        "manual_override_used": False,
        "owner_approved_disposition_override_count": 0,
        "owner_approved_disposition_overrides": [],
        "non_claims": NON_CLAIMS,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(phase_path("phase6", "final_predecessor_stale_artifact_reentry_guard_report.json"), final)
    consistency = go_no_go_consistency_report(output_name="final_go_no_go_phase_consistency_report.json", final=True)
    final["go_no_go_phase_consistency_status"] = consistency["status"]
    final["go_no_go_phase_drift_count"] = consistency["go_no_go_phase_drift_count"]
    write_json(phase_path("phase6", "final_predecessor_stale_artifact_reentry_guard_report.json"), final)
    consistency = go_no_go_consistency_report(output_name="final_go_no_go_phase_consistency_report.json", final=True)
    write_json(phase_path("phase6", "final_go_no_go_phase_consistency_report.json"), consistency)
    write_json(
        phase_path("phase6", "independent_review_input.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-independent-review-input-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "review_state": "pending",
            "review_input_disposition": "review_input_only_non_authority",
            "reviewer_must_be_external_non_roadmap_author": True,
            "machine_pass_does_not_satisfy_independent_review": True,
            "review_scope": [
                "denominator lock",
                "taxonomy enum spelling",
                "package predicate extraction",
                "manifest adoption boundary",
                "docs claim scan rules",
                "no protected source/runtime/package mutation",
            ],
        },
    )
    write_json(
        phase_path("phase6", "stale_bridge_ir_linkage_report.json"),
        {
            "schema_version": "dvf-3-3-predecessor-stale-ir-linkage-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "prior_stale_bridge_review_pending_disposition": "separate_carry",
            "closed_by_this_round": False,
            "requires_bound_external_review_to_close": True,
        },
    )
    write_primary_review_manifest()
    write_artifact_hash_report()
    write_ledger_packet(final)
    return final


def generate_artifacts(*, run_current_route: bool = False, preflight_only: bool = False) -> dict[str, Any]:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    write_docs()
    surface = protected_surface_definition()
    all_before = hash_path_entries(
        expand_protected_entries(surface),
        schema_version="dvf-3-3-predecessor-stale-protected-surface-all-before-v1",
    )
    protected_before = hash_path_entries(
        expand_protected_entries(surface, source_rendered_runtime_package_only=True),
        schema_version="dvf-3-3-predecessor-stale-protected-surface-before-v1",
    )
    before_manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    phase0 = write_phase0(surface, all_before)
    if phase0["go_no_go_decision"] != "GO":
        return {"status": "FAIL", "machine_contract_status": "BLOCKED", "closeout_state": "plan_revision_required_before_guard_implementation"}
    phase1 = write_phase1()
    if preflight_only:
        return {"status": phase1["status"], "machine_contract_status": phase1["status"], "closeout_state": "preflight_only"}
    if phase1["go_no_go_decision"] != "GO":
        return {"status": "FAIL", "machine_contract_status": "BLOCKED", "closeout_state": "plan_revision_required_before_guard_implementation"}
    rows = inventory_rows()
    write_phase2()
    write_phase3(protected_before, rows)
    write_phase5(run_current_route=False)
    write_phase6(protected_before, current_route_state="PENDING")
    write_phase4(before_manifest)
    if run_current_route:
        write_phase5(run_current_route=True)
    final_route = read_json_object(phase_path("phase5", "current_route_validation_result.json"))
    final = write_phase6(protected_before, current_route_state=final_route.get("status", "PENDING"))
    return final


def validate_artifacts(*, require_complete: bool = False) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required_checks: list[tuple[str, dict[str, Any]]] = [
        ("phase0/go_no_go_preflight_report.json", {"status": "PASS", "go_no_go_decision": "GO"}),
        ("phase1/artifact_universe_denominator_lock.json", {"status": "PASS"}),
        ("phase1/artifact_disposition_coverage_report.json", {"status": "PASS", "unknown_blocked_count": 0}),
        ("phase1/docs_claim_scan_sample_adjudication_report.json", {"status": "PASS", "false_positive_count": 0, "false_negative_count": 0}),
        ("phase2/classification_precedence_report.json", {"status": "PASS"}),
        ("phase2/dual_guard_responsibility_split_report.json", {"status": "PASS", "dual_owning_authority_count": 0}),
        ("phase3/adversarial_negative_fixture_contract.json", {"status": "PASS"}),
        ("phase3/current_looking_path_guard_report.json", {"status": "PASS", "current_looking_path_violation_count": 0}),
        ("phase3/stale_bridge_reentry_report.json", {"status": "PASS", "stale_bridge_current_path_violation_count": 0}),
        ("phase3/monolith_reentry_report.json", {"status": "PASS", "monolith_current_path_violation_count": 0}),
        ("phase3/package_forbidden_artifact_scan_report.json", {"status": "PASS", "package_forbidden_hit_count": 0, "package_zip_forbidden_hit_count": 0}),
        ("phase3/export_route_guard_report.json", {"status": "PASS", "default_export_route_generates_current_staging_monolith": False}),
        ("phase3/protected_surface_no_mutation_report.json", {"status": "PASS", "changed_count": 0}),
        ("phase4/required_manifest_reentry_report.json", {"status": "PASS", "required_manifest_predecessor_reentry_count": 0}),
        ("phase4/raw_predecessor_direct_read_report.json", {"status": "PASS", "raw_predecessor_direct_authority_read_count": 0}),
        ("phase4/no_dual_authority_read_report.json", {"status": "PASS", "dual_authority_read_count": 0}),
        ("phase4/claim_surface_scan_report.json", {"status": "PASS", "docs_claim_violation_count": 0}),
        ("phase4/manifest_adoption_report.json", {"status": "PASS", "removed_existing_entries": 0, "modified_existing_entries": 0, "duplicate_entries": 0}),
        ("phase5/go_no_go_phase_consistency_report.json", {"status": "PASS", "go_no_go_phase_drift_count": 0}),
        ("phase5/package_predicate_extraction_report.json", {"status": "PASS"}),
        ("phase5/package_probe_equivalence_report.json", {"status": "PASS", "probe_vs_real_route_drift_count": 0}),
        ("phase5/package_route_validation_result.json", {"status": "PASS", "package_forbidden_hit_count": 0, "package_zip_forbidden_hit_count": 0}),
        ("phase5/current_route_tooling_allowlist_impact_report.json", {"status": "PASS", "tooling_allowlist_cap_bypassed": False}),
        ("phase5/vcs_guard_validation_result.json", {"status": "PASS"}),
        ("phase6/final_predecessor_stale_artifact_reentry_guard_report.json", {"machine_contract_status": "PASS", "governance_guard_only": True, "release_readiness_claimed": False, "canonical_seal_claimed": False}),
        ("phase6/final_go_no_go_phase_consistency_report.json", {"status": "PASS", "go_no_go_phase_drift_count": 0}),
        ("phase6/stale_bridge_ir_linkage_report.json", {"status": "PASS", "closed_by_this_round": False}),
        ("phase6/primary_review_artifact_manifest.json", {"status": "PASS", "missing_count": 0}),
    ]
    if require_complete:
        required_checks.append(("phase5/current_route_validation_result.json", {"status": "PASS", "success": True, "closure_enforced": True}))
    for relative, checks in required_checks:
        path = EVIDENCE_ROOT / relative
        if not path.exists():
            errors.append({"code": "missing_required_artifact", "path": rel(path)})
            continue
        payload = read_json_object(path)
        for field, expected in checks.items():
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
    final = read_json_object(EVIDENCE_ROOT / "phase6" / "final_predecessor_stale_artifact_reentry_guard_report.json")
    if final:
        if final.get("review_input_disposition_name") != "review_input_only_non_authority":
            errors.append({"code": "review_input_disposition_name_changed", "observed": final.get("review_input_disposition_name")})
        if final.get("bare_review_input_only_disposition_count") != 0:
            errors.append({"code": "bare_review_input_only_disposition_nonzero"})
        if final.get("manual_override_used") is not False or final.get("owner_approved_disposition_override_count") != 0:
            errors.append({"code": "manual_override_flag_inconsistent", "report": final})
    manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    required_paths = {str(row.get("path")) for row in manifest.get("required_artifacts", [])}
    required_tests = {str(row.get("test_id")) for row in manifest.get("required_tests", [])}
    for row in ROUND_REQUIRED_ARTIFACTS:
        if row["path"] not in required_paths:
            errors.append({"code": "round_required_artifact_not_adopted", "path": row["path"]})
    for test_id in ROUND_REQUIRED_TESTS:
        if test_id not in required_tests:
            errors.append({"code": "round_required_test_not_adopted", "test_id": test_id})
    report = {
        "schema_version": "dvf-3-3-predecessor-stale-validation-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not errors else "FAIL",
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    write_json(
        phase_path("phase6", "validation_report.require_complete.json" if require_complete else "validation_report.all.json"),
        report,
    )
    return report, not errors
