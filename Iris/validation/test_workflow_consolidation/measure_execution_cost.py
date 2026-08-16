from __future__ import annotations

import argparse
import json
import os
import random
import re
import signal
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

try:
    from ._common import (
        committed_blob_identity,
        ContractError,
        environment_identity,
        git,
        ignored_worktree_entries,
        interpreter_identity,
        normalized_command_signature,
        percentile,
        read_json,
        read_jsonl,
        require,
        require_path_outside_repositories,
        resolve_within,
        sha256_bytes,
        sha256_file,
        subject_identity,
        write_json,
    )
except ImportError:  # Direct script execution.
    from _common import (
        committed_blob_identity,
        ContractError,
        environment_identity,
        git,
        ignored_worktree_entries,
        interpreter_identity,
        normalized_command_signature,
        percentile,
        read_json,
        read_jsonl,
        require,
        require_path_outside_repositories,
        resolve_within,
        sha256_bytes,
        sha256_file,
        subject_identity,
        write_json,
    )


CLI_SCHEMA_VERSION = "iris-test-workflow-cost-cli-v1"
CONTRACT_SCHEMA = "iris_test_workflow_measurement_contract_v1"
RECEIPT_SCHEMA = "iris_test_workflow_measurement_receipt_v1"
SCHEDULE_SCHEMA = "iris_test_workflow_accepted_session_schedule_v1"
RESOURCE_SCHEMA = "iris_test_workflow_session_resource_estimate_v1"


OBSERVER_SOURCE = r'''from __future__ import annotations
import atexit
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading

_root_value = os.environ.get("IRIS_WF_OBSERVER_EVENT_ROOT")
_root = Path(_root_value) if _root_value else None
_emit_lock = threading.Lock()
_sequence = 0

def _safe(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, os.PathLike):
        return os.fspath(value)
    if isinstance(value, (list, tuple)):
        return [_safe(item) for item in value]
    return repr(value)

def _emit(kind, **fields):
    global _sequence
    if _root is None:
        return
    with _emit_lock:
        _sequence += 1
        _root.mkdir(parents=True, exist_ok=True)
        target = _root / ("events-" + str(os.getpid()) + ".jsonl")
        row = {"kind": kind, "pid": os.getpid(), "sequence": _sequence, **fields}
        with target.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")

_emit("observer_start", parent_pid=os.getppid())
atexit.register(lambda: _emit("observer_complete"))

def _python_observer_expected(args):
    if isinstance(args, (list, tuple)) and args:
        executable = os.fspath(args[0])
    elif isinstance(args, str) and args.strip():
        executable = args.strip().split(maxsplit=1)[0].strip('"')
    else:
        return False
    normalized = os.path.normcase(os.path.abspath(executable))
    if normalized == os.path.normcase(os.path.abspath(sys.executable)):
        return True
    name = os.path.basename(executable).lower()
    return re.fullmatch(r"python(?:w)?(?:[0-9]+(?:\.[0-9]+)*)?(?:\.exe)?", name) is not None

_original_popen = subprocess.Popen
class _ObservedPopen(_original_popen):
    def __init__(self, args, *positional, **kwargs):
        super().__init__(args, *positional, **kwargs)
        _emit(
            "subprocess",
            argv=_safe(args),
            cwd=_safe(kwargs.get("cwd")),
            child_pid=self.pid,
            python_observer_expected=_python_observer_expected(args),
        )
subprocess.Popen = _ObservedPopen

_original_mkdtemp = tempfile.mkdtemp
def _observed_mkdtemp(*args, **kwargs):
    result = _original_mkdtemp(*args, **kwargs)
    _emit("materialization", operation="mkdtemp")
    return result
tempfile.mkdtemp = _observed_mkdtemp

_copy_depth = 0
def _copy_bytes(src):
    try:
        return os.stat(src).st_size
    except OSError:
        return None

_original_copyfile = shutil.copyfile
def _observed_copyfile(src, dst, *args, **kwargs):
    global _copy_depth
    outermost = _copy_depth == 0
    _copy_depth += 1
    try:
        result = _original_copyfile(src, dst, *args, **kwargs)
    finally:
        _copy_depth -= 1
    if outermost:
        _emit("copy", operation="copyfile", copied_bytes=_copy_bytes(src))
    return result
shutil.copyfile = _observed_copyfile

try:
    import _winapi
    _original_copy_file_2 = _winapi.CopyFile2
    def _observed_copy_file_2(src, dst, *args, **kwargs):
        global _copy_depth
        outermost = _copy_depth == 0
        _copy_depth += 1
        try:
            result = _original_copy_file_2(src, dst, *args, **kwargs)
        finally:
            _copy_depth -= 1
        if outermost:
            _emit("copy", operation="CopyFile2", copied_bytes=_copy_bytes(src))
        return result
    _winapi.CopyFile2 = _observed_copy_file_2
except (ImportError, AttributeError):
    pass
'''


def protocol_identity(contract_path: Path) -> dict[str, str]:
    repo = Path(git(contract_path.parent, "rev-parse", "--show-toplevel"))
    identity = committed_blob_identity(repo, contract_path)
    return {
        "schema_version": CONTRACT_SCHEMA,
        "canonical_contract_path": identity["canonical_path"],
        "raw_sha256": identity["raw_sha256"],
        "git_blob_id": identity["git_blob_id"],
    }


def load_contract(path: Path) -> tuple[dict[str, Any], bytes, dict[str, str]]:
    raw = path.read_bytes()
    try:
        contract = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ContractError(f"malformed measurement contract: {error}") from error
    require(contract.get("schema_version") == CONTRACT_SCHEMA, "measurement contract schema mismatch")
    return contract, raw, protocol_identity(path)


def ensure_contract_unchanged(path: Path, initial: bytes) -> None:
    require(path.read_bytes() == initial, "measurement contract changed during execution")


def write_receipt_after_contract_check(
    output: Path,
    receipt: dict[str, Any],
    contract_path: Path,
    contract_raw: bytes,
) -> None:
    ensure_contract_unchanged(contract_path, contract_raw)
    write_json(output, receipt)


