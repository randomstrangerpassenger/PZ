"""Validate Iris baseline-admission evidence without granting authority writes."""

from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from Iris.validation.baseline_admission.iris_baseline_admission_common import (
    AdmissionError, CONTEXT, S_BASE_COMMIT, S_BASE_TREE, clean_worktree, path_preflight, read_json, repo_identity,
    require_boolean, require_external, require_zero, sha256_file, validate_registry, write_json,
)


BOOLEAN_REQUIREMENTS = (
    "configured_current_green", "rtc_durable_bundle_qualification", "reseal_a_qualification",
    "reseal_b_qualification", "baseline_admission_run_a_chain", "baseline_admission_run_b_chain",
    "full_repository_denominator_identity_match", "full_repository_dependency_inventory_identity_match",
    "full_repository_canonical_result_identity_match", "full_repository_execution_context_identity_match",
    "near_boundary_path_control", "baseline_admission_dedicated_test_route",
    "s_base_forensic_evidence_bound", "durable_evidence_retrievable", "negative_coverage_complete",
)
ZERO_REQUIREMENTS = (
    "configured_current_denominator_reduction_count", "full_repository_denominator_reduction_count",
    "unknown_failure_count", "evidence_absent_unclassifiable_count", "workflow_consolidation_application_delta_count",
    "required_manifest_mutation_without_owner_adoption_count", "full_repository_census_membership_added_without_adoption_count",
    "unresolved_finding_count",
)

REQUIRED_RECEIPTS = (
    "s_base_forensic", "configured_current", "environment", "rtc", "reseal_a", "reseal_b", "run_a", "run_b",
    "full_gate_run_a", "full_gate_run_b", "comparison", "path_control",
)


def _receipt_bundle(payload: dict[str, Any], durable_root: Path) -> dict[str, dict[str, Any]]:
    bindings = payload.get("receipt_bindings")
    manifest = payload.get("durable_evidence_hash_manifest")
    if not isinstance(bindings, dict) or not isinstance(manifest, dict):
        raise AdmissionError("admission_receipt_bindings_missing", "receipt bindings and durable hash manifest are required")
    receipts: dict[str, dict[str, Any]] = {}
    for name in REQUIRED_RECEIPTS:
        relative = bindings.get(name)
        if not isinstance(relative, str) or not relative:
            raise AdmissionError("admission_receipt_binding_missing", name)
        expected = manifest.get(relative)
        if not isinstance(expected, str):
            raise AdmissionError("durable_evidence_hash_manifest_missing", relative)
        path = (durable_root / relative).resolve()
        try:
            path.relative_to(durable_root.resolve())
        except ValueError as exc:
            raise AdmissionError("durable_evidence_path_escape", relative) from exc
        if not path.is_file() or sha256_file(path) != expected:
            raise AdmissionError("durable_evidence_hash_mismatch", relative)
        receipts[name] = read_json(path)
    return receipts


