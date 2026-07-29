from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.build import naturalization_compiler_identity as compiler_identity
    from tools.build import public_text_quality_acceptance as publish_consumer
    from tools.build import run_dvf_3_3_korean_prose_identity_v2_attempt as base
else:
    from . import naturalization_compiler_identity as compiler_identity
    from . import public_text_quality_acceptance as publish_consumer
    from . import run_dvf_3_3_korean_prose_identity_v2_attempt as base


producer = base.producer
validator = base.validator

START_COMMIT = "98f98027be06221f2ec28aad1f4c503ffccd0e28"
START_TREE = "06890646e52de91217aded7782fd4220b95b4554"
COMPILER_CORRECTION_COMMIT = "2b05eea9651a6b2593263d40955dfdfd4cc26a66"
COMPILER_CORRECTION_TREE = "82be740ec92d8d2300d5047444156a17609e9903"
PRIMARY_ATTEMPT_ID = "attempt-0024-publish-remediation-a"
REPLAY_ATTEMPT_ID = "attempt-0024-publish-remediation-b"
CURRENT_COMPILER_AGGREGATE_SHA256 = (
    "2dcff095b1cc34c8fb6d3ad735ac8f9d0ca2affe259f6bb97870b19e7235cc7f"
)
PREDECESSOR_COMPILER_AGGREGATE_SHA256 = (
    "aa88ee878cfb570b8278b40e62c560f093dc6ffdc363f06ed7133352d635c647"
)
COMPILER_IDENTITY_ALGORITHM_ID = (
    "naturalization_compiler_identity_sha256_lf_normalized_ordered_paths_v2"
)
CORRECTION_RECORD_SHA256 = (
    "3e8a3c962543d80814ea2c2200e7889648aab9302b4c7f3a416f2ba516c3139f"
)
BOUNDED_PROJECTION_REPORT_SHA256 = (
    "6212d1ab7fd4626db4aa07da6bcef1ff59a298ad8ec3b604689d733fdebc4e19"
)
OFFICIAL_DISPOSITION_SHA256 = (
    "50e342e91fc453939828c2fe9350c501dedc30aa6cd4fa35562c15b3091f2063"
)
OFFICIAL_FAILURE_LEDGER_SHA256 = (
    "abf0722fe97c35554282d63a535f58352c4552be4ce94229c93a5e7768870993"
)

CORRECTION_RECORD = (
    producer.REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "iris_publish_boundary_public_text_quality_acceptance_policy_closure"
    / "official_attempt_corrections"
    / "attempt-0004"
    / "phase5-review-schema-incompatibility-correction-0001.json"
)
OFFICIAL_PHASE5 = (
    producer.V2_ROOT
    / "staging"
    / "iris_publish_boundary_public_text_quality_acceptance_policy_closure"
    / "attempts"
    / "attempt-0004-official"
    / "phase5"
)
OFFICIAL_DISPOSITION = OFFICIAL_PHASE5 / "evaluation_subject_disposition.json"
OFFICIAL_FAILURE_LEDGER = OFFICIAL_PHASE5 / "naturalization_failure_ledger.json"
BOUNDED_ROOT = (
    producer.DURABLE_ROOT
    / "compiler_corrections"
    / "publish_remediation_0001"
)
BOUNDED_PROJECTION_REPORT = BOUNDED_ROOT / "bounded_projection_report.json"
DISPOSABLE_PROJECTION_ROOT = (
    producer.DEFAULT_ATTEMPT_PARENT
    / "projections"
    / "publish-remediation-correction-0001"
)
DISPOSABLE_CANDIDATE = (
    DISPOSABLE_PROJECTION_ROOT / "candidate_rendered.json"
)
DISPOSABLE_TRACE = (
    DISPOSABLE_PROJECTION_ROOT / "candidate_proposition_trace.jsonl"
)
HUMAN_REVIEW_DECISION = (
    producer.DURABLE_ROOT / "attempt_0024_human_review_decision.json"
)
ORCHESTRATOR_PATH = Path(__file__).resolve()