def tooling_identity(repo: Path, manifest_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    subject = subject_identity(repo)
    entries: list[dict[str, str]] = []
    for row in manifest.get("tool_files", []):
        relative = str(row.get("path", ""))
        path = resolve_within(repo, relative)
        require(path.is_file(), f"tooling dependency is missing: {relative}")
        observed = committed_blob_identity(repo, path)
        observed_blob = observed["git_blob_id"]
        observed_sha = observed["raw_sha256"]
        require(row.get("raw_sha256") == observed_sha, f"tooling raw hash mismatch: {relative}")
        require(row.get("git_blob_id") == observed_blob, f"tooling blob mismatch: {relative}")
        entries.append({"path": relative, "raw_sha256": observed_sha, "git_blob_id": observed_blob})
    require(manifest.get("cli_schema_version") == CLI_SCHEMA_VERSION, "measurement CLI schema mismatch")
    manifest_identity = committed_blob_identity(repo, manifest_path)
    return {
        "tool_subject": subject,
        "manifest_path": manifest_path.resolve().relative_to(repo.resolve()).as_posix(),
        "manifest_raw_sha256": manifest_identity["raw_sha256"],
        "manifest_git_blob_id": manifest_identity["git_blob_id"],
        "tool_file_raw_hash_source": "committed_git_blob_bytes_before_checkout_filters",
        "cli_schema_version": CLI_SCHEMA_VERSION,
        "tool_files": entries,
        "harness_interpreter_identity": interpreter_identity(),
        "environment_identity": environment_identity(),
    }


def render_command(template: list[str], repository: Path, sample_root: Path) -> list[str]:
    substitutions = {
        "{python}": sys.executable,
        "{repository}": str(repository),
        "{result_root}": str(sample_root),
        "{denominator_receipt}": str(sample_root / "denominator-receipt.json"),
    }
    return [substitutions.get(value, value) for value in template]


def _normalized_output(value: bytes) -> str:
    text = value.decode("utf-8", errors="replace").replace("\r\n", "\n")
    text = re.sub(r"\bin \d+(?:\.\d+)?s\b", "in <elapsed>", text)
    return text


class _WindowsKillJob:
    def __init__(self, process: subprocess.Popen[bytes]) -> None:
        import ctypes
        from ctypes import wintypes

        class _BasicLimitInformation(ctypes.Structure):
            _fields_ = [
                ("per_process_user_time_limit", ctypes.c_longlong),
                ("per_job_user_time_limit", ctypes.c_longlong),
                ("limit_flags", wintypes.DWORD),
                ("minimum_working_set_size", ctypes.c_size_t),
                ("maximum_working_set_size", ctypes.c_size_t),
                ("active_process_limit", wintypes.DWORD),
                ("affinity", ctypes.c_size_t),
                ("priority_class", wintypes.DWORD),
                ("scheduling_class", wintypes.DWORD),
            ]

        class _IoCounters(ctypes.Structure):
            _fields_ = [
                ("read_operation_count", ctypes.c_ulonglong),
                ("write_operation_count", ctypes.c_ulonglong),
                ("other_operation_count", ctypes.c_ulonglong),
                ("read_transfer_count", ctypes.c_ulonglong),
                ("write_transfer_count", ctypes.c_ulonglong),
                ("other_transfer_count", ctypes.c_ulonglong),
            ]

        class _ExtendedLimitInformation(ctypes.Structure):
            _fields_ = [
                ("basic_limit_information", _BasicLimitInformation),
                ("io_info", _IoCounters),
                ("process_memory_limit", ctypes.c_size_t),
                ("job_memory_limit", ctypes.c_size_t),
                ("peak_process_memory_used", ctypes.c_size_t),
                ("peak_job_memory_used", ctypes.c_size_t),
            ]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        kernel32.SetInformationJobObject.argtypes = (
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
        )
        kernel32.SetInformationJobObject.restype = wintypes.BOOL
        kernel32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
        kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel32.TerminateJobObject.argtypes = (wintypes.HANDLE, wintypes.UINT)
        kernel32.TerminateJobObject.restype = wintypes.BOOL
        kernel32.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
        kernel32.WaitForSingleObject.restype = wintypes.DWORD
        kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel32.CloseHandle.restype = wintypes.BOOL

        handle = kernel32.CreateJobObjectW(None, None)
        require(bool(handle), "failed to create Windows measurement job object")
        limits = _ExtendedLimitInformation()
        limits.basic_limit_information.limit_flags = 0x00002000
        configured = kernel32.SetInformationJobObject(
            handle,
            9,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        )
        if not configured:
            kernel32.CloseHandle(handle)
            raise ContractError("failed to configure Windows measurement job object")
        assigned = kernel32.AssignProcessToJobObject(handle, int(process._handle))
        if not assigned:
            kernel32.CloseHandle(handle)
            raise ContractError("failed to assign measurement process to Windows job object")
        self._kernel32 = kernel32
        self._handle = handle
        self._reaped: bool | None = None

    def reap(self) -> bool:
        if self._reaped is not None:
            return self._reaped
        terminated = bool(self._kernel32.TerminateJobObject(self._handle, 1))
        wait_result = int(self._kernel32.WaitForSingleObject(self._handle, 30_000))
        closed = bool(self._kernel32.CloseHandle(self._handle))
        self._handle = None
        self._reaped = terminated and wait_result == 0 and closed
        return self._reaped


def _terminate_suspended_process(process: subprocess.Popen[bytes]) -> bool:
    try:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5.0)
    except (OSError, subprocess.TimeoutExpired):
        return False
    finally:
        for stream in (process.stdout, process.stderr):
            if stream is not None:
                stream.close()
    return process.poll() is not None


def _resume_windows_process(process: subprocess.Popen[bytes]) -> None:
    import ctypes
    from ctypes import wintypes

    class _ThreadEntry32(ctypes.Structure):
        _fields_ = [
            ("size", wintypes.DWORD),
            ("usage_count", wintypes.DWORD),
            ("thread_id", wintypes.DWORD),
            ("owner_process_id", wintypes.DWORD),
            ("base_priority", wintypes.LONG),
            ("priority_delta", wintypes.LONG),
            ("flags", wintypes.DWORD),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateToolhelp32Snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
    kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel32.Thread32First.argtypes = (wintypes.HANDLE, ctypes.POINTER(_ThreadEntry32))
    kernel32.Thread32First.restype = wintypes.BOOL
    kernel32.Thread32Next.argtypes = (wintypes.HANDLE, ctypes.POINTER(_ThreadEntry32))
    kernel32.Thread32Next.restype = wintypes.BOOL
    kernel32.OpenThread.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel32.OpenThread.restype = wintypes.HANDLE
    kernel32.ResumeThread.argtypes = (wintypes.HANDLE,)
    kernel32.ResumeThread.restype = wintypes.DWORD
    kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel32.CloseHandle.restype = wintypes.BOOL

    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000004, 0)
    require(
        snapshot not in (None, ctypes.c_void_p(-1).value),
        "failed to enumerate suspended measurement process threads",
    )
    entry = _ThreadEntry32()
    entry.size = ctypes.sizeof(entry)
    thread_ids: list[int] = []
    try:
        available = bool(kernel32.Thread32First(snapshot, ctypes.byref(entry)))
        while available:
            if int(entry.owner_process_id) == process.pid:
                thread_ids.append(int(entry.thread_id))
            available = bool(kernel32.Thread32Next(snapshot, ctypes.byref(entry)))
    finally:
        kernel32.CloseHandle(snapshot)
    require(len(thread_ids) == 1, "suspended measurement process thread identity is ambiguous")
    thread_handle = kernel32.OpenThread(0x0002, False, thread_ids[0])
    require(bool(thread_handle), "failed to open suspended measurement process thread")
    try:
        previous_suspend_count = int(kernel32.ResumeThread(thread_handle))
        require(
            previous_suspend_count not in (0, 0xFFFFFFFF),
            "failed to resume suspended measurement process thread",
        )
        while previous_suspend_count > 1:
            previous_suspend_count = int(kernel32.ResumeThread(thread_handle))
            require(
                previous_suspend_count != 0xFFFFFFFF,
                "failed to fully resume suspended measurement process thread",
            )
    finally:
        kernel32.CloseHandle(thread_handle)


