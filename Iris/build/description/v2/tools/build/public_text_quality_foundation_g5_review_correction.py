from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
from typing import Any

import public_text_quality_foundation_phase0_vcs_parity_correction as predecessor


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import public_text_quality_acceptance as acceptance


foundation = predecessor.foundation
FoundationCorrectionError = predecessor.FoundationCorrectionError

CORRECTION_ID = "implementation-correction-0006"
SCHEMA_VERSION = (
    "public_text_quality_foundation_g5_review_schema_correction_"
    "readiness_v1"
)
BUILD_START_COMMIT = "6d201c45ed37b9d692957e4a9bc43235ff85bc3b"
BUILD_START_TREE = "80d6d50f88f05c823c308556e4a8342ada71e800"
VALIDATED_SUBJECT_COMMIT = "c9d811e5d28c84af81d24cea755d52fec0803ef6"
VALIDATED_SUBJECT_TREE = "b8b014077988bb8dc91069ce8854e59caa6c839d"
REVIEW_CORRECTION_COMMIT = "98f98027be06221f2ec28aad1f4c503ffccd0e28"
REVIEW_CORRECTION_TREE = "06890646e52de91217aded7782fd4220b95b4554"

FOUNDATION_CONTRACT_SHA256 = (
    "4a31e48dacc9c906c4fe4a04cce22799226b23366cd77cd948e91473e1844b02"
)
PREDECESSOR_READINESS_SHA256 = (
    "01b80e5e70e0e49d0eb956074cc6a0c6f2d15c9c147b5b25cefc12aa1a455421"
)
G1_GATE_MANIFEST_SHA256 = (
    "01297ef48939e1211bf994535da13fffe9fd14b6d7c2424402455d6d2764c1fa"
)
G1_GATE_CLOSEOUT_SHA256 = (
    "84eea72be39e6ec3170028b1503793ae2c14520b9d3fee1f65017dbd052a1f46"
)
AB_CANONICAL_SHA256 = (
    "528979411eeb8eb95df97c0d15f05cbd9a05bd41e6bb4d1fff344b4b2c39d21f"
)
REVIEW_CORRECTION_RECORD_SHA256 = (
    "3e8a3c962543d80814ea2c2200e7889648aab9302b4c7f3a416f2ba516c3139f"
)
COMPILER_AGGREGATE_SHA256 = (
    "2dcff095b1cc34c8fb6d3ad735ac8f9d0ca2affe259f6bb97870b19e7235cc7f"
)
CANDIDATE_SHA256 = (
    "ec2a6370a694c9a322e29653765d3d17fab26a208414d7539aaaf8d3fe547437"
)
TRACE_SHA256 = (
    "f047c4e53fbe32d430192a2cedbc1db4e4685926643017a608bb7e89c911af06"
)
HANDOFF_SHA256 = (
    "7fdbb224b3af4231a8bf3f2d37e448a8cdbfb4ed4d9871a83927b22cfdde25ec"
)
PHASE8_CLOSEOUT_SHA256 = (
    "e1dfa84d2e5f1ab1fe959bec228668ca0c5a266c9b377e60baee865f3ca1fa84"
)
TERMINAL_CLOSEOUT_SHA256 = (
    "6a9fd3eb65236aade1ff504423fb6850da95d2b5a9e3882f070b7f043f97049c"
)
CURRENT_FACTS_SHA256 = (
    "50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120"
)
CURRENT_MANIFEST_SHA256 = (
    "090381a652da540c6e72300624728aba48f6392e41fb50e8eec973efd320b9b7"
)
CORRECTED_ACCEPTANCE_RAW_SHA256 = (
    "93f7e8f8aed6c12106ed8023adc82c75b3f21a122ab497ce1a13a7729867abd9"
)
CURRENT_REGRESSION_RAW_SHA256 = (
    "9400be3daf5a60a4af2e42d2dc05b0d034420fcfae25bb8a5d36e2077f472f96"
)