CORRECTION_COMMIT_PATHS = {
    (
        "Iris/_docs/round3/dvf_3_3_korean_prose_naturalization_public_text_"
        "rewrite_closure/compiler_corrections/publish_remediation_0001/"
        "bounded_projection_changed_items.jsonl"
    ),
    (
        "Iris/_docs/round3/dvf_3_3_korean_prose_naturalization_public_text_"
        "rewrite_closure/compiler_corrections/publish_remediation_0001/"
        "bounded_projection_classification.jsonl"
    ),
    (
        "Iris/_docs/round3/dvf_3_3_korean_prose_naturalization_public_text_"
        "rewrite_closure/compiler_corrections/publish_remediation_0001/"
        "bounded_projection_report.json"
    ),
    "Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_compiler.py",
    "Iris/build/description/v2/tools/build/compose_layer3_identity.py",
    (
        "Iris/build/description/v2/tools/build/"
        "project_dvf_3_3_publish_remediation.py"
    ),
}


class PublishRemediationAttemptError(base.IdentityV2AttemptError):
    pass


def git(*args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=producer.REPO_ROOT,
        capture_output=True,
        check=False,
        text=not binary,
    )
    if result.returncode != 0:
        raise PublishRemediationAttemptError(
            f"git command failed ({result.returncode}): {' '.join(args)}"
        )
    return result.stdout


def git_is_ancestor(commit: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=producer.REPO_ROOT,
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )


def current_identity_from_correction_commit() -> dict[str, Any]:
    contents = {
        relative: git(
            "show",
            f"{COMPILER_CORRECTION_COMMIT}:{relative}",
            binary=True,
        )
        for relative in compiler_identity.COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER
    }
    return compiler_identity.build_compiler_identity_from_bytes(contents)


def actual_identity_input_field_count(evidence: dict[str, Any]) -> int:
    forbidden = {"absolute_path", "mtime", "worktree_location", "host_metadata"}
    return sum(
        key in forbidden
        for row in evidence.get("ordered_files", [])
        if isinstance(row, dict)
        for key in row
    ) + sum(
        key in forbidden
        for key in evidence
        if key != "excluded_identity_inputs"
    )


