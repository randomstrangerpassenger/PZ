from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


SCHEMA_PREFIX = "food-semantic-vc1-validation-contract"
ATTEMPT_ID = "attempt-0022"
EXPECTED_PROPOSAL_SHA256 = (
    "3d1c4b2ab56dba796163fc18ef8db2f495ab5a90579f9dc72acbf759cd42b10f"
)
EXPECTED_REVIEW_SHA256 = (
    "4bc0c8cc52cea8d5b9758e45515c2ebafcc069b3f058c496bb7f3a05855a32b5"
)
EXPECTED_FAILURE_SHA256 = (
    "5901af660199fb3e13ff8d86ae3445c8894a935ff32c3abafc410004af62f135"
)
EXPECTED_SUCCESSOR_FACTS_SHA256 = (
    "1ef1785f12d53fbfdca7e96d372079c16fcec276cbae93280e62908c8a891b40"
)
EXPECTED_SUCCESSOR_MANIFEST_SHA256 = (
    "d1dea3b7b871fac90fc6a15ec18d95641a52d566cd62d14ffb0114c2bfb0098a"
)
EXPECTED_ENVIRONMENT_RECEIPT_SHA256 = (
    "fb5dd78e15c41346f15b39065c60c2ce4d83254d73bbde3d3181d327b30b6bc2"
)
FULL_GATE_PATH = "Iris/validation/clean_checkout/contracts/full_repository_gate.json"
CORRECTION_REVIEW_NAME = "validation_contract_correction_review.json"
FOCUSED_COMMAND = (
    "uv run python -B -m unittest discover "
    "-s Iris/build/description/v2/tests "
    '-p "test_dvf_3_3_food_semantic_*.py"'
)
D16_ACCEPTANCE_COMMAND = (
    "uv run python -B -m unittest discover "
    "-s Iris/build/description/v2/tests "
    '-p "test_dvf_3_3_korean_prose_acceptance_gate.py"'
)
D16_PRESERVATION_COMMAND = (
    "uv run python -B -m unittest discover "
    "-s Iris/build/description/v2/tests "
    '-p "test_dvf_3_3_korean_prose_semantic_preservation.py"'
)


class ReconciliationError(RuntimeError):
    pass


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ReconciliationError(code)


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReconciliationError(f"json_read_failed:{path}") from exc
    if not isinstance(value, dict):
        raise ReconciliationError(f"json_object_required:{path}")
    return value


def write_json_once(path: Path, value: dict[str, Any]) -> None:
    payload = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_bytes() == payload, f"write_once_conflict:{path}")
        return
    path.write_bytes(payload)


def run_git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise ReconciliationError(
            f"git_failed:{' '.join(args)}:{completed.stderr.strip()}"
        )
    return completed.stdout.strip()


def git_subject(repo: Path, revision: str) -> dict[str, str]:
    return {
        "commit": run_git(repo, "rev-parse", revision),
        "tree": run_git(repo, "show", "-s", "--format=%T", revision),
    }


def git_blob(repo: Path, revision: str, relative: str) -> str:
    return run_git(repo, "rev-parse", f"{revision}:{relative}")


def ensure_attempt_root(repo: Path, attempt_root: Path) -> Path:
    resolved_repo = repo.resolve()
    resolved_attempt = attempt_root.resolve()
    try:
        relative = resolved_attempt.relative_to(resolved_repo).as_posix()
    except ValueError as exc:
        raise ReconciliationError("attempt_root_outside_repository") from exc
    expected = (
        "Iris/build/description/v2/staging/"
        "dvf_3_3_food_semantic_facts_authority/attempts/attempt-0022"
    )
    require(relative == expected, "attempt_root_identity_mismatch")
    return resolved_attempt