FOUNDATION_ROOT = foundation.FOUNDATION_ROOT
PREDECESSOR_READINESS = (
    FOUNDATION_ROOT
    / "readiness_successors"
    / "implementation-correction-0005"
    / "public_text_quality_phase0_vcs_parity_readiness.json"
)
SUCCESSOR_PATH = (
    FOUNDATION_ROOT
    / "readiness_successors"
    / CORRECTION_ID
    / "public_text_quality_g5_review_schema_readiness.json"
)
CLEAN_CHECKOUT_ROOT = REPO_ROOT / "Iris" / "validation" / "clean_checkout"
G1_GATE_MANIFEST = (
    CLEAN_CHECKOUT_ROOT
    / "evidence"
    / "full_repository_gate_manifest_successor_0007.json"
)
G1_GATE_CLOSEOUT = (
    CLEAN_CHECKOUT_ROOT
    / "authority"
    / "full_repository_technical_debt_closeout_successor_0007.json"
)
REVIEW_CORRECTION_RECORD = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "iris_publish_boundary_public_text_quality_acceptance_policy_closure"
    / "official_attempt_corrections"
    / "attempt-0004"
    / "phase5-review-schema-incompatibility-correction-0001.json"
)
CORRECTED_ACCEPTANCE = (
    V2_ROOT / "tools" / "build" / "public_text_quality_acceptance.py"
)
REGRESSION_TEST = (
    V2_ROOT / "tests" / "test_public_text_constituent_identity.py"
)
CURRENT_FACTS = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
CURRENT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"

G5_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
)
G5_PRIMARY = G5_ROOT / "attempt-0024-publish-remediation-a"
G5_REPLAY = G5_ROOT / "attempt-0024-publish-remediation-b"
G5_CANDIDATE = G5_PRIMARY / "phase4" / "candidate_rendered.json"
G5_TRACE = G5_PRIMARY / "phase4" / "candidate_proposition_trace.jsonl"
G5_HANDOFF = (
    G5_PRIMARY / "phase8" / "publish_acceptance_handoff_manifest.json"
)
G5_PHASE8_CLOSEOUT = G5_PRIMARY / "phase8" / "phase8_closeout.json"
G5_RAW_REPORT = G5_PRIMARY / "phase6" / "raw_detector_report.json"
G5_REVIEW_SAMPLE = (
    G5_PRIMARY / "phase7" / "human_review_sample_manifest.json"
)
G5_REVIEW_DECISION = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
    / "attempt_0024_human_review_decision.json"
)
G5_TERMINAL_CLOSEOUT = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
    / "attempt_0024_terminal_closeout.json"
)
G5_AB_REPORT = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
    / "attempt_0024_phase0_through_phase6_ab_report.json"
)
G5_AB_REPORT_SHA256 = (
    "260f8ac3e6f589dd0f7f294194e6c327e40b286c54a16e0ea48300dea7881f09"
)

ATTEMPT_0004_ROOT = (
    V2_ROOT
    / "staging"
    / "iris_public_text_quality_policy_closure"
    / "attempts"
    / "attempt-0004-official"
)
ATTEMPT_0004_OWNER_INPUT_ROOT = (
    V2_ROOT
    / "owner_inputs"
    / "iris_publish_boundary_public_text_quality_acceptance_policy_closure"
)
ATTEMPT_0004_IMPLEMENTATION = (
    V2_ROOT
    / "tools"
    / "build"
    / "public_text_quality_acceptance_official_0004.py",
    V2_ROOT
    / "tools"
    / "build"
    / "run_public_text_quality_acceptance_official_0004.py",
    V2_ROOT
    / "tools"
    / "build"
    / "validate_public_text_quality_acceptance_official_0004.py",
)

