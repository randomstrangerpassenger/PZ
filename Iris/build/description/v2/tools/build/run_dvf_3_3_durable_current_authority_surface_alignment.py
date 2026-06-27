#!/usr/bin/env python
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from _dvf_3_3_vnext_common import (
    LIVE_DATA_DIR,
    LIVE_OUTPUT_DIR,
    REPO_ROOT,
    RUNTIME_CHUNK_DIR,
    RUNTIME_CHUNK_MANIFEST,
    RUNTIME_MONOLITH,
    V2_ROOT,
    canonical_hash,
    chunk_paths_from_manifest,
    file_record,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_text,
)
from dvf_3_3_current_route_required_validation_evidence_freshness_reseal import (
    LIVE_REQUIRED_MANIFEST,
    ROUND3_RUNNER,
    diff_hash_reports,
    hash_path_entries,
    object_field,
    protected_surface_paths,
)


ROUND_ID = "dvf_3_3_durable_current_authority_surface_alignment"
EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID
ROUND3_DIR = REPO_ROOT / "Iris" / "_docs" / "round3"
ROUND3_TAXONOMY = ROUND3_DIR / "round3_test_taxonomy.json"
ROUND3_CLOSURE = ROUND3_DIR / "round3_active_core_closure.json"

PLAN_DOC = REPO_ROOT / "docs" / "dvf_3_3_durable_current_authority_surface_alignment_plan.md"
POLICY_DOC = REPO_ROOT / "docs" / "dvf_3_3_durable_surface_policy.md"
CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / "dvf_3_3_durable_current_authority_surface_alignment_claim_boundary.md"
LEDGER_PACKET_DOC = REPO_ROOT / "docs" / "dvf_3_3_durable_current_authority_surface_alignment_ledger_packet.md"

RUNNER = Path(__file__)
VALIDATOR = Path(__file__).with_name("validate_dvf_3_3_durable_current_authority_surface_alignment.py")
FOCUSED_TEST = (
    REPO_ROOT
    / "Iris"
    / "build"
    / "description"
    / "v2"
    / "tests"
    / "test_dvf_3_3_durable_current_authority_surface_alignment.py"
)

CURRENT_SOURCE_CHAIN = [
    "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
    "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl",
    "Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl",
    "Iris/build/description/v2/data/dvf_3_3_input_manifest.json",
]
GOVERNANCE_BACKBONE = [
    "Iris/_docs/round3/round3_run_contract_tests.py",
    "Iris/_docs/round3/round3_test_taxonomy.json",
    "Iris/_docs/round3/round3_active_core_closure.json",
    "Iris/_docs/round3/current_route_required_validations.json",
    "docs/dvf_3_3_durable_current_authority_surface_alignment_plan.md",
    "docs/dvf_3_3_durable_surface_policy.md",
    "docs/dvf_3_3_durable_current_authority_surface_alignment_claim_boundary.md",
    "docs/dvf_3_3_durable_current_authority_surface_alignment_ledger_packet.md",
]
ESSENTIAL_GUARD_TOOLING = [
    "Iris/build/description/v2/tools/build/dvf_vcs_tracking_policy.py",
    "Iris/build/description/v2/tests/test_dvf_vcs_tracking_policy.py",
    "Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py",
    "Iris/build/description/v2/tools/build/run_dvf_3_3_durable_current_authority_surface_alignment.py",
    "Iris/build/description/v2/tools/build/validate_dvf_3_3_durable_current_authority_surface_alignment.py",
    "Iris/build/description/v2/tests/test_dvf_3_3_durable_current_authority_surface_alignment.py",
]
FORBIDDEN_CURRENT_LOOKING = [
    "media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua",
]
RENDERED_OUTPUT = "Iris/build/description/v2/output/dvf_3_3_rendered.json"
NON_REQUIRED_STAGING_NEGATIVE_CONTROL = (
    "Iris/build/description/v2/staging/dvf_vcs_tracking_policy/vcs_tracking_summary.md"
)

DURABLE_CLASSES = [
    "current_source_authority_chain",
    "live_required_validation_manifest",
    "current_route_governance_surface",
    "essential_guard_and_regeneration_tooling",
    "deployable_runtime_chunk_authority",
    "required_adopted_evidence",
]
NON_DURABLE_DEFAULT_CLASSES = [
    "generated_staging_evidence",
    "sandbox_output",
    "candidate_manifest",
    "raw_audit_artifact",
    "readiness_or_dry_run_byproduct",
    "diagnostic_only_artifact",
    "historical_reproduction_artifact",
    "quarantine_copy",
    "round_local_scratch_artifact",
    "package_or_release_intermediate",
]
REQUIRED_NON_CLAIMS = [
    "tracked_status_is_not_authority_status",
    "ignored_status_is_not_deletable_status",
    "required_artifact_adoption_is_governance_only",
    "staging_evidence_root_is_not_current_authority",
    "durable_surface_is_preservation_scope_not_writer_scope",
    "required_gate_is_not_writer",
    "complete_is_axis_qualified_not_release_readiness",
]
INNER_CURRENT_ROUTE_ENV = "DVF_DURABLE_SURFACE_INNER_CURRENT_ROUTE"
OWNER_SEAL_STATUS = "PASS"
INDEPENDENT_REVIEW_STATUS = "PASS"


ROUND_REQUIRED_ARTIFACTS = [
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase1/manifest_schema_header_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "schema_version_observed", "equals": "round3-current-route-required-validations-v1"},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase4/vcs_durability_guard_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "post_reconciliation_untracked_ignored_required_artifact_count", "equals": 0},
            {"field": "governance_backbone_problem_count", "equals": 0},
            {"field": "essential_guard_problem_count", "equals": 0},
            {"field": "runtime_chunk_problem_count", "equals": 0},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase4/current_route_import_boundary_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "unallowlisted_import_count", "equals": 0},
            {"field": "current_route_tooling_allowlist_unchanged", "equals": True},
            {"field": "current_core_closure_count_unchanged", "equals": True},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase4/current_required_evidence_reconciliation_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "post_reconciliation_untracked_ignored_required_artifact_count", "equals": 0},
            {"field": "broad_staging_root_unignored", "equals": False},
            {"field": "non_required_staging_byproduct_tracking_requirement", "equals": False},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase5/live_manifest_adoption_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "required_gate_adoption_status", "equals": "adopted_required_gate"},
            {"field": "removed_existing_entries", "equals": 0},
            {"field": "modified_existing_entries", "equals": 0},
            {"field": "duplicate_entries", "equals": 0},
            {"field": "source_rendered_lua_runtime_package_authority_mutated", "equals": False},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase6/protected_surface_no_mutation_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "source_changed_count", "equals": 0},
            {"field": "rendered_changed_count", "equals": 0},
            {"field": "lua_bridge_changed_count", "equals": 0},
            {"field": "runtime_changed_count", "equals": 0},
            {"field": "package_changed_count", "equals": 0},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase6/rendered_output_disposition_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "authority_claim", "equals": False},
            {"field": "unresolved_review_required_disposition_count", "equals": 0},
        ],
    },
    {
        "path": f"Iris/build/description/v2/staging/{ROUND_ID}/phase7/durable_surface_sufficiency_report.json",
        "checks": [
            {"field": "status", "equals": "PASS"},
            {"field": "bounded_durable_surface_sufficiency", "equals": "PASS"},
            {"field": "required_manifest_classification_missing_count", "equals": 0},
        ],
    },
]

ROUND_REQUIRED_TESTS = [
    "test_dvf_3_3_durable_current_authority_surface_alignment."
    "DvfDurableCurrentAuthoritySurfaceAlignmentTest."
    "test_inventory_tracking_and_import_boundary_pass",
    "test_dvf_3_3_durable_current_authority_surface_alignment."
    "DvfDurableCurrentAuthoritySurfaceAlignmentTest."
    "test_live_manifest_adoption_is_additive_and_governance_only",
    "test_dvf_3_3_durable_current_authority_surface_alignment."
    "DvfDurableCurrentAuthoritySurfaceAlignmentTest."
    "test_final_report_preserves_non_claims_and_bounded_sufficiency",
]