def _kill_process_tree(
    process: subprocess.Popen[bytes], windows_job: _WindowsKillJob | None
) -> bool:
    if os.name == "nt":
        require(windows_job is not None, "Windows measurement process lacks a kill job")
        return windows_job.reap()
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    return True


def _read_events(event_root: Path, expected_root_pid: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    require(event_root.is_dir(), "observer event root is missing")
    paths = sorted(event_root.iterdir())
    require(paths, "observer event stream is missing")
    require(
        all(path.is_file() and re.fullmatch(r"events-[0-9]+\.jsonl", path.name) for path in paths),
        "observer event root contains an unexpected entry",
    )
    observed_pids: list[int] = []
    observer_parents: dict[int, int] = {}
    for path in paths:
        pid = int(path.stem.removeprefix("events-"))
        try:
            process_rows = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        except (OSError, json.JSONDecodeError) as error:
            raise ContractError(f"observer event stream is unreadable: {path.name}") from error
        require(process_rows, f"observer event stream is empty: {path.name}")
        require(
            all(row.get("pid") == pid for row in process_rows),
            f"observer event pid binding mismatch: {path.name}",
        )
        require(
            [row.get("sequence") for row in process_rows] == list(range(1, len(process_rows) + 1)),
            f"observer event sequence is incomplete: {path.name}",
        )
        require(
            process_rows[0].get("kind") == "observer_start"
            and process_rows[-1].get("kind") == "observer_complete"
            and sum(row.get("kind") == "observer_start" for row in process_rows) == 1
            and sum(row.get("kind") == "observer_complete" for row in process_rows) == 1,
            f"observer lifecycle is incomplete: {path.name}",
        )
        observed_pids.append(pid)
        parent_pid = process_rows[0].get("parent_pid")
        require(isinstance(parent_pid, int), f"observer parent pid is missing: {path.name}")
        observer_parents[pid] = parent_pid
        rows.extend(process_rows)
    require(expected_root_pid in observed_pids, "root Python observer lifecycle is missing")
    subprocess_rows = [row for row in rows if row.get("kind") == "subprocess"]
    require(
        all(
            isinstance(row.get("child_pid"), int)
            and row["child_pid"] > 0
            and isinstance(row.get("python_observer_expected"), bool)
            for row in subprocess_rows
        ),
        "subprocess observer expectation binding is incomplete",
    )
    expected_python_children = {
        int(row["child_pid"]): int(row["pid"])
        for row in subprocess_rows
        if row["python_observer_expected"] is True
    }
    missing_python_children = sorted(set(expected_python_children) - set(observed_pids))
    require(
        not missing_python_children,
        f"expected Python descendant observer lifecycle is missing: {missing_python_children}",
    )
    require(
        all(observer_parents[pid] == parent for pid, parent in expected_python_children.items()),
        "Python descendant observer parent binding mismatch",
    )
    return rows, {
        "status": "PASS",
        "root_process_pid": expected_root_pid,
        "observed_process_count": len(observed_pids),
        "complete_process_count": len(observed_pids),
        "expected_python_descendant_count": len(expected_python_children),
        "missing_python_descendant_count": 0,
        "sequence_gap_count": 0,
    }


def _tree_file_metrics(root: Path) -> dict[str, int]:
    files = [path for path in root.rglob("*") if path.is_file()]
    return {
        "copied_files": len(files),
        "copied_bytes": sum(path.stat().st_size for path in files),
    }


def _argv_text(event: dict[str, Any]) -> str:
    argv = event.get("argv", [])
    if isinstance(argv, list):
        return " ".join(str(value) for value in argv).replace("\\", "/")
    return str(argv).replace("\\", "/")


def count_producer_invocations(
    argv: list[str], subprocess_events: list[dict[str, Any]], patterns: list[str]
) -> int:
    top_level = " ".join(str(value) for value in argv).replace("\\", "/")
    return int(any(pattern in top_level for pattern in patterns)) + sum(
        any(pattern in _argv_text(row) for pattern in patterns)
        for row in subprocess_events
    )


def canonical_input_hashes(
    repository: Path, workload: dict[str, Any]
) -> dict[str, str]:
    paths = workload.get("canonical_input_paths")
    require(
        isinstance(paths, list)
        and bool(paths)
        and len(paths) == len(set(paths))
        and all(
            isinstance(path, str)
            and bool(path)
            and not Path(path).is_absolute()
            and ".." not in Path(path).parts
            for path in paths
        ),
        "canonical input path contract is incomplete",
    )
    return {
        path: git(repository, "rev-parse", f"HEAD:{path}") for path in paths
    }


def observe_command(
    repository: Path,
    workload: dict[str, Any],
    sample_root: Path,
    *,
    instrumented: bool,
    resolved_input_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    sample_root.mkdir(parents=True, exist_ok=False)
    before = subject_identity(repository)
    ignored_before = ignored_worktree_entries(repository)
    require(not ignored_before, "target checkout contains ignored worktree state before observation")
    argv = render_command(workload["command"], repository, sample_root)
    input_hashes = (
        canonical_input_hashes(repository, workload)
        if resolved_input_hashes is None
        else dict(resolved_input_hashes)
    )
    expected_output_contract = workload.get("expected_output_contract")
    require(
        isinstance(expected_output_contract, dict)
        and set(expected_output_contract)
        == {"valid_exit_codes", "normalized_stdout", "normalized_stderr"},
        "expected output contract is incomplete",
    )
    valid_exit_codes = set(workload.get("valid_exit_codes", [0]))
    require(
        expected_output_contract["valid_exit_codes"] == sorted(valid_exit_codes),
        "expected output and valid-exit contracts disagree",
    )
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    execution_context = None
    execution_parent = env.get("IRIS_WORKFLOW_EXECUTION_OUTPUT_PARENT")
    event_root = sample_root / "observer-events"
    if instrumented:
        observer_root = sample_root / "observer"
        observer_root.mkdir()
        (observer_root / "sitecustomize.py").write_text(OBSERVER_SOURCE, encoding="utf-8", newline="\n")
        env["IRIS_WF_OBSERVER_EVENT_ROOT"] = str(event_root)
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = str(observer_root) + (os.pathsep + existing if existing else "")
    setup_copy_metrics = {"copied_files": 0, "copied_bytes": 0}
    setup_materialization_count = 0
    started = time.perf_counter_ns()
    if execution_parent:
        execution_parent_path = Path(execution_parent).resolve()
        require_path_outside_repositories(
            execution_parent_path,
            (repository,),
            label="workflow execution output parent",
        )
        execution_parent_path.mkdir(parents=True, exist_ok=True)
        execution_context = tempfile.TemporaryDirectory(
            prefix="w-",
            dir=execution_parent_path,
        )
        setup_materialization_count += 1
        execution_root = Path(execution_context.name)
    else:
        execution_root = sample_root
    test_output_root = execution_root / "t"
    legacy_output_root = execution_root / "l"
    source_output_root = repository / "Iris" / "output"
    if source_output_root.is_dir():
        legacy_output_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_output_root, legacy_output_root)
        setup_copy_metrics = _tree_file_metrics(legacy_output_root)
        setup_materialization_count += 1
    env["IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT"] = str(test_output_root)
    env["IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT"] = str(legacy_output_root)
    env["UV_CACHE_DIR"] = str(execution_root / "u")
    process = subprocess.Popen(
        argv,
        cwd=repository,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=os.name != "nt",
        creationflags=0x00000004 if os.name == "nt" else 0,
    )
    windows_job = None
    if os.name == "nt":
        try:
            windows_job = _WindowsKillJob(process)
            _resume_windows_process(process)
        except ContractError as setup_error:
            cleanup_valid = (
                windows_job.reap()
                if windows_job is not None
                else _terminate_suspended_process(process)
            )
            require(cleanup_valid, "suspended measurement process cleanup could not be confirmed")
            raise setup_error
    timed_out = False
    cleanup_valid = True
    try:
        stdout, stderr = process.communicate(timeout=float(workload["timeout_seconds"]))
    except subprocess.TimeoutExpired as timeout_error:
        timed_out = True
        cleanup_valid = _kill_process_tree(process, windows_job)
        try:
            stdout, stderr = process.communicate(timeout=30.0)
        except subprocess.TimeoutExpired as cleanup_error:
            cleanup_valid = _kill_process_tree(process, windows_job) and cleanup_valid
            if process.poll() is None:
                process.kill()
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    stream.close()
            try:
                process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5.0)
            stdout = cleanup_error.output or timeout_error.output or b""
            stderr = cleanup_error.stderr or timeout_error.stderr or b""
    finally:
        cleanup_valid = _kill_process_tree(process, windows_job) and cleanup_valid
    require(cleanup_valid, "measurement process tree cleanup could not be confirmed")
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000.0
    try:
        after = subject_identity(repository)
        require(before == after, "target subject or working tree changed during observation")
        require(
            not ignored_worktree_entries(repository),
            "target checkout gained ignored worktree state during observation",
        )
        if instrumented:
            events, observer_integrity = _read_events(event_root, process.pid)
        else:
            events = []
            observer_integrity = {
                "status": "NOT_APPLICABLE_uninstrumented_companion",
                "root_process_pid": process.pid,
                "observed_process_count": 0,
                "complete_process_count": 0,
                "expected_python_descendant_count": 0,
                "missing_python_descendant_count": 0,
                "sequence_gap_count": 0,
            }
        subprocess_events = [row for row in events if row.get("kind") == "subprocess"]
        producer_patterns = [value.replace("\\", "/") for value in workload.get("producer_patterns", [])]
        eligible_patterns = [value.replace("\\", "/") for value in workload.get("eligible_subprocess_patterns", [])]
        producer_count = count_producer_invocations(argv, subprocess_events, producer_patterns)
        eligible_count = sum(
            any(pattern in _argv_text(row) for pattern in eligible_patterns)
            for row in subprocess_events
        )
        copied_values = [row.get("copied_bytes") for row in events if row.get("kind") == "copy"]
        copied_observed = [int(value) for value in copied_values if isinstance(value, int)]
        observation = {
        "elapsed_ms": elapsed_ms,
        "exit_code": process.returncode,
        "timed_out": timed_out,
        "contract_valid": not timed_out and process.returncode in valid_exit_codes,
        "stdout_sha256": sha256_bytes(stdout),
        "stderr_sha256": sha256_bytes(stderr),
        "normalized_stdout_sha256": sha256_bytes(_normalized_output(stdout).encode("utf-8")),
        "normalized_stderr_sha256": sha256_bytes(_normalized_output(stderr).encode("utf-8")),
        "command_signature": {
            **normalized_command_signature(argv, repository, workload.get("environment_contract", {})),
            "ordered_argv": workload["command"][1:],
            "path_normalization": "repository_and_result_roots_are_role_descriptors",
            "declared_input_identity": workload.get("input_identity", "target_subject_tree"),
            "canonical_input_hashes": input_hashes,
            "expected_output_contract": expected_output_contract,
        },
        "operation_counts": {
            "producer_invocations": producer_count,
            "eligible_subprocesses": eligible_count,
            "temporary_materializations": setup_materialization_count
            + sum(row.get("kind") == "materialization" for row in events),
            "copied_files": setup_copy_metrics["copied_files"] + len(copied_observed),
            "copied_bytes": setup_copy_metrics["copied_bytes"] + sum(copied_observed),
        },
        "observation_coverage": {
            "subprocess": "python_process_tree" if instrumented else "unobserved",
            "temporary_materialization": "measurement_wrapper_setup_and_python_process_tree"
            if instrumented
            else "measurement_wrapper_setup_only",
            "copy": "measurement_wrapper_setup_and_python_process_tree"
            if instrumented
            else "measurement_wrapper_setup_only",
            "read_parse_hash": "unobserved",
        },
        "observer_integrity": observer_integrity,
        "measurement_boundary": {
            "starts_before_execution_root_and_legacy_output_materialization": True,
            "ends_after_child_process_completion": True,
            "legacy_output_copy_in_elapsed_time_and_operation_counts": True,
        },
        "event_count": len(events),
        "instrumented": instrumented,
        }
    finally:
        if execution_context is not None:
            execution_context.cleanup()
    return observation


