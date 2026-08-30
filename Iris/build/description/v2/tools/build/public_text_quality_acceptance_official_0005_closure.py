from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Iterable

import public_text_quality_acceptance as base
import public_text_quality_acceptance_official_0005 as official

if str(official.REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(official.REPO_ROOT))
from Iris.validation.execution.checkout_environment import (  # noqa: E402
    ensure_external_root,
)


PREDECESSOR_CORRECTION_ID = "g1-successor-0008-revalidation-0001"
CORRECTION_ID = "g1-successor-0008-revalidation-0002"
G1_GATE_MANIFEST = (
    official.REPO_ROOT
    / "Iris"
    / "validation"
    / "clean_checkout"
    / "evidence"
    / "full_repository_gate_manifest_successor_0008.json"
)
G1_GATE_MANIFEST_SHA256 = (
    "b81878c89f9e1aa4dd9873bd1ec204632547938e33ce33567c09633f77de758f"
)
G1_CLOSEOUT = (
    official.REPO_ROOT
    / "Iris"
    / "validation"
    / "clean_checkout"
    / "authority"
    / "full_repository_technical_debt_closeout_successor_0008.json"
)
G1_CLOSEOUT_SHA256 = (
    "e6c4e877532ac196f4e8f84fcda7274251d26f1431e9a8c5b3192a9ca2e0cc1a"
)
G1_VALIDATED_SUBJECT_COMMIT = "1235e7bc497fea7f33774190a406534509838fa6"
G1_VALIDATED_SUBJECT_TREE = "b19ed0b21d0eafe19e719a16138437edf1dd2fd7"
G1_CANONICAL_RESULT_SHA256 = (
    "2381b79faaecf73780cbe57d518ce788162f1575c990f29d526111af5d746f9f"
)
G1_CANDIDATE_ROUTE_RESULT_SHA256 = (
    "216d142c00c2eb357a35d5d6824dfd3674460eaaeb8d3c6dda972e6d5f427fe0"
)
PREDECESSOR_FAILURE_COMMIT = "6b8549208f27a8a62819fee08864afffd79abfbf"
PREDECESSOR_PHASE6_TREE = "7ada1295f6a449775d26b9a21b27df2c0a17f0d1"
LIVE_BASE_SHA256 = (
    "2ccf98edfd087bb193387a77d0fec5bdb3a1efe9905d66fa9ac5ae74eec2c7d1"
)
CANDIDATE_MANIFEST_SHA256 = (
    "3107201fd7e6da0c8a97a3c8d9ee8119d2d4d9768d0da3fcbcb306cc2447c75b"
)
CANDIDATE_PATCH_SHA256 = (
    "fc2068f1018e9f8ace56e31958702616710d38c38914cb2307c6e598e1db42ad"
)
FAILED_ROUTE_RESULT_SHA256 = (
    "f4306493bf346a076f8745bcb7422f58110a1c01845f7a3d44ddbe6cc91441cb"
)
DISPOSITION_SHA256 = (
    "2a944a8f7e683726229aade6a9afc12e0475b8e46cf980c24dc03a36be560e64"
)
POLICY_SHA256 = (
    "12bf2c9e025108f217bf5c7304a900694503cebe08fc96d60cdf4c96a48267f0"
)
TASK_START_COMMIT = "dd4b8ac37d2b974717364c79aa04afe2fe445f58"
TASK_START_TREE = "64782adcf856213f61c3fbccaad217d321c287f8"

PHASE6 = official.ATTEMPT_ROOT / "phase6"
PHASE7 = official.ATTEMPT_ROOT / "phase7"
PREDECESSOR_CORRECTION_ROOT = (
    PHASE6 / "corrections" / PREDECESSOR_CORRECTION_ID
)
PREDECESSOR_CORRECTION_ROUTE_RESULT = (
    PREDECESSOR_CORRECTION_ROOT / "candidate_current_route_result.json"
)
PREDECESSOR_CORRECTION_FAILURE_RECORD = (
    PREDECESSOR_CORRECTION_ROOT / "phase6_revalidation_failure_record.json"
)
PREDECESSOR_CORRECTION_ROUTE_RESULT_SHA256 = (
    "5ee07d23641dc9253057efea275ff0f31ca8686451b581c102580bf4d88554fe"
)
PREDECESSOR_CORRECTION_FAILURE_RECORD_SHA256 = (
    "1a92afe40ff2dcdbdf5f3fdbbcafc87160ca71ba1068f86580d21234d9ba19d5"
)
CORRECTION_ROOT = PHASE6 / "corrections" / CORRECTION_ID
LONG_ROOT_FAILURE_EXECUTION_ENVIRONMENT_RECEIPT = (
    CORRECTION_ROOT / "execution_environment_receipt.json"
)
LONG_ROOT_FAILURE_AFFECTED_TEST_RESULT = (
    CORRECTION_ROOT / "affected_tests_result.json"
)
LONG_ROOT_FAILURE_ROUTE_RESULT = (
    CORRECTION_ROOT / "candidate_current_route_result.json"
)
LONG_ROOT_FAILURE_EXECUTION_ENVIRONMENT_RECEIPT_SHA256 = (
    "3fb55560c3ab08b6cec917ad413250ebe907164a9734f1b0055a0313ebb9dfb0"
)
LONG_ROOT_FAILURE_AFFECTED_TEST_RESULT_SHA256 = (
    "528fb35ecfb8426c8b49aa7d0a812e81e3ac21df01b5ec40b780ccea10dd2e95"
)
LONG_ROOT_FAILURE_ROUTE_RESULT_SHA256 = (
    "26e7c2582d5f4095527ae1c49d8673ddb803d5ed5d0f683bdefd016170aa3e18"
)
LONG_PATH_PARTIAL_REVALIDATION_RECORD = (
    CORRECTION_ROOT / "phase6_revalidation_record.json"
)
LONG_PATH_PARTIAL_REVALIDATION_RECORD_SHA256 = (
    "527ffa45144e1f883fdcfff305f501373bb6c7d590351d74794bf08a398b4bf5"
)
EXECUTION_ENVIRONMENT_RECEIPT = (
    CORRECTION_ROOT / "env_receipt_s2.json"
)
AFFECTED_TEST_RESULT = (
    CORRECTION_ROOT / "affected_4_s2.json"
)
CORRECTION_ROUTE_RESULT = (
    CORRECTION_ROOT / "route_136_s2.json"
)
REVALIDATION_RECORD = CORRECTION_ROOT / "phase6_pass_s2.json"
ADOPTION_CONTRACT_SUCCESSOR = (
    CORRECTION_ROOT / "gate_contract_s2.json"
)
GATE_DECISION = official.OWNER_INPUT_ROOT / "gate_adoption_decision.json"
OWNER_CLOSURE_SEAL = official.OWNER_INPUT_ROOT / "owner_closure_seal.json"
REVIEWER_INPUT_ROOT = (
    official.V2_ROOT
    / "reviewer_inputs"
    / base.ROUND_ID
    / official.ATTEMPT_ID
)
INDEPENDENT_REVIEW = REVIEWER_INPUT_ROOT / "independent_review.json"
REVIEWER_ELIGIBILITY = (
    REVIEWER_INPUT_ROOT / "reviewer_eligibility_declaration.json"
)
ADOPTION_DECISION_RECORD = PHASE6 / "gate_adoption_decision_record.json"
ADOPTION_RECEIPT = PHASE6 / "live_required_gate_adoption_receipt.json"
POST_ADOPTION_ROUTE_RESULT = PHASE6 / "post_adoption_current_route_result.json"
POST_ADOPTION_EXECUTION_RECEIPT = (
    PHASE6 / "post_adoption_execution_environment_receipt.json"
)
FREEZE_MANIFEST = PHASE7 / "final_evidence_freeze_manifest.json"
FINAL_ARTIFACT_MANIFEST = PHASE7 / "final_artifact_hash_manifest.json"
REVIEW_REQUEST = PHASE7 / "independent_review_request.json"
PRE_REVIEW_VCS_CENSUS = PHASE7 / "vcs_authority_census_pre_review.json"
INDEPENDENT_REVIEW_VALIDATION = (
    PHASE7 / "independent_review_validation_report.json"
)
OWNER_SEAL_VALIDATION = PHASE7 / "owner_seal_validation_report.json"
FINAL_VCS_PRESERVATION = PHASE7 / "final_vcs_preservation_report.json"
FINAL_CLOSEOUT = PHASE7 / "final_closeout_report.json"
TERMINAL_SEAL = PHASE7 / "terminal_hash_seal.json"
CLOSEOUT_DOC = (
    official.REPO_ROOT
    / "docs"
    / "iris_publish_boundary_public_text_quality_acceptance_policy_closure_closeout.md"
)

AFFECTED_TEST_IDS = (
    (
        "test_lua_bridge_export_contract_realign."
        "LuaBridgeExportContractRealignTest."
        "test_bridge_report_forbidden_claim_scan"
    ),
    (
        "test_lua_bridge_export_contract_realign."
        "LuaBridgeExportContractRealignTest."
        "test_chunk_bundle_determinism"
    ),
    (
        "test_lua_bridge_export_contract_realign."
        "LuaBridgeExportContractRealignTest."
        "test_default_route_writes_chunk_bundle_under_pinned_staging_root"
    ),
    (
        "test_lua_bridge_export_contract_realign."
        "LuaBridgeExportContractRealignTest."
        "test_explicit_historical_and_diagnostic_monolith_routes_are_preserved"
    ),
)
AFFECTED_FIXTURE_NAMES = (
    "_tmp_lua_bridge_forbidden_claims",
    "_tmp_lua_bridge_determinism",
    "_tmp_lua_bridge_default_contract",
    "_tmp_lua_bridge_monolith_routes",
)
EXECUTION_ENVIRONMENT_VARIABLE_NAMES = (
    "IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT",
    "TEMP",
    "TMP",
    "TMPDIR",
)

PREDECESSOR_PHASE6_HASHES = {
    "candidate_current_route_result.json": FAILED_ROUTE_RESULT_SHA256,
    "gitignore_exact_unignore_patch.json": (
        "38736a5283b379c7ebf3f554db125ad122c95f5b6e4f97fc34cda5136e6f4506"
    ),
    "pre_adoption_protected_surface_report.json": (
        "301f5a5fbf2adbbb755de9e6581d3086b324ecedebd7161602fd24e1ee3ddbde"
    ),
    "required_artifact_recensus_report.json": (
        "de42355d0daf2055abd164ddf34f8b1c959fb97eb9162ce30d194a04440e0376"
    ),
    "required_gate_adoption_contract.json": (
        "f956fc2bf5e49ef677bf7ae1ff6149bdb1ba861ad7bd9b515dd865a36dbfeac4"
    ),
    "required_gate_adoption_contract.md": (
        "6b85522e1596dde7c864a6a642e6d2f996c93c7fb95654c4fc158ce3cd447827"
    ),
    "required_gate_candidate.json": CANDIDATE_MANIFEST_SHA256,
    "required_gate_patch.json": CANDIDATE_PATCH_SHA256,
    "stale_disposition_consumption_guard_report.json": (
        "d8ec53ca8e6c3fcd6d5c02a258d8e0bd97dad736e00dbb8ef60b6833879c59a8"
    ),
}


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=official.REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise base.FoundationContractError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result


def _head_tree() -> str:
    return _git("rev-parse", "HEAD^{tree}").stdout.strip()