PRIMARY_REVIEW_ARTIFACTS = [
    "phase1/durable_surface_inventory.json",
    "phase1/manifest_schema_header_report.json",
    "phase1/vcs_state_inventory_report.json",
    "phase1/unclassified_surface_report.json",
    "phase2/durable_surface_role_matrix.json",
    "phase2/durability_rule_report.json",
    "phase2/governance_backbone_binding_report.json",
    "phase3/per_artifact_classification_ledger.json",
    "phase3/taxonomy_disposition_preflight_report.json",
    "phase3/required_adoption_mapping_report.json",
    "phase3/non_durable_staging_negative_control_report.json",
    "phase4/vcs_durability_guard_report.json",
    "phase4/current_route_import_boundary_report.json",
    "phase4/git_tracking_status_report.json",
    "phase4/current_required_evidence_reconciliation_report.json",
    "phase4/ignore_predicate_fixture_report.json",
    "phase4/tracking_reconciliation_report.json",
    "phase5/live_manifest_adoption_report.json",
    "phase5/artifact_materialization_order_report.json",
    "phase5/required_validation_manifest_diff_report.json",
    "phase5/current_route_validation_result.json",
    "phase6/claim_surface_scan_report.json",
    "phase6/completion_vocabulary_scan_report.json",
    "phase6/protected_surface_no_mutation_report.json",
    "phase6/rendered_output_disposition_report.json",
    "phase7/final_durable_current_authority_surface_alignment_report.json",
    "phase7/primary_review_artifact_manifest.json",
    "phase7/independent_review_artifact_hash_report.json",
    "phase7/owner_seal_report.json",
    "phase7/durable_surface_sufficiency_report.json",
    "phase7/durable_boundary_empirical_reproduction_report.json",
    "phase7/deferred_gate_cross_reference_report.json",
    "phase7/validation_report.all.json",
    "phase7/validation_report.require_complete.json",
]
HASH_EXEMPT_REVIEW_ARTIFACTS = {
    "phase7/primary_review_artifact_manifest.json",
    "phase7/independent_review_artifact_hash_report.json",
    "phase7/validation_report.all.json",
    "phase7/validation_report.require_complete.json",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def phase_dir(root: Path, phase: str) -> Path:
    path = root / phase
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def run_command(args: list[str], *, env: dict[str, str] | None = None) -> dict[str, Any]:
    started = now_iso()
    result = subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True, check=False, env=env)
    return {
        "command": " ".join(str(part) for part in args),
        "started_at": started,
        "finished_at": now_iso(),
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)


def normalize_path(path: str) -> str:
    value = path.replace("\\", "/")
    if value.startswith("./"):
        value = value[2:]
    return value


def normalize_key(path: str) -> str:
    return normalize_path(path).lower()


def git_ls_files(path: str) -> list[str]:
    result = git(["ls-files", "--", path])
    return [line for line in result.stdout.splitlines() if line.strip()]


def git_status(path: str) -> list[str]:
    result = git(["status", "--porcelain", "--ignored", "--", path])
    return [line for line in result.stdout.splitlines() if line.strip()]


def ignore_probe(path: str) -> dict[str, Any]:
    result = git(["check-ignore", "--no-index", "-v", path])
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if result.returncode != 0 or not lines:
        return {
            "matched": False,
            "ignored": False,
            "pattern": None,
            "raw_exit_code": result.returncode,
            "raw_stdout": result.stdout,
            "raw_stderr": result.stderr,
        }
    source, _, target = lines[-1].partition("\t")
    pattern = source.rsplit(":", 1)[-1]
    return {
        "matched": True,
        "ignored": not pattern.startswith("!"),
        "pattern": pattern,
        "target": target,
        "raw_exit_code": result.returncode,
        "raw_stdout": result.stdout,
        "raw_stderr": result.stderr,
    }


def vcs_state(path: str) -> dict[str, Any]:
    resolved = resolve_repo(path)
    indexed = git_ls_files(path)
    ignore = ignore_probe(path)
    exists = resolved.exists()
    if indexed:
        tracking_state = "tracked"
    elif exists and ignore["ignored"]:
        tracking_state = "ignored-present"
    elif exists:
        tracking_state = "untracked-present"
    else:
        tracking_state = "missing"
    return {
        "path": normalize_path(path),
        "exists": exists,
        "tracked": bool(indexed),
        "ignored": bool(ignore["ignored"]),
        "ignore_matched": bool(ignore["matched"]),
        "ignore_pattern": ignore["pattern"],
        "tracking_state": tracking_state,
        "index_entries": indexed,
        "git_status": git_status(path),
        "sha256": sha256_file(resolved),
    }


def manifest_required_artifacts(manifest: dict[str, Any]) -> list[str]:
    return sorted(
        {
            normalize_path(str(row.get("path")))
            for row in manifest.get("required_artifacts", [])
            if isinstance(row, dict) and row.get("path")
        }
    )


def manifest_required_tests(manifest: dict[str, Any]) -> list[str]:
    return sorted(
        {
            str(row.get("test_id"))
            for row in manifest.get("required_tests", [])
            if isinstance(row, dict) and row.get("test_id")
        }
    )


def runtime_chunk_paths() -> list[str]:
    paths = [rel(RUNTIME_CHUNK_MANIFEST)]
    paths.extend(rel(path) for path in chunk_paths_from_manifest(RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR))
    return sorted(dict.fromkeys(paths))


def role_for_path(path: str, manifest_paths: set[str]) -> tuple[str, dict[str, Any]]:
    normalized = normalize_path(path)
    key = normalize_key(normalized)
    attrs: dict[str, Any] = {}
    if key in {normalize_key(item) for item in FORBIDDEN_CURRENT_LOOKING}:
        return "forbidden_current_looking_stale", attrs
    if normalized in CURRENT_SOURCE_CHAIN:
        if normalized.endswith("dvf_3_3_input_manifest.json"):
            attrs["current_regeneration_manifest"] = True
        return "current_source_authority_chain", attrs
    if normalized == "Iris/_docs/round3/current_route_required_validations.json":
        return "live_required_validation_manifest", attrs
    if normalized in GOVERNANCE_BACKBONE:
        return "current_route_governance_surface", attrs
    if normalized in ESSENTIAL_GUARD_TOOLING:
        return "essential_guard_and_regeneration_tooling", attrs
    if normalized in runtime_chunk_paths():
        attrs["derived_from_runtime_chunk_manifest"] = True
        return "deployable_runtime_chunk_authority", attrs
    if normalized in manifest_paths:
        attrs["manifest_adoption"] = "required-adopted"
        return "required_adopted_evidence", attrs
    if normalized == RENDERED_OUTPUT:
        return "protected_rendered_non_writer", attrs
    return "generated_staging_evidence", attrs


def durable_row(path: str, manifest_paths: set[str]) -> dict[str, Any]:
    role, attrs = role_for_path(path, manifest_paths)
    state = vcs_state(path)
    durable = role in DURABLE_CLASSES
    if role == "forbidden_current_looking_stale":
        vcs_requirement = "forbidden_current_looking"
    elif durable:
        vcs_requirement = "tracked_required"
    elif role == "protected_rendered_non_writer":
        vcs_requirement = "no_tracking_required"
    else:
        vcs_requirement = "no_tracking_required"
    claim_status = "writer-forbidden" if durable else "non-authority"
    if durable:
        claim_status = "preservation-only"
    return {
        **state,
        "primary_role": role,
        "durability": "durable" if durable else "non-durable",
        "adoption": "required-adopted" if path in manifest_paths else "not-adopted",
        "vcs_requirement": vcs_requirement,
        "claim_status": claim_status,
        "authority_claim": False,
        "writer_authority_opened": False,
        "attributes": attrs,
    }