def _require_successful_receipts(
    receipts: dict[str, dict[str, Any]],
    subject: dict[str, str],
    durable_manifest: dict[str, str],
) -> None:
    for name, receipt in receipts.items():
        if receipt.get("subject") != subject:
            raise AdmissionError("qualification_receipt_subject_mismatch", name)
    configured = receipts["configured_current"]
    if any(configured.get(field) != 0 for field in ("native_exit_code", "failed_count", "error_count")):
        raise AdmissionError("configured_current_receipt_not_green", "configured-current receipt contains a nonzero result")
    forensic = receipts["s_base_forensic"]
    observed_ids = forensic.get("observed_node_ids")
    artifact_hashes = forensic.get("forensic_artifact_hashes")
    if (
        forensic.get("status") != "PASS"
        or forensic.get("forensic_subject") != {"commit": S_BASE_COMMIT, "tree": S_BASE_TREE}
        or not isinstance(observed_ids, list)
        or not observed_ids
        or any(not isinstance(node_id, str) or not node_id for node_id in observed_ids)
        or len(set(observed_ids)) != len(observed_ids)
        or forensic.get("observed_nonpassing_node_count") != len(observed_ids)
        or forensic.get("candidate_counterfactual_pass_count") != len(observed_ids)
        or forensic.get("unknown_failure_count") != 0
        or forensic.get("evidence_absent_unclassifiable_count") != 0
        or forensic.get("subject_finding_count") != 0
        or forensic.get("raw_assertion_trace_hashes_verified") is not True
        or forensic.get("route_receipt_schemas_verified") is not True
        or forensic.get("environment_identity_verified") is not True
        or forensic.get("rtc_required_gate_evidence_verified") is not True
        or forensic.get("rtc_required_gate_expected_failure_code")
        != forensic.get("rtc_required_gate_observed_failure_code")
        or not isinstance(forensic.get("rtc_required_gate_observed_failure_code"), str)
        or not forensic.get("rtc_required_gate_observed_failure_code")
        or not isinstance(forensic.get("rtc_selected_bundle_id"), str)
        or not forensic.get("rtc_selected_bundle_id")
        or forensic.get("rtc_selected_bundle_member_count") != 11
        or forensic.get("rtc_hypotheses_evidence_derived") is not True
        or not isinstance(forensic.get("reproduction_drift"), bool)
        or not isinstance(artifact_hashes, dict)
        or not artifact_hashes
        or any(not isinstance(value, str) or len(value) != 64 for value in artifact_hashes.values())
    ):
        raise AdmissionError("s_base_forensic_qualification_receipt_invalid", "S_base evidence binding is incomplete")
    for name, expected in artifact_hashes.items():
        if durable_manifest.get(f"evidence/forensic/{name}") != expected:
            raise AdmissionError("s_base_forensic_artifact_manifest_mismatch", name)
    environment = receipts["environment"]
    if (
        environment.get("status") != "PASS"
        or not isinstance(environment.get("environment_receipt_sha256"), str)
        or len(environment["environment_receipt_sha256"]) != 64
        or not isinstance(environment.get("interpreter_sha256"), str)
        or len(environment["interpreter_sha256"]) != 64
    ):
        raise AdmissionError("environment_qualification_receipt_invalid", "environment binding is incomplete")
    for name in ("rtc", "reseal_a", "reseal_b", "path_control"):
        if receipts[name].get("status") != "PASS":
            raise AdmissionError("qualification_receipt_not_pass", name)
    rtc = receipts["rtc"]
    if (
        rtc.get("promotion_role_count") != 11
        or rtc.get("member_inventory_relation_verified") is not True
        or rtc.get("hash_relation_verified") is not True
        or rtc.get("byte_relation_verified") is not True
        or rtc.get("tracking_visibility_verified") is not True
        or rtc.get("consumer_resolution_verified") is not True
        or rtc.get("rtc_global_pass_claimed") is not False
        or rtc.get("observed_node_count") != 2
    ):
        raise AdmissionError("rtc_qualification_receipt_invalid", "RTC receipt lacks durable parity evidence")
    for name, count in (("reseal_a", 5), ("reseal_b", 4)):
        receipt = receipts[name]
        if (
            receipt.get("observed_node_count") != count
            or receipt.get("repository_local_generated_write_count") != 0
            or not isinstance(receipt.get("ordered_node_ids"), list)
            or len(receipt["ordered_node_ids"]) != count
        ):
            raise AdmissionError("reseal_qualification_receipt_invalid", name)
    for name in ("run_a", "run_b", "full_gate_run_a", "full_gate_run_b"):
        receipt = receipts[name]
        if receipt.get("subject") != subject or receipt.get("native_exit_code") != 0:
            raise AdmissionError("qualification_chain_receipt_invalid", name)
        if name.startswith("full_gate") and receipt.get("execution_context") != CONTEXT:
            raise AdmissionError("full_gate_execution_context_mismatch", name)
    comparison = receipts["comparison"]
    if comparison.get("status") not in {"PASS", "succeeded"} or comparison.get("execution_context") != CONTEXT:
        raise AdmissionError("comparison_receipt_invalid", "Run A/B comparison is not bound to stage 6")


