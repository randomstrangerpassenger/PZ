from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import sys
from typing import Any

import public_text_quality_foundation_protected_snapshot_correction as predecessor


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import public_text_quality_acceptance as acceptance


foundation = predecessor.foundation
FoundationCorrectionError = predecessor.FoundationCorrectionError

CORRECTION_ID = "implementation-correction-0005"
SCHEMA_VERSION = (
    "public_text_quality_foundation_phase0_required_input_vcs_preflight_"
    "parity_correction_readiness_v1"
)
BUILD_START_COMMIT = "30cb8dfa797ee55f66cfa31bb829dc68e5517df8"
BUILD_START_TREE = "a8dcf953e214f0803d15153e76616966f0c32981"
G1_GATE_EVIDENCE_COMMIT = "c0ffb2708db9ead6feb2ca2468ce9dae010cb1f6"
G1_GATE_EVIDENCE_TREE = "b74f6edb2e7bf5d524b1b3cbac6eefba264342db"
VALIDATED_SUBJECT_COMMIT = "437aa3e8723d189ae92ef4fdb466536bc037bb81"
VALIDATED_SUBJECT_TREE = "53b2bd1d990e8c2e054431a1a44f3582f0b02a9c"
VALIDATED_SUBJECT_PARENT = "f00e15f56ba27aac0b4ffff4aab7e9b8e89a6336"

FOUNDATION_CONTRACT_SHA256 = (
    "4a31e48dacc9c906c4fe4a04cce22799226b23366cd77cd948e91473e1844b02"
)
PREDECESSOR_READINESS_SHA256 = (
    "8d52c65a17565c39eb623d3213e7c209ace5b0a2204b05b8eeea0da1bede61e0"
)
G1_GATE_MANIFEST_SHA256 = (
    "4a8e04e8fdcefdc78d9aca9b607ca735f3d07e5620a673ab0ef47b3b1905d8c1"
)
G1_GATE_CLOSEOUT_SHA256 = (
    "9278eaa57343e0c7c000eaf7f4d4cf418d04a651c9c95c50c8e033dd10255689"
)
G1_IDENTITY_CORRECTION_MANIFEST_SHA256 = (
    "f8b46cb5832be3c6759e9a3c7be93daa5c6bddd211b39dcd64e730772a1844a3"
)
G1_IDENTITY_CORRECTION_CLOSEOUT_SHA256 = (
    "3b237adb15e8bc11ea697289257a63d43f78133ce054e15e1ab4f9b81dfdf7a6"
)
AB_CANONICAL_SHA256 = (
    "340c691946fec4844802ef179f896ad38bdc344316d2d19ceff8d4504a2d5ea5"
)
PHASE0_REQUIRED_PATH_SET_SHA256 = (
    "4ae5f7549124c4f411cc743ff0b6331052c09103bbdbc902e19fd3102eb3d85c"
)
COMPILER_AGGREGATE_SHA256 = (
    "aa88ee878cfb570b8278b40e62c560f093dc6ffdc363f06ed7133352d635c647"
)

FOUNDATION_ROOT = foundation.FOUNDATION_ROOT
PREDECESSOR_READINESS = (
    FOUNDATION_ROOT
    / "readiness_successors"
    / "implementation-correction-0004"
    / "public_text_quality_protected_snapshot_identity_readiness.json"
)
SUCCESSOR_ROOT = FOUNDATION_ROOT / "readiness_successors" / CORRECTION_ID
SUCCESSOR_PATH = (
    SUCCESSOR_ROOT / "public_text_quality_phase0_vcs_parity_readiness.json"
)

CLEAN_CHECKOUT_ROOT = REPO_ROOT / "Iris" / "validation" / "clean_checkout"
G1_GATE_MANIFEST = (
    CLEAN_CHECKOUT_ROOT
    / "evidence"
    / "full_repository_gate_manifest_successor_0005.json"
)
G1_GATE_CLOSEOUT = (
    CLEAN_CHECKOUT_ROOT
    / "authority"
    / "full_repository_technical_debt_closeout_successor_0005.json"
)
G1_IDENTITY_CORRECTION_MANIFEST = (
    CLEAN_CHECKOUT_ROOT
    / "evidence"
    / "full_repository_gate_manifest_successor_0006.json"
)
G1_IDENTITY_CORRECTION_CLOSEOUT = (
    CLEAN_CHECKOUT_ROOT
    / "authority"
    / "full_repository_technical_debt_closeout_successor_0006.json"
)
GITIGNORE = REPO_ROOT / ".gitignore"
GITATTRIBUTES = REPO_ROOT / ".gitattributes"
CORRECTED_IMPLEMENTATION = (
    V2_ROOT / "tools" / "build" / "public_text_quality_acceptance.py"
)
OFFICIAL_WRAPPER = (
    V2_ROOT
    / "tools"
    / "build"
    / "public_text_quality_acceptance_official_0004.py"
)
REGRESSION_TEST = (
    V2_ROOT / "tests" / "test_public_text_constituent_identity.py"
)