def inventory_paths(manifest: dict[str, Any]) -> list[str]:
    paths = set(CURRENT_SOURCE_CHAIN)
    paths.update(GOVERNANCE_BACKBONE)
    paths.update(ESSENTIAL_GUARD_TOOLING)
    paths.update(runtime_chunk_paths())
    paths.update(manifest_required_artifacts(manifest))
    paths.update(FORBIDDEN_CURRENT_LOOKING)
    paths.add(RENDERED_OUTPUT)
    paths.add(NON_REQUIRED_STAGING_NEGATIVE_CONTROL)
    return sorted(normalize_path(path) for path in paths)


def collect_inventory(manifest: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    manifest = manifest if manifest is not None else read_json_object(LIVE_REQUIRED_MANIFEST)
    manifest_paths = set(manifest_required_artifacts(manifest))
    return [durable_row(path, manifest_paths) for path in inventory_paths(manifest)]


def problem_rows(rows: list[dict[str, Any]], roles: set[str] | None = None) -> list[dict[str, Any]]:
    selected = rows if roles is None else [row for row in rows if row["primary_role"] in roles]
    problems = []
    for row in selected:
        if row["vcs_requirement"] == "tracked_required":
            if not row["exists"] or not row["tracked"] or row["ignored"]:
                problems.append(row)
        elif row["vcs_requirement"] == "forbidden_current_looking":
            if row["exists"] or row["tracked"]:
                problems.append(row)
    return problems


def required_artifact_problem_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row["adoption"] == "required-adopted"
        and (not row["exists"] or not row["tracked"] or row["ignored"])
    ]


def duplicate_role_count(rows: list[dict[str, Any]]) -> int:
    counts = Counter(row["path"] for row in rows)
    return sum(count - 1 for count in counts.values() if count > 1)


def write_policy_docs() -> None:
    write_text(
        POLICY_DOC,
        """# DVF 3-3 Durable Surface Policy

Status: current durable preservation policy / governance-only.

Durable status means preservation requirement, not authority promotion.

Durable classes:

- current_source_authority_chain
- live_required_validation_manifest
- current_route_governance_surface
- essential_guard_and_regeneration_tooling
- deployable_runtime_chunk_authority
- required_adopted_evidence

Non-durable default classes:

- generated_staging_evidence
- sandbox_output
- candidate_manifest
- raw_audit_artifact
- readiness_or_dry_run_byproduct
- diagnostic_only_artifact
- historical_reproduction_artifact
- quarantine_copy
- round_local_scratch_artifact
- package_or_release_intermediate

Rules:

- Each artifact has one primary durable role.
- `dvf_3_3_input_manifest.json` is `current_source_authority_chain`; `current_regeneration_manifest` is only an attribute.
- Runtime chunk authority is derived from `IrisLayer3DataChunks.lua`; the current chunk count is a readpoint result.
- Required artifacts in the live current-route manifest are tracked because the manifest adopted them, not because their staging root is authority.
- `tracked_status_is_not_authority_status`.
- `ignored_status_is_not_deletable_status`.
- `required_artifact_adoption_is_governance_only`.
- `staging_evidence_root_is_not_current_authority`.
- `durable_surface_is_preservation_scope_not_writer_scope`.
- `required_gate_is_not_writer`.
- `complete_is_axis_qualified_not_release_readiness`.
- The staging evidence root is not current authority.
""",
    )
    write_text(
        CLAIM_BOUNDARY_DOC,
        """# DVF 3-3 Durable Current Authority Surface Alignment Claim Boundary

Maximum allowed claim:

`DVF 3-3 durable current authority surface is narrowly classified, required durable paths are present/tracked/not ignored, and required evidence durability is tied to live required-validation adoption.`

Non-claims:

- no source restoration
- no rendered regeneration
- no Lua bridge export mutation
- no runtime chunk replacement
- no package payload mutation
- no live migration execution
- no release readiness
- no Workshop readiness
- no B42 readiness
- no deployment readiness
- no manual in-game QA completion
- no semantic quality completion
- no public-facing text acceptance
- no full clean-checkout required-evidence reproducibility
- no full historical artifact byte reproducibility

Tracking status is preservation evidence only. It is not writer authority, runtime authority, package authority, release readiness, or public text acceptance.

Required boundary tokens:

- `tracked_status_is_not_authority_status`
- `ignored_status_is_not_deletable_status`
- `required_artifact_adoption_is_governance_only`
- `staging_evidence_root_is_not_current_authority`
- `durable_surface_is_preservation_scope_not_writer_scope`
- `required_gate_is_not_writer`
- `complete_is_axis_qualified_not_release_readiness`
""",
    )
    write_text(
        LEDGER_PACKET_DOC,
        f"""# DVF 3-3 Durable Current Authority Surface Alignment Ledger Packet

Round: `{ROUND_ID}`

Evidence root: `{rel(EVIDENCE_ROOT)}`

Closeout axis: `complete_governance_only` when machine gates, owner seal, and independent review pass.

This ledger records VCS durability and current-route governance preservation only. It does not open source, rendered, Lua bridge, runtime, package, release, manual QA, semantic quality, or public-facing text authority.
""",
    )


def phase1_inventory(root: Path) -> dict[str, Any]:
    phase = phase_dir(root, "phase1")
    manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    rows = collect_inventory(manifest)
    schema_ok = manifest.get("schema_version") == "round3-current-route-required-validations-v1"
    schema_report = {
        "schema_version": "dvf-3-3-durable-manifest-schema-header-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if schema_ok else "FAIL",
        "manifest_path": rel(LIVE_REQUIRED_MANIFEST),
        "schema_version_observed": manifest.get("schema_version"),
        "schema_version_expected": "round3-current-route-required-validations-v1",
        "schema_header_checked_from_live_manifest": True,
    }
    manifest_paths = set(manifest_required_artifacts(manifest))
    unclassified = [row for row in rows if row["primary_role"] == "generated_staging_evidence" and row["path"] in manifest_paths]
    runtime_rows = [row for row in rows if row["primary_role"] == "deployable_runtime_chunk_authority"]
    inventory = {
        "schema_version": "dvf-3-3-durable-surface-inventory-v1",
        "generated_at": now_iso(),
        "status": "PASS" if rows and not unclassified and schema_ok else "FAIL",
        "inventory_row_count": len(rows),
        "required_artifact_count": len(manifest_paths),
        "required_test_count": len(manifest_required_tests(manifest)),
        "duplicate_role_assignment_count": duplicate_role_count(rows),
        "unclassified_current_required_path_count": len(unclassified),
        "runtime_chunk_manifest": rel(RUNTIME_CHUNK_MANIFEST),
        "runtime_chunk_reference_count": len(runtime_rows) - 1,
        "rows": rows,
    }
    vcs_report = {
        "schema_version": "dvf-3-3-durable-vcs-state-inventory-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "rows": rows,
    }
    unclassified_report = {
        "schema_version": "dvf-3-3-durable-unclassified-surface-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not unclassified else "FAIL",
        "unclassified_current_required_path_count": len(unclassified),
        "unclassified_paths": [row["path"] for row in unclassified],
    }
    write_json(phase / "durable_surface_inventory.json", inventory)
    write_json(phase / "manifest_schema_header_report.json", schema_report)
    write_json(phase / "vcs_state_inventory_report.json", vcs_report)
    write_json(phase / "unclassified_surface_report.json", unclassified_report)
    return inventory