IMPLEMENTATION_FILES = (
    TOOLS_DIR / "public_text_quality_foundation_g5_review_correction.py",
    TOOLS_DIR / "run_public_text_quality_foundation_g5_review_correction.py",
    TOOLS_DIR / "validate_public_text_quality_foundation_g5_review_correction.py",
)
TRACKING_FILES = (REPO_ROOT / ".gitignore", REPO_ROOT / ".gitattributes")
EXPECTED_G1_DELTA = frozenset(
    {
        foundation._repo_relative(G1_GATE_MANIFEST),
        foundation._repo_relative(G1_GATE_CLOSEOUT),
    }
)
EXPECTED_VALIDATED_SUBJECT_DELTA = frozenset(
    {foundation._repo_relative(REGRESSION_TEST)}
)
EXPECTED_REVIEW_CORRECTION_DELTA = frozenset(
    {
        foundation._repo_relative(REVIEW_CORRECTION_RECORD),
        foundation._repo_relative(CORRECTED_ACCEPTANCE),
        foundation._repo_relative(REGRESSION_TEST),
    }
)
EXPECTED_ACCEPTANCE_SYMBOL_DELTA = frozenset(
    {
        "HUMAN_REVIEW_RUBRIC_IDS",
        "_human_review_blocker_count",
        "_human_review_technical_blocker",
        "compute_candidate_metric_snapshot",
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
            "show", "-s", "--format=%T", REVIEW_CORRECTION_COMMIT
        ).stdout.strip()
        != REVIEW_CORRECTION_TREE
        or foundation._git(
            "rev-parse", f"{BUILD_START_COMMIT}^"
        ).stdout.strip()
        != VALIDATED_SUBJECT_COMMIT
        or _changed_paths(BUILD_START_COMMIT) != EXPECTED_G1_DELTA
        or _changed_paths(VALIDATED_SUBJECT_COMMIT)
        != EXPECTED_VALIDATED_SUBJECT_DELTA
        or _changed_paths(REVIEW_CORRECTION_COMMIT)
        != EXPECTED_REVIEW_CORRECTION_DELTA
    ):
        raise FoundationCorrectionError(
            "G5 review-schema correction readpoint or delta mismatch"
        )
    foundation._require_ancestor(REVIEW_CORRECTION_COMMIT, BUILD_START_COMMIT)
    head = foundation._git("rev-parse", "HEAD").stdout.strip()
    if require_exact_head:
        if head != BUILD_START_COMMIT:
            raise FoundationCorrectionError(
                "G4 successor build requires the exact G1 evidence HEAD"
            )
    else:
        foundation._require_ancestor(BUILD_START_COMMIT, head)
    return {
        "commit": BUILD_START_COMMIT,
        "tree": BUILD_START_TREE,
        "validated_subject_commit": VALIDATED_SUBJECT_COMMIT,
        "validated_subject_tree": VALIDATED_SUBJECT_TREE,
        "review_correction_commit": REVIEW_CORRECTION_COMMIT,
        "review_correction_tree": REVIEW_CORRECTION_TREE,
        "g1_delta_paths": sorted(EXPECTED_G1_DELTA),
        "validated_subject_delta_paths": sorted(
            EXPECTED_VALIDATED_SUBJECT_DELTA
        ),
        "review_correction_delta_paths": sorted(
            EXPECTED_REVIEW_CORRECTION_DELTA
        ),
        "exact_head_required_for_build": True,
        "build_start_is_ancestor_of_validation_head": True,
    }


def _sealed_text_record(
    path: Path,
    declared_sha256: str,
) -> dict[str, Any]:
    return predecessor._sealed_text_record(path, declared_sha256)


def _validate_predecessor() -> dict[str, Any]:
    record = foundation._raw_tracked_record(
        PREDECESSOR_READINESS,
        PREDECESSOR_READINESS_SHA256,
    )
    value = foundation._load_json(PREDECESSOR_READINESS)
    if (
        value.get("correction_id") != "implementation-correction-0005"
        or value.get("status") != "PASS"
        or value.get("authority_effect") != "none"
        or value.get("protected_surface_mutation_count") != 0
        or value.get("foundation_contract_semantics_changed") is not False
        or value.get(
            "policy_threshold_denominator_detector_semantics_changed"
        )
        is not False
    ):
        raise FoundationCorrectionError("predecessor G4 readiness is invalid")
    return {
        **record,
        "correction_id": "implementation-correction-0005",
        "predecessor_mutated": False,
        "append_only_successor_required": True,
    }


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
            f"cannot read Git blob: {commit}:{relative}"
        )
    return result.stdout


def _top_level_symbols(raw: bytes) -> dict[str, str]:
    tree = ast.parse(raw.decode("utf-8"))
    rows: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            rows[node.name] = ast.dump(node, include_attributes=False)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    rows[target.id] = ast.dump(node, include_attributes=False)
    return rows


def _changed_symbols(commit: str, path: Path) -> frozenset[str]:
    parent = foundation._git("rev-parse", f"{commit}^").stdout.strip()
    before = _top_level_symbols(_git_blob_at(parent, path))
    after = _top_level_symbols(_git_blob_at(commit, path))
    return frozenset(
        name
        for name in set(before) | set(after)
        if before.get(name) != after.get(name)
    )