def block_arms(block_number: int) -> list[str]:
    return ["A", "B", "B", "A"] if block_number % 2 == 0 else ["B", "A", "A", "B"]


def workload_schedule(workload_id: str, measured_blocks: int) -> list[dict[str, Any]]:
    rows = [
        {"workload_id": workload_id, "phase": "warmup", "block": -1, "position": index, "arm": arm}
        for index, arm in enumerate(["A", "B", "B", "A"], 1)
    ]
    for block in range(measured_blocks):
        for position, arm in enumerate(block_arms(block), 1):
            rows.append(
                {"workload_id": workload_id, "phase": "measured", "block": block, "position": position, "arm": arm}
            )
    return rows


def adjacent_deltas(samples: list[dict[str, Any]], sign: str = "A-B") -> list[float]:
    deltas: list[float] = []
    by_block: dict[int, list[dict[str, Any]]] = {}
    for row in samples:
        if row["phase"] == "measured":
            by_block.setdefault(int(row["block"]), []).append(row)
    for rows in by_block.values():
        ordered = sorted(rows, key=lambda value: int(value["position"]))
        for left, right in ((ordered[0], ordered[1]), (ordered[2], ordered[3])):
            a = left if left["arm"] == "A" else right
            b = right if left["arm"] == "A" else left
            delta = float(a["observation"]["elapsed_ms"]) - float(b["observation"]["elapsed_ms"])
            deltas.append(delta if sign == "A-B" else -delta)
    return deltas