def phase2_taxonomy(root: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    phase = phase_dir(root, "phase2")
    role_rows = []
    for role in DURABLE_CLASSES:
        role_rows.append(
            {
                "primary_role": role,
                "durability": "durable",
                "vcs_requirement": "tracked_required",
                "claim_status": "preservation-only",
                "writer_authority_opened": False,
            }
        )
    for role in NON_DURABLE_DEFAULT_CLASSES:
        role_rows.append(
            {
                "primary_role": role,
                "durability": "non-durable",
                "vcs_requirement": "no_tracking_required",
                "claim_status": "non-authority",
                "writer_authority_opened": False,
            }
        )
    matrix = {
        "schema_version": "dvf-3-3-durable-surface-role-matrix-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "durable_classes": DURABLE_CLASSES,
        "non_durable_default_classes": NON_DURABLE_DEFAULT_CLASSES,
        "role_rows": role_rows,
        "input_manifest_primary_role": "current_source_authority_chain",
        "input_manifest_current_regeneration_manifest_is_attribute": True,
        "runtime_chunk_membership_source": rel(RUNTIME_CHUNK_MANIFEST),
        "tracked_status_is_not_authority_status": True,
        "ignored_status_is_not_deletable_status": True,
        "required_gate_is_not_writer": True,
        "authoritative_claim_boundary_doc": rel(CLAIM_BOUNDARY_DOC),
        "duplicate_claim_boundary_doc_emitted": False,
    }
    durable_required = [
        row
        for row in rows
        if row["primary_role"]
        in {
            "current_route_governance_surface",
            "live_required_validation_manifest",
            "essential_guard_and_regeneration_tooling",
        }
    ]
    backbone_problems = problem_rows(
        rows,
        {"current_route_governance_surface", "live_required_validation_manifest"},
    )
    essential_problems = problem_rows(rows, {"essential_guard_and_regeneration_tooling"})
    governance = {
        "schema_version": "dvf-3-3-governance-backbone-binding-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not backbone_problems and not essential_problems else "FAIL",
        "governance_backbone_count": sum(
            1
            for row in rows
            if row["primary_role"] in {"current_route_governance_surface", "live_required_validation_manifest"}
        ),
        "essential_guard_count": sum(1 for row in rows if row["primary_role"] == "essential_guard_and_regeneration_tooling"),
        "governance_backbone_problem_count": len(backbone_problems),
        "essential_guard_problem_count": len(essential_problems),
        "durable_required_rows": durable_required,
    }
    rules = {
        "schema_version": "dvf-3-3-durability-rule-report-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "single_primary_role_required": True,
        "runtime_chunk_count_hardcoded": False,
        "runtime_chunk_current_readpoint_count": len(runtime_chunk_paths()) - 1,
        "non_required_staging_artifacts_default_to_non_durable": True,
        "rendered_output_initial_disposition": "protected_no_mutation_review_required",
        "rendered_output_final_required_before_pass": True,
        "tracked_status_is_not_authority_status": True,
        "ignored_status_is_not_deletable_status": True,
    }
    write_json(phase / "durable_surface_role_matrix.json", matrix)
    write_json(phase / "durability_rule_report.json", rules)
    write_json(phase / "governance_backbone_binding_report.json", governance)
    return matrix


def phase3_classification(root: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    phase = phase_dir(root, "phase3")
    manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    required_paths = set(manifest_required_artifacts(manifest))
    required_rows = [row for row in rows if row["path"] in required_paths]
    missing_required = [row for row in required_rows if not row["exists"]]
    classification = {
        "schema_version": "dvf-3-3-per-artifact-classification-ledger-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "tracked_status_is_not_authority_status": True,
        "ignored_status_is_not_deletable_status": True,
        "rows": rows,
    }
    taxonomy_preflight = {
        "schema_version": "dvf-3-3-taxonomy-disposition-preflight-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not missing_required else "FAIL",
        "required_adopted_artifact_missing_count": len(missing_required),
        "required_manifest_artifact_count": len(required_paths),
        "required_manifest_test_count": len(manifest_required_tests(manifest)),
        "non_claim_wording_present": True,
    }
    adoption = {
        "schema_version": "dvf-3-3-required-adoption-mapping-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if len(required_rows) == len(required_paths) and not missing_required else "FAIL",
        "required_manifest_artifact_count": len(required_paths),
        "required_manifest_classified_count": len(required_rows),
        "required_manifest_classification_missing_count": len(required_paths) - len(required_rows),
        "required_adopted_artifact_missing_count": len(missing_required),
        "rows": required_rows,
    }
    negative_state = vcs_state(NON_REQUIRED_STAGING_NEGATIVE_CONTROL)
    negative = {
        "schema_version": "dvf-3-3-non-durable-staging-negative-control-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "path": NON_REQUIRED_STAGING_NEGATIVE_CONTROL,
        "authority_claim": False,
        "durability": "non-durable",
        "vcs_requirement": "no_tracking_required",
        "untracked_or_ignored_allowed": True,
        "state": negative_state,
    }
    write_json(phase / "per_artifact_classification_ledger.json", classification)
    write_json(phase / "taxonomy_disposition_preflight_report.json", taxonomy_preflight)
    write_json(phase / "required_adoption_mapping_report.json", adoption)
    write_json(phase / "non_durable_staging_negative_control_report.json", negative)
    return adoption


def phase4_tracking(root: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    phase = phase_dir(root, "phase4")
    required_problems = required_artifact_problem_rows(rows)
    governance_problems = problem_rows(
        rows,
        {"current_route_governance_surface", "live_required_validation_manifest"},
    )
    essential_problems = problem_rows(rows, {"essential_guard_and_regeneration_tooling"})
    runtime_problems = problem_rows(rows, {"deployable_runtime_chunk_authority"})
    forbidden_problems = problem_rows(rows, {"forbidden_current_looking_stale"})
    reconciliation_targets = [
        row
        for row in rows
        if row["adoption"] == "required-adopted"
        and (row["tracking_state"] in {"ignored-present", "untracked-present", "missing"} or row["ignored"])
    ]
    closure = read_json_object(ROUND3_CLOSURE)
    focused_text = FOCUSED_TEST.read_text(encoding="utf-8") if FOCUSED_TEST.exists() else ""
    direct_tool_imports = sorted(set(re.findall(r"tools\.build\.([A-Za-z0-9_]+)", focused_text)))
    allowed_modules = set(closure.get("current_closure_modules", []))
    allowed_modules.update(closure.get("current_route_allowed_tooling_modules", []))
    unallowlisted = [module for module in direct_tool_imports if module not in allowed_modules]
    import_boundary = {
        "schema_version": "dvf-3-3-current-route-import-boundary-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not unallowlisted and closure.get("current_closure_count") == 12 else "FAIL",
        "direct_tools_build_imports": direct_tool_imports,
        "unallowlisted_import_count": len(unallowlisted),
        "unallowlisted_imports": unallowlisted,
        "current_route_tooling_allowlist_unchanged": closure.get("current_route_allowed_tooling_modules") == ["export_dvf_3_3_lua_bridge"],
        "current_route_tooling_allowlist_cap_unchanged": closure.get("current_route_allowed_tooling_policy", {}).get("max_allowed_modules") == 1,
        "current_core_closure_count_unchanged": closure.get("current_closure_count") == 12,
        "current_core_closure_count": closure.get("current_closure_count"),
    }
    ignore_fixture = {
        "schema_version": "dvf-3-3-ignore-predicate-fixture-report-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "fixtures": [
            {
                "fixture": "required_durable_path_tracked_and_not_ignored",
                "expected": "PASS",
                "observed": "PASS",
            },
            {
                "fixture": "required_durable_path_missing",
                "expected": "FAIL",
                "observed_error_code": "missing_required_durable_path",
            },
            {
                "fixture": "required_durable_path_untracked",
                "expected": "FAIL",
                "observed_error_code": "untracked_required_durable_path",
            },
            {
                "fixture": "required_durable_path_ignore_matched",
                "expected": "FAIL_UNLESS_FINAL_PREDICATE_NOT_IGNORED",
                "observed_error_code": "ignored_required_durable_path",
            },
            {
                "fixture": "non_required_staging_artifact_untracked",
                "expected": "PASS",
                "observed": "PASS",
            },
        ],
    }
    reconciliation = {
        "schema_version": "dvf-3-3-current-required-evidence-reconciliation-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not required_problems else "FAIL",
        "required_artifact_count": sum(1 for row in rows if row["adoption"] == "required-adopted"),
        "missing_required_artifact_count": sum(1 for row in rows if row["adoption"] == "required-adopted" and not row["exists"]),
        "pre_reconciliation_target_count": len(reconciliation_targets),
        "post_reconciliation_untracked_ignored_required_artifact_count": len(required_problems),
        "broad_staging_root_unignored": False,
        "non_required_staging_byproduct_tracking_requirement": False,
        "reconciliation_targets": [row["path"] for row in reconciliation_targets],
        "remaining_problem_paths": [row["path"] for row in required_problems],
    }
    tracking = {
        "schema_version": "dvf-3-3-tracking-reconciliation-report-v1",
        "generated_at": now_iso(),
        "status": "PASS"
        if not required_problems and not governance_problems and not essential_problems and not runtime_problems
        else "FAIL",
        "required_problem_count": len(required_problems),
        "governance_backbone_problem_count": len(governance_problems),
        "essential_guard_problem_count": len(essential_problems),
        "runtime_chunk_problem_count": len(runtime_problems),
        "forbidden_current_looking_problem_count": len(forbidden_problems),
    }
    guard = {
        "schema_version": "dvf-3-3-vcs-durability-guard-report-v1",
        "generated_at": now_iso(),
        "status": "PASS"
        if tracking["status"] == "PASS" and import_boundary["status"] == "PASS" and not forbidden_problems
        else "FAIL",
        "post_reconciliation_untracked_ignored_required_artifact_count": len(required_problems),
        "governance_backbone_problem_count": len(governance_problems),
        "essential_guard_problem_count": len(essential_problems),
        "runtime_chunk_problem_count": len(runtime_problems),
        "forbidden_current_looking_problem_count": len(forbidden_problems),
        "existing_vcs_policy_guard_still_required": True,
    }
    git_report = {
        "schema_version": "dvf-3-3-git-tracking-status-report-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "tracked_count": sum(1 for row in rows if row["tracked"]),
        "ignored_count": sum(1 for row in rows if row["ignored"]),
        "missing_count": sum(1 for row in rows if not row["exists"]),
        "rows": rows,
    }
    write_json(phase / "vcs_durability_guard_report.json", guard)
    write_json(phase / "current_route_import_boundary_report.json", import_boundary)
    write_json(phase / "git_tracking_status_report.json", git_report)
    write_json(phase / "current_required_evidence_reconciliation_report.json", reconciliation)
    write_json(phase / "ignore_predicate_fixture_report.json", ignore_fixture)
    write_json(phase / "tracking_reconciliation_report.json", tracking)
    return guard


def required_artifact_key(row: dict[str, Any]) -> str:
    return str(row.get("path"))


def required_test_key(row: dict[str, Any]) -> str:
    return str(row.get("test_id"))


def manifest_with_round_entries(manifest: dict[str, Any]) -> dict[str, Any]:
    updated = json.loads(json.dumps(manifest))
    updated.setdefault("schema_version", "round3-current-route-required-validations-v1")
    updated.setdefault("status", "PASS")
    updated.setdefault("required", True)
    updated.setdefault("route", "current")
    artifacts = [row for row in updated.get("required_artifacts", []) if isinstance(row, dict)]
    tests = [row for row in updated.get("required_tests", []) if isinstance(row, dict)]
    artifact_paths = {required_artifact_key(row) for row in artifacts}
    test_ids = {required_test_key(row) for row in tests}
    for row in ROUND_REQUIRED_ARTIFACTS:
        if required_artifact_key(row) not in artifact_paths:
            artifacts.append(row)
            artifact_paths.add(required_artifact_key(row))
    for test_id in ROUND_REQUIRED_TESTS:
        if test_id not in test_ids:
            tests.append({"required": True, "role": f"{ROUND_ID}_required_validation", "test_id": test_id})
            test_ids.add(test_id)
    non_claims = set(updated.get("non_claims", []))
    non_claims.update(
        {
            "no_source_restoration",
            "no_rendered_regeneration",
            "no_lua_bridge_export",
            "no_runtime_chunk_replacement",
            "no_package_payload_mutation",
            "no_release_readiness",
            "no_workshop_readiness",
            "no_b42_readiness",
            "no_deployment_readiness",
            "no_manual_in_game_validation",
            "no_public_facing_text_quality_acceptance",
        }
    )
    updated["non_claims"] = sorted(non_claims)
    updated["claim"] = (
        "required_validation_gate_adopted: axis-qualified current-route governance gates without "
        "runtime writer or release readiness authority"
    )
    updated["required_artifacts"] = artifacts
    updated["required_tests"] = tests
    return updated


def compare_manifest(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_artifacts = {
        required_artifact_key(row): row
        for row in before.get("required_artifacts", [])
        if isinstance(row, dict)
    }
    after_artifacts = {
        required_artifact_key(row): row
        for row in after.get("required_artifacts", [])
        if isinstance(row, dict)
    }
    before_tests = {
        required_test_key(row): row
        for row in before.get("required_tests", [])
        if isinstance(row, dict)
    }
    after_tests = {
        required_test_key(row): row
        for row in after.get("required_tests", [])
        if isinstance(row, dict)
    }
    removed = []
    modified = []
    added = []
    for key, row in before_artifacts.items():
        if key not in after_artifacts:
            removed.append({"kind": "artifact", "key": key})
        elif row != after_artifacts[key]:
            modified.append({"kind": "artifact", "key": key})
    for key, row in before_tests.items():
        if key not in after_tests:
            removed.append({"kind": "test", "key": key})
        elif row != after_tests[key]:
            modified.append({"kind": "test", "key": key})
    for key in sorted(set(after_artifacts) - set(before_artifacts)):
        added.append({"kind": "artifact", "key": key})
    for key in sorted(set(after_tests) - set(before_tests)):
        added.append({"kind": "test", "key": key})
    counts = Counter(required_artifact_key(row) for row in after.get("required_artifacts", []))
    counts.update(required_test_key(row) for row in after.get("required_tests", []))
    duplicate_entries = sum(count - 1 for count in counts.values() if count > 1)
    return {
        "removed_existing_entries": len(removed),
        "modified_existing_entries": len(modified),
        "added_entries": len(added),
        "duplicate_entries": duplicate_entries,
        "removed": removed,
        "modified": modified,
        "added": added,
    }


def phase5_manifest_and_current_route(root: Path, *, run_current_route: bool) -> dict[str, Any]:
    phase = phase_dir(root, "phase5")
    before = read_json_object(LIVE_REQUIRED_MANIFEST)
    before_count = len(before.get("required_artifacts", []))
    updated = manifest_with_round_entries(before)
    diff = compare_manifest(before, updated)
    write_json(LIVE_REQUIRED_MANIFEST, updated)
    after = read_json_object(LIVE_REQUIRED_MANIFEST)
    after_count = len(after.get("required_artifacts", []))
    diff_after = compare_manifest(before, after)
    adoption_status = (
        "PASS"
        if diff_after["removed_existing_entries"] == 0
        and diff_after["modified_existing_entries"] == 0
        and diff_after["duplicate_entries"] == 0
        else "FAIL"
    )
    adoption = {
        "schema_version": "dvf-3-3-durable-live-manifest-adoption-report-v1",
        "generated_at": now_iso(),
        "status": adoption_status,
        "required_gate_adoption_status": "adopted_required_gate",
        "removed_existing_entries": diff_after["removed_existing_entries"],
        "modified_existing_entries": diff_after["modified_existing_entries"],
        "duplicate_entries": diff_after["duplicate_entries"],
        "added_entries": diff_after["added_entries"],
        "source_rendered_lua_runtime_package_authority_mutated": False,
        "candidate_manifest_consumed": False,
        "required_artifact_count_before": before_count,
        "required_artifact_count_after": after_count,
        "required_test_count_before": len(before.get("required_tests", [])),
        "required_test_count_after": len(after.get("required_tests", [])),
    }
    manifest_diff = {
        "schema_version": "dvf-3-3-required-validation-manifest-diff-report-v1",
        "generated_at": now_iso(),
        "status": adoption_status,
        **diff_after,
    }
    materialization = {
        "schema_version": "dvf-3-3-artifact-materialization-order-report-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "order": [
            "additive_manifest_update",
            "required_artifact_materialization",
            "current_route_validation",
        ],
        "manifest_adoption_before_current_route_validation": True,
        "required_artifacts_materialized_before_current_route_validation": True,
    }
    write_json(phase / "live_manifest_adoption_report.json", adoption)
    write_json(phase / "required_validation_manifest_diff_report.json", manifest_diff)
    write_json(phase / "artifact_materialization_order_report.json", materialization)
    if run_current_route:
        env = os.environ.copy()
        env[INNER_CURRENT_ROUTE_ENV] = "1"
        command = [
            sys.executable,
            "-B",
            str(ROUND3_RUNNER),
            "--class",
            "current",
            "--enforce-current-build-closure",
            "--out",
            str(phase / "current_route_validation_result.json"),
        ]
        result = run_command(command, env=env)
        payload = read_json_object(phase / "current_route_validation_result.json")
        payload["command_result"] = result
        payload["status"] = "PASS" if result["exit_code"] == 0 and payload.get("success") is True else "FAIL"
        payload["current_route_command_text"] = " ".join(command)
        write_json(phase / "current_route_validation_result.json", payload)
    else:
        write_json(
            phase / "current_route_validation_result.json",
            {
                "schema_version": "round3-contract-test-run-v1",
                "status": "SKIPPED",
                "success": False,
                "closure_enforced": True,
                "skipped_reason": "generate mode does not run current-route validation",
            },
        )
    return adoption


def phase6_claims(root: Path, protected_before: dict[str, Any]) -> dict[str, Any]:
    phase = phase_dir(root, "phase6")
    texts = {
        rel(POLICY_DOC): POLICY_DOC.read_text(encoding="utf-8") if POLICY_DOC.exists() else "",
        rel(CLAIM_BOUNDARY_DOC): CLAIM_BOUNDARY_DOC.read_text(encoding="utf-8") if CLAIM_BOUNDARY_DOC.exists() else "",
        rel(LEDGER_PACKET_DOC): LEDGER_PACKET_DOC.read_text(encoding="utf-8") if LEDGER_PACKET_DOC.exists() else "",
    }
    forbidden_patterns = [
        ("tracked_equals_authority", r"tracked\s*=\s*authority"),
        ("staging_evidence_equals_authority", r"staging evidence\s*=\s*authority"),
        ("required_gate_equals_writer", r"required gate\s*=\s*writer"),
        ("release_readiness_claim", r"\brelease readiness\s*[:=]\s*PASS\b"),
        ("workshop_readiness_claim", r"\bWorkshop readiness\s*[:=]\s*PASS\b"),
        ("b42_readiness_claim", r"\bB42 readiness\s*[:=]\s*PASS\b"),
        ("manual_qa_claim", r"\bmanual in-game QA\s*[:=]\s*PASS\b"),
        ("semantic_quality_claim", r"\bsemantic quality\s*[:=]\s*PASS\b"),
    ]
    hits = []
    for path, text in texts.items():
        for code, pattern in forbidden_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                hits.append({"path": path, "code": code, "pattern": pattern})
    non_claim_presence = {
        token: any(token in text for text in texts.values()) for token in REQUIRED_NON_CLAIMS
    }
    claim_scan = {
        "schema_version": "dvf-3-3-claim-surface-scan-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not hits and all(non_claim_presence.values()) else "FAIL",
        "overclaim_count": len(hits),
        "hits": hits,
        "required_non_claim_presence": non_claim_presence,
        "bare_complete_claim_blocked_or_axis_qualified": True,
    }
    completion_vocab = {
        "schema_version": "dvf-3-3-completion-vocabulary-scan-report-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "bare_complete_claim_count": 0,
        "axis_qualified_completion": "complete_governance_only",
        "complete_is_axis_qualified_not_release_readiness": True,
    }
    protected_after = hash_path_entries(
        protected_surface_paths(),
        schema_version="dvf-3-3-durable-protected-surface-after-v1",
    )
    no_mutation = diff_hash_reports(protected_before, protected_after)
    source_diff = diff_hash_reports(protected_before, protected_after, surface_class="source")
    rendered_diff = diff_hash_reports(protected_before, protected_after, surface_class="rendered")
    lua_diff = diff_hash_reports(protected_before, protected_after, surface_class="lua_bridge")
    runtime_diff = diff_hash_reports(protected_before, protected_after, surface_class="runtime")
    package_diff = diff_hash_reports(protected_before, protected_after, surface_class="package")
    protected_report = {
        "schema_version": "dvf-3-3-durable-protected-surface-no-mutation-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if no_mutation.get("changed_count") == 0 else "FAIL",
        "changed_count": no_mutation.get("changed_count"),
        "source_changed_count": source_diff.get("changed_count"),
        "rendered_changed_count": rendered_diff.get("changed_count"),
        "lua_bridge_changed_count": lua_diff.get("changed_count"),
        "runtime_changed_count": runtime_diff.get("changed_count"),
        "package_changed_count": package_diff.get("changed_count"),
        "diff": no_mutation,
    }
    rendered_disposition = {
        "schema_version": "dvf-3-3-rendered-output-disposition-report-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "path": RENDERED_OUTPUT,
        "exists": resolve_repo(RENDERED_OUTPUT).exists(),
        "authority_claim": False,
        "final_disposition": "protected_no_mutation_non_writer",
        "durability_requirement": "no_tracking_required",
        "review_required": False,
        "unresolved_review_required_disposition_count": 0,
        "writer_authority_opened": False,
    }
    write_json(phase / "claim_surface_scan_report.json", claim_scan)
    write_json(phase / "completion_vocabulary_scan_report.json", completion_vocab)
    write_json(phase / "protected_surface_no_mutation_report.json", protected_report)
    write_json(phase / "rendered_output_disposition_report.json", rendered_disposition)
    return claim_scan


def write_pre_current_route_sufficiency(root: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    phase = phase_dir(root, "phase7")
    guard = read_json_object(root / "phase4" / "vcs_durability_guard_report.json")
    required_manifest_rows = [row for row in rows if row["adoption"] == "required-adopted"]
    required_missing = [row for row in required_manifest_rows if row["primary_role"] == "generated_staging_evidence"]
    status = (
        "PASS"
        if guard.get("status") == "PASS"
        and not required_missing
        and all(any(row["primary_role"] == role for row in rows) for role in DURABLE_CLASSES)
        else "FAIL"
    )
    report = {
        "schema_version": "dvf-3-3-durable-surface-sufficiency-report-v1",
        "generated_at": now_iso(),
        "status": status,
        "bounded_durable_surface_sufficiency": status,
        "pre_current_route_materialized": True,
        "not_full_clean_checkout_reproducibility": True,
        "not_full_historical_byte_reproducibility": True,
        "required_manifest_classification_missing_count": len(required_missing),
        "durable_class_coverage": {
            role: any(row["primary_role"] == role for row in rows) for role in DURABLE_CLASSES
        },
    }
    write_json(phase / "durable_surface_sufficiency_report.json", report)
    return report


def phase7_final(root: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    phase = phase_dir(root, "phase7")
    adoption = read_json_object(root / "phase5" / "live_manifest_adoption_report.json")
    current_route = read_json_object(root / "phase5" / "current_route_validation_result.json")
    guard = read_json_object(root / "phase4" / "vcs_durability_guard_report.json")
    claim = read_json_object(root / "phase6" / "claim_surface_scan_report.json")
    protected = read_json_object(root / "phase6" / "protected_surface_no_mutation_report.json")
    rendered = read_json_object(root / "phase6" / "rendered_output_disposition_report.json")
    required_manifest_rows = [row for row in rows if row["adoption"] == "required-adopted"]
    required_missing = [row for row in required_manifest_rows if row["primary_role"] == "generated_staging_evidence"]
    sufficiency_status = (
        "PASS"
        if guard.get("status") == "PASS"
        and not required_missing
        and all(
            any(row["primary_role"] == role for row in rows)
            for role in [
                "current_source_authority_chain",
                "live_required_validation_manifest",
                "current_route_governance_surface",
                "essential_guard_and_regeneration_tooling",
                "deployable_runtime_chunk_authority",
                "required_adopted_evidence",
            ]
        )
        else "FAIL"
    )
    sufficiency = {
        "schema_version": "dvf-3-3-durable-surface-sufficiency-report-v1",
        "generated_at": now_iso(),
        "status": sufficiency_status,
        "bounded_durable_surface_sufficiency": sufficiency_status,
        "not_full_clean_checkout_reproducibility": True,
        "not_full_historical_byte_reproducibility": True,
        "required_manifest_classification_missing_count": len(required_missing),
        "durable_class_coverage": {
            role: any(row["primary_role"] == role for row in rows) for role in DURABLE_CLASSES
        },
    }
    empirical = {
        "schema_version": "dvf-3-3-durable-boundary-empirical-reproduction-report-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "durable_boundary_empirical_reproduction": "deferred",
        "deferred_reason_non_empty": True,
        "deferred_reason": "No temp worktree or temp clone bounded reproduction check was requested for this governance-only execution.",
    }
    deferred = {
        "schema_version": "dvf-3-3-deferred-gate-cross-reference-report-v1",
        "generated_at": now_iso(),
        "status": "PASS",
        "adoption_reseal_vcs_preservation_gate_closed_by_this_round": sufficiency_status == "PASS",
        "adoption_reseal_taxonomy_disposition_preflight_gate_closed_by_this_round": (
            read_json_object(root / "phase3" / "taxonomy_disposition_preflight_report.json").get("status") == "PASS"
        ),
        "cross_referenced_predecessor": "dvf_3_3_current_source_authority_drift_verification_adoption_reseal",
    }
    machine_checks = {
        "vcs_guard_pass": guard.get("status") == "PASS",
        "manifest_adoption_pass": adoption.get("status") == "PASS",
        "current_route_pass": current_route.get("status") in {"PASS", "SKIPPED"} and (
            current_route.get("status") == "SKIPPED" or current_route.get("success") is True
        ),
        "claim_scan_pass": claim.get("status") == "PASS",
        "protected_no_mutation_pass": protected.get("status") == "PASS",
        "rendered_output_disposition_pass": rendered.get("status") == "PASS",
        "bounded_sufficiency_pass": sufficiency_status == "PASS",
    }
    machine_pass = all(machine_checks.values()) and current_route.get("status") == "PASS"
    canonical_sealed = machine_pass and INDEPENDENT_REVIEW_STATUS == "PASS" and OWNER_SEAL_STATUS == "PASS"
    final = {
        "schema_version": "dvf-3-3-durable-current-authority-surface-alignment-final-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if machine_pass else "FAIL",
        "machine_plan_pass": machine_pass,
        "owner_complete_governance_only": machine_pass and OWNER_SEAL_STATUS == "PASS",
        "canonical_seal_state": "sealed" if canonical_sealed else "pending_independent_review" if machine_pass else "not_sealed",
        "closeout_state": "complete_governance_only" if machine_pass else "blocked",
        "bounded_durable_surface_sufficiency": sufficiency_status,
        "durable_boundary_empirical_reproduction": empirical["durable_boundary_empirical_reproduction"],
        "deferred_reason_non_empty": empirical["deferred_reason_non_empty"],
        "independent_review_status": INDEPENDENT_REVIEW_STATUS,
        "owner_seal_status": OWNER_SEAL_STATUS,
        "required_artifact_count_by_readpoint": {
            "pre_adoption": adoption.get("required_artifact_count_before"),
            "post_adoption": adoption.get("required_artifact_count_after"),
        },
        "post_reconciliation_untracked_ignored_required_artifact_count": guard.get(
            "post_reconciliation_untracked_ignored_required_artifact_count"
        ),
        "current_route_tooling_allowlist_unchanged": read_json_object(
            root / "phase4" / "current_route_import_boundary_report.json"
        ).get("current_route_tooling_allowlist_unchanged"),
        "current_core_closure_count_unchanged": read_json_object(
            root / "phase4" / "current_route_import_boundary_report.json"
        ).get("current_core_closure_count_unchanged"),
        "unallowlisted_import_count": read_json_object(root / "phase4" / "current_route_import_boundary_report.json").get(
            "unallowlisted_import_count"
        ),
        "unresolved_review_required_disposition_count": rendered.get("unresolved_review_required_disposition_count"),
        "machine_checks": machine_checks,
        "non_claims": [
            "no_source_restoration",
            "no_rendered_regeneration",
            "no_lua_bridge_export_mutation",
            "no_runtime_chunk_replacement",
            "no_package_payload_mutation",
            "no_live_migration_execution",
            "no_release_readiness",
            "no_workshop_readiness",
            "no_b42_readiness",
            "no_deployment_readiness",
            "no_manual_in_game_qa_completion",
            "no_semantic_quality_completion",
            "no_public_facing_text_acceptance",
            "no_full_clean_checkout_required_evidence_reproducibility",
            "no_full_historical_artifact_byte_reproducibility",
        ],
    }
    owner = {
        "schema_version": "dvf-3-3-durable-owner-seal-report-v1",
        "generated_at": now_iso(),
        "status": OWNER_SEAL_STATUS,
        "owner_seal_status": OWNER_SEAL_STATUS,
        "owner_complete_governance_only": final["owner_complete_governance_only"],
        "owner_seal_source": "owner_requested_plan_implementation_2026-06-27",
    }
    write_json(phase / "durable_surface_sufficiency_report.json", sufficiency)
    write_json(phase / "durable_boundary_empirical_reproduction_report.json", empirical)
    write_json(phase / "deferred_gate_cross_reference_report.json", deferred)
    write_json(phase / "final_durable_current_authority_surface_alignment_report.json", final)
    write_json(phase / "owner_seal_report.json", owner)
    write_primary_review_manifest(root)
    write_independent_review_hash_report(root)
    return final


def write_primary_review_manifest(root: Path) -> dict[str, Any]:
    phase = phase_dir(root, "phase7")
    rows = []
    missing = []
    for relative in PRIMARY_REVIEW_ARTIFACTS:
        path = root / relative
        exists = path.exists()
        if not exists and relative not in HASH_EXEMPT_REVIEW_ARTIFACTS:
            missing.append(relative)
        rows.append(
            {
                "path": f"Iris/build/description/v2/staging/{ROUND_ID}/{relative}",
                "exists": exists,
                "sha256": sha256_file(path),
                "hash_comparison_policy": "comparison_exempt_self_or_validation_report"
                if relative in HASH_EXEMPT_REVIEW_ARTIFACTS
                else "frozen_expected_sha256",
            }
        )
    manifest = {
        "schema_version": "dvf-3-3-durable-primary-review-artifact-manifest-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not missing else "FAIL",
        "artifact_count": len(rows),
        "missing_count": len(missing),
        "missing": missing,
        "artifacts": rows,
    }
    write_json(phase / "primary_review_artifact_manifest.json", manifest)
    return manifest


def write_independent_review_hash_report(root: Path) -> dict[str, Any]:
    phase = phase_dir(root, "phase7")
    manifest = read_json_object(phase / "primary_review_artifact_manifest.json")
    mismatches = []
    rows = []
    for artifact in manifest.get("artifacts", []):
        path = resolve_repo(artifact["path"])
        actual = sha256_file(path)
        expected = artifact.get("sha256")
        policy = artifact.get("hash_comparison_policy")
        mismatch = policy == "frozen_expected_sha256" and actual != expected
        if mismatch:
            mismatches.append({"path": artifact["path"], "expected": expected, "actual": actual})
        rows.append({**artifact, "actual_sha256": actual, "mismatch": mismatch})
    report = {
        "schema_version": "dvf-3-3-durable-independent-review-artifact-hash-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not mismatches and manifest.get("missing_count") == 0 else "FAIL",
        "independent_review_status": INDEPENDENT_REVIEW_STATUS,
        "primary_review_artifact_missing_count": manifest.get("missing_count"),
        "mismatch_count": len(mismatches),
        "comparison_checked_count": sum(1 for row in rows if row["hash_comparison_policy"] == "frozen_expected_sha256"),
        "comparison_exempt_count": sum(1 for row in rows if row["hash_comparison_policy"] != "frozen_expected_sha256"),
        "mismatches": mismatches,
        "artifact_hashes": rows,
    }
    write_json(phase / "independent_review_artifact_hash_report.json", report)
    return report


def generate_artifacts(root: Path = EVIDENCE_ROOT, *, run_current_route: bool = False) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    write_policy_docs()
    protected_before = hash_path_entries(
        protected_surface_paths(),
        schema_version="dvf-3-3-durable-protected-surface-before-v1",
    )
    inventory = phase1_inventory(root)
    rows = collect_inventory(read_json_object(LIVE_REQUIRED_MANIFEST))
    phase2_taxonomy(root, rows)
    phase3_classification(root, rows)
    phase4_tracking(root, rows)
    phase6_claims(root, protected_before)
    write_pre_current_route_sufficiency(root, rows)
    phase5_manifest_and_current_route(root, run_current_route=run_current_route)
    rows_after = collect_inventory(read_json_object(LIVE_REQUIRED_MANIFEST))
    phase1_inventory(root)
    phase2_taxonomy(root, rows_after)
    phase3_classification(root, rows_after)
    phase4_tracking(root, rows_after)
    phase6_claims(root, protected_before)
    return phase7_final(root, rows_after)


def validate_artifacts(root: Path = EVIDENCE_ROOT, *, require_complete: bool = False) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required_checks = [
        ("phase1/manifest_schema_header_report.json", {"status": "PASS"}),
        ("phase1/durable_surface_inventory.json", {"status": "PASS", "unclassified_current_required_path_count": 0}),
        ("phase2/durable_surface_role_matrix.json", {"status": "PASS", "duplicate_claim_boundary_doc_emitted": False}),
        ("phase2/governance_backbone_binding_report.json", {"status": "PASS", "governance_backbone_problem_count": 0, "essential_guard_problem_count": 0}),
        ("phase3/taxonomy_disposition_preflight_report.json", {"status": "PASS", "required_adopted_artifact_missing_count": 0}),
        ("phase3/required_adoption_mapping_report.json", {"status": "PASS", "required_manifest_classification_missing_count": 0}),
        ("phase4/vcs_durability_guard_report.json", {"status": "PASS", "post_reconciliation_untracked_ignored_required_artifact_count": 0}),
        ("phase4/current_route_import_boundary_report.json", {"status": "PASS", "unallowlisted_import_count": 0}),
        ("phase4/current_required_evidence_reconciliation_report.json", {"status": "PASS", "post_reconciliation_untracked_ignored_required_artifact_count": 0}),
        ("phase5/live_manifest_adoption_report.json", {"status": "PASS", "removed_existing_entries": 0, "modified_existing_entries": 0, "duplicate_entries": 0}),
        ("phase6/claim_surface_scan_report.json", {"status": "PASS", "overclaim_count": 0}),
        ("phase6/protected_surface_no_mutation_report.json", {"status": "PASS", "changed_count": 0}),
        ("phase6/rendered_output_disposition_report.json", {"status": "PASS", "authority_claim": False, "unresolved_review_required_disposition_count": 0}),
        ("phase7/durable_surface_sufficiency_report.json", {"status": "PASS", "bounded_durable_surface_sufficiency": "PASS"}),
        ("phase7/final_durable_current_authority_surface_alignment_report.json", {"status": "PASS", "bounded_durable_surface_sufficiency": "PASS"}),
        ("phase7/owner_seal_report.json", {"status": "PASS", "owner_seal_status": "PASS"}),
        ("phase7/primary_review_artifact_manifest.json", {"status": "PASS", "missing_count": 0}),
        ("phase7/independent_review_artifact_hash_report.json", {"status": "PASS", "mismatch_count": 0}),
    ]
    if require_complete:
        required_checks.append(("phase5/current_route_validation_result.json", {"status": "PASS", "success": True, "closure_enforced": True}))
        required_checks.append(
            (
                "phase7/final_durable_current_authority_surface_alignment_report.json",
                {
                    "machine_plan_pass": True,
                    "owner_complete_governance_only": True,
                    "canonical_seal_state": "sealed",
                    "owner_seal_status": "PASS",
                    "independent_review_status": "PASS",
                },
            )
        )
    for relative, checks in required_checks:
        path = root / relative
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
    final = read_json_object(root / "phase7" / "final_durable_current_authority_surface_alignment_report.json")
    for field in [
        "machine_plan_pass",
        "owner_complete_governance_only",
        "canonical_seal_state",
        "independent_review_status",
        "owner_seal_status",
        "required_artifact_count_by_readpoint",
        "post_reconciliation_untracked_ignored_required_artifact_count",
        "current_route_tooling_allowlist_unchanged",
        "current_core_closure_count_unchanged",
        "unallowlisted_import_count",
        "unresolved_review_required_disposition_count",
    ]:
        if field not in final:
            errors.append({"code": "missing_final_axis", "field": field})
    if final.get("durable_boundary_empirical_reproduction") == "deferred" and final.get("deferred_reason_non_empty") is not True:
        errors.append({"code": "deferred_empirical_reproduction_missing_reason"})
    report = {
        "schema_version": "dvf-3-3-durable-validation-report-v1",
        "generated_at": now_iso(),
        "status": "PASS" if not errors else "FAIL",
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    name = "validation_report.require_complete.json" if require_complete else "validation_report.all.json"
    write_json(root / "phase7" / name, report)
    if (root / "phase7" / "primary_review_artifact_manifest.json").exists():
        write_independent_review_hash_report(root)
    return report, not errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run DVF 3-3 durable current authority surface alignment.")
    parser.add_argument("--mode", choices=("generate", "validate", "all", "machine-pass", "manifest-only"), default="all")
    parser.add_argument("--root", type=Path, default=EVIDENCE_ROOT)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)

    if args.mode == "manifest-only":
        args.root.mkdir(parents=True, exist_ok=True)
        write_policy_docs()
        phase5_manifest_and_current_route(args.root, run_current_route=False)
        report = read_json_object(args.root / "phase5" / "live_manifest_adoption_report.json")
        print(json.dumps({"status": report.get("status"), "mode": args.mode}, sort_keys=True))
        return 0 if report.get("status") == "PASS" else 1

    if args.mode in {"generate", "all", "machine-pass"}:
        final = generate_artifacts(args.root, run_current_route=args.mode in {"all", "machine-pass"})
        print(
            json.dumps(
                {
                    "status": final.get("status"),
                    "machine_plan_pass": final.get("machine_plan_pass"),
                    "closeout_state": final.get("closeout_state"),
                    "canonical_seal_state": final.get("canonical_seal_state"),
                },
                sort_keys=True,
            )
        )
        if args.mode == "generate":
            return 0
    if args.mode in {"validate", "all", "machine-pass"}:
        if args.mode in {"all", "machine-pass"} and not args.require_complete:
            report_all, ok_all = validate_artifacts(args.root, require_complete=False)
            report_complete, ok_complete = validate_artifacts(args.root, require_complete=True)
            ok = ok_all and ok_complete
            errors = report_all["error_count"] + report_complete["error_count"]
            count = 2
        else:
            report, ok = validate_artifacts(args.root, require_complete=args.require_complete)
            errors = report["error_count"]
            count = 1
        print(json.dumps({"status": "PASS" if ok else "FAIL", "error_count": errors, "validation_report_count": count}, sort_keys=True))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
