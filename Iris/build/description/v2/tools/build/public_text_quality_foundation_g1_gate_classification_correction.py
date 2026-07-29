from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import public_text_quality_foundation_g1_handoff_correction as predecessor


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import public_text_quality_acceptance as acceptance


foundation = predecessor.foundation
FoundationCorrectionError = predecessor.FoundationCorrectionError

CORRECTION_ID = "implementation-correction-0003"
SCHEMA_VERSION = (
    "public_text_quality_foundation_g1_gate_classification_"
    "correction_readiness_v1"
)
START_COMMIT = "f5e5007255fcb4c88468834225b249fcbd0682e6"
START_TREE = "5f7227e440984dfcdb8cc45cb89a27ad8cbf15c0"
VALIDATED_SUBJECT_COMMIT = "cf8bbb3e083f1ea8155b24d9ead3eaf80c35b684"
VALIDATED_SUBJECT_TREE = "fdc2b9cab16a9d2a7dbf912ece3a6574a63b92fb"

FOUNDATION_CONTRACT_SHA256 = (
    "4a31e48dacc9c906c4fe4a04cce22799226b23366cd77cd948e91473e1844b02"
)
PREDECESSOR_READINESS_SHA256 = (
    "abe9ce479647ed1f126a3c11ab5dd7c9c11afdd1c757fd68241eef58f8095e25"
)
GATE_CONTRACT_SHA256 = (
    "4688229eb5dacaa809e52d614db579fc3c810b3c6c0787fe08aa01ca52cca7d5"
)
GATE_MANIFEST_SHA256 = (
    "876af6afc01f1349f369ed8982228944df31fedc79917bc885b3171fcdf6bb15"
)
GATE_CLOSEOUT_SHA256 = (
    "5dfd72386d0853f35eac13c2274f47b876dda4aa905334ca72cd49a25a07d632"
)
AB_CANONICAL_SHA256 = (
    "bd424ddcc2b22abcdd81843099a4cd603785ba62d61d8a6d5bb115708fd6fe84"
)
COMPILER_AGGREGATE_SHA256 = (
    "aa88ee878cfb570b8278b40e62c560f093dc6ffdc363f06ed7133352d635c647"
)

FOUNDATION_ROOT = foundation.FOUNDATION_ROOT
PREDECESSOR_READINESS = (
    FOUNDATION_ROOT
    / "readiness_successors"
    / "implementation-correction-0002"
    / "public_text_quality_development_readiness_g1_handoff_correction.json"
)
SUCCESSOR_ROOT = FOUNDATION_ROOT / "readiness_successors" / CORRECTION_ID
SUCCESSOR_PATH = (
    SUCCESSOR_ROOT
    / "public_text_quality_g1_gate_classification_readiness.json"
)

CLEAN_CHECKOUT_ROOT = REPO_ROOT / "Iris" / "validation" / "clean_checkout"
GATE_CONTRACT = CLEAN_CHECKOUT_ROOT / "contracts" / "full_repository_gate.json"
GATE_MANIFEST = (
    CLEAN_CHECKOUT_ROOT
    / "evidence"
    / "full_repository_gate_manifest_successor_0003.json"
)
GATE_CLOSEOUT = (
    CLEAN_CHECKOUT_ROOT
    / "authority"
    / "full_repository_technical_debt_closeout_successor_0003.json"
)
CLASSIFIER_RUNNER = (
    CLEAN_CHECKOUT_ROOT / "run_iris_clean_checkout_validation.py"
)
CLASSIFIER_TEST = (
    CLEAN_CHECKOUT_ROOT / "tests" / "test_iris_clean_checkout_validation.py"
)
CONSTITUENT_TEST = (
    V2_ROOT / "tests" / "test_public_text_constituent_identity.py"
)
CONSTITUENT_TEST_RELATIVE = foundation._repo_relative(CONSTITUENT_TEST)

EXPECTED_VALIDATED_SUBJECT_DELTA = frozenset(
    {
        foundation._repo_relative(GATE_CONTRACT),
        foundation._repo_relative(CLASSIFIER_RUNNER),
        foundation._repo_relative(CLASSIFIER_TEST),
    }
)
EXPECTED_EVIDENCE_DELTA = frozenset(
    {
        foundation._repo_relative(GATE_MANIFEST),
        foundation._repo_relative(GATE_CLOSEOUT),
    }
)