def _sealed_record(path: Path, expected_sha256: str) -> dict[str, Any]:
    record = official._sealed_text_record(path, expected_sha256)
    if record.get("match") is not True:
        raise base.FoundationContractError(
            f"sealed record mismatch: {base.repo_relative(path)}"
        )
    return {
        "path": base.repo_relative(path),
        "sha256": expected_sha256,
        "head_git_blob_id": record["head_git_blob_id"],
        "tracked": True,
        "ignored": False,
        "working_identity": True,
    }


def _tracked_head_record(path: Path) -> dict[str, Any]:
    if not official._tracked_not_ignored(path):
        raise base.FoundationContractError(
            f"required closure artifact is not tracked and clean: "
            f"{base.repo_relative(path)}"
        )
    relative = base.repo_relative(path)
    blob_id = _git("rev-parse", f"HEAD:{relative}").stdout.strip()
    blob = subprocess.run(
        ["git", "cat-file", "blob", blob_id],
        cwd=official.REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if blob.returncode != 0:
        raise base.FoundationContractError(
            f"cannot read HEAD blob for {relative}"
        )
    filtered = _git("hash-object", "--", relative).stdout.strip()
    if filtered != blob_id:
        raise base.FoundationContractError(
            f"working identity differs from HEAD for {relative}"
        )
    return {
        "path": relative,
        "sha256": base.sha256_bytes(blob.stdout),
        "git_blob_id": blob_id,
        "tracked": True,
        "ignored": False,
        "working_identity": True,
    }


def _sealed_head_git_record(
    path: Path,
    expected_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    relative = base.repo_relative(path)
    tracked = _git(
        "ls-files",
        "--error-unmatch",
        "--",
        relative,
        check=False,
    ).returncode == 0
    ignored = _git(
        "check-ignore",
        "-q",
        "--",
        relative,
        check=False,
    ).returncode == 0
    unstaged = _git(
        "diff",
        "--quiet",
        "--",
        relative,
        check=False,
    ).returncode != 0
    staged = _git(
        "diff",
        "--cached",
        "--quiet",
        "HEAD",
        "--",
        relative,
        check=False,
    ).returncode != 0
    blob_id = _git("rev-parse", f"HEAD:{relative}").stdout.strip()
    blob = subprocess.run(
        ["git", "cat-file", "blob", blob_id],
        cwd=official.REPO_ROOT,
        capture_output=True,
        check=False,
    )
    sha256 = base.sha256_bytes(blob.stdout)
    if (
        not tracked
        or ignored
        or unstaged
        or staged
        or blob.returncode != 0
        or sha256 != expected_sha256
    ):
        raise base.FoundationContractError(
            f"sealed HEAD Git artifact mismatch: {relative}"
        )
    try:
        value = json.loads(blob.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise base.FoundationContractError(
            f"sealed HEAD Git artifact is not strict UTF-8 JSON: {relative}"
        ) from exc
    return (
        {
            "path": relative,
            "sha256": sha256,
            "head_git_blob_id": blob_id,
            "tracked": True,
            "ignored": False,
            "working_identity": True,
        },
        value,
    )


def _working_record(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise base.FoundationContractError(
            f"required generated closure artifact is missing: "
            f"{base.repo_relative(path)}"
        )
    return {
        "path": base.repo_relative(path),
        "sha256": base.sha256_file(path),
    }


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _bounded_execution_environment() -> dict[str, Any]:
    declared_root = ensure_external_root(
        official.REPO_ROOT,
        (
            Path(tempfile.gettempdir()).resolve()
            / "i-g4-p6-r2"
        ),
    )
    test_output_root = (declared_root / "test-output").resolve()
    system_temp_root = (declared_root / "system-temp").resolve()
    test_output_root.mkdir(parents=True, exist_ok=True)
    system_temp_root.mkdir(parents=True, exist_ok=True)
    environment_values = {
        "IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT": str(test_output_root),
        "TEMP": str(system_temp_root),
        "TMP": str(system_temp_root),
        "TMPDIR": str(system_temp_root),
    }
    fixture_paths = [
        (test_output_root / name).resolve()
        for name in AFFECTED_FIXTURE_NAMES
    ]
    if (
        _is_within(declared_root, official.REPO_ROOT)
        or _is_within(official.REPO_ROOT, declared_root)
        or any(
            not _is_within(Path(value), declared_root)
            for value in environment_values.values()
        )
        or any(not _is_within(path, test_output_root) for path in fixture_paths)
    ):
        raise base.FoundationContractError(
            "bounded repository-external execution root containment failed"
        )
    environment = os.environ.copy()
    environment.pop("PYTHONHOME", None)
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTEST_ADDOPTS", None)
    environment.update(
        {
            "GIT_OPTIONAL_LOCKS": "0",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_NO_INDEX": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "PYTHONNOUSERSITE": "1",
            "PYTHONPYCACHEPREFIX": str(system_temp_root / "pycache"),
            **environment_values,
        }
    )
    return {
        "declared_external_root": declared_root,
        "test_output_root": test_output_root,
        "system_temp_root": system_temp_root,
        "environment": environment,
        "environment_values": environment_values,
        "fixture_paths": fixture_paths,
    }


def _run_command(
    argv: list[str],
    *,
    environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=official.REPO_ROOT,
        env=environment,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def _affected_test_result(
    completed: subprocess.CompletedProcess[str],
) -> dict[str, Any]:
    combined = f"{completed.stdout}\n{completed.stderr}"
    match = re.search(r"Ran\s+(\d+)\s+tests?", combined)
    observed_count = int(match.group(1)) if match else 0
    passed = completed.returncode == 0 and observed_count == len(
        AFFECTED_TEST_IDS
    )
    return {
        "schema_version": (
            "public_text_quality_phase6_affected_test_result_v1"
        ),
        "status": "PASS" if passed else "FAIL",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "required_test_count": len(AFFECTED_TEST_IDS),
        "executed_test_count": observed_count,
        "passed_test_count": len(AFFECTED_TEST_IDS) if passed else 0,
        "failed_test_count": 0 if passed else len(AFFECTED_TEST_IDS),
        "test_ids": list(AFFECTED_TEST_IDS),
        "exit_code": completed.returncode,
        "stdout_sha256": base.sha256_bytes(completed.stdout.encode("utf-8")),
        "stderr_sha256": base.sha256_bytes(completed.stderr.encode("utf-8")),
    }


def _execution_row(
    *,
    role: str,
    argv: list[str],
    result_path: Path,
    exit_code: int,
    selected_count: int,
    passed_count: int,
) -> dict[str, Any]:
    return {
        "role": role,
        "argv": argv,
        "cwd": str(official.REPO_ROOT),
        "result_path": base.repo_relative(result_path),
        "result_sha256": base.sha256_file(result_path),
        "exit_code": exit_code,
        "selected_test_count": selected_count,
        "passed_test_count": passed_count,
    }


def _write_execution_receipt(
    *,
    receipt_path: Path,
    environment_contract: dict[str, Any],
    executions: list[dict[str, Any]],
    status: str,
    execution_role: str,
) -> dict[str, Any]:
    receipt_core = {
        "schema_version": (
            "public_text_quality_phase6_bounded_execution_environment_receipt_v1"
        ),
        "status": status,
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "execution_role": execution_role,
        "execution_commit": base.git_head(),
        "execution_tree": _head_tree(),
        "declared_external_root": str(
            environment_contract["declared_external_root"]
        ),
        "repository_root": str(official.REPO_ROOT),
        "repository_external": True,
        "g1_execution_isolation_contract_reused": True,
        "g1_external_root_validator": (
            "Iris.validation.execution."
            "checkout_environment.ensure_external_root"
        ),
        "environment_variable_names": list(
            EXECUTION_ENVIRONMENT_VARIABLE_NAMES
        ),
        "environment_values": environment_contract["environment_values"],
        "fixture_path_count": len(environment_contract["fixture_paths"]),
        "fixture_paths": [
            str(path) for path in environment_contract["fixture_paths"]
        ],
        "all_environment_paths_within_declared_root": True,
        "all_fixture_paths_within_declared_test_output_root": True,
        "rtc_containment_rules_modified": False,
        "validator_bypass_used": False,
        "test_specific_path_exception_used": False,
        "execution_count": len(executions),
        "executions": executions,
        "authority_effect": "none",
    }
    receipt = {
        **receipt_core,
        "receipt_hash": base.canonical_hash(receipt_core),
    }
    base.write_once_or_same(receipt_path, receipt)
    return receipt


def _candidate_route_argv(result_path: Path) -> list[str]:
    return [
        sys.executable,
        "-B",
        "Iris/_docs/round3/round3_run_contract_tests.py",
        "--class",
        "current",
        "--required-validations",
        base.repo_relative(PHASE6 / "required_gate_candidate.json"),
        "--enforce-current-build-closure",
        "--out",
        base.repo_relative(result_path),
    ]


def _post_adoption_route_argv(result_path: Path) -> list[str]:
    return [
        sys.executable,
        "-B",
        "Iris/_docs/round3/round3_run_contract_tests.py",
        "--class",
        "current",
        "--required-validations",
        base.repo_relative(base.LIVE_REQUIRED_VALIDATIONS),
        "--enforce-current-build-closure",
        "--out",
        base.repo_relative(result_path),
    ]


def run_bounded_phase6_revalidation() -> dict[str, Any]:
    if EXECUTION_ENVIRONMENT_RECEIPT.is_file():
        return validate_execution_environment_receipt(
            require_tracked=False,
            receipt_path=EXECUTION_ENVIRONMENT_RECEIPT,
            result_path=CORRECTION_ROUTE_RESULT,
            require_affected=True,
        )
    contract = _bounded_execution_environment()
    affected_argv = [
        sys.executable,
        "-B",
        (
            "Iris/build/description/v2/tests/"
            "test_lua_bridge_export_contract_realign.py"
        ),
        *[
            test_id.split("test_lua_bridge_export_contract_realign.", 1)[1]
            for test_id in AFFECTED_TEST_IDS
        ],
    ]
    affected_completed = _run_command(
        affected_argv,
        environment=contract["environment"],
    )
    affected = _affected_test_result(affected_completed)
    base.write_once_or_same(AFFECTED_TEST_RESULT, affected)
    executions = [
        _execution_row(
            role="affected_four_tests",
            argv=affected_argv,
            result_path=AFFECTED_TEST_RESULT,
            exit_code=affected_completed.returncode,
            selected_count=len(AFFECTED_TEST_IDS),
            passed_count=affected["passed_test_count"],
        )
    ]
    if affected["status"] != "PASS":
        _write_execution_receipt(
            receipt_path=EXECUTION_ENVIRONMENT_RECEIPT,
            environment_contract=contract,
            executions=executions,
            status="FAIL",
            execution_role="pre_adoption_candidate_revalidation",
        )
        raise base.FoundationContractError(
            "affected four tests failed under the bounded environment"
        )
    route_argv = _candidate_route_argv(CORRECTION_ROUTE_RESULT)
    route_completed = _run_command(
        route_argv,
        environment=contract["environment"],
    )
    if not CORRECTION_ROUTE_RESULT.is_file():
        raise base.FoundationContractError(
            "candidate current-route result was not materialized"
        )
    route_value = base.load_json_strict(CORRECTION_ROUTE_RESULT)
    passed_count = (
        route_value.get("test_count", 0)
        - len(route_value.get("failures", []))
        - len(route_value.get("errors", []))
        - len(route_value.get("skipped", []))
    )
    executions.append(
        _execution_row(
            role="candidate_current_route_136",
            argv=route_argv,
            result_path=CORRECTION_ROUTE_RESULT,
            exit_code=route_completed.returncode,
            selected_count=route_value.get("selected_identity_count", 0),
            passed_count=passed_count,
        )
    )
    receipt_status = (
        "PASS"
        if route_completed.returncode == 0
        and route_value.get("success") is True
        else "FAIL"
    )
    _write_execution_receipt(
        receipt_path=EXECUTION_ENVIRONMENT_RECEIPT,
        environment_contract=contract,
        executions=executions,
        status=receipt_status,
        execution_role="pre_adoption_candidate_revalidation",
    )
    if receipt_status != "PASS":
        raise base.FoundationContractError(
            "full candidate current route failed under bounded environment"
        )
    return validate_execution_environment_receipt(
        require_tracked=False,
        receipt_path=EXECUTION_ENVIRONMENT_RECEIPT,
        result_path=CORRECTION_ROUTE_RESULT,
        require_affected=True,
    )


def run_bounded_post_adoption_route() -> dict[str, Any]:
    if POST_ADOPTION_EXECUTION_RECEIPT.is_file():
        return validate_execution_environment_receipt(
            require_tracked=False,
            receipt_path=POST_ADOPTION_EXECUTION_RECEIPT,
            result_path=POST_ADOPTION_ROUTE_RESULT,
            require_affected=False,
        )
    contract = _bounded_execution_environment()
    argv = _post_adoption_route_argv(POST_ADOPTION_ROUTE_RESULT)
    completed = _run_command(argv, environment=contract["environment"])
    if not POST_ADOPTION_ROUTE_RESULT.is_file():
        raise base.FoundationContractError(
            "post-adoption current-route result was not materialized"
        )
    value = base.load_json_strict(POST_ADOPTION_ROUTE_RESULT)
    passed_count = (
        value.get("test_count", 0)
        - len(value.get("failures", []))
        - len(value.get("errors", []))
        - len(value.get("skipped", []))
    )
    executions = [
        _execution_row(
            role="post_adoption_current_route_136",
            argv=argv,
            result_path=POST_ADOPTION_ROUTE_RESULT,
            exit_code=completed.returncode,
            selected_count=value.get("selected_identity_count", 0),
            passed_count=passed_count,
        )
    ]
    status = (
        "PASS"
        if completed.returncode == 0 and value.get("success") is True
        else "FAIL"
    )
    _write_execution_receipt(
        receipt_path=POST_ADOPTION_EXECUTION_RECEIPT,
        environment_contract=contract,
        executions=executions,
        status=status,
        execution_role="post_adoption_live_route",
    )
    if status != "PASS":
        raise base.FoundationContractError(
            "post-adoption current route failed under bounded environment"
        )
    return validate_execution_environment_receipt(
        require_tracked=False,
        receipt_path=POST_ADOPTION_EXECUTION_RECEIPT,
        result_path=POST_ADOPTION_ROUTE_RESULT,
        require_affected=False,
    )


def _validate_g1_successor_0008() -> dict[str, Any]:
    gate_record = _sealed_record(
        G1_GATE_MANIFEST,
        G1_GATE_MANIFEST_SHA256,
    )
    closeout_record = _sealed_record(G1_CLOSEOUT, G1_CLOSEOUT_SHA256)
    gate = base.load_json_strict(G1_GATE_MANIFEST)
    closeout = base.load_json_strict(G1_CLOSEOUT)
    gate_projection = gate.get("current_route_projection", {})
    execution = gate.get("execution_reproducibility", {})
    if (
        gate.get("status") != "PASS"
        or gate.get("validated_subject", {}).get("commit")
        != G1_VALIDATED_SUBJECT_COMMIT
        or gate.get("validated_subject", {}).get("tree")
        != G1_VALIDATED_SUBJECT_TREE
        or gate_projection.get("final_g4_candidate", {}).get("status")
        != "PASS"
        or gate_projection.get("final_g4_candidate", {}).get("test_count")
        != 136
        or gate_projection.get("final_g4_candidate", {}).get(
            "required_test_count"
        )
        != 57
        or gate_projection.get("final_g4_candidate", {}).get(
            "required_artifact_count"
        )
        != 159
        or gate_projection.get("final_g4_candidate", {}).get("result_sha256")
        != G1_CANDIDATE_ROUTE_RESULT_SHA256
        or execution.get("run_a", {}).get("status") != "PASS"
        or execution.get("run_b", {}).get("status") != "PASS"
        or execution.get("run_a", {}).get("required_execution_unit_count")
        != 199
        or execution.get("run_b", {}).get("required_execution_unit_count")
        != 199
        or execution.get("canonical_results_equal") is not True
        or execution.get("canonical_result_sha256")
        != G1_CANONICAL_RESULT_SHA256
        or gate.get("preservation", {}).get(
            "g4_attempt_0005_phase6_failure_evidence_changed"
        )
        is not False
        or closeout.get("status") != "complete"
        or closeout.get("gate_manifest_successor", {}).get(
            "git_blob_raw_sha256"
        )
        != G1_GATE_MANIFEST_SHA256
        or closeout.get("validated_subject", {}).get("commit")
        != G1_VALIDATED_SUBJECT_COMMIT
        or closeout.get("validated_subject", {}).get("tree")
        != G1_VALIDATED_SUBJECT_TREE
        or closeout.get("current_route_closeout", {}).get(
            "g4_candidate_status"
        )
        != "PASS"
        or closeout.get("current_route_closeout", {}).get(
            "g4_candidate_test_count"
        )
        != 136
        or closeout.get("execution_closeout", {}).get(
            "required_execution_unit_count"
        )
        != 199
        or closeout.get("scope_closeout", {}).get(
            "protected_or_live_mutation_count"
        )
        != 0
    ):
        raise base.FoundationContractError(
            "G1 successor 0008 exact binding is stale"
        )
    return {
        "status": "PASS",
        "gate_manifest": gate_record,
        "closeout": closeout_record,
        "validated_subject_commit": G1_VALIDATED_SUBJECT_COMMIT,
        "validated_subject_tree": G1_VALIDATED_SUBJECT_TREE,
        "run_a": "199/199 PASS",
        "run_b": "199/199 PASS",
        "canonical_result_sha256": G1_CANONICAL_RESULT_SHA256,
        "candidate_current_route": "136/136 PASS",
        "candidate_current_route_result_sha256": (
            G1_CANDIDATE_ROUTE_RESULT_SHA256
        ),
    }


def _validate_disposition_immutable() -> dict[str, Any]:
    path = official.ATTEMPT_ROOT / "phase5" / "evaluation_subject_disposition.json"
    value = base.load_json_strict(path)
    core = {key: child for key, child in value.items() if key != "disposition_hash"}
    if (
        value.get("disposition_hash") != base.canonical_hash(core)
        or value.get("disposition_hash") != DISPOSITION_SHA256
        or value.get("qualified_disposition") != "accepted"
        or value.get("effective_blocking_finding_count") != 0
        or value.get("advisory_debt_count") != 0
        or value.get("technical_blocker_count") != 0
        or value.get("active_waiver_count") != 0
        or value.get("policy_raw_sha256") != POLICY_SHA256
        or value.get("evaluation_subject_hash") != official.CANDIDATE_SHA256
        or value.get("naturalization_handoff_hash")
        != official.PHASE8_HANDOFF_SHA256
    ):
        raise base.FoundationContractError(
            "immutable Phase 5 accepted disposition is stale"
        )
    return {
        "path": base.repo_relative(path),
        "sha256": base.sha256_file(path),
        "disposition_hash": DISPOSITION_SHA256,
        "qualified_disposition": "accepted",
        "blocking_finding_count": 0,
        "advisory_finding_count": 0,
        "technical_finding_count": 0,
        "active_waiver_count": 0,
    }


def _validate_predecessor_failure() -> dict[str, Any]:
    rows = []
    for name, expected_sha in PREDECESSOR_PHASE6_HASHES.items():
        rows.append(_sealed_record(PHASE6 / name, expected_sha))
    predecessor_tree = _git(
        "rev-parse",
        (
            f"{PREDECESSOR_FAILURE_COMMIT}:./"
            f"{base.repo_relative(PHASE6)}"
        ),
    ).stdout.strip()
    if predecessor_tree != PREDECESSOR_PHASE6_TREE:
        raise base.FoundationContractError(
            "predecessor Phase 6 failure tree mismatch"
        )
    phase0_5_diff = _git(
        "diff",
        "--name-only",
        f"{PREDECESSOR_FAILURE_COMMIT}..HEAD",
        "--",
        *[
            base.repo_relative(official.ATTEMPT_ROOT / f"phase{phase}")
            for phase in range(6)
        ],
    ).stdout.strip()
    if phase0_5_diff:
        raise base.FoundationContractError(
            "attempt-0005 Phase 0-5 immutable evidence changed"
        )
    correction_route, _correction_route_value = _sealed_head_git_record(
        PREDECESSOR_CORRECTION_ROUTE_RESULT,
        PREDECESSOR_CORRECTION_ROUTE_RESULT_SHA256,
    )
    correction_failure, correction_failure_value = _sealed_head_git_record(
        PREDECESSOR_CORRECTION_FAILURE_RECORD,
        PREDECESSOR_CORRECTION_FAILURE_RECORD_SHA256,
    )
    if (
        correction_failure_value.get("status") != "FAIL_CLOSED"
        or correction_failure_value.get("correction_id")
        != PREDECESSOR_CORRECTION_ID
        or correction_failure_value.get("fresh_current_route", {}).get(
            "passed_test_count"
        )
        != 132
        or correction_failure_value.get("fresh_current_route", {}).get(
            "error_count"
        )
        != 4
        or correction_failure_value.get("fail_close", {}).get(
            "live_adoption_performed"
        )
        is not False
    ):
        raise base.FoundationContractError(
            "correction-0001 failure evidence is stale"
        )
    return {
        "status": "PASS",
        "failure_commit": PREDECESSOR_FAILURE_COMMIT,
        "phase6_tree": PREDECESSOR_PHASE6_TREE,
        "direct_artifact_count": len(rows),
        "direct_artifacts": rows,
        "phase0_through_phase5_changed_path_count": 0,
        "failed_route_result_sha256": FAILED_ROUTE_RESULT_SHA256,
        "failed_route_preserved": True,
        "correction_0001_route_result": correction_route,
        "correction_0001_failure_record": correction_failure,
        "correction_0001_failure_preserved": True,
    }


def _validate_protected_inputs() -> dict[str, Any]:
    expected = (
        (official.FOUNDATION_CONTRACT, official.FOUNDATION_CONTRACT_SHA256),
        (official.G4_READINESS, official.G4_READINESS_SHA256),
        (official.CURRENT_FACTS, official.CURRENT_FACTS_SHA256),
        (official.CURRENT_MANIFEST, official.CURRENT_MANIFEST_SHA256),
        (official.PHASE8_HANDOFF, official.PHASE8_HANDOFF_SHA256),
        (official.PHASE8_CLOSEOUT, official.PHASE8_CLOSEOUT_SHA256),
        (official.TERMINAL_CLOSEOUT, official.TERMINAL_CLOSEOUT_SHA256),
        (official.CANDIDATE, official.CANDIDATE_SHA256),
        (official.TRACE, official.TRACE_SHA256),
    )
    rows = [_sealed_record(path, sha256) for path, sha256 in expected]
    return {
        "status": "PASS",
        "required_count": len(rows),
        "fresh_count": len(rows),
        "rows": rows,
        "facts_manifest_foundation_candidate_handoff_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "g6_discovery_mutation_count": 0,
    }


def _scope_diff_audit() -> dict[str, Any]:
    changed = [
        row
        for row in _git(
            "diff",
            "--name-only",
            f"{TASK_START_COMMIT}..HEAD",
        ).stdout.splitlines()
        if row
    ]
    exact_allowed = {
        ".gitignore",
        base.repo_relative(base.LIVE_REQUIRED_VALIDATIONS),
        base.repo_relative(official.THIS_MODULE),
        base.repo_relative(official.RUNNER_MODULE),
        base.repo_relative(official.VALIDATOR_MODULE),
        base.repo_relative(Path(__file__).resolve()),
        base.repo_relative(CLOSEOUT_DOC),
    }
    allowed_prefixes = (
        f"{base.repo_relative(official.OWNER_INPUT_ROOT)}/",
        f"{base.repo_relative(REVIEWER_INPUT_ROOT)}/",
        f"{base.repo_relative(PHASE6)}/corrections/",
        f"{base.repo_relative(PHASE7)}/",
    )
    exact_phase6_allowed = {
        base.repo_relative(ADOPTION_DECISION_RECORD),
        base.repo_relative(ADOPTION_RECEIPT),
        base.repo_relative(POST_ADOPTION_ROUTE_RESULT),
        base.repo_relative(POST_ADOPTION_EXECUTION_RECEIPT),
    }
    unexpected = [
        path
        for path in changed
        if path not in exact_allowed
        and path not in exact_phase6_allowed
        and not path.startswith(allowed_prefixes)
    ]
    if unexpected:
        raise base.FoundationContractError(
            f"task-scope protected path mutation detected: {unexpected}"
        )
    return {
        "status": "PASS",
        "task_start_commit": TASK_START_COMMIT,
        "task_start_tree": TASK_START_TREE,
        "changed_path_count": len(changed),
        "changed_paths": changed,
        "unexpected_changed_path_count": 0,
        "unexpected_changed_paths": [],
        "g5_candidate_trace_handoff_mutation_count": 0,
        "g6_discovery_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "phase0_through_phase5_mutation_count": 0,
    }


def _validate_route_result(path: Path) -> dict[str, Any]:
    value = base.load_json_strict(path)
    required = value.get("required_validations", {})
    if (
        value.get("schema_version") != "round3-contract-test-run-v1"
        or value.get("contract_class") != "current"
        or value.get("closure_enforced") is not True
        or value.get("selected_identity_count") != 136
        or value.get("test_count") != 136
        or value.get("success") is not True
        or value.get("failures") != []
        or value.get("errors") != []
        or value.get("skipped") != []
        or required.get("success") is not True
        or required.get("errors") != []
        or required.get("required_test_count") != 57
        or required.get("required_artifact_count") != 159
    ):
        raise base.FoundationContractError(
            f"current-route result is not exact 136/136 PASS: "
            f"{base.repo_relative(path)}"
        )
    return {
        "path": base.repo_relative(path),
        "sha256": base.sha256_file(path),
        "selected_identity_count": 136,
        "test_count": 136,
        "passed_count": 136,
        "failure_count": 0,
        "error_count": 0,
        "skipped_count": 0,
        "required_test_count": 57,
        "required_artifact_count": 159,
        "status": "PASS",
    }


def _validate_long_root_failure() -> dict[str, Any]:
    receipt_ref = _sealed_record(
        LONG_ROOT_FAILURE_EXECUTION_ENVIRONMENT_RECEIPT,
        LONG_ROOT_FAILURE_EXECUTION_ENVIRONMENT_RECEIPT_SHA256,
    )
    affected_ref = _sealed_record(
        LONG_ROOT_FAILURE_AFFECTED_TEST_RESULT,
        LONG_ROOT_FAILURE_AFFECTED_TEST_RESULT_SHA256,
    )
    route_ref = _sealed_record(
        LONG_ROOT_FAILURE_ROUTE_RESULT,
        LONG_ROOT_FAILURE_ROUTE_RESULT_SHA256,
    )
    receipt = base.load_json_strict(
        LONG_ROOT_FAILURE_EXECUTION_ENVIRONMENT_RECEIPT
    )
    affected = base.load_json_strict(LONG_ROOT_FAILURE_AFFECTED_TEST_RESULT)
    route = base.load_json_strict(LONG_ROOT_FAILURE_ROUTE_RESULT)
    core = {
        key: value
        for key, value in receipt.items()
        if key != "receipt_hash"
    }
    if (
        receipt.get("receipt_hash") != base.canonical_hash(core)
        or receipt.get("status") != "FAIL"
        or receipt.get("correction_id") != CORRECTION_ID
        or receipt.get("execution_count") != 2
        or receipt.get("executions", [])[0].get("passed_test_count") != 4
        or receipt.get("executions", [])[1].get("exit_code") != 1
        or affected.get("status") != "PASS"
        or affected.get("passed_test_count") != 4
        or route.get("selected_identity_count") != 136
        or route.get("test_count") != 121
        or route.get("success") is not False
        or len(route.get("errors", [])) != 4
        or route.get("failures") != []
        or receipt.get("authority_effect") != "none"
    ):
        raise base.FoundationContractError(
            "correction-0002 long-root failure evidence is stale"
        )
    return {
        "status": "FAIL_CLOSED_PRESERVED",
        "failure_class": "windows_external_root_path_length",
        "execution_environment_receipt": receipt_ref,
        "affected_test_result": affected_ref,
        "candidate_current_route_result": route_ref,
        "affected_test_count": 4,
        "affected_passed_count": 4,
        "selected_current_route_count": 136,
        "executed_current_route_count": 121,
        "current_route_error_count": 4,
        "live_adoption_performed": False,
        "phase7_executed": False,
        "authority_effect": "none",
        "preserved": True,
    }


def _validate_long_path_partial_revalidation() -> dict[str, Any]:
    record_ref = _sealed_record(
        LONG_PATH_PARTIAL_REVALIDATION_RECORD,
        LONG_PATH_PARTIAL_REVALIDATION_RECORD_SHA256,
    )
    value = base.load_json_strict(LONG_PATH_PARTIAL_REVALIDATION_RECORD)
    core = {
        key: child
        for key, child in value.items()
        if key != "record_hash"
    }
    if (
        value.get("record_hash") != base.canonical_hash(core)
        or value.get("status") != "PASS"
        or value.get("correction_id") != CORRECTION_ID
        or value.get("phase6_blocker_count") != 0
        or value.get("disposition_maintained") is not True
        or value.get("live_manifest_mutated") is not False
        or value.get("authority_effect") != "none"
    ):
        raise base.FoundationContractError(
            "correction-0002 long-path partial revalidation is stale"
        )
    return {
        "status": "PASS_RECORD_PRESERVED_WITHOUT_CONTRACT",
        "failure_class": "windows_evidence_path_length",
        "record": record_ref,
        "adoption_contract_materialized": False,
        "live_adoption_performed": False,
        "phase7_executed": False,
        "authority_effect": "none",
        "preserved": True,
    }


def validate_execution_environment_receipt(
    *,
    require_tracked: bool,
    receipt_path: Path,
    result_path: Path,
    require_affected: bool,
) -> dict[str, Any]:
    receipt = base.load_json_strict(receipt_path)
    core = {
        key: value
        for key, value in receipt.items()
        if key != "receipt_hash"
    }
    declared_root = Path(receipt.get("declared_external_root", "")).resolve()
    environment_values = receipt.get("environment_values", {})
    fixture_paths = [
        Path(path).resolve() for path in receipt.get("fixture_paths", [])
    ]
    test_output_root = Path(
        environment_values.get(
            "IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT",
            "",
        )
    ).resolve()
    execution_commit = str(receipt.get("execution_commit", ""))
    execution_tree = str(receipt.get("execution_tree", ""))
    resolved_commit = _git(
        "rev-parse",
        "--verify",
        f"{execution_commit}^{{commit}}",
    ).stdout.strip()
    resolved_tree = _git(
        "rev-parse",
        f"{resolved_commit}^{{tree}}",
    ).stdout.strip()
    ancestor = _git(
        "merge-base",
        "--is-ancestor",
        resolved_commit,
        "HEAD",
        check=False,
    ).returncode == 0
    expected_fixture_paths = [
        (test_output_root / name).resolve()
        for name in AFFECTED_FIXTURE_NAMES
    ]
    executions = receipt.get("executions", [])
    expected_roles = (
        ["affected_four_tests", "candidate_current_route_136"]
        if require_affected
        else ["post_adoption_current_route_136"]
    )
    if (
        receipt.get("schema_version")
        != "public_text_quality_phase6_bounded_execution_environment_receipt_v1"
        or receipt.get("status") != "PASS"
        or receipt.get("attempt_id") != official.ATTEMPT_ID
        or receipt.get("correction_id") != CORRECTION_ID
        or receipt.get("receipt_hash") != base.canonical_hash(core)
        or receipt.get("repository_external") is not True
        or receipt.get("g1_execution_isolation_contract_reused") is not True
        or receipt.get("environment_variable_names")
        != list(EXECUTION_ENVIRONMENT_VARIABLE_NAMES)
        or sorted(environment_values)
        != sorted(EXECUTION_ENVIRONMENT_VARIABLE_NAMES)
        or _is_within(declared_root, official.REPO_ROOT)
        or _is_within(official.REPO_ROOT, declared_root)
        or any(
            not _is_within(Path(value), declared_root)
            for value in environment_values.values()
        )
        or fixture_paths != expected_fixture_paths
        or any(not _is_within(path, test_output_root) for path in fixture_paths)
        or receipt.get("all_environment_paths_within_declared_root") is not True
        or receipt.get("all_fixture_paths_within_declared_test_output_root")
        is not True
        or receipt.get("rtc_containment_rules_modified") is not False
        or receipt.get("validator_bypass_used") is not False
        or receipt.get("test_specific_path_exception_used") is not False
        or resolved_commit != execution_commit
        or resolved_tree != execution_tree
        or not ancestor
        or receipt.get("execution_count") != len(expected_roles)
        or [row.get("role") for row in executions] != expected_roles
        or any(row.get("exit_code") != 0 for row in executions)
        or any(
            base.sha256_file(official.REPO_ROOT / row["result_path"])
            != row.get("result_sha256")
            for row in executions
        )
        or executions[-1].get("result_path") != base.repo_relative(result_path)
        or executions[-1].get("selected_test_count") != 136
        or executions[-1].get("passed_test_count") != 136
        or receipt.get("authority_effect") != "none"
    ):
        raise base.FoundationContractError(
            "bounded execution-environment receipt is stale"
        )
    result = _validate_route_result(result_path)
    if require_affected:
        affected = base.load_json_strict(AFFECTED_TEST_RESULT)
        if (
            affected.get("status") != "PASS"
            or affected.get("required_test_count") != 4
            or affected.get("executed_test_count") != 4
            or affected.get("passed_test_count") != 4
            or affected.get("failed_test_count") != 0
            or affected.get("exit_code") != 0
            or affected.get("test_ids") != list(AFFECTED_TEST_IDS)
            or executions[0].get("result_path")
            != base.repo_relative(AFFECTED_TEST_RESULT)
            or executions[0].get("selected_test_count") != 4
            or executions[0].get("passed_test_count") != 4
        ):
            raise base.FoundationContractError(
                "affected-test bounded execution result is stale"
            )
    if require_tracked:
        receipt_ref = _tracked_head_record(receipt_path)
        result_ref = _tracked_head_record(result_path)
        affected_ref = (
            _tracked_head_record(AFFECTED_TEST_RESULT)
            if require_affected
            else None
        )
    else:
        receipt_ref = _working_record(receipt_path)
        result_ref = _working_record(result_path)
        affected_ref = (
            _working_record(AFFECTED_TEST_RESULT)
            if require_affected
            else None
        )
    return {
        "status": "PASS",
        "receipt": receipt_ref,
        "result": result_ref,
        "affected_result": affected_ref,
        "declared_external_root": str(declared_root),
        "repository_external": True,
        "execution_commit": execution_commit,
        "execution_tree": execution_tree,
        "environment_variable_names": list(
            EXECUTION_ENVIRONMENT_VARIABLE_NAMES
        ),
        "affected_test_count": 4 if require_affected else 0,
        "current_route_test_count": result["test_count"],
        "current_route_passed_count": result["passed_count"],
        "authority_effect": "none",
    }


def _validate_candidate_against_live() -> dict[str, Any]:
    live_record = official._live_manifest_record()
    if live_record["sha256"] != LIVE_BASE_SHA256:
        raise base.FoundationContractError(
            "live-manifest CAS base is not exact"
        )
    candidate_path = PHASE6 / "required_gate_candidate.json"
    patch_path = PHASE6 / "required_gate_patch.json"
    if (
        base.sha256_file(candidate_path) != CANDIDATE_MANIFEST_SHA256
        or base.sha256_file(patch_path) != CANDIDATE_PATCH_SHA256
    ):
        raise base.FoundationContractError(
            "immutable Phase 6 candidate or patch changed"
        )
    live = base.load_json_strict(base.LIVE_REQUIRED_VALIDATIONS)
    candidate = base.load_json_strict(candidate_path)
    patch = base.load_json_strict(patch_path)
    if (
        candidate["required_artifacts"]
        != [
            *live["required_artifacts"],
            *patch["added_required_artifacts"],
        ]
        or candidate["required_tests"]
        != [*live["required_tests"], *patch["added_required_tests"]]
        or patch.get("base_manifest_sha256") != LIVE_BASE_SHA256
        or patch.get("candidate_manifest_sha256")
        != CANDIDATE_MANIFEST_SHA256
        or patch.get("removed_required_artifact_count") != 0
        or patch.get("modified_required_artifact_count") != 0
        or patch.get("removed_required_test_count") != 0
        or patch.get("modified_required_test_count") != 0
        or patch.get("existing_entry_reorder_count") != 0
    ):
        raise base.FoundationContractError(
            "Phase 6 candidate is not exact additive-only CAS successor"
        )
    live_other = {
        key: value
        for key, value in live.items()
        if key not in ("required_artifacts", "required_tests")
    }
    candidate_other = {
        key: value
        for key, value in candidate.items()
        if key not in ("required_artifacts", "required_tests")
    }
    if live_other != candidate_other:
        raise base.FoundationContractError(
            "Phase 6 candidate changed non-additive live fields"
        )
    protected = base.load_json_strict(
        PHASE6 / "pre_adoption_protected_surface_report.json"
    )
    if (
        protected.get("status") != "PASS"
        or protected.get("live_manifest_mutation_count") != 0
        or protected.get(
            "facts_manifest_foundation_candidate_mutation_count"
        )
        != 0
        or protected.get("runtime_lua_package_mutation_count") != 0
        or protected.get("authority_effect") != "none"
    ):
        raise base.FoundationContractError(
            "pre-adoption protected-surface evidence is stale"
        )
    return {
        "candidate_manifest_path": base.repo_relative(candidate_path),
        "candidate_manifest_sha256": CANDIDATE_MANIFEST_SHA256,
        "candidate_patch_path": base.repo_relative(patch_path),
        "candidate_patch_sha256": CANDIDATE_PATCH_SHA256,
        "live_manifest_path": base.repo_relative(
            base.LIVE_REQUIRED_VALIDATIONS
        ),
        "live_manifest_base_sha256": LIVE_BASE_SHA256,
        "required_artifact_addition_count": len(
            patch["added_required_artifacts"]
        ),
        "required_test_addition_count": len(
            patch["added_required_tests"]
        ),
        "additive_only": True,
        "cas_fresh": True,
        "protected_surface_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }


def build_phase6_revalidation() -> dict[str, Any]:
    execution = run_bounded_phase6_revalidation()
    long_root_failure = _validate_long_root_failure()
    long_path_partial = _validate_long_path_partial_revalidation()
    g1 = _validate_g1_successor_0008()
    predecessor = _validate_predecessor_failure()
    protected_inputs = _validate_protected_inputs()
    disposition = _validate_disposition_immutable()
    candidate = _validate_candidate_against_live()
    route = _validate_route_result(CORRECTION_ROUTE_RESULT)
    core = {
        "schema_version": (
            "public_text_quality_phase6_g1_successor_revalidation_v1"
        ),
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "record_mode": "append_only_failed_phase6_correction_revalidation",
        "validation_commit": base.git_head(),
        "validation_tree": _head_tree(),
        "g1_successor_0008": g1,
        "predecessor_failure": predecessor,
        "protected_inputs": protected_inputs,
        "immutable_phase5_disposition": disposition,
        "candidate_and_cas": candidate,
        "long_root_execution_failure_preservation": long_root_failure,
        "long_path_partial_revalidation_preservation": long_path_partial,
        "bounded_execution_environment": execution,
        "fresh_candidate_current_route": route,
        "phase6_blocker_count": 0,
        "disposition_maintained": True,
        "live_adoption_allowed": True,
        "live_manifest_mutated": False,
        "protected_surface_mutation_count": 0,
        "authority_effect": "none",
        "phase7_allowed": False,
    }
    record = {**core, "record_hash": base.canonical_hash(core)}
    base.write_once_or_same(REVALIDATION_RECORD, record)
    contract_core = {
        "schema_version": (
            "public_text_quality_required_gate_adoption_contract_successor_v1"
        ),
        "status": "READY_FOR_CONDITIONAL_OWNER_AUTHORIZATION",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "predecessor_contract_path": base.repo_relative(
            PHASE6 / "required_gate_adoption_contract.json"
        ),
        "predecessor_contract_sha256": PREDECESSOR_PHASE6_HASHES[
            "required_gate_adoption_contract.json"
        ],
        "predecessor_mutated": False,
        "phase6_revalidation_record_path": base.repo_relative(
            REVALIDATION_RECORD
        ),
        "phase6_revalidation_record_sha256": base.sha256_file(
            REVALIDATION_RECORD
        ),
        "execution_environment_receipt_sha256": base.sha256_file(
            EXECUTION_ENVIRONMENT_RECEIPT
        ),
        "affected_test_result_sha256": base.sha256_file(AFFECTED_TEST_RESULT),
        "g1_gate_manifest_sha256": G1_GATE_MANIFEST_SHA256,
        "g1_closeout_sha256": G1_CLOSEOUT_SHA256,
        "candidate_manifest_sha256": CANDIDATE_MANIFEST_SHA256,
        "candidate_patch_sha256": CANDIDATE_PATCH_SHA256,
        "candidate_current_route_result_sha256": route["sha256"],
        "live_manifest_base_sha256": LIVE_BASE_SHA256,
        "evaluation_subject_kind": official.EVALUATION_SUBJECT_KIND,
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "evaluation_subject_disposition": "accepted",
        "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
        "naturalization_handoff_manifest_hash": (
            official.PHASE8_HANDOFF_SHA256
        ),
        "expected_post_adoption_official_route_state": "PASS",
        "expected_exit_code": 0,
        "exact_blocker_attribution": "none",
        "adoption_timing": "immediate",
        "owner_authorization": False,
        "live_manifest_mutated": False,
        "authority_effect": "none",
        "phase7_allowed": False,
        "policy_closure_state": "incomplete",
        "rollback_contract": {
            "cas_base_sha256": LIVE_BASE_SHA256,
            "rollback_target_path": base.repo_relative(
                base.LIVE_REQUIRED_VALIDATIONS
            ),
            "rollback_scope": (
                "exact_attempt_0005_additive_required_artifact_and_test_rows"
            ),
            "post_rollback_validation": "full_current_route",
        },
    }
    contract = {
        **contract_core,
        "contract_hash": base.canonical_hash(contract_core),
    }
    base.write_once_or_same(ADOPTION_CONTRACT_SUCCESSOR, contract)
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "mode": "phase6-revalidate",
        "correction_id": CORRECTION_ID,
        "revalidation_record_path": base.repo_relative(REVALIDATION_RECORD),
        "revalidation_record_sha256": base.sha256_file(REVALIDATION_RECORD),
        "adoption_contract_successor_path": base.repo_relative(
            ADOPTION_CONTRACT_SUCCESSOR
        ),
        "adoption_contract_successor_sha256": base.sha256_file(
            ADOPTION_CONTRACT_SUCCESSOR
        ),
        "current_route_test_count": 136,
        "current_route_passed_count": 136,
        "phase6_blocker_count": 0,
        "qualified_disposition": "accepted",
        "live_manifest_mutated": False,
        "protected_surface_mutation_count": 0,
        "authority_effect": "none",
    }


def validate_phase6_revalidation(*, require_tracked: bool) -> dict[str, Any]:
    execution = validate_execution_environment_receipt(
        require_tracked=require_tracked,
        receipt_path=EXECUTION_ENVIRONMENT_RECEIPT,
        result_path=CORRECTION_ROUTE_RESULT,
        require_affected=True,
    )
    long_root_failure = _validate_long_root_failure()
    long_path_partial = _validate_long_path_partial_revalidation()
    g1 = _validate_g1_successor_0008()
    predecessor = _validate_predecessor_failure()
    protected_inputs = _validate_protected_inputs()
    disposition = _validate_disposition_immutable()
    route = _validate_route_result(CORRECTION_ROUTE_RESULT)
    if require_tracked:
        record_ref = _tracked_head_record(REVALIDATION_RECORD)
        contract_ref = _tracked_head_record(ADOPTION_CONTRACT_SUCCESSOR)
        route_ref = _tracked_head_record(CORRECTION_ROUTE_RESULT)
    else:
        record_ref = {
            "path": base.repo_relative(REVALIDATION_RECORD),
            "sha256": base.sha256_file(REVALIDATION_RECORD),
        }
        contract_ref = {
            "path": base.repo_relative(ADOPTION_CONTRACT_SUCCESSOR),
            "sha256": base.sha256_file(ADOPTION_CONTRACT_SUCCESSOR),
        }
        route_ref = route
    record = base.load_json_strict(REVALIDATION_RECORD)
    record_core = {
        key: value for key, value in record.items() if key != "record_hash"
    }
    contract = base.load_json_strict(ADOPTION_CONTRACT_SUCCESSOR)
    contract_core = {
        key: value for key, value in contract.items() if key != "contract_hash"
    }
    if (
        record.get("record_hash") != base.canonical_hash(record_core)
        or record.get("status") != "PASS"
        or record.get("correction_id") != CORRECTION_ID
        or record.get("phase6_blocker_count") != 0
        or record.get("disposition_maintained") is not True
        or record.get("authority_effect") != "none"
        or record.get("bounded_execution_environment", {})
        .get("receipt", {})
        .get("sha256")
        != execution["receipt"]["sha256"]
        or record.get("bounded_execution_environment", {})
        .get("affected_result", {})
        .get("sha256")
        != execution["affected_result"]["sha256"]
        or contract.get("contract_hash") != base.canonical_hash(contract_core)
        or contract.get("status")
        != "READY_FOR_CONDITIONAL_OWNER_AUTHORIZATION"
        or contract.get("candidate_manifest_sha256")
        != CANDIDATE_MANIFEST_SHA256
        or contract.get("candidate_patch_sha256")
        != CANDIDATE_PATCH_SHA256
        or contract.get("candidate_current_route_result_sha256")
        != route["sha256"]
        or contract.get("execution_environment_receipt_sha256")
        != execution["receipt"]["sha256"]
        or contract.get("affected_test_result_sha256")
        != execution["affected_result"]["sha256"]
        or contract.get("live_manifest_base_sha256") != LIVE_BASE_SHA256
        or contract.get("evaluation_subject_disposition_hash")
        != DISPOSITION_SHA256
        or contract.get("owner_authorization") is not False
    ):
        raise base.FoundationContractError(
            "Phase 6 correction revalidation evidence is stale"
        )
    return {
        "status": "PASS",
        "g1_successor_0008": g1,
        "predecessor_failure": predecessor,
        "protected_inputs": protected_inputs,
        "disposition": disposition,
        "long_root_execution_failure_preservation": long_root_failure,
        "long_path_partial_revalidation_preservation": long_path_partial,
        "bounded_execution_environment": execution,
        "route": route_ref,
        "revalidation_record": record_ref,
        "adoption_contract_successor": contract_ref,
        "phase6_blocker_count": 0,
        "qualified_disposition": "accepted",
        "disposition_maintained": True,
        "authority_effect": "none",
    }


def _validate_owner_gate_decision() -> dict[str, Any]:
    record = _tracked_head_record(GATE_DECISION)
    value = base.load_json_strict(GATE_DECISION)
    core = {
        key: child
        for key, child in value.items()
        if key != "owner_binding_proof"
    }
    revalidation_sha = base.sha256_file(REVALIDATION_RECORD)
    route_sha = base.sha256_file(CORRECTION_ROUTE_RESULT)
    if (
        value.get("schema_version")
        != "public_text_quality_gate_adoption_decision_v2"
        or value.get("decision") != "adopt"
        or value.get("attempt_id") != official.ATTEMPT_ID
        or value.get("owner_identity")
        != "repository_owner_via_direct_codex_instruction"
        or not isinstance(value.get("authorized_at"), str)
        or value.get("candidate_manifest_sha256")
        != CANDIDATE_MANIFEST_SHA256
        or value.get("candidate_patch_sha256")
        != CANDIDATE_PATCH_SHA256
        or value.get("live_manifest_base_sha256") != LIVE_BASE_SHA256
        or value.get("phase6_revalidation_record_sha256")
        != revalidation_sha
        or value.get("candidate_current_route_result_sha256") != route_sha
        or value.get("g1_gate_manifest_sha256")
        != G1_GATE_MANIFEST_SHA256
        or value.get("g1_closeout_sha256") != G1_CLOSEOUT_SHA256
        or value.get("evaluation_subject_hash") != official.CANDIDATE_SHA256
        or value.get("evaluation_subject_disposition") != "accepted"
        or value.get("evaluation_subject_disposition_hash")
        != DISPOSITION_SHA256
        or value.get("naturalization_handoff_manifest_hash")
        != official.PHASE8_HANDOFF_SHA256
        or value.get("phase6_blocker_count") != 0
        or value.get("expected_post_adoption_official_route_state") != "PASS"
        or value.get("expected_exit_code") != 0
        or value.get("live_gate_adoption_authorized") is not True
        or value.get("phase7_authorized_after_post_adoption_pass") is not True
        or value.get("owner_binding_proof") != base.canonical_hash(core)
    ):
        raise base.FoundationContractError(
            "owner gate-adoption decision is invalid"
        )
    return {**record, "owner_binding_proof_valid": True}


def adopt_live_gate() -> dict[str, Any]:
    revalidation = validate_phase6_revalidation(require_tracked=True)
    decision = _validate_owner_gate_decision()
    live_before = official._live_manifest_record()
    if live_before["sha256"] != LIVE_BASE_SHA256:
        raise base.FoundationContractError(
            "live-manifest CAS failed before adoption"
        )
    candidate_path = PHASE6 / "required_gate_candidate.json"
    candidate_bytes = candidate_path.read_bytes()
    if base.sha256_bytes(candidate_bytes) != CANDIDATE_MANIFEST_SHA256:
        raise base.FoundationContractError(
            "candidate bytes changed before adoption"
        )
    live_bytes = base.LIVE_REQUIRED_VALIDATIONS.read_bytes()
    decision_value = base.load_json_strict(GATE_DECISION)
    decision_record = {
        "schema_version": (
            "public_text_quality_gate_adoption_decision_record_v1"
        ),
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "decision": "adopt",
        "owner_input_path": base.repo_relative(GATE_DECISION),
        "owner_input_sha256": decision["sha256"],
        "owner_identity": decision_value["owner_identity"],
        "authorized_at": decision_value["authorized_at"],
        "owner_binding_proof": decision_value["owner_binding_proof"],
        "candidate_manifest_sha256": CANDIDATE_MANIFEST_SHA256,
        "candidate_patch_sha256": CANDIDATE_PATCH_SHA256,
        "phase6_revalidation_record_sha256": base.sha256_file(
            REVALIDATION_RECORD
        ),
        "phase6_blocker_count": 0,
        "qualified_disposition": "accepted",
    }
    receipt = {
        "schema_version": (
            "public_text_quality_live_required_gate_adoption_receipt_v1"
        ),
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "operation": "append_only_required_artifacts_and_required_tests",
        "live_manifest_path": base.repo_relative(
            base.LIVE_REQUIRED_VALIDATIONS
        ),
        "live_manifest_before_sha256": LIVE_BASE_SHA256,
        "live_manifest_after_sha256": CANDIDATE_MANIFEST_SHA256,
        "candidate_manifest_sha256": CANDIDATE_MANIFEST_SHA256,
        "candidate_patch_sha256": CANDIDATE_PATCH_SHA256,
        "owner_decision_sha256": decision["sha256"],
        "phase6_revalidation_record_sha256": base.sha256_file(
            REVALIDATION_RECORD
        ),
        "g1_gate_manifest_sha256": G1_GATE_MANIFEST_SHA256,
        "g1_closeout_sha256": G1_CLOSEOUT_SHA256,
        "evaluation_subject_disposition": "accepted",
        "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
        "required_artifact_addition_count": 10,
        "required_test_addition_count": 1,
        "removed_or_modified_entry_count": 0,
        "existing_entry_reorder_count": 0,
        "cas_base_match": True,
        "live_required_gate_adopted": True,
        "protected_surface_mutation_count": 0,
        "live_manifest_mutation_count": 1,
        "runtime_lua_package_mutation_count": 0,
        "authority_effect": "live_required_validation_governance_only",
        "phase7_allowed_after_post_adoption_route_pass": True,
    }
    try:
        base.write_once_or_same(ADOPTION_DECISION_RECORD, decision_record)
        base.LIVE_REQUIRED_VALIDATIONS.write_bytes(candidate_bytes)
        if (
            base.sha256_file(base.LIVE_REQUIRED_VALIDATIONS)
            != CANDIDATE_MANIFEST_SHA256
        ):
            raise base.FoundationContractError(
                "live manifest bytes do not equal candidate after adoption"
            )
        base.write_once_or_same(ADOPTION_RECEIPT, receipt)
    except Exception:
        base.LIVE_REQUIRED_VALIDATIONS.write_bytes(live_bytes)
        raise
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "mode": "phase6-adopt-gate",
        "live_manifest_before_sha256": LIVE_BASE_SHA256,
        "live_manifest_after_sha256": CANDIDATE_MANIFEST_SHA256,
        "candidate_manifest_sha256": CANDIDATE_MANIFEST_SHA256,
        "candidate_patch_sha256": CANDIDATE_PATCH_SHA256,
        "qualified_disposition": "accepted",
        "phase6_blocker_count": revalidation["phase6_blocker_count"],
        "live_required_gate_adopted": True,
        "protected_surface_mutation_count": 0,
        "live_manifest_mutation_count": 1,
        "authority_effect": "live_required_validation_governance_only",
        "phase7_allowed_after_post_adoption_route_pass": True,
    }


def _live_is_adopted() -> bool:
    if not ADOPTION_RECEIPT.is_file():
        return False
    if base._has_unstaged_delta(base.LIVE_REQUIRED_VALIDATIONS):
        return False
    try:
        return (
            official._live_manifest_record()["sha256"]
            == CANDIDATE_MANIFEST_SHA256
        )
    except base.FoundationContractError:
        return False


def validate_required_gate() -> dict[str, Any]:
    disposition = _validate_disposition_immutable()
    live_adopted = _live_is_adopted()
    terminal_complete = TERMINAL_SEAL.is_file() and live_adopted
    if live_adopted:
        receipt = base.load_json_strict(ADOPTION_RECEIPT)
        if (
            receipt.get("status") != "PASS"
            or receipt.get("live_required_gate_adopted") is not True
            or receipt.get("live_manifest_after_sha256")
            != CANDIDATE_MANIFEST_SHA256
            or receipt.get("protected_surface_mutation_count") != 0
        ):
            raise base.FoundationContractError(
                "live required-gate adoption receipt is invalid"
            )
    return {
        "schema_version": "public_text_quality_required_gate_result_v2",
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "qualified_disposition": disposition["qualified_disposition"],
        "evaluation_subject_sha256": official.CANDIDATE_SHA256,
        "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
        "policy_closure_state": (
            "complete" if terminal_complete else "incomplete"
        ),
        "live_gate_adopted": live_adopted,
        "publish_boundary_pass_claimed": False,
        "package_or_release_ready_claimed": False,
    }


def validate_phase6() -> dict[str, Any]:
    revalidation = validate_phase6_revalidation(require_tracked=True)
    decision = _validate_owner_gate_decision()
    receipt_ref = _tracked_head_record(ADOPTION_RECEIPT)
    decision_record_ref = _tracked_head_record(ADOPTION_DECISION_RECORD)
    post_route_ref = _tracked_head_record(POST_ADOPTION_ROUTE_RESULT)
    post_route = _validate_route_result(POST_ADOPTION_ROUTE_RESULT)
    post_execution = validate_execution_environment_receipt(
        require_tracked=True,
        receipt_path=POST_ADOPTION_EXECUTION_RECEIPT,
        result_path=POST_ADOPTION_ROUTE_RESULT,
        require_affected=False,
    )
    live = official._live_manifest_record()
    receipt = base.load_json_strict(ADOPTION_RECEIPT)
    candidate = base.load_json_strict(
        PHASE6 / "required_gate_candidate.json"
    )
    live_value = base.load_json_strict(base.LIVE_REQUIRED_VALIDATIONS)
    if (
        live["sha256"] != CANDIDATE_MANIFEST_SHA256
        or live_value != candidate
        or receipt.get("status") != "PASS"
        or receipt.get("live_required_gate_adopted") is not True
        or receipt.get("live_manifest_before_sha256") != LIVE_BASE_SHA256
        or receipt.get("live_manifest_after_sha256")
        != CANDIDATE_MANIFEST_SHA256
        or receipt.get("owner_decision_sha256") != decision["sha256"]
        or receipt.get("protected_surface_mutation_count") != 0
        or receipt.get("live_manifest_mutation_count") != 1
    ):
        raise base.FoundationContractError(
            "Phase 6 live adoption validation failed"
        )
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "requirement": "phase6",
        "no_write": True,
        "qualified_disposition": "accepted",
        "disposition_maintained": True,
        "phase6_blocker_count": 0,
        "revalidation": revalidation,
        "owner_decision": decision,
        "owner_decision_record": decision_record_ref,
        "adoption_receipt": receipt_ref,
        "post_adoption_current_route": {
            **post_route_ref,
            **{
                key: value
                for key, value in post_route.items()
                if key not in ("path", "sha256")
            },
        },
        "post_adoption_bounded_execution_environment": post_execution,
        "live_manifest_sha256": live["sha256"],
        "live_required_gate_adopted": True,
        "post_adoption_artifact_set_complete": True,
        "protected_surface_mutation_count": 0,
        "live_manifest_mutation_count": 1,
        "authority_effect": "live_required_validation_governance_only",
        "phase7_allowed": True,
        "policy_closure_state": "incomplete",
    }


def _artifact_rows(paths: Iterable[Path]) -> list[dict[str, Any]]:
    return [
        _tracked_head_record(path)
        for path in sorted(paths, key=lambda item: base.repo_relative(item))
    ]


def build_phase7_freeze() -> dict[str, Any]:
    phase6 = validate_phase6()
    if _git("status", "--porcelain=v1").stdout.strip():
        raise base.FoundationContractError(
            "Phase 7 freeze requires a clean checkout"
        )
    paths: list[Path] = []
    for phase in range(6):
        paths.extend(
            path
            for path in (official.ATTEMPT_ROOT / f"phase{phase}").iterdir()
            if path.is_file()
        )
    paths.extend(
        [
            path
            for path in PHASE6.rglob("*")
            if path.is_file()
        ]
    )
    paths.extend(
        [
            G1_GATE_MANIFEST,
            G1_CLOSEOUT,
            GATE_DECISION,
            base.LIVE_REQUIRED_VALIDATIONS,
            official.FOUNDATION_CONTRACT,
            official.G4_READINESS,
            official.PHASE8_HANDOFF,
            official.PHASE8_CLOSEOUT,
            official.TERMINAL_CLOSEOUT,
            official.CANDIDATE,
            official.TRACE,
        ]
    )
    artifact_rows = _artifact_rows(paths)
    implementation_paths = [
        official.THIS_MODULE,
        official.RUNNER_MODULE,
        official.VALIDATOR_MODULE,
        Path(__file__).resolve(),
        official.CURRENT_ROUTE_TEST,
    ]
    implementation_rows = _artifact_rows(implementation_paths)
    freeze_core = {
        "schema_version": (
            "public_text_quality_phase7_final_evidence_freeze_v1"
        ),
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "freeze_commit": base.git_head(),
        "freeze_tree": _head_tree(),
        "g1_gate_manifest_sha256": G1_GATE_MANIFEST_SHA256,
        "g1_closeout_sha256": G1_CLOSEOUT_SHA256,
        "phase6_revalidation_record_sha256": base.sha256_file(
            REVALIDATION_RECORD
        ),
        "phase6_post_adoption_route_sha256": base.sha256_file(
            POST_ADOPTION_ROUTE_RESULT
        ),
        "live_manifest_sha256": CANDIDATE_MANIFEST_SHA256,
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "evaluation_subject_disposition": "accepted",
        "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
        "policy_sha256": POLICY_SHA256,
        "naturalization_handoff_sha256": official.PHASE8_HANDOFF_SHA256,
        "claim_bearing_artifact_count": len(artifact_rows),
        "claim_bearing_artifacts": artifact_rows,
        "implementation_path_count": len(implementation_rows),
        "implementation_paths": implementation_rows,
        "failed_phase6_evidence_preserved": True,
        "live_required_gate_adopted": True,
        "post_adoption_artifact_set_complete": True,
        "phase6_blocker_count": 0,
        "protected_surface_mutation_count": 0,
        "policy_closure_state": "pending_independent_review_and_owner_seal",
    }
    freeze = {
        **freeze_core,
        "freeze_hash": base.canonical_hash(freeze_core),
    }
    base.write_once_or_same(FREEZE_MANIFEST, freeze)
    manifest_core = {
        "schema_version": (
            "public_text_quality_phase7_final_artifact_hash_manifest_v1"
        ),
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "self_hash_included": False,
        "terminal_seal_included": False,
        "ordered_artifact_count": len(artifact_rows),
        "ordered_artifacts": artifact_rows,
        "freeze_manifest_path": base.repo_relative(FREEZE_MANIFEST),
        "freeze_manifest_sha256": base.sha256_file(FREEZE_MANIFEST),
    }
    manifest = {
        **manifest_core,
        "manifest_hash": base.canonical_hash(manifest_core),
    }
    base.write_once_or_same(FINAL_ARTIFACT_MANIFEST, manifest)
    request = {
        "schema_version": (
            "public_text_quality_phase7_independent_review_request_v1"
        ),
        "status": "READY_FOR_CODEX_REVIEWER",
        "attempt_id": official.ATTEMPT_ID,
        "review_subject_commit": base.git_head(),
        "review_subject_tree": _head_tree(),
        "freeze_manifest_sha256": base.sha256_file(FREEZE_MANIFEST),
        "final_artifact_hash_manifest_sha256": base.sha256_file(
            FINAL_ARTIFACT_MANIFEST
        ),
        "required_reviewer_kind": "codex_reviewer",
        "required_scopes": [
            "policy_and_denominator_unchanged",
            "validator_and_adversarial_contract",
            "exact_accepted_disposition",
            "g1_successor_0008_phase6_revalidation",
            "additive_live_gate_effect",
            "failed_evidence_preservation",
            "claim_boundary",
        ],
        "required_critical_finding_count": 0,
        "required_important_finding_count": 0,
        "owner_or_implementation_author_ineligible": True,
    }
    base.write_once_or_same(REVIEW_REQUEST, request)
    census = {
        "schema_version": (
            "public_text_quality_phase7_pre_review_vcs_census_v1"
        ),
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "claim_bearing_artifact_required_count": len(artifact_rows),
        "claim_bearing_artifact_tracked_count": len(artifact_rows),
        "claim_bearing_artifact_ignored_count": 0,
        "implementation_required_count": len(implementation_rows),
        "implementation_tracked_count": len(implementation_rows),
        "implementation_ignored_count": 0,
        "protected_surface_mutation_count": 0,
        "live_manifest_sha256": CANDIDATE_MANIFEST_SHA256,
    }
    base.write_once_or_same(PRE_REVIEW_VCS_CENSUS, census)
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "mode": "phase7-freeze",
        "freeze_manifest_path": base.repo_relative(FREEZE_MANIFEST),
        "freeze_manifest_sha256": base.sha256_file(FREEZE_MANIFEST),
        "final_artifact_hash_manifest_sha256": base.sha256_file(
            FINAL_ARTIFACT_MANIFEST
        ),
        "review_request_path": base.repo_relative(REVIEW_REQUEST),
        "reviewer_input_required": True,
        "phase6": phase6,
        "policy_closure_state": "pending_independent_review_and_owner_seal",
    }


def validate_independent_review() -> dict[str, Any]:
    review_ref = _tracked_head_record(INDEPENDENT_REVIEW)
    eligibility_ref = _tracked_head_record(REVIEWER_ELIGIBILITY)
    freeze_ref = _tracked_head_record(FREEZE_MANIFEST)
    manifest_ref = _tracked_head_record(FINAL_ARTIFACT_MANIFEST)
    review = base.load_json_strict(INDEPENDENT_REVIEW)
    eligibility = base.load_json_strict(REVIEWER_ELIGIBILITY)
    review_core = {
        key: child
        for key, child in review.items()
        if key != "reviewer_binding_proof"
    }
    eligibility_core = {
        key: child
        for key, child in eligibility.items()
        if key != "eligibility_binding_proof"
    }
    if (
        review.get("schema_version")
        != "public_text_quality_phase7_independent_review_v1"
        or review.get("status") != "PASS"
        or review.get("attempt_id") != official.ATTEMPT_ID
        or review.get("reviewer_kind") != "codex_reviewer"
        or review.get("reviewer_identity") != "codex_reviewer"
        or review.get("freeze_manifest_sha256") != freeze_ref["sha256"]
        or review.get("final_artifact_hash_manifest_sha256")
        != manifest_ref["sha256"]
        or review.get("critical_finding_count") != 0
        or review.get("important_finding_count") != 0
        or review.get("findings") != []
        or review.get("reviewed_scope_count") != 7
        or review.get("reviewer_binding_proof")
        != base.canonical_hash(review_core)
        or eligibility.get("schema_version")
        != "public_text_quality_phase7_reviewer_eligibility_v1"
        or eligibility.get("status") != "PASS"
        or eligibility.get("attempt_id") != official.ATTEMPT_ID
        or eligibility.get("reviewer_kind") != "codex_reviewer"
        or eligibility.get("reviewer_identity") != "codex_reviewer"
        or eligibility.get("independent_from_owner") is not True
        or eligibility.get("independent_from_implementation_author")
        is not True
        or eligibility.get("owner_input_cross_reclassification") is not False
        or eligibility.get("conflict_of_interest") is not False
        or eligibility.get("eligibility_binding_proof")
        != base.canonical_hash(eligibility_core)
    ):
        raise base.FoundationContractError(
            "Phase 7 independent review or reviewer eligibility is invalid"
        )
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "review": review_ref,
        "eligibility": eligibility_ref,
        "freeze_manifest": freeze_ref,
        "final_artifact_hash_manifest": manifest_ref,
        "independent_review_complete": True,
        "independent_review_eligible": True,
        "critical_finding_count": 0,
        "important_finding_count": 0,
        "reviewer_owner_cross_reclassification_count": 0,
    }


def validate_owner_seal() -> dict[str, Any]:
    review = validate_independent_review()
    owner_ref = _tracked_head_record(OWNER_CLOSURE_SEAL)
    value = base.load_json_strict(OWNER_CLOSURE_SEAL)
    core = {
        key: child
        for key, child in value.items()
        if key != "owner_binding_proof"
    }
    if (
        value.get("schema_version")
        != "public_text_quality_phase7_owner_closure_seal_v1"
        or value.get("status") != "PASS"
        or value.get("decision") != "seal_policy_closure"
        or value.get("attempt_id") != official.ATTEMPT_ID
        or value.get("owner_identity")
        != "repository_owner_via_direct_codex_instruction"
        or not isinstance(value.get("sealed_at"), str)
        or value.get("independent_review_sha256")
        != review["review"]["sha256"]
        or value.get("reviewer_eligibility_sha256")
        != review["eligibility"]["sha256"]
        or value.get("evaluation_subject_hash") != official.CANDIDATE_SHA256
        or value.get("evaluation_subject_disposition") != "accepted"
        or value.get("evaluation_subject_disposition_hash")
        != DISPOSITION_SHA256
        or value.get("policy_sha256") != POLICY_SHA256
        or value.get("live_manifest_sha256")
        != CANDIDATE_MANIFEST_SHA256
        or value.get("live_required_gate_adopted") is not True
        or value.get("post_adoption_artifact_set_complete") is not True
        or value.get("policy_closure_state") != "complete"
        or value.get("owner_binding_proof") != base.canonical_hash(core)
    ):
        raise base.FoundationContractError(
            "Phase 7 owner closure seal is invalid"
        )
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "owner_seal": owner_ref,
        "owner_seal_valid": True,
        "review": review,
    }