def validate_bound_authority(
    repo: Path,
    attempt_root: Path,
    owner_ratification_path: Path,
) -> dict[str, Any]:
    phase = attempt_root / "phase13_closeout"
    proposal_path = phase / "validation_contract_reconciliation_proposal.json"
    review_path = phase / "validation_contract_reconciliation_review.json"
    failure_path = phase / "post_authority_validation_failure.json"
    ratification = load_object(owner_ratification_path)
    require(
        sha256_file(proposal_path) == EXPECTED_PROPOSAL_SHA256,
        "proposal_sha256_mismatch",
    )
    require(
        sha256_file(review_path) == EXPECTED_REVIEW_SHA256,
        "proposal_review_sha256_mismatch",
    )
    require(
        sha256_file(failure_path) == EXPECTED_FAILURE_SHA256,
        "preserved_failure_sha256_mismatch",
    )
    require(ratification.get("status") == "APPROVED", "owner_ratification_not_approved")
    require(
        ratification.get("verdict") == "APPROVE_EXACT_PROPOSAL",
        "owner_ratification_verdict_mismatch",
    )
    require(
        ratification.get("attempt_id") == ATTEMPT_ID,
        "owner_ratification_attempt_mismatch",
    )
    require(
        ratification.get("proposal_sha256") == EXPECTED_PROPOSAL_SHA256,
        "owner_ratification_proposal_mismatch",
    )
    require(
        ratification.get("review_sha256") == EXPECTED_REVIEW_SHA256,
        "owner_ratification_review_mismatch",
    )
    require(
        ratification.get("same_attempt_continuation_approved") is True,
        "same_attempt_continuation_not_approved",
    )
    require(
        ratification.get("failed_validation_rewrite_allowed") is False,
        "failed_validation_rewrite_not_forbidden",
    )
    require(
        ratification.get("sealed_successor_hash_change_allowed") is False,
        "successor_hash_change_not_forbidden",
    )
    require(
        ratification.get("current_facts_manifest_mutation_allowed") is False,
        "current_authority_mutation_not_forbidden",
    )
    successor_facts = (
        attempt_root / "authority_execution/successor_facts.jsonl"
    )
    successor_manifest = (
        attempt_root / "authority_execution/successor_input_manifest.json"
    )
    require(
        sha256_file(successor_facts) == EXPECTED_SUCCESSOR_FACTS_SHA256,
        "successor_facts_sha256_mismatch",
    )
    require(
        sha256_file(successor_manifest) == EXPECTED_SUCCESSOR_MANIFEST_SHA256,
        "successor_manifest_sha256_mismatch",
    )
    authority_summary = load_object(
        attempt_root / "authority_execution/authority_execution_summary.json"
    )
    require(authority_summary.get("status") == "PASS", "authority_summary_not_pass")
    require(
        authority_summary.get("selected_branch") == "B",
        "authority_branch_not_B",
    )
    require(
        authority_summary.get("sealed_non_current_successor") is True,
        "sealed_non_current_successor_missing",
    )
    require(
        authority_summary.get("current_facts_manifest_mutation_count") == 0,
        "current_facts_manifest_mutated",
    )
    return {
        "proposal_sha256": EXPECTED_PROPOSAL_SHA256,
        "proposal_review_sha256": EXPECTED_REVIEW_SHA256,
        "owner_ratification_sha256": sha256_file(owner_ratification_path),
        "preserved_failure_sha256": EXPECTED_FAILURE_SHA256,
        "successor_facts_sha256": EXPECTED_SUCCESSOR_FACTS_SHA256,
        "successor_manifest_sha256": EXPECTED_SUCCESSOR_MANIFEST_SHA256,
    }