def admit(repo: Path, qualification: Path, durable_root: Path) -> dict[str, Any]:
    repo = repo.resolve()
    require_external(repo, durable_root, "durable root")
    payload = read_json(qualification)
    identity = repo_identity(repo)
    subject = payload.get("subject")
    if subject != identity:
        raise AdmissionError("stale_subject_receipt", "qualification subject does not match candidate checkout")
    if not clean_worktree(repo):
        raise AdmissionError("dirty_checkout_rejected", "candidate checkout is not clean")
    path_contract = payload.get("windows_path_contract")
    if not isinstance(path_contract, dict):
        raise AdmissionError("windows_path_contract_missing", "qualification lacks path contract")
    preflight = path_preflight(path_contract, repo)
    if preflight["status"] != "PASS":
        raise AdmissionError("windows_path_contract_rejected", "candidate checkout is outside declared path budget")
    if payload.get("full_gate_execution_context") != CONTEXT:
        raise AdmissionError("full_gate_execution_context_mismatch", "composite stage-6 context is absent or mismatched")
    if payload.get("configured_current_exit_code") != 0 or payload.get("configured_current_failed_count") != 0 or payload.get("configured_current_error_count") != 0:
        raise AdmissionError("configured_current_result_missing_or_nonzero", "configured-current result is not exact green")
    if payload.get("rtc_successor_bundle_adoption_pending") is not False:
        raise AdmissionError("rtc_successor_bundle_adoption_pending", "RTC successor selection is not adopted")
    membership = payload.get("full_repository_test_membership_owner_adoption")
    if membership not in {"adopted", "not_applicable_dedicated_route"}:
        raise AdmissionError("full_repository_membership_decision_missing", "membership owner decision is invalid")
    if membership == "not_applicable_dedicated_route" and (
        payload.get("baseline_admission_dedicated_test_route") is not True
        or payload.get("full_repository_census_membership_added_without_adoption_count") != 0
    ):
        raise AdmissionError("full_repository_membership_not_applicable_invalid", "dedicated-route disposition prerequisites are missing")
    for field in BOOLEAN_REQUIREMENTS:
        require_boolean(payload, field)
    for field in ZERO_REQUIREMENTS:
        require_zero(payload, field)
    registry = payload.get("precondition_negative_coverage")
    if not isinstance(registry, dict) or registry.get("status") != "PASS":
        raise AdmissionError("admission_negative_coverage_missing", "precondition coverage receipt is not PASS")
    durable_manifest = payload.get("durable_evidence_hash_manifest")
    if not isinstance(durable_manifest, dict) or not durable_manifest:
        raise AdmissionError("durable_evidence_hash_manifest_missing", "durable evidence manifest is missing")
    for relative, expected in durable_manifest.items():
        path = (durable_root / relative).resolve()
        try:
            path.relative_to(durable_root.resolve())
        except ValueError as exc:
            raise AdmissionError("durable_evidence_path_escape", relative) from exc
        if not path.is_file() or sha256_file(path) != expected:
            raise AdmissionError("durable_evidence_hash_mismatch", relative)
    _require_successful_receipts(_receipt_bundle(payload, durable_root), identity, durable_manifest)
    return {
        "schema_version": "iris-baseline-admission-receipt-v1",
        "status": "admitted",
        "subject": identity,
        "qualification_sha256": sha256_file(qualification),
        "durable_evidence_file_count": len(durable_manifest),
        "baseline_admission_gate_implementation": "fail_closed",
        "baseline_admission_gate_enforcement_proof": "synthetic_harness_only",
        "baseline_admission_gate_real_entry_binding": "pending_absent_application_entrypoint",
    }


def synthetic_gate(payload: dict[str, Any]) -> dict[str, Any]:
    calls = 0
    try:
        if payload.get("admission_status") != "admitted":
            raise AdmissionError("synthetic_gate_rejected", "receipt is not admitted")
        calls += 1
        return {"status": "PASS", "mutator_call_count": calls, "gate_before_application_mutation_synthetic": True}
    except AdmissionError as exc:
        return {"status": "REJECTED", "rejection_code": exc.code, "mutator_call_count": calls, "gate_before_application_mutation_synthetic": True}