def bootstrap_interval(values: list[float], seed: int, iterations: int, *, one_sided: bool = False) -> dict[str, float]:
    require(values, "bootstrap sample is empty")
    generator = random.Random(seed)
    estimates = [
        statistics.mean(generator.choice(values) for _ in values)
        for _ in range(iterations)
    ]
    return {
        "lower": percentile(estimates, 0.05 if one_sided else 0.025),
        "upper": percentile(estimates, 0.95 if one_sided else 0.975),
    }


def summarize_workload(
    samples: list[dict[str, Any]], workload: dict[str, Any], statistics_contract: dict[str, Any]
) -> dict[str, Any]:
    measured = [row for row in samples if row["phase"] == "measured"]
    arm_a = [float(row["observation"]["elapsed_ms"]) for row in measured if row["arm"] == "A"]
    arm_b = [float(row["observation"]["elapsed_ms"]) for row in measured if row["arm"] == "B"]
    deltas = adjacent_deltas(measured)
    interval = bootstrap_interval(
        deltas,
        int(statistics_contract["bootstrap_seed"]),
        int(statistics_contract["bootstrap_iterations"]),
    )
    improved = statistics.median(arm_b) < statistics.median(arm_a) and interval["lower"] > 0
    operation_axes: dict[str, Any] = {}
    for axis in (
        "producer_invocations",
        "eligible_subprocesses",
        "temporary_materializations",
        "copied_files",
        "copied_bytes",
    ):
        before = sum(row["observation"]["operation_counts"][axis] for row in measured if row["arm"] == "A")
        after = sum(row["observation"]["operation_counts"][axis] for row in measured if row["arm"] == "B")
        operation_axes[axis] = {
            "before": before,
            "after": after,
            "delta_before_minus_after": before - after,
            "strictly_reduced": before > 0 and after < before,
            "regressed_from_zero": before == 0 and after > 0,
            "applicability": "APPLICABLE" if before > 0 else "NOT_APPLICABLE",
        }
    summary = {
        "workload_id": workload["workload_id"],
        "measured_samples_per_arm": len(arm_a),
        "valid": bool(measured) and all(row["observation"]["contract_valid"] for row in samples),
        "before_median_ms": statistics.median(arm_a),
        "after_median_ms": statistics.median(arm_b),
        "paired_delta_a_minus_b": {"values": deltas, "bootstrap_95_percent": interval},
        "improved_beyond_observed_noise": improved,
        "operation_axes": operation_axes,
    }
    if workload.get("role") == "configured_route_performance_observation":
        regression_deltas = adjacent_deltas(measured, sign="B-A")
        upper = bootstrap_interval(
            regression_deltas,
            int(statistics_contract["bootstrap_seed"]),
            int(statistics_contract["bootstrap_iterations"]),
            one_sided=True,
        )["upper"]
        margin = effective_regression_ceiling_ms(arm_a, statistics_contract)
        summary["configured_route_no_regression"] = {
            "one_sided_95_upper_bound_ms": upper,
            **margin,
            "status": "PASS" if upper <= margin["effective_regression_ceiling_ms"] else "FAIL",
        }
    return summary


def targeted_summary_accepted(summary: dict[str, Any]) -> bool:
    axes = list(summary.get("operation_axes", {}).values())
    applicable_axes = [
        row
        for row in axes
        if row.get("applicability") == "APPLICABLE"
    ]
    return (
        summary.get("improved_beyond_observed_noise") is True
        and bool(applicable_axes)
        and all(row.get("strictly_reduced") is True for row in applicable_axes)
        and not any(row.get("regressed_from_zero") is True for row in axes)
    )


def effective_regression_ceiling_ms(
    arm_a_elapsed_ms: list[float], statistics_contract: dict[str, Any]
) -> dict[str, float]:
    require(arm_a_elapsed_ms, "configured-route baseline sample is empty")
    margin_ms = float(statistics_contract["maximum_acceptable_regression_ms"])
    margin_pct = float(statistics_contract["maximum_acceptable_regression_pct"])
    before_median_ms = statistics.median(arm_a_elapsed_ms)
    percent_ceiling_ms = before_median_ms * margin_pct / 100.0
    return {
        "before_median_ms": before_median_ms,
        "maximum_acceptable_regression_ms": margin_ms,
        "maximum_acceptable_regression_pct": margin_pct,
        "percent_ceiling_ms_from_before_median": percent_ceiling_ms,
        "effective_regression_ceiling_ms": min(margin_ms, percent_ceiling_ms),
    }


def minimum_detectable_regression_ms(
    deltas: list[float], statistics_contract: dict[str, Any]
) -> float:
    centered_mean = statistics.mean(deltas)
    centered = [value - centered_mean for value in deltas]
    generator = random.Random(int(statistics_contract["bootstrap_seed"]) + 1)
    iterations = int(statistics_contract["bootstrap_iterations"])
    null_means = sorted(
        statistics.mean(generator.choice(centered) for _ in centered)
        for _ in range(iterations)
    )
    critical = percentile(null_means, 0.95)
    shifted_detection = [critical - value for value in null_means]
    return max(0.0, percentile(shifted_detection, float(statistics_contract["power_target"])))