def validate_correction_review(
    repo: Path,
    attempt_root: Path,
    validation_subject: dict[str, str],
) -> dict[str, Any]:
    review_path = attempt_root / "phase13_closeout" / CORRECTION_REVIEW_NAME
    review = load_object(review_path)
    require(review.get("status") == "PASS", "correction_review_not_pass")
    require(review.get("verdict") == "PASS", "correction_review_verdict_not_pass")
    require(
        review.get("terminal_independent_review_credit") == 0,
        "correction_review_terminal_credit_nonzero",
    )
    reviewed_subject = review.get("reviewed_correction_subject")
    require(
        isinstance(reviewed_subject, dict),
        "correction_review_subject_missing",
    )
    reviewed_commit = str(reviewed_subject.get("commit", ""))
    reviewed_tree = str(reviewed_subject.get("tree", ""))
    require(
        git_subject(repo, reviewed_commit)
        == {"commit": reviewed_commit, "tree": reviewed_tree},
        "correction_review_subject_git_mismatch",
    )
    require(
        review.get("open_critical_finding_count") == 0,
        "correction_review_open_critical",
    )
    require(
        review.get("open_important_finding_count") == 0,
        "correction_review_open_important",
    )
    require(
        review.get("unresolved_finding_count") == 0,
        "correction_review_unresolved_findings",
    )
    bindings = review.get("reviewed_bindings")
    require(isinstance(bindings, dict), "correction_review_bindings_missing")
    for key in ("plan", "correction_tool", "owner_ratification"):
        row = bindings.get(key)
        require(isinstance(row, dict), f"correction_review_binding_missing:{key}")
        relative = str(row.get("path", ""))
        require(
            row.get("git_blob_id") == git_blob(repo, reviewed_commit, relative),
            f"correction_review_blob_mismatch:{key}",
        )
    allowed_delta = (
        "Iris/build/description/v2/staging/"
        "dvf_3_3_food_semantic_facts_authority/attempts/attempt-0022/"
        f"phase13_closeout/{CORRECTION_REVIEW_NAME}"
    )
    changed = {
        line
        for line in run_git(
            repo,
            "diff",
            "--name-only",
            f"{reviewed_commit}..{validation_subject['commit']}",
        ).splitlines()
        if line
    }
    require(
        changed == {allowed_delta},
        "validation_subject_contains_unreviewed_delta",
    )
    return {
        "path": allowed_delta,
        "sha256": sha256_file(review_path),
        "reviewed_correction_subject": reviewed_subject,
        "validation_subject": validation_subject,
        "review_to_validation_subject_delta": sorted(changed),
    }