def _matrix_repository(root: Path) -> tuple[Path, dict[str, str]]:
    repo = root / "subject"
    repo.mkdir(parents=True)
    (repo / "subject.txt").write_text("matrix subject\n", encoding="utf-8")
    commands = (
        ("init", "-q"),
        ("add", "."),
        ("-c", "user.name=Iris Matrix", "-c", "user.email=iris-matrix@example.invalid", "commit", "-q", "-m", "matrix subject"),
    )
    for arguments in commands:
        completed = subprocess.run(["git", "-C", str(repo), *arguments], text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            raise AdmissionError("admission_matrix_setup_failed", completed.stderr.strip())
    return repo, repo_identity(repo)


def _clone_exact(source: Path, target: Path, commit: str) -> dict[str, str]:
    clone = subprocess.run(
        ["git", "-c", "core.longpaths=true", "clone", "--no-local", "--no-checkout", str(source), str(target)],
        text=True,
        capture_output=True,
        check=False,
    )
    checkout = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-C", str(target), "checkout", "--detach", commit],
        text=True,
        capture_output=True,
        check=False,
    ) if clone.returncode == 0 else None
    if clone.returncode != 0 or checkout is None or checkout.returncode != 0:
        detail = clone.stderr if clone.returncode != 0 else checkout.stderr
        raise AdmissionError("admission_matrix_exact_checkout_failed", detail.strip())
    if not clean_worktree(target):
        raise AdmissionError("admission_matrix_exact_checkout_dirty", str(target))
    return repo_identity(target, commit)


