from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    from ._common import (
        ContractError,
        environment_identity,
        git,
        interpreter_identity,
        normalized_command_signature,
        percentile,
        read_json,
        read_jsonl,
        require,
        resolve_within,
        sha256_bytes,
        sha256_file,
        subject_identity,
        write_json,
    )
except ImportError:  # Direct script execution.
    from _common import (
        ContractError,
        environment_identity,
        git,
        interpreter_identity,
        normalized_command_signature,
        percentile,
        read_json,
        read_jsonl,
        require,
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
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

_root_value = os.environ.get("IRIS_WF_OBSERVER_EVENT_ROOT")
_root = Path(_root_value) if _root_value else None

def _safe(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, os.PathLike):
        return os.fspath(value)
    if isinstance(value, (list, tuple)):
        return [_safe(item) for item in value]
    return repr(value)

def _emit(kind, **fields):
    if _root is None:
        return
    try:
        _root.mkdir(parents=True, exist_ok=True)
        target = _root / ("events-" + str(os.getpid()) + ".jsonl")
        row = {"kind": kind, "pid": os.getpid(), **fields}
        with target.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    except Exception:
        pass

_original_popen = subprocess.Popen
class _ObservedPopen(_original_popen):
    def __init__(self, args, *positional, **kwargs):
        _emit("subprocess", argv=_safe(args), cwd=_safe(kwargs.get("cwd")))
        super().__init__(args, *positional, **kwargs)
subprocess.Popen = _ObservedPopen

_original_mkdtemp = tempfile.mkdtemp
def _observed_mkdtemp(*args, **kwargs):
    result = _original_mkdtemp(*args, **kwargs)
    _emit("materialization", operation="mkdtemp")
    return result
tempfile.mkdtemp = _observed_mkdtemp

_original_copyfile = shutil.copyfile
def _observed_copyfile(src, dst, *args, **kwargs):
    result = _original_copyfile(src, dst, *args, **kwargs)
    try:
        copied_bytes = os.stat(src).st_size
    except OSError:
        copied_bytes = None
    _emit("copy", operation="copyfile", copied_bytes=copied_bytes)
    return result
shutil.copyfile = _observed_copyfile
'''


def protocol_identity(contract_path: Path, contract_bytes: bytes) -> dict[str, str]:
    repo = Path(git(contract_path.parent, "rev-parse", "--show-toplevel"))
    relative = contract_path.resolve().relative_to(repo.resolve()).as_posix()
    return {
        "schema_version": CONTRACT_SCHEMA,
        "canonical_contract_path": relative,
        "raw_sha256": sha256_bytes(contract_bytes),
        "git_blob_id": git(repo, "hash-object", "--no-filters", str(contract_path)),
    }


def load_contract(path: Path) -> tuple[dict[str, Any], bytes, dict[str, str]]:
    raw = path.read_bytes()
    try:
        contract = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ContractError(f"malformed measurement contract: {error}") from error
    require(contract.get("schema_version") == CONTRACT_SCHEMA, "measurement contract schema mismatch")
    return contract, raw, protocol_identity(path, raw)


def ensure_contract_unchanged(path: Path, initial: bytes) -> None:
    require(path.read_bytes() == initial, "measurement contract changed during execution")


def tooling_identity(repo: Path, manifest_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    subject = subject_identity(repo)
    entries: list[dict[str, str]] = []
    for row in manifest.get("tool_files", []):
        relative = str(row.get("path", ""))
        path = resolve_within(repo, relative)
        require(path.is_file(), f"tooling dependency is missing: {relative}")
        observed_sha = sha256_file(path)
        observed_blob = git(repo, "rev-parse", f"HEAD:{relative}")
        require(row.get("raw_sha256") == observed_sha, f"tooling raw hash mismatch: {relative}")
        require(row.get("git_blob_id") == observed_blob, f"tooling blob mismatch: {relative}")
        entries.append({"path": relative, "raw_sha256": observed_sha, "git_blob_id": observed_blob})
    require(manifest.get("cli_schema_version") == CLI_SCHEMA_VERSION, "measurement CLI schema mismatch")
    return {
        "tool_subject": subject,
        "manifest_path": manifest_path.resolve().relative_to(repo.resolve()).as_posix(),
        "manifest_raw_sha256": sha256_file(manifest_path),
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


def _kill_process_tree(process: subprocess.Popen[bytes]) -> None:
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        process.kill()


def _read_events(event_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not event_root.is_dir():
        return rows
    for path in sorted(event_root.glob("events-*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _argv_text(event: dict[str, Any]) -> str:
    argv = event.get("argv", [])
    if isinstance(argv, list):
        return " ".join(str(value) for value in argv).replace("\\", "/")
    return str(argv).replace("\\", "/")


def observe_command(
    repository: Path,
    workload: dict[str, Any],
    sample_root: Path,
    *,
    instrumented: bool,
) -> dict[str, Any]:
    sample_root.mkdir(parents=True, exist_ok=False)
    before = subject_identity(repository)
    argv = render_command(workload["command"], repository, sample_root)
    env = os.environ.copy()
    event_root = sample_root / "observer-events"
    if instrumented:
        observer_root = sample_root / "observer"
        observer_root.mkdir()
        (observer_root / "sitecustomize.py").write_text(OBSERVER_SOURCE, encoding="utf-8", newline="\n")
        env["IRIS_WF_OBSERVER_EVENT_ROOT"] = str(event_root)
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = str(observer_root) + (os.pathsep + existing if existing else "")
    started = time.perf_counter_ns()
    process = subprocess.Popen(
        argv,
        cwd=repository,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=float(workload["timeout_seconds"]))
    except subprocess.TimeoutExpired:
        timed_out = True
        _kill_process_tree(process)
        stdout, stderr = process.communicate()
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000.0
    after = subject_identity(repository)
    require(before == after, "target subject or working tree changed during observation")
    events = _read_events(event_root)
    subprocess_events = [row for row in events if row.get("kind") == "subprocess"]
    producer_patterns = [value.replace("\\", "/") for value in workload.get("producer_patterns", [])]
    eligible_patterns = [value.replace("\\", "/") for value in workload.get("eligible_subprocess_patterns", [])]
    producer_count = sum(
        any(pattern in _argv_text(row) for pattern in producer_patterns)
        for row in subprocess_events
    )
    eligible_count = sum(
        any(pattern in _argv_text(row) for pattern in eligible_patterns)
        for row in subprocess_events
    )
    copied_values = [row.get("copied_bytes") for row in events if row.get("kind") == "copy"]
    copied_observed = [int(value) for value in copied_values if isinstance(value, int)]
    valid_exit_codes = set(workload.get("valid_exit_codes", [0]))
    return {
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
        },
        "operation_counts": {
            "producer_invocations": producer_count,
            "eligible_subprocesses": eligible_count,
            "temporary_materializations": sum(row.get("kind") == "materialization" for row in events),
            "copied_files": len(copied_observed),
            "copied_bytes": sum(copied_observed),
        },
        "observation_coverage": {
            "subprocess": "python_process_tree" if instrumented else "unobserved",
            "temporary_materialization": "python_process_tree" if instrumented else "unobserved",
            "copy": "python_process_tree" if instrumented else "unobserved",
            "read_parse_hash": "unobserved",
        },
        "event_count": len(events),
        "instrumented": instrumented,
    }


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
            "applicability": "APPLICABLE" if before > 0 else "NOT_APPLICABLE",
        }
    summary = {
        "workload_id": workload["workload_id"],
        "measured_samples_per_arm": len(arm_a),
        "valid": bool(measured) and all(row["observation"]["contract_valid"] for row in measured),
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
        margin_ms = float(statistics_contract["maximum_acceptable_regression_ms"])
        summary["configured_route_no_regression"] = {
            "one_sided_95_upper_bound_ms": upper,
            "maximum_acceptable_regression_ms": margin_ms,
            "status": "PASS" if upper < margin_ms else "FAIL",
        }
    return summary


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
    for ordinal, position in enumerate(schedule["positions"]):
        workload = workloads[position["workload_id"]]
        arm = position["arm"]
        sample_root = output_root / "samples" / f"{ordinal:04d}-{position['workload_id']}-{arm}"
        observation = observe_command(repositories[arm], workload, sample_root, instrumented=True)
        samples.append({**position, "ordinal": ordinal, "observation": observation})
    for workload in workloads.values():
        relevant = [row for row in samples if row["workload_id"] == workload["workload_id"]]
        summaries.append(summarize_workload(relevant, workload, schedule["statistics"]))
    return samples, summaries


def build_schedule(
    contract: dict[str, Any], family_rows: list[dict[str, Any]], session_kind: str
) -> dict[str, Any]:
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
    if session_kind == "terminal-acceptance":
        for row in adopted:
            workload = row.get("terminal_measurement_workload")
            require(isinstance(workload, dict), f"adopted family lacks terminal workload: {row['family_id']}")
            require(workload.get("workload_id") == row["family_id"], "family workload identity mismatch")
            workloads.append(workload)
        workloads.append(definitions["configured-current"])
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


def resource_estimate(schedule: dict[str, Any], qualification: dict[str, Any]) -> dict[str, Any]:
    elapsed_by_workload: dict[str, list[float]] = {}
    for row in qualification.get("samples", []):
        elapsed_by_workload.setdefault(row["workload_id"], []).append(float(row["observation"]["elapsed_ms"]))
    p50_total = 0.0
    p95_total = 0.0
    timeout_total = 0.0
    workloads = {row["workload_id"]: row for row in schedule["workloads"]}
    for position in schedule["positions"]:
        values = elapsed_by_workload.get(position["workload_id"], [1000.0])
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


def qualify_protocol(
    args: argparse.Namespace, contract: dict[str, Any], contract_path: Path, contract_raw: bytes, protocol: dict[str, str]
) -> int:
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=False)
    target = args.target_repository.resolve()
    target_subject = subject_identity(target)
    selected = [
        row for row in contract["workloads"] if row["workload_id"] in contract["qualification_workload_ids"]
    ]
    positions: list[dict[str, Any]] = []
    for workload in selected:
        blocks = (
            int(contract["schedule"]["configured_measured_blocks"])
            if workload["workload_id"] == "configured-current"
            else int(contract["schedule"]["targeted_measured_blocks"])
        )
        positions.extend(workload_schedule(workload["workload_id"], blocks))
    schedule = {
        "schema_version": SCHEDULE_SCHEMA,
        "session_kind": "baseline-protocol-qualification",
        "workloads": selected,
        "positions": positions,
        "statistics": contract["statistics"],
    }
    samples, summaries = execute_schedule(schedule, {"A": target, "B": target}, output_root)
    companions = []
    for workload in selected:
        instrumented = observe_command(target, workload, output_root / "companions" / f"{workload['workload_id']}-on", instrumented=True)
        plain = observe_command(target, workload, output_root / "companions" / f"{workload['workload_id']}-off", instrumented=False)
        parity = (
            instrumented["exit_code"] == plain["exit_code"]
            and instrumented["normalized_stdout_sha256"] == plain["normalized_stdout_sha256"]
            and instrumented["normalized_stderr_sha256"] == plain["normalized_stderr_sha256"]
        )
        companions.append({"workload_id": workload["workload_id"], "contract_result_parity": parity})
    configured_samples = [row for row in samples if row["workload_id"] == "configured-current"]
    configured_deltas = adjacent_deltas(configured_samples, sign="B-A")
    detection = minimum_detectable_regression_ms(configured_deltas, contract["statistics"])
    margin = float(contract["statistics"]["maximum_acceptable_regression_ms"])
    status = (
        "PASS"
        if all(row["valid"] for row in summaries)
        and all(row["contract_result_parity"] for row in companions)
        and detection <= margin
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
            "maximum_acceptable_regression_ms": margin,
            "status": "PASS" if detection <= margin else "UNDERPOWERED",
        },
    }
    write_json(output_root / "qualification-receipt.json", receipt)
    ensure_contract_unchanged(contract_path, contract_raw)
    require(status == "PASS", "baseline protocol qualification failed")
    return 0


def plan_paired_session(
    args: argparse.Namespace, contract: dict[str, Any], contract_path: Path, contract_raw: bytes, protocol: dict[str, str]
) -> int:
    qualification = read_json(args.qualification_receipt)
    require(qualification.get("status") == "PASS", "qualification receipt is not PASS")
    require(qualification.get("measurement_protocol_identity") == protocol, "qualification protocol identity mismatch")
    family_rows = read_jsonl(args.family_ledger)
    schedule = build_schedule(contract, family_rows, args.session_kind)
    schedule["measurement_protocol_identity"] = protocol
    schedule["family_ledger_sha256"] = sha256_file(args.family_ledger)
    write_json(args.schedule_output, schedule)
    estimate = resource_estimate(schedule, qualification)
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
    require(estimate.get("schedule_sha256") == sha256_file(args.schedule), "resource estimate schedule binding mismatch")
    require(acknowledgment.get("approved") is True, "owner resource acknowledgment is missing")
    require(acknowledgment.get("schedule_sha256") == sha256_file(args.schedule), "owner acknowledgment schedule mismatch")
    family_rows = read_jsonl(args.family_ledger)
    expected = build_schedule(contract, family_rows, args.session_kind)
    for key in ("adopted_nonpilot_family_ids", "n_adopted_nonpilot", "workloads", "positions", "total_execution_positions"):
        require(schedule.get(key) == expected.get(key), f"schedule drift: {key}")
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    require(not (output_root / "session-receipt.json").exists(), "result root was already consumed")
    repositories = {
        "A": args.base_repository.resolve(),
        "B": args.terminal_repository.resolve(),
    }
    subjects = {arm: subject_identity(repo) for arm, repo in repositories.items()}
    samples, summaries = execute_schedule(schedule, repositories, output_root)
    valid = all(row["valid"] for row in summaries)
    targeted = [row for row in summaries if row["workload_id"] != "configured-current"]
    targeted_ok = all(row["improved_beyond_observed_noise"] for row in targeted)
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
    write_json(output_root / "session-receipt.json", receipt)
    ensure_contract_unchanged(contract_path, contract_raw)
    require(receipt["status"] == "PASS", f"{args.session_kind} failed")
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Measure Iris test workflow execution cost")
    value.add_argument("--mode", choices=("verify-tooling", "qualify-protocol", "plan-paired-session", "run-paired-session"), required=True)
    value.add_argument("--contract", type=Path, required=True)
    value.add_argument("--tooling-manifest", type=Path)
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