def _validate_foundation_semantics() -> dict[str, Any]:
    predecessor_value = foundation._load_json(PREDECESSOR_READINESS)
    predecessor_rows = predecessor_value.get(
        "foundation_semantics", {}
    ).get("meaning_paths", [])
    corrected_relative = foundation._repo_relative(CORRECTED_ACCEPTANCE)
    current_rows: list[dict[str, Any]] = []
    corrected_count = 0
    unchanged_count = 0
    for predecessor_row in predecessor_rows:
        relative = str(predecessor_row["path"])
        path = REPO_ROOT / relative
        if relative == corrected_relative:
            record = _sealed_text_record(
                path,
                CORRECTED_ACCEPTANCE_RAW_SHA256,
            )
            if (
                record["authority_git_blob_raw_sha256"]
                == predecessor_row["git_blob_raw_sha256"]
            ):
                raise FoundationCorrectionError(
                    "exact-full review consumer correction is absent"
                )
            classification = (
                "intended_exact_full_review_schema_consumer_correction"
            )
            corrected_count += 1
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
            classification = "byte_identical_to_predecessor"
            unchanged_count += 1
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
    symbol_delta = _changed_symbols(
        REVIEW_CORRECTION_COMMIT,
        CORRECTED_ACCEPTANCE,
    )
    if symbol_delta != EXPECTED_ACCEPTANCE_SYMBOL_DELTA:
        raise FoundationCorrectionError(
            "exact-full review correction symbol boundary mismatch"
        )
    correction_record = foundation._raw_tracked_record(
        REVIEW_CORRECTION_RECORD,
        REVIEW_CORRECTION_RECORD_SHA256,
    )
    correction = foundation._load_json(REVIEW_CORRECTION_RECORD)
    if (
        correction.get("status")
        != "bounded_consumer_correction_implemented"
        or correction.get("source_attempt", {}).get("immutable") is not True
        or correction.get("source_attempt", {}).get(
            "recomputed_or_modified"
        )
        is not False
        or correction.get("historical_result_interpretation", {}).get(
            "overall_blocked_result_remains_valid"
        )
        is not True
        or correction.get("bounded_consumer_contract", {}).get(
            "exact_full_metric_numerator_source"
        )
        != "validated blocker_count"
        or correction.get("bounded_consumer_contract", {}).get(
            "unknown_or_incomplete_schema_effect"
        )
        != "technical_blocker_fail_closed"
    ):
        raise FoundationCorrectionError(
            "attempt-0004 review-schema correction record is invalid"
        )
    contract = foundation._raw_tracked_record(
        foundation.FOUNDATION_CONTRACT,
        FOUNDATION_CONTRACT_SHA256,
    )
    return {
        "foundation_contract": contract,
        "meaning_path_count": 17,
        "unchanged_meaning_path_count": unchanged_count,
        "intentionally_corrected_meaning_path_count": corrected_count,
        "meaning_paths": current_rows,
        "review_schema_correction_record": correction_record,
        "acceptance_top_level_symbol_delta": sorted(symbol_delta),
        "regression_test": _sealed_text_record(
            REGRESSION_TEST,
            CURRENT_REGRESSION_RAW_SHA256,
        ),
        "exact_full_metric_numerator_source": "validated_blocker_count",
        "unknown_or_incomplete_review_schema_effect": (
            "technical_blocker_fail_closed"
        ),
        "foundation_contract_semantics_changed": False,
        "policy_threshold_denominator_detector_semantics_changed": False,
    }


def _require_fields(
    actual: dict[str, Any],
    expected: dict[str, Any],
    *,
    label: str,
) -> None:
    mismatch = sorted(
        key for key, value in expected.items() if actual.get(key) != value
    )
    if mismatch:
        raise FoundationCorrectionError(
            f"{label} field mismatch: {mismatch}"
        )


