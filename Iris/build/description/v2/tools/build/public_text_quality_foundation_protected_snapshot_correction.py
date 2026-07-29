from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import sys
from typing import Any

import public_text_quality_foundation_g1_gate_classification_correction as predecessor


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import public_text_quality_acceptance as acceptance


foundation = predecessor.foundation
FoundationCorrectionError = predecessor.FoundationCorrectionError

CORRECTION_ID = "implementation-correction-0004"
SCHEMA_VERSION = (
    "public_text_quality_foundation_protected_snapshot_identity_"
    "correction_readiness_v1"
)
BUILD_START_COMMIT = "3073d06b1d3b03e6f5b17603a4fa2031dfcbeb2e"
BUILD_START_TREE = "506361c8d4ea82cc09e89b157f4004cf4d3d08f0"
VALIDATED_SUBJECT_COMMIT = "edc70fdca94edc7b114f350e74373de9d39e2b0e"
VALIDATED_SUBJECT_TREE = "5350b45eecd62491306247b659339af44616706e"

FOUNDATION_CONTRACT_SHA256 = (
    "4a31e48dacc9c906c4fe4a04cce22799226b23366cd77cd948e91473e1844b02"
)
PREDECESSOR_READINESS_SHA256 = (
    "fa96bbdeddbcb287fd5c9c39894385729cc1d165bc1281a00f8ee031f3c85e59"
)
G1_GATE_MANIFEST_SHA256 = (
    "fc837f3c6957ac8da1ee4bf4cf2d9f9b0e5588c843ecc27ba2b903b1334e12f9"
)
G1_GATE_CLOSEOUT_SHA256 = (
    "9a85e375db6c272b6f8eb685fb0024ee839e9f0dac3e42d728ed5e3632462f1e"
)
AB_CANONICAL_SHA256 = (
    "62b6eb0a0be79cbfe99b5072058cc1d0e1ff60885cc10a2e0fd8341bd709b4f1"
)
COMPILER_AGGREGATE_SHA256 = (
    "aa88ee878cfb570b8278b40e62c560f093dc6ffdc363f06ed7133352d635c647"
)
PROTECTED_SNAPSHOT_ALGORITHM_ID = (
    "git_head_blob_raw_sha256_with_filtered_or_lf_canonical_working_text_"
    "and_raw_binary_v1"
)

FOUNDATION_ROOT = foundation.FOUNDATION_ROOT
PREDECESSOR_READINESS = (
    FOUNDATION_ROOT
    / "readiness_successors"
    / "implementation-correction-0003"
    / "public_text_quality_g1_gate_classification_readiness.json"
)
SUCCESSOR_ROOT = FOUNDATION_ROOT / "readiness_successors" / CORRECTION_ID
SUCCESSOR_PATH = (
    SUCCESSOR_ROOT
    / "public_text_quality_protected_snapshot_identity_readiness.json"
)

CLEAN_CHECKOUT_ROOT = REPO_ROOT / "Iris" / "validation" / "clean_checkout"
G1_GATE_MANIFEST = (
    CLEAN_CHECKOUT_ROOT
    / "evidence"
    / "full_repository_gate_manifest_successor_0004.json"
)
G1_GATE_CLOSEOUT = (
    CLEAN_CHECKOUT_ROOT
    / "authority"
    / "full_repository_technical_debt_closeout_successor_0004.json"
)
CORRECTED_IMPLEMENTATION = (
    V2_ROOT / "tools" / "build" / "public_text_quality_acceptance.py"
)
REGRESSION_TEST = (
    V2_ROOT / "tests" / "test_public_text_constituent_identity.py"
)
CORRECTED_IMPLEMENTATION_SHA256 = (
    "96911c4db921937ca6928234773e5392ab4ef614962b79c5cfc59e2cd823b620"
)
REGRESSION_TEST_SHA256 = (
    "df1ab5ab403ef6c79b1306107e185a8a9ca425cc131943912a7ff66878672c0b"
)

IMPLEMENTATION_FILES = (
    TOOLS_DIR
    / "public_text_quality_foundation_protected_snapshot_correction.py",
    TOOLS_DIR
    / "run_public_text_quality_foundation_protected_snapshot_correction.py",
    TOOLS_DIR
    / "validate_public_text_quality_foundation_protected_snapshot_correction.py",
)
TRACKING_FILES = (REPO_ROOT / ".gitignore", REPO_ROOT / ".gitattributes")