GITIGNORE_SHA256 = (
    "0b7eafc5accb7bc7e8baec6e752a9d563490901f5f13a092cb6748280043cb89"
)
CORRECTED_IMPLEMENTATION_SHA256 = (
    "39a764890e7a9baea3bcab4eb871891c385f142436dcb33e2cca1860078f0abc"
)
OFFICIAL_WRAPPER_SHA256 = (
    "49f5cfa5d0e6f28552d5bf1ccf14b02d6787ff090fdee7b60d9c8be3c30d3b10"
)
REGRESSION_TEST_SHA256 = (
    "bc86cc68ffc48aa093527f86f592445a1648907b49b66efbbde986dcd9d87a2c"
)

IMPLEMENTATION_FILES = (
    TOOLS_DIR
    / "public_text_quality_foundation_phase0_vcs_parity_correction.py",
    TOOLS_DIR
    / "run_public_text_quality_foundation_phase0_vcs_parity_correction.py",
    TOOLS_DIR
    / "validate_public_text_quality_foundation_phase0_vcs_parity_correction.py",
)
TRACKING_FILES = (GITIGNORE, GITATTRIBUTES)

EXPECTED_G1_GATE_DELTA = frozenset(
    {
        foundation._repo_relative(G1_GATE_MANIFEST),
        foundation._repo_relative(G1_GATE_CLOSEOUT),
    }
)
EXPECTED_G1_IDENTITY_CORRECTION_DELTA = frozenset(
    {
        foundation._repo_relative(G1_IDENTITY_CORRECTION_MANIFEST),
        foundation._repo_relative(G1_IDENTITY_CORRECTION_CLOSEOUT),
    }
)
EXPECTED_IMPLEMENTATION_DELTA = frozenset(
    {
        foundation._repo_relative(GITIGNORE),
        foundation._repo_relative(CORRECTED_IMPLEMENTATION),
        foundation._repo_relative(OFFICIAL_WRAPPER),
        foundation._repo_relative(REGRESSION_TEST),
    }
)
EXPECTED_ACCEPTANCE_SYMBOL_DELTA = frozenset(
    {
        "PHASE0_REQUIRED_VCS_CONSUMERS",
        "_vcs_preflight",
        "build_phase0_binding",
        "phase0_required_vcs_paths",
        "phase0_required_vcs_preflight",
        "require_phase0_required_vcs_preflight",
    }
)
EXPECTED_WRAPPER_SYMBOL_DELTA = frozenset({"run_official_mode"})
EXPECTED_TEST_SYMBOL_DELTA = frozenset(
    {
        "NATURALIZATION_ATTEMPT_ROOT",
        "PHASE0_ATTEMPT_REQUIRED_PATHS",
        "PHASE0_IMPLEMENTATION_REQUIRED_PATHS",
        "PublicTextConstituentIdentityTest",
    }
)


def _changed_paths(commit: str) -> frozenset[str]:
    return frozenset(
        line
        for line in foundation._git(
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            commit,
        ).stdout.splitlines()
        if line
    )