def validate_full_gate_run(
    repo: Path,
    receipt_path: Path,
    expected_subject: dict[str, str],
) -> dict[str, Any]:
    receipt = load_object(receipt_path)
    require(
        receipt.get("schema_version")
        == "iris-clean-checkout-full-run-receipt-v1",
        "full_gate_receipt_schema_mismatch",
    )
    require(receipt.get("status") == "PASS", "full_gate_receipt_not_pass")
    require(receipt.get("subject") == expected_subject, "full_gate_subject_mismatch")
    require(receipt.get("pytest_return_code") == 0, "full_gate_pytest_nonzero")
    require(
        receipt.get("source_repository_status_before") == [],
        "full_gate_source_dirty_before",
    )
    require(
        receipt.get("source_repository_status_after") == [],
        "full_gate_source_dirty_after",
    )
    require(
        receipt.get("external_execution_checkout_cleanup_status") == "PASS",
        "full_gate_external_cleanup_not_pass",
    )
    require(
        receipt.get("external_work_root_empty_after") is True,
        "full_gate_external_work_root_not_empty",
    )
    standalone_rows = receipt.get("standalone_rows")
    require(
        isinstance(standalone_rows, list) and len(standalone_rows) == 4,
        "full_gate_standalone_denominator_mismatch",
    )
    require(
        all(
            isinstance(row, dict)
            and row.get("status") == "PASS"
            and row.get("return_code") == 0
            for row in standalone_rows
        ),
        "full_gate_standalone_failure",
    )
    canonical_binding = receipt.get("canonical_result")
    require(
        isinstance(canonical_binding, dict),
        "full_gate_canonical_binding_missing",
    )
    canonical_path = Path(str(canonical_binding.get("path", ""))).resolve()
    require(canonical_path.is_file(), "full_gate_canonical_result_missing")
    canonical_sha256 = sha256_file(canonical_path)
    require(
        canonical_binding.get("sha256") == canonical_sha256,
        "full_gate_canonical_result_hash_mismatch",
    )
    canonical = load_object(canonical_path)
    require(
        canonical.get("schema_version")
        == "iris-clean-checkout-canonical-full-result-v1",
        "full_gate_canonical_schema_mismatch",
    )
    require(canonical.get("status") == "PASS", "full_gate_canonical_not_pass")
    require(canonical.get("subject") == expected_subject, "canonical_subject_mismatch")
    require(
        canonical.get("collection_error_count") == 0,
        "full_gate_collection_errors",
    )
    require(
        canonical.get("source_checkout_clean_before") is True
        and canonical.get("source_checkout_clean_after") is True,
        "canonical_source_checkout_not_clean",
    )
    require(
        canonical.get("external_execution_checkout_cleanup_status") == "PASS"
        and canonical.get("external_work_root_empty_after") is True,
        "canonical_external_cleanup_not_pass",
    )
    require(
        canonical.get("full_repository_gate_blob_id")
        == git_blob(repo, expected_subject["commit"], FULL_GATE_PATH),
        "canonical_full_gate_blob_mismatch",
    )
    environment_path = Path(str(receipt.get("environment_receipt_path", "")))
    require(environment_path.is_file(), "environment_receipt_missing")
    require(
        sha256_file(environment_path) == EXPECTED_ENVIRONMENT_RECEIPT_SHA256,
        "environment_receipt_sha256_mismatch",
    )
    return {
        "run_receipt_sha256": sha256_file(receipt_path),
        "run_receipt_schema_version": receipt["schema_version"],
        "status": receipt["status"],
        "subject": receipt["subject"],
        "pytest_return_code": receipt["pytest_return_code"],
        "standalone_validation_count": len(standalone_rows),
        "required_execution_unit_count": canonical.get(
            "required_execution_unit_count"
        ),
        "test_inventory_sha256": canonical.get("test_inventory_sha256"),
        "canonical_result_sha256": canonical_sha256,
        "source_checkout_clean_before": True,
        "source_checkout_clean_after": True,
        "external_execution_checkout_cleanup_status": "PASS",
        "external_work_root_empty_after": True,
        "environment_receipt_sha256": EXPECTED_ENVIRONMENT_RECEIPT_SHA256,
        "embedded_canonical_result": canonical,
    }