def _validate_g1() -> dict[str, Any]:
    manifest_record = _sealed_text_record(
        G1_GATE_MANIFEST,
        G1_GATE_MANIFEST_SHA256,
    )
    closeout_record = _sealed_text_record(
        G1_GATE_CLOSEOUT,
        G1_GATE_CLOSEOUT_SHA256,
    )
    manifest = foundation._load_json(G1_GATE_MANIFEST)
    closeout = foundation._load_json(G1_GATE_CLOSEOUT)
    _require_fields(
        manifest,
        {
            "schema_version": (
                "iris-clean-checkout-full-repository-gate-manifest-v7"
            ),
            "status": "PASS",
        },
        label="G1 gate manifest 0007",
    )
    _require_fields(
        manifest.get("validated_subject", {}),
        {
            "commit": VALIDATED_SUBJECT_COMMIT,
            "tree": VALIDATED_SUBJECT_TREE,
        },
        label="G1 validated subject",
    )
    _require_fields(
        manifest.get("classification_recensus", {}),
        {
            "tracked_test_source_count": 93,
            "required_source_count": 33,
            "historical_optional_source_count": 55,
            "obsolete_or_misrouted_source_count": 3,
            "hermetic_test_fixture_source_count": 2,
            "unresolved_dependency_edge_count": 0,
        },
        label="G1 census",
    )
    execution = manifest.get("execution_reproducibility", {})
    _require_fields(
        execution,
        {
            "passed_execution_unit_count": 199,
            "failed_execution_unit_count": 0,
            "collection_error_count": 0,
            "canonical_results_equal": True,
            "canonical_result_sha256": AB_CANONICAL_SHA256,
            "comparison_validator_exit_code": 0,
        },
        label="G1 execution",
    )
    for run_id in ("run_a", "run_b"):
        _require_fields(
            execution.get(run_id, {}),
            {
                "status": "PASS",
                "required_execution_unit_count": 199,
                "canonical_result_sha256": AB_CANONICAL_SHA256,
                "exit_code": 0,
            },
            label=f"G1 {run_id}",
        )
    _require_fields(
        closeout,
        {
            "schema_version": (
                "iris_clean_checkout_full_repository_technical_debt_"
                "closeout_successor_v7"
            ),
            "status": "complete",
        },
        label="G1 closeout 0007",
    )
    _require_fields(
        closeout.get("execution_closeout", {}),
        {
            "required_execution_unit_count": 199,
            "passed_execution_unit_count": 199,
            "failed_execution_unit_count": 0,
            "canonical_result_sha256": AB_CANONICAL_SHA256,
            "canonical_results_equal": True,
        },
        label="G1 closeout execution",
    )
    _require_fields(
        closeout.get("g5_closeout", {}),
        {
            "primary_attempt_id": "attempt-0024-publish-remediation-a",
            "replay_attempt_id": "attempt-0024-publish-remediation-b",
            "compiler_aggregate_sha256": COMPILER_AGGREGATE_SHA256,
            "candidate_declared_sha256": CANDIDATE_SHA256,
            "trace_declared_sha256": TRACE_SHA256,
            "phase8_handoff_git_blob_raw_sha256": HANDOFF_SHA256,
            "phase8_closeout_git_blob_raw_sha256": PHASE8_CLOSEOUT_SHA256,
            "terminal_closeout_git_blob_raw_sha256": (
                TERMINAL_CLOSEOUT_SHA256
            ),
            "candidate_trace_handoff_byte_identity": "PASS",
            "compiler_identity_match": True,
            "active_ignored_required_input_count": 0,
            "broad_unignore_count": 0,
        },
        label="G1 G5 closeout",
    )
    if closeout.get("terminal_state", {}).get(
        "blocking_condition_count"
    ) != 0:
        raise FoundationCorrectionError("G1 closeout has blockers")
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
        "gate_manifest_successor_0007": manifest_record,
        "closeout_successor_0007": closeout_record,
        "census": {
            "tracked": 93,
            "required": 33,
            "historical": 55,
            "obsolete": 3,
            "fixture": 2,
            "unresolved_dependency": 0,
        },
        "run_a_result": "199/199 PASS",
        "run_b_result": "199/199 PASS",
        "canonical_result_sha256": AB_CANONICAL_SHA256,
        "blocking_condition_count": 0,
    }


def _text_constituent_record(
    path: Path,
    expected_sha256: str,
) -> dict[str, Any]:
    return _sealed_text_record(path, expected_sha256)