def _validate_readpoints(*, require_exact_head: bool) -> dict[str, Any]:
    if (
        foundation._git(
            "show", "-s", "--format=%T", BUILD_START_COMMIT
        ).stdout.strip()
        != BUILD_START_TREE
        or foundation._git(
            "show", "-s", "--format=%T", VALIDATED_SUBJECT_COMMIT
        ).stdout.strip()
        != VALIDATED_SUBJECT_TREE
        or foundation._git(
            "rev-parse", f"{BUILD_START_COMMIT}^"
        ).stdout.strip()
        != G1_GATE_EVIDENCE_COMMIT
        or foundation._git(
            "show", "-s", "--format=%T", G1_GATE_EVIDENCE_COMMIT
        ).stdout.strip()
        != G1_GATE_EVIDENCE_TREE
        or foundation._git(
            "rev-parse", f"{G1_GATE_EVIDENCE_COMMIT}^"
        ).stdout.strip()
        != VALIDATED_SUBJECT_COMMIT
        or foundation._git(
            "rev-parse", f"{VALIDATED_SUBJECT_COMMIT}^"
        ).stdout.strip()
        != VALIDATED_SUBJECT_PARENT
        or _changed_paths(BUILD_START_COMMIT)
        != EXPECTED_G1_IDENTITY_CORRECTION_DELTA
        or _changed_paths(G1_GATE_EVIDENCE_COMMIT)
        != EXPECTED_G1_GATE_DELTA
        or _changed_paths(VALIDATED_SUBJECT_COMMIT)
        != EXPECTED_IMPLEMENTATION_DELTA
    ):
        raise FoundationCorrectionError(
            "Phase 0 VCS-preflight correction readpoint or delta mismatch"
        )
    head = foundation._git("rev-parse", "HEAD").stdout.strip()
    if require_exact_head:
        if head != BUILD_START_COMMIT:
            raise FoundationCorrectionError(
                "readiness build requires the exact G1 successor HEAD"
            )
    else:
        foundation._require_ancestor(BUILD_START_COMMIT, head)
    return {
        "commit": BUILD_START_COMMIT,
        "tree": BUILD_START_TREE,
        "validated_subject_commit": VALIDATED_SUBJECT_COMMIT,
        "validated_subject_tree": VALIDATED_SUBJECT_TREE,
        "validated_subject_delta_paths": sorted(
            EXPECTED_IMPLEMENTATION_DELTA
        ),
        "g1_gate_evidence_commit": G1_GATE_EVIDENCE_COMMIT,
        "g1_gate_evidence_tree": G1_GATE_EVIDENCE_TREE,
        "g1_gate_evidence_delta_paths": sorted(EXPECTED_G1_GATE_DELTA),
        "g1_identity_correction_delta_paths": sorted(
            EXPECTED_G1_IDENTITY_CORRECTION_DELTA
        ),
        "exact_head_required_for_build": True,
        "build_start_is_ancestor_of_validation_head": True,
    }


def _validate_predecessor_readiness() -> dict[str, Any]:
    record = foundation._raw_tracked_record(
        PREDECESSOR_READINESS,
        PREDECESSOR_READINESS_SHA256,
    )
    readiness = foundation._load_json(PREDECESSOR_READINESS)
    if (
        readiness.get("schema_version")
        != (
            "public_text_quality_foundation_protected_snapshot_identity_"
            "correction_readiness_v1"
        )
        or readiness.get("correction_id") != "implementation-correction-0004"
        or readiness.get("status") != "PASS"
        or readiness.get("authority_effect") != "none"
        or readiness.get("protected_surface_mutation_count") != 0
        or readiness.get("foundation_contract_semantics_changed") is not False
        or readiness.get(
            "policy_threshold_denominator_detector_semantics_changed"
        )
        is not False
    ):
        raise FoundationCorrectionError(
            "implementation-correction-0004 predecessor is invalid"
        )
    return {
        **record,
        "correction_id": "implementation-correction-0004",
        "append_only_successor_required": True,
        "predecessor_mutated": False,
    }


def _top_level_symbol_map(raw: bytes) -> dict[str, str]:
    tree = ast.parse(raw.decode("utf-8"))
    result: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            result[node.name] = ast.dump(node, include_attributes=False)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    result[target.id] = ast.dump(
                        node,
                        include_attributes=False,
                    )
    return result


def _git_blob_at(commit: str, path: Path) -> bytes:
    relative = foundation._repo_relative(path)
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise FoundationCorrectionError(
            f"cannot read correction blob at {commit}: {relative}"
        )
    return result.stdout


def _changed_symbols(path: Path) -> frozenset[str]:
    predecessor_symbols = _top_level_symbol_map(
        _git_blob_at(VALIDATED_SUBJECT_PARENT, path)
    )
    corrected_symbols = _top_level_symbol_map(
        _git_blob_at(VALIDATED_SUBJECT_COMMIT, path)
    )
    return frozenset(
        symbol
        for symbol in set(predecessor_symbols) | set(corrected_symbols)
        if predecessor_symbols.get(symbol) != corrected_symbols.get(symbol)
    )


def _sealed_text_record(
    path: Path,
    declared_sha256: str,
) -> dict[str, Any]:
    return predecessor.predecessor._sealed_text_record(
        path,
        declared_sha256,
    )


def _historical_raw_record(
    commit: str,
    path: Path,
    declared_sha256: str,
) -> dict[str, Any]:
    raw = _git_blob_at(commit, path)
    actual_sha256 = foundation._sha256_bytes(raw)
    relative = foundation._repo_relative(path)
    blob_id = foundation._git(
        "rev-parse",
        f"{commit}:{relative}",
    ).stdout.strip()
    if actual_sha256 != declared_sha256:
        raise FoundationCorrectionError(
            f"historical raw identity mismatch: {relative}"
        )
    return {
        "path": relative,
        "commit": commit,
        "git_blob_id": blob_id,
        "git_blob_raw_sha256": actual_sha256,
        "match": True,
    }