def execute_schedule(
    schedule: dict[str, Any], repositories: dict[str, Path], output_root: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    samples: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    workloads = {row["workload_id"]: row for row in schedule["workloads"]}
    input_hashes = {
        (arm, workload_id): canonical_input_hashes(repositories[arm], workload)
        for arm in {position["arm"] for position in schedule["positions"]}
        for workload_id, workload in workloads.items()
    }
    for ordinal, position in enumerate(schedule["positions"]):
        workload = workloads[position["workload_id"]]
        arm = position["arm"]
        sample_root = output_root / "samples" / f"{ordinal:04d}-{position['workload_id']}-{arm}"
        observation = observe_command(
            repositories[arm],
            workload,
            sample_root,
            instrumented=True,
            resolved_input_hashes=input_hashes[(arm, workload["workload_id"])],
        )
        samples.append({**position, "ordinal": ordinal, "observation": observation})
    for workload in workloads.values():
        relevant = [row for row in samples if row["workload_id"] == workload["workload_id"]]
        summaries.append(summarize_workload(relevant, workload, schedule["statistics"]))
    return samples, summaries


def build_schedule(
    contract: dict[str, Any], family_rows: list[dict[str, Any]], session_kind: str
) -> dict[str, Any]:
    contract_ids = [row["workload_id"] for row in contract["workloads"]]
    require(len(contract_ids) == len(set(contract_ids)), "duplicate contract workload_id")
    definitions = {row["workload_id"]: dict(row) for row in contract["workloads"]}
    workloads = [definitions["mandatory_pilot"]]
    adopted = sorted(
        (
            row
            for row in family_rows
            if row.get("disposition") == "adopted" and not row.get("mandatory_pilot")
        ),
        key=lambda row: row["family_id"],
    )
    require(len({row["family_id"] for row in adopted}) == len(adopted), "duplicate adopted family_id")
    if session_kind == "candidate-qualification":
        candidates = [
            row
            for row in family_rows
            if isinstance(row.get("candidate_measurement_workload"), dict)
        ]
        require(len(candidates) == 1, "candidate session must select exactly one family workload")
        candidate = candidates[0]
        workload = candidate["candidate_measurement_workload"]
        require(workload.get("workload_id") == candidate.get("family_id"), "candidate workload identity mismatch")
        workloads = [workload]
    elif session_kind == "terminal-acceptance":
        for row in adopted:
            workload = row.get("terminal_measurement_workload")
            require(isinstance(workload, dict), f"adopted family lacks terminal workload: {row['family_id']}")
            require(workload.get("workload_id") == row["family_id"], "family workload identity mismatch")
            workloads.append(workload)
        workloads.append(definitions["configured-current"])
    workload_ids = [row["workload_id"] for row in workloads]
    require(len(workload_ids) == len(set(workload_ids)), "duplicate scheduled workload_id")
    positions: list[dict[str, Any]] = []
    family_blocks = int(contract["schedule"]["targeted_measured_blocks"])
    configured_blocks = int(contract["schedule"]["configured_measured_blocks"])
    for workload in workloads:
        blocks = configured_blocks if workload["workload_id"] == "configured-current" else family_blocks
        positions.extend(workload_schedule(workload["workload_id"], blocks))
    nonpilot_count = len(adopted) if session_kind == "terminal-acceptance" else 0
    expected_positions = 24 * nonpilot_count + 68 if session_kind == "terminal-acceptance" else 24
    require(len(positions) == expected_positions, "parameterized session position formula mismatch")
    return {
        "schema_version": SCHEDULE_SCHEMA,
        "session_kind": session_kind,
        "adopted_nonpilot_family_ids": [row["family_id"] for row in adopted] if session_kind == "terminal-acceptance" else [],
        "n_adopted_nonpilot": nonpilot_count,
        "workloads": workloads,
        "positions": positions,
        "measured_block_count": sum(row["phase"] == "measured" and row["position"] == 1 for row in positions),
        "total_execution_positions": len(positions),
        "statistics": contract["statistics"],
    }


def build_qualification_schedule(contract: dict[str, Any]) -> dict[str, Any]:
    qualification_ids = contract.get("qualification_workload_ids")
    require(
        isinstance(qualification_ids, list)
        and bool(qualification_ids)
        and len(qualification_ids) == len(set(qualification_ids)),
        "qualification workload identity is invalid",
    )
    definitions = {row["workload_id"]: row for row in contract["workloads"]}
    require(
        set(qualification_ids) <= set(definitions),
        "qualification workload is missing from the measurement contract",
    )
    selected = [
        definitions[workload_id] for workload_id in qualification_ids
    ]
    positions: list[dict[str, Any]] = []
    for workload in selected:
        blocks = (
            int(contract["schedule"]["configured_measured_blocks"])
            if workload["workload_id"] == "configured-current"
            else int(contract["schedule"]["targeted_measured_blocks"])
        )
        positions.extend(workload_schedule(workload["workload_id"], blocks))
    return {
        "schema_version": SCHEDULE_SCHEMA,
        "session_kind": "baseline-protocol-qualification",
        "workloads": selected,
        "positions": positions,
        "statistics": contract["statistics"],
    }


def candidate_elapsed_samples(
    candidate_root: Path | None, family_ids: list[str]
) -> dict[str, list[float]]:
    if not family_ids:
        return {}
    require(candidate_root is not None and candidate_root.is_dir(), "candidate receipt root is required for adopted families")
    result: dict[str, list[float]] = {}
    for path in sorted(candidate_root.rglob("*.json")):
        try:
            payload = read_json(path)
        except ContractError:
            continue
        if not isinstance(payload, dict) or payload.get("status") != "PASS":
            continue
        for row in payload.get("samples", []):
            workload_id = str(row.get("workload_id", ""))
            if workload_id in family_ids and row.get("phase") == "measured":
                result.setdefault(workload_id, []).append(
                    float(row["observation"]["elapsed_ms"])
                )
    missing = sorted(set(family_ids) - result.keys())
    require(not missing, f"candidate timing receipt is missing for adopted families: {missing}")
    return result


def resource_estimate(
    schedule: dict[str, Any],
    qualification: dict[str, Any],
    candidate_root: Path | None,
) -> dict[str, Any]:
    elapsed_by_workload: dict[str, list[float]] = {}
    for row in qualification.get("samples", []):
        elapsed_by_workload.setdefault(row["workload_id"], []).append(float(row["observation"]["elapsed_ms"]))
    scheduled_ids = {row["workload_id"] for row in schedule["workloads"]}
    missing_ids = sorted(scheduled_ids - elapsed_by_workload.keys())
    estimation_basis = {
        workload_id: "baseline_protocol_qualification_receipt"
        for workload_id in scheduled_ids - set(missing_ids)
    }
    workloads = {row["workload_id"]: row for row in schedule["workloads"]}
    if schedule["session_kind"] == "candidate-qualification":
        for workload_id in missing_ids:
            timeout_ms = float(workloads[workload_id]["timeout_seconds"]) * 1000.0
            elapsed_by_workload[workload_id] = [timeout_ms]
            estimation_basis[workload_id] = "declared_timeout_upper_bound_first_candidate_session"
    else:
        candidate_samples = candidate_elapsed_samples(candidate_root, missing_ids)
        elapsed_by_workload.update(candidate_samples)
        estimation_basis.update(
            {workload_id: "accepted_candidate_receipt" for workload_id in candidate_samples}
        )
    p50_total = 0.0
    p95_total = 0.0
    timeout_total = 0.0
    for position in schedule["positions"]:
        values = elapsed_by_workload.get(position["workload_id"])
        require(values, f"no qualified duration estimate for workload: {position['workload_id']}")
        p50_total += statistics.median(values)
        p95_total += percentile(values, 0.95)
        timeout_total += float(workloads[position["workload_id"]]["timeout_seconds"]) * 1000.0
    return {
        "schema_version": RESOURCE_SCHEMA,
        "session_kind": schedule["session_kind"],
        "n_adopted_nonpilot": schedule["n_adopted_nonpilot"],
        "total_execution_positions": schedule["total_execution_positions"],
        "expected_p50_duration_ms": p50_total,
        "expected_p95_duration_ms": p95_total,
        "worst_case_timeout_duration_ms": timeout_total,
        "estimated_external_disk_bytes": schedule["total_execution_positions"] * 2_000_000,
        "full_restart_expected_p95_ms": p95_total,
        "partial_sample_reuse_allowed": False,
        "workload_estimation_basis": estimation_basis,
    }


def verify_tooling(args: argparse.Namespace, contract_path: Path, contract_raw: bytes, protocol: dict[str, str]) -> int:
    repo = Path(git(contract_path.parent, "rev-parse", "--show-toplevel"))
    manifest = read_json(args.tooling_manifest)
    identity = tooling_identity(repo, args.tooling_manifest, manifest)
    ensure_contract_unchanged(contract_path, contract_raw)
    payload = {
        "schema_version": "iris_test_workflow_tooling_verification_v1",
        "status": "PASS",
        "measurement_tooling_identity": identity,
        "measurement_protocol_identity": protocol,
    }
    if args.output:
        write_json(args.output, payload)
    else:
        print(json.dumps(payload, sort_keys=True))
    return 0


def resolved_tooling_identity(args: argparse.Namespace, contract_path: Path) -> dict[str, Any]:
    manifest_path = args.tooling_manifest or contract_path.parent / "measurement_tooling_manifest.json"
    manifest = read_json(manifest_path)
    repo = Path(git(contract_path.parent, "rev-parse", "--show-toplevel"))
    return tooling_identity(repo, manifest_path, manifest)


def resolved_touch_surface_identity(args: argparse.Namespace, contract_path: Path) -> dict[str, str]:
    touch_surface_path = args.touch_surface or contract_path.parent / "declared_round_touch_surface.json"
    repository = Path(git(contract_path.parent, "rev-parse", "--show-toplevel"))
    return committed_blob_identity(repository, touch_surface_path)


def qualify_protocol(
    args: argparse.Namespace, contract: dict[str, Any], contract_path: Path, contract_raw: bytes, protocol: dict[str, str]
) -> int:
    target = args.target_repository.resolve()
    tool_repository = Path(git(contract_path.parent, "rev-parse", "--show-toplevel")).resolve()
    output_root = require_path_outside_repositories(
        args.output_root,
        (target, tool_repository),
        label="qualification output root",
    )
    target_subject = subject_identity(target)
    measurement_tooling = resolved_tooling_identity(args, contract_path)
    touch_surface_identity = resolved_touch_surface_identity(args, contract_path)
    output_root.mkdir(parents=True, exist_ok=False)
    schedule = build_qualification_schedule(contract)
    selected = schedule["workloads"]
    samples, summaries = execute_schedule(schedule, {"A": target, "B": target}, output_root)
    companions = []
    for workload in selected:
        input_hashes = canonical_input_hashes(target, workload)
        instrumented = observe_command(target, workload, output_root / "companions" / f"{workload['workload_id']}-on", instrumented=True, resolved_input_hashes=input_hashes)
        plain = observe_command(target, workload, output_root / "companions" / f"{workload['workload_id']}-off", instrumented=False, resolved_input_hashes=input_hashes)
        parity = (
            instrumented["exit_code"] == plain["exit_code"]
            and instrumented["normalized_stdout_sha256"] == plain["normalized_stdout_sha256"]
            and instrumented["normalized_stderr_sha256"] == plain["normalized_stderr_sha256"]
        )
        companions.append({"workload_id": workload["workload_id"], "contract_result_parity": parity})
    configured_samples = [row for row in samples if row["workload_id"] == "configured-current"]
    configured_deltas = adjacent_deltas(configured_samples, sign="B-A")
    detection = minimum_detectable_regression_ms(configured_deltas, contract["statistics"])
    configured_arm_a = [
        float(row["observation"]["elapsed_ms"])
        for row in configured_samples
        if row["phase"] == "measured" and row["arm"] == "A"
    ]
    margin = effective_regression_ceiling_ms(configured_arm_a, contract["statistics"])
    effective_margin_ms = margin["effective_regression_ceiling_ms"]
    status = (
        "PASS"
        if all(row["valid"] for row in summaries)
        and all(row["contract_result_parity"] for row in companions)
        and detection <= effective_margin_ms
        else "FAIL"
    )
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "receipt_kind": "baseline_protocol_qualification",
        "status": status,
        "accepted_before_after_sample": False,
        "target_subject_a": target_subject,
        "target_subject_b": target_subject,
        "measurement_protocol_identity": protocol,
        "measurement_tooling_identity": measurement_tooling,
        "declared_round_touch_surface_identity": touch_surface_identity,
        "harness_interpreter_identity": interpreter_identity(),
        "target_execution_interpreter_identity_a": interpreter_identity(),
        "target_execution_interpreter_identity_b": interpreter_identity(),
        "environment_identity": environment_identity(),
        "samples": samples,
        "workload_summaries": summaries,
        "instrumentation_companions": companions,
        "configured_route_noise_calibration": {
            "measured_samples_per_arm": len(configured_deltas),
            "minimum_detectable_regression_ms": detection,
            **margin,
            "status": "PASS" if detection <= effective_margin_ms else "UNDERPOWERED",
        },
    }
    write_receipt_after_contract_check(
        output_root / "qualification-receipt.json", receipt, contract_path, contract_raw
    )
    require(status == "PASS", "baseline protocol qualification failed")
    return 0


