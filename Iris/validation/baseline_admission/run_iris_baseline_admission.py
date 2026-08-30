"""Collect bounded baseline-admission evidence in caller-supplied external roots."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import stat
import time
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from Iris.validation.baseline_admission.iris_baseline_admission_common import (
    AdmissionError, S_BASE_COMMIT, S_BASE_TREE, clean_worktree, path_preflight,
    read_json, require_external, repo_identity, sha256_file, validate_registry,
    write_json,
)


HISTORICAL_RESEAL_GROUPS = (
    (
        "Iris/build/description/v2/tests/test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py",
        "Iris.build.description.v2.tests.test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.DvfCurrentRouteRequiredValidationEvidenceFreshnessResealTest",
        (
            "test_current_source_identity_redrive_and_drift_field_check_pass",
            "test_live_manifest_update_is_additive_and_governance_only",
            "test_external_bundle_and_final_report_are_fresh_when_not_in_inner_runner",
            "test_negative_fixtures_remain_fail_closed_without_live_mutation",
            "test_final_state_keeps_machine_pass_separate_from_canonical_complete",
        ),
        "root-reseal-a-class-setup",
    ),
    (
        "Iris/build/description/v2/tests/test_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py",
        "Iris.build.description.v2.tests.test_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.DvfCurrentSourceAuthorityDriftVerificationAdoptionResealTest",
        (
            "test_branch_selection_contract_and_rederivation_pass",
            "test_live_manifest_adoption_is_additive_and_governance_only",
            "test_negative_fixture_matrix_passes_without_live_mutation",
            "test_final_report_preserves_scope_ceiling_and_guard_checklist",
        ),
        "root-reseal-b-class-setup",
    ),
)

HISTORICAL_RTC_NODES = (
    (
        "test_required_gate_runs_standalone_subprocess",
        "root-rtc-durable-materialization",
        "rtc_bundle_materialization_defect",
    ),
    (
        "test_explicit_canonical_surface_validation_fails_closed_on_missing_input",
        "root-rtc-gate-reason-classification",
        "gate_reason_classification_defect",
    ),
)


def _plan_historical_node_ids() -> list[str]:
    """Return plan-declared identities only; these are not raw failure evidence."""
    nodes: list[str] = []
    for relative, classname, methods, root_id in HISTORICAL_RESEAL_GROUPS:
        del relative, root_id
        for method in methods:
            nodes.append(f"{classname}::{method}")
    rtc_class = (
        "Iris.build.description.v2.tests.test_dvf_3_3_registry_runtime_compatibility_current."
        "RegistryRuntimeCompatibilityCurrentRouteTest"
    )
    nodes.extend(f"{rtc_class}::{method}" for method, _root_id, _subtype in HISTORICAL_RTC_NODES)
    return nodes


def _classify_observed_failure(evidence: str) -> dict[str, str] | None:
    """Classify only signatures proven by the captured assertion/trace."""
    folded = evidence.casefold()
    if "get-filehash" in folded and "not recognized" in folded:
        return {
            "root_cause_id": "root-powershell-hash-autoload",
            "category": "orchestration_failure",
            "cause_subtype": "validation_tooling_defect",
            "evidence_rule": "powershell_get_file_hash_command_not_found",
        }
    if "registry-authority-projection" in folded and (
        "winerror 145" in folded or "no such file or directory" in folded
    ):
        return {
            "root_cause_id": "root-registry-projection-cleanup",
            "category": "orchestration_failure",
            "cause_subtype": "windows_path_contract_defect",
            "evidence_rule": "registry_projection_cleanup_or_concurrent_path_loss",
        }
    if "test_historical_reproduction_corpus_is_exact_and_fail_closed" in folded and "no such file or directory" in folded:
        return {
            "root_cause_id": "root-historical-overlay-path-materialization",
            "category": "orchestration_failure",
            "cause_subtype": "windows_path_contract_defect",
            "evidence_rule": "historical_overlay_materialization_path_failure",
        }
    if "missing fixture output" in folded and "legacy-output" in folded:
        return {
            "root_cause_id": "root-legacy-output-materialization",
            "category": "orchestration_failure",
            "cause_subtype": "evidence_materialization_defect",
            "evidence_rule": "configured_current_legacy_output_missing",
        }
    return None


def _environment_identity() -> dict[str, object]:
    import pytest

    uv_path = shutil.which("uv")
    uv_version = None
    if uv_path:
        completed = subprocess.run([uv_path, "--version"], text=True, capture_output=True, check=False)
        if completed.returncode == 0:
            uv_version = completed.stdout.strip()
    executable = Path(sys.executable).resolve()
    return {
        "python_executable": str(executable),
        "python_executable_sha256": sha256_file(executable),
        "python_version": sys.version,
        "pytest_version": pytest.__version__,
        "platform": platform.platform(),
        "uv_executable": str(Path(uv_path).resolve()) if uv_path else None,
        "uv_executable_sha256": sha256_file(Path(uv_path)) if uv_path else None,
        "uv_version": uv_version,
    }


def _git_path_state(repo: Path, path: Path) -> tuple[bool, bool]:
    relative = path.relative_to(repo).as_posix()
    tracked = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--error-unmatch", relative],
        text=True,
        capture_output=True,
        check=False,
    ).returncode == 0
    ignored = subprocess.run(
        ["git", "-C", str(repo), "check-ignore", "-q", relative],
        text=True,
        capture_output=True,
        check=False,
    ).returncode == 0
    return tracked, ignored


def _build_rtc_forensic_observation(
    repo: Path,
    result_root: Path,
    attempt: dict[str, object],
) -> dict[str, object]:
    """Bind the S_base standalone required-gate result to its exact inputs."""
    required_manifest_path = repo / "Iris/validation/current_route/required_validations.json"
    raw_receipt_path = result_root / "rtc-required-gate.json"
    required = read_json(required_manifest_path, code="forensic_rtc_required_manifest_invalid")
    raw = read_json(raw_receipt_path, code="forensic_rtc_required_gate_receipt_invalid")
    selection = required.get("registry_runtime_compatibility")
    if not isinstance(selection, dict):
        raise AdmissionError("forensic_rtc_selection_invalid", "required manifest has no RTC selection")
    bundle_id = selection.get("bundle_id")
    bundle_relative = selection.get("bundle_root")
    if not isinstance(bundle_id, str) or not isinstance(bundle_relative, str):
        raise AdmissionError("forensic_rtc_selection_invalid", "RTC bundle identity is incomplete")
    bundle_root = (repo / bundle_relative).resolve()
    try:
        bundle_root.relative_to(repo)
    except ValueError as exc:
        raise AdmissionError("forensic_rtc_bundle_path_escape", bundle_relative) from exc
    bundle_manifest_path = bundle_root / "durable_bundle_manifest.json"
    bundle_manifest = read_json(bundle_manifest_path, code="forensic_rtc_bundle_manifest_invalid")
    rows = bundle_manifest.get("rows")
    if not isinstance(rows, list):
        raise AdmissionError("forensic_rtc_bundle_manifest_invalid", "RTC member rows are missing")
    members: list[dict[str, object]] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("destination_path"), str):
            raise AdmissionError("forensic_rtc_bundle_manifest_invalid", "RTC member row is incomplete")
        destination = (bundle_root / row["destination_path"]).resolve()
        try:
            destination.relative_to(bundle_root)
        except ValueError as exc:
            raise AdmissionError("forensic_rtc_bundle_path_escape", row["destination_path"]) from exc
        exists = destination.is_file()
        actual_size = destination.stat().st_size if exists else None
        actual_hash = sha256_file(destination) if exists else None
        tracked, ignored = _git_path_state(repo, destination) if exists else (False, False)
        members.append(
            {
                "role": row.get("role"),
                "destination_path": row["destination_path"],
                "resolved_destination": str(destination),
                "resolved_destination_path_length": len(str(destination)),
                "expected_byte_count": row.get("byte_count"),
                "actual_byte_count": actual_size,
                "expected_sha256": row.get("sha256"),
                "actual_sha256": actual_hash,
                "exists": exists,
                "byte_count_match": actual_size == row.get("byte_count"),
                "sha256_match": actual_hash == row.get("sha256") == row.get("destination_sha256"),
                "tracked": tracked,
                "ignored": ignored,
            }
        )
    expected_roles = {
        "policy", "exclusion", "disposition", "plan_contract_approval",
        "collision_owner_disposition", "phase0_contract_review", "candidate_binding",
        "package_guard_contract", "implementation_toolchain",
        "pre_promotion_toolchain_freshness", "pre_adoption_machine_result",
    }
    bundle_integrity = (
        bundle_manifest.get("bundle_id") == bundle_id
        and bundle_root.name == bundle_id
        and sha256_file(bundle_manifest_path) == selection.get("bundle_manifest_sha256")
        and selection.get("policy_lifecycle_state") == "live_required_gate_adopted"
        and bundle_manifest.get("promotion_role_count") == 11
        and bundle_manifest.get("all_source_destination_bytes_equal") is True
        and len(rows) == 11
        and {row.get("role") for row in rows} == expected_roles
        and len({row.get("destination_path") for row in rows}) == 11
        and all(row.get("byte_parity") is True for row in rows)
        and all(
            row["exists"]
            and row["byte_count_match"]
            and row["sha256_match"]
            and row["tracked"]
            and not row["ignored"]
            for row in members
        )
    )

    alignment = selection.get("current_source_alignment")
    if not isinstance(alignment, dict):
        raise AdmissionError("forensic_rtc_alignment_invalid", "current-source alignment is missing")
    facts_relative = alignment.get("applies_when_current_facts_path")
    facts_expected_hash = alignment.get("applies_when_current_facts_sha256")
    facts_path = (repo / str(facts_relative)).resolve()
    facts_actual_hash = sha256_file(facts_path)
    facts_match_stale_marker = facts_actual_hash == facts_expected_hash

    toolchain_path = bundle_root / "implementation_toolchain_manifest.json"
    toolchain = read_json(toolchain_path, code="forensic_rtc_toolchain_manifest_invalid")
    toolchain_rows = toolchain.get("rows")
    if not isinstance(toolchain_rows, list):
        raise AdmissionError("forensic_rtc_toolchain_manifest_invalid", "toolchain rows are missing")
    toolchain_manifest_integrity = (
        toolchain.get("schema_version") == "rtc-implementation-toolchain-manifest-v1"
        and toolchain.get("row_count") == len(toolchain_rows)
        and toolchain.get("unclassified_tool_dependency_count") == 0
    )
    drift: list[str] = []
    missing: list[str] = []
    untracked: list[str] = []
    ignored: list[str] = []
    toolchain_members: list[dict[str, object]] = []
    for index, row in enumerate(toolchain_rows):
        relative = str(row.get("path", ""))
        current = (repo / relative).resolve()
        if not current.is_file():
            missing.append(relative)
            toolchain_members.append(
                {
                    "artifact_name": f"rtc_toolchain_input_{index:03d}",
                    "path": relative,
                    "resolved_path": str(current),
                    "resolved_path_length": len(str(current)),
                    "exists": False,
                    "expected_byte_count": row.get("byte_count"),
                    "actual_byte_count": None,
                    "expected_sha256": row.get("sha256"),
                    "actual_sha256": None,
                    "tracked": False,
                    "ignored": False,
                }
            )
            continue
        actual_size = current.stat().st_size
        actual_hash = sha256_file(current)
        if actual_size != row.get("byte_count") or actual_hash != row.get("sha256"):
            drift.append(relative)
        tracked, is_ignored = _git_path_state(repo, current)
        if row.get("tracked") is not True or not tracked:
            untracked.append(relative)
        if row.get("not_ignored") is not True or is_ignored:
            ignored.append(relative)
        toolchain_members.append(
            {
                "artifact_name": f"rtc_toolchain_input_{index:03d}",
                "path": relative,
                "resolved_path": str(current),
                "resolved_path_length": len(str(current)),
                "exists": True,
                "expected_byte_count": row.get("byte_count"),
                "actual_byte_count": actual_size,
                "expected_sha256": row.get("sha256"),
                "actual_sha256": actual_hash,
                "tracked": tracked,
                "ignored": is_ignored,
            }
        )
    if facts_match_stale_marker:
        expected_failure_code = "registry_runtime_compatibility_current_source_stale"
        expected_failure_basis = "current_facts_exactly_match_stale_alignment_marker"
    elif bundle_integrity and toolchain_manifest_integrity and (drift or missing or untracked or ignored):
        expected_failure_code = "implementation_toolchain_freshness_failed"
        expected_failure_basis = "selected_bundle_valid_and_toolchain_inventory_drift_observed"
    else:
        expected_failure_code = None
        expected_failure_basis = "no_authorized_expected_blocker_rule_matched"
    observed_failure_code = raw.get("failure_code")
    expected_observed_match = expected_failure_code is not None and observed_failure_code == expected_failure_code
    message = str(raw.get("message", ""))
    path_signature = any(
        token in message.casefold()
        for token in ("winerror", "path too long", "filename too long", "no such file or directory")
    )
    hypotheses = {
        "H1_gate_reason_classification": {
            "finding": "supported" if expected_observed_match else "contradicted",
            "evidence_rule": expected_failure_basis,
            "expected_failure_code": expected_failure_code,
            "observed_failure_code": observed_failure_code,
        },
        "H2_stale_expected_governance_state": {
            "finding": "supported" if facts_match_stale_marker else "not_supported",
            "facts_path": str(facts_path),
            "expected_sha256": facts_expected_hash,
            "actual_sha256": facts_actual_hash,
        },
        "H3_durable_materialization_defect": {
            "finding": "not_supported" if bundle_integrity else "supported",
            "bundle_integrity_verified": bundle_integrity,
            "member_count": len(members),
        },
        "H4_windows_path_observation_defect": {
            "finding": "supported" if path_signature else "not_supported",
            "failure_message_path_signature": path_signature,
            "checkout_root_length": len(str(repo)),
            "max_resolved_destination_path_length": max(
                (int(row["resolved_destination_path_length"]) for row in members),
                default=0,
            ),
        },
    }
    return {
        "schema_version": "iris-baseline-admission-rtc-forensic-observation-v1",
        "status": "PASS" if (
            attempt.get("native_exit_code") == 2
            and raw.get("status") == "BLOCKED"
            and raw.get("schema_version") == "rtc-validator-failure-v1"
            and expected_observed_match
            and bundle_integrity
            and toolchain_manifest_integrity
        ) else "FAIL",
        "subject": {"commit": S_BASE_COMMIT, "tree": S_BASE_TREE},
        "command": attempt.get("command"),
        "native_exit_code": attempt.get("native_exit_code"),
        "raw_required_gate_receipt": str(raw_receipt_path),
        "raw_required_gate_receipt_sha256": sha256_file(raw_receipt_path),
        "raw_required_gate_status": raw.get("status"),
        "expected_failure_code": expected_failure_code,
        "expected_failure_code_basis": expected_failure_basis,
        "observed_failure_code": observed_failure_code,
        "expected_observed_failure_code_match": expected_observed_match,
        "required_manifest_path": str(required_manifest_path),
        "required_manifest_sha256": sha256_file(required_manifest_path),
        "selected_bundle_id": bundle_id,
        "selected_bundle_root": str(bundle_root),
        "selected_bundle_root_path_length": len(str(bundle_root)),
        "selected_bundle_manifest_path": str(bundle_manifest_path),
        "selected_bundle_manifest_sha256": sha256_file(bundle_manifest_path),
        "selected_bundle_member_count": len(members),
        "selected_bundle_integrity_verified": bundle_integrity,
        "selected_bundle_members": members,
        "toolchain_manifest_path": str(toolchain_path),
        "toolchain_manifest_sha256": sha256_file(toolchain_path),
        "toolchain_manifest_integrity_verified": toolchain_manifest_integrity,
        "toolchain_members": toolchain_members,
        "toolchain_drift_paths": sorted(drift),
        "toolchain_missing_paths": sorted(missing),
        "toolchain_untracked_paths": sorted(untracked),
        "toolchain_ignored_paths": sorted(ignored),
        "hypotheses": hypotheses,
        "all_hypotheses_evidence_derived": True,
        "waiver_applied": False,
    }


def forensic(repo: Path, result_root: Path) -> dict:
    repo = repo.resolve()
    require_external(repo, result_root, "result root")
    if not clean_worktree(repo):
        raise AdmissionError("forensic_subject_not_clean", "forensic source checkout must be clean")
    identity = repo_identity(repo)
    if identity != {"commit": S_BASE_COMMIT, "tree": S_BASE_TREE}:
        raise AdmissionError("forensic_subject_not_s_base", "forensic mode requires exact frozen S_base")
    result_root.mkdir(parents=True, exist_ok=False)
    status_before = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain=v1", "--untracked-files=all"],
        text=True,
        capture_output=True,
        check=False,
    ).stdout
    ignored_before = subprocess.run(
        ["git", "-C", str(repo), "status", "--ignored", "--porcelain=v1", "--untracked-files=all"],
        text=True,
        capture_output=True,
        check=False,
    ).stdout
    base_env = os.environ.copy()
    for name in ("PYTHONHOME", "PYTHONPATH", "PYTEST_ADDOPTS"):
        base_env.pop(name, None)
    base_env["UV_CACHE_DIR"] = str(result_root / "uv-cache")
    base_env["PYTHONDONTWRITEBYTECODE"] = "1"
    commands = {
        "collection": [
            sys.executable, "-B", "-m", "pytest", "-s", "--collect-only", "-q", "-p", "no:cacheprovider",
            "--round3-contract=current", "--round3-enforce-denominator",
            "--round3-denominator-receipt", str(result_root / "configured-current-collection.json"),
        ],
        "exact_current": [
            sys.executable, "-B", "Iris/validation/current_route/run_contract_tests.py",
            "--class", "current", "--enforce-current-build-closure", "--out", str(result_root / "exact-current.json"),
        ],
        "configured_current": [
            sys.executable, "-B", "-m", "pytest", "-s", "-q", "-p", "no:cacheprovider",
            "--round3-contract=current", "--round3-enforce-denominator",
            "--round3-denominator-receipt", str(result_root / "configured-current.json"),
            "--junitxml", str(result_root / "configured-current.junit.xml"),
        ],
        "rtc_required_gate": [
            sys.executable, "-B",
            "Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_runtime_compatibility.py",
            "--required-gate",
            "--required-manifest", "Iris/validation/current_route/required_validations.json",
            "--out", str(result_root / "rtc-required-gate.json"),
        ],
    }
    attempts: dict[str, dict[str, object]] = {}
    for name, command in commands.items():
        env = base_env.copy()
        test_output_root = result_root / f"{name}-test-output"
        legacy_output_root = result_root / f"{name}-legacy-output"
        env["IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT"] = str(test_output_root)
        env["IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT"] = str(legacy_output_root)
        # The configured-current fixture requires an absent destination and
        # copies the predecessor output only after validating the destination.
        completed = subprocess.run(command, cwd=repo, env=env, text=True, capture_output=True, check=False)
        stdout_path = result_root / f"{name}.stdout.log"
        stderr_path = result_root / f"{name}.stderr.log"
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        attempts[name] = {
            "command": command,
            "native_exit_code": completed.returncode,
            "stdout": stdout_path.name,
            "stdout_sha256": sha256_file(stdout_path),
            "stderr": stderr_path.name,
            "stderr_sha256": sha256_file(stderr_path),
            "test_output_root": str(test_output_root),
            "legacy_output_root": str(legacy_output_root),
            "output_roots_reused_by_other_commands": False,
        }

    rtc_observation = _build_rtc_forensic_observation(
        repo,
        result_root,
        attempts["rtc_required_gate"],
    )
    rtc_observation_path = result_root / "rtc-required-gate-observation.json"
    write_json(rtc_observation_path, rtc_observation)

    junit_path = result_root / "configured-current.junit.xml"
    observed_nodes: list[dict[str, object]] = []
    observed_root_causes: dict[str, dict[str, object]] = {}
    observed_edges: list[dict[str, str]] = []
    junit_outcomes: dict[str, str] = {}
    if junit_path.is_file():
        try:
            junit_root = ET.parse(junit_path).getroot()
        except ET.ParseError as exc:
            raise AdmissionError("forensic_junit_invalid", str(junit_path)) from exc
        for case in junit_root.iter("testcase"):
            node_id = f"{case.get('classname', '')}::{case.get('name', '')}"
            finding = case.find("failure")
            outcome = "failure"
            if finding is None:
                finding = case.find("error")
                outcome = "error"
            if finding is None:
                junit_outcomes[node_id] = "skipped" if case.find("skipped") is not None else "pass"
                continue
            junit_outcomes[node_id] = outcome
            evidence = (finding.text or "") + "\n" + finding.get("message", "")
            signature = hashlib.sha256(evidence.encode("utf-8", errors="replace")).hexdigest()
            classification = _classify_observed_failure(evidence)
            if classification is None:
                root_id = f"root-unclassified-{signature[:12]}"
                category = "evidence_absent_unclassifiable"
                subtype = "unclassified"
                evidence_rule = "no_authorized_trace_rule_matched"
                disposition = "blocks_admission"
            else:
                root_id = classification["root_cause_id"]
                category = classification["category"]
                subtype = classification["cause_subtype"]
                evidence_rule = classification["evidence_rule"]
                disposition = "candidate_counterfactual_required"
            observed_nodes.append(
                {
                    "node_id": node_id,
                    "outcome": outcome,
                    "category": category,
                    "cause_subtype": subtype,
                    "primary_or_propagated": "propagated" if classification is not None else "primary",
                    "upstream_failure_identity": root_id if classification is not None else None,
                    "root_cause_id": root_id,
                    "raw_evidence_sha256": signature,
                    "raw_evidence_artifact": "configured-current.junit.xml",
                    "raw_evidence_locator": {
                        "classname": case.get("classname", ""),
                        "name": case.get("name", ""),
                        "outcome": outcome,
                    },
                    "evidence_rule": evidence_rule,
                    "disposition": disposition,
                }
            )
            root = observed_root_causes.setdefault(
                root_id,
                {
                    "root_cause_id": root_id,
                    "category": category,
                    "cause_subtype": subtype,
                    "evidence_rule": evidence_rule,
                    "child_raw_evidence_sha256s": [],
                },
            )
            root["child_raw_evidence_sha256s"].append(signature)
            observed_edges.append({"from": root_id, "to": node_id, "relation": "trace_rule_attribution"})
    for root in observed_root_causes.values():
        root["raw_evidence_sha256"] = hashlib.sha256(
            "\n".join(sorted(root["child_raw_evidence_sha256s"])).encode("ascii")
        ).hexdigest()
    historical_expected = _plan_historical_node_ids()
    historical_fresh_outcomes = [
        {
            "node_id": node_id,
            "fresh_outcome": junit_outcomes.get(node_id, "absent"),
            "evidence_artifact": "configured-current.junit.xml",
            "evidence_locator": {"node_id": node_id},
        }
        for node_id in historical_expected
    ]
    unknown_count = sum(row["category"] == "evidence_absent_unclassifiable" for row in observed_nodes)
    subject_finding_count = sum(row["category"] == "subject_finding" for row in observed_nodes)
    ledger = {
        "schema_version": "iris-baseline-admission-failure-ledger-v1",
        "subject": identity,
        "nodes": observed_nodes,
        "root_causes": list(observed_root_causes.values()),
        "historical_plan_declared_node_ids": historical_expected,
        "historical_plan_declared_raw_evidence_claimed": False,
        "historical_plan_declared_fresh_outcomes": historical_fresh_outcomes,
        "historical_nonpassing_node_count": len(historical_expected),
        "observed_nonpassing_node_count": len(observed_nodes),
        "propagated_node_count": sum(row["primary_or_propagated"] == "propagated" for row in observed_nodes),
        "primary_root_cause_count": len(observed_root_causes),
        "remaining_failure_node_count": unknown_count + subject_finding_count,
        "subject_finding_count": subject_finding_count,
        "unknown_failure_count": unknown_count,
        "evidence_absent_unclassifiable_count": unknown_count,
        "all_existing_nodes_have_evidence_bound_disposition": all(
            row.get("raw_evidence_sha256")
            and row.get("raw_evidence_artifact")
            and row.get("raw_evidence_locator")
            and row.get("disposition") != "blocks_admission"
            for row in observed_nodes
        ),
        "primary_and_propagated_relation_complete": all(
            row["primary_or_propagated"] == "primary" or row.get("upstream_failure_identity")
            for row in observed_nodes
        ),
        "reproduction_drift": set(row["node_id"] for row in observed_nodes) != set(historical_expected),
        "reproduction_drift_attribution": "fresh_evidence_bound_successor_observation",
    }
    ledger_path = result_root / "node-ledger.json"
    graph_path = result_root / "root-cause-graph.json"
    rtc_path = result_root / "rtc-hypothesis-report.json"
    write_json(ledger_path, ledger)
    write_json(
        graph_path,
        {"subject": identity, "root_causes": list(observed_root_causes.values()), "edges": observed_edges},
    )
    historical_rtc_ids = set(historical_expected[-2:])
    write_json(
        rtc_path,
        {
            "subject": identity,
            "historical_rtc_node_fresh_outcomes": [
                row for row in historical_fresh_outcomes if row["node_id"] in historical_rtc_ids
            ],
            "standalone_required_gate": {
                "native_exit_code": rtc_observation["native_exit_code"],
                "raw_receipt_sha256": rtc_observation["raw_required_gate_receipt_sha256"],
                "observation_sha256": sha256_file(rtc_observation_path),
                "expected_failure_code": rtc_observation["expected_failure_code"],
                "observed_failure_code": rtc_observation["observed_failure_code"],
                "expected_observed_failure_code_match": rtc_observation[
                    "expected_observed_failure_code_match"
                ],
                "selected_bundle_id": rtc_observation["selected_bundle_id"],
                "selected_bundle_member_count": rtc_observation["selected_bundle_member_count"],
            },
            "hypotheses": rtc_observation["hypotheses"],
            "all_hypotheses_evidence_derived": rtc_observation[
                "all_hypotheses_evidence_derived"
            ],
            "waiver_applied": False,
            "historical_failure_claim_used_for_admission": False,
        },
    )
    status_after = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain=v1", "--untracked-files=all"],
        text=True,
        capture_output=True,
        check=False,
    ).stdout
    ignored_after = subprocess.run(
        ["git", "-C", str(repo), "status", "--ignored", "--porcelain=v1", "--untracked-files=all"],
        text=True,
        capture_output=True,
        check=False,
    ).stdout
    required_capture_paths = (
        result_root / "configured-current-collection.json",
        result_root / "exact-current.json",
        result_root / "configured-current.json",
        junit_path,
        ledger_path,
        graph_path,
        rtc_path,
        result_root / "rtc-required-gate.json",
        rtc_observation_path,
    )
    evidence_capture_pass = forensic_evidence_capture_pass(
        result_root=result_root,
        attempts=attempts,
        required_paths=required_capture_paths,
        ledger=ledger,
        status_before=status_before,
        status_after=status_after,
        ignored_before=ignored_before,
        ignored_after=ignored_after,
    )
    artifact_paths = {
        "configured_current_collection_receipt": result_root / "configured-current-collection.json",
        "exact_current_receipt": result_root / "exact-current.json",
        "configured_current_receipt": result_root / "configured-current.json",
        "configured_current_junit": junit_path,
        "failure_ledger": ledger_path,
        "root_cause_graph": graph_path,
        "rtc_hypothesis_report": rtc_path,
        "rtc_required_gate_receipt": result_root / "rtc-required-gate.json",
        "rtc_required_gate_observation": rtc_observation_path,
        "rtc_required_manifest": Path(str(rtc_observation["required_manifest_path"])),
        "rtc_bundle_manifest": Path(str(rtc_observation["selected_bundle_manifest_path"])),
        "rtc_toolchain_manifest": Path(str(rtc_observation["toolchain_manifest_path"])),
        "rtc_current_facts": Path(str(rtc_observation["hypotheses"]["H2_stale_expected_governance_state"]["facts_path"])),
    }
    for member in rtc_observation["selected_bundle_members"]:
        artifact_paths[f"rtc_bundle_member_{member['role']}"] = Path(
            str(member["resolved_destination"])
        )
    for member in rtc_observation["toolchain_members"]:
        if member["exists"]:
            artifact_paths[str(member["artifact_name"])] = Path(str(member["resolved_path"]))
    for attempt_name, attempt in attempts.items():
        artifact_paths[f"{attempt_name}_stdout"] = result_root / str(attempt["stdout"])
        artifact_paths[f"{attempt_name}_stderr"] = result_root / str(attempt["stderr"])
    return {
        "schema_version": "iris-baseline-forensic-attempt-v1",
        "status": "PASS" if evidence_capture_pass else "FAIL",
        "native_exit_code": 0 if evidence_capture_pass else 1,
        "subject": identity,
        "route": "configured_current_plus_exact_current",
        "environment": _environment_identity(),
        "attempts": attempts,
        "artifacts": {
            name: {"path": str(path.resolve()), "sha256": sha256_file(path)}
            for name, path in artifact_paths.items()
            if path.is_file()
        },
        "junit_state": "produced" if junit_path.is_file() else "not_produced",
        "junit_sha256": sha256_file(junit_path) if junit_path.is_file() else None,
        "failure_ledger": {"path": str(ledger_path), "sha256": sha256_file(ledger_path)},
        "root_cause_graph": {"path": str(graph_path), "sha256": sha256_file(graph_path)},
        "rtc_hypothesis_report": {"path": str(rtc_path), "sha256": sha256_file(rtc_path)},
        "raw_evidence_complete": all(path.is_file() for path in required_capture_paths),
        "historical_failure_census": {
            "plan_declared_nonpassing_node_count": len(historical_expected),
            "plan_declared_raw_evidence_claimed": False,
            "fresh_outcomes": historical_fresh_outcomes,
        },
        "observed_failure_census": {
            "nonpassing_node_count": len(observed_nodes),
            "propagated_node_count": ledger["propagated_node_count"],
            "primary_root_cause_count": ledger["primary_root_cause_count"],
            "remaining_failure_node_count": ledger["remaining_failure_node_count"],
            "unknown_failure_count": ledger["unknown_failure_count"],
            "evidence_absent_unclassifiable_count": ledger["evidence_absent_unclassifiable_count"],
            "subject_finding_count": ledger["subject_finding_count"],
            "all_nodes_evidence_bound_and_dispositioned": ledger[
                "all_existing_nodes_have_evidence_bound_disposition"
            ],
        },
        "fresh_observation_nonpassing_node_count": len(observed_nodes),
        "reproduction_drift": ledger["reproduction_drift"],
        "source_status_before": status_before,
        "source_status_after": status_after,
        "source_checkout_mutation_count": 0 if status_before == status_after else 1,
        "ignored_status_before_sha256": hashlib.sha256(ignored_before.encode()).hexdigest(),
        "ignored_status_after_sha256": hashlib.sha256(ignored_after.encode()).hexdigest(),
        "ignored_state_unchanged": ignored_before == ignored_after,
        "result_root_external": True,
    }


def forensic_evidence_capture_pass(
    *,
    result_root: Path,
    attempts: dict,
    required_paths: tuple[Path, ...],
    ledger: dict,
    status_before: str,
    status_after: str,
    ignored_before: str,
    ignored_after: str,
) -> bool:
    """Validate captured bytes and schemas; non-green S_base exits are evidence, not failure here."""
    try:
        collection = read_json(result_root / "configured-current-collection.json")
        configured = read_json(result_root / "configured-current.json")
        exact = read_json(result_root / "exact-current.json")
        rtc_raw = read_json(result_root / "rtc-required-gate.json")
        rtc_observation = read_json(result_root / "rtc-required-gate-observation.json")
        junit_root = ET.parse(result_root / "configured-current.junit.xml").getroot()
    except (AdmissionError, OSError, ET.ParseError):
        return False
    junit_nodes = {
        f"{case.get('classname', '')}::{case.get('name', '')}"
        for case in junit_root.iter("testcase")
        if case.find("failure") is not None or case.find("error") is not None
    }
    ledger_nodes = {str(row.get("node_id")) for row in ledger.get("nodes", [])}
    log_hashes_valid = True
    for attempt in attempts.values():
        for stream in ("stdout", "stderr"):
            path = result_root / str(attempt.get(stream, ""))
            log_hashes_valid = log_hashes_valid and path.is_file() and sha256_file(path) == attempt.get(f"{stream}_sha256")
    exact_findings = list(exact.get("failures", [])) + list(exact.get("errors", []))
    exact_findings_valid = exact.get("success") is True or (
        bool(exact_findings)
        and all(isinstance(row.get("traceback"), str) and row["traceback"] for row in exact_findings)
    )
    rtc_hypotheses = (
        rtc_observation.get("hypotheses")
        if isinstance(rtc_observation.get("hypotheses"), dict)
        else {}
    )
    return (
        attempts["collection"]["native_exit_code"] == 0
        and attempts["rtc_required_gate"]["native_exit_code"] == 2
        and all(isinstance(row.get("native_exit_code"), int) for row in attempts.values())
        and all(path.is_file() for path in required_paths)
        and collection.get("schema_version") == "round3-denominator-execution-receipt-v1"
        and configured.get("schema_version") == "round3-denominator-execution-receipt-v1"
        and collection.get("status") == "PASS"
        and configured.get("status") == "PASS"
        and collection.get("ordered_node_ids_sha256") == configured.get("ordered_node_ids_sha256")
        and exact.get("schema_version") == "round3-contract-test-run-v1"
        and isinstance(exact.get("test_count"), int)
        and exact_findings_valid
        and rtc_raw.get("schema_version") == "rtc-validator-failure-v1"
        and rtc_raw.get("status") == "BLOCKED"
        and rtc_observation.get("schema_version")
        == "iris-baseline-admission-rtc-forensic-observation-v1"
        and rtc_observation.get("status") == "PASS"
        and rtc_observation.get("subject") == {"commit": S_BASE_COMMIT, "tree": S_BASE_TREE}
        and rtc_observation.get("raw_required_gate_receipt_sha256")
        == sha256_file(result_root / "rtc-required-gate.json")
        and rtc_observation.get("expected_failure_code") == rtc_raw.get("failure_code")
        and rtc_observation.get("observed_failure_code") == rtc_raw.get("failure_code")
        and rtc_observation.get("expected_observed_failure_code_match") is True
        and rtc_observation.get("selected_bundle_member_count") == 11
        and rtc_observation.get("selected_bundle_integrity_verified") is True
        and rtc_observation.get("toolchain_manifest_integrity_verified") is True
        and rtc_observation.get("all_hypotheses_evidence_derived") is True
        and set(rtc_hypotheses)
        == {
            "H1_gate_reason_classification",
            "H2_stale_expected_governance_state",
            "H3_durable_materialization_defect",
            "H4_windows_path_observation_defect",
        }
        and all(
            isinstance(row, dict)
            and row.get("finding") in {"supported", "not_supported", "contradicted"}
            for row in rtc_hypotheses.values()
        )
        and rtc_hypotheses.get("H1_gate_reason_classification", {}).get("finding")
        == "supported"
        and junit_nodes == ledger_nodes
        and log_hashes_valid
        and ledger["unknown_failure_count"] == 0
        and ledger["evidence_absent_unclassifiable_count"] == 0
        and ledger["subject_finding_count"] == 0
        and ledger["all_existing_nodes_have_evidence_bound_disposition"] is True
        and ledger["primary_and_propagated_relation_complete"] is True
        and status_before == status_after
        and ignored_before == ignored_after
    )


def _path_normalize(value: object) -> object:
    if isinstance(value, dict):
        return {key: _path_normalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_path_normalize(item) for item in value]
    if isinstance(value, str) and (Path(value).is_absolute() or (len(value) > 2 and value[1:3] == ":/")):
        return "<absolute-path>"
    return value


def _remove_checkout(path: Path) -> None:
    def clear_readonly(func: object, target: str, exc: object) -> None:
        del exc
        os.chmod(target, stat.S_IWRITE)
        func(target)

    removal_path = path
    if os.name == "nt":
        removal_path = Path("\\\\?\\" + str(path.resolve()))
    last_error: OSError | None = None
    for _attempt in range(10):
        if not path.exists():
            return
        try:
            shutil.rmtree(removal_path, onexc=clear_readonly)
            if not path.exists():
                return
        except OSError as exc:
            last_error = exc
            time.sleep(0.2)
    detail = "checkout still exists after cleanup retries"
    if last_error is not None:
        detail = f"{detail}: {last_error}"
    raise AdmissionError("qualification_checkout_cleanup_failed", detail)


def _canonical_result(orchestration_path: Path, subject: dict[str, str]) -> dict:
    try:
        orchestration = json.loads(orchestration_path.read_text(encoding="utf-8"))
        inner_path = Path(orchestration["result_receipt"]["path"])
        inner = json.loads(inner_path.read_text(encoding="utf-8"))
        canonical_path = Path(inner["canonical_result"]["path"])
        canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise AdmissionError("path_control_receipt_unreadable", str(orchestration_path)) from exc
    if orchestration.get("native_exit_code") != 0 or inner.get("status") != "PASS" or canonical.get("status") != "PASS":
        raise AdmissionError("path_control_receipt_not_pass", str(orchestration_path))
    if inner.get("subject") != subject or canonical.get("subject") != subject:
        raise AdmissionError("path_control_subject_mismatch", str(orchestration_path))
    if inner.get("execution_context") != "composite_baseline_admission_chain_stage_6":
        raise AdmissionError("path_control_execution_context_mismatch", str(orchestration_path))
    return canonical


def _compare_path_control(run_a: Path, path_control: Path, subject: dict[str, str], output: Path) -> dict:
    a = _canonical_result(run_a, subject)
    p = _canonical_result(path_control, subject)
    if a.get("test_inventory_sha256") != p.get("test_inventory_sha256"):
        raise AdmissionError("path_control_denominator_mismatch", "test inventory differs")
    if a.get("required_dependency_inventory", {}).get("sha256") != p.get("required_dependency_inventory", {}).get("sha256"):
        raise AdmissionError("path_control_dependency_inventory_mismatch", "dependency inventory differs")
    normalized_equal = _path_normalize(a) == _path_normalize(p)
    result = {
        "schema_version": "iris-baseline-admission-path-control-comparison-v1",
        "status": "PASS" if normalized_equal else "FAIL",
        "subject": subject,
        "run_a_test_inventory_sha256": a.get("test_inventory_sha256"),
        "path_control_test_inventory_sha256": p.get("test_inventory_sha256"),
        "run_a_required_dependency_inventory_sha256": a.get("required_dependency_inventory", {}).get("sha256"),
        "path_control_required_dependency_inventory_sha256": p.get("required_dependency_inventory", {}).get("sha256"),
        "path_normalized_semantic_identity_match": normalized_equal,
    }
    write_json(output, result)
    if not normalized_equal:
        raise AdmissionError("path_control_semantic_identity_mismatch", "Run A and Path Control P differ after path normalization")
    return result


def _copy_evidence(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise AdmissionError("qualification_evidence_missing", str(source))
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise AdmissionError("qualification_evidence_destination_exists", str(destination))
    shutil.copy2(source, destination)


def _stage_path(stage_set: dict[str, object], stage: str, field: str) -> Path:
    stages = stage_set.get("stages")
    if not isinstance(stages, dict):
        raise AdmissionError("qualification_stage_set_invalid", "stages object is missing")
    row = stages.get(stage)
    if not isinstance(row, dict) or row.get("status") != "PASS":
        raise AdmissionError("qualification_stage_not_pass", stage)
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise AdmissionError("qualification_stage_evidence_missing", f"{stage}.{field}")
    return Path(value).resolve()


def _validate_rtc_bundle(repo: Path, subject: dict[str, str]) -> dict[str, object]:
    required = read_json(repo / "Iris/validation/current_route/required_validations.json")
    selection = required.get("registry_runtime_compatibility")
    if not isinstance(selection, dict):
        raise AdmissionError("rtc_selection_invalid", "live RTC selection is missing")
    bundle_id = selection.get("bundle_id")
    bundle_relative = selection.get("bundle_root")
    if not isinstance(bundle_id, str) or not isinstance(bundle_relative, str):
        raise AdmissionError("rtc_selection_invalid", "bundle identity is incomplete")
    bundle_root = (repo / bundle_relative).resolve()
    try:
        bundle_root.relative_to(repo.resolve())
    except ValueError as exc:
        raise AdmissionError("rtc_bundle_path_escape", bundle_relative) from exc
    manifest_path = bundle_root / "durable_bundle_manifest.json"
    if sha256_file(manifest_path) != selection.get("bundle_manifest_sha256"):
        raise AdmissionError("rtc_bundle_manifest_hash_mismatch", str(manifest_path))
    manifest = read_json(manifest_path, code="rtc_bundle_manifest_invalid")
    rows = manifest.get("rows")
    if (
        manifest.get("bundle_id") != bundle_id
        or manifest.get("promotion_role_count") != 11
        or not isinstance(rows, list)
        or len(rows) != 11
    ):
        raise AdmissionError("rtc_bundle_inventory_mismatch", bundle_id)
    roles: set[str] = set()
    destinations: set[str] = set()
    verified: list[dict[str, object]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise AdmissionError("rtc_bundle_manifest_invalid", "row is not an object")
        role, destination = row.get("role"), row.get("destination_path")
        if not isinstance(role, str) or not isinstance(destination, str) or role in roles or destination in destinations:
            raise AdmissionError("rtc_bundle_inventory_mismatch", "roles and destinations must be unique")
        roles.add(role)
        destinations.add(destination)
        path = (bundle_root / destination).resolve()
        try:
            path.relative_to(bundle_root)
        except ValueError as exc:
            raise AdmissionError("rtc_bundle_path_escape", destination) from exc
        if not path.is_file():
            raise AdmissionError("rtc_bundle_member_missing", destination)
        actual_hash = sha256_file(path)
        if path.stat().st_size != row.get("byte_count"):
            raise AdmissionError("rtc_bundle_member_byte_count_mismatch", destination)
        if actual_hash != row.get("sha256") or actual_hash != row.get("destination_sha256"):
            raise AdmissionError("rtc_bundle_member_sha256_mismatch", destination)
        tracked = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "--error-unmatch", path.relative_to(repo).as_posix()],
            text=True,
            capture_output=True,
            check=False,
        )
        ignored = subprocess.run(
            ["git", "-C", str(repo), "check-ignore", "-q", path.relative_to(repo).as_posix()],
            text=True,
            capture_output=True,
            check=False,
        )
        if tracked.returncode != 0 or ignored.returncode == 0:
            raise AdmissionError("rtc_bundle_manifest_visibility_invalid", destination)
        verified.append({"role": role, "destination_path": destination, "byte_count": path.stat().st_size, "sha256": actual_hash})
    if manifest.get("all_source_destination_bytes_equal") is not True or any(row.get("byte_parity") is not True for row in rows):
        raise AdmissionError("rtc_bundle_byte_parity_mismatch", bundle_id)
    if selection.get("policy_lifecycle_state") != "live_required_gate_adopted" or selection.get("owner_explicitly_approved") is not True:
        raise AdmissionError("rtc_successor_bundle_adoption_pending", bundle_id)
    return {
        "schema_version": "iris-baseline-admission-rtc-qualification-v1",
        "status": "PASS",
        "subject": subject,
        "bundle_id": bundle_id,
        "bundle_root": bundle_relative,
        "bundle_manifest_sha256": sha256_file(manifest_path),
        "promotion_role_count": 11,
        "member_inventory_relation_verified": True,
        "hash_relation_verified": True,
        "byte_relation_verified": True,
        "tracking_visibility_verified": True,
        "consumer_resolution_verified": True,
        "policy_lifecycle_state": selection["policy_lifecycle_state"],
        "rtc_global_pass_claimed": False,
        "members": verified,
    }


def _focused_receipts(
    repo: Path,
    subject: dict[str, str],
    stage_set: dict[str, object],
    evidence_root: Path,
) -> dict[str, dict[str, object]]:
    junit = _stage_path(stage_set, "focused_rtc_reseal", "junit")
    output_root = _stage_path(stage_set, "focused_rtc_reseal", "output_root")
    require_external(repo, junit, "focused JUnit")
    require_external(repo, output_root, "focused output root")
    if not junit.is_file() or not output_root.is_dir():
        raise AdmissionError("focused_qualification_evidence_missing", "focused JUnit or output root is missing")
    try:
        xml_root = ET.parse(junit).getroot()
    except (OSError, ET.ParseError) as exc:
        raise AdmissionError("focused_junit_invalid", str(junit)) from exc
    cases = list(xml_root.iter("testcase"))
    if any(case.find("failure") is not None or case.find("error") is not None or case.find("skipped") is not None for case in cases):
        raise AdmissionError("focused_qualification_not_green", "focused JUnit has a non-passing case")
    groups = {
        "rtc": "test_dvf_3_3_registry_runtime_compatibility_current",
        "reseal_a": "test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal",
        "reseal_b": "test_dvf_3_3_current_source_authority_drift_verification_adoption_reseal",
    }
    expected_counts = {"rtc": 2, "reseal_a": 5, "reseal_b": 4}
    node_ids: dict[str, list[str]] = {}
    for name, marker in groups.items():
        selected = [
            f"{case.get('classname', '')}::{case.get('name', '')}"
            for case in cases
            if marker in case.get("classname", "")
        ]
        if len(selected) != expected_counts[name]:
            raise AdmissionError("focused_qualification_denominator_mismatch", f"{name}: {len(selected)}")
        node_ids[name] = selected
    _copy_evidence(junit, evidence_root / "focused" / "focused.junit.xml")
    junit_hash = sha256_file(junit)
    receipts: dict[str, dict[str, object]] = {"rtc": _validate_rtc_bundle(repo, subject)}
    reseal_specs = {
        "reseal_a": (
            output_root / "current-route-freshness-reseal-validation",
            "final_current_route_required_validation_evidence_freshness_reseal_report.json",
        ),
        "reseal_b": (
            output_root / "current-source-adoption-reseal-validation",
            "final_current_source_authority_drift_verification_adoption_reseal_report.json",
        ),
    }
    for name, (root, final_name) in reseal_specs.items():
        final_path = root / "phase6" / final_name
        validation_path = root / "phase6" / "validation_report.require_complete.json"
        final = read_json(final_path, code="reseal_qualification_receipt_invalid")
        validation = read_json(validation_path, code="reseal_qualification_receipt_invalid")
        if final.get("status") != "PASS" or final.get("machine_contract_status") != "PASS" or validation.get("status") != "PASS" or validation.get("error_count") != 0:
            raise AdmissionError("reseal_qualification_not_pass", name)
        _copy_evidence(final_path, evidence_root / "focused" / name / final_name)
        _copy_evidence(validation_path, evidence_root / "focused" / name / "validation_report.require_complete.json")
        receipts[name] = {
            "schema_version": "iris-baseline-admission-reseal-qualification-v1",
            "status": "PASS",
            "subject": subject,
            "route": name,
            "observed_node_count": expected_counts[name],
            "ordered_node_ids": node_ids[name],
            "junit_sha256": junit_hash,
            "final_report_sha256": sha256_file(final_path),
            "validation_report_sha256": sha256_file(validation_path),
            "repository_local_generated_write_count": 0,
        }
    receipts["rtc"]["observed_node_count"] = expected_counts["rtc"]
    receipts["rtc"]["ordered_node_ids"] = node_ids["rtc"]
    receipts["rtc"]["junit_sha256"] = junit_hash
    return receipts


def _forensic_stage_binding(
    repo: Path,
    candidate_subject: dict[str, str],
    stage_set: dict[str, object],
    candidate_junit_path: Path,
    environment_receipt_path: Path,
    evidence_root: Path,
) -> dict[str, object]:
    receipt_path = _stage_path(stage_set, "s_base_forensic", "receipt")
    require_external(repo, receipt_path, "S_base forensic receipt")
    forensic_receipt = read_json(receipt_path, code="forensic_receipt_invalid")
    s_base_subject = {"commit": S_BASE_COMMIT, "tree": S_BASE_TREE}
    if (
        forensic_receipt.get("status") != "PASS"
        or forensic_receipt.get("native_exit_code") != 0
        or forensic_receipt.get("subject") != s_base_subject
        or forensic_receipt.get("raw_evidence_complete") is not True
        or forensic_receipt.get("source_checkout_mutation_count") != 0
        or forensic_receipt.get("ignored_state_unchanged") is not True
    ):
        raise AdmissionError("forensic_receipt_invalid", "S_base forensic receipt is not exact, complete, and immutable")
    artifacts = forensic_receipt.get("artifacts")
    required_artifacts = {
        "configured_current_collection_receipt",
        "exact_current_receipt",
        "configured_current_receipt",
        "configured_current_junit",
        "failure_ledger",
        "root_cause_graph",
        "rtc_hypothesis_report",
        "collection_stdout", "collection_stderr",
        "exact_current_stdout", "exact_current_stderr",
        "configured_current_stdout", "configured_current_stderr",
        "rtc_required_gate_receipt", "rtc_required_gate_observation",
        "rtc_required_manifest", "rtc_bundle_manifest", "rtc_toolchain_manifest",
        "rtc_current_facts",
        "rtc_required_gate_stdout", "rtc_required_gate_stderr",
    }
    member_artifact_names = {
        name for name in artifacts if name.startswith("rtc_bundle_member_")
    } if isinstance(artifacts, dict) else set()
    toolchain_artifact_names = {
        name for name in artifacts if name.startswith("rtc_toolchain_input_")
    } if isinstance(artifacts, dict) else set()
    expected_artifact_names = (
        required_artifacts | member_artifact_names | toolchain_artifact_names
    )
    if (
        not isinstance(artifacts, dict)
        or set(artifacts) != expected_artifact_names
        or len(member_artifact_names) != 11
        or not toolchain_artifact_names
    ):
        raise AdmissionError("forensic_artifact_set_invalid", "forensic artifact set is incomplete or has undeclared members")
    artifact_paths: dict[str, Path] = {}
    for name in sorted(expected_artifact_names):
        row = artifacts.get(name)
        if not isinstance(row, dict) or not isinstance(row.get("path"), str) or not isinstance(row.get("sha256"), str):
            raise AdmissionError("forensic_artifact_identity_invalid", name)
        path = require_external(repo, Path(row["path"]), f"forensic artifact {name}")
        if not path.is_file() or sha256_file(path) != row["sha256"]:
            raise AdmissionError("forensic_artifact_hash_mismatch", name)
        artifact_paths[name] = path

    collection = read_json(artifact_paths["configured_current_collection_receipt"], code="forensic_collection_receipt_invalid")
    configured = read_json(artifact_paths["configured_current_receipt"], code="forensic_configured_receipt_invalid")
    exact = read_json(artifact_paths["exact_current_receipt"], code="forensic_exact_receipt_invalid")
    rtc_raw = read_json(
        artifact_paths["rtc_required_gate_receipt"],
        code="forensic_rtc_required_gate_receipt_invalid",
    )
    rtc_observation = read_json(
        artifact_paths["rtc_required_gate_observation"],
        code="forensic_rtc_observation_invalid",
    )
    if (
        collection.get("schema_version") != "round3-denominator-execution-receipt-v1"
        or configured.get("schema_version") != "round3-denominator-execution-receipt-v1"
        or collection.get("status") != "PASS"
        or configured.get("status") != "PASS"
        or collection.get("ordered_node_ids_sha256") != configured.get("ordered_node_ids_sha256")
        or exact.get("schema_version") != "round3-contract-test-run-v1"
        or not isinstance(exact.get("test_count"), int)
    ):
        raise AdmissionError("forensic_route_receipt_schema_invalid", "collection/configured/exact forensic receipts do not bind one route")
    exact_findings = list(exact.get("failures", [])) + list(exact.get("errors", []))
    if exact.get("success") is not True and (
        not exact_findings
        or any(not isinstance(row.get("traceback"), str) or not row["traceback"] for row in exact_findings)
    ):
        raise AdmissionError("forensic_exact_raw_trace_missing", "non-green exact-current result lacks assertion traces")
    rtc_members = rtc_observation.get("selected_bundle_members")
    rtc_toolchain_members = rtc_observation.get("toolchain_members")
    rtc_hypotheses = rtc_observation.get("hypotheses")
    expected_member_artifacts = {
        f"rtc_bundle_member_{row.get('role')}"
        for row in rtc_members
        if isinstance(row, dict)
    } if isinstance(rtc_members, list) else set()
    expected_toolchain_artifacts = {
        str(row.get("artifact_name"))
        for row in rtc_toolchain_members
        if isinstance(row, dict) and row.get("exists") is True
    } if isinstance(rtc_toolchain_members, list) else set()
    if (
        rtc_raw.get("schema_version") != "rtc-validator-failure-v1"
        or rtc_raw.get("status") != "BLOCKED"
        or rtc_observation.get("schema_version")
        != "iris-baseline-admission-rtc-forensic-observation-v1"
        or rtc_observation.get("status") != "PASS"
        or rtc_observation.get("subject") != s_base_subject
        or rtc_observation.get("native_exit_code") != 2
        or rtc_observation.get("raw_required_gate_receipt_sha256")
        != sha256_file(artifact_paths["rtc_required_gate_receipt"])
        or rtc_observation.get("expected_failure_code") != rtc_raw.get("failure_code")
        or rtc_observation.get("observed_failure_code") != rtc_raw.get("failure_code")
        or rtc_observation.get("expected_observed_failure_code_match") is not True
        or rtc_observation.get("selected_bundle_member_count") != 11
        or rtc_observation.get("selected_bundle_integrity_verified") is not True
        or rtc_observation.get("toolchain_manifest_integrity_verified") is not True
        or not isinstance(rtc_observation.get("selected_bundle_id"), str)
        or not rtc_observation.get("selected_bundle_id")
        or expected_member_artifacts != member_artifact_names
        or expected_toolchain_artifacts != toolchain_artifact_names
        or rtc_observation.get("required_manifest_sha256")
        != sha256_file(artifact_paths["rtc_required_manifest"])
        or rtc_observation.get("selected_bundle_manifest_sha256")
        != sha256_file(artifact_paths["rtc_bundle_manifest"])
        or rtc_observation.get("toolchain_manifest_sha256")
        != sha256_file(artifact_paths["rtc_toolchain_manifest"])
        or not isinstance(rtc_hypotheses, dict)
        or rtc_hypotheses.get("H2_stale_expected_governance_state", {}).get("actual_sha256")
        != sha256_file(artifact_paths["rtc_current_facts"])
        or set(rtc_hypotheses) != {
            "H1_gate_reason_classification",
            "H2_stale_expected_governance_state",
            "H3_durable_materialization_defect",
            "H4_windows_path_observation_defect",
        }
        or any(
            not isinstance(row, dict)
            or row.get("finding") not in {"supported", "not_supported", "contradicted"}
            for row in rtc_hypotheses.values()
        )
        or rtc_hypotheses.get("H1_gate_reason_classification", {}).get("finding")
        != "supported"
        or rtc_observation.get("all_hypotheses_evidence_derived") is not True
        or rtc_observation.get("waiver_applied") is not False
    ):
        raise AdmissionError(
            "forensic_rtc_required_gate_evidence_invalid",
            "standalone RTC required-gate evidence is incomplete or mismatched",
        )
    s_base_repo = artifact_paths["rtc_required_manifest"].parents[3]
    recomputed_rtc_observation = _build_rtc_forensic_observation(
        s_base_repo,
        artifact_paths["rtc_required_gate_receipt"].parent,
        {
            "command": rtc_observation.get("command"),
            "native_exit_code": rtc_observation.get("native_exit_code"),
        },
    )
    if recomputed_rtc_observation != rtc_observation:
        raise AdmissionError(
            "forensic_rtc_observation_recomputation_mismatch",
            "standalone RTC observation is not derivable from captured inputs",
        )
    for member in rtc_members:
        name = f"rtc_bundle_member_{member['role']}"
        path = artifact_paths[name]
        if (
            member.get("resolved_destination") != str(path)
            or member.get("resolved_destination_path_length") != len(str(path))
            or member.get("actual_byte_count") != path.stat().st_size
            or member.get("actual_sha256") != sha256_file(path)
            or member.get("byte_count_match") is not True
            or member.get("sha256_match") is not True
            or member.get("tracked") is not True
            or member.get("ignored") is not False
        ):
            raise AdmissionError("forensic_rtc_bundle_member_invalid", name)
    for member in rtc_toolchain_members:
        if member.get("exists") is not True:
            continue
        name = str(member.get("artifact_name"))
        path = artifact_paths[name]
        if (
            member.get("resolved_path") != str(path)
            or member.get("resolved_path_length") != len(str(path))
            or member.get("actual_byte_count") != path.stat().st_size
            or member.get("actual_sha256") != sha256_file(path)
        ):
            raise AdmissionError("forensic_rtc_toolchain_input_invalid", name)

    ledger = read_json(artifact_paths["failure_ledger"], code="forensic_failure_ledger_invalid")
    graph = read_json(artifact_paths["root_cause_graph"], code="forensic_root_cause_graph_invalid")
    rtc = read_json(artifact_paths["rtc_hypothesis_report"], code="forensic_rtc_hypothesis_invalid")
    nodes = ledger.get("nodes")
    if (
        ledger.get("subject") != s_base_subject
        or not isinstance(nodes, list)
        or not nodes
        or ledger.get("unknown_failure_count") != 0
        or ledger.get("evidence_absent_unclassifiable_count") != 0
        or ledger.get("subject_finding_count") != 0
        or ledger.get("all_existing_nodes_have_evidence_bound_disposition") is not True
        or ledger.get("primary_and_propagated_relation_complete") is not True
        or ledger.get("historical_plan_declared_raw_evidence_claimed") is not False
        or ledger.get("reproduction_drift_attribution") != "fresh_evidence_bound_successor_observation"
    ):
        raise AdmissionError("forensic_failure_ledger_invalid", "failure ledger has unresolved or synthetic evidence")
    try:
        s_base_junit = ET.parse(artifact_paths["configured_current_junit"]).getroot()
        candidate_junit = ET.parse(candidate_junit_path).getroot()
    except (OSError, ET.ParseError) as exc:
        raise AdmissionError("forensic_junit_invalid", str(exc)) from exc
    s_base_evidence: dict[str, tuple[str, str]] = {}
    for case in s_base_junit.iter("testcase"):
        finding = case.find("failure")
        if finding is None:
            finding = case.find("error")
        if finding is None:
            continue
        node_id = f"{case.get('classname', '')}::{case.get('name', '')}"
        raw = (finding.text or "") + "\n" + finding.get("message", "")
        s_base_evidence[node_id] = (
            raw,
            hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest(),
        )
    ledger_ids = {str(row.get("node_id")) for row in nodes}
    if (
        len(ledger_ids) != len(nodes)
        or ledger_ids != set(s_base_evidence)
        or ledger.get("observed_nonpassing_node_count") != len(nodes)
        or ledger.get("propagated_node_count") != sum(
            row.get("primary_or_propagated") == "propagated" for row in nodes
        )
        or ledger.get("primary_root_cause_count") != len(ledger.get("root_causes", []))
        or ledger.get("remaining_failure_node_count") != 0
    ):
        raise AdmissionError("forensic_junit_ledger_mismatch", "ledger does not exactly cover S_base JUnit findings")
    for row in nodes:
        node_id = str(row.get("node_id"))
        classification = _classify_observed_failure(s_base_evidence[node_id][0])
        if (
            classification is None
            or row.get("raw_evidence_sha256") != s_base_evidence[node_id][1]
            or row.get("raw_evidence_artifact") != "configured-current.junit.xml"
            or not isinstance(row.get("raw_evidence_locator"), dict)
            or row.get("disposition") != "candidate_counterfactual_required"
            or row.get("root_cause_id") != classification["root_cause_id"]
            or row.get("category") != classification["category"]
            or row.get("cause_subtype") != classification["cause_subtype"]
            or row.get("evidence_rule") != classification["evidence_rule"]
        ):
            raise AdmissionError("forensic_node_evidence_invalid", node_id)
    graph_edges = graph.get("edges")
    if not isinstance(graph_edges, list) or {str(row.get("to")) for row in graph_edges} != ledger_ids:
        raise AdmissionError("forensic_root_cause_graph_incomplete", "root-cause graph does not cover every observed node")
    rtc_outcomes = rtc.get("historical_rtc_node_fresh_outcomes")
    rtc_gate = rtc.get("standalone_required_gate")
    if (
        not isinstance(rtc_outcomes, list)
        or len(rtc_outcomes) != 2
        or any(row.get("fresh_outcome") != "pass" for row in rtc_outcomes)
        or rtc.get("waiver_applied") is not False
        or rtc.get("historical_failure_claim_used_for_admission") is not False
        or not isinstance(rtc_gate, dict)
        or rtc_gate.get("native_exit_code") != 2
        or rtc_gate.get("raw_receipt_sha256")
        != sha256_file(artifact_paths["rtc_required_gate_receipt"])
        or rtc_gate.get("observation_sha256")
        != sha256_file(artifact_paths["rtc_required_gate_observation"])
        or rtc_gate.get("expected_observed_failure_code_match") is not True
        or rtc_gate.get("selected_bundle_member_count") != 11
        or rtc.get("hypotheses") != rtc_hypotheses
        or rtc.get("all_hypotheses_evidence_derived") is not True
    ):
        raise AdmissionError("forensic_rtc_drift_attribution_invalid", "historical RTC nodes lack raw gate evidence")

    candidate_outcomes: dict[str, str] = {}
    for case in candidate_junit.iter("testcase"):
        node_id = f"{case.get('classname', '')}::{case.get('name', '')}"
        if case.find("failure") is not None:
            candidate_outcomes[node_id] = "failure"
        elif case.find("error") is not None:
            candidate_outcomes[node_id] = "error"
        elif case.find("skipped") is not None:
            candidate_outcomes[node_id] = "skipped"
        else:
            candidate_outcomes[node_id] = "pass"
    if any(candidate_outcomes.get(node_id) != "pass" for node_id in ledger_ids):
        raise AdmissionError("forensic_candidate_counterfactual_not_green", "candidate does not pass every S_base forensic node")
    environment = forensic_receipt.get("environment")
    owner_environment = read_json(environment_receipt_path, code="environment_receipt_invalid")
    interpreter = owner_environment.get("interpreter")
    if (
        not isinstance(environment, dict)
        or not isinstance(interpreter, dict)
        or not isinstance(interpreter.get("path"), str)
        or str(Path(str(environment.get("python_executable", ""))).resolve()).casefold()
        != str(Path(interpreter["path"]).resolve()).casefold()
        or environment.get("python_executable_sha256") != sha256_file(Path(interpreter["path"]))
        or environment.get("python_version") != interpreter.get("python_version")
        or environment.get("pytest_version") != next(
            (row.get("version") for row in owner_environment.get("packages", []) if row.get("name") == "pytest"),
            None,
        )
        or not isinstance(environment.get("uv_version"), str)
    ):
        raise AdmissionError("forensic_environment_mismatch", "forensic interpreter does not match owner-bound environment")

    forensic_evidence_root = evidence_root / "forensic"
    _copy_evidence(receipt_path, forensic_evidence_root / "forensic.json")
    copied_hashes = {"forensic.json": sha256_file(receipt_path)}
    for name, path in artifact_paths.items():
        suffix = "".join(path.suffixes) or ".bin"
        destination_name = f"{name}{suffix}"
        _copy_evidence(path, forensic_evidence_root / destination_name)
        copied_hashes[destination_name] = sha256_file(path)
    return {
        "schema_version": "iris-baseline-admission-forensic-binding-v1",
        "status": "PASS",
        "subject": candidate_subject,
        "forensic_subject": s_base_subject,
        "forensic_receipt_sha256": sha256_file(receipt_path),
        "forensic_artifact_hashes": copied_hashes,
        "observed_nonpassing_node_count": len(nodes),
        "observed_node_ids": sorted(ledger_ids),
        "candidate_counterfactual_pass_count": len(ledger_ids),
        "unknown_failure_count": ledger["unknown_failure_count"],
        "evidence_absent_unclassifiable_count": ledger["evidence_absent_unclassifiable_count"],
        "subject_finding_count": ledger["subject_finding_count"],
        "reproduction_drift": ledger.get("reproduction_drift") is True,
        "raw_assertion_trace_hashes_verified": True,
        "route_receipt_schemas_verified": True,
        "environment_identity_verified": True,
        "rtc_required_gate_evidence_verified": True,
        "rtc_required_gate_expected_failure_code": rtc_observation["expected_failure_code"],
        "rtc_required_gate_observed_failure_code": rtc_observation["observed_failure_code"],
        "rtc_selected_bundle_id": rtc_observation["selected_bundle_id"],
        "rtc_selected_bundle_member_count": rtc_observation["selected_bundle_member_count"],
        "rtc_hypotheses_evidence_derived": True,
    }


def _finalize_qualification_manifest(
    *,
    repo: Path,
    subject: dict[str, str],
    stage_set_path: Path,
    contract_path: Path,
    durable_root: Path,
    launches: dict[str, dict[str, object]],
    path_contract: dict[str, object],
    normal_preflight: dict[str, object],
    path_control_preflight: dict[str, object],
    claim: str,
    stage_hash: str,
    contract_hash: str,
    environment_receipt_path: Path,
) -> dict[str, object]:
    stage_set = read_json(stage_set_path, code="qualification_stage_set_invalid")
    if stage_set.get("subject") != subject:
        raise AdmissionError("qualification_stage_subject_mismatch", str(stage_set_path))
    stages = stage_set.get("stages")
    if not isinstance(stages, dict):
        raise AdmissionError("qualification_stage_set_invalid", "stages object is missing")
    for name in ("s_base_forensic", "static_schema", "focused_rtc_reseal", "exact_current", "configured_current_collection", "configured_current_execution"):
        row = stages.get(name)
        if not isinstance(row, dict) or row.get("status") != "PASS":
            raise AdmissionError("qualification_stage_not_pass", name)

    configured_row = stages["configured_current_execution"]
    if any(configured_row.get(name) != 0 for name in ("native_exit_code", "failed_count", "error_count")):
        raise AdmissionError("configured_current_receipt_not_green", "stage-set configured-current result is not green")
    configured_receipt = _stage_path(stage_set, "configured_current_execution", "receipt")
    configured_junit = _stage_path(stage_set, "configured_current_execution", "junit")
    exact_receipt = _stage_path(stage_set, "exact_current", "receipt")
    collection_receipt = _stage_path(stage_set, "configured_current_collection", "receipt")
    for source in (configured_receipt, configured_junit, exact_receipt, collection_receipt):
        require_external(repo, source, "predecessor-stage evidence")
        if not source.is_file():
            raise AdmissionError("qualification_stage_evidence_missing", str(source))
    configured_payload = read_json(configured_receipt, code="configured_current_receipt_invalid")
    collection_payload = read_json(collection_receipt, code="configured_current_collection_receipt_invalid")
    exact_payload = read_json(exact_receipt, code="exact_current_receipt_invalid")
    if configured_payload.get("status") != "PASS" or collection_payload.get("status") != "PASS":
        raise AdmissionError("configured_current_receipt_not_green", "configured-current denominator receipt is not PASS")
    if exact_payload.get("success") is not True:
        raise AdmissionError("exact_current_receipt_not_green", "exact-current receipt is not PASS")
    if (
        not isinstance(stages["static_schema"].get("test_count"), int)
        or stages["static_schema"].get("test_count", 0) < 1
        or stages["focused_rtc_reseal"].get("test_count") != 11
        or stages["exact_current"].get("test_count") != exact_payload.get("test_count")
        or stages["configured_current_collection"].get("selected_node_count") != collection_payload.get("selected_node_count")
    ):
        raise AdmissionError("qualification_stage_denominator_mismatch", "stage-set counts differ from their bound receipts")

    evidence_root = durable_root / "evidence"
    _copy_evidence(stage_set_path, evidence_root / "predecessor-stage-receipt-set.json")
    _copy_evidence(contract_path, evidence_root / "qualification-contract.json")
    _copy_evidence(configured_receipt, evidence_root / "configured-current.json")
    _copy_evidence(configured_junit, evidence_root / "configured-current.junit.xml")
    _copy_evidence(exact_receipt, evidence_root / "exact-current.json")
    _copy_evidence(collection_receipt, evidence_root / "configured-current-collection.json")
    environment_receipt_path = require_external(repo, environment_receipt_path, "environment receipt")
    environment_payload = read_json(environment_receipt_path, code="environment_receipt_invalid")
    interpreter = environment_payload.get("interpreter")
    if not isinstance(interpreter, dict) or not isinstance(interpreter.get("path"), str):
        raise AdmissionError("environment_receipt_invalid", "interpreter identity is missing")
    _copy_evidence(environment_receipt_path, evidence_root / "environment-receipt.json")

    context = "composite_baseline_admission_chain_stage_6"
    bindings_root = durable_root / "bindings"
    receipt_bindings = {
        "s_base_forensic": "bindings/s_base_forensic.json",
        "configured_current": "bindings/configured_current.json",
        "environment": "bindings/environment.json",
        "rtc": "bindings/rtc.json",
        "reseal_a": "bindings/reseal_a.json",
        "reseal_b": "bindings/reseal_b.json",
        "run_a": "bindings/run_a.json",
        "run_b": "bindings/run_b.json",
        "full_gate_run_a": "bindings/full_gate_run_a.json",
        "full_gate_run_b": "bindings/full_gate_run_b.json",
        "comparison": "comparison/compare_receipt.json",
        "path_control": "bindings/path_control.json",
    }
    write_json(
        bindings_root / "configured_current.json",
        {
            "status": "PASS",
            "subject": subject,
            "native_exit_code": configured_row["native_exit_code"],
            "failed_count": configured_row["failed_count"],
            "error_count": configured_row["error_count"],
            "source_receipt_sha256": sha256_file(configured_receipt),
            "junit_sha256": sha256_file(configured_junit),
        },
    )
    write_json(
        bindings_root / "environment.json",
        {
            "status": "PASS",
            "subject": subject,
            "environment_receipt_sha256": sha256_file(environment_receipt_path),
            "interpreter_path": str(Path(interpreter["path"]).resolve()).replace("\\", "/"),
            "interpreter_sha256": sha256_file(Path(interpreter["path"])),
        },
    )
    forensic_binding = _forensic_stage_binding(
        repo,
        subject,
        stage_set,
        configured_junit,
        environment_receipt_path,
        evidence_root,
    )
    write_json(bindings_root / "s_base_forensic.json", forensic_binding)
    focused = stages["focused_rtc_reseal"]
    focused_receipts = _focused_receipts(repo, subject, stage_set, evidence_root)
    for binding, qualification_field in (
        ("rtc", "rtc_durable_bundle_qualification"),
        ("reseal_a", "reseal_a_qualification"),
        ("reseal_b", "reseal_b_qualification"),
    ):
        if focused.get(qualification_field) != "PASS":
            raise AdmissionError("qualification_stage_not_pass", qualification_field)
        write_json(bindings_root / f"{binding}.json", focused_receipts[binding])

    for label in ("run_a", "run_b"):
        orchestration_path = Path(str(launches[label]["orchestration_receipt"]))
        orchestration = read_json(orchestration_path, code="qualification_orchestration_invalid")
        if orchestration.get("native_exit_code") != 0 or orchestration.get("identity", {}).get("subject") != subject:
            raise AdmissionError("qualification_chain_receipt_invalid", label)
        inner_path = Path(str(orchestration.get("result_receipt", {}).get("path", "")))
        inner = read_json(inner_path, code="qualification_full_gate_receipt_invalid")
        if inner.get("status") != "PASS" or inner.get("subject") != subject or inner.get("execution_context") != context:
            raise AdmissionError("qualification_full_gate_receipt_invalid", label)
        promoted = evidence_root / label
        _copy_evidence(inner_path, promoted / "full_run_receipt.json")
        canonical_path = Path(str(inner.get("canonical_result", {}).get("path", "")))
        _copy_evidence(canonical_path, promoted / "canonical_full_result.json")
        write_json(
            bindings_root / f"{label}.json",
            {
                "status": "PASS",
                "subject": subject,
                "native_exit_code": 0,
                "orchestration_receipt_sha256": sha256_file(orchestration_path),
            },
        )
        write_json(
            bindings_root / f"full_gate_{label}.json",
            {
                "status": "PASS",
                "subject": subject,
                "native_exit_code": 0,
                "execution_context": context,
                "full_run_receipt_sha256": sha256_file(inner_path),
                "canonical_result_sha256": sha256_file(canonical_path),
            },
        )

    path_orchestration_path = Path(str(launches["path_control"]["orchestration_receipt"]))
    path_orchestration = read_json(path_orchestration_path, code="qualification_orchestration_invalid")
    if path_orchestration.get("native_exit_code") != 0 or path_orchestration.get("identity", {}).get("subject") != subject:
        raise AdmissionError("qualification_chain_receipt_invalid", "path_control")
    path_inner_path = Path(str(path_orchestration.get("result_receipt", {}).get("path", "")))
    path_inner = read_json(path_inner_path, code="qualification_full_gate_receipt_invalid")
    if path_inner.get("status") != "PASS" or path_inner.get("subject") != subject or path_inner.get("execution_context") != context:
        raise AdmissionError("qualification_full_gate_receipt_invalid", "path_control")
    path_canonical = Path(str(path_inner.get("canonical_result", {}).get("path", "")))
    _copy_evidence(path_inner_path, evidence_root / "path_control" / "full_run_receipt.json")
    _copy_evidence(path_canonical, evidence_root / "path_control" / "canonical_full_result.json")
    write_json(
        bindings_root / "path_control.json",
        {
            "status": "PASS",
            "subject": subject,
            "native_exit_code": 0,
            "execution_context": context,
            "full_run_receipt_sha256": sha256_file(path_inner_path),
            "canonical_result_sha256": sha256_file(path_canonical),
        },
    )

    preconditions = read_json(repo / "Iris/validation/baseline_admission/contracts/admission_precondition_registry.json")
    fixtures = read_json(repo / "Iris/validation/baseline_admission/contracts/admission_negative_fixture_registry.json")
    coverage = validate_registry(preconditions, fixtures)
    if coverage.get("status") != "PASS":
        raise AdmissionError("admission_negative_coverage_incomplete", json.dumps(coverage, sort_keys=True))
    owner_decision = read_json(repo / "Iris/validation/baseline_admission/authority/full_repository_test_membership_owner_decision.json")
    membership = owner_decision.get("decision")
    if owner_decision.get("approved_by_owner") is not True or membership not in {"adopted", "not_applicable_dedicated_route"}:
        raise AdmissionError("full_repository_membership_decision_missing", "owner decision is invalid")

    durable_manifest = {
        path.relative_to(durable_root).as_posix(): sha256_file(path)
        for path in sorted(durable_root.rglob("*"))
        if path.is_file()
    }
    return {
        "schema_version": "iris-baseline-admission-qualification-run-v1",
        "status": "PASS",
        "subject": subject,
        "claim_id": claim,
        "execution_context": context,
        "full_gate_execution_context": context,
        "predecessor_stage_receipt_set_sha256": stage_hash,
        "qualification_contract_sha256": contract_hash,
        "environment_receipt_sha256": sha256_file(environment_receipt_path),
        "windows_path_contract": path_contract,
        "normal_path_preflight": normal_preflight,
        "near_boundary_path_preflight": path_control_preflight,
        "launches": launches,
        "configured_current_exit_code": 0,
        "configured_current_failed_count": 0,
        "configured_current_error_count": 0,
        "rtc_successor_bundle_adoption_pending": False,
        "full_repository_test_membership_owner_adoption": membership,
        "configured_current_green": True,
        "rtc_durable_bundle_qualification": True,
        "reseal_a_qualification": True,
        "reseal_b_qualification": True,
        "baseline_admission_run_a_chain": True,
        "baseline_admission_run_b_chain": True,
        "full_repository_denominator_identity_match": True,
        "full_repository_dependency_inventory_identity_match": True,
        "full_repository_canonical_result_identity_match": True,
        "full_repository_execution_context_identity_match": True,
        "near_boundary_path_control": True,
        "baseline_admission_dedicated_test_route": True,
        "s_base_forensic_evidence_bound": True,
        "durable_evidence_retrievable": True,
        "negative_coverage_complete": True,
        "configured_current_denominator_reduction_count": 0,
        "full_repository_denominator_reduction_count": 0,
        "unknown_failure_count": forensic_binding["unknown_failure_count"],
        "evidence_absent_unclassifiable_count": forensic_binding["evidence_absent_unclassifiable_count"],
        "workflow_consolidation_application_delta_count": 0,
        "required_manifest_mutation_without_owner_adoption_count": 0,
        "full_repository_census_membership_added_without_adoption_count": 0,
        "unresolved_finding_count": forensic_binding["subject_finding_count"],
        "precondition_negative_coverage": coverage,
        "receipt_bindings": receipt_bindings,
        "durable_evidence_hash_manifest": durable_manifest,
    }


def _windows_powershell_environment(base: dict[str, str] | None = None) -> dict[str, str]:
    """Keep Windows PowerShell from autoloading incompatible PowerShell 7 modules."""
    environment = dict(os.environ if base is None else base)
    program_files = environment.get("ProgramFiles", r"C:\Program Files").rstrip("\\/")
    windows = environment.get("WINDIR", r"C:\Windows").rstrip("\\/")
    environment["PSModulePath"] = ";".join((
        program_files + r"\WindowsPowerShell\Modules",
        windows + r"\System32\WindowsPowerShell\v1.0\Modules",
    ))
    return environment


def qualify(args: argparse.Namespace) -> dict:
    """Run the canonical A/B/P full-gate launchers from an exact clean source.

    Focused/configured stage receipts are deliberately supplied as one
    immutable external receipt-set; this wrapper hashes and passes that exact
    object to every stage-6 launch rather than inferring prior-stage PASS.
    """
    repo = Path(args.repo).resolve()
    subject = repo_identity(repo, args.commit)
    if not clean_worktree(repo):
        raise AdmissionError("qualification_subject_not_clean", "qualification source checkout must be clean")
    roots = {name: Path(getattr(args, name)) for name in (
        "determinism_checkout_slot", "run_a_work_root", "run_a_result_root",
        "run_b_work_root", "run_b_result_root", "path_control_checkout_root",
        "path_control_work_root", "path_control_result_root", "durable_root", "out",
    )}
    resolved = {name: require_external(repo, path, name.replace("_", " ")) for name, path in roots.items()}
    if len({str(path) for path in resolved.values()}) != len(resolved):
        raise AdmissionError("qualification_roots_not_disjoint", "qualification roots must be pairwise distinct")
    directory_roots = {
        name: path for name, path in resolved.items()
        if name not in {"determinism_checkout_slot", "path_control_checkout_root", "out"}
    }
    directory_values = list(directory_roots.values())
    for index, left in enumerate(directory_values):
        for right in directory_values[index + 1:]:
            try:
                left.relative_to(right)
            except ValueError:
                try:
                    right.relative_to(left)
                except ValueError:
                    continue
            raise AdmissionError("qualification_roots_not_disjoint", f"nested qualification roots: {left}, {right}")
    for name, path in directory_roots.items():
        if not path.is_dir() or any(path.iterdir()):
            raise AdmissionError("qualification_root_not_new_empty", f"{name} must be a caller-created empty directory")
    stage_set = require_external(repo, Path(args.predecessor_stage_receipt_set), "predecessor stage receipt set")
    contract = require_external(repo, Path(args.qualification_contract), "qualification contract")
    if not stage_set.is_file() or not contract.is_file():
        raise AdmissionError("qualification_identity_input_missing", "stage receipt set or qualification contract is missing")
    stage_hash, contract_hash = sha256_file(stage_set), sha256_file(contract)
    launcher_relative = Path("Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1")
    comparator_relative = Path("Iris/validation/clean_checkout/invoke_deterministic_compare.ps1")
    if not (repo / launcher_relative).is_file() or not (repo / comparator_relative).is_file():
        raise AdmissionError("qualification_launcher_missing", "canonical full-gate launcher is missing")
    path_contract_path = repo / "Iris/validation/baseline_admission/contracts/windows_path_contract.json"
    path_contract = read_json(path_contract_path, code="windows_path_contract_invalid")
    normal_preflight = path_preflight(path_contract, resolved["determinism_checkout_slot"])
    path_control_preflight = path_preflight(path_contract, resolved["path_control_checkout_root"])
    if normal_preflight["status"] != "PASS":
        raise AdmissionError("windows_path_contract_rejected", "determinism checkout slot is outside the qualified range")
    if path_control_preflight["status"] != "PASS":
        raise AdmissionError("windows_path_contract_rejected", "path-control checkout root is outside the qualified range")
    if path_control_preflight["materialized_path_length"] != path_control_preflight["qualified_materialized_path_limit"]:
        raise AdmissionError("path_control_not_near_boundary", "path-control checkout root must exercise the exact qualified boundary")
    claim = f"iris-baseline-admission-{subject['commit']}"
    launches: dict[str, dict[str, object]] = {}
    run_b_checkout: Path | None = None
    for label, checkout_key, work_key, result_key in (
        ("run_a", "determinism_checkout_slot", "run_a_work_root", "run_a_result_root"),
        ("run_b", "determinism_checkout_slot", "run_b_work_root", "run_b_result_root"),
    ):
        result_root = resolved[result_key]
        orchestration = (
            resolved["durable_root"]
            / "orchestration"
            / label
            / "receipt.json"
        )
        checkout = resolved[checkout_key]
        if checkout.exists():
            if any(checkout.iterdir()):
                raise AdmissionError("qualification_checkout_slot_not_empty", f"{label} checkout root is not empty")
            checkout.rmdir()
        clone = subprocess.run(
            ["git", "-c", "core.longpaths=true", "clone", "--no-local", "--no-checkout", str(repo), str(checkout)],
            cwd=checkout.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        checkout_result = subprocess.run(
            ["git", "-c", "core.longpaths=true", "-C", str(checkout), "checkout", "--detach", subject["commit"]],
            cwd=checkout.parent,
            text=True,
            capture_output=True,
            check=False,
        ) if clone.returncode == 0 else None
        if clone.returncode != 0 or checkout_result is None or checkout_result.returncode != 0:
            launches[label] = {"native_exit_code": clone.returncode if clone.returncode != 0 else checkout_result.returncode, "checkout_root": str(checkout), "clone_stderr": clone.stderr, "checkout_stderr": "" if checkout_result is None else checkout_result.stderr}
            break
        launcher = checkout / launcher_relative
        command = [
            "powershell", "-ExecutionPolicy", "Bypass", "-File", str(launcher),
            "-RepositoryRoot", str(checkout), "-Commit", subject["commit"], "-ClaimId", claim,
            "-EnvironmentReceipt", args.environment_receipt, "-ExecutionContext", "composite_baseline_admission_chain_stage_6",
            "-PredecessorStageReceiptSetSha256", stage_hash, "-QualificationContractSha256", contract_hash,
            "-PredecessorStageReceiptSet", str(stage_set), "-QualificationContract", str(contract),
            "-WorkRoot", str(resolved[work_key]), "-ResultRoot", str(result_root), "-OrchestrationReceipt", str(orchestration),
        ]
        completed = subprocess.run(
            command,
            cwd=checkout,
            env=_windows_powershell_environment(),
            text=True,
            capture_output=True,
            check=False,
        )
        launches[label] = {"native_exit_code": completed.returncode, "checkout_root": str(checkout), "orchestration_receipt": str(orchestration), "stdout": completed.stdout, "stderr": completed.stderr}
        if label == "run_b":
            run_b_checkout = checkout
        else:
            _remove_checkout(checkout)
            launches[label]["checkout_cleanup_status"] = "PASS" if not checkout.exists() else "FAIL"
        if completed.returncode != 0:
            break
    if all(launches.get(name, {}).get("native_exit_code") == 0 for name in ("run_a", "run_b")):
        compare_root = resolved["durable_root"] / "comparison"
        compare_root.mkdir(parents=True, exist_ok=False)
        compare = subprocess.run([
            "powershell", "-ExecutionPolicy", "Bypass", "-File", str(run_b_checkout / comparator_relative),
            "-RepositoryRoot", str(run_b_checkout), "-Commit", subject["commit"], "-ClaimId", claim,
            "-EnvironmentReceipt", args.environment_receipt,
            "-RunAOrchestrationReceipt", launches["run_a"]["orchestration_receipt"],
            "-RunBOrchestrationReceipt", launches["run_b"]["orchestration_receipt"],
            "-AttemptRoot", str(compare_root), "-ExecutionContext", "composite_baseline_admission_chain_stage_6",
        ], cwd=repo, env=_windows_powershell_environment(), text=True, capture_output=True, check=False)
        launches["comparison"] = {"native_exit_code": compare.returncode, "stdout": compare.stdout, "stderr": compare.stderr}
    if launches.get("comparison", {}).get("native_exit_code") == 0:
        checkout = resolved["path_control_checkout_root"]
        result_root = resolved["path_control_result_root"]
        orchestration = (
            resolved["durable_root"]
            / "orchestration"
            / "path_control"
            / "receipt.json"
        )
        clone = subprocess.run(
            ["git", "-c", "core.longpaths=true", "clone", "--no-local", "--no-checkout", str(repo), str(checkout)],
            cwd=checkout.parent, text=True, capture_output=True, check=False,
        )
        checkout_result = subprocess.run(
            ["git", "-c", "core.longpaths=true", "-C", str(checkout), "checkout", "--detach", subject["commit"]],
            cwd=checkout.parent, text=True, capture_output=True, check=False,
        ) if clone.returncode == 0 else None
        if clone.returncode != 0 or checkout_result is None or checkout_result.returncode != 0:
            launches["path_control"] = {
                "native_exit_code": clone.returncode if clone.returncode != 0 else checkout_result.returncode,
                "checkout_root": str(checkout), "clone_stderr": clone.stderr,
                "checkout_stderr": "" if checkout_result is None else checkout_result.stderr,
            }
        else:
            command = [
                "powershell", "-ExecutionPolicy", "Bypass", "-File", str(checkout / launcher_relative),
                "-RepositoryRoot", str(checkout), "-Commit", subject["commit"], "-ClaimId", claim,
                "-EnvironmentReceipt", args.environment_receipt, "-ExecutionContext", "composite_baseline_admission_chain_stage_6",
                "-PredecessorStageReceiptSetSha256", stage_hash, "-QualificationContractSha256", contract_hash,
                "-PredecessorStageReceiptSet", str(stage_set), "-QualificationContract", str(contract),
                "-WorkRoot", str(resolved["path_control_work_root"]), "-ResultRoot", str(result_root),
                "-OrchestrationReceipt", str(orchestration),
            ]
            completed = subprocess.run(
                command,
                cwd=checkout,
                env=_windows_powershell_environment(),
                text=True,
                capture_output=True,
                check=False,
            )
            launches["path_control"] = {
                "native_exit_code": completed.returncode, "checkout_root": str(checkout),
                "orchestration_receipt": str(orchestration), "stdout": completed.stdout, "stderr": completed.stderr,
            }
        _remove_checkout(checkout)
        launches["path_control"]["checkout_cleanup_status"] = "PASS" if not checkout.exists() else "FAIL"
    if all(launches.get(name, {}).get("native_exit_code") == 0 for name in ("run_a", "path_control")):
        comparison_path = resolved["durable_root"] / "path-control-comparison.json"
        try:
            _compare_path_control(
                Path(str(launches["run_a"]["orchestration_receipt"])),
                Path(str(launches["path_control"]["orchestration_receipt"])),
                subject,
                comparison_path,
            )
            launches["path_control_comparison"] = {"native_exit_code": 0, "receipt": str(comparison_path)}
        except AdmissionError as exc:
            launches["path_control_comparison"] = {"native_exit_code": 1, "rejection_code": exc.code, "message": exc.message}
    if run_b_checkout is not None and run_b_checkout.exists():
        _remove_checkout(run_b_checkout)
        launches["run_b"]["checkout_cleanup_status"] = "PASS" if not run_b_checkout.exists() else "FAIL"
    status = "PASS" if all(row.get("native_exit_code") == 0 for row in launches.values()) and len(launches) == 5 else "FAIL"
    if status == "PASS":
        return _finalize_qualification_manifest(
            repo=repo,
            subject=subject,
            stage_set_path=stage_set,
            contract_path=contract,
            durable_root=resolved["durable_root"],
            launches=launches,
            path_contract=path_contract,
            normal_preflight=normal_preflight,
            path_control_preflight=path_control_preflight,
            claim=claim,
            stage_hash=stage_hash,
            contract_hash=contract_hash,
            environment_receipt_path=Path(args.environment_receipt),
        )
    return {
        "schema_version": "iris-baseline-admission-qualification-run-v1", "status": status,
        "subject": subject, "claim_id": claim,
        "execution_context": "composite_baseline_admission_chain_stage_6",
        "predecessor_stage_receipt_set_sha256": stage_hash,
        "qualification_contract_sha256": contract_hash,
        "windows_path_contract": path_contract,
        "normal_path_preflight": normal_preflight,
        "near_boundary_path_preflight": path_control_preflight,
        "launches": launches,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    collect = sub.add_parser("forensic")
    collect.add_argument("--repo", required=True)
    collect.add_argument("--result-root", required=True)
    collect.add_argument("--out", required=True)
    qualify_parser = sub.add_parser("qualify")
    qualify_parser.add_argument("--repo", required=True)
    qualify_parser.add_argument("--commit", required=True)
    qualify_parser.add_argument("--determinism-checkout-slot", required=True)
    qualify_parser.add_argument("--run-a-work-root", required=True)
    qualify_parser.add_argument("--run-a-result-root", required=True)
    qualify_parser.add_argument("--run-b-work-root", required=True)
    qualify_parser.add_argument("--run-b-result-root", required=True)
    qualify_parser.add_argument("--path-control-checkout-root", required=True)
    qualify_parser.add_argument("--path-control-work-root", required=True)
    qualify_parser.add_argument("--path-control-result-root", required=True)
    qualify_parser.add_argument("--environment-receipt", required=True)
    qualify_parser.add_argument("--durable-root", required=True)
    qualify_parser.add_argument("--predecessor-stage-receipt-set", required=True)
    qualify_parser.add_argument("--qualification-contract", required=True)
    qualify_parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        require_external(Path(args.repo), Path(args.out), "admission receipt")
        payload = forensic(Path(args.repo), Path(args.result_root)) if args.command == "forensic" else qualify(args)
        write_json(Path(args.out), payload)
        return int(payload.get("native_exit_code", 0 if payload.get("status") == "PASS" else 1))
    except Exception as exc:
        wrapped = exc if isinstance(exc, AdmissionError) else AdmissionError("qualification_unhandled_exception", str(exc))
        rejection = {
            "schema_version": "iris-baseline-admission-qualification-rejection-v1",
            "status": "FAIL", "rejection_code": wrapped.code, "message": wrapped.message,
        }
        try:
            write_json(Path(args.out), rejection)
        except OSError:
            pass
        print(str(wrapped), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