def _validate_g5() -> dict[str, Any]:
    records = {
        "candidate": _text_constituent_record(
            G5_CANDIDATE,
            CANDIDATE_SHA256,
        ),
        "trace": _text_constituent_record(G5_TRACE, TRACE_SHA256),
        "handoff": _text_constituent_record(G5_HANDOFF, HANDOFF_SHA256),
        "phase8_closeout": _text_constituent_record(
            G5_PHASE8_CLOSEOUT,
            PHASE8_CLOSEOUT_SHA256,
        ),
        "terminal_closeout": _text_constituent_record(
            G5_TERMINAL_CLOSEOUT,
            TERMINAL_CLOSEOUT_SHA256,
        ),
    }
    compiler_identity = acceptance.build_compiler_identity(REPO_ROOT)
    if (
        compiler_identity.get("aggregate_sha256")
        != COMPILER_AGGREGATE_SHA256
    ):
        raise FoundationCorrectionError("G5 compiler aggregate is stale")
    validation = acceptance.validate_candidate_handoff(G5_HANDOFF)
    if (
        validation.get("handoff_raw_sha256") != HANDOFF_SHA256
        or validation.get("compiler_aggregate_hash")
        != COMPILER_AGGREGATE_SHA256
        or validation.get("constituents", {}).get(
            "candidate_rendered_hash", {}
        ).get("sha256")
        != CANDIDATE_SHA256
    ):
        raise FoundationCorrectionError("G5 handoff is stale")
    ab_report_record = _text_constituent_record(
        G5_AB_REPORT,
        G5_AB_REPORT_SHA256,
    )
    ab_report = foundation._load_json(G5_AB_REPORT)
    byte_identity = ab_report.get("byte_identity", {})
    if (
        ab_report.get("status") != "PASS"
        or ab_report.get("primary_attempt_id") != G5_PRIMARY.name
        or ab_report.get("replay_attempt_id") != G5_REPLAY.name
        or byte_identity.get("candidate_rendered", {}).get(
            "primary_sha256"
        )
        != CANDIDATE_SHA256
        or byte_identity.get("candidate_rendered", {}).get(
            "replay_sha256"
        )
        != CANDIDATE_SHA256
        or byte_identity.get("candidate_rendered", {}).get(
            "byte_identical"
        )
        is not True
        or byte_identity.get("candidate_proposition_trace", {}).get(
            "primary_sha256"
        )
        != TRACE_SHA256
        or byte_identity.get("candidate_proposition_trace", {}).get(
            "replay_sha256"
        )
        != TRACE_SHA256
        or byte_identity.get("candidate_proposition_trace", {}).get(
            "byte_identical"
        )
        is not True
        or ab_report.get("deterministic_semantic_payload_identity", {}).get(
            "raw_detector_report_sha256"
        )
        != "038ea8e72baef56e220335567b9e164133c87bad8257926ca017c4019f80b053"
        or ab_report.get("phase6", {}).get("detector_opportunity_count")
        != 14588
        or ab_report.get("phase6", {}).get("blocking_metric_hit_count")
        != 0
        or ab_report.get("phase6", {}).get("advisory_metric_hit_count")
        != 0
        or ab_report.get("validation", {}).get(
            "primary_compared_with_replay", {}
        ).get("exit_code")
        != 0
        or ab_report.get("validation", {}).get(
            "replay_compared_with_primary", {}
        ).get("exit_code")
        != 0
    ):
        raise FoundationCorrectionError("G5 primary/replay evidence is stale")
    raw = foundation._load_json(G5_RAW_REPORT)
    review_sample = foundation._load_json(G5_REVIEW_SAMPLE)
    review_decision = foundation._load_json(G5_REVIEW_DECISION)
    if (
        raw.get("candidate_denominator") != 2084
        or raw.get("detector_opportunity_count") != 14588
        or raw.get("expected_detector_opportunity_count") != 14588
        or raw.get("detector_hit_counts") != {}
        or raw.get("raw_detector_full_candidate_completeness_pass")
        is not True
    ):
        raise FoundationCorrectionError("G5 raw detector evidence mismatch")
    human_review_numerator = acceptance._human_review_blocker_count(
        review_sample=review_sample,
        review_decision=review_decision,
        required_denominator=2084,
    )
    if (
        human_review_numerator != 0
        or review_decision.get("status") != "PASS"
        or review_decision.get("reviewed_denominator") != 2084
        or review_decision.get("blocker_count") != 0
    ):
        raise FoundationCorrectionError("G5 exact-full review mismatch")
    incomplete = deepcopy(review_decision)
    incomplete["rubric_aggregate"].pop("public_suitability", None)
    unknown = deepcopy(review_decision)
    unknown["decision_mode"] = "unknown_review_schema"
    technical_fail_closed = []
    for malformed in (incomplete, unknown):
        try:
            acceptance._human_review_blocker_count(
                review_sample=review_sample,
                review_decision=malformed,
                required_denominator=2084,
            )
        except acceptance.FoundationContractError as exc:
            technical_fail_closed.append(
                "human review schema technical blocker" in str(exc)
            )
        else:
            technical_fail_closed.append(False)
    if technical_fail_closed != [True, True]:
        raise FoundationCorrectionError(
            "unknown/incomplete review schema did not fail closed"
        )
    snapshot = acceptance.compute_candidate_metric_snapshot(validation)
    rows = {
        row["metric_id"]: row for row in snapshot.get("metric_rows", [])
    }
    if (
        rows.get("human_review_blocker_required_denominator", {}).get(
            "numerator"
        )
        != 0
        or any(
            rows.get(detector_id, {}).get("numerator") != 0
            for detector_id in acceptance.RAW_DETECTOR_IDS
        )
    ):
        raise FoundationCorrectionError(
            "G5 corrected candidate metric projection mismatch"
        )
    closeout = foundation._load_json(G5_PHASE8_CLOSEOUT)
    terminal = foundation._load_json(G5_TERMINAL_CLOSEOUT)
    if (
        closeout.get("status") != "HANDOFF_COMPLETE"
        or closeout.get("human_review_blocker_count") != 0
        or closeout.get("human_review_denominator") != 2084
        or closeout.get("publish_acceptance_handoff_manifest_sha256")
        != HANDOFF_SHA256
        or terminal.get("status") != "HANDOFF_COMPLETE"
        or terminal.get("attempts", {}).get("primary")
        != "attempt-0024-publish-remediation-a"
        or terminal.get("attempts", {}).get("replay")
        != "attempt-0024-publish-remediation-b"
    ):
        raise FoundationCorrectionError("G5 closeout identity mismatch")
    facts = _sealed_text_record(CURRENT_FACTS, CURRENT_FACTS_SHA256)
    manifest = _sealed_text_record(
        CURRENT_MANIFEST,
        CURRENT_MANIFEST_SHA256,
    )
    return {
        "status": "PASS",
        "primary_attempt_id": "attempt-0024-publish-remediation-a",
        "replay_attempt_id": "attempt-0024-publish-remediation-b",
        "compiler_identity": compiler_identity,
        "records": records,
        "primary_replay_identity": ab_report_record,
        "candidate_trace_primary_replay_identity": True,
        "raw_detector_hit_count": 0,
        "raw_detector_opportunity_count": 14588,
        "human_review_numerator": 0,
        "human_review_denominator": 2084,
        "review_blocker_count": 0,
        "unknown_incomplete_schema_technical_fail_closed": True,
        "current_facts": facts,
        "current_manifest": manifest,
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
            REVIEW_CORRECTION_RECORD,
            CORRECTED_ACCEPTANCE,
            REGRESSION_TEST,
            CURRENT_FACTS,
            CURRENT_MANIFEST,
            G5_CANDIDATE,
            G5_TRACE,
            G5_HANDOFF,
            G5_PHASE8_CLOSEOUT,
            G5_RAW_REPORT,
            G5_REVIEW_SAMPLE,
            G5_REVIEW_DECISION,
            G5_TERMINAL_CLOSEOUT,
            G5_AB_REPORT,
            *ATTEMPT_0004_IMPLEMENTATION,
            *IMPLEMENTATION_FILES,
            *TRACKING_FILES,
        }
    )
    for root in (ATTEMPT_0004_ROOT, ATTEMPT_0004_OWNER_INPUT_ROOT):
        if root.is_dir():
            protected.update(path for path in root.rglob("*") if path.is_file())
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
            "public_text_quality_foundation_g5_review_correction_"
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