def plan_paired_session(
    args: argparse.Namespace, contract: dict[str, Any], contract_path: Path, contract_raw: bytes, protocol: dict[str, str]
) -> int:
    qualification = read_json(args.qualification_receipt)
    require(qualification.get("status") == "PASS", "qualification receipt is not PASS")
    require(qualification.get("measurement_protocol_identity") == protocol, "qualification protocol identity mismatch")
    measurement_tooling = resolved_tooling_identity(args, contract_path)
    touch_surface_identity = resolved_touch_surface_identity(args, contract_path)
    require(
        qualification.get("measurement_tooling_identity") == measurement_tooling,
        "qualification tooling identity mismatch",
    )
    require(
        qualification.get("declared_round_touch_surface_identity") == touch_surface_identity,
        "qualification touch-surface identity mismatch",
    )
    family_rows = read_jsonl(args.family_ledger)
    schedule = build_schedule(contract, family_rows, args.session_kind)
    schedule["measurement_protocol_identity"] = protocol
    schedule["measurement_tooling_identity"] = measurement_tooling
    schedule["declared_round_touch_surface_identity"] = touch_surface_identity
    schedule["family_ledger_sha256"] = sha256_file(args.family_ledger)
    write_json(args.schedule_output, schedule)
    estimate = resource_estimate(schedule, qualification, args.candidate_receipt_root)
    estimate["schedule_sha256"] = sha256_file(args.schedule_output)
    estimate["owner_acknowledgment_required"] = True
    write_json(args.resource_estimate_output, estimate)
    ensure_contract_unchanged(contract_path, contract_raw)
    return 0