def _validate_foundation_semantics() -> dict[str, Any]:
    predecessor_readiness = foundation._load_json(PREDECESSOR_READINESS)
    predecessor_rows = predecessor_readiness.get(
        "foundation_semantics", {}
    ).get("meaning_paths", [])
    corrected_relative = foundation._repo_relative(CORRECTED_IMPLEMENTATION)
    current_rows: list[dict[str, Any]] = []
    corrected_count = 0
    unchanged_count = 0
    for predecessor_row in predecessor_rows:
        relative = str(predecessor_row["path"])
        path = REPO_ROOT / relative
        if relative == corrected_relative:
            record = _sealed_text_record(
                path,
                CORRECTED_IMPLEMENTATION_SHA256,
            )
            if (
                record["authority_git_blob_raw_sha256"]
                == predecessor_row["git_blob_raw_sha256"]
            ):
                raise FoundationCorrectionError(
                    "Phase 0 VCS-preflight implementation correction is absent"
                )
            corrected_count += 1
            classification = (
                "intended_phase0_required_input_vcs_preflight_parity_"
                "correction"
            )
        else:
            record = _sealed_text_record(
                path,
                str(predecessor_row["git_blob_raw_sha256"]),
            )
            if (
                record["head_git_blob_id"]
                != predecessor_row["git_blob_id"]
                or record["authority_git_blob_raw_sha256"]
                != predecessor_row["git_blob_raw_sha256"]
            ):
                raise FoundationCorrectionError(
                    f"unintended Foundation meaning change: {relative}"
                )
            unchanged_count += 1
            classification = "byte_identical_to_predecessor"
        current_rows.append(
            {
                "path": relative,
                "git_blob_id": record["head_git_blob_id"],
                "git_blob_raw_sha256": record[
                    "authority_git_blob_raw_sha256"
                ],
                "classification": classification,
            }
        )
    if (
        len(current_rows) != 17
        or corrected_count != 1
        or unchanged_count != 16
    ):
        raise FoundationCorrectionError(
            "Foundation meaning-path correction census mismatch"
        )
    contract = foundation._raw_tracked_record(
        foundation.FOUNDATION_CONTRACT,
        FOUNDATION_CONTRACT_SHA256,
    )
    acceptance_symbol_delta = _changed_symbols(CORRECTED_IMPLEMENTATION)
    wrapper_symbol_delta = _changed_symbols(OFFICIAL_WRAPPER)
    test_symbol_delta = _changed_symbols(REGRESSION_TEST)
    predecessor_semantics = predecessor_readiness.get(
        "foundation_semantics", {}
    )
    if (
        acceptance_symbol_delta != EXPECTED_ACCEPTANCE_SYMBOL_DELTA
        or wrapper_symbol_delta != EXPECTED_WRAPPER_SYMBOL_DELTA
        or test_symbol_delta != EXPECTED_TEST_SYMBOL_DELTA
        or acceptance.TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID
        != predecessor_semantics.get(
            "handoff_text_constituent_identity_algorithm_id"
        )
        or acceptance.PROTECTED_SNAPSHOT_IDENTITY_ALGORITHM_ID
        != predecessor_semantics.get(
            "protected_snapshot_identity_algorithm_id"
        )
    ):
        raise FoundationCorrectionError(
            "correction symbol or identity-algorithm boundary mismatch"
        )
    return {
        "foundation_contract": contract,
        "meaning_path_count": len(current_rows),
        "unchanged_meaning_path_count": unchanged_count,
        "intentionally_corrected_meaning_path_count": corrected_count,
        "meaning_paths": current_rows,
        "correction_support": {
            "validated_subject_gitignore": _historical_raw_record(
                VALIDATED_SUBJECT_COMMIT,
                GITIGNORE,
                GITIGNORE_SHA256,
            ),
            "official_wrapper": _sealed_text_record(
                OFFICIAL_WRAPPER,
                OFFICIAL_WRAPPER_SHA256,
            ),
            "regression_test": _sealed_text_record(
                REGRESSION_TEST,
                REGRESSION_TEST_SHA256,
            ),
        },
        "acceptance_top_level_symbol_delta": sorted(
            acceptance_symbol_delta
        ),
        "official_wrapper_top_level_symbol_delta": sorted(
            wrapper_symbol_delta
        ),
        "regression_test_top_level_symbol_delta": sorted(test_symbol_delta),
        "handoff_text_constituent_identity_algorithm_id": (
            acceptance.TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID
        ),
        "protected_snapshot_identity_algorithm_id": (
            acceptance.PROTECTED_SNAPSHOT_IDENTITY_ALGORITHM_ID
        ),
        "foundation_contract_semantics_changed": False,
        "policy_threshold_denominator_detector_semantics_changed": False,
        "freshness_algorithm_changed": False,
        "phase0_required_input_vcs_preflight_implementation_changed": True,
    }