IMPLEMENTATION_FILES = (
    TOOLS_DIR
    / "public_text_quality_foundation_g1_gate_classification_correction.py",
    TOOLS_DIR
    / "run_public_text_quality_foundation_g1_gate_classification_correction.py",
    TOOLS_DIR
    / "validate_public_text_quality_foundation_g1_gate_classification_correction.py",
)
TRACKING_FILES = (REPO_ROOT / ".gitignore", REPO_ROOT / ".gitattributes")


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
            "show", "-s", "--format=%T", START_COMMIT
        ).stdout.strip()
        != START_TREE
        or foundation._git(
            "show", "-s", "--format=%T", VALIDATED_SUBJECT_COMMIT
        ).stdout.strip()
        != VALIDATED_SUBJECT_TREE
        or foundation._git(
            "rev-parse", f"{START_COMMIT}^"
        ).stdout.strip()
        != VALIDATED_SUBJECT_COMMIT
        or _changed_paths(START_COMMIT) != EXPECTED_EVIDENCE_DELTA
        or _changed_paths(VALIDATED_SUBJECT_COMMIT)
        != EXPECTED_VALIDATED_SUBJECT_DELTA
    ):
        raise FoundationCorrectionError(
            "G1 gate-classification correction readpoint or delta mismatch"
        )
    head = foundation._git("rev-parse", "HEAD").stdout.strip()
    if require_exact_head:
        if head != START_COMMIT:
            raise FoundationCorrectionError(
                "readiness build requires the exact G1 evidence HEAD"
            )
    else:
        foundation._require_ancestor(START_COMMIT, head)
    return {
        "commit": START_COMMIT,
        "tree": START_TREE,
        "validated_subject_commit": VALIDATED_SUBJECT_COMMIT,
        "validated_subject_tree": VALIDATED_SUBJECT_TREE,
        "validated_subject_delta_paths": sorted(
            EXPECTED_VALIDATED_SUBJECT_DELTA
        ),
        "evidence_delta_paths": sorted(EXPECTED_EVIDENCE_DELTA),
        "exact_head_required_for_build": True,
        "start_commit_is_ancestor_of_validation_head": True,
    }


def _sealed_text_record(path: Path, declared_sha256: str) -> dict[str, Any]:
    record = acceptance._head_text_constituent_record(
        path,
        declared_sha256,
    )
    canonical_contract_match = record.get("match") is True
    exact_working_raw_match = (
        foundation._sha256_file(path) == declared_sha256
    )
    sealed_match = canonical_contract_match or (
        exact_working_raw_match
        and record.get("working_matches_head_authority") is True
    )
    if not sealed_match:
        raise FoundationCorrectionError(
            f"sealed text identity mismatch: {foundation._repo_relative(path)}"
        )
    return {
        **record,
        "match": True,
        "canonical_contract_declared_match": canonical_contract_match,
        "exact_working_raw_sha256_match": exact_working_raw_match,
        "declared_binding_mode": (
            "canonical_line_ending_representation"
            if canonical_contract_match
            else "exact_working_raw_plus_canonical_head_identity"
        ),
        "sealed_declared_sha256": declared_sha256,
        "raw_head_git_identity_strict": True,
    }


def _validate_predecessor_readiness() -> dict[str, Any]:
    record = foundation._raw_tracked_record(
        PREDECESSOR_READINESS,
        PREDECESSOR_READINESS_SHA256,
    )
    readiness = foundation._load_json(PREDECESSOR_READINESS)
    if (
        readiness.get("schema_version")
        != "public_text_quality_foundation_g1_handoff_correction_readiness_v1"
        or readiness.get("correction_id") != "implementation-correction-0002"
        or readiness.get("status") != "PASS"
        or readiness.get("authority_effect") != "none"
        or readiness.get("foundation_contract_semantics_changed") is not False
        or readiness.get(
            "policy_threshold_denominator_detector_semantics_changed"
        )
        is not False
        or readiness.get("protected_surface_mutation_count") != 0
    ):
        raise FoundationCorrectionError(
            "implementation-correction-0002 predecessor is invalid"
        )
    return {
        **record,
        "correction_id": "implementation-correction-0002",
        "append_only_successor_required": True,
        "predecessor_mutated": False,
    }


