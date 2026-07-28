from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


SCHEMA_PREFIX = "food-semantic-vc1-validation-contract"
ATTEMPT_ID = "attempt-0022"
EXPECTED_PROPOSAL_SHA256 = (
    "3d1c4b2ab56dba796163fc18ef8db2f495ab5a90579f9dc72acbf759cd42b10f"
)
EXPECTED_PROPOSAL_BLOB = "28b33ecd1d6642b46df3fea2ae64d068c427cde1"
EXPECTED_REVIEW_SHA256 = (
    "4bc0c8cc52cea8d5b9758e45515c2ebafcc069b3f058c496bb7f3a05855a32b5"
)
EXPECTED_REVIEW_BLOB = "4c5a1b6c4cf381827b8084da206dd37a3b9e2f8e"
EXPECTED_FAILURE_SHA256 = (
    "5901af660199fb3e13ff8d86ae3445c8894a935ff32c3abafc410004af62f135"
)
EXPECTED_FAILURE_BLOB = "bf63aea81716af8e8f7c9dd512a2e071006de2d8"
EXPECTED_SUCCESSOR_FACTS_SHA256 = (
    "1ef1785f12d53fbfdca7e96d372079c16fcec276cbae93280e62908c8a891b40"
)
EXPECTED_SUCCESSOR_MANIFEST_SHA256 = (
    "d1dea3b7b871fac90fc6a15ec18d95641a52d566cd62d14ffb0114c2bfb0098a"
)
EXPECTED_RATIFICATION_SHA256 = (
    "c12c0598fb0e8c65d39a8323bf337eae60f7116dba8997bd0235a4714acb4b52"
)
EXPECTED_RATIFICATION_BLOB = "7b1fa03d4784e0f53eb409bc0ac6c781f6dc3dd2"
EXPECTED_PLAN_SHA256 = (
    "e23fff82de3cf661fb0d22299f708989a7ae75589e70bbfd6e3ec442b1c8d26f"
)
EXPECTED_SCOPE_DIRECTION_SHA256 = (
    "85b4038c4395eab0fd4d3fc9313e1fe461e6225fca3f8d00f9eca525f80f16ea"
)
EXPECTED_SCOPE_DIRECTION_BLOB = "0cfd31bec1992581ad864981a8757be187ebf4e8"
ATTEMPT_RELATIVE = (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_food_semantic_facts_authority/attempts/attempt-0022"
)
PLAN_PATH = (
    "docs/dvf_3_3_food_semantic_facts_authority_reconstruction_"
    "implementation_plan.md"
)
CORRECTION_REVIEW_NAME = "validation_contract_correction_review.json"
RATIFICATION_NAME = (
    "validation_contract_reconciliation_owner_ratification.json"
)
FOCUSED_RECEIPT_NAME = "vc1_focused_validation_receipt.json"
FOCUSED_WORK_ROOT = Path(
    "C:/Users/Public/Documents/ESTsoft/CreatorTemp/fsvc-focused"
)
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
COMMAND_SPECS = (
    (
        "food_semantic_focused",
        FOCUSED_COMMAND,
        "test_dvf_3_3_food_semantic_*.py",
    ),
    (
        "d16_acceptance",
        D16_ACCEPTANCE_COMMAND,
        "test_dvf_3_3_korean_prose_acceptance_gate.py",
    ),
    (
        "d16_semantic_preservation",
        D16_PRESERVATION_COMMAND,
        "test_dvf_3_3_korean_prose_semantic_preservation.py",
    ),
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


def write_bytes_once(path: Path, payload: bytes) -> None:
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


def git_blob_sha256(repo: Path, revision: str, relative: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), "show", f"{revision}:{relative}"],
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise ReconciliationError(
            f"git_blob_read_failed:{revision}:{relative}"
        )
    return sha256_bytes(completed.stdout)