def record_validation(args: argparse.Namespace) -> dict[str, Any]:
    repo = Path(args.repo).resolve()
    attempt_root = ensure_attempt_root(repo, Path(args.attempt_root))
    owner_ratification = Path(args.owner_ratification).resolve()
    authority_binding = validate_bound_authority(
        repo, attempt_root, owner_ratification
    )
    validation_subject = git_subject(repo, "HEAD")
    correction_review = validate_correction_review(
        repo, attempt_root, validation_subject
    )
    exit_codes = {
        "food_semantic_focused": args.food_focused_exit_code,
        "d16_acceptance": args.d16_acceptance_exit_code,
        "d16_semantic_preservation": args.d16_preservation_exit_code,
    }
    require(
        all(value == 0 for value in exit_codes.values()),
        "explicit_food_or_d16_validation_nonzero",
    )
    run_a = validate_full_gate_run(
        repo, Path(args.run_a_receipt).resolve(), validation_subject
    )
    run_b = validate_full_gate_run(
        repo, Path(args.run_b_receipt).resolve(), validation_subject
    )
    canonical_a = run_a.pop("embedded_canonical_result")
    canonical_b = run_b.pop("embedded_canonical_result")
    canonical_equal = canonical_json_bytes(canonical_a) == canonical_json_bytes(
        canonical_b
    )
    require(canonical_equal, "full_gate_canonical_results_not_equal")
    require(
        run_a["canonical_result_sha256"] == run_b["canonical_result_sha256"],
        "full_gate_canonical_result_file_hash_mismatch",
    )
    require(
        run_a["test_inventory_sha256"] == run_b["test_inventory_sha256"],
        "full_gate_inventory_hash_mismatch",
    )
    phase = attempt_root / "phase13_closeout"
    clean_receipt = {
        "schema_version": f"{SCHEMA_PREFIX}-clean-checkout-receipt-v1",
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "validation_subject": validation_subject,
        "authority_contract": FULL_GATE_PATH,
        "run_count": 2,
        "run_a": run_a,
        "run_b": run_b,
        "canonical_results_equal": True,
        "canonical_result_sha256": sha256_bytes(
            canonical_json_bytes(canonical_a)
        ),
        "embedded_canonical_result": canonical_a,
        "repository_retrievable_without_external_receipts": True,
        "external_receipts_are_validation_inputs_not_terminal_dependencies": True,
    }
    clean_receipt_path = phase / "vc1_clean_checkout_validation_receipt.json"
    write_json_once(clean_receipt_path, clean_receipt)
    failure_path = phase / "post_authority_validation_failure.json"
    correction_review_path = phase / CORRECTION_REVIEW_NAME
    result = {
        "schema_version": "food-semantic-post-authority-validation-vc1-v1",
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "validation_contract": "VC-1",
        "validation_subject": validation_subject,
        "commands": {
            "food_semantic_focused": {
                "command": FOCUSED_COMMAND,
                "exit_code": exit_codes["food_semantic_focused"],
                "status": "PASS",
            },
            "d16_acceptance": {
                "command": D16_ACCEPTANCE_COMMAND,
                "exit_code": exit_codes["d16_acceptance"],
                "status": "PASS",
            },
            "d16_semantic_preservation": {
                "command": D16_PRESERVATION_COMMAND,
                "exit_code": exit_codes["d16_semantic_preservation"],
                "status": "PASS",
            },
            "full_required_repository_run_a": {
                "authority_contract": FULL_GATE_PATH,
                "exit_code": 0,
                "status": "PASS",
                "run_receipt_sha256": run_a["run_receipt_sha256"],
            },
            "full_required_repository_run_b": {
                "authority_contract": FULL_GATE_PATH,
                "exit_code": 0,
                "status": "PASS",
                "run_receipt_sha256": run_b["run_receipt_sha256"],
            },
            "current_route": {
                "selected_branch": "B+G2",
                "status": "NOT_APPLICABLE",
                "exit_code": None,
                "fake_success_code_allowed": False,
                "future_G1_rule_unchanged": True,
            },
            "direct_all_unittest_discovery": {
                "status": "PRESERVED_FAIL_DIAGNOSTIC_ONLY",
                "terminal_gate_credit": 0,
                "waiver_created": False,
                "failure_evidence_path": failure_path.relative_to(repo).as_posix(),
                "failure_evidence_sha256": EXPECTED_FAILURE_SHA256,
            },
        },
        "command_count": 7,
        "failed_command_count": 0,
        "applicable_command_group_count": 5,
        "applicable_failed_command_count": 0,
        "not_applicable_command_group_count": 1,
        "diagnostic_only_command_group_count": 1,
        "canonical_clean_checkout_receipt_path": clean_receipt_path.relative_to(
            repo
        ).as_posix(),
        "canonical_clean_checkout_receipt_sha256": sha256_file(
            clean_receipt_path
        ),
        "canonical_results_equal": True,
        "authority_binding": authority_binding,
        "correction_review": {
            **correction_review,
            "sha256": sha256_file(correction_review_path),
        },
        "current_facts_manifest_mutation_count": 0,
        "sealed_non_current_successor_preserved": True,
        "closeout_may_prepare": True,
    }
    result_path = phase / "post_authority_validation_result.json"
    write_json_once(result_path, result)
    return {
        "status": "PASS",
        "validation_subject": validation_subject,
        "canonical_results_equal": True,
        "post_authority_validation_result_sha256": sha256_file(result_path),
        "clean_checkout_validation_receipt_sha256": sha256_file(
            clean_receipt_path
        ),
    }