def build_phase7_finalize() -> dict[str, Any]:
    phase6 = validate_phase6()
    owner = validate_owner_seal()
    review = owner["review"]
    independent_validation = {
        "schema_version": (
            "public_text_quality_phase7_independent_review_validation_v1"
        ),
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "independent_review_sha256": review["review"]["sha256"],
        "reviewer_eligibility_sha256": review["eligibility"]["sha256"],
        "independent_review_complete": True,
        "independent_review_eligible": True,
        "critical_finding_count": 0,
        "important_finding_count": 0,
        "reviewer_owner_cross_reclassification_count": 0,
    }
    owner_validation = {
        "schema_version": (
            "public_text_quality_phase7_owner_seal_validation_v1"
        ),
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "owner_seal_sha256": owner["owner_seal"]["sha256"],
        "owner_identity": "repository_owner_via_direct_codex_instruction",
        "owner_seal_valid": True,
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
        "policy_sha256": POLICY_SHA256,
        "live_manifest_sha256": CANDIDATE_MANIFEST_SHA256,
    }
    base.write_once_or_same(
        INDEPENDENT_REVIEW_VALIDATION,
        independent_validation,
    )
    base.write_once_or_same(OWNER_SEAL_VALIDATION, owner_validation)
    owner_inputs = [
        official.POLICY_OWNER_INPUT,
        official.WAIVER_OWNER_INPUT,
        GATE_DECISION,
        OWNER_CLOSURE_SEAL,
    ]
    reviewer_inputs = [INDEPENDENT_REVIEW, REVIEWER_ELIGIBILITY]
    owner_rows = _artifact_rows(owner_inputs)
    reviewer_rows = _artifact_rows(reviewer_inputs)
    scope_audit = _scope_diff_audit()
    vcs_report = {
        "schema_version": (
            "public_text_quality_phase7_final_vcs_preservation_v1"
        ),
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "owner_input_required_count": len(owner_rows),
        "owner_input_tracked_count": len(owner_rows),
        "owner_input_ignored_count": 0,
        "reviewer_input_required_count": len(reviewer_rows),
        "reviewer_input_tracked_count": len(reviewer_rows),
        "reviewer_input_ignored_count": 0,
        "reviewer_owner_cross_reclassification_count": 0,
        "task_scope_diff_audit": scope_audit,
        "failed_phase6_evidence_preserved": True,
        "phase0_through_phase5_mutation_count": 0,
        "g5_candidate_trace_handoff_mutation_count": 0,
        "g6_discovery_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "protected_surface_mutation_count": 0,
        "live_manifest_mutation_count": 1,
        "live_manifest_sha256": CANDIDATE_MANIFEST_SHA256,
        "owner_inputs": owner_rows,
        "reviewer_inputs": reviewer_rows,
    }
    base.write_once_or_same(FINAL_VCS_PRESERVATION, vcs_report)
    closeout_core = {
        "schema_version": (
            "public_text_quality_acceptance_policy_closure_closeout_v1"
        ),
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "claim": "Public Text Quality Acceptance Policy Closure: complete",
        "evaluation_subject_kind": official.EVALUATION_SUBJECT_KIND,
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "qualified_disposition": "accepted",
        "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
        "policy_sha256": POLICY_SHA256,
        "g1_gate_manifest_sha256": G1_GATE_MANIFEST_SHA256,
        "g1_closeout_sha256": G1_CLOSEOUT_SHA256,
        "phase6_revalidation_record_sha256": base.sha256_file(
            REVALIDATION_RECORD
        ),
        "phase6_post_adoption_route_sha256": base.sha256_file(
            POST_ADOPTION_ROUTE_RESULT
        ),
        "independent_review_sha256": review["review"]["sha256"],
        "reviewer_eligibility_sha256": review["eligibility"]["sha256"],
        "owner_seal_sha256": owner["owner_seal"]["sha256"],
        "live_manifest_sha256": CANDIDATE_MANIFEST_SHA256,
        "machine_validation_complete": True,
        "independent_review_complete": True,
        "independent_review_eligible": True,
        "critical_finding_count": 0,
        "important_finding_count": 0,
        "owner_seal_valid": True,
        "live_required_gate_adopted": True,
        "post_adoption_artifact_set_complete": True,
        "gate_adoption_informed_authorization_valid": True,
        "policy_hash_unchanged_since_phase2": True,
        "disposition_hash_unchanged_since_phase5": True,
        "failed_evidence_preserved": True,
        "final_vcs_preservation_pass": True,
        "protected_surface_mutation_count": 0,
        "live_manifest_mutation_count": 1,
        "publish_boundary_pass_claimed": False,
        "package_or_release_ready_claimed": False,
        "registry_runtime_current_adoption_claimed": False,
        "policy_closure_state": "complete",
        "g5_return": {
            "naturalization_attempt_id": official.NATURALIZATION_ATTEMPT_ID,
            "naturalization_handoff_sha256": official.PHASE8_HANDOFF_SHA256,
            "evaluation_subject_hash": official.CANDIDATE_SHA256,
            "qualified_disposition": "accepted",
            "publish_live_required_gate_adopted": True,
            "publish_policy_closure_state": "complete",
        },
    }
    closeout = {
        **closeout_core,
        "closeout_hash": base.canonical_hash(closeout_core),
    }
    base.write_once_or_same(FINAL_CLOSEOUT, closeout)
    base.write_once_text(
        CLOSEOUT_DOC,
        (
            "# Public Text Quality Acceptance Policy Closure Closeout\n\n"
            f"- Official attempt: `{official.ATTEMPT_ID}`\n"
            f"- Evaluation subject: `{official.CANDIDATE_SHA256}`\n"
            "- Qualified disposition: `accepted`\n"
            "- Live required gate: `adopted`\n"
            "- Policy closure state: `complete`\n"
            "- Protected-surface mutation count: `0`\n"
            "- Runtime/Lua/package mutation count: `0`\n"
            "- This closeout does not claim package, release, Workshop, "
            "or manual-QA readiness.\n"
        ),
    )
    terminal_inputs = _artifact_rows(
        [
            FREEZE_MANIFEST,
            FINAL_ARTIFACT_MANIFEST,
            INDEPENDENT_REVIEW,
            REVIEWER_ELIGIBILITY,
            OWNER_CLOSURE_SEAL,
            ADOPTION_RECEIPT,
            POST_ADOPTION_ROUTE_RESULT,
        ]
    )
    terminal_inputs.extend(
        _working_record(path)
        for path in (
            INDEPENDENT_REVIEW_VALIDATION,
            OWNER_SEAL_VALIDATION,
            FINAL_VCS_PRESERVATION,
            FINAL_CLOSEOUT,
        )
    )
    terminal_inputs.sort(key=lambda row: row["path"])
    closeout_doc_record = {
        "path": base.repo_relative(CLOSEOUT_DOC),
        "sha256": base.sha256_file(CLOSEOUT_DOC),
    }
    terminal_core = {
        "schema_version": (
            "public_text_quality_acceptance_terminal_hash_seal_v1"
        ),
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "terminal_claim": (
            "Public Text Quality Acceptance Policy Closure: complete"
        ),
        "sealed_input_count": len(terminal_inputs),
        "sealed_inputs": terminal_inputs,
        "closeout_doc": closeout_doc_record,
        "final_closeout_sha256": base.sha256_file(FINAL_CLOSEOUT),
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "qualified_disposition": "accepted",
        "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
        "policy_sha256": POLICY_SHA256,
        "live_manifest_sha256": CANDIDATE_MANIFEST_SHA256,
        "naturalization_handoff_sha256": official.PHASE8_HANDOFF_SHA256,
        "live_required_gate_adopted": True,
        "policy_closure_state": "complete",
        "terminal_hash_seal_valid": True,
        "claim_bearing_mutation_after_terminal_forbidden": True,
        "protected_surface_mutation_count": 0,
        "live_manifest_mutation_count": 1,
        "runtime_lua_package_mutation_count": 0,
        "publish_boundary_pass_claimed": False,
        "package_or_release_ready_claimed": False,
    }
    terminal = {
        **terminal_core,
        "terminal_hash": base.canonical_hash(terminal_core),
    }
    base.write_once_or_same(TERMINAL_SEAL, terminal)
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "mode": "phase7-finalize",
        "phase6": phase6,
        "independent_review": review,
        "owner_seal": owner["owner_seal"],
        "final_closeout_path": base.repo_relative(FINAL_CLOSEOUT),
        "final_closeout_sha256": base.sha256_file(FINAL_CLOSEOUT),
        "terminal_artifact_path": base.repo_relative(TERMINAL_SEAL),
        "terminal_artifact_sha256": base.sha256_file(TERMINAL_SEAL),
        "qualified_disposition": "accepted",
        "live_required_gate_adopted": True,
        "policy_closure_state": "complete",
        "protected_surface_mutation_count": 0,
        "live_manifest_mutation_count": 1,
    }