def repository_status(repo: Path) -> list[str]:
    output = run_git(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    return output.splitlines() if output else []


def require_empty_external_root(repo: Path, path: Path, expected: Path) -> Path:
    resolved = path.resolve()
    require(
        resolved == expected.resolve(),
        f"external_root_identity_mismatch:{expected.name}",
    )
    try:
        resolved.relative_to(repo.resolve())
    except ValueError:
        pass
    else:
        raise ReconciliationError("external_root_inside_repository")
    if resolved.exists():
        require(resolved.is_dir(), "external_root_not_directory")
        require(not any(resolved.iterdir()), "external_root_not_empty")
    else:
        resolved.mkdir(parents=True)
    return resolved


def progress(event: str) -> None:
    print(
        json.dumps({"vc1_progress": event}, sort_keys=True),
        file=sys.stderr,
        flush=True,
    )


def ensure_attempt_root(repo: Path, attempt_root: Path) -> Path:
    resolved_repo = repo.resolve()
    resolved_attempt = attempt_root.resolve()
    try:
        relative = resolved_attempt.relative_to(resolved_repo).as_posix()
    except ValueError as exc:
        raise ReconciliationError("attempt_root_outside_repository") from exc
    require(relative == ATTEMPT_RELATIVE, "attempt_root_identity_mismatch")
    return resolved_attempt


def validate_bound_authority(
    repo: Path,
    attempt_root: Path,
    validation_subject: dict[str, str],
) -> dict[str, Any]:
    phase = attempt_root / "phase13_closeout"
    proposal_path = phase / "validation_contract_reconciliation_proposal.json"
    review_path = phase / "validation_contract_reconciliation_review.json"
    failure_path = phase / "post_authority_validation_failure.json"
    owner_ratification_path = phase / RATIFICATION_NAME
    scope_direction_path = phase / "validation_scope_owner_direction.json"
    require(
        owner_ratification_path.relative_to(repo).as_posix()
        == f"{ATTEMPT_RELATIVE}/phase13_closeout/{RATIFICATION_NAME}",
        "owner_ratification_path_mismatch",
    )
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
    require(
        sha256_file(owner_ratification_path) == EXPECTED_RATIFICATION_SHA256,
        "owner_ratification_sha256_mismatch",
    )
    require(
        sha256_file(scope_direction_path)
        == EXPECTED_SCOPE_DIRECTION_SHA256,
        "scope_direction_sha256_mismatch",
    )
    subject_commit = validation_subject["commit"]
    for bound_path, expected_blob, expected_sha256, code in (
        (
            proposal_path,
            EXPECTED_PROPOSAL_BLOB,
            EXPECTED_PROPOSAL_SHA256,
            "proposal",
        ),
        (
            review_path,
            EXPECTED_REVIEW_BLOB,
            EXPECTED_REVIEW_SHA256,
            "proposal_review",
        ),
        (
            failure_path,
            EXPECTED_FAILURE_BLOB,
            EXPECTED_FAILURE_SHA256,
            "preserved_failure",
        ),
    ):
        relative = bound_path.relative_to(repo).as_posix()
        require(
            git_blob(repo, subject_commit, relative) == expected_blob,
            f"{code}_subject_blob_mismatch",
        )
        require(
            git_blob_sha256(repo, subject_commit, relative)
            == expected_sha256,
            f"{code}_subject_sha256_mismatch",
        )
    require(
        git_blob(
            repo,
            subject_commit,
            owner_ratification_path.relative_to(repo).as_posix(),
        )
        == EXPECTED_RATIFICATION_BLOB,
        "owner_ratification_blob_mismatch",
    )
    require(
        git_blob(
            repo,
            subject_commit,
            scope_direction_path.relative_to(repo).as_posix(),
        )
        == EXPECTED_SCOPE_DIRECTION_BLOB,
        "scope_direction_blob_mismatch",
    )
    require(
        git_blob_sha256(repo, subject_commit, PLAN_PATH)
        == EXPECTED_PLAN_SHA256,
        "validation_subject_plan_sha256_mismatch",
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
    scope_direction = load_object(scope_direction_path)
    require(
        scope_direction.get("status") == "APPROVED"
        and scope_direction.get("scope_effect")
        == (
            "restrict_validation_to_food_semantic_authority_"
            "and_direct_D16_handoff_only"
        ),
        "scope_direction_not_approved",
    )
    require(
        scope_direction.get("excluded_failure_waiver_created") is False
        and scope_direction.get("same_attempt_continuation") is True,
        "scope_direction_predicate_mismatch",
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
        "owner_ratification_sha256": EXPECTED_RATIFICATION_SHA256,
        "owner_ratification_git_blob_id": EXPECTED_RATIFICATION_BLOB,
        "plan_sha256": EXPECTED_PLAN_SHA256,
        "scope_direction_sha256": EXPECTED_SCOPE_DIRECTION_SHA256,
        "scope_direction_git_blob_id": EXPECTED_SCOPE_DIRECTION_BLOB,
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
    require(
        review.get("schema_version")
        == "food-semantic-validation-contract-correction-review-v1",
        "correction_review_schema_mismatch",
    )
    require(review.get("status") == "PASS", "correction_review_not_pass")
    require(review.get("verdict") == "PASS", "correction_review_verdict_not_pass")
    require(
        review.get("review_role")
        == "external_Codex_Reviewer_VC1_correction_review",
        "correction_review_role_mismatch",
    )
    reviewer_identity = review.get("reviewer_identity")
    require(
        isinstance(reviewer_identity, str)
        and reviewer_identity.startswith("Codex Reviewer /root/"),
        "correction_reviewer_identity_invalid",
    )
    require(
        review.get("tests_executed") is False,
        "correction_reviewer_executed_tests",
    )
    require(
        review.get("files_modified") is False,
        "correction_reviewer_modified_files",
    )
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
    binding_paths = {
        "plan": PLAN_PATH,
        "correction_tool": (
            f"{ATTEMPT_RELATIVE}/phase13_closeout/"
            "vc1_validation_contract.py"
        ),
        "closeout_overlay": (
            f"{ATTEMPT_RELATIVE}/phase13_closeout/"
            "vc1_prepare_closeout.py"
        ),
        "owner_ratification": (
            f"{ATTEMPT_RELATIVE}/phase13_closeout/{RATIFICATION_NAME}"
        ),
        "owner_scope_direction": (
            f"{ATTEMPT_RELATIVE}/phase13_closeout/"
            "validation_scope_owner_direction.json"
        ),
        "reconciliation_implementation": (
            f"{ATTEMPT_RELATIVE}/phase13_closeout/"
            "validation_contract_reconciliation_implementation.json"
        ),
    }
    require(
        set(bindings) == set(binding_paths),
        "correction_review_binding_key_set_mismatch",
    )
    for key, expected_path in binding_paths.items():
        row = bindings.get(key)
        require(isinstance(row, dict), f"correction_review_binding_missing:{key}")
        relative = str(row.get("path", ""))
        require(
            relative == expected_path,
            f"correction_review_binding_path_mismatch:{key}",
        )
        require(
            row.get("git_blob_id") == git_blob(repo, reviewed_commit, relative),
            f"correction_review_blob_mismatch:{key}",
        )
        require(
            row.get("sha256")
            == git_blob_sha256(repo, reviewed_commit, relative),
            f"correction_review_sha256_mismatch:{key}",
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


def command_argv(pattern: str) -> list[str]:
    return [
        "uv",
        "run",
        "python",
        "-B",
        "-m",
        "unittest",
        "discover",
        "-s",
        "Iris/build/description/v2/tests",
        "-p",
        pattern,
    ]


def run_scoped_validation_commands(
    repo: Path,
    subject: dict[str, str],
) -> tuple[dict[str, Any], dict[str, tuple[bytes, bytes]]]:
    source_before = repository_status(repo)
    require(source_before == [], "source_repository_dirty_before_scoped_validation")
    work_root = require_empty_external_root(
        repo, FOCUSED_WORK_ROOT, FOCUSED_WORK_ROOT
    )
    checkout = work_root / "checkout"
    outputs: dict[str, tuple[bytes, bytes]] = {}
    command_rows: list[dict[str, Any]] = []
    checkout_before: list[str] | None = None
    checkout_after: list[str] | None = None
    cleanup_status = "NOT_RUN"
    try:
        progress("scoped_checkout_materialization_started")
        cloned = subprocess.run(
            [
                "git",
                "clone",
                "--no-hardlinks",
                "--quiet",
                str(repo),
                str(checkout),
            ],
            check=False,
            capture_output=True,
        )
        require(cloned.returncode == 0, "scoped_checkout_clone_failed")
        checked_out = subprocess.run(
            [
                "git",
                "-C",
                str(checkout),
                "checkout",
                "--detach",
                "--quiet",
                subject["commit"],
            ],
            check=False,
            capture_output=True,
        )
        require(checked_out.returncode == 0, "scoped_checkout_detach_failed")
        require(
            git_subject(checkout, "HEAD") == subject,
            "scoped_checkout_subject_mismatch",
        )
        checkout_before = repository_status(checkout)
        require(checkout_before == [], "scoped_checkout_dirty_before")
        for command_id, display_command, pattern in COMMAND_SPECS:
            argv = command_argv(pattern)
            progress(f"{command_id}_started")
            completed = subprocess.run(
                argv,
                cwd=checkout,
                check=False,
                capture_output=True,
            )
            outputs[command_id] = (completed.stdout, completed.stderr)
            command_rows.append(
                {
                    "command_id": command_id,
                    "command": display_command,
                    "argv": argv,
                    "exit_code": completed.returncode,
                    "status": (
                        "PASS" if completed.returncode == 0 else "FAIL"
                    ),
                    "stdout_sha256": sha256_bytes(completed.stdout),
                    "stdout_byte_count": len(completed.stdout),
                    "stderr_sha256": sha256_bytes(completed.stderr),
                    "stderr_byte_count": len(completed.stderr),
                }
            )
            progress(f"{command_id}_finished")
        checkout_after = repository_status(checkout)
    finally:
        if checkout.exists():
            shutil.rmtree(checkout)
        cleanup_status = (
            "PASS"
            if work_root.is_dir() and not any(work_root.iterdir())
            else "FAIL"
        )
    require(
        len(command_rows) == len(COMMAND_SPECS)
        and all(row["exit_code"] == 0 for row in command_rows),
        "scoped_validation_command_failure",
    )
    require(checkout_after == [], "scoped_checkout_dirty_after")
    require(cleanup_status == "PASS", "scoped_checkout_cleanup_failed")
    source_after = repository_status(repo)
    require(source_after == [], "source_repository_dirty_after_scoped_validation")
    return (
        {
            "source_repository_status_before": source_before,
            "source_repository_status_after": source_after,
            "external_checkout_status_before": checkout_before,
            "external_checkout_status_after": checkout_after,
            "external_checkout_cleanup_status": cleanup_status,
            "external_work_root": work_root.as_posix(),
            "external_work_root_empty_after": True,
            "commands": command_rows,
        },
        outputs,
    )


def write_scoped_receipt(
    repo: Path,
    attempt_root: Path,
    subject: dict[str, str],
    execution: dict[str, Any],
    outputs: dict[str, tuple[bytes, bytes]],
) -> tuple[Path, dict[str, Any]]:
    phase = attempt_root / "phase13_closeout"
    log_root = phase / "vc1_command_logs"
    rows: list[dict[str, Any]] = []
    for row in execution["commands"]:
        command_id = row["command_id"]
        stdout, stderr = outputs[command_id]
        stdout_path = log_root / f"{command_id}.stdout.bin"
        stderr_path = log_root / f"{command_id}.stderr.bin"
        write_bytes_once(stdout_path, stdout)
        write_bytes_once(stderr_path, stderr)
        rows.append(
            {
                **row,
                "stdout_path": stdout_path.relative_to(repo).as_posix(),
                "stderr_path": stderr_path.relative_to(repo).as_posix(),
            }
        )
    receipt = {
        "schema_version": f"{SCHEMA_PREFIX}-scoped-receipt-v1",
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "validation_subject": subject,
        "owner_scope": "food_semantic_authority_and_direct_D16_handoff_only",
        "execution_mode": "external_disposable_git_clone",
        "test_command_count": len(rows),
        "commands": rows,
        **{
            key: value
            for key, value in execution.items()
            if key != "commands"
        },
        "caller_supplied_exit_code_count": 0,
        "full_repository_gate_execution_count": 0,
        "direct_all_unittest_discovery_execution_count": 0,
    }
    receipt_path = phase / FOCUSED_RECEIPT_NAME
    write_json_once(receipt_path, receipt)
    return receipt_path, receipt


def validate_scoped_receipt(
    repo: Path,
    attempt_root: Path,
    subject: dict[str, str],
) -> tuple[Path, dict[str, Any]]:
    phase = attempt_root / "phase13_closeout"
    receipt_path = phase / FOCUSED_RECEIPT_NAME
    receipt = load_object(receipt_path)
    expected_rows: list[dict[str, Any]] = []
    actual_rows = receipt.get("commands")
    require(isinstance(actual_rows, list), "scoped_receipt_commands_missing")
    require(
        len(actual_rows) == len(COMMAND_SPECS),
        "scoped_receipt_command_count_mismatch",
    )
    for index, (command_id, display_command, pattern) in enumerate(
        COMMAND_SPECS
    ):
        actual = actual_rows[index]
        require(isinstance(actual, dict), "scoped_receipt_command_invalid")
        stdout_path = (
            phase / "vc1_command_logs" / f"{command_id}.stdout.bin"
        )
        stderr_path = (
            phase / "vc1_command_logs" / f"{command_id}.stderr.bin"
        )
        expected_rows.append(
            {
                "command_id": command_id,
                "command": display_command,
                "argv": command_argv(pattern),
                "exit_code": 0,
                "status": "PASS",
                "stdout_sha256": sha256_file(stdout_path),
                "stdout_byte_count": stdout_path.stat().st_size,
                "stderr_sha256": sha256_file(stderr_path),
                "stderr_byte_count": stderr_path.stat().st_size,
                "stdout_path": stdout_path.relative_to(repo).as_posix(),
                "stderr_path": stderr_path.relative_to(repo).as_posix(),
            }
        )
    expected = {
        "schema_version": f"{SCHEMA_PREFIX}-scoped-receipt-v1",
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "validation_subject": subject,
        "owner_scope": "food_semantic_authority_and_direct_D16_handoff_only",
        "execution_mode": "external_disposable_git_clone",
        "test_command_count": len(expected_rows),
        "commands": expected_rows,
        "source_repository_status_before": [],
        "source_repository_status_after": [],
        "external_checkout_status_before": [],
        "external_checkout_status_after": [],
        "external_checkout_cleanup_status": "PASS",
        "external_work_root": FOCUSED_WORK_ROOT.resolve().as_posix(),
        "external_work_root_empty_after": True,
        "caller_supplied_exit_code_count": 0,
        "full_repository_gate_execution_count": 0,
        "direct_all_unittest_discovery_execution_count": 0,
    }
    require(receipt == expected, "scoped_receipt_canonical_structure_mismatch")
    return receipt_path, receipt


def build_validation_result(
    repo: Path,
    attempt_root: Path,
    subject: dict[str, str],
    receipt_path: Path,
    receipt: dict[str, Any],
    authority_binding: dict[str, Any],
    correction_review: dict[str, Any],
) -> dict[str, Any]:
    phase = attempt_root / "phase13_closeout"
    failure_path = phase / "post_authority_validation_failure.json"
    correction_review_path = phase / CORRECTION_REVIEW_NAME
    commands = {
        row["command_id"]: {
            key: row[key]
            for key in (
                "command",
                "argv",
                "exit_code",
                "status",
                "stdout_path",
                "stdout_sha256",
                "stderr_path",
                "stderr_sha256",
            )
        }
        for row in receipt["commands"]
    }
    commands.update(
        {
            "current_route": {
                "selected_branch": "B+G2",
                "status": "NOT_APPLICABLE",
                "exit_code": None,
                "fake_success_code_allowed": False,
                "future_G1_rule_unchanged": True,
            },
            "full_repository_gate": {
                "status": "NOT_EXECUTED_OUT_OF_SCOPE",
                "exit_code": None,
                "owner_scope_direction_sha256": (
                    EXPECTED_SCOPE_DIRECTION_SHA256
                ),
                "waiver_created": False,
            },
            "direct_all_unittest_discovery": {
                "status": "PRESERVED_FAIL_DIAGNOSTIC_ONLY",
                "terminal_gate_credit": 0,
                "waiver_created": False,
                "failure_evidence_path": failure_path.relative_to(
                    repo
                ).as_posix(),
                "failure_evidence_sha256": EXPECTED_FAILURE_SHA256,
            },
        }
    )
    return {
        "schema_version": "food-semantic-post-authority-validation-vc1-v2",
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "validation_contract": "VC-1+owner-scoped-Appendix-C",
        "validation_subject": subject,
        "commands": commands,
        "command_group_count": 6,
        "failed_command_count": 0,
        "applicable_command_group_count": 3,
        "applicable_failed_command_count": 0,
        "not_applicable_or_out_of_scope_command_group_count": 2,
        "diagnostic_only_command_group_count": 1,
        "scoped_validation_receipt_path": receipt_path.relative_to(
            repo
        ).as_posix(),
        "scoped_validation_receipt_sha256": sha256_file(receipt_path),
        "authority_binding": authority_binding,
        "correction_review": {
            **correction_review,
            "sha256": sha256_file(correction_review_path),
        },
        "current_facts_manifest_mutation_count": 0,
        "sealed_non_current_successor_preserved": True,
        "closeout_may_prepare": True,
    }


def record_validation(args: argparse.Namespace) -> dict[str, Any]:
    repo = Path(args.repo).resolve()
    attempt_root = ensure_attempt_root(repo, Path(args.attempt_root))
    validation_subject = git_subject(repo, "HEAD")
    authority_binding = validate_bound_authority(
        repo, attempt_root, validation_subject
    )
    correction_review = validate_correction_review(
        repo, attempt_root, validation_subject
    )
    execution, outputs = run_scoped_validation_commands(
        repo, validation_subject
    )
    receipt_path, receipt = write_scoped_receipt(
        repo,
        attempt_root,
        validation_subject,
        execution,
        outputs,
    )
    receipt_path, receipt = validate_scoped_receipt(
        repo, attempt_root, validation_subject
    )
    result = build_validation_result(
        repo,
        attempt_root,
        validation_subject,
        receipt_path,
        receipt,
        authority_binding,
        correction_review,
    )
    result_path = (
        attempt_root
        / "phase13_closeout/post_authority_validation_result.json"
    )
    write_json_once(result_path, result)
    return {
        "status": "PASS",
        "validation_subject": validation_subject,
        "applicable_command_group_count": 3,
        "post_authority_validation_result_sha256": sha256_file(result_path),
        "scoped_validation_receipt_sha256": sha256_file(receipt_path),
    }


def validate_recorded(args: argparse.Namespace) -> dict[str, Any]:
    repo = Path(args.repo).resolve()
    attempt_root = ensure_attempt_root(repo, Path(args.attempt_root))
    phase = attempt_root / "phase13_closeout"
    receipt_path = phase / FOCUSED_RECEIPT_NAME
    receipt = load_object(receipt_path)
    subject = receipt.get("validation_subject")
    require(isinstance(subject, dict), "recorded_validation_subject_missing")
    require(
        git_subject(repo, str(subject.get("commit", ""))) == subject,
        "recorded_validation_subject_git_mismatch",
    )
    authority_binding = validate_bound_authority(
        repo, attempt_root, subject
    )
    correction_review = validate_correction_review(
        repo, attempt_root, subject
    )
    receipt_path, receipt = validate_scoped_receipt(
        repo, attempt_root, subject
    )
    expected_result = build_validation_result(
        repo,
        attempt_root,
        subject,
        receipt_path,
        receipt,
        authority_binding,
        correction_review,
    )
    result_path = phase / "post_authority_validation_result.json"
    result = load_object(result_path)
    require(
        result == expected_result,
        "recorded_validation_canonical_structure_mismatch",
    )
    return {
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "validation_subject": subject,
        "post_authority_validation_result_sha256": sha256_file(result_path),
        "scoped_validation_receipt_sha256": sha256_file(receipt_path),
        "repository_only_revalidation": True,
        "full_repository_gate_execution_count": 0,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Record or validate the owner-ratified VC-1 contract."
    )
    parser.add_argument("command", choices=("record", "validate"))
    parser.add_argument("--repo", required=True)
    parser.add_argument("--attempt-root", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "record":
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