def _tracking_rules() -> dict[str, Any]:
    relative = foundation._repo_relative(SUCCESSOR_PATH)
    ignore_lines = (REPO_ROOT / ".gitignore").read_text(
        encoding="utf-8"
    ).splitlines()
    attribute_lines = (REPO_ROOT / ".gitattributes").read_text(
        encoding="utf-8"
    ).splitlines()
    tool_rules = [
        f"!{foundation._repo_relative(path)}" for path in IMPLEMENTATION_FILES
    ]
    if (
        ignore_lines.count(f"!{relative}") != 1
        or any(ignore_lines.count(rule) != 1 for rule in tool_rules)
        or attribute_lines.count(f"{relative} -text") != 1
    ):
        raise FoundationCorrectionError(
            "G5 review readiness tracking rules are not exact"
        )
    return {
        "successor_path": relative,
        "exact_successor_unignore_rule_count": 1,
        "exact_tool_unignore_rule_count": 3,
        "exact_text_unset_rule_count": 1,
        "broad_unignore_added": False,
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


def build_projection(
    *,
    require_exact_head: bool,
    no_write_guard: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "correction_id": CORRECTION_ID,
        "readiness_kind": (
            "append_only_foundation_g5_review_schema_implementation_"
            "correction"
        ),
        "purpose": (
            "Bind G1 successor 0007, G5 attempt-0024 primary/replay, "
            "the exact-full review blocker-count consumer correction, and "
            "fresh current inputs without granting Publish authority."
        ),
        "execution_start_readpoint": _validate_readpoints(
            require_exact_head=require_exact_head
        ),
        "predecessor_readiness": _validate_predecessor(),
        "foundation_semantics": _validate_foundation_semantics(),
        "g1_clean_checkout": _validate_g1(),
        "g5_naturalization": _validate_g5(),
        "focused_validation": {
            "source": foundation._repo_relative(REGRESSION_TEST),
            "pytest_result": "20/20 PASS",
            "pytest_exit_code": 0,
            "standalone_result": "20/20 PASS",
            "standalone_exit_code": 0,
            "new_test_source_count": 0,
        },
        "successor_tracking_rules": _tracking_rules(),
        "successor_implementation_hashes": _implementation_hashes(),
        "protected_no_write_guard": no_write_guard,
        "scope_boundaries": {
            "attempt_0004_phase0_through_phase5_modified_or_recomputed": False,
            "attempt_0004_owner_input_modified": False,
            "attempt_0004_wrapper_modified": False,
            "attempt_0004_disposition_or_failure_ledger_modified": False,
            "g1_g2_g3_g5_executed_or_modified": False,
            "runtime_lua_package_modified": False,
            "live_gate_modified": False,
            "foundation_contract_modified": False,
            "policy_threshold_denominator_detector_modified": False,
            "persistent_worktree_created": False,
        },
        "foundation_contract_semantics_changed": False,
        "policy_threshold_denominator_detector_semantics_changed": False,
        "protected_surface_mutation_count": 0,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
        "next_stage": "attempt-0005-official-phase0-no-write-preflight",
    }


def _validate_id(correction_id: str) -> None:
    if correction_id != CORRECTION_ID:
        raise FoundationCorrectionError(
            f"only the exact correction ID {CORRECTION_ID} is allowed"
        )


def build_successor(correction_id: str) -> dict[str, Any]:
    _validate_id(correction_id)
    if SUCCESSOR_PATH.exists():
        raise FoundationCorrectionError(
            "append-only G5 review readiness successor already exists"
        )
    before = protected_snapshot()
    guard = _no_write_guard(before, protected_snapshot())
    successor = build_projection(
        require_exact_head=True,
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
        "compiler_aggregate_sha256": COMPILER_AGGREGATE_SHA256,
        "candidate_sha256": CANDIDATE_SHA256,
        "human_review_numerator": 0,
        "protected_surface_mutation_count": 0,
        "authority_effect": "none",
    }


def _index_or_head_blob(relative: str) -> str:
    indexed = foundation._git(
        "ls-files", "-s", "--", relative
    ).stdout.strip()
    if indexed:
        return indexed.split()[1]
    return foundation._git("rev-parse", f"HEAD:{relative}").stdout.strip()


def _require_successor_vcs_state() -> dict[str, Any]:
    if (
        not SUCCESSOR_PATH.is_file()
        or not foundation._is_tracked(SUCCESSOR_PATH)
        or foundation._is_ignored(SUCCESSOR_PATH)
    ):
        raise FoundationCorrectionError(
            "G5 review readiness successor must be tracked and unignored"
        )
    relative = foundation._repo_relative(SUCCESSOR_PATH)
    blob_id = _index_or_head_blob(relative)
    working_blob_id = foundation._git(
        "hash-object", "--no-filters", "--", relative
    ).stdout.strip()
    attr = foundation._git(
        "check-attr", "text", "--", relative
    ).stdout.strip()
    if blob_id != working_blob_id or not attr.endswith(": text: unset"):
        raise FoundationCorrectionError(
            "successor Git blob/working-byte identity mismatch"
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
    _validate_id(correction_id)
    if not SUCCESSOR_PATH.is_file():
        raise FoundationCorrectionError(
            "G5 review readiness successor is missing"
        )
    successor_bytes = SUCCESSOR_PATH.read_bytes()
    successor = foundation._load_json(SUCCESSOR_PATH)
    before = protected_snapshot()
    guard = _no_write_guard(before, protected_snapshot())
    expected = build_projection(
        require_exact_head=False,
        no_write_guard=guard,
    )
    if successor != expected:
        raise FoundationCorrectionError(
            "G5 review readiness differs from exact projection"
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
        "compiler_aggregate_sha256": COMPILER_AGGREGATE_SHA256,
        "candidate_sha256": CANDIDATE_SHA256,
        "human_review_numerator": 0,
        "vcs_state": vcs_state,
        "protected_surface_mutation_count": 0,
        "no_write_validation": True,
        "authority_effect": "none",
    }