def build_publish_remediation_identity_binding_report() -> dict[str, Any]:
    required = (
        CORRECTION_RECORD,
        OFFICIAL_DISPOSITION,
        OFFICIAL_FAILURE_LEDGER,
        BOUNDED_PROJECTION_REPORT,
        base.FOUNDATION_IMPLEMENTATION_READINESS,
        producer.FOUNDATION_CONTRACT,
        producer.FOUNDATION_READINESS_CURRENT_INPUT_REBIND,
        base.IDENTITY_CORRECTION_CONTRACT,
        base.IDENTITY_HELPER,
        producer.FACTS_PATH,
        producer.INPUT_MANIFEST,
        producer.REGISTRY_ADOPTION_RECEIPT,
        producer.REGISTRY_CORRECTION_TERMINAL_SEAL,
        producer.REGISTRY_NATURALIZATION_HANDOFF,
    )
    missing = [
        base.repo_relative(path) for path in required if not path.is_file()
    ]
    if missing:
        raise PublishRemediationAttemptError(
            f"missing publish-remediation input: {missing}"
        )

    readiness = base._BASE_LOAD_JSON(
        base.FOUNDATION_IMPLEMENTATION_READINESS
    )
    bounded = base._BASE_LOAD_JSON(BOUNDED_PROJECTION_REPORT)
    correction_record = base._BASE_LOAD_JSON(CORRECTION_RECORD)
    evidence = compiler_identity.build_compiler_identity(producer.REPO_ROOT)
    producer_evidence = producer.implementation_identity()
    consumer_evidence = publish_consumer.build_compiler_identity(
        publish_consumer.REPO_ROOT
    )
    committed_evidence = current_identity_from_correction_commit()
    variants = base.line_ending_variant_identities()
    variant_aggregates = {
        name: value.get("aggregate_sha256")
        for name, value in variants.items()
    }
    correction_paths = {
        line.strip()
        for line in str(
            git(
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                COMPILER_CORRECTION_COMMIT,
            )
        ).splitlines()
        if line.strip()
    }
    foundation_paths = (
        base.FOUNDATION_IMPLEMENTATION_READINESS,
        producer.FOUNDATION_CONTRACT,
        producer.FOUNDATION_READINESS_CURRENT_INPUT_REBIND,
    )
    foundation_diff = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            f"{START_COMMIT}..HEAD",
            "--",
            *(base.repo_relative(path) for path in foundation_paths),
        ],
        cwd=producer.REPO_ROOT,
        capture_output=True,
        check=False,
    )
    identity_input_count = actual_identity_input_field_count(evidence)
    correction = readiness.get("compiler_identity_correction", {})
    checks = {
        "exact_start_commit_tree_match": (
            str(git("rev-parse", f"{START_COMMIT}^{{tree}}")).strip()
            == START_TREE
        ),
        "exact_start_commit_is_correction_parent": (
            str(git("show", "-s", "--format=%P", COMPILER_CORRECTION_COMMIT))
            .strip()
            == START_COMMIT
        ),
        "compiler_correction_commit_tree_match": (
            str(
                git(
                    "show",
                    "-s",
                    "--format=%T",
                    COMPILER_CORRECTION_COMMIT,
                )
            ).strip()
            == COMPILER_CORRECTION_TREE
        ),
        "compiler_correction_commit_is_ancestor": git_is_ancestor(
            COMPILER_CORRECTION_COMMIT
        ),
        "compiler_correction_path_set_exact": (
            correction_paths == CORRECTION_COMMIT_PATHS
        ),
        "correction_record_sha256_match": (
            base.sha256_file(CORRECTION_RECORD) == CORRECTION_RECORD_SHA256
        ),
        "official_disposition_immutable": (
            base.sha256_file(OFFICIAL_DISPOSITION)
            == OFFICIAL_DISPOSITION_SHA256
        ),
        "official_failure_ledger_immutable": (
            base.sha256_file(OFFICIAL_FAILURE_LEDGER)
            == OFFICIAL_FAILURE_LEDGER_SHA256
        ),
        "correction_record_interpretation_match": (
            correction_record.get("record_mode") == "append_only"
            and correction_record.get("status")
            == "bounded_consumer_correction_implemented"
            and correction_record.get("historical_result_interpretation", {})
            .get("misclassified_human_review_finding", {})
            .get("naturalization_remediation_target")
            is False
        ),
        "bounded_projection_report_sha256_match": (
            base.sha256_file(BOUNDED_PROJECTION_REPORT)
            == BOUNDED_PROJECTION_REPORT_SHA256
        ),
        "bounded_projection_pass": (
            bounded.get("status") == "PASS"
            and bounded.get("failed_checks") == []
            and bounded.get("changed_item_count") == 676
            and all(bounded.get("checks", {}).values())
        ),
        "bounded_detector_after_all_zero": all(
            value == 0
            for value in bounded.get("detector_after", {}).values()
        ),
        "bounded_semantic_structural_regression_zero": (
            bounded.get("source_proposition_regression_count") == 0
            and bounded.get("structural_satisfaction_regression_count") == 0
            and bounded.get("unexpected_changed_item_count") == 0
            and bounded.get("compiler_invalid_count") == 0
        ),
        "facts_sha256_match": (
            base.sha256_file(producer.FACTS_PATH)
            == base.EXPECTED_FACTS_SHA256
        ),
        "manifest_sha256_match": (
            base.sha256_file(producer.INPUT_MANIFEST)
            == base.EXPECTED_MANIFEST_SHA256
        ),
        "g3_receipt_sha256_match": (
            base.sha256_file(producer.REGISTRY_ADOPTION_RECEIPT)
            == base.EXPECTED_G3_RECEIPT_SHA256
        ),
        "g3_terminal_seal_sha256_match": (
            base.sha256_file(producer.REGISTRY_CORRECTION_TERMINAL_SEAL)
            == base.EXPECTED_G3_TERMINAL_SEAL_SHA256
        ),
        "g3_handoff_sha256_match": (
            base.sha256_file(producer.REGISTRY_NATURALIZATION_HANDOFF)
            == base.EXPECTED_G3_HANDOFF_SHA256
        ),
        "foundation_files_unchanged": foundation_diff.returncode == 0,
        "foundation_implementation_readiness_sha256_match": (
            base.sha256_file(base.FOUNDATION_IMPLEMENTATION_READINESS)
            == base.EXPECTED_IMPLEMENTATION_READINESS_SHA256
        ),
        "foundation_contract_sha256_match": (
            base.sha256_file(producer.FOUNDATION_CONTRACT)
            == base.EXPECTED_FOUNDATION_CONTRACT_SHA256
        ),
        "predecessor_readiness_sha256_match": (
            base.sha256_file(
                producer.FOUNDATION_READINESS_CURRENT_INPUT_REBIND
            )
            == base.EXPECTED_PREDECESSOR_READINESS_SHA256
        ),
        "predecessor_identity_claim_preserved": (
            correction.get("compiler_aggregate_sha256")
            == PREDECESSOR_COMPILER_AGGREGATE_SHA256
            and correction.get("algorithm_id")
            == COMPILER_IDENTITY_ALGORITHM_ID
        ),
        "current_identity_algorithm_match": (
            evidence.get("algorithm_id")
            == COMPILER_IDENTITY_ALGORITHM_ID
        ),
        "current_identity_aggregate_match": (
            evidence.get("aggregate_sha256")
            == CURRENT_COMPILER_AGGREGATE_SHA256
        ),
        "ordered_nine_path_evidence_present": (
            len(evidence.get("ordered_files", [])) == 9
            and len(evidence.get("path_order", [])) == 9
            and all(
                isinstance(row, dict)
                and len(str(row.get("canonical_sha256", ""))) == 64
                for row in evidence.get("ordered_files", [])
            )
        ),
        "producer_publish_consumer_recomputation_match": (
            producer_evidence == consumer_evidence == evidence
        ),
        "lf_crlf_lone_cr_identity_equal": (
            set(variant_aggregates.values())
            == {CURRENT_COMPILER_AGGREGATE_SHA256}
        ),
        "correction_commit_fresh_checkout_identity_match": (
            committed_evidence == evidence
        ),
        "absolute_path_worktree_mtime_identity_input_zero": (
            identity_input_count == 0
        ),
        "worktree_clean_before_attempt": (
            str(git("status", "--porcelain")).strip() == ""
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    report = {
        "schema_version": (
            "dvf-3-3-naturalization-publish-remediation-identity-binding-v1"
        ),
        "status": "PASS" if not failed else "FAIL",
        "naturalization_start_commit": START_COMMIT,
        "naturalization_start_tree": START_TREE,
        "compiler_correction_commit": COMPILER_CORRECTION_COMMIT,
        "compiler_correction_tree": COMPILER_CORRECTION_TREE,
        "execution_head": str(git("rev-parse", "HEAD")).strip(),
        "correction_record_path": base.repo_relative(CORRECTION_RECORD),
        "correction_record_sha256": base.sha256_file(CORRECTION_RECORD),
        "bounded_projection_report_path": base.repo_relative(
            BOUNDED_PROJECTION_REPORT
        ),
        "bounded_projection_report_sha256": base.sha256_file(
            BOUNDED_PROJECTION_REPORT
        ),
        "foundation_implementation_correction_readiness_sha256": (
            base.sha256_file(base.FOUNDATION_IMPLEMENTATION_READINESS)
        ),
        "foundation_contract_sha256": base.sha256_file(
            producer.FOUNDATION_CONTRACT
        ),
        "predecessor_readiness_sha256": base.sha256_file(
            producer.FOUNDATION_READINESS_CURRENT_INPUT_REBIND
        ),
        "identity_correction_contract_sha256": base.sha256_file(
            base.IDENTITY_CORRECTION_CONTRACT
        ),
        "identity_helper_sha256": base.sha256_file(base.IDENTITY_HELPER),
        "predecessor_canonical_compiler_aggregate_sha256": (
            PREDECESSOR_COMPILER_AGGREGATE_SHA256
        ),
        "canonical_compiler_identity": evidence,
        "producer_compiler_identity": producer_evidence,
        "publish_consumer_compiler_identity": consumer_evidence,
        "correction_commit_compiler_identity": committed_evidence,
        "line_ending_variant_aggregates": variant_aggregates,
        "actual_identity_input_field_count": identity_input_count,
        "checks": checks,
        "failed_checks": failed,
        "scope_guards": {
            "attempt_0004_disposition_or_failure_ledger_modified": False,
            "attempt_0023_modified_or_resumed": False,
            "official_publish_attempt_created": False,
            "g1_full_gate_executed": False,
            "g4_readiness_mutated": False,
            "live_gate_mutated": False,
            "facts_manifest_policy_detector_threshold_mutated": False,
            "runtime_lua_package_mutated": False,
            "new_worktree_or_repository_clone_created": False,
        },
    }
    if failed:
        raise PublishRemediationAttemptError(
            f"publish-remediation identity binding failed: {failed}"
        )
    return report


def write_phase0_remediation_binding(attempt_root: Path) -> dict[str, Any]:
    phase0 = attempt_root / "phase0"
    standard_particle = producer.load_json(
        phase0 / "compiler_particle_correction_binding_report.json"
    )
    identity_report = build_publish_remediation_identity_binding_report()
    report = {
        "schema_version": (
            "dvf-3-3-phase0-bounded-publish-remediation-binding-v1"
        ),
        "status": "PASS",
        "standard_particle_predecessor_binding_status": (
            standard_particle.get("status")
        ),
        "standard_particle_binding_interpretation": (
            "predecessor_constraint_satisfied; current compiler authority is "
            "the bounded publish-remediation correction commit"
        ),
        "compiler_semantics_changed": True,
        "compiler_change_authority": {
            "commit": COMPILER_CORRECTION_COMMIT,
            "tree": COMPILER_CORRECTION_TREE,
            "bounded_projection_report_sha256": (
                BOUNDED_PROJECTION_REPORT_SHA256
            ),
            "current_compiler_aggregate_sha256": (
                CURRENT_COMPILER_AGGREGATE_SHA256
            ),
        },
        "repository_line_ending_authority_substitutions": [
            base._LINE_ENDING_AUTHORITY_ROWS[path]
            for path in sorted(base._LINE_ENDING_AUTHORITY_ROWS)
        ],
        "tracked_files_mutated_by_binding": False,
        "foundation_mutated": False,
        "facts_manifest_policy_detector_threshold_mutated": False,
    }
    producer.write_once_or_same(
        phase0 / "bounded_publish_remediation_compiler_binding_report.json",
        report,
    )
    producer.write_once_or_same(
        phase0 / "repository_line_ending_authority_correction_report.json",
        {
            "schema_version": (
                "dvf-3-3-phase0-repository-authority-view-v1"
            ),
            "status": "PASS",
            "line_ending_authority_substitution_count": len(
                base._LINE_ENDING_AUTHORITY_ROWS
            ),
            "line_ending_authority_substitutions": report[
                "repository_line_ending_authority_substitutions"
            ],
            "compiler_semantics_changed_by_line_endings": False,
            "compiler_semantics_changed_by_bounded_correction": True,
            "bounded_correction_binding_sha256": producer.canonical_hash(
                identity_report
            ),
        },
    )
    return report


def write_phase1_authority_report(attempt_root: Path) -> dict[str, Any]:
    phase1 = attempt_root / "phase1"
    result = producer.load_json(phase1 / "phase1_result.json")
    snapshot = dict(base._CURRENT_SNAPSHOT_IDENTITY_VIEW)
    report = {
        "schema_version": "dvf-3-3-phase1-snapshot-authority-view-v1",
        "status": (
            "PASS"
            if result.get("status") == "PASS"
            and snapshot.get("snapshot_semantic_authority") is False
            and snapshot.get("candidate_answer_corpus") is False
            else "FAIL"
        ),
        "current_snapshot_identity_view": snapshot,
        "source_semantics_changed": False,
        "compiler_semantics_changed": False,
        "tracked_files_mutated": False,
    }
    if report["status"] != "PASS":
        raise PublishRemediationAttemptError(
            "Phase 1 repository snapshot authority view failed"
        )
    producer.write_once_or_same(
        phase1 / "current_snapshot_identity_correction_report.json",
        report,
    )
    return report


def write_phase2_publish_remediation_reseal(
    attempt_root: Path,
    identity_report: dict[str, Any],
) -> dict[str, Any]:
    phase2 = attempt_root / "phase2"
    standard_path = phase2 / "source_authority_reseal_report.json"
    standard = producer.load_json(standard_path)
    bounded = producer.load_json(BOUNDED_PROJECTION_REPORT)
    checks = {
        "standard_reseal_pass": standard.get("status") == "PASS",
        "facts_sha256_match": standard.get("current_facts_sha256")
        == base.EXPECTED_FACTS_SHA256,
        "manifest_sha256_match": standard.get("current_manifest_sha256")
        == base.EXPECTED_MANIFEST_SHA256,
        "g3_receipt_sha256_match": standard.get(
            "registry_adoption_receipt_sha256"
        )
        == base.EXPECTED_G3_RECEIPT_SHA256,
        "g3_terminal_seal_sha256_match": standard.get(
            "registry_correction_terminal_seal_sha256"
        )
        == base.EXPECTED_G3_TERMINAL_SEAL_SHA256,
        "g3_handoff_sha256_match": standard.get(
            "registry_naturalization_handoff_sha256"
        )
        == base.EXPECTED_G3_HANDOFF_SHA256,
        "foundation_contract_sha256_match": identity_report.get(
            "foundation_contract_sha256"
        )
        == base.EXPECTED_FOUNDATION_CONTRACT_SHA256,
        "foundation_readiness_sha256_match": identity_report.get(
            "foundation_implementation_correction_readiness_sha256"
        )
        == base.EXPECTED_IMPLEMENTATION_READINESS_SHA256,
        "bounded_projection_pass": bounded.get("status") == "PASS",
        "current_compiler_identity_match": identity_report.get(
            "canonical_compiler_identity", {}
        ).get("aggregate_sha256")
        == CURRENT_COMPILER_AGGREGATE_SHA256,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    report = {
        "schema_version": (
            "dvf-3-3-source-authority-publish-remediation-reseal-v1"
        ),
        "status": "PASS" if not failed else "FAIL",
        "naturalization_start_commit": START_COMMIT,
        "naturalization_start_tree": START_TREE,
        "compiler_correction_commit": COMPILER_CORRECTION_COMMIT,
        "compiler_correction_tree": COMPILER_CORRECTION_TREE,
        "correction_record_sha256": CORRECTION_RECORD_SHA256,
        "bounded_projection_report_sha256": (
            BOUNDED_PROJECTION_REPORT_SHA256
        ),
        "current_facts_sha256": base.EXPECTED_FACTS_SHA256,
        "current_manifest_sha256": base.EXPECTED_MANIFEST_SHA256,
        "g3_adoption_receipt_sha256": base.EXPECTED_G3_RECEIPT_SHA256,
        "g3_terminal_correction_seal_sha256": (
            base.EXPECTED_G3_TERMINAL_SEAL_SHA256
        ),
        "g3_naturalization_handoff_sha256": base.EXPECTED_G3_HANDOFF_SHA256,
        "foundation_contract_sha256": (
            base.EXPECTED_FOUNDATION_CONTRACT_SHA256
        ),
        "foundation_implementation_correction_readiness_sha256": (
            base.EXPECTED_IMPLEMENTATION_READINESS_SHA256
        ),
        "predecessor_readiness_sha256": (
            base.EXPECTED_PREDECESSOR_READINESS_SHA256
        ),
        "compiler_identity_algorithm_id": COMPILER_IDENTITY_ALGORITHM_ID,
        "canonical_compiler_aggregate_sha256": (
            CURRENT_COMPILER_AGGREGATE_SHA256
        ),
        "predecessor_compiler_aggregate_sha256": (
            PREDECESSOR_COMPILER_AGGREGATE_SHA256
        ),
        "foundation_mutated": False,
        "facts_manifest_mutated": False,
        "checks": checks,
        "failed_checks": failed,
    }
    if failed:
        raise PublishRemediationAttemptError(
            f"Phase 2 publish-remediation reseal failed: {failed}"
        )
    producer.write_once_or_same(
        phase2 / "source_authority_identity_v2_reseal_report.json",
        report,
    )
    return report


def write_bounded_projection_equality_report(
    attempt_root: Path,
) -> dict[str, Any]:
    phase4 = attempt_root / "phase4"
    candidate = phase4 / "candidate_rendered.json"
    trace = phase4 / "candidate_proposition_trace.jsonl"
    bounded = producer.load_json(BOUNDED_PROJECTION_REPORT)
    checks = {
        "candidate_sha256_matches_projection": (
            base.sha256_file(candidate)
            == bounded.get("projected_candidate_sha256")
        ),
        "trace_sha256_matches_projection": (
            base.sha256_file(trace) == bounded.get("projected_trace_sha256")
        ),
        "candidate_byte_identity": (
            candidate.read_bytes() == DISPOSABLE_CANDIDATE.read_bytes()
        ),
        "trace_byte_identity": (
            trace.read_bytes() == DISPOSABLE_TRACE.read_bytes()
        ),
        "bounded_projection_pass": bounded.get("status") == "PASS",
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    report = {
        "schema_version": (
            "dvf-3-3-bounded-projection-candidate-equality-v1"
        ),
        "status": "PASS" if not failed else "FAIL",
        "bounded_projection_report_sha256": (
            BOUNDED_PROJECTION_REPORT_SHA256
        ),
        "candidate_sha256": base.sha256_file(candidate),
        "trace_sha256": base.sha256_file(trace),
        "projected_candidate_sha256": bounded.get(
            "projected_candidate_sha256"
        ),
        "projected_trace_sha256": bounded.get("projected_trace_sha256"),
        "candidate_byte_identity": checks["candidate_byte_identity"],
        "trace_byte_identity": checks["trace_byte_identity"],
        "attempt_0022_public_text_comparison_performed": False,
        "comparison_authority": (
            "pre-attempt bounded non-authoritative projection sealed by "
            "compiler correction commit"
        ),
        "checks": checks,
        "failed_checks": failed,
    }
    if failed:
        raise PublishRemediationAttemptError(
            f"candidate differs from bounded projection: {failed}"
        )
    producer.write_once_or_same(
        phase4 / "bounded_projection_candidate_equality_report.json",
        report,
    )
    # The inherited identity-v2 validator compares this compatibility path
    # byte-for-byte across A/B.  Its content explicitly declines the obsolete
    # attempt-0022 equality interpretation.
    producer.write_once_or_same(
        phase4 / "attempt_0022_public_text_equality_report.json",
        report,
    )
    return report


_ORIGINAL_APPLY_RUNTIME_BINDING = base.apply_runtime_binding


def apply_runtime_binding() -> None:
    _ORIGINAL_APPLY_RUNTIME_BINDING()
    preserved = tuple(
        dict.fromkeys(
            (
                *producer.PRESERVED_PREDECESSOR_ATTEMPT_IDS,
                "attempt-0023-compiler-identity-v2-a",
                "attempt-0023-compiler-identity-v2-b",
            )
        )
    )
    producer.PRESERVED_PREDECESSOR_ATTEMPT_IDS = preserved
    validator.PRESERVED_PREDECESSOR_ATTEMPT_IDS = preserved


def configure() -> None:
    base.START_COMMIT = START_COMMIT
    base.START_TREE = START_TREE
    base.PRIMARY_ATTEMPT_ID = PRIMARY_ATTEMPT_ID
    base.REPLAY_ATTEMPT_ID = REPLAY_ATTEMPT_ID
    base.ALLOWED_ATTEMPT_IDS = (PRIMARY_ATTEMPT_ID, REPLAY_ATTEMPT_ID)
    base.EXPECTED_COMPILER_AGGREGATE_SHA256 = (
        CURRENT_COMPILER_AGGREGATE_SHA256
    )
    base.HUMAN_REVIEW_DECISION = HUMAN_REVIEW_DECISION
    base.ORCHESTRATOR_PATH = ORCHESTRATOR_PATH
    base.EFFECTIVE_PHASE_DIRECTORY_NAMES = {}
    base.apply_runtime_binding = apply_runtime_binding
    base.build_identity_binding_report = (
        build_publish_remediation_identity_binding_report
    )
    base.write_line_ending_authority_correction_report = (
        write_phase0_remediation_binding
    )
    base.write_phase1_snapshot_identity_correction_report = (
        write_phase1_authority_report
    )
    base.write_phase2_identity_reseal = (
        write_phase2_publish_remediation_reseal
    )
    base.write_attempt_0022_equality_report = (
        write_bounded_projection_equality_report
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run or validate the immutable attempt-0024 bounded Publish "
            "remediation Primary/replay pair."
        )
    )
    parser.add_argument("--action", choices=("run", "validate"), required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--mode", choices=producer.RUNNER_MODES)
    parser.add_argument("--compare-attempt")
    parser.add_argument(
        "--validate-scope",
        choices=("phase0-6", "phase7-8"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configure()
    delegated = [
        "--action",
        args.action,
        "--attempt-id",
        args.attempt_id,
    ]
    if args.mode is not None:
        delegated.extend(["--mode", args.mode])
    if args.compare_attempt is not None:
        delegated.extend(["--compare-attempt", args.compare_attempt])
    if args.validate_scope is not None:
        delegated.extend(["--validate-scope", args.validate_scope])
    return base.main(delegated)


if __name__ == "__main__":
    raise SystemExit(main())