def _require_mapping(
    actual: dict[str, Any],
    expected: dict[str, Any],
    *,
    label: str,
) -> None:
    mismatches = sorted(
        key for key, value in expected.items() if actual.get(key) != value
    )
    if mismatches:
        raise FoundationCorrectionError(
            f"{label} field mismatch: {mismatches}"
        )


def _validate_g1_evidence() -> dict[str, Any]:
    manifest_record = _sealed_text_record(
        G1_GATE_MANIFEST,
        G1_GATE_MANIFEST_SHA256,
    )
    closeout_record = _sealed_text_record(
        G1_GATE_CLOSEOUT,
        G1_GATE_CLOSEOUT_SHA256,
    )
    identity_manifest_record = _sealed_text_record(
        G1_IDENTITY_CORRECTION_MANIFEST,
        G1_IDENTITY_CORRECTION_MANIFEST_SHA256,
    )
    identity_closeout_record = _sealed_text_record(
        G1_IDENTITY_CORRECTION_CLOSEOUT,
        G1_IDENTITY_CORRECTION_CLOSEOUT_SHA256,
    )
    manifest = foundation._load_json(G1_GATE_MANIFEST)
    closeout = foundation._load_json(G1_GATE_CLOSEOUT)
    identity_manifest = foundation._load_json(
        G1_IDENTITY_CORRECTION_MANIFEST
    )
    identity_closeout = foundation._load_json(
        G1_IDENTITY_CORRECTION_CLOSEOUT
    )
    _require_mapping(
        manifest,
        {
            "schema_version": (
                "iris-clean-checkout-full-repository-gate-manifest-v5"
            ),
            "status": "PASS",
            "manifest_state": "frozen",
        },
        label="G1 gate manifest successor 0005",
    )
    _require_mapping(
        manifest.get("validated_subject", {}),
        {
            "commit": VALIDATED_SUBJECT_COMMIT,
            "tree": VALIDATED_SUBJECT_TREE,
        },
        label="G1 validated subject",
    )
    _require_mapping(
        manifest.get("phase0_required_input_vcs_preflight", {}),
        {
            "status": "PASS",
            "required_path_count": 38,
            "required_path_set_sha256": PHASE0_REQUIRED_PATH_SET_SHA256,
            "path_sets_equal": True,
            "ignored_count": 0,
            "unstaged_delta_count": 0,
            "head_working_identity_pass_count": 38,
            "blocking_condition_count": 0,
        },
        label="Phase 0 required-input VCS preflight",
    )
    _require_mapping(
        manifest.get("classification_recensus", {}),
        {
            "tracked_test_source_count": 93,
            "required_source_count": 33,
            "historical_optional_source_count": 55,
            "obsolete_or_misrouted_source_count": 3,
            "hermetic_test_fixture_source_count": 2,
            "unresolved_edge_count": 0,
        },
        label="G1 census",
    )
    execution = manifest.get("execution_reproducibility", {})
    _require_mapping(
        execution,
        {
            "pytest_identity_count": 185,
            "standalone_validation_count": 4,
            "required_execution_unit_count": 189,
            "passed_execution_unit_count": 189,
            "failed_execution_unit_count": 0,
            "collection_error_count": 0,
            "canonical_results_equal": True,
            "canonical_result_sha256": AB_CANONICAL_SHA256,
            "comparison_validator_exit_code": 0,
        },
        label="G1 A/B execution",
    )
    for run_id in ("run_a", "run_b"):
        _require_mapping(
            execution.get(run_id, {}),
            {
                "status": "PASS",
                "canonical_result_sha256": AB_CANONICAL_SHA256,
                "exit_code": 0,
            },
            label=f"G1 {run_id}",
        )
    _require_mapping(
        manifest.get("focused_validation", {}).get(
            "current_required_pytest", {}
        ),
        {"status": "PASS", "result": "12/12", "exit_code": 0},
        label="focused current-required regression",
    )
    _require_mapping(
        manifest.get("cleanup", {}),
        {
            "residual_disposable_checkout_count": 0,
            "persistent_worktree_entry_count_before": 14,
            "persistent_worktree_entry_count_after": 14,
            "persistent_worktree_created": False,
        },
        label="G1 cleanup",
    )
    _require_mapping(
        manifest.get("preservation", {}),
        {
            "foundation_contract_changed": False,
            "policy_changed": False,
            "threshold_changed": False,
            "denominator_changed": False,
            "detector_changed": False,
            "naturalization_changed_or_executed": False,
            "phase8_handoff_changed": False,
            "candidate_changed": False,
            "facts_or_manifest_changed": False,
            "publish_attempt_changed_or_executed": False,
            "protected_product_surface_mutation_count": 0,
            "authority_effect": "none",
            "existing_g1_evidence_overwritten": False,
        },
        label="G1 preservation",
    )
    _require_mapping(
        closeout,
        {
            "schema_version": (
                "iris_clean_checkout_full_repository_technical_debt_"
                "closeout_successor_v5"
            ),
            "status": "complete",
        },
        label="G1 closeout successor 0005",
    )
    _require_mapping(
        closeout.get("closeout", {}),
        {
            "exact_unignore_status": "PASS",
            "phase0_required_input_vcs_preflight_parity_status": "PASS",
            "full_clean_checkout_gate_status": "PASS",
            "blocking_condition_count": 0,
            "blocking_conditions": [],
        },
        label="G1 closeout status",
    )
    _require_mapping(
        identity_manifest,
        {
            "schema_version": (
                "iris-clean-checkout-full-repository-gate-manifest-v6"
            ),
            "status": "PASS",
            "record_mode": "append_only_raw_git_identity_label_correction",
        },
        label="G1 identity correction manifest 0006",
    )
    _require_mapping(
        identity_manifest.get("correction", {}),
        {
            "corrected_field_count": 2,
            "tests_rerun": False,
            "validated_subject_changed": False,
            "execution_result_changed": False,
            "authority_effect": "none",
        },
        label="G1 identity correction",
    )
    corrected_identities = identity_manifest.get(
        "corrected_raw_git_identities", []
    )
    expected_corrected_identities = {
        ".gitignore": GITIGNORE_SHA256,
        foundation._repo_relative(CORRECTED_IMPLEMENTATION): (
            "3eb3b5bbc48ac62910a8eb6ccf2313086f638acaa80d4efc28cdd7f3c763e4ed"
        ),
    }
    if (
        len(corrected_identities) != 2
        or {
            str(row.get("path")): str(row.get("git_blob_raw_sha256"))
            for row in corrected_identities
        }
        != expected_corrected_identities
    ):
        raise FoundationCorrectionError(
            "G1 corrected raw Git identities mismatch"
        )
    _require_mapping(
        identity_closeout,
        {
            "schema_version": (
                "iris_clean_checkout_full_repository_technical_debt_"
                "closeout_successor_v6"
            ),
            "status": "complete",
        },
        label="G1 identity closeout 0006",
    )
    _require_mapping(
        identity_closeout.get("correction_closeout", {}),
        {
            "corrected_field_count": 2,
            "predecessor_preserved": True,
            "tests_rerun": False,
            "gate_result_changed": False,
            "blocking_condition_count": 0,
            "blocking_conditions": [],
        },
        label="G1 identity closeout",
    )
    compiler_identity = acceptance.build_compiler_identity(REPO_ROOT)
    if (
        compiler_identity.get("aggregate_sha256")
        != COMPILER_AGGREGATE_SHA256
    ):
        raise FoundationCorrectionError(
            "canonical Naturalization compiler aggregate is stale"
        )
    return {
        "status": "PASS",
        "validated_subject": {
            "commit": VALIDATED_SUBJECT_COMMIT,
            "tree": VALIDATED_SUBJECT_TREE,
        },
        "evidence_commit": {
            "commit": BUILD_START_COMMIT,
            "tree": BUILD_START_TREE,
        },
        "gate_evidence_commit": {
            "commit": G1_GATE_EVIDENCE_COMMIT,
            "tree": G1_GATE_EVIDENCE_TREE,
        },
        "gate_manifest_successor_0005": manifest_record,
        "closeout_successor_0005": closeout_record,
        "raw_identity_correction_manifest_0006": identity_manifest_record,
        "raw_identity_correction_closeout_0006": identity_closeout_record,
        "phase0_required_path_count": 38,
        "phase0_required_path_set_sha256": PHASE0_REQUIRED_PATH_SET_SHA256,
        "ignored_required_input_count": 0,
        "broad_unignore_count": 0,
        "census": {
            "tracked": 93,
            "required": 33,
            "historical": 55,
            "obsolete": 3,
            "fixture": 2,
            "unresolved_dependency": 0,
        },
        "focused_pytest_result": "12/12 PASS",
        "focused_standalone_result": "12/12 PASS",
        "run_a_result": "189/189 PASS",
        "run_b_result": "189/189 PASS",
        "canonical_results_equal": True,
        "canonical_result_sha256": AB_CANONICAL_SHA256,
        "compiler_identity_algorithm_id": compiler_identity["algorithm_id"],
        "compiler_aggregate_sha256": COMPILER_AGGREGATE_SHA256,
        "blocking_condition_count": 0,
    }