def validate_recorded(args: argparse.Namespace) -> dict[str, Any]:
    repo = Path(args.repo).resolve()
    attempt_root = ensure_attempt_root(repo, Path(args.attempt_root))
    phase = attempt_root / "phase13_closeout"
    ratification = (
        phase / "validation_contract_reconciliation_owner_ratification.json"
    )
    authority_binding = validate_bound_authority(repo, attempt_root, ratification)
    clean_path = phase / "vc1_clean_checkout_validation_receipt.json"
    result_path = phase / "post_authority_validation_result.json"
    clean = load_object(clean_path)
    result = load_object(result_path)
    require(clean.get("status") == "PASS", "recorded_clean_receipt_not_pass")
    require(clean.get("run_count") == 2, "recorded_clean_run_count_mismatch")
    require(
        clean.get("canonical_results_equal") is True,
        "recorded_canonical_results_not_equal",
    )
    canonical = clean.get("embedded_canonical_result")
    require(isinstance(canonical, dict), "embedded_canonical_result_missing")
    canonical_sha256 = sha256_bytes(canonical_json_bytes(canonical))
    require(
        clean.get("canonical_result_sha256") == canonical_sha256,
        "embedded_canonical_result_hash_mismatch",
    )
    subject = clean.get("validation_subject")
    require(isinstance(subject, dict), "recorded_validation_subject_missing")
    require(
        git_subject(repo, str(subject.get("commit", ""))) == subject,
        "recorded_validation_subject_git_mismatch",
    )
    require(result.get("status") == "PASS", "recorded_validation_not_pass")
    require(
        result.get("validation_contract") == "VC-1",
        "recorded_validation_contract_mismatch",
    )
    require(
        result.get("validation_subject") == subject,
        "recorded_result_subject_mismatch",
    )
    require(
        result.get("applicable_failed_command_count") == 0,
        "recorded_applicable_failure_count_nonzero",
    )
    current_route = result.get("commands", {}).get("current_route", {})
    require(
        current_route.get("status") == "NOT_APPLICABLE"
        and current_route.get("exit_code") is None
        and current_route.get("fake_success_code_allowed") is False,
        "recorded_current_route_disposition_invalid",
    )
    require(
        result.get("canonical_clean_checkout_receipt_sha256")
        == sha256_file(clean_path),
        "recorded_clean_receipt_binding_mismatch",
    )
    require(
        result.get("authority_binding") == authority_binding,
        "recorded_authority_binding_mismatch",
    )
    return {
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "validation_subject": subject,
        "post_authority_validation_result_sha256": sha256_file(result_path),
        "clean_checkout_validation_receipt_sha256": sha256_file(clean_path),
        "repository_only_revalidation": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Record or validate the owner-ratified VC-1 contract."
    )
    parser.add_argument("command", choices=("record", "validate"))
    parser.add_argument("--repo", required=True)
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--owner-ratification")
    parser.add_argument("--run-a-receipt")
    parser.add_argument("--run-b-receipt")
    parser.add_argument("--food-focused-exit-code", type=int)
    parser.add_argument("--d16-acceptance-exit-code", type=int)
    parser.add_argument("--d16-preservation-exit-code", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "record":
            required = {
                "--owner-ratification": args.owner_ratification,
                "--run-a-receipt": args.run_a_receipt,
                "--run-b-receipt": args.run_b_receipt,
                "--food-focused-exit-code": args.food_focused_exit_code,
                "--d16-acceptance-exit-code": args.d16_acceptance_exit_code,
                "--d16-preservation-exit-code": args.d16_preservation_exit_code,
            }
            missing = [
                name for name, value in required.items() if value is None
            ]
            require(not missing, "missing_record_arguments:" + ",".join(missing))
            result = record_validation(args)
        else:
            result = validate_recorded(args)
    except (OSError, ReconciliationError, KeyError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "BLOCKED", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
