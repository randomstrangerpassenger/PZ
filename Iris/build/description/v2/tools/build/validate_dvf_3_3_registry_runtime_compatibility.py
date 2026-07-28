#!/usr/bin/env python3
"""Standalone fail-closed validator for DVF 3.3 registry compatibility."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence


TOOLS_ROOT = Path(__file__).resolve().parent
V2_ROOT = TOOLS_ROOT.parents[1]
REPO_ROOT = TOOLS_ROOT.parents[5]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import dvf_3_3_registry_runtime_compatibility as rtc
from tools.build import dvf_3_3_registry_runtime_compatibility_closeout as rtc_closeout


ROUND_ID = rtc.ROUND_ID
DEFAULT_REQUIRED_MANIFEST = (
    REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
)
CURRENT_FACTS = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
REQUIRED_ROLES = {
    "policy",
    "identity_field_exclusions",
    "current_collision_disposition",
    "plan_contract_approval",
    "collision_owner_disposition",
    "phase0_contract_review",
}
PROMOTION_ROLES = {
    "policy",
    "exclusion",
    "disposition",
    "plan_contract_approval",
    "collision_owner_disposition",
    "phase0_contract_review",
    "candidate_binding",
    "package_guard_contract",
    "implementation_toolchain",
    "pre_promotion_toolchain_freshness",
    "pre_adoption_machine_result",
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise rtc.CompatibilityError(
            "required_json_invalid",
            f"Cannot read JSON {path}: {exc}",
        ) from exc
    if not isinstance(value, dict):
        raise rtc.CompatibilityError(
            "required_json_not_object",
            f"JSON root must be an object: {path}",
        )
    return value


def reject_stale_current_source_alignment(
    selection: dict[str, Any],
    *,
    isolated_candidate_probe: bool,
) -> None:
    alignment = selection.get("current_source_alignment")
    if alignment is None:
        return
    if not isinstance(alignment, dict):
        raise rtc.CompatibilityError(
            "registry_runtime_compatibility_current_source_alignment_invalid",
            "Current-source alignment marker is not an object",
        )
    if alignment.get("state") != "stale_requires_successor_rtc":
        return
    if isolated_candidate_probe:
        if alignment.get("isolated_successor_candidate_probe_allowed") is not True:
            raise rtc.CompatibilityError(
                "registry_runtime_compatibility_current_source_stale",
                "Successor candidate probing is not allowed by the marker",
            )
        return
    expected_path = alignment.get("applies_when_current_facts_path")
    expected_sha256 = alignment.get("applies_when_current_facts_sha256")
    if (
        expected_path
        != "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
        or not isinstance(expected_sha256, str)
        or len(expected_sha256) != 64
        or not CURRENT_FACTS.is_file()
    ):
        raise rtc.CompatibilityError(
            "registry_runtime_compatibility_current_source_alignment_invalid",
            "Current-source alignment marker is incomplete",
        )
    if rtc.sha256_file(CURRENT_FACTS) == expected_sha256:
        raise rtc.CompatibilityError(
            "registry_runtime_compatibility_current_source_stale",
            "Current facts require a successor Registry Runtime Compatibility closure",
        )


def validate_toolchain_freshness(path: Path) -> dict[str, Any]:
    manifest = read_json(path)
    rows = manifest.get("rows")
    if (
        manifest.get("schema_version")
        != "rtc-implementation-toolchain-manifest-v1"
        or not isinstance(rows, list)
        or manifest.get("row_count") != len(rows)
        or manifest.get("unclassified_tool_dependency_count") != 0
    ):
        raise rtc.CompatibilityError(
            "implementation_toolchain_manifest_invalid",
            "Durable implementation toolchain manifest is incomplete",
        )
    drift: list[str] = []
    missing: list[str] = []
    untracked: list[str] = []
    ignored: list[str] = []
    for row in rows:
        relative = str(row.get("path", ""))
        current = contained_relative(REPO_ROOT, relative)
        if not current.is_file():
            missing.append(relative)
            continue
        if (
            current.stat().st_size != row.get("byte_count")
            or rtc.sha256_file(current) != row.get("sha256")
        ):
            drift.append(relative)
        if row.get("tracked") is not True or not rtc.git_tracked(
            REPO_ROOT,
            current,
        ):
            untracked.append(relative)
        if (
            row.get("not_ignored") is not True
            or rtc.git_ignored(REPO_ROOT, [relative])
        ):
            ignored.append(relative)
    if drift or missing or untracked or ignored:
        raise rtc.CompatibilityError(
            "implementation_toolchain_freshness_failed",
            "Required-gate toolchain drift: "
            f"drift={drift}, missing={missing}, untracked={untracked}, "
            f"ignored={ignored}",
        )
    return {
        "implementation_toolchain_manifest_sha256": rtc.sha256_file(path),
        "implementation_toolchain_row_count": len(rows),
        "implementation_toolchain_drift_count": 0,
        "required_tool_missing_count": 0,
        "required_tool_untracked_count": 0,
        "required_tool_ignored_count": 0,
        "unclassified_tool_dependency_count": 0,
    }


def validate_durable_bundle(
    *,
    bundle_root: Path,
    bundle_manifest_path: Path,
    selection: dict[str, Any],
    expected_lifecycle_state: str,
) -> dict[str, Any]:
    manifest = read_json(bundle_manifest_path)
    rows = manifest.get("rows")
    bundle_id = str(selection.get("bundle_id", ""))
    if (
        manifest.get("schema_version") != "rtc-durable-bundle-manifest-v1"
        or manifest.get("bundle_id") != bundle_id
        or bundle_root.name != bundle_id
        or manifest.get("promotion_role_count") != 11
        or not isinstance(rows, list)
        or len(rows) != 11
        or manifest.get("all_source_destination_bytes_equal") is not True
    ):
        raise rtc.CompatibilityError(
            "durable_bundle_manifest_invalid",
            "Selected durable bundle does not satisfy the eleven-role contract",
        )
    roles = {row.get("role") for row in rows}
    destinations = [str(row.get("destination_path", "")) for row in rows]
    if roles != PROMOTION_ROLES or len(set(destinations)) != 11:
        raise rtc.CompatibilityError(
            "durable_bundle_role_set_invalid",
            "Selected durable bundle roles or destinations differ",
        )
    if (
        not rtc.git_tracked(REPO_ROOT, bundle_manifest_path)
        or rtc.git_ignored(
            REPO_ROOT,
            [rtc.normalized_relative(REPO_ROOT, bundle_manifest_path)],
        )
    ):
        raise rtc.CompatibilityError(
            "durable_bundle_manifest_visibility_invalid",
            "Selected durable bundle manifest must be tracked and not ignored",
        )
    for row in rows:
        destination = contained_relative(
            bundle_root,
            str(row["destination_path"]),
        )
        relative = rtc.normalized_relative(REPO_ROOT, destination)
        if (
            not destination.is_file()
            or destination.stat().st_size != row.get("byte_count")
            or rtc.sha256_file(destination) != row.get("destination_sha256")
            or row.get("source_sha256") != row.get("destination_sha256")
            or row.get("byte_parity") is not True
        ):
            raise rtc.CompatibilityError(
                "durable_bundle_destination_drift",
                f"Durable bundle destination differs: {destination}",
            )
        if (
            not rtc.git_tracked(REPO_ROOT, destination)
            or rtc.git_ignored(REPO_ROOT, [relative])
        ):
            raise rtc.CompatibilityError(
                "durable_bundle_destination_visibility_invalid",
                f"Durable bundle destination is not tracked and visible: {destination}",
            )
    lifecycle_ledger = (
        REPO_ROOT
        / "Iris"
        / "_docs"
        / "round3"
        / "registry_runtime_compatibility"
        / "bundle_lifecycle_events.jsonl"
    )
    if (
        not lifecycle_ledger.is_file()
        or not rtc.git_tracked(REPO_ROOT, lifecycle_ledger)
        or rtc.git_ignored(
            REPO_ROOT,
            [rtc.normalized_relative(REPO_ROOT, lifecycle_ledger)],
        )
    ):
        raise rtc.CompatibilityError(
            "bundle_lifecycle_ledger_visibility_invalid",
            "Bundle lifecycle ledger must be tracked and not ignored",
        )
    previous_hash = "0" * 64
    selected_events: list[dict[str, Any]] = []
    for sequence, raw_line in enumerate(
        lifecycle_ledger.read_bytes().splitlines(keepends=True),
        1,
    ):
        if not raw_line.endswith(b"\n"):
            raise rtc.CompatibilityError(
                "bundle_lifecycle_truncated_line",
                f"Bundle lifecycle event {sequence} lacks LF",
            )
        event = json.loads(raw_line.decode("utf-8"))
        if (
            event.get("event_sequence") != sequence
            or event.get("previous_event_sha256") != previous_hash
        ):
            raise rtc.CompatibilityError(
                "bundle_lifecycle_hash_chain_break",
                f"Bundle lifecycle event chain broke at {sequence}",
            )
        record_path = contained_relative(
            REPO_ROOT,
            str(event.get("record_path", "")),
        )
        record = read_json(record_path)
        if (
            not record_path.is_file()
            or rtc.sha256_file(record_path) != event.get("record_sha256")
            or record.get("bundle_id") != event.get("bundle_id")
            or record.get("current_state") != event.get("current_state")
            or record.get("previous_event_sha256") != previous_hash
            or (
                event.get("bundle_id") == bundle_id
                and record.get("bundle_manifest_sha256")
                != selection.get("bundle_manifest_sha256")
            )
        ):
            raise rtc.CompatibilityError(
                "bundle_lifecycle_record_mismatch",
                f"Bundle lifecycle record differs at event {sequence}",
            )
        if (
            not rtc.git_tracked(REPO_ROOT, record_path)
            or rtc.git_ignored(
                REPO_ROOT,
                [rtc.normalized_relative(REPO_ROOT, record_path)],
            )
        ):
            raise rtc.CompatibilityError(
                "bundle_lifecycle_record_visibility_invalid",
                f"Bundle lifecycle record is not tracked and visible: {record_path}",
            )
        if event.get("bundle_id") == bundle_id:
            selected_events.append(event)
        previous_hash = rtc.sha256_bytes(raw_line)
    if (
        not selected_events
        or selected_events[-1].get("current_state") != expected_lifecycle_state
    ):
        raise rtc.CompatibilityError(
            "bundle_lifecycle_state_mismatch",
            "Selected bundle does not have the required latest lifecycle state",
        )
    toolchain = validate_toolchain_freshness(
        bundle_root / "implementation_toolchain_manifest.json"
    )
    return {
        **toolchain,
        "durable_bundle_role_count": len(rows),
        "durable_bundle_lifecycle_state": expected_lifecycle_state,
        "durable_bundle_lifecycle_event_count": len(selected_events),
    }


def contained_relative(base: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise rtc.CompatibilityError(
            "binding_manifest_path_escape",
            f"Binding leaf must be a contained relative path: {relative}",
        )
    resolved = (base / candidate).resolve()
    try:
        resolved.relative_to(base.resolve())
    except ValueError as exc:
        raise rtc.CompatibilityError(
            "binding_manifest_path_escape",
            f"Binding leaf escapes manifest root: {relative}",
        ) from exc
    return resolved


def validate_binding_contract(
    *,
    policy_context: str,
    policy_path: Path,
    disposition_path: Path,
    binding_path: Path,
) -> dict[str, Any]:
    if policy_context not in {"candidate", "canonical_durable"}:
        raise rtc.CompatibilityError(
            "policy_context_invalid",
            f"Unsupported policy context {policy_context!r}",
        )
    binding = read_json(binding_path)
    if (
        binding.get("schema_version")
        != "rtc-candidate-contract-binding-manifest-v1"
    ):
        raise rtc.CompatibilityError(
            "binding_manifest_schema_invalid",
            f"Unsupported binding schema in {binding_path}",
        )
    leaves = binding.get("leaves")
    if not isinstance(leaves, list) or len(leaves) != 6:
        raise rtc.CompatibilityError(
            "binding_manifest_leaf_count_invalid",
            "Candidate binding must contain exactly six leaves",
        )
    if binding.get("leaf_count") != 6:
        raise rtc.CompatibilityError(
            "binding_manifest_declared_leaf_count_invalid",
            "Candidate binding declared leaf_count must be six",
        )
    paths = [row.get("artifact_path") for row in leaves]
    if paths != sorted(paths) or len(set(paths)) != 6:
        raise rtc.CompatibilityError(
            "binding_manifest_leaf_order_or_duplicate",
            "Candidate binding leaves must be unique and path-sorted",
        )
    roles = {row.get("artifact_role") for row in leaves}
    if roles != REQUIRED_ROLES:
        raise rtc.CompatibilityError(
            "binding_manifest_role_set_invalid",
            f"Candidate binding role set differs: {sorted(roles)}",
        )
    root = binding_path.parent.resolve()
    normalized_root = root.as_posix()
    if policy_context == "candidate":
        marker = (
            "/Iris/build/description/v2/staging/"
            "dvf_3_3_registry_runtime_compatibility/attempts/"
        )
        if marker.lower() not in normalized_root.lower() or not normalized_root.endswith(
            "/phase1/candidate"
        ):
            raise rtc.CompatibilityError(
                "candidate_policy_context_substitution",
                f"Candidate binding is outside an attempt candidate root: {root}",
            )
    else:
        durable_root = (
            REPO_ROOT
            / "Iris"
            / "_docs"
            / "round3"
            / "registry_runtime_compatibility"
            / "bundles"
        ).resolve()
        try:
            relative_root = root.relative_to(durable_root)
        except ValueError as exc:
            raise rtc.CompatibilityError(
                "canonical_policy_context_substitution",
                f"Canonical binding is outside durable bundles: {root}",
            ) from exc
        if len(relative_root.parts) != 1:
            raise rtc.CompatibilityError(
                "canonical_policy_context_substitution",
                f"Canonical binding root must be one versioned bundle: {root}",
            )
    resolved_by_role: dict[str, Path] = {}
    for row in leaves:
        relative = str(row["artifact_path"])
        leaf_path = contained_relative(root, relative)
        if not leaf_path.is_file():
            raise rtc.CompatibilityError(
                "binding_leaf_missing",
                f"Binding leaf is missing: {leaf_path}",
            )
        if leaf_path.stat().st_size != row.get("byte_count"):
            raise rtc.CompatibilityError(
                "binding_leaf_byte_count_mismatch",
                f"Binding leaf byte count drift: {leaf_path}",
            )
        if rtc.sha256_file(leaf_path) != row.get("sha256"):
            raise rtc.CompatibilityError(
                "binding_leaf_hash_mismatch",
                f"Binding leaf hash drift: {leaf_path}",
            )
        payload = read_json(leaf_path)
        if payload.get("schema_version") != row.get("schema_version"):
            raise rtc.CompatibilityError(
                "binding_leaf_schema_mismatch",
                f"Binding leaf schema drift: {leaf_path}",
            )
        record_id = payload.get("record_id", "not_applicable")
        if record_id != row.get("record_id"):
            raise rtc.CompatibilityError(
                "binding_leaf_record_id_mismatch",
                f"Binding leaf record-id drift: {leaf_path}",
            )
        resolved_by_role[str(row["artifact_role"])] = leaf_path
    if policy_path.resolve() != resolved_by_role["policy"]:
        raise rtc.CompatibilityError(
            "policy_path_binding_mismatch",
            "Explicit policy path differs from binding manifest policy leaf",
        )
    if disposition_path.resolve() != resolved_by_role["current_collision_disposition"]:
        raise rtc.CompatibilityError(
            "disposition_path_binding_mismatch",
            "Explicit disposition path differs from binding manifest disposition leaf",
        )
    policy = read_json(policy_path)
    disposition = read_json(disposition_path)
    if policy.get("exact_identity_algorithm") != "decoded_codepoint_exact_v1":
        raise rtc.CompatibilityError(
            "exact_identity_algorithm_mismatch",
            "Policy does not select decoded_codepoint_exact_v1",
        )
    if policy.get("comparison_algorithm") != "ascii_lower_v1":
        raise rtc.CompatibilityError(
            "comparison_algorithm_mismatch",
            "Policy does not select ascii_lower_v1",
        )
    if policy.get("normalization") != "forbidden":
        raise rtc.CompatibilityError(
            "normalization_policy_invalid",
            "Compatibility policy must forbid normalization",
        )
    owner_path = resolved_by_role["collision_owner_disposition"]
    if disposition.get("selected_collision_owner_record_sha256") != rtc.sha256_file(
        owner_path
    ):
        raise rtc.CompatibilityError(
            "disposition_owner_record_hash_mismatch",
            "Disposition does not bind the candidate owner authority bytes",
        )
    approval = read_json(resolved_by_role["plan_contract_approval"])
    owner = read_json(owner_path)
    review = read_json(resolved_by_role["phase0_contract_review"])
    if (
        approval.get("record_state") != "issued"
        or approval.get("owner_explicitly_approved") is not True
        or approval.get("governance_bootstrap_allowed") is not True
        or approval.get("mutable_current_authority_pointer_used") is not False
        or approval.get("technical_failure_waiver_allowed") is not False
        or approval.get("final_plan_review_reviewer_closeout_eligible") is not False
    ):
        raise rtc.CompatibilityError(
            "plan_approval_contract_invalid",
            "Selected plan approval does not preserve fixed owner contracts",
        )
    if (
        owner.get("decision") != "approve_bounded_non_resolving_roles"
        or owner.get("authority_chain_state") != "unique_head"
        or owner.get("comparison_algorithm") != "ascii_lower_v1"
        or owner.get("role_contract", {}).get("role_resolution_power") != "none"
    ):
        raise rtc.CompatibilityError(
            "collision_owner_authority_invalid",
            "Selected collision owner record is not the unique bounded head",
        )
    if (
        review.get("verdict") != "PASS"
        or review.get("authority_chain_state") != "unique_head"
        or review.get("final_independent_review_eligible") is not False
        or review.get("review_checks", {}).get("technical_failure_count") != 0
        or review.get("review_checks", {}).get("implementation_blocker_count")
        != 0
    ):
        raise rtc.CompatibilityError(
            "review2_verdict_not_pass",
            "Candidate Review 2 authority is not an eligible unique PASS head",
        )
    return {
        "policy_context": policy_context,
        "candidate_root": str(root),
        "binding_manifest_sha256": rtc.sha256_file(binding_path),
        "leaf_count": 6,
        "leaf_hashes": {
            role: rtc.sha256_file(path)
            for role, path in sorted(resolved_by_role.items())
        },
        "resolved_by_role": resolved_by_role,
        "policy": policy,
        "disposition": disposition,
    }


def authorized_groups(disposition: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in disposition.get("groups", []):
        roles = group.get("roles", [])
        if (
            group.get("member_count") != 2
            or group.get("reference_role_count") != 1
            or group.get("exception_role_count") != 1
            or group.get("role_resolution_power") != "none"
            or sorted(row.get("role") for row in roles)
            != ["exception", "reference"]
        ):
            raise rtc.CompatibilityError(
                "collision_disposition_multiplicity_invalid",
                f"Invalid bounded role contract: {group}",
            )
        rows.append(
            {
                key: group[key]
                for key in (
                    "collision_group_id",
                    "comparison_key",
                    "member_count",
                    "member_set_sha256",
                    "members",
                )
            }
        )
    rows.sort(key=lambda row: row["collision_group_id"])
    return rows


def unauthorized_group_count(
    observed: list[dict[str, Any]],
    expected: list[dict[str, Any]],
    *,
    require_complete: bool,
) -> int:
    expected_by_id = {row["collision_group_id"]: row for row in expected}
    mismatches = sum(
        expected_by_id.get(row["collision_group_id"]) != row for row in observed
    )
    if require_complete:
        mismatches += len(set(expected_by_id) - {row["collision_group_id"] for row in observed})
    return mismatches


def command_bridge_preflight(args: argparse.Namespace) -> int:
    input_path = Path(args.bridge_preflight_input_manifest).resolve()
    output_path = Path(args.out).resolve()
    inputs = read_json(input_path)
    if inputs.get("schema_version") != "rtc-bridge-preflight-input-v1":
        raise rtc.CompatibilityError(
            "bridge_preflight_input_schema_invalid",
            "Bridge preflight input manifest has an unsupported schema",
        )
    rendered_row = inputs.get("rendered", {})
    rendered_path = Path(rendered_row.get("path", "")).resolve()
    if not rendered_path.is_file():
        raise rtc.CompatibilityError(
            "bridge_preflight_rendered_missing",
            f"Rendered input is missing: {rendered_path}",
        )
    if rendered_path.stat().st_size != rendered_row.get("byte_count"):
        raise rtc.CompatibilityError(
            "bridge_preflight_rendered_byte_count_mismatch",
            "Rendered input byte count differs from explicit manifest",
        )
    if rtc.sha256_file(rendered_path) != rendered_row.get("sha256"):
        raise rtc.CompatibilityError(
            "bridge_preflight_rendered_hash_mismatch",
            "Rendered input hash differs from explicit manifest",
        )
    binding = validate_binding_contract(
        policy_context=args.policy_context,
        policy_path=Path(args.policy).resolve(),
        disposition_path=Path(args.disposition).resolve(),
        binding_path=Path(args.binding_manifest).resolve(),
    )
    if inputs.get("binding_manifest_sha256") != binding[
        "binding_manifest_sha256"
    ]:
        raise rtc.CompatibilityError(
            "bridge_preflight_binding_hash_mismatch",
            "Input manifest does not bind the selected contract manifest",
        )
    records = rtc.load_rendered_surface(rendered_path, repo=REPO_ROOT)
    duplicates = rtc.exact_duplicates(records)
    observed_groups = rtc.collision_groups(records)
    expected_groups = authorized_groups(binding["disposition"])
    unauthorized_count = unauthorized_group_count(
        observed_groups,
        expected_groups,
        require_complete=len(records) == 2105,
    )
    if duplicates:
        raise rtc.CompatibilityError(
            "rendered_exact_duplicate",
            f"Rendered input has decoded exact duplicates: {duplicates}",
        )
    if unauthorized_count:
        raise rtc.CompatibilityError(
            "rendered_unauthorized_comparison_collision",
            "Rendered collision groups differ from selected disposition",
        )
    report = {
        "schema_version": "rtc-bridge-preflight-report-v1",
        "round_id": ROUND_ID,
        "status": "PASS",
        "responsibility_scope": "rendered_and_contract_pre_materialization_only",
        "four_surface_claim_prohibited": True,
        "rendered_path": str(rendered_path),
        "rendered_sha256": rtc.sha256_file(rendered_path),
        "rendered_byte_count": rendered_path.stat().st_size,
        "rendered_ordered_pair_count": len(records),
        "rendered_exact_duplicate_count": 0,
        "rendered_comparison_collision_group_count": len(observed_groups),
        "rendered_unauthorized_collision_count": 0,
        "binding_manifest_sha256": binding["binding_manifest_sha256"],
        "policy_context": args.policy_context,
    }
    rtc.write_json(output_path, report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


def checked_surface_path(row: dict[str, Any], field: str) -> Path:
    path = Path(str(row.get(field, ""))).resolve()
    if not path.exists():
        raise rtc.CompatibilityError(
            "surface_input_missing",
            f"Surface input {field!r} is missing: {path}",
        )
    expected = row.get(f"{field}_sha256")
    if expected and path.is_file() and rtc.sha256_file(path) != expected:
        raise rtc.CompatibilityError(
            "surface_input_hash_mismatch",
            f"Surface input {field!r} hash differs: {path}",
        )
    return path


def validate_four_surfaces(
    *,
    manifest_path: Path,
    policy_context: str,
    policy_path: Path,
    disposition_path: Path,
    binding_path: Path,
) -> dict[str, Any]:
    inputs = read_json(manifest_path)
    if inputs.get("schema_version") != "rtc-compatibility-surface-input-v1":
        raise rtc.CompatibilityError(
            "surface_input_manifest_schema_invalid",
            "Surface input manifest has an unsupported schema",
        )
    binding = validate_binding_contract(
        policy_context=policy_context,
        policy_path=policy_path,
        disposition_path=disposition_path,
        binding_path=binding_path,
    )
    if inputs.get("binding_manifest_sha256") != binding[
        "binding_manifest_sha256"
    ]:
        raise rtc.CompatibilityError(
            "surface_binding_manifest_hash_mismatch",
            "Surface input manifest does not bind the selected contract",
        )
    source_row = inputs["source"]
    source_paths = {
        component: checked_surface_path(source_row, component)
        for component in ("facts", "decisions", "overlay")
    }
    rendered_path = checked_surface_path(inputs["rendered"], "path")
    runtime_manifest = checked_surface_path(inputs["runtime"], "manifest")
    runtime_chunks = Path(inputs["runtime"]["chunks"]).resolve()
    package_manifest = checked_surface_path(inputs["package"], "manifest")
    package_chunks = Path(inputs["package"]["chunks"]).resolve()
    source, source_diagnostics = rtc.load_jsonl_surface(
        source_paths,
        repo=REPO_ROOT,
    )
    rendered = rtc.load_rendered_surface(rendered_path, repo=REPO_ROOT)
    runtime, runtime_inputs = rtc.load_lua_surface(
        surface="runtime",
        manifest_path=runtime_manifest,
        chunk_dir=runtime_chunks,
        repo=REPO_ROOT,
    )
    package, package_inputs = rtc.load_lua_surface(
        surface="package",
        manifest_path=package_manifest,
        chunk_dir=package_chunks,
        repo=REPO_ROOT,
    )
    surfaces = {
        "source": source,
        "rendered": rendered,
        "runtime": runtime,
        "package": package,
    }
    duplicates = {
        surface: rtc.exact_duplicates(records)
        for surface, records in surfaces.items()
    }
    duplicate_count = sum(len(rows) for rows in duplicates.values())
    sets = rtc.compare_surface_sets(surfaces)
    payloads = rtc.compare_runtime_payloads(surfaces)
    observed_groups = rtc.collision_groups(source)
    collision_payloads = rtc.compare_collision_payloads(
        surfaces,
        observed_groups,
    )
    expected_groups = authorized_groups(binding["disposition"])
    collision_mismatch = unauthorized_group_count(
        observed_groups,
        expected_groups,
        require_complete=len(source) == 2105,
    )
    aliases = rtc.exporter_alias_declarations(
        REPO_ROOT
        / "Iris"
        / "build"
        / "description"
        / "v2"
        / "tools"
        / "build"
        / "export_dvf_3_3_lua_bridge.py"
    )
    alias_report = rtc.alias_regression(
        aliases=aliases,
        source_keys={record.decoded_key for record in source},
        baseline_collision_count=len(observed_groups),
    )
    technical_failure_count = (
        duplicate_count
        + len(source_diagnostics["component_set_mismatches"])
        + (0 if sets["source_rendered_runtime_package_exact_keyset_match"] else 1)
        + payloads["runtime_projection_payload_mismatch_count"]
        + collision_payloads["collision_group_payload_mismatch_count"]
        + collision_mismatch
        + alias_report["applied_new_alias_key_count"]
        + alias_report["unexpected_emission_count"]
        + max(0, alias_report["alias_induced_comparison_collision_increase"])
    )
    return {
        "schema_version": "rtc-four-surface-compatibility-report-v1",
        "round_id": ROUND_ID,
        "status": "PASS" if technical_failure_count == 0 else "FAIL",
        "policy_context": policy_context,
        "binding_manifest_sha256": binding["binding_manifest_sha256"],
        "technical_failure_count": technical_failure_count,
        "exact_duplicate_count": duplicate_count,
        "collision_group_count": len(observed_groups),
        "unauthorized_collision_count": collision_mismatch,
        **sets,
        **payloads,
        **collision_payloads,
        **alias_report,
        "runtime_inputs": runtime_inputs,
        "package_inputs": package_inputs,
        "claim_scope": "registry_runtime_compatibility_machine_evidence",
    }


def command_surface_validation(args: argparse.Namespace) -> int:
    output_path = Path(args.out).resolve()
    report = validate_four_surfaces(
        manifest_path=Path(args.surface_input_manifest).resolve(),
        policy_context=args.policy_context,
        policy_path=Path(args.policy).resolve(),
        disposition_path=Path(args.disposition).resolve(),
        binding_path=Path(args.binding_manifest).resolve(),
    )
    rtc.write_json(output_path, report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "PASS" else 2


def validate_selected_attempt_closeout(
    *,
    manifest_path: Path,
    selection: dict[str, Any],
) -> dict[str, Any]:
    attempt_id = str(selection.get("attempt_id", ""))
    event_ledger = (
        REPO_ROOT
        / "Iris"
        / "_docs"
        / "round3"
        / "registry_runtime_compatibility"
        / "attempt_events.jsonl"
    )
    previous_hash = "0" * 64
    selected_events: list[dict[str, Any]] = []
    for sequence, raw_line in enumerate(
        event_ledger.read_bytes().splitlines(keepends=True),
        1,
    ):
        if not raw_line.endswith(b"\n"):
            raise rtc.CompatibilityError(
                "attempt_event_truncated_line",
                f"Attempt event {sequence} lacks LF",
            )
        event = json.loads(raw_line.decode("utf-8"))
        if (
            event.get("event_sequence") != sequence
            or event.get("previous_event_sha256") != previous_hash
        ):
            raise rtc.CompatibilityError(
                "attempt_event_hash_chain_break",
                f"Attempt event chain broke at {sequence}",
            )
        record_path = contained_relative(
            REPO_ROOT,
            str(event.get("record_path", "")),
        )
        if (
            not record_path.is_file()
            or rtc.sha256_file(record_path) != event.get("record_sha256")
            or not rtc.git_tracked(REPO_ROOT, record_path)
            or rtc.git_ignored(
                REPO_ROOT,
                [rtc.normalized_relative(REPO_ROOT, record_path)],
            )
        ):
            raise rtc.CompatibilityError(
                "attempt_event_record_invalid",
                f"Attempt event record is missing, changed, or invisible: {record_path}",
            )
        if event.get("attempt_id") == attempt_id:
            selected_events.append(event)
        previous_hash = rtc.sha256_bytes(raw_line)
    reservation_events = [
        row for row in selected_events if row.get("event_type") == "reservation"
    ]
    terminal_events = [
        row for row in selected_events if row.get("event_type") == "terminal"
    ]
    if len(reservation_events) != 1 or len(terminal_events) > 1:
        raise rtc.CompatibilityError(
            "selected_attempt_event_cardinality_invalid",
            f"Selected attempt event cardinality differs: {attempt_id}",
        )
    if not terminal_events:
        return {
            "selected_attempt_terminal_event_count": 0,
            "selected_attempt_closeout_state": (
                "compatibility_machine_pass_governance_pending"
            ),
            "durable_closeout_required_role_count": 9,
            "durable_closeout_artifact_missing_count": 0,
            "durable_closeout_hash_mismatch_count": 0,
            "independent_review_content_available": False,
            "owner_seal_content_available": False,
            "terminal_seal_content_available": False,
            "terminal_event_before_closeout_commit_count": 0,
        }
    terminal_event = terminal_events[0]
    if (
        terminal_event.get("terminal_state")
        != "registry_runtime_compatibility_canonical_complete"
    ):
        raise rtc.CompatibilityError(
            "selected_live_attempt_terminal_not_canonical",
            "A selected live bundle cannot be governed by a non-canonical terminal",
        )
    terminal_path = contained_relative(
        REPO_ROOT,
        str(terminal_event["record_path"]),
    )
    terminal = read_json(terminal_path)
    packet_path = contained_relative(
        REPO_ROOT,
        str(terminal.get("durable_closeout_packet_manifest_path", "")),
    )
    evidence_path = contained_relative(
        REPO_ROOT,
        str(terminal.get("evidence_manifest_path", "")),
    )
    terminal_seal_path = contained_relative(
        REPO_ROOT,
        str(terminal.get("terminal_hash_seal_path", "")),
    )
    closeout_commit = str(terminal.get("durable_closeout_packet_commit", ""))
    terminal_commit = rtc.git_text(
        REPO_ROOT,
        "log",
        "-1",
        "--format=%H",
        "--",
        rtc.normalized_relative(REPO_ROOT, terminal_path),
    )
    ancestry = subprocess.run(
        [
            "git",
            "-C",
            str(REPO_ROOT),
            "merge-base",
            "--is-ancestor",
            closeout_commit,
            terminal_commit,
        ],
        capture_output=True,
        check=False,
    )
    if (
        not packet_path.is_file()
        or rtc.sha256_file(packet_path)
        != terminal.get("durable_closeout_packet_manifest_sha256")
        or not evidence_path.is_file()
        or rtc.sha256_file(evidence_path)
        != terminal.get("evidence_manifest_sha256")
        or not terminal_seal_path.is_file()
        or rtc.sha256_file(terminal_seal_path)
        != terminal.get("terminal_hash_seal_sha256")
        or closeout_commit == terminal_commit
        or ancestry.returncode != 0
    ):
        raise rtc.CompatibilityError(
            "durable_closeout_terminal_binding_invalid",
            "Terminal does not bind a prior durable closeout commit",
        )
    packet = read_json(packet_path)
    rows = packet.get("rows")
    if (
        packet.get("schema_version")
        != "rtc-durable-closeout-packet-manifest-v1"
        or packet.get("required_role_count") != 9
        or packet.get("artifact_missing_count") != 0
        or packet.get("hash_mismatch_count") != 0
        or not isinstance(rows, list)
        or len(rows) != 9
        or {row.get("role") for row in rows}
        != set(rtc_closeout.NINE_PACKET_ROLES)
    ):
        raise rtc.CompatibilityError(
            "durable_closeout_packet_invalid",
            "Durable closeout packet does not satisfy the nine-role contract",
        )
    closeout_root = packet_path.parent
    role_paths: dict[str, Path] = {}
    for row in rows:
        path = (closeout_root / Path(str(row.get("path", "")))).resolve()
        try:
            path.relative_to(closeout_root.resolve())
        except ValueError as exc:
            raise rtc.CompatibilityError(
                "durable_closeout_path_escape",
                f"Closeout role escapes packet root: {path}",
            ) from exc
        role_paths[str(row["role"])] = path
        if (
            not path.is_file()
            or path.stat().st_size != row.get("byte_count")
            or rtc.sha256_file(path) != row.get("sha256")
            or read_json(path).get("schema_version") != row.get("schema_version")
            or not rtc.git_tracked(REPO_ROOT, path)
            or rtc.git_ignored(
                REPO_ROOT,
                [rtc.normalized_relative(REPO_ROOT, path)],
            )
        ):
            raise rtc.CompatibilityError(
                "durable_closeout_role_invalid",
                f"Durable closeout role is missing, changed, or invisible: {path}",
            )
    final_machine = read_json(role_paths["final_machine_report"])
    independent = read_json(role_paths["independent_review"])
    owner = read_json(role_paths["owner_canonical_seal"])
    final_report = read_json(role_paths["final_compatibility_report"])
    claim_scan = read_json(role_paths["final_claim_scan_report"])
    terminal_seal = read_json(role_paths["terminal_hash_seal"])
    expected_binding = {
        "pre_adoption_live_manifest_sha256": final_machine.get(
            "pre_adoption_live_manifest_sha256"
        ),
        "post_adoption_live_manifest_sha256": rtc.sha256_file(manifest_path),
        "selected_durable_bundle_id": selection.get("bundle_id"),
        "selected_bundle_manifest_sha256": selection.get(
            "bundle_manifest_sha256"
        ),
        "adopted_row_identity": selection.get("adopted_row_identity"),
    }
    binding_artifacts = (
        terminal,
        packet,
        final_machine,
        independent,
        owner,
        final_report,
        claim_scan,
        terminal_seal,
    )
    if any(
        any(artifact.get(field) != value for field, value in expected_binding.items())
        for artifact in binding_artifacts
    ):
        raise rtc.CompatibilityError(
            "durable_closeout_final_binding_mismatch",
            "Closeout artifacts do not bind the selected live identity",
        )
    if (
        final_machine.get("status") != "PASS"
        or final_machine.get("machine_contract_status") != "PASS"
        or independent.get("status") != "PASS"
        or independent.get("verdict") != "PASS"
        or owner.get("owner_seal_status") != "PASS"
        or owner.get("canonical_seal_status") != "PASS"
        or owner.get("final_signoff_status") != "PASS"
        or final_report.get("formal_claim")
        != "Registry Runtime Compatibility PASS"
        or claim_scan.get("formal_claim_count") != 1
        or claim_scan.get("bare_pass_claim_count") != 0
        or claim_scan.get("bare_runtime_compatibility_claim_count") != 0
        or terminal_seal.get("status") != "PASS"
    ):
        raise rtc.CompatibilityError(
            "durable_closeout_governance_invalid",
            "Review, owner seal, final claim, or terminal seal is not PASS",
        )
    return {
        "selected_attempt_terminal_event_count": 1,
        "selected_attempt_closeout_state": (
            "registry_runtime_compatibility_canonical_complete"
        ),
        "durable_closeout_required_role_count": 9,
        "durable_closeout_artifact_missing_count": 0,
        "durable_closeout_hash_mismatch_count": 0,
        "independent_review_content_available": True,
        "owner_seal_content_available": True,
        "terminal_seal_content_available": True,
        "terminal_event_before_closeout_commit_count": 0,
        "durable_closeout_packet_manifest_sha256": rtc.sha256_file(packet_path),
    }


def live_contract_from_manifest(path: Path) -> dict[str, Any]:
    manifest = read_json(path)
    row = manifest.get("registry_runtime_compatibility")
    if not isinstance(row, dict):
        raise rtc.CompatibilityError(
            "compatibility_policy_context_required",
            "Live required manifest has no registry compatibility selection",
        )
    is_candidate_probe = (
        row.get("candidate_manifest_probe") is True
        and row.get("policy_lifecycle_state")
        == "package_guard_active_not_required_gate_adopted"
    )
    reject_stale_current_source_alignment(
        row,
        isolated_candidate_probe=is_candidate_probe,
    )
    if (
        row.get("policy_lifecycle_state") != "live_required_gate_adopted"
        and not is_candidate_probe
    ):
        raise rtc.CompatibilityError(
            "compatibility_policy_context_required",
            "Registry compatibility selection is not live-gate adopted",
        )
    bundle_root = (REPO_ROOT / Path(str(row.get("bundle_root", "")))).resolve()
    manifest_path = bundle_root / "durable_bundle_manifest.json"
    if (
        not manifest_path.is_file()
        or rtc.sha256_file(manifest_path) != row.get("bundle_manifest_sha256")
    ):
        raise rtc.CompatibilityError(
            "live_bundle_manifest_hash_mismatch",
            "Live required manifest does not bind durable bundle bytes",
        )
    lifecycle_state = (
        "package_guard_active_not_required_gate_adopted"
        if is_candidate_probe
        else "live_required_gate_adopted"
    )
    durable_validation = validate_durable_bundle(
        bundle_root=bundle_root,
        bundle_manifest_path=manifest_path,
        selection=row,
        expected_lifecycle_state=lifecycle_state,
    )
    closeout_validation = (
        {
            "selected_attempt_terminal_event_count": 0,
            "selected_attempt_closeout_state": "candidate_manifest_probe",
        }
        if is_candidate_probe
        else validate_selected_attempt_closeout(
            manifest_path=path,
            selection=row,
        )
    )
    return {
        "bundle_root": bundle_root,
        "policy": bundle_root / "registry_runtime_compatibility_policy.json",
        "disposition": bundle_root / "current_collision_disposition.json",
        "binding": bundle_root / "candidate_contract_binding_manifest.json",
        "bundle_manifest": manifest_path,
        "row": row,
        "candidate_probe": is_candidate_probe,
        "durable_validation": durable_validation,
        "closeout_validation": closeout_validation,
    }


def command_required_gate(args: argparse.Namespace) -> int:
    manifest_path = Path(args.required_manifest).resolve()
    output_path = Path(args.out).resolve()
    contract = live_contract_from_manifest(manifest_path)
    required_gate_temp_root = (
        V2_ROOT
        / "staging"
        / "dvf_3_3_registry_runtime_compatibility"
        / "required-gate-temp"
    )
    required_gate_temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="iris-rtc-required-gate-",
        dir=required_gate_temp_root,
    ) as temporary:
        package_data = (
            Path(temporary)
            / "Iris"
            / "media"
            / "lua"
            / "client"
            / "Iris"
            / "Data"
        )
        package_data.mkdir(parents=True)
        live_data = (
            REPO_ROOT
            / "Iris"
            / "media"
            / "lua"
            / "client"
            / "Iris"
            / "Data"
        )
        shutil.copy2(
            live_data / "IrisLayer3DataChunks.lua",
            package_data / "IrisLayer3DataChunks.lua",
        )
        shutil.copytree(
            live_data / "IrisLayer3DataChunks",
            package_data / "IrisLayer3DataChunks",
        )
        surface_manifest = Path(temporary) / "surface-inputs.json"
        source_root = REPO_ROOT / "Iris" / "build" / "description" / "v2"
        rendered = source_root / "output" / "dvf_3_3_rendered.json"
        surface = {
            "schema_version": "rtc-compatibility-surface-input-v1",
            "round_id": ROUND_ID,
            "producer_attempt_id": contract["row"].get("attempt_id"),
            "binding_manifest_sha256": rtc.sha256_file(contract["binding"]),
            "source": {
                "facts": str(source_root / "data" / "dvf_3_3_facts.jsonl"),
                "facts_sha256": rtc.sha256_file(
                    source_root / "data" / "dvf_3_3_facts.jsonl"
                ),
                "decisions": str(source_root / "data" / "dvf_3_3_decisions.jsonl"),
                "decisions_sha256": rtc.sha256_file(
                    source_root / "data" / "dvf_3_3_decisions.jsonl"
                ),
                "overlay": str(source_root / "data" / "dvf_3_3_overlay_support.jsonl"),
                "overlay_sha256": rtc.sha256_file(
                    source_root / "data" / "dvf_3_3_overlay_support.jsonl"
                ),
            },
            "rendered": {
                "path": str(rendered),
                "path_sha256": rtc.sha256_file(rendered),
            },
            "runtime": {
                "manifest": str(live_data / "IrisLayer3DataChunks.lua"),
                "manifest_sha256": rtc.sha256_file(
                    live_data / "IrisLayer3DataChunks.lua"
                ),
                "chunks": str(live_data / "IrisLayer3DataChunks"),
            },
            "package": {
                "manifest": str(package_data / "IrisLayer3DataChunks.lua"),
                "manifest_sha256": rtc.sha256_file(
                    package_data / "IrisLayer3DataChunks.lua"
                ),
                "chunks": str(package_data / "IrisLayer3DataChunks"),
            },
        }
        rtc.write_json(surface_manifest, surface)
        report = validate_four_surfaces(
            manifest_path=surface_manifest,
            policy_context="canonical_durable",
            policy_path=contract["policy"],
            disposition_path=contract["disposition"],
            binding_path=contract["binding"],
        )
    report["schema_version"] = "rtc-required-gate-report-v1"
    report["required_manifest_path"] = rtc.normalized_relative(
        REPO_ROOT,
        manifest_path,
    )
    report["required_manifest_sha256"] = rtc.sha256_file(manifest_path)
    report["resolution_mode"] = (
        "candidate_required_manifest_override"
        if contract["candidate_probe"]
        else "post_adoption_live_manifest_default"
    )
    report["selected_durable_bundle_id"] = contract["row"].get("bundle_id")
    report["selected_bundle_manifest_sha256"] = contract["row"].get(
        "bundle_manifest_sha256"
    )
    report["required_gate_state"] = (
        "not_adopted" if contract["candidate_probe"] else "live_gate_adopted"
    )
    if contract["candidate_probe"]:
        report["candidate_manifest_route_status"] = "PASS"
    report.update(contract["durable_validation"])
    report.update(contract["closeout_validation"])
    rtc.write_json(output_path, report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "PASS" else 2


def command_contract_only(args: argparse.Namespace) -> int:
    binding = validate_binding_contract(
        policy_context=args.policy_context,
        policy_path=Path(args.policy).resolve(),
        disposition_path=Path(args.disposition).resolve(),
        binding_path=Path(args.binding_manifest).resolve(),
    )
    report = {
        "schema_version": "rtc-contract-only-report-v1",
        "round_id": ROUND_ID,
        "status": "PASS",
        "policy_context": args.policy_context,
        "binding_manifest_sha256": binding["binding_manifest_sha256"],
        "leaf_count": binding["leaf_count"],
    }
    rtc.write_json(Path(args.out).resolve(), report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


def command_require_implementation(args: argparse.Namespace) -> int:
    attempt_root = Path(args.attempt_root).resolve()
    required_paths = [
        Path(__file__).resolve(),
        TOOLS_ROOT / "dvf_3_3_registry_runtime_compatibility.py",
        TOOLS_ROOT / "run_dvf_3_3_registry_runtime_compatibility.py",
        TOOLS_ROOT / "export_registry_runtime_records.py",
        REPO_ROOT / "Iris" / "tools" / "inspect_registry_runtime_compatibility.ps1",
        TOOLS_ROOT / "export_dvf_3_3_lua_bridge.py",
        REPO_ROOT / "Iris" / "tools" / "package_iris.ps1",
        attempt_root / "phase0" / "production_integration_gate_report.json",
        attempt_root / "phase0" / "phase0_disposition_verdict.json",
        attempt_root / "phase1" / "candidate" / "candidate_contract_binding_manifest.json",
    ]
    missing = [str(path) for path in required_paths if not path.exists()]
    tracked_required = required_paths[:7]
    untracked = [
        rtc.normalized_relative(REPO_ROOT, path)
        for path in tracked_required
        if path.exists() and not rtc.git_tracked(REPO_ROOT, path)
    ]
    ignored = rtc.git_ignored(
        REPO_ROOT,
        [
            rtc.normalized_relative(REPO_ROOT, path)
            for path in tracked_required
            if path.exists()
        ],
    )
    exporter_text = (TOOLS_ROOT / "export_dvf_3_3_lua_bridge.py").read_text(
        encoding="utf-8"
    )
    forbidden_import_count = sum(
        token in exporter_text
        for token in (
            "import dvf_3_3_registry_runtime_compatibility",
            "from tools.build.dvf_3_3_registry_runtime_compatibility",
        )
    )
    report = {
        "schema_version": "rtc-static-implementation-validation-v1",
        "round_id": ROUND_ID,
        "status": (
            "PASS"
            if not missing and not untracked and not ignored and not forbidden_import_count
            else "FAIL"
        ),
        "required_path_missing_count": len(missing),
        "required_path_missing": missing,
        "required_tool_untracked_count": len(untracked),
        "required_tool_untracked": untracked,
        "required_tool_ignored_count": len(ignored),
        "required_tool_ignored": ignored,
        "exporter_forbidden_analyzer_import_count": forbidden_import_count,
    }
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "PASS" else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--bridge-preflight", action="store_true")
    modes.add_argument("--surface-validation", action="store_true")
    modes.add_argument("--contract-only", action="store_true")
    modes.add_argument("--required-gate", action="store_true")
    modes.add_argument("--require-implementation", action="store_true")
    parser.add_argument("--bridge-preflight-input-manifest")
    parser.add_argument("--surface-input-manifest")
    parser.add_argument("--policy-context")
    parser.add_argument("--policy")
    parser.add_argument("--disposition")
    parser.add_argument("--binding-manifest")
    parser.add_argument("--required-manifest", default=str(DEFAULT_REQUIRED_MANIFEST))
    parser.add_argument("--attempt-root")
    parser.add_argument("--out")
    return parser


def require_arguments(args: argparse.Namespace, names: Sequence[str]) -> None:
    missing = [name for name in names if not getattr(args, name)]
    if missing:
        raise rtc.CompatibilityError(
            "validator_required_argument_missing",
            f"Validator mode is missing arguments: {missing}",
        )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.bridge_preflight:
            require_arguments(
                args,
                (
                    "bridge_preflight_input_manifest",
                    "policy_context",
                    "policy",
                    "disposition",
                    "binding_manifest",
                    "out",
                ),
            )
            return command_bridge_preflight(args)
        if args.surface_validation:
            require_arguments(
                args,
                (
                    "surface_input_manifest",
                    "policy_context",
                    "policy",
                    "disposition",
                    "binding_manifest",
                    "out",
                ),
            )
            return command_surface_validation(args)
        if args.contract_only:
            require_arguments(
                args,
                (
                    "policy_context",
                    "policy",
                    "disposition",
                    "binding_manifest",
                    "out",
                ),
            )
            return command_contract_only(args)
        if args.required_gate:
            require_arguments(args, ("required_manifest", "out"))
            return command_required_gate(args)
        require_arguments(args, ("attempt_root",))
        return command_require_implementation(args)
    except rtc.CompatibilityError as exc:
        failure = {
            "schema_version": "rtc-validator-failure-v1",
            "round_id": ROUND_ID,
            "status": "BLOCKED",
            "failure_code": exc.code,
            "message": str(exc),
        }
        if args.out:
            rtc.write_json(Path(args.out).resolve(), failure)
        print(json.dumps(failure, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
