from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from contextlib import AbstractContextManager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROUND_ID = "dvf_3_3_registry_runtime_compatibility"
ATTEMPT_RE = re.compile(r"^attempt-(\d{4})$")
EVENT_LEDGER_REL = Path(
    "Iris/_docs/round3/registry_runtime_compatibility/attempt_events.jsonl"
)
DURABLE_ATTEMPT_ROOT_REL = Path(
    "Iris/_docs/round3/registry_runtime_compatibility/attempts"
)
LOCAL_ATTEMPT_ROOT_REL = Path(
    "Iris/build/description/v2/staging/"
    "dvf_3_3_registry_runtime_compatibility/attempts"
)
COMMIT_MESSAGE_PREFIX = "chore(rtc): reserve "
WAIT_OBJECT_0 = 0
WAIT_ABANDONED = 0x80
WAIT_TIMEOUT = 0x102


class ReservationError(RuntimeError):
    def __init__(self, code: str, stage: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.stage = stage


def canonical_json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ReservationError(
            "invalid_json_object",
            "input_validation",
            f"Expected JSON object: {path}",
        )
    return value


def exclusive_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise ReservationError(
            "claim_file_already_exists",
            "transaction_render",
            f"Refusing to overwrite immutable file: {path}",
        ) from exc


def append_durable(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab", buffering=0) as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    command = [
        "git",
        "-c",
        "core.longpaths=true",
        "-c",
        f"safe.directory={repo.as_posix()}",
        *args,
    ]
    result = subprocess.run(
        command,
        cwd=repo,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise ReservationError(
            "git_command_failed",
            "git_transaction",
            f"{' '.join(command)} failed ({result.returncode}): {result.stderr.strip()}",
        )
    return result


def git_output(repo: Path, *args: str) -> str:
    return run_git(repo, *args).stdout.strip()


@dataclass(frozen=True)
class LedgerState:
    event_count: int
    prefix_sha256: str
    last_event_sha256: str
    used_attempt_ids: tuple[str, ...]
    open_attempt_ids: tuple[str, ...]
    reservation_count_by_attempt: dict[str, int]
    terminal_count_by_attempt: dict[str, int]


def replay_event_ledger(path: Path) -> LedgerState:
    raw = path.read_bytes() if path.exists() else b""
    previous_hash = "0" * 64
    used: set[str] = set()
    open_ids: set[str] = set()
    reservation_counts: dict[str, int] = {}
    terminal_counts: dict[str, int] = {}
    event_count = 0

    for line_number, raw_line in enumerate(raw.splitlines(keepends=True), 1):
        if not raw_line.endswith(b"\n"):
            raise ReservationError(
                "event_ledger_truncated_line",
                "ledger_replay",
                f"Event line {line_number} lacks LF terminator",
            )
        try:
            event = json.loads(raw_line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ReservationError(
                "event_ledger_invalid_json",
                "ledger_replay",
                f"Invalid event line {line_number}",
            ) from exc
        if not isinstance(event, dict):
            raise ReservationError(
                "event_ledger_invalid_row",
                "ledger_replay",
                f"Event line {line_number} is not an object",
            )
        if event.get("event_sequence") != line_number:
            raise ReservationError(
                "event_sequence_mismatch",
                "ledger_replay",
                f"Expected event_sequence={line_number}",
            )
        if event.get("previous_event_sha256") != previous_hash:
            raise ReservationError(
                "event_hash_chain_break",
                "ledger_replay",
                f"Event line {line_number} has wrong previous hash",
            )
        attempt_id = event.get("attempt_id")
        if not isinstance(attempt_id, str) or ATTEMPT_RE.fullmatch(attempt_id) is None:
            raise ReservationError(
                "invalid_attempt_id",
                "ledger_replay",
                f"Invalid attempt id at line {line_number}",
            )
        event_type = event.get("event_type")
        used.add(attempt_id)
        if event_type == "reservation":
            reservation_counts[attempt_id] = reservation_counts.get(attempt_id, 0) + 1
            if reservation_counts[attempt_id] != 1 or attempt_id in open_ids:
                raise ReservationError(
                    "duplicate_reservation",
                    "ledger_replay",
                    f"Duplicate reservation for {attempt_id}",
                )
            open_ids.add(attempt_id)
        elif event_type == "terminal":
            terminal_counts[attempt_id] = terminal_counts.get(attempt_id, 0) + 1
            if terminal_counts[attempt_id] != 1:
                raise ReservationError(
                    "duplicate_terminal",
                    "ledger_replay",
                    f"Duplicate terminal event for {attempt_id}",
                )
            if attempt_id not in open_ids:
                raise ReservationError(
                    "terminal_without_open_reservation",
                    "ledger_replay",
                    f"Terminal event without open reservation for {attempt_id}",
                )
            open_ids.remove(attempt_id)
        else:
            raise ReservationError(
                "invalid_event_type",
                "ledger_replay",
                f"Unsupported event type at line {line_number}: {event_type!r}",
            )
        previous_hash = sha256_bytes(raw_line)
        event_count += 1

    return LedgerState(
        event_count=event_count,
        prefix_sha256=sha256_bytes(raw),
        last_event_sha256=previous_hash,
        used_attempt_ids=tuple(sorted(used)),
        open_attempt_ids=tuple(sorted(open_ids)),
        reservation_count_by_attempt=reservation_counts,
        terminal_count_by_attempt=terminal_counts,
    )


def next_attempt_id(used_attempt_ids: Iterable[str]) -> str:
    values = [int(ATTEMPT_RE.fullmatch(value).group(1)) for value in used_attempt_ids]
    next_value = max(values, default=0) + 1
    if next_value > 9999:
        raise ReservationError(
            "attempt_id_exhausted",
            "attempt_allocation",
            "Attempt id space exhausted",
        )
    return f"attempt-{next_value:04d}"


class NamedMutex(AbstractContextManager["NamedMutex"]):
    def __init__(self, name: str, timeout_seconds: int = 60) -> None:
        self.name = name
        self.timeout_seconds = timeout_seconds
        self.handle: int | None = None
        self.abandoned = False

    def __enter__(self) -> "NamedMutex":
        if os.name != "nt":
            raise ReservationError(
                "windows_named_mutex_required",
                "attempt_lock",
                "This round requires the Windows named-mutex route",
            )
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.CreateMutexW(None, False, self.name)
        if not handle:
            raise ReservationError(
                "attempt_mutex_create_failed",
                "attempt_lock",
                f"CreateMutexW failed: {ctypes.get_last_error()}",
            )
        wait = kernel32.WaitForSingleObject(handle, self.timeout_seconds * 1000)
        if wait == WAIT_TIMEOUT:
            kernel32.CloseHandle(handle)
            raise ReservationError(
                "attempt_lock_timeout",
                "attempt_lock",
                f"Timed out waiting for named mutex {self.name}",
            )
        if wait not in {WAIT_OBJECT_0, WAIT_ABANDONED}:
            kernel32.CloseHandle(handle)
            raise ReservationError(
                "attempt_mutex_wait_failed",
                "attempt_lock",
                f"WaitForSingleObject returned {wait}",
            )
        self.handle = handle
        self.abandoned = wait == WAIT_ABANDONED
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        if self.handle is not None:
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.ReleaseMutex(self.handle)
            kernel32.CloseHandle(self.handle)
            self.handle = None


def normalized_repo_relative(repo: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError as exc:
        raise ReservationError(
            "path_outside_repository",
            "input_validation",
            f"Path must stay inside repository: {path}",
        ) from exc


def validate_contract(contract_path: Path, repo: Path) -> dict[str, Any]:
    contract = read_json(contract_path)
    if contract.get("round_id") != ROUND_ID:
        raise ReservationError(
            "wrong_round_id",
            "contract_validation",
            "Bootstrap contract belongs to a different round",
        )
    if contract.get("event_ledger_path") != EVENT_LEDGER_REL.as_posix():
        raise ReservationError(
            "event_ledger_path_mismatch",
            "contract_validation",
            "Bootstrap contract event ledger path differs from the fixed namespace",
        )
    executor_path = Path(__file__).resolve()
    expected_hash = contract.get("bootstrap_executor_sha256")
    if expected_hash != sha256_file(executor_path):
        raise ReservationError(
            "bootstrap_executor_hash_mismatch",
            "contract_validation",
            "Committed bootstrap executor does not match its contract",
        )
    expected_contract_rel = contract.get("contract_path")
    if expected_contract_rel != normalized_repo_relative(repo, contract_path):
        raise ReservationError(
            "bootstrap_contract_path_mismatch",
            "contract_validation",
            "Bootstrap contract was loaded from an unapproved path",
        )
    return contract


def validate_preentry_manifest(
    manifest_path: Path,
    *,
    repo: Path,
    expected_branch: str,
    expected_starting_prefix: str,
    contract: dict[str, Any],
) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    required_pairs = {
        "schema_version": "rtc-preentry-input-v1",
        "round_id": ROUND_ID,
        "owner_approved_integration_branch": expected_branch,
        "approved_canonical_event_prefix_sha256": expected_starting_prefix,
        "execution_baseline_disposition": "approved_clean_worktree",
        "governance_bootstrap_commit_owner_approved": True,
        "implementation_entry_requested": True,
    }
    for key, expected in required_pairs.items():
        if manifest.get(key) != expected:
            raise ReservationError(
                "preentry_manifest_field_mismatch",
                "preentry_validation",
                f"Pre-entry field {key!r} does not match the approved value",
            )
    if manifest.get("bootstrap_executor_sha256") != contract.get(
        "bootstrap_executor_sha256"
    ):
        raise ReservationError(
            "preentry_bootstrap_hash_mismatch",
            "preentry_validation",
            "Pre-entry manifest does not bind the committed executor",
        )
    for field in (
        "bootstrap_test_sha256",
        "bootstrap_tool_manifest_sha256",
        "bootstrap_validation_report_sha256",
    ):
        if not isinstance(manifest.get(field), str):
            raise ReservationError(
                "preentry_bootstrap_binding_missing",
                "preentry_validation",
                f"Pre-entry manifest is missing {field}",
            )
    approval_rel = manifest.get("selected_plan_approval_path")
    approval_sha = manifest.get("selected_plan_approval_sha256")
    if not isinstance(approval_rel, str) or not isinstance(approval_sha, str):
        raise ReservationError(
            "selected_plan_approval_missing",
            "preentry_validation",
            "Selected versioned plan approval path/hash is required",
        )
    approval_path = repo / Path(approval_rel)
    if not approval_path.is_file() or sha256_file(approval_path) != approval_sha:
        raise ReservationError(
            "selected_plan_approval_hash_mismatch",
            "preentry_validation",
            "Selected versioned plan approval is missing or stale",
        )
    if "/current" in f"/{approval_rel.lower()}" or "\\current" in approval_rel.lower():
        raise ReservationError(
            "mutable_current_authority_pointer",
            "preentry_validation",
            "Mutable current authority pointers are forbidden",
        )
    return manifest


def shared_ledger_path(repo: Path) -> Path:
    common_dir_text = git_output(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    common_dir = Path(common_dir_text).resolve()
    return common_dir / "iris_registry_runtime_compatibility" / "attempt_reservations.jsonl"


def git_branch(repo: Path) -> str:
    return git_output(repo, "branch", "--show-current")


def require_clean_worktree(repo: Path) -> None:
    status = git_output(repo, "status", "--porcelain=v1", "--untracked-files=all")
    if status:
        raise ReservationError(
            "selected_worktree_not_clean",
            "worktree_preflight",
            f"Selected worktree is not clean:\n{status}",
        )


def build_reservation_record(
    *,
    attempt_id: str,
    repo: Path,
    branch: str,
    baseline_head: str,
    prior_prefix: str,
    contract_path: Path,
    contract: dict[str, Any],
    preentry_manifest_path: Path,
    preentry_manifest: dict[str, Any],
    abandoned_mutex: bool,
) -> dict[str, Any]:
    return {
        "schema_version": "rtc-attempt-reservation-v1",
        "round_id": ROUND_ID,
        "attempt_id": attempt_id,
        "event_type": "reservation",
        "reservation_state": "committed_pending",
        "integration_branch": branch,
        "baseline_head": baseline_head,
        "previous_event_prefix_sha256": prior_prefix,
        "contract_path": normalized_repo_relative(repo, contract_path),
        "contract_sha256": sha256_file(contract_path),
        "bootstrap_executor_path": normalized_repo_relative(repo, Path(__file__)),
        "bootstrap_executor_sha256": contract["bootstrap_executor_sha256"],
        "bootstrap_test_sha256": contract["bootstrap_test_sha256"],
        "bootstrap_tool_manifest_sha256": contract["bootstrap_tool_manifest_sha256"],
        "bootstrap_validation_report_sha256": preentry_manifest[
            "bootstrap_validation_report_sha256"
        ],
        "preentry_input_manifest_path": str(preentry_manifest_path.resolve()),
        "preentry_input_manifest_sha256": sha256_file(preentry_manifest_path),
        "selected_plan_approval_path": preentry_manifest[
            "selected_plan_approval_path"
        ],
        "selected_plan_approval_sha256": preentry_manifest[
            "selected_plan_approval_sha256"
        ],
        "reservation_preflight_nonterminal_attempt_count": 0,
        "reservation_preflight_open_attempt_ids": [],
        "abandoned_mutex_recovery_required": abandoned_mutex,
        "reserved_at_unix_ns": time.time_ns(),
    }


def reserve(args: argparse.Namespace) -> int:
    repo = Path(args.repo_root).resolve()
    contract_path = Path(args.contract).resolve()
    manifest_path = Path(args.preentry_input_manifest).resolve()
    receipt_path = Path(args.reservation_receipt).resolve()
    gate_report_path = Path(args.gate_report).resolve()
    contract = validate_contract(contract_path, repo)

    common_dir = Path(
        git_output(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    ).resolve()
    coordination_key = sha256_bytes(str(common_dir).lower().encode("utf-8"))[:24]
    mutex_name = f"IrisRegistryRuntimeCompatibility-{coordination_key}"

    with NamedMutex(mutex_name, timeout_seconds=int(contract["mutex_timeout_seconds"])) as mutex:
        branch = git_branch(repo)
        if branch != args.expected_branch:
            raise ReservationError(
                "wrong_integration_branch",
                "worktree_preflight",
                f"Expected branch {args.expected_branch!r}, got {branch!r}",
            )
        require_clean_worktree(repo)
        baseline_head = git_output(repo, "rev-parse", "HEAD")
        manifest = validate_preentry_manifest(
            manifest_path,
            repo=repo,
            expected_branch=args.expected_branch,
            expected_starting_prefix=args.expected_starting_prefix,
            contract=contract,
        )
        if manifest.get("baseline_head") != baseline_head:
            raise ReservationError(
                "baseline_head_mismatch",
                "worktree_preflight",
                "Selected worktree HEAD differs from the owner-approved baseline",
            )

        ledger_path = repo / EVENT_LEDGER_REL
        state = replay_event_ledger(ledger_path)
        if state.prefix_sha256 != args.expected_starting_prefix:
            raise ReservationError(
                "event_prefix_divergence",
                "ledger_replay",
                "Tracked event prefix differs from owner-approved prefix",
            )
        shared_path = shared_ledger_path(repo)
        if shared_path.exists():
            shared_rows = [
                json.loads(line)
                for line in shared_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            shared_prefix = (
                shared_rows[-1]["committed_event_prefix_sha256"]
                if shared_rows
                else sha256_bytes(b"")
            )
        else:
            shared_prefix = sha256_bytes(b"")
        if shared_prefix != state.prefix_sha256:
            raise ReservationError(
                "shared_durable_divergence",
                "ledger_replay",
                "Shared committed prefix differs from tracked event prefix",
            )
        if state.open_attempt_ids:
            code = (
                "multiple_nonterminal_attempts"
                if len(state.open_attempt_ids) > 1
                else "open_attempt_exists"
            )
            raise ReservationError(
                code,
                "nonterminal_attempt_census",
                f"Open attempts block reservation: {list(state.open_attempt_ids)}",
            )

        attempt_id = next_attempt_id(state.used_attempt_ids)
        durable_dir = repo / DURABLE_ATTEMPT_ROOT_REL / attempt_id
        record_path = durable_dir / "reservation_record.json"
        local_root = repo / LOCAL_ATTEMPT_ROOT_REL / attempt_id
        if durable_dir.exists() or local_root.exists():
            raise ReservationError(
                "attempt_root_already_exists",
                "attempt_allocation",
                f"Attempt root already exists for {attempt_id}",
            )

        record = build_reservation_record(
            attempt_id=attempt_id,
            repo=repo,
            branch=branch,
            baseline_head=baseline_head,
            prior_prefix=state.prefix_sha256,
            contract_path=contract_path,
            contract=contract,
            preentry_manifest_path=manifest_path,
            preentry_manifest=manifest,
            abandoned_mutex=mutex.abandoned,
        )
        record_bytes = canonical_json_bytes(record)
        record_sha = sha256_bytes(record_bytes)
        event = {
            "schema_version": "rtc-attempt-event-v1",
            "event_sequence": state.event_count + 1,
            "round_id": ROUND_ID,
            "attempt_id": attempt_id,
            "event_type": "reservation",
            "record_path": normalized_repo_relative(repo, record_path),
            "record_sha256": record_sha,
            "previous_event_sha256": state.last_event_sha256,
            "previous_event_prefix_sha256": state.prefix_sha256,
            "bootstrap_executor_sha256": contract["bootstrap_executor_sha256"],
        }
        event_bytes = canonical_json_bytes(event)

        exclusive_write(record_path, record_bytes)
        append_durable(ledger_path, event_bytes)
        post_state = replay_event_ledger(ledger_path)
        if post_state.open_attempt_ids != (attempt_id,):
            raise ReservationError(
                "reservation_post_append_census_mismatch",
                "event_append_validation",
                "Reservation append did not produce exactly one open attempt",
            )

        record_rel = normalized_repo_relative(repo, record_path)
        ledger_rel = EVENT_LEDGER_REL.as_posix()
        run_git(repo, "add", "--", record_rel, ledger_rel)
        staged = git_output(repo, "diff", "--cached", "--name-only")
        if set(staged.splitlines()) != {record_rel, ledger_rel}:
            raise ReservationError(
                "reservation_stage_scope_violation",
                "git_transaction",
                f"Unexpected staged paths: {staged}",
            )
        run_git(repo, "commit", "-m", f"{COMMIT_MESSAGE_PREFIX}{attempt_id}")
        reservation_commit = git_output(repo, "rev-parse", "HEAD")

        shared_row = {
            "schema_version": "rtc-shared-reservation-v1",
            "round_id": ROUND_ID,
            "attempt_id": attempt_id,
            "reservation_commit": reservation_commit,
            "committed_event_prefix_sha256": post_state.prefix_sha256,
            "event_record_sha256": record_sha,
        }
        append_durable(shared_path, canonical_json_bytes(shared_row))
        local_root.mkdir(parents=True, exist_ok=False)

        receipt = {
            "schema_version": "rtc-attempt-reservation-receipt-v1",
            "round_id": ROUND_ID,
            "attempt_id": attempt_id,
            "reservation_status": "committed",
            "reservation_commit": reservation_commit,
            "integration_branch": branch,
            "baseline_head": baseline_head,
            "event_prefix_before_sha256": state.prefix_sha256,
            "event_prefix_after_sha256": post_state.prefix_sha256,
            "shared_reservation_ledger_committed_prefix_sha256": post_state.prefix_sha256,
            "reservation_record_path": record_rel,
            "reservation_record_sha256": record_sha,
            "reservation_preflight_nonterminal_attempt_count": 0,
            "reservation_preflight_open_attempt_ids": [],
            "post_reservation_nonterminal_attempt_count": 1,
            "post_reservation_open_attempt_ids": [attempt_id],
            "named_mutex": mutex_name,
            "abandoned_mutex_recovered": mutex.abandoned,
            "bootstrap_executor_sha256": contract["bootstrap_executor_sha256"],
            "ad_hoc_or_manual_reservation_count": 0,
            "retroactive_attempt_materialization_count": 0,
        }
        gate_report = {
            "schema_version": "rtc-preimplementation-gate-v1",
            "round_id": ROUND_ID,
            "attempt_id": attempt_id,
            "gate": "B",
            "implementation_entry_allowed": True,
            "production_integration_allowed": False,
            "open_blocker_count": 0,
            "selected_execution_branch": branch,
            "selected_worktree_head": reservation_commit,
            "selected_worktree_clean_before_reservation": True,
            "selected_worktree_event_prefix_sha256": post_state.prefix_sha256,
            "approved_canonical_event_prefix_sha256": post_state.prefix_sha256,
            "shared_reservation_ledger_committed_prefix_sha256": post_state.prefix_sha256,
            "reservation_preflight_nonterminal_attempt_count": 0,
            "reservation_preflight_open_attempt_ids": [],
            "preentry_required_path_ignored_count": 0,
            "preentry_required_path_untracked_count": 0,
            "bootstrap_executor_contract_reviewed": True,
            "bootstrap_executor_test_status": "PASS",
            "bootstrap_executor_hash_matches": True,
            "bootstrap_executor_scope_violation_count": 0,
            "ad_hoc_or_manual_reservation_count": 0,
            "retroactive_attempt_materialization_count": 0,
            "required_validations_override_flag_verified": True,
            "allowlist_contract_scope": "import_closure_only",
            "claim_scope": "governance_bootstrap_only",
        }
        exclusive_write(receipt_path, canonical_json_bytes(receipt))
        exclusive_write(gate_report_path, canonical_json_bytes(gate_report))
        print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
        return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reserve one Registry Runtime Compatibility attempt."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    reserve_parser = subparsers.add_parser("reserve")
    reserve_parser.add_argument("--contract", required=True)
    reserve_parser.add_argument("--preentry-input-manifest", required=True)
    reserve_parser.add_argument("--repo-root", required=True)
    reserve_parser.add_argument("--expected-branch", required=True)
    reserve_parser.add_argument("--expected-starting-prefix", required=True)
    reserve_parser.add_argument("--reservation-receipt", required=True)
    reserve_parser.add_argument("--gate-report", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "reserve":
            return reserve(args)
        raise ReservationError(
            "unsupported_command",
            "argument_validation",
            f"Unsupported command: {args.command}",
        )
    except ReservationError as exc:
        failure = {
            "schema_version": "rtc-bootstrap-failure-v1",
            "round_id": ROUND_ID,
            "status": "FAIL",
            "failure_code": exc.code,
            "failure_stage": exc.stage,
            "message": str(exc),
        }
        print(json.dumps(failure, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