def _validate_foundation_semantics() -> dict[str, Any]:
    predecessor_readiness = foundation._load_json(PREDECESSOR_READINESS)
    predecessor_rows = predecessor_readiness.get(
        "foundation_semantics", {}
    ).get("meaning_paths", [])
    current_rows: list[dict[str, Any]] = []
    for predecessor_row in predecessor_rows:
        relative = str(predecessor_row["path"])
        path = REPO_ROOT / relative
        expected_blob_id = str(
            predecessor_row.get(
                "corrected_git_blob_id",
                predecessor_row.get("git_blob_id", ""),
            )
        )
        expected_raw_sha256 = str(
            predecessor_row.get(
                "corrected_git_blob_raw_sha256",
                predecessor_row.get("git_blob_raw_sha256", ""),
            )
        )
        record = _sealed_text_record(path, expected_raw_sha256)
        if record["head_git_blob_id"] != expected_blob_id:
            raise FoundationCorrectionError(
                f"Foundation meaning path changed: {relative}"
            )
        current_rows.append(
            {
                "path": relative,
                "git_blob_id": record["head_git_blob_id"],
                "git_blob_raw_sha256": record[
                    "authority_git_blob_raw_sha256"
                ],
                "predecessor_current_git_blob_identity": True,
            }
        )
    if len(current_rows) != 17:
        raise FoundationCorrectionError(
            "Foundation meaning path census is not exactly 17"
        )
    contract = foundation._raw_tracked_record(
        foundation.FOUNDATION_CONTRACT,
        FOUNDATION_CONTRACT_SHA256,
    )
    if (
        predecessor_readiness.get("foundation_semantics", {})
        .get("foundation_contract", {})
        .get("sha256")
        != FOUNDATION_CONTRACT_SHA256
        or acceptance.TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID
        != predecessor_readiness.get(
            "handoff_text_constituent_freshness", {}
        )
        .get("identity_probes", {})
        .get("algorithm_id")
    ):
        raise FoundationCorrectionError(
            "Foundation contract or freshness algorithm changed"
        )
    return {
        "foundation_contract": contract,
        "meaning_path_count": len(current_rows),
        "unchanged_meaning_path_count": len(current_rows),
        "meaning_paths": current_rows,
        "freshness_algorithm_id": (
            acceptance.TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID
        ),
        "foundation_contract_semantics_changed": False,
        "policy_threshold_denominator_detector_semantics_changed": False,
        "freshness_algorithm_changed": False,
    }