EXPECTED_G1_EVIDENCE_DELTA = frozenset(
    {
        foundation._repo_relative(G1_GATE_MANIFEST),
        foundation._repo_relative(G1_GATE_CLOSEOUT),
    }
)
EXPECTED_IMPLEMENTATION_DELTA = frozenset(
    {
        foundation._repo_relative(CORRECTED_IMPLEMENTATION),
        foundation._repo_relative(REGRESSION_TEST),
    }
)
EXPECTED_ACCEPTANCE_SYMBOL_DELTA = frozenset(
    {
        "PROTECTED_SNAPSHOT_IDENTITY_ALGORITHM_ID",
        "build_protected_snapshot_identity_from_bytes",
        "build_protected_snapshot_present_row_from_bytes",
        "_protected_snapshot",
    }
)
EXPECTED_TEST_SYMBOL_DELTA = frozenset(
    {
        "protected_identity",
        "protected_snapshot_row",
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
        != VALIDATED_SUBJECT_COMMIT
        or _changed_paths(BUILD_START_COMMIT) != EXPECTED_G1_EVIDENCE_DELTA
        or _changed_paths(VALIDATED_SUBJECT_COMMIT)
        != EXPECTED_IMPLEMENTATION_DELTA
    ):
        raise FoundationCorrectionError(
            "protected-snapshot correction readpoint or delta mismatch"
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
        "g1_evidence_delta_paths": sorted(EXPECTED_G1_EVIDENCE_DELTA),
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
            "public_text_quality_foundation_g1_gate_classification_"
            "correction_readiness_v1"
        )
        or readiness.get("correction_id") != "implementation-correction-0003"
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
            "implementation-correction-0003 predecessor is invalid"
        )
    return {
        **record,
        "correction_id": "implementation-correction-0003",
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
            targets = (
                node.targets
                if isinstance(node, ast.Assign)
                else [node.target]
            )
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
        _git_blob_at(f"{VALIDATED_SUBJECT_COMMIT}^", path)
    )
    corrected_symbols = _top_level_symbol_map(
        _git_blob_at(VALIDATED_SUBJECT_COMMIT, path)
    )
    return frozenset(
        symbol
        for symbol in set(predecessor_symbols) | set(corrected_symbols)
        if predecessor_symbols.get(symbol) != corrected_symbols.get(symbol)
    )


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
            record = predecessor._sealed_text_record(
                path,
                CORRECTED_IMPLEMENTATION_SHA256,
            )
            if (
                record["authority_git_blob_raw_sha256"]
                == predecessor_row["git_blob_raw_sha256"]
            ):
                raise FoundationCorrectionError(
                    "protected-snapshot implementation correction is absent"
                )
            corrected_count += 1
            classification = (
                "intended_protected_snapshot_identity_representation_"
                "correction"
            )
        else:
            record = predecessor._sealed_text_record(
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
    test_symbol_delta = _changed_symbols(REGRESSION_TEST)
    if (
        acceptance_symbol_delta != EXPECTED_ACCEPTANCE_SYMBOL_DELTA
        or test_symbol_delta != EXPECTED_TEST_SYMBOL_DELTA
        or acceptance.TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID
        != predecessor_readiness.get(
            "foundation_semantics", {}
        ).get("freshness_algorithm_id")
        or acceptance.PROTECTED_SNAPSHOT_IDENTITY_ALGORITHM_ID
        != PROTECTED_SNAPSHOT_ALGORITHM_ID
    ):
        raise FoundationCorrectionError(
            "correction symbol or identity-algorithm boundary mismatch"
        )
    regression_record = predecessor._sealed_text_record(
        REGRESSION_TEST,
        REGRESSION_TEST_SHA256,
    )
    return {
        "foundation_contract": contract,
        "meaning_path_count": len(current_rows),
        "unchanged_meaning_path_count": unchanged_count,
        "intentionally_corrected_meaning_path_count": corrected_count,
        "meaning_paths": current_rows,
        "regression_test": regression_record,
        "acceptance_top_level_symbol_delta": sorted(
            acceptance_symbol_delta
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
        "handoff_text_constituent_freshness_algorithm_changed": False,
        "protected_snapshot_identity_implementation_changed": True,
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
    manifest_record = predecessor._sealed_text_record(
        G1_GATE_MANIFEST,
        G1_GATE_MANIFEST_SHA256,
    )
    closeout_record = predecessor._sealed_text_record(
        G1_GATE_CLOSEOUT,
        G1_GATE_CLOSEOUT_SHA256,
    )
    manifest = foundation._load_json(G1_GATE_MANIFEST)
    closeout = foundation._load_json(G1_GATE_CLOSEOUT)
    _require_mapping(
        manifest,
        {
            "schema_version": (
                "iris-clean-checkout-full-repository-gate-manifest-v4"
            ),
            "status": "PASS",
            "manifest_state": "frozen",
        },
        label="G1 gate manifest successor 0004",
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
            "pytest_identity_count": 181,
            "standalone_validation_count": 4,
            "required_execution_unit_count": 185,
            "passed_execution_unit_count": 185,
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
        {"status": "PASS", "result": "8/8", "exit_code": 0},
        label="focused current-required regression",
    )
    cleanup = manifest.get("cleanup", {})
    _require_mapping(
        cleanup,
        {
            "residual_disposable_checkout_count": 0,
            "persistent_worktree_entry_count_before": 14,
            "persistent_worktree_entry_count_after": 14,
            "persistent_worktree_created": False,
        },
        label="G1 cleanup",
    )
    preservation = manifest.get("preservation", {})
    _require_mapping(
        preservation,
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
                "closeout_successor_v4"
            ),
            "status": "complete",
        },
        label="G1 closeout successor 0004",
    )
    _require_mapping(
        closeout.get("closeout", {}),
        {
            "protected_snapshot_identity_correction_status": "PASS",
            "full_clean_checkout_gate_status": "PASS",
            "blocking_condition_count": 0,
            "blocking_conditions": [],
        },
        label="G1 closeout status",
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
        "gate_manifest_successor_0004": manifest_record,
        "closeout_successor_0004": closeout_record,
        "census": {
            "tracked": 93,
            "required": 33,
            "historical": 55,
            "obsolete": 3,
            "fixture": 2,
            "unresolved_dependency": 0,
        },
        "focused_pytest_result": "8/8 PASS",
        "focused_standalone_result": "8/8 PASS",
        "run_a_result": "185/185 PASS",
        "run_b_result": "185/185 PASS",
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
            CORRECTED_IMPLEMENTATION,
            REGRESSION_TEST,
            *TRACKING_FILES,
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
            "public_text_quality_foundation_protected_snapshot_correction_"
            "no_write_snapshot_v1"
        ),
        "surface_count": len(rows),
        "surface_hash": foundation._canonical_hash(rows),
        "surfaces": rows,
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
    ignore_lines = (REPO_ROOT / ".gitignore").read_text(
        encoding="utf-8"
    ).splitlines()
    attribute_lines = (REPO_ROOT / ".gitattributes").read_text(
        encoding="utf-8"
    ).splitlines()
    if (
        ignore_lines.count(ignore_line) != 1
        or attribute_lines.count(attribute_line) != 1
    ):
        raise FoundationCorrectionError(
            "protected-snapshot successor tracking rules are not exact"
        )
    return {
        "successor_path": relative,
        "exact_unignore_rule_count": 1,
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
            "append_only_foundation_protected_snapshot_identity_"
            "implementation_correction"
        ),
        "purpose": (
            "Bind the Phase 0 protected-snapshot HEAD authority and "
            "line-ending-independent tracked UTF-8 working identity "
            "correction, its focused regression, and its 185/185 G1 "
            "clean-checkout A/B evidence without granting authority."
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
            "protected_snapshot_identity_algorithm_modified": True,
            "foundation_contract_modified": False,
            "policy_threshold_denominator_detector_modified": False,
            "handoff_text_constituent_identity_modified": False,
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
        "handoff_text_constituent_freshness_algorithm_changed": False,
        "protected_snapshot_identity_implementation_changed": True,
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
            "append-only protected-snapshot readiness successor already exists"
        )
    before = protected_snapshot()
    guard = predecessor.predecessor._no_write_guard(
        before,
        protected_snapshot(),
    )
    successor = build_successor_projection(
        require_exact_start_head=True,
        no_write_guard=guard,
    )
    SUCCESSOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUCCESSOR_PATH.write_bytes(foundation._pretty_json_bytes(successor))
    predecessor.predecessor._no_write_guard(before, protected_snapshot())
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
        "required_execution_unit_count": 185,
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
            "protected-snapshot readiness successor must be tracked and unignored"
        )
    relative = foundation._repo_relative(SUCCESSOR_PATH)
    blob_id = predecessor.predecessor._index_or_head_blob(relative)
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
            "protected-snapshot readiness successor is missing"
        )
    successor_bytes = SUCCESSOR_PATH.read_bytes()
    successor = foundation._load_json(SUCCESSOR_PATH)
    before = protected_snapshot()
    guard = predecessor.predecessor._no_write_guard(
        before,
        protected_snapshot(),
    )
    expected = build_successor_projection(
        require_exact_start_head=False,
        no_write_guard=guard,
    )
    if successor != expected:
        raise FoundationCorrectionError(
            "protected-snapshot readiness differs from exact projection"
        )
    vcs_state = _require_successor_vcs_state()
    if SUCCESSOR_PATH.read_bytes() != successor_bytes:
        raise FoundationCorrectionError(
            "no-write validator changed successor bytes"
        )
    predecessor.predecessor._no_write_guard(before, protected_snapshot())
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
        "required_execution_unit_count": 185,
        "canonical_result_sha256": AB_CANONICAL_SHA256,
        "vcs_state": vcs_state,
        "protected_surface_mutation_count": 0,
        "no_write_validation": True,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
    }