def validate_terminal() -> dict[str, Any]:
    phase6 = validate_phase6()
    owner = validate_owner_seal()
    scope_audit = _scope_diff_audit()
    terminal_ref = _tracked_head_record(TERMINAL_SEAL)
    final_ref = _tracked_head_record(FINAL_CLOSEOUT)
    closeout_doc_ref = _tracked_head_record(CLOSEOUT_DOC)
    terminal = base.load_json_strict(TERMINAL_SEAL)
    core = {
        key: child
        for key, child in terminal.items()
        if key != "terminal_hash"
    }
    closeout = base.load_json_strict(FINAL_CLOSEOUT)
    closeout_core = {
        key: child
        for key, child in closeout.items()
        if key != "closeout_hash"
    }
    sealed_rows = terminal.get("sealed_inputs", [])
    if (
        terminal.get("terminal_hash") != base.canonical_hash(core)
        or terminal.get("status") != "PASS"
        or terminal.get("terminal_hash_seal_valid") is not True
        or terminal.get("qualified_disposition") != "accepted"
        or terminal.get("live_required_gate_adopted") is not True
        or terminal.get("policy_closure_state") != "complete"
        or terminal.get("final_closeout_sha256") != final_ref["sha256"]
        or terminal.get("closeout_doc", {}).get("sha256")
        != closeout_doc_ref["sha256"]
        or terminal.get("sealed_input_count") != len(sealed_rows)
        or any(
            _tracked_head_record(official.REPO_ROOT / row["path"])[
                "sha256"
            ]
            != row["sha256"]
            for row in sealed_rows
        )
        or closeout.get("closeout_hash") != base.canonical_hash(closeout_core)
        or closeout.get("status") != "PASS"
        or closeout.get("policy_closure_state") != "complete"
        or closeout.get("failed_evidence_preserved") is not True
        or closeout.get("protected_surface_mutation_count") != 0
        or closeout.get("live_manifest_mutation_count") != 1
    ):
        raise base.FoundationContractError(
            "Phase 7 terminal hash seal validation failed"
        )
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "requirement": "terminal-seal",
        "no_write": True,
        "phase6": phase6,
        "owner_seal": owner["owner_seal"],
        "terminal_artifact": terminal_ref,
        "final_closeout": final_ref,
        "closeout_doc": closeout_doc_ref,
        "terminal_hash_seal_valid": True,
        "qualified_disposition": "accepted",
        "live_required_gate_adopted": True,
        "policy_closure_state": "complete",
        "protected_surface_mutation_count": 0,
        "live_manifest_mutation_count": 1,
        "task_scope_diff_audit": scope_audit,
    }