def _new_short_checkout_slot(source_repo: Path) -> Path:
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    parent = source_repo.resolve().parent
    offset = os.getpid() % (len(alphabet) ** 2)
    for step in range(len(alphabet) ** 2):
        value = (offset + step) % (len(alphabet) ** 2)
        token = alphabet[value // len(alphabet)] + alphabet[value % len(alphabet)]
        candidate = parent / token
        try:
            candidate.mkdir()
        except FileExistsError:
            continue
        return candidate
    raise AdmissionError("admission_matrix_short_checkout_slot_unavailable", str(parent))


def _remove_matrix_checkout(path: Path) -> None:
    from Iris.validation.baseline_admission.run_iris_baseline_admission import _remove_checkout

    _remove_checkout(path)
    if path.exists():
        raise AdmissionError("admission_matrix_checkout_cleanup_failed", str(path))


def _matrix_qualification(
    root: Path,
    repo: Path,
    subject: dict[str, str],
    coverage: dict[str, Any],
) -> tuple[Path, Path, dict[str, Any]]:
    durable = root / "durable"
    durable.mkdir()
    forensic_evidence = durable / "evidence" / "forensic" / "configured_current_junit.xml"
    forensic_evidence.parent.mkdir(parents=True)
    forensic_evidence.write_text("matrix S_base JUnit evidence\n", encoding="utf-8")
    binding_names = REQUIRED_RECEIPTS
    bindings = {name: f"bindings/{name}.json" for name in binding_names}
    for name in binding_names:
        receipt: dict[str, Any] = {"status": "PASS", "subject": subject}
        if name == "configured_current":
            receipt.update(native_exit_code=0, failed_count=0, error_count=0)
        elif name == "s_base_forensic":
            receipt.update(
                forensic_subject={"commit": S_BASE_COMMIT, "tree": S_BASE_TREE},
                forensic_receipt_sha256="0" * 64,
                forensic_artifact_hashes={
                    "configured_current_junit.xml": sha256_file(forensic_evidence),
                },
                observed_nonpassing_node_count=1,
                observed_node_ids=["matrix::s_base_observed_failure"],
                candidate_counterfactual_pass_count=1,
                unknown_failure_count=0,
                evidence_absent_unclassifiable_count=0,
                subject_finding_count=0,
                reproduction_drift=True,
                raw_assertion_trace_hashes_verified=True,
                route_receipt_schemas_verified=True,
                environment_identity_verified=True,
                rtc_required_gate_evidence_verified=True,
                rtc_required_gate_expected_failure_code="implementation_toolchain_freshness_failed",
                rtc_required_gate_observed_failure_code="implementation_toolchain_freshness_failed",
                rtc_selected_bundle_id="matrix-s-base-bundle",
                rtc_selected_bundle_member_count=11,
                rtc_hypotheses_evidence_derived=True,
            )
        elif name == "environment":
            receipt.update(
                environment_receipt_sha256="1" * 64,
                interpreter_path=sys.executable,
                interpreter_sha256="2" * 64,
            )
        elif name == "rtc":
            receipt.update(
                promotion_role_count=11,
                member_inventory_relation_verified=True,
                hash_relation_verified=True,
                byte_relation_verified=True,
                tracking_visibility_verified=True,
                consumer_resolution_verified=True,
                rtc_global_pass_claimed=False,
                observed_node_count=2,
            )
        elif name in {"reseal_a", "reseal_b"}:
            count = 5 if name == "reseal_a" else 4
            receipt.update(
                observed_node_count=count,
                ordered_node_ids=[f"{name}::{index}" for index in range(count)],
                repository_local_generated_write_count=0,
            )
        elif name in {"run_a", "run_b", "full_gate_run_a", "full_gate_run_b"}:
            receipt["native_exit_code"] = 0
            if name.startswith("full_gate"):
                receipt["execution_context"] = CONTEXT
        elif name == "comparison":
            receipt.update(status="succeeded", execution_context=CONTEXT)
        write_json(durable / bindings[name], receipt)
    manifest = {
        path.relative_to(durable).as_posix(): sha256_file(path)
        for path in durable.rglob("*")
        if path.is_file()
    }
    payload: dict[str, Any] = {
        "subject": subject,
        "windows_path_contract": {
            "budget": {
                "longest_required_relative_path": 0,
                "worst_case_generated_suffix": 0,
                "separator_allowance": 0,
                "safety_margin": 0,
                "qualified_materialized_path_limit": 32767,
            }
        },
        "full_gate_execution_context": CONTEXT,
        "configured_current_exit_code": 0,
        "configured_current_failed_count": 0,
        "configured_current_error_count": 0,
        "rtc_successor_bundle_adoption_pending": False,
        "full_repository_test_membership_owner_adoption": "not_applicable_dedicated_route",
        "precondition_negative_coverage": coverage,
        "receipt_bindings": bindings,
        "durable_evidence_hash_manifest": manifest,
    }
    payload.update({field: True for field in BOOLEAN_REQUIREMENTS})
    payload.update({field: 0 for field in ZERO_REQUIREMENTS})
    qualification = root / "qualification.json"
    write_json(qualification, payload)
    return qualification, durable, payload


def _known_bad_s_base_case(
    source_repo: Path,
    root: Path,
    coverage: dict[str, Any],
) -> dict[str, Any]:
    repo = _new_short_checkout_slot(source_repo)
    try:
        subject = _clone_exact(source_repo, repo, S_BASE_COMMIT)
        if subject != {"commit": S_BASE_COMMIT, "tree": S_BASE_TREE}:
            raise AdmissionError("admission_matrix_s_base_identity_mismatch", json.dumps(subject, sort_keys=True))
        case_root = root / "known-bad-s-base-evidence"
        case_root.mkdir()
        qualification, durable, payload = _matrix_qualification(case_root, repo, subject, coverage)
        configured_relative = payload["receipt_bindings"]["configured_current"]
        configured_path = durable / configured_relative
        configured = read_json(configured_path)
        configured.update(
            {
                "status": "FAIL",
                "native_exit_code": 1,
                "failed_count": 2,
                "error_count": 9,
                "historical_nonpassing_node_count": 11,
                "historical_propagated_node_count": 9,
                "historical_setup_root_cause_count": 2,
                "evidence_basis": "plan_bound_historical_s_base_non_green_census",
            }
        )
        write_json(configured_path, configured)
        payload["durable_evidence_hash_manifest"][configured_relative] = sha256_file(configured_path)
        write_json(qualification, payload)
        try:
            admit(repo, qualification, durable)
        except AdmissionError as exc:
            observed = exc.code
        else:
            observed = "accepted"
        gate = synthetic_gate({"admission_status": "rejected" if observed != "accepted" else "admitted"})
        return {
            "fixture_id": "known_bad_s_base_exact_checkout",
            "expected_rejection_code": "configured_current_receipt_not_green",
            "observed_rejection_code": observed,
            "rejected": observed == "configured_current_receipt_not_green",
            "synthetic_mutator_call_count": gate["mutator_call_count"],
            "exact_subject_checkout": subject == {"commit": S_BASE_COMMIT, "tree": S_BASE_TREE},
            "qualification_subject_matches_checkout": payload["subject"] == subject,
            "historical_non_green_evidence_bound": configured["historical_nonpassing_node_count"] == 11,
        }
    finally:
        _remove_matrix_checkout(repo)


def qualification_over_budget_preflight_case(source_repo: Path, root: Path) -> dict[str, Any]:
    """Invoke qualification one character over budget and prove it wrote nothing."""
    from Iris.validation.baseline_admission.run_iris_baseline_admission import qualify

    candidate_repo = _new_short_checkout_slot(source_repo)
    candidate_subject = _clone_exact(source_repo, candidate_repo, repo_identity(source_repo)["commit"])
    contract = read_json(candidate_repo / "Iris/validation/baseline_admission/contracts/windows_path_contract.json")
    budget = contract["budget"]
    root_length = budget["qualified_materialized_path_limit"] + 1 - sum(
        budget[name]
        for name in (
            "longest_required_relative_path",
            "worst_case_generated_suffix",
            "separator_allowance",
            "safety_margin",
        )
    )
    anchor = candidate_repo.anchor
    if root_length <= len(anchor):
        raise AdmissionError("admission_matrix_path_fixture_invalid", "over-budget root length is not constructible")
    over_budget_checkout = Path(anchor + ("q" * (root_length - len(anchor))))
    if over_budget_checkout.exists():
        over_budget_checkout = Path(anchor + ("z" * (root_length - len(anchor))))
    if over_budget_checkout.exists():
        raise AdmissionError("admission_matrix_path_fixture_collision", str(over_budget_checkout))
    path_control_checkout = Path(anchor + ("p" * (root_length - len(anchor) - 1)))
    if path_control_checkout.exists():
        path_control_checkout = Path(anchor + ("r" * (root_length - len(anchor) - 1)))
    if path_control_checkout.exists():
        raise AdmissionError("admission_matrix_path_fixture_collision", str(path_control_checkout))

    case_root = root / "qualification-over-budget"
    case_root.mkdir()
    directory_names = (
        "run_a_work_root",
        "run_a_result_root",
        "run_b_work_root",
        "run_b_result_root",
        "path_control_work_root",
        "path_control_result_root",
        "durable_root",
    )
    directories: dict[str, Path] = {}
    for name in directory_names:
        path = case_root / name
        path.mkdir()
        directories[name] = path
    stage_set = case_root / "stage.json"
    qualification_contract = case_root / "contract.json"
    write_json(stage_set, {"schema_version": "matrix-stage-set-v1"})
    write_json(qualification_contract, {"schema_version": "matrix-qualification-contract-v1"})
    out = case_root / "qualification.json"
    args = argparse.Namespace(
        repo=str(candidate_repo),
        commit=candidate_subject["commit"],
        determinism_checkout_slot=str(over_budget_checkout),
        path_control_checkout_root=str(path_control_checkout),
        environment_receipt=str(case_root / "unused-environment.json"),
        predecessor_stage_receipt_set=str(stage_set),
        qualification_contract=str(qualification_contract),
        out=str(out),
        **{name: str(path) for name, path in directories.items()},
    )
    try:
        try:
            qualify(args)
        except AdmissionError as exc:
            observed = exc.code
        else:
            observed = "accepted"
        roots_untouched = (
            not over_budget_checkout.exists()
            and not path_control_checkout.exists()
            and not out.exists()
            and all(not any(path.iterdir()) for path in directories.values())
        )
        return {
            "fixture_id": "qualification_one_character_over_budget_before_clone",
            "expected_rejection_code": "windows_path_contract_rejected",
            "observed_rejection_code": observed,
            "rejected": observed == "windows_path_contract_rejected" and roots_untouched,
            "synthetic_mutator_call_count": 0,
            "materialized_path_length": path_preflight(contract, over_budget_checkout)["materialized_path_length"],
            "qualified_materialized_path_limit": budget["qualified_materialized_path_limit"],
            "checkout_work_result_mutation_count": 0 if roots_untouched else 1,
            "qualification_preflight_before_clone_mutation": roots_untouched,
        }
    finally:
        _remove_matrix_checkout(candidate_repo)


def execute_negative_matrix(
    preconditions: dict[str, Any],
    fixtures: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    coverage = validate_registry(preconditions, fixtures)
    if coverage["status"] != "PASS":
        raise AdmissionError("admission_negative_coverage_incomplete", json.dumps(coverage, sort_keys=True))
    repo, subject = _matrix_repository(root)
    qualification, durable, base = _matrix_qualification(root, repo, subject, coverage)
    positive = admit(repo, qualification, durable)
    if positive.get("status") != "admitted":
        raise AdmissionError("admission_matrix_positive_control_failed", "canonical fixture was not admitted")
    results: list[dict[str, Any]] = []
    mutator_calls = 0
    for index, fixture in enumerate(fixtures["fixtures"]):
        payload = copy.deepcopy(base)
        mutation = fixture["mutation"]
        payload[mutation["field"]] = mutation["value"]
        candidate = root / f"negative-{index}.json"
        write_json(candidate, payload)
        try:
            admit(repo, candidate, durable)
        except AdmissionError as exc:
            observed = exc.code
        else:
            observed = "accepted"
        gate = synthetic_gate({"admission_status": "rejected" if observed != "accepted" else "admitted"})
        mutator_calls += gate["mutator_call_count"]
        expected = fixture["expected_rejection_code"]
        results.append(
            {
                "fixture_id": fixture["fixture_id"],
                "invalidates": fixture["invalidates"],
                "expected_rejection_code": expected,
                "observed_rejection_code": observed,
                "rejected": observed == expected,
                "synthetic_mutator_call_count": gate["mutator_call_count"],
            }
        )

    source_repo = Path(__file__).resolve().parents[3]
    known_bad = _known_bad_s_base_case(source_repo, root, coverage)
    results.append(known_bad)
    mutator_calls += int(known_bad["synthetic_mutator_call_count"])

    special_cases = (
        ("wrong_commit", {"subject": {"commit": "0" * 40, "tree": subject["tree"]}}, "stale_subject_receipt"),
        ("wrong_tree", {"subject": {"commit": subject["commit"], "tree": "0" * 40}}, "stale_subject_receipt"),
        ("path_over_budget", {"windows_path_contract": {"budget": {"longest_required_relative_path": 0, "worst_case_generated_suffix": 0, "separator_allowance": 0, "safety_margin": 0, "qualified_materialized_path_limit": 1}}}, "windows_path_contract_rejected"),
        ("rtc_adoption_pending", {"rtc_successor_bundle_adoption_pending": True}, "rtc_successor_bundle_adoption_pending"),
        ("full_gate_context_missing", {"full_gate_execution_context": "standalone_full_gate"}, "full_gate_execution_context_mismatch"),
        ("configured_current_nonzero", {"configured_current_exit_code": 1}, "configured_current_result_missing_or_nonzero"),
    )
    for index, (name, mutation, expected) in enumerate(special_cases):
        payload = copy.deepcopy(base)
        payload.update(mutation)
        candidate = root / f"special-{index}.json"
        write_json(candidate, payload)
        try:
            admit(repo, candidate, durable)
        except AdmissionError as exc:
            observed = exc.code
        else:
            observed = "accepted"
        gate = synthetic_gate({"admission_status": "rejected" if observed != "accepted" else "admitted"})
        mutator_calls += gate["mutator_call_count"]
        results.append(
            {
                "fixture_id": name,
                "expected_rejection_code": expected,
                "observed_rejection_code": observed,
                "rejected": observed == expected,
                "synthetic_mutator_call_count": gate["mutator_call_count"],
            }
        )

    over_budget = qualification_over_budget_preflight_case(source_repo, root)
    results.append(over_budget)
    mutator_calls += int(over_budget["synthetic_mutator_call_count"])

    dirty = repo / "dirty-untracked.txt"
    dirty.write_text("dirty\n", encoding="utf-8")
    try:
        try:
            admit(repo, qualification, durable)
        except AdmissionError as exc:
            dirty_observed = exc.code
        else:
            dirty_observed = "accepted"
    finally:
        dirty.unlink()
    dirty_gate = synthetic_gate({"admission_status": "rejected" if dirty_observed != "accepted" else "admitted"})
    mutator_calls += dirty_gate["mutator_call_count"]
    results.append(
        {
            "fixture_id": "dirty_checkout",
            "expected_rejection_code": "dirty_checkout_rejected",
            "observed_rejection_code": dirty_observed,
            "rejected": dirty_observed == "dirty_checkout_rejected",
            "synthetic_mutator_call_count": dirty_gate["mutator_call_count"],
        }
    )
    all_rejected = all(row["rejected"] and row["synthetic_mutator_call_count"] == 0 for row in results)
    return {
        **coverage,
        "status": "PASS" if all_rejected else "FAIL",
        "executable_negative_case_count": len(results),
        "known_bad_s_base_rejected": next(
            row["rejected"] for row in results if row["fixture_id"] == "known_bad_s_base_exact_checkout"
        ),
        "known_bad_s_base_exact_checkout_exercised": known_bad["exact_subject_checkout"],
        "qualification_over_budget_preflight_before_clone_proven": over_budget[
            "qualification_preflight_before_clone_mutation"
        ],
        "qualified_positive_control_admitted": True,
        "mutator_called_on_rejected_case_count": mutator_calls,
        "cases": results,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    sub = result.add_subparsers(dest="command", required=True)
    matrix = sub.add_parser("validate-matrix")
    matrix.add_argument("--preconditions", required=True)
    matrix.add_argument("--fixtures", required=True)
    matrix.add_argument("--out", required=True)
    admission = sub.add_parser("admit")
    admission.add_argument("--repo", required=True)
    admission.add_argument("--qualification", required=True)
    admission.add_argument("--durable-root", required=True)
    admission.add_argument("--out", required=True)
    synthetic = sub.add_parser("synthetic-gate")
    synthetic.add_argument("--receipt", required=True)
    synthetic.add_argument("--out", required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "validate-matrix":
            with tempfile.TemporaryDirectory(prefix="iris-admission-matrix-") as temporary:
                result = execute_negative_matrix(
                    read_json(Path(args.preconditions)),
                    read_json(Path(args.fixtures)),
                    Path(temporary),
                )
            if result["status"] != "PASS":
                raise AdmissionError("admission_negative_matrix_failed", json.dumps(result, sort_keys=True))
        elif args.command == "admit":
            result = admit(Path(args.repo), Path(args.qualification), Path(args.durable_root))
        else:
            receipt = read_json(Path(args.receipt))
            result = synthetic_gate({"admission_status": receipt.get("status")})
        write_json(Path(args.out), result)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result.get("status") in {"PASS", "admitted"} else 2
    except AdmissionError as exc:
        result = {"schema_version": "iris-baseline-admission-rejection-v1", "status": "rejected", "rejection_code": exc.code, "message": exc.message}
        if hasattr(args, "out"):
            write_json(Path(args.out), result)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