def run_paired_session(
    args: argparse.Namespace, contract: dict[str, Any], contract_path: Path, contract_raw: bytes, protocol: dict[str, str]
) -> int:
    schedule = read_json(args.schedule)
    estimate = read_json(args.resource_estimate)
    acknowledgment = read_json(args.owner_acknowledgment)
    require(schedule.get("schema_version") == SCHEDULE_SCHEMA, "schedule schema mismatch")
    require(schedule.get("session_kind") == args.session_kind, "schedule kind mismatch")
    require(schedule.get("measurement_protocol_identity") == protocol, "schedule protocol identity mismatch")
    measurement_tooling = resolved_tooling_identity(args, contract_path)
    touch_surface_identity = resolved_touch_surface_identity(args, contract_path)
    require(
        schedule.get("measurement_tooling_identity") == measurement_tooling,
        "schedule tooling identity mismatch",
    )
    require(
        schedule.get("declared_round_touch_surface_identity") == touch_surface_identity,
        "schedule touch-surface identity mismatch",
    )
    require(estimate.get("schedule_sha256") == sha256_file(args.schedule), "resource estimate schedule binding mismatch")
    require(acknowledgment.get("approved") is True, "owner resource acknowledgment is missing")
    require(acknowledgment.get("schedule_sha256") == sha256_file(args.schedule), "owner acknowledgment schedule mismatch")
    require(
        acknowledgment.get("resource_estimate_sha256") == sha256_file(args.resource_estimate),
        "owner acknowledgment resource estimate mismatch",
    )
    family_rows = read_jsonl(args.family_ledger)
    require(
        schedule.get("family_ledger_sha256") == sha256_file(args.family_ledger),
        "family ledger changed after session planning",
    )
    expected = build_schedule(contract, family_rows, args.session_kind)
    for key in (
        "adopted_nonpilot_family_ids",
        "n_adopted_nonpilot",
        "workloads",
        "positions",
        "measured_block_count",
        "total_execution_positions",
        "statistics",
    ):
        require(schedule.get(key) == expected.get(key), f"schedule drift: {key}")
    repositories = {
        "A": args.base_repository.resolve(),
        "B": args.terminal_repository.resolve(),
    }
    tool_repository = Path(git(contract_path.parent, "rev-parse", "--show-toplevel")).resolve()
    output_root = require_path_outside_repositories(
        args.output_root,
        (*repositories.values(), tool_repository),
        label="paired-session output root",
    )
    subjects = {arm: subject_identity(repo) for arm, repo in repositories.items()}
    output_root.mkdir(parents=True, exist_ok=True)
    require(not (output_root / "session-receipt.json").exists(), "result root was already consumed")
    samples, summaries = execute_schedule(schedule, repositories, output_root)
    valid = all(row["valid"] for row in summaries)
    targeted = [row for row in summaries if row["workload_id"] != "configured-current"]
    targeted_ok = all(targeted_summary_accepted(row) for row in targeted)
    configured = next((row for row in summaries if row["workload_id"] == "configured-current"), None)
    configured_ok = configured is None or configured["configured_route_no_regression"]["status"] == "PASS"
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "receipt_kind": args.session_kind,
        "session_id": args.session_id,
        "status": "PASS" if valid and targeted_ok and configured_ok else "FAIL",
        "accepted_before_after_sample": args.session_kind == "terminal-acceptance",
        "target_subject_a": subjects["A"],
        "target_subject_b": subjects["B"],
        "measurement_protocol_identity": protocol,
        "measurement_tooling_identity": measurement_tooling,
        "declared_round_touch_surface_identity": touch_surface_identity,
        "schedule_sha256": sha256_file(args.schedule),
        "resource_estimate_sha256": sha256_file(args.resource_estimate),
        "owner_acknowledgment_sha256": sha256_file(args.owner_acknowledgment),
        "harness_interpreter_identity": interpreter_identity(),
        "target_execution_interpreter_identity_a": interpreter_identity(),
        "target_execution_interpreter_identity_b": interpreter_identity(),
        "environment_identity": environment_identity(),
        "cross_session_sample_count": 0,
        "schedule_projection": {
            "session_kind": schedule["session_kind"],
            "adopted_nonpilot_family_ids": schedule.get("adopted_nonpilot_family_ids", []),
            "n_adopted_nonpilot": schedule.get("n_adopted_nonpilot", 0),
            "total_execution_positions": schedule["total_execution_positions"],
            "measured_block_count": schedule["measured_block_count"],
        },
        "samples": samples,
        "workload_summaries": summaries,
    }
    write_receipt_after_contract_check(
        output_root / "session-receipt.json", receipt, contract_path, contract_raw
    )
    require(receipt["status"] == "PASS", f"{args.session_kind} failed")
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Measure Iris test workflow execution cost")
    value.add_argument("--mode", choices=("verify-tooling", "qualify-protocol", "plan-paired-session", "run-paired-session"), required=True)
    value.add_argument("--contract", type=Path, required=True)
    value.add_argument("--tooling-manifest", type=Path)
    value.add_argument("--touch-surface", type=Path)
    value.add_argument("--target-repository", type=Path)
    value.add_argument("--output-root", type=Path)
    value.add_argument("--output", type=Path)
    value.add_argument("--session-kind", choices=("candidate-qualification", "terminal-acceptance"))
    value.add_argument("--session-id")
    value.add_argument("--base-repository", type=Path)
    value.add_argument("--terminal-repository", type=Path)
    value.add_argument("--family-ledger", type=Path)
    value.add_argument("--qualification-receipt", type=Path)
    value.add_argument("--candidate-receipt-root", type=Path)
    value.add_argument("--schedule-output", type=Path)
    value.add_argument("--resource-estimate-output", type=Path)
    value.add_argument("--schedule", type=Path)
    value.add_argument("--resource-estimate", type=Path)
    value.add_argument("--owner-acknowledgment", type=Path)
    return value


def main() -> int:
    args = parser().parse_args()
    contract, raw, protocol = load_contract(args.contract)
    if args.mode == "verify-tooling":
        require(args.tooling_manifest is not None, "--tooling-manifest is required")
        return verify_tooling(args, args.contract, raw, protocol)
    if args.mode == "qualify-protocol":
        require(args.target_repository is not None and args.output_root is not None, "qualification paths are required")
        return qualify_protocol(args, contract, args.contract, raw, protocol)
    if args.mode == "plan-paired-session":
        require(all((args.session_kind, args.family_ledger, args.qualification_receipt, args.schedule_output, args.resource_estimate_output)), "paired-session planning arguments are incomplete")
        return plan_paired_session(args, contract, args.contract, raw, protocol)
    require(all((args.session_kind, args.session_id, args.base_repository, args.terminal_repository, args.family_ledger, args.schedule, args.resource_estimate, args.owner_acknowledgment, args.output_root)), "paired-session execution arguments are incomplete")
    return run_paired_session(args, contract, args.contract, raw, protocol)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