def _protected_paths() -> list[Path]:
    protected = set(predecessor._protected_paths())
    protected.update(
        {
            PREDECESSOR_READINESS,
            foundation.FOUNDATION_CONTRACT,
            G1_GATE_MANIFEST,
            G1_GATE_CLOSEOUT,
            G1_IDENTITY_CORRECTION_MANIFEST,
            G1_IDENTITY_CORRECTION_CLOSEOUT,
            GITIGNORE,
            GITATTRIBUTES,
            CORRECTED_IMPLEMENTATION,
            OFFICIAL_WRAPPER,
            REGRESSION_TEST,
            *IMPLEMENTATION_FILES,
        }
    )
    protected.discard(SUCCESSOR_PATH)
    return sorted(protected, key=foundation._repo_relative)


def protected_snapshot() -> dict[str, Any]:
    rows = []
    for path in _protected_paths():
        present = path.is_file()
        rows.append(
            {
                "path": foundation._repo_relative(path),
                "present": present,
                "raw_sha256": (
                    foundation._sha256_file(path) if present else None
                ),
                "byte_count": path.stat().st_size if present else None,
            }
        )
    return {
        "schema_version": (
            "public_text_quality_foundation_phase0_vcs_parity_"
            "no_write_snapshot_v1"
        ),
        "surface_count": len(rows),
        "surface_hash": foundation._canonical_hash(rows),
        "surfaces": rows,
    }