def _require_exact_mapping(
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


def _validate_gate_classification() -> dict[str, Any]:
    gate_record = _sealed_text_record(GATE_CONTRACT, GATE_CONTRACT_SHA256)
    manifest_record = _sealed_text_record(
        GATE_MANIFEST,
        GATE_MANIFEST_SHA256,
    )
    closeout_record = _sealed_text_record(
        GATE_CLOSEOUT,
        GATE_CLOSEOUT_SHA256,
    )
    gate = foundation._load_json(GATE_CONTRACT)
    manifest = foundation._load_json(GATE_MANIFEST)
    closeout = foundation._load_json(GATE_CLOSEOUT)

    explicit_sources = gate.get("source_disposition_policy", {}).get(
        "explicit_current_required_sources", []
    )
    if (
        gate.get("schema_version")
        != "iris-clean-checkout-full-repository-gate-v3"
        or [row.get("path") for row in explicit_sources]
        != [CONSTITUENT_TEST_RELATIVE]
    ):
        raise FoundationCorrectionError(
            "G1 explicit-current gate contract is invalid"
        )

    _require_exact_mapping(
        manifest,
        {
            "schema_version": (
                "iris-clean-checkout-full-repository-gate-manifest-v3"
            ),
            "status": "PASS",
            "manifest_state": "frozen",
            "terminal_claim": (
                "public text constituent identity is an explicit "
                "current-required full-gate source"
            ),
        },
        label="G1 gate manifest",
    )
    _require_exact_mapping(
        manifest.get("validated_subject", {}),
        {
            "commit": VALIDATED_SUBJECT_COMMIT,
            "tree": VALIDATED_SUBJECT_TREE,
        },
        label="G1 validated subject",
    )
    _require_exact_mapping(
        manifest.get("classification_recensus", {}).get(
            "validated_subject", {}
        ),
        {
            "tracked_test_source_count": 93,
            "required_source_count": 33,
            "historical_optional_source_count": 55,
            "obsolete_or_misrouted_source_count": 3,
            "hermetic_test_fixture_source_count": 2,
            "unresolved_edge_count": 0,
        },
        label="G1 classification census",
    )
    execution = manifest.get("execution_reproducibility", {})
    _require_exact_mapping(
        execution,
        {
            "pytest_identity_count": 176,
            "standalone_validation_count": 4,
            "required_execution_unit_count": 180,
            "passed_execution_unit_count": 180,
            "failed_execution_unit_count": 0,
            "collection_error_count": 0,
            "constituent_identity_count": 3,
            "constituent_identity_passed_count": 3,
            "canonical_results_equal": True,
            "canonical_result_sha256": AB_CANONICAL_SHA256,
        },
        label="G1 A/B execution",
    )
    for run_id in ("run_a", "run_b"):
        _require_exact_mapping(
            execution.get(run_id, {}),
            {
                "status": "PASS",
                "canonical_result_sha256": AB_CANONICAL_SHA256,
            },
            label=f"G1 {run_id}",
        )
    focused = manifest.get("focused_validation", {})
    _require_exact_mapping(
        focused.get("constituent_identity", {}),
        {"status": "PASS", "result": "3/3", "exit_code": 0},
        label="constituent identity validation",
    )
    _require_exact_mapping(
        focused.get("clean_checkout_classifier_regression", {}),
        {
            "status": "PASS",
            "result": "11/11",
            "exit_code": 0,
            "required_demotion_failure_case_exercised": True,
        },
        label="classifier regression validation",
    )
    cleanup = manifest.get("cleanup", {})
    if (
        cleanup.get("residual_disposable_checkout_count") != 0
        or cleanup.get("persistent_worktree_created") is not False
        or any(
            cleanup.get(key) is not True
            for key in (
                "run_a_source_checkout_clean_before",
                "run_a_source_checkout_clean_after",
                "run_b_source_checkout_clean_before",
                "run_b_source_checkout_clean_after",
                "run_a_source_ignored_state_unchanged",
                "run_b_source_ignored_state_unchanged",
            )
        )
    ):
        raise FoundationCorrectionError("G1 cleanup evidence is invalid")
    preservation = manifest.get("preservation", {})
    if not preservation or any(value is not False for value in preservation.values()):
        raise FoundationCorrectionError("G1 preservation boundary is invalid")

    _require_exact_mapping(
        closeout,
        {
            "schema_version": (
                "iris_clean_checkout_full_repository_technical_debt_"
                "closeout_successor_v3"
            ),
            "status": "complete",
        },
        label="G1 gate closeout",
    )
    _require_exact_mapping(
        closeout.get("inventory_closeout", {}),
        {
            "tracked_test_source_count": 93,
            "required_source_count": 33,
            "historical_optional_source_count": 55,
            "obsolete_or_misrouted_source_count": 3,
            "hermetic_test_fixture_source_count": 2,
        },
        label="G1 closeout census",
    )
    _require_exact_mapping(
        closeout.get("closeout", {}),
        {
            "explicit_current_required_classification_status": "PASS",
            "full_clean_checkout_gate_status": "PASS",
            "blocking_condition_count": 0,
            "blocking_conditions": [],
        },
        label="G1 closeout status",
    )
    if (
        closeout.get("validation_closeout", {}).get(
            "canonical_result_sha256"
        )
        != AB_CANONICAL_SHA256
    ):
        raise FoundationCorrectionError("G1 closeout A/B hash mismatch")

    classification_binding = manifest.get("classification_contract", {})
    if (
        classification_binding.get("path")
        != foundation._repo_relative(GATE_CONTRACT)
        or classification_binding.get("git_blob_id")
        != gate_record["head_git_blob_id"]
        or classification_binding.get("git_blob_raw_sha256")
        != gate_record["authority_git_blob_raw_sha256"]
        or classification_binding.get("explicit_current_required_source")
        != CONSTITUENT_TEST_RELATIVE
    ):
        raise FoundationCorrectionError(
            "G1 manifest contract binding mismatch"
        )

    implementation_records: dict[str, dict[str, Any]] = {}
    for key, path in (
        ("runner", CLASSIFIER_RUNNER),
        ("regression_tests", CLASSIFIER_TEST),
        ("constituent_test", CONSTITUENT_TEST),
    ):
        binding = manifest.get("implementation_bindings", {}).get(key, {})
        record = _sealed_text_record(
            path,
            str(binding.get("git_blob_raw_sha256", "")),
        )
        if (
            binding.get("path") != foundation._repo_relative(path)
            or binding.get("git_blob_id") != record["head_git_blob_id"]
        ):
            raise FoundationCorrectionError(
                f"G1 implementation binding mismatch: {key}"
            )
        implementation_records[key] = record

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
            "commit": START_COMMIT,
            "tree": START_TREE,
        },
        "gate_contract": gate_record,
        "gate_manifest_successor_0003": manifest_record,
        "closeout_successor_0003": closeout_record,
        "classification": "current_required",
        "execution_role": "required_pytest",
        "census": {
            "tracked": 93,
            "required": 33,
            "historical": 55,
            "obsolete": 3,
            "fixture": 2,
        },
        "run_a_result": "180/180 PASS",
        "run_b_result": "180/180 PASS",
        "canonical_results_equal": True,
        "canonical_result_sha256": AB_CANONICAL_SHA256,
        "implementation_bindings": implementation_records,
        "compiler_identity_algorithm_id": compiler_identity["algorithm_id"],
        "compiler_aggregate_sha256": COMPILER_AGGREGATE_SHA256,
        "blocking_condition_count": 0,
    }