def _no_write_guard(
    before: dict[str, Any],
    after: dict[str, Any],
) -> dict[str, Any]:
    if before != after:
        raise FoundationCorrectionError(
            "protected surface changed during no-write validation"
        )
    return {
        "status": "PASS",
        "protected_surface_count": before["surface_count"],
        "before_surface_hash": before["surface_hash"],
        "after_surface_hash": after["surface_hash"],
        "mutation_count": 0,
        "authority_effect": "none",
    }


def _implementation_hashes() -> list[dict[str, Any]]:
    return [
        {
            "path": foundation._repo_relative(path),
            "hash_algorithm": "sha256_utf8_lf_normalized_v1",
            "sha256": foundation._sha256_lf(path),
        }
        for path in IMPLEMENTATION_FILES
    ]


def _tracking_rules() -> dict[str, Any]:
    relative = foundation._repo_relative(SUCCESSOR_PATH)
    ignore_line = f"!{relative}"
    attribute_line = f"{relative} -text"
    ignore_lines = GITIGNORE.read_text(encoding="utf-8").splitlines()
    attribute_lines = GITATTRIBUTES.read_text(
        encoding="utf-8"
    ).splitlines()
    implementation_unignore_lines = [
        f"!{foundation._repo_relative(path)}" for path in IMPLEMENTATION_FILES
    ]
    if (
        ignore_lines.count(ignore_line) != 1
        or attribute_lines.count(attribute_line) != 1
        or any(ignore_lines.count(line) != 1 for line in implementation_unignore_lines)
    ):
        raise FoundationCorrectionError(
            "Phase 0 VCS-parity successor tracking rules are not exact"
        )
    return {
        "successor_path": relative,
        "exact_successor_unignore_rule_count": 1,
        "exact_implementation_unignore_rule_count": 3,
        "exact_text_unset_rule_count": 1,
        "broad_unignore_added": False,
    }


def build_successor_projection(
    *,
    require_exact_start_head: bool,
    no_write_guard: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "correction_id": CORRECTION_ID,
        "readiness_kind": (
            "append_only_foundation_phase0_required_input_vcs_preflight_"
            "parity_implementation_correction"
        ),
        "purpose": (
            "Bind the exact attempt-0023 required-input unignore surface, "
            "the single helper shared by Phase 0 no-write and real binding, "
            "and the 189/189 G1 clean-checkout A/B evidence without granting "
            "authority."
        ),
        "execution_start_readpoint": _validate_readpoints(
            require_exact_head=require_exact_start_head
        ),
        "predecessor_readiness": _validate_predecessor_readiness(),
        "foundation_semantics": _validate_foundation_semantics(),
        "g1_clean_checkout_correction": _validate_g1_evidence(),
        "successor_tracking_rules": _tracking_rules(),
        "successor_implementation_hashes": _implementation_hashes(),
        "protected_no_write_guard": no_write_guard,
        "scope_boundaries": {
            "foundation_implementation_modified": True,
            "phase0_required_input_vcs_preflight_modified": True,
            "exact_unignore_modified": True,
            "foundation_contract_modified": False,
            "policy_threshold_denominator_detector_modified": False,
            "freshness_algorithm_modified": False,
            "naturalization_modified_or_executed": False,
            "phase8_handoff_modified": False,
            "candidate_modified": False,
            "facts_or_manifest_modified": False,
            "official_attempt_0004_created_or_executed": False,
            "live_gate_modified": False,
            "runtime_lua_package_modified": False,
            "persistent_worktree_created": False,
        },
        "foundation_contract_semantics_changed": False,
        "policy_threshold_denominator_detector_semantics_changed": False,
        "freshness_algorithm_changed": False,
        "phase0_required_input_vcs_preflight_implementation_changed": True,
        "protected_surface_mutation_count": 0,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
        "next_stage": "official_attempt_0004_phase0_no_write_preflight",
    }