def _protected_paths() -> list[Path]:
    protected = set(predecessor.predecessor._protected_paths())
    protected.update(
        {
            PREDECESSOR_READINESS,
            foundation.FOUNDATION_CONTRACT,
            GATE_CONTRACT,
            GATE_MANIFEST,
            GATE_CLOSEOUT,
            CLASSIFIER_RUNNER,
            CLASSIFIER_TEST,
            CONSTITUENT_TEST,
            *TRACKING_FILES,
            *IMPLEMENTATION_FILES,
        }
    )
    protected.update(
        REPO_ROOT / relative
        for relative in foundation.FOUNDATION_MEANING_PATHS
    )
    protected.update(
        REPO_ROOT / relative
        for relative in foundation._git(
            "ls-files",
            "--",
            foundation._repo_relative(CLEAN_CHECKOUT_ROOT),
        ).stdout.splitlines()
        if relative
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
            "public_text_quality_foundation_g1_gate_classification_"
            "correction_no_write_snapshot_v1"
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
    if ignore_lines.count(ignore_line) != 1 or attribute_lines.count(
        attribute_line
    ) != 1:
        raise FoundationCorrectionError(
            "successor tracking rules are not exact"
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
            "append_only_foundation_g1_gate_classification_correction"
        ),
        "purpose": (
            "Bind the G1 explicit-current constituent-identity test "
            "classification and its 180/180 clean-checkout evidence without "
            "changing Foundation meaning or authority."
        ),
        "execution_start_readpoint": _validate_readpoints(
            require_exact_head=require_exact_start_head
        ),
        "predecessor_readiness": _validate_predecessor_readiness(),
        "foundation_semantics": _validate_foundation_semantics(),
        "g1_gate_classification_correction": (
            _validate_gate_classification()
        ),
        "successor_tracking_rules": _tracking_rules(),
        "successor_implementation_hashes": _implementation_hashes(),
        "protected_no_write_guard": no_write_guard,
        "scope_boundaries": {
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
            "new_worktree_or_repository_copy_created": False,
        },
        "foundation_contract_semantics_changed": False,
        "policy_threshold_denominator_detector_semantics_changed": False,
        "freshness_algorithm_changed": False,
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
            "append-only G1 classification readiness successor already exists"
        )
    before = protected_snapshot()
    guard = predecessor._no_write_guard(before, protected_snapshot())
    successor = build_successor_projection(
        require_exact_start_head=True,
        no_write_guard=guard,
    )
    SUCCESSOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUCCESSOR_PATH.write_bytes(foundation._pretty_json_bytes(successor))
    predecessor._no_write_guard(before, protected_snapshot())
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
        "required_execution_unit_count": 180,
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
            "classification readiness successor must be tracked and unignored"
        )
    relative = foundation._repo_relative(SUCCESSOR_PATH)
    blob_id = predecessor._index_or_head_blob(relative)
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
            "classification readiness successor is missing"
        )
    successor_bytes = SUCCESSOR_PATH.read_bytes()
    successor = foundation._load_json(SUCCESSOR_PATH)
    before = protected_snapshot()
    guard = predecessor._no_write_guard(before, protected_snapshot())
    expected = build_successor_projection(
        require_exact_start_head=False,
        no_write_guard=guard,
    )
    if successor != expected:
        raise FoundationCorrectionError(
            "classification readiness successor differs from exact projection"
        )
    vcs_state = _require_successor_vcs_state()
    if SUCCESSOR_PATH.read_bytes() != successor_bytes:
        raise FoundationCorrectionError(
            "no-write validator changed successor bytes"
        )
    predecessor._no_write_guard(before, protected_snapshot())
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
        "required_execution_unit_count": 180,
        "canonical_result_sha256": AB_CANONICAL_SHA256,
        "vcs_state": vcs_state,
        "protected_surface_mutation_count": 0,
        "no_write_validation": True,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
    }