def _validate_correction_id(correction_id: str) -> None:
    if correction_id != CORRECTION_ID:
        raise FoundationCorrectionError(
            f"only the exact correction ID {CORRECTION_ID} is allowed"
        )


def build_successor(correction_id: str) -> dict[str, Any]:
    _validate_correction_id(correction_id)
    if SUCCESSOR_PATH.exists():
        raise FoundationCorrectionError(
            "append-only Phase 0 VCS-parity readiness successor already exists"
        )
    before = protected_snapshot()
    guard = _no_write_guard(before, protected_snapshot())
    successor = build_successor_projection(
        require_exact_start_head=True,
        no_write_guard=guard,
    )
    SUCCESSOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUCCESSOR_PATH.write_bytes(foundation._pretty_json_bytes(successor))
    _no_write_guard(before, protected_snapshot())
    return {
        "status": "PASS",
        "correction_id": CORRECTION_ID,
        "readiness_successor_path": foundation._repo_relative(
            SUCCESSOR_PATH
        ),
        "readiness_successor_raw_sha256": foundation._sha256_file(
            SUCCESSOR_PATH
        ),
        "foundation_contract_sha256": FOUNDATION_CONTRACT_SHA256,
        "predecessor_readiness_sha256": PREDECESSOR_READINESS_SHA256,
        "required_execution_unit_count": 189,
        "protected_surface_mutation_count": 0,
        "authority_effect": "none",
    }


def _require_successor_vcs_state() -> dict[str, Any]:
    if (
        not SUCCESSOR_PATH.is_file()
        or not foundation._is_tracked(SUCCESSOR_PATH)
        or foundation._is_ignored(SUCCESSOR_PATH)
    ):
        raise FoundationCorrectionError(
            "Phase 0 VCS-parity readiness successor must be tracked and unignored"
        )
    relative = foundation._repo_relative(SUCCESSOR_PATH)
    blob_id = predecessor.predecessor.predecessor._index_or_head_blob(relative)
    working_blob_id = foundation._git(
        "hash-object", "--no-filters", "--", relative
    ).stdout.strip()
    attr = foundation._git(
        "check-attr", "text", "--", relative
    ).stdout.strip()
    if blob_id != working_blob_id or not attr.endswith(": text: unset"):
        raise FoundationCorrectionError(
            "successor Git blob/working-byte or -text identity mismatch"
        )
    return {
        "tracked": True,
        "ignored": False,
        "text_attribute": "unset",
        "git_blob_id": blob_id,
        "working_raw_blob_id": working_blob_id,
        "git_blob_working_byte_identity": True,
    }


def validate_successor(correction_id: str) -> dict[str, Any]:
    _validate_correction_id(correction_id)
    if not SUCCESSOR_PATH.is_file():
        raise FoundationCorrectionError(
            "Phase 0 VCS-parity readiness successor is missing"
        )
    successor_bytes = SUCCESSOR_PATH.read_bytes()
    successor = foundation._load_json(SUCCESSOR_PATH)
    before = protected_snapshot()
    guard = _no_write_guard(before, protected_snapshot())
    expected = build_successor_projection(
        require_exact_start_head=False,
        no_write_guard=guard,
    )
    if successor != expected:
        raise FoundationCorrectionError(
            "Phase 0 VCS-parity readiness differs from exact projection"
        )
    vcs_state = _require_successor_vcs_state()
    if SUCCESSOR_PATH.read_bytes() != successor_bytes:
        raise FoundationCorrectionError(
            "no-write validator changed successor bytes"
        )
    _no_write_guard(before, protected_snapshot())
    return {
        "status": "PASS",
        "correction_id": CORRECTION_ID,
        "readiness_successor_path": foundation._repo_relative(
            SUCCESSOR_PATH
        ),
        "readiness_successor_raw_sha256": foundation._sha256_file(
            SUCCESSOR_PATH
        ),
        "foundation_contract_sha256": FOUNDATION_CONTRACT_SHA256,
        "predecessor_readiness_sha256": PREDECESSOR_READINESS_SHA256,
        "required_execution_unit_count": 189,
        "canonical_result_sha256": AB_CANONICAL_SHA256,
        "vcs_state": vcs_state,
        "protected_surface_mutation_count": 0,
        "no_write_validation": True,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
    }
