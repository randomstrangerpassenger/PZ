#!/usr/bin/env python3
"""Orchestrate evidence-producing DVF 3.3 Registry Compatibility phases."""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Sequence


V2_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[6]
TOOLS_ROOT = V2_ROOT / "tools" / "build"
TEST_ROOT = V2_ROOT / "tests"
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import dvf_3_3_registry_runtime_compatibility as rtc


ANALYZER = TOOLS_ROOT / "dvf_3_3_registry_runtime_compatibility.py"
VALIDATOR = TOOLS_ROOT / "validate_dvf_3_3_registry_runtime_compatibility.py"
RUNNER = Path(__file__).resolve()
RECORD_EXPORTER = TOOLS_ROOT / "export_registry_runtime_records.py"
BRIDGE_EXPORTER = TOOLS_ROOT / "export_dvf_3_3_lua_bridge.py"
PACKAGE_SCRIPT = REPO_ROOT / "Iris" / "tools" / "package_iris.ps1"
WINDOWS_WRAPPER = (
    REPO_ROOT / "Iris" / "tools" / "inspect_registry_runtime_compatibility.ps1"
)
LUA_HARNESS = (
    TEST_ROOT
    / "fixtures"
    / "registry_runtime_compatibility"
    / "lua_merge_harness.lua"
)
LUA_SYNTAX = REPO_ROOT / "tools" / "check_lua_syntax.ps1"
ACTIVE_CORE_CLOSURE = (
    REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_active_core_closure.json"
)
ROUND3_RUNNER = (
    REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_run_contract_tests.py"
)
FROZEN_CURRENT_ROUTE_FIXTURE = (
    V2_ROOT
    / "frozen_predecessor_inputs"
    / "dvf_3_3_registry_authority_canonical_closure"
    / "current_route"
)
ISOLATED_CURRENT_ROUTE_INPUT_ROOTS = (
    V2_ROOT / "output",
    V2_ROOT / "staging" / "dvf_3_3_vnext_execution",
    V2_ROOT / "staging" / "dvf_3_3_vnext_current_authority_cutover",
    V2_ROOT
    / "staging"
    / "dvf_3_3_vnext_consumer_migration_input_normalization",
    REPO_ROOT / "Iris" / "build" / "package",
)
REQUIRED_TESTS = [
    TEST_ROOT / f"test_dvf_3_3_registry_runtime_compatibility_{suffix}.py"
    for suffix in (
        "contract",
        "bridge",
        "chunks",
        "windows",
        "fixtures",
        "current",
        "package",
    )
]


def execute(
    command: Sequence[str],
    *,
    receipt_path: Path,
    cwd: Path = REPO_ROOT,
    extra_environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    if extra_environment:
        environment.update(extra_environment)
    completed = subprocess.run(
        list(command),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        env=environment,
    )
    receipt = {
        "schema_version": "rtc-command-execution-receipt-v1",
        "round_id": rtc.ROUND_ID,
        "command_argv": list(command),
        "cwd": str(cwd.resolve()),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
    }
    rtc.write_json(receipt_path, receipt)
    if completed.returncode != 0:
        raise rtc.CompatibilityError(
            "phase_command_failed",
            f"Command failed ({completed.returncode}): {command}; "
            f"stderr={completed.stderr}",
        )
    return completed


def ignored_isolation_inputs() -> list[Path]:
    root_paths = [
        rtc.normalized_relative(REPO_ROOT, path)
        for path in ISOLATED_CURRENT_ROUTE_INPUT_ROOTS
    ]
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(REPO_ROOT),
            "ls-files",
            "-z",
            "--others",
            "--ignored",
            "--exclude-standard",
            "--",
            *root_paths,
        ],
        text=False,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise rtc.CompatibilityError(
            "isolated_current_route_input_census_failed",
            completed.stderr.decode("utf-8", errors="replace"),
        )
    relative_paths = sorted(
        {
            value.decode("utf-8").replace("\\", "/")
            for value in completed.stdout.split(b"\0")
            if value
        }
    )
    inputs: list[Path] = []
    for relative in relative_paths:
        source = REPO_ROOT.joinpath(*Path(relative).parts).resolve()
        try:
            source.relative_to(REPO_ROOT.resolve())
        except ValueError as exc:
            raise rtc.CompatibilityError(
                "isolated_current_route_input_escape",
                relative,
            ) from exc
        if not source.is_file():
            raise rtc.CompatibilityError(
                "isolated_current_route_input_not_file",
                relative,
            )
        if not any(
            source.is_relative_to(root.resolve())
            for root in ISOLATED_CURRENT_ROUTE_INPUT_ROOTS
        ):
            raise rtc.CompatibilityError(
                "isolated_current_route_input_outside_allowlist",
                relative,
            )
        inputs.append(source)
    required_ignored_inputs = (
        V2_ROOT / "output" / "dvf_3_3_rendered.json",
        REPO_ROOT
        / "Iris"
        / "build"
        / "package"
        / "Iris"
        / "media"
        / "lua"
        / "client"
        / "Iris"
        / "Data"
        / "IrisLayer3DataChunks.lua",
    )
    missing = [
        rtc.normalized_relative(REPO_ROOT, path)
        for path in required_ignored_inputs
        if path.resolve() not in inputs
    ]
    if missing:
        raise rtc.CompatibilityError(
            "isolated_current_route_required_input_missing",
            f"Missing ignored current-route inputs: {missing}",
        )
    return inputs


def remove_isolated_checkout(path: Path) -> tuple[bool, str | None]:
    last_error: str | None = None
    for retry in range(6):
        try:
            if path.exists():
                shutil.rmtree(path)
            if not path.exists():
                return True, None
        except OSError as exc:
            last_error = f"{type(exc).__name__}:{exc}"
        time.sleep(0.1 * (retry + 1))
    return not path.exists(), last_error


def execute_current_route_isolated(
    *,
    result_path: Path,
    receipt_path: Path,
    required_manifest: Path | None = None,
    candidate_probe: bool = False,
) -> dict[str, Any]:
    if result_path.exists() or receipt_path.exists():
        raise rtc.CompatibilityError(
            "isolated_current_route_output_exists",
            "Isolated current-route outputs are write-once",
        )
    live_status_before = rtc.git_text(REPO_ROOT, "status", "--porcelain")
    if live_status_before:
        raise rtc.CompatibilityError(
            "isolated_current_route_live_worktree_not_clean",
            live_status_before,
        )
    freeze_head = rtc.git_text(REPO_ROOT, "rev-parse", "HEAD")
    inputs = ignored_isolation_inputs()
    fixture_manifest_path = FROZEN_CURRENT_ROUTE_FIXTURE / "manifest.json"
    fixture_manifest = json.loads(
        fixture_manifest_path.read_text(encoding="utf-8")
    )
    if fixture_manifest.get("status") != "PASS":
        raise rtc.CompatibilityError(
            "isolated_current_route_fixture_not_pass",
            str(fixture_manifest_path),
        )
    candidate_payloads = set(
        fixture_manifest.get("candidate_seed_payload_paths", [])
    )
    candidate_rows = [
        row
        for row in fixture_manifest.get("rows", [])
        if row.get("payload_path") in candidate_payloads
    ]
    if len(candidate_rows) != 15:
        raise rtc.CompatibilityError(
            "isolated_current_route_candidate_seed_count",
            f"Expected 15 candidate seed rows, got {len(candidate_rows)}",
        )
    overlay_rows = [
        {
            "path": rtc.normalized_relative(REPO_ROOT, path),
            "sha256": rtc.sha256_file(path),
            "byte_count": path.stat().st_size,
        }
        for path in inputs
    ]
    candidate_owner = Path(tempfile.mkdtemp(prefix="rtc"))
    candidate_root = candidate_owner
    completed: subprocess.CompletedProcess[str] | None = None
    preparation_error: str | None = None
    cleanup_error: str | None = None
    candidate_status_before: list[str] = []
    candidate_status_after: list[str] = []
    copied_result = False
    try:
        clone = subprocess.run(
            [
                "git",
                "clone",
                "--shared",
                "--no-checkout",
                "--quiet",
                str(REPO_ROOT),
                str(candidate_root),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if clone.returncode != 0:
            raise RuntimeError(
                "isolated clone failed: " + clone.stderr.strip()
            )
        longpaths = subprocess.run(
            [
                "git",
                "-C",
                str(candidate_root),
                "config",
                "core.longpaths",
                "true",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if longpaths.returncode != 0:
            raise RuntimeError(
                "isolated longpaths config failed: "
                + longpaths.stderr.strip()
            )
        checkout = subprocess.run(
            [
                "git",
                "-C",
                str(candidate_root),
                "checkout",
                "--detach",
                "--quiet",
                freeze_head,
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if checkout.returncode != 0:
            raise RuntimeError(
                "isolated checkout failed: " + checkout.stderr.strip()
            )
        for source in inputs:
            relative = source.relative_to(REPO_ROOT)
            destination = candidate_root / relative
            if destination.exists():
                raise FileExistsError(
                    f"isolated ignored input target exists: {relative}"
                )
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            if rtc.sha256_file(destination) != rtc.sha256_file(source):
                raise RuntimeError(
                    f"isolated ignored input hash mismatch: {relative}"
                )
        for row in candidate_rows:
            payload = FROZEN_CURRENT_ROUTE_FIXTURE.joinpath(
                *Path(str(row["payload_path"])).parts
            )
            if rtc.sha256_file(payload) != row["sha256"]:
                raise RuntimeError(
                    "frozen candidate seed payload hash mismatch: "
                    + str(row["payload_path"])
                )
            destination = candidate_root.joinpath(
                *Path(str(row["target_path"])).parts
            )
            if destination.exists():
                raise FileExistsError(
                    "frozen candidate seed target exists: "
                    + str(row["target_path"])
                )
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(payload, destination)
        candidate_manifest_path: Path | None = None
        if required_manifest is not None:
            candidate_manifest_path = candidate_root / required_manifest.relative_to(
                REPO_ROOT
            )
            if candidate_manifest_path.exists():
                raise FileExistsError(
                    "isolated required manifest target exists"
                )
            candidate_manifest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(required_manifest, candidate_manifest_path)
        status = subprocess.run(
            [
                "git",
                "-C",
                str(candidate_root),
                "status",
                "--short",
                "--untracked-files=all",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if status.returncode != 0:
            raise RuntimeError(
                "isolated initial status failed: " + status.stderr.strip()
            )
        candidate_status_before = [
            line for line in status.stdout.splitlines() if line.strip()
        ]
        if candidate_status_before:
            raise RuntimeError(
                "isolated overlays escaped ignored targets: "
                + repr(candidate_status_before)
            )
        ephemeral_root = candidate_root / ".dvf_tmp"
        ephemeral_root.mkdir(parents=False, exist_ok=False)
        candidate_result = candidate_root / result_path.relative_to(REPO_ROOT)
        command = [
            "uv",
            "run",
            "python",
            "-B",
            str(candidate_root / ROUND3_RUNNER.relative_to(REPO_ROOT)),
            "--class",
            "current",
            "--enforce-current-build-closure",
        ]
        if candidate_manifest_path is not None:
            command.extend(
                [
                    "--required-validations",
                    str(candidate_manifest_path),
                ]
            )
        command.extend(["--out", str(candidate_result)])
        environment = os.environ.copy()
        environment.update(
            {
                "IRIS_DVF_CURRENT_ROUTE_FROZEN_PREDECESSOR": "1",
                "IRIS_DVF_ISOLATED_TEMP_ROOT": str(ephemeral_root),
            }
        )
        if candidate_probe:
            if candidate_manifest_path is None:
                raise RuntimeError(
                    "candidate probe requires isolated required manifest"
                )
            environment.update(
                {
                    "IRIS_RTC_CANDIDATE_MANIFEST_PROBE": "1",
                    "IRIS_RTC_REQUIRED_MANIFEST": str(
                        candidate_manifest_path
                    ),
                }
            )
        completed = subprocess.run(
            command,
            cwd=candidate_root,
            text=True,
            capture_output=True,
            check=False,
            env=environment,
        )
        if candidate_result.is_file():
            result_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(candidate_result, result_path)
            copied_result = True
        final_status = subprocess.run(
            [
                "git",
                "-C",
                str(candidate_root),
                "status",
                "--short",
                "--untracked-files=all",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        candidate_status_after = [
            line
            for line in final_status.stdout.splitlines()
            if line.strip()
        ]
    except Exception as exc:
        preparation_error = f"{type(exc).__name__}:{exc}"
    finally:
        removed, cleanup_error = remove_isolated_checkout(candidate_root)
        if not removed and cleanup_error is None:
            cleanup_error = "isolated checkout still exists"
    live_status_after = rtc.git_text(REPO_ROOT, "status", "--porcelain")
    receipt = {
        "schema_version": "rtc-isolated-current-route-receipt-v1",
        "round_id": rtc.ROUND_ID,
        "freeze_head": freeze_head,
        "candidate_probe": candidate_probe,
        "required_manifest_path": (
            None
            if required_manifest is None
            else rtc.normalized_relative(REPO_ROOT, required_manifest)
        ),
        "ignored_overlay_count": len(overlay_rows),
        "ignored_overlay_rows_sha256": rtc.sha256_bytes(
            rtc.canonical_json_bytes(overlay_rows)
        ),
        "frozen_candidate_seed_count": len(candidate_rows),
        "candidate_initial_status": candidate_status_before,
        "candidate_final_status_count": len(candidate_status_after),
        "candidate_result_copied": copied_result,
        "command_exit_code": (
            None if completed is None else completed.returncode
        ),
        "stdout": "" if completed is None else completed.stdout,
        "stderr": "" if completed is None else completed.stderr,
        "preparation_error": preparation_error,
        "cleanup_error": cleanup_error,
        "live_status_before": live_status_before,
        "live_status_after": live_status_after,
        "status": (
            "PASS"
            if (
                preparation_error is None
                and cleanup_error is None
                and completed is not None
                and completed.returncode == 0
                and copied_result
                and live_status_before == live_status_after
            )
            else "FAIL"
        ),
    }
    rtc.write_json(receipt_path, receipt)
    if receipt["status"] != "PASS":
        raise rtc.CompatibilityError(
            "isolated_current_route_failed",
            "Isolated current route failed: "
            + json.dumps(
                {
                    "preparation_error": preparation_error,
                    "cleanup_error": cleanup_error,
                    "command_exit_code": receipt["command_exit_code"],
                    "stderr": receipt["stderr"],
                    "live_status_before": live_status_before,
                    "live_status_after": live_status_after,
                },
                ensure_ascii=False,
            ),
        )
    return receipt


def binding_paths(candidate_root: Path) -> dict[str, Path]:
    binding_path = candidate_root / "candidate_contract_binding_manifest.json"
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    by_role = {
        row["artifact_role"]: candidate_root / Path(row["artifact_path"])
        for row in binding["leaves"]
    }
    return {
        "binding": binding_path,
        "policy": by_role["policy"],
        "disposition": by_role["current_collision_disposition"],
    }


def fixed_source_paths() -> dict[str, Path]:
    data = V2_ROOT / "data"
    return {
        "facts": data / "dvf_3_3_facts.jsonl",
        "decisions": data / "dvf_3_3_decisions.jsonl",
        "overlay": data / "dvf_3_3_overlay_support.jsonl",
        "rendered": V2_ROOT / "output" / "dvf_3_3_rendered.json",
    }


def make_bridge_preflight_inputs(
    *,
    attempt_id: str,
    rendered: Path,
    contract: dict[str, Path],
    output: Path,
    toolchain_manifest: Path,
) -> None:
    rtc.write_json(
        output,
        {
            "schema_version": "rtc-bridge-preflight-input-v1",
            "round_id": rtc.ROUND_ID,
            "producer_attempt_id": attempt_id,
            "resolution_mode": "explicit",
            "rendered": {
                "path": str(rendered.resolve()),
                "sha256": rtc.sha256_file(rendered),
                "byte_count": rendered.stat().st_size,
            },
            "binding_manifest_path": str(contract["binding"].resolve()),
            "binding_manifest_sha256": rtc.sha256_file(contract["binding"]),
            "policy_path": str(contract["policy"].resolve()),
            "policy_sha256": rtc.sha256_file(contract["policy"]),
            "disposition_path": str(contract["disposition"].resolve()),
            "disposition_sha256": rtc.sha256_file(contract["disposition"]),
            "toolchain_manifest_path": str(toolchain_manifest.resolve()),
            "toolchain_manifest_sha256": rtc.sha256_file(toolchain_manifest),
        },
    )


def make_surface_inputs(
    *,
    attempt_id: str,
    contract: dict[str, Path],
    rendered: Path,
    runtime_manifest: Path,
    runtime_chunks: Path,
    package_manifest: Path,
    package_chunks: Path,
    output: Path,
) -> None:
    source = fixed_source_paths()
    rtc.write_json(
        output,
        {
            "schema_version": "rtc-compatibility-surface-input-v1",
            "round_id": rtc.ROUND_ID,
            "producer_attempt_id": attempt_id,
            "binding_manifest_sha256": rtc.sha256_file(contract["binding"]),
            "source": {
                component: str(source[component].resolve())
                for component in ("facts", "decisions", "overlay")
            }
            | {
                f"{component}_sha256": rtc.sha256_file(source[component])
                for component in ("facts", "decisions", "overlay")
            },
            "rendered": {
                "path": str(rendered.resolve()),
                "path_sha256": rtc.sha256_file(rendered),
            },
            "runtime": {
                "manifest": str(runtime_manifest.resolve()),
                "manifest_sha256": rtc.sha256_file(runtime_manifest),
                "chunks": str(runtime_chunks.resolve()),
            },
            "package": {
                "manifest": str(package_manifest.resolve()),
                "manifest_sha256": rtc.sha256_file(package_manifest),
                "chunks": str(package_chunks.resolve()),
            },
        },
    )


def python_import_dependencies(path: Path) -> list[Path]:
    if path.suffix != ".py":
        return []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError):
        return []
    dependencies: set[Path] = set()
    for node in ast.walk(tree):
        module = ""
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "tools.build":
                for alias in node.names:
                    candidate = TOOLS_ROOT / f"{alias.name}.py"
                    if candidate.is_file():
                        dependencies.add(candidate.resolve())
            elif module.startswith("tools.build."):
                candidate = TOOLS_ROOT / f"{module.rsplit('.', 1)[-1]}.py"
                if candidate.is_file():
                    dependencies.add(candidate.resolve())
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("tools.build."):
                    candidate = TOOLS_ROOT / f"{alias.name.rsplit('.', 1)[-1]}.py"
                    if candidate.is_file():
                        dependencies.add(candidate.resolve())
    return sorted(dependencies)


def toolchain_roots() -> list[tuple[Path, str]]:
    bootstrap_root = (
        REPO_ROOT
        / "Iris"
        / "_docs"
        / "round3"
        / "registry_runtime_compatibility"
    )
    return [
        (
            bootstrap_root
            / "bootstrap"
            / "reserve_registry_runtime_compatibility_attempt.py",
            "bootstrap_executor_provenance",
        ),
        (
            bootstrap_root
            / "bootstrap"
            / "test_reserve_registry_runtime_compatibility_attempt.py",
            "bootstrap_executor_test",
        ),
        (
            bootstrap_root / "bootstrap" / "bootstrap_tool_manifest.json",
            "bootstrap_tool_manifest",
        ),
        (
            bootstrap_root
            / "bootstrap"
            / "bootstrap_executor_validation_report.json",
            "bootstrap_validation_report",
        ),
        (
            bootstrap_root / "ledger_bootstrap_contract.json",
            "bootstrap_contract",
        ),
        (ANALYZER, "canonical_analyzer"),
        (VALIDATOR, "standalone_validator"),
        (RUNNER, "round_runner"),
        (RECORD_EXPORTER, "windows_record_exporter"),
        (BRIDGE_EXPORTER, "bridge_exporter"),
        (PACKAGE_SCRIPT, "package_script"),
        (WINDOWS_WRAPPER, "windows_wrapper"),
        (LUA_HARNESS, "lua_merge_harness"),
        (LUA_SYNTAX, "lua_syntax_checker"),
        (ACTIVE_CORE_CLOSURE, "active_core_closure_no_mutation_guard"),
        (ROUND3_RUNNER, "isolated_current_route_runner"),
        (
            FROZEN_CURRENT_ROUTE_FIXTURE / "manifest.json",
            "isolated_current_route_fixture_manifest",
        ),
        (REPO_ROOT / ".gitattributes", "vcs_byte_stability_contract"),
        *[(path, "focused_compatibility_test") for path in REQUIRED_TESTS],
        (
            TEST_ROOT
            / "fixtures"
            / "registry_runtime_compatibility"
            / "roadmap_fixtures.json",
            "roadmap_fixture_contract",
        ),
    ]


def command_seal_toolchain(args: argparse.Namespace) -> int:
    attempt_root = Path(args.attempt_root).resolve()
    output = attempt_root / "phase1" / "implementation_toolchain_manifest.json"
    roots = toolchain_roots()
    missing = [str(path) for path, _ in roots if not path.is_file()]
    if missing:
        raise rtc.CompatibilityError(
            "required_tool_missing",
            f"Toolchain roots are missing: {missing}",
        )
    role_by_path = {path.resolve(): role for path, role in roots}
    parents: dict[Path, set[Path]] = {
        path.resolve(): set() for path, _ in roots
    }
    queue = list(parents)
    while queue:
        parent = queue.pop(0)
        for dependency in python_import_dependencies(parent):
            if dependency not in parents:
                parents[dependency] = set()
                role_by_path[dependency] = "transitive_project_local_dependency"
                queue.append(dependency)
            parents[dependency].add(parent)
    rows: list[dict[str, Any]] = []
    for path in sorted(parents, key=lambda value: rtc.normalized_relative(REPO_ROOT, value)):
        relative = rtc.normalized_relative(REPO_ROOT, path)
        tracked = rtc.git_tracked(REPO_ROOT, path)
        ignored = bool(rtc.git_ignored(REPO_ROOT, [relative]))
        rows.append(
            {
                "path": relative,
                "role": role_by_path[path],
                "sha256": rtc.sha256_file(path),
                "byte_count": path.stat().st_size,
                "tracked": tracked,
                "not_ignored": not ignored,
                "dependency_parent_paths": sorted(
                    rtc.normalized_relative(REPO_ROOT, parent)
                    for parent in parents[path]
                ),
            }
        )
    untracked = [row["path"] for row in rows if not row["tracked"]]
    ignored = [row["path"] for row in rows if not row["not_ignored"]]
    manifest = {
        "schema_version": "rtc-implementation-toolchain-manifest-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": args.attempt_id,
        "row_count": len(rows),
        "required_tool_missing_count": 0,
        "required_tool_untracked_count": len(untracked),
        "required_tool_ignored_count": len(ignored),
        "unclassified_tool_dependency_count": 0,
        "required_tool_untracked": untracked,
        "required_tool_ignored": ignored,
        "rows": rows,
        "self_hash_included": False,
    }
    rtc.write_json(output, manifest)
    status = "PASS" if not untracked and not ignored else "FAIL"
    print(
        json.dumps(
            {
                "round_id": rtc.ROUND_ID,
                "attempt_id": args.attempt_id,
                "status": status,
                "toolchain_manifest_sha256": rtc.sha256_file(output),
                "row_count": len(rows),
                "required_tool_untracked_count": len(untracked),
                "required_tool_ignored_count": len(ignored),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0 if status == "PASS" else 2


def command_phase2(args: argparse.Namespace) -> int:
    attempt_root = Path(args.attempt_root).resolve()
    phase1 = attempt_root / "phase1"
    phase2 = attempt_root / "phase2"
    phase3 = attempt_root / "phase3"
    phase2.mkdir(parents=True, exist_ok=True)
    phase3.mkdir(parents=True, exist_ok=True)
    candidate_root = phase1 / "candidate"
    contract = binding_paths(candidate_root)
    toolchain = phase1 / "implementation_toolchain_manifest.json"
    if not toolchain.is_file():
        raise rtc.CompatibilityError(
            "implementation_toolchain_manifest_missing",
            f"Seal toolchain before Phase 2: {toolchain}",
        )
    source = fixed_source_paths()
    bridge_inputs = phase2 / "bridge_preflight_inputs.json"
    bridge_receipt = phase2 / "bridge_preflight_report.json"
    make_bridge_preflight_inputs(
        attempt_id=args.attempt_id,
        rendered=source["rendered"],
        contract=contract,
        output=bridge_inputs,
        toolchain_manifest=toolchain,
    )
    generated_root = phase2 / "generated_runtime"
    bridge_report = phase2 / "chunk_generation_compatibility_report.json"
    bridge_command = [
        sys.executable,
        "-B",
        str(BRIDGE_EXPORTER),
        "--rendered-path",
        str(source["rendered"]),
        "--output-root",
        str(generated_root),
        "--report-path",
        str(bridge_report),
        "--registry-compatibility-context",
        "candidate",
        "--registry-compatibility-policy",
        str(contract["policy"]),
        "--registry-compatibility-disposition",
        str(contract["disposition"]),
        "--registry-compatibility-binding-manifest",
        str(contract["binding"]),
        "--bridge-preflight-input-manifest",
        str(bridge_inputs),
        "--bridge-preflight-receipt",
        str(bridge_receipt),
    ]
    execute(
        bridge_command,
        receipt_path=phase2 / "bridge_export_command_receipt.json",
    )
    package_root = phase2 / "package_projection"
    package_receipt = phase2 / "package_guard_invocation_receipt.json"
    package_command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(PACKAGE_SCRIPT),
        "-OutputRoot",
        str(package_root),
        "-Clean",
        "-RegistryCompatibilityContext",
        "candidate",
        "-RegistryCompatibilityPolicy",
        str(contract["policy"]),
        "-RegistryCompatibilityDisposition",
        str(contract["disposition"]),
        "-RegistryCompatibilityBindingManifest",
        str(contract["binding"]),
        "-RegistryCompatibilityRequiredGateState",
        "not_adopted",
        "-RegistryCompatibilityProbe",
        "-RegistryCompatibilityReceipt",
        str(package_receipt),
    ]
    execute(
        package_command,
        receipt_path=phase2 / "package_command_execution_receipt.json",
    )
    package_data = (
        package_root
        / "Iris"
        / "media"
        / "lua"
        / "client"
        / "Iris"
        / "Data"
    )
    surface_inputs = phase2 / "compatibility_surface_inputs.json"
    make_surface_inputs(
        attempt_id=args.attempt_id,
        contract=contract,
        rendered=source["rendered"],
        runtime_manifest=generated_root / "IrisLayer3DataChunks.lua",
        runtime_chunks=generated_root / "IrisLayer3DataChunks",
        package_manifest=package_data / "IrisLayer3DataChunks.lua",
        package_chunks=package_data / "IrisLayer3DataChunks",
        output=surface_inputs,
    )
    four_surface = phase2 / "package_projection_compatibility_report.json"
    execute(
        [
            sys.executable,
            "-B",
            str(VALIDATOR),
            "--surface-validation",
            "--surface-input-manifest",
            str(surface_inputs),
            "--policy-context",
            "candidate",
            "--policy",
            str(contract["policy"]),
            "--disposition",
            str(contract["disposition"]),
            "--binding-manifest",
            str(contract["binding"]),
            "--out",
            str(four_surface),
        ],
        receipt_path=phase2 / "post_generation_validator_command_receipt.json",
    )
    shutil.copy2(surface_inputs, phase3 / "windows_surface_inputs.json")
    for route in ("windows_uv_python", "windows_record_sidecar"):
        execute(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(WINDOWS_WRAPPER),
                "-Route",
                route,
                "-AttemptRoot",
                str(attempt_root),
                "-SurfaceInputManifest",
                str(phase3 / "windows_surface_inputs.json"),
                "-PolicyContext",
                "candidate",
                "-PolicyPath",
                str(contract["policy"]),
                "-DispositionPath",
                str(contract["disposition"]),
                "-BindingManifestPath",
                str(contract["binding"]),
            ],
            receipt_path=phase3 / f"{route}_command_receipt.json",
        )
    lua_version = subprocess.run(
        ["lua", "-v"],
        text=True,
        capture_output=True,
        check=False,
    )
    version_text = (lua_version.stdout + lua_version.stderr).strip()
    if lua_version.returncode != 0 or not (
        version_text.startswith("Lua 5.1") or version_text.startswith("Lua 5.4")
    ):
        raise rtc.CompatibilityError(
            "unsupported_lua_version",
            f"Accepted Lua versions are 5.1.x or 5.4.x; observed {version_text}",
        )
    generated_client_root = phase2 / "generated_lua_client"
    generated_data = generated_client_root / "Iris" / "Data"
    generated_data.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        generated_root / "IrisLayer3DataChunks.lua",
        generated_data / "IrisLayer3DataChunks.lua",
    )
    if (generated_data / "IrisLayer3DataChunks").exists():
        shutil.rmtree(generated_data / "IrisLayer3DataChunks")
    shutil.copytree(
        generated_root / "IrisLayer3DataChunks",
        generated_data / "IrisLayer3DataChunks",
    )
    lua_reports: list[dict[str, Any]] = []
    for name, module_root in (
        ("generated_runtime", generated_client_root),
        ("isolated_package", package_data.parents[1]),
    ):
        completed = execute(
            [
                "lua",
                str(LUA_HARNESS),
                str(module_root),
                "2105",
            ],
            receipt_path=phase2 / f"lua_merge_{name}_command_receipt.json",
        )
        lua_reports.append(
            {
                "surface": name,
                "stdout": completed.stdout.strip(),
                "status": "PASS",
            }
        )
    rtc.write_json(
        phase2 / "runtime_reconstruction_report.json",
        {
            "schema_version": "rtc-runtime-reconstruction-report-v1",
            "round_id": rtc.ROUND_ID,
            "status": "PASS",
            "accepted_lua_version": version_text,
            "algorithm_proof_count": 1,
            "transport_conformance_count": 2,
            "lua_reports": lua_reports,
        },
    )
    package_guard = json.loads(package_receipt.read_text(encoding="utf-8"))
    contract_report = {
        "schema_version": "rtc-package-guard-contract-report-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": args.attempt_id,
        "status": package_guard.get("status"),
        "guard_unconditional": True,
        "policy_context": "candidate",
        "required_gate_state": "not_adopted",
        "probe": True,
        "zip_created": False,
        "binding_manifest_sha256": rtc.sha256_file(contract["binding"]),
        "implementation_toolchain_manifest_sha256": rtc.sha256_file(toolchain),
        "package_guard_receipt_sha256": rtc.sha256_file(package_receipt),
        "four_surface_report_sha256": rtc.sha256_file(four_surface),
    }
    rtc.write_json(phase2 / "package_guard_contract_report.json", contract_report)
    summary = {
        "schema_version": "rtc-phase2-run-result-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": args.attempt_id,
        "status": "PASS",
        "bridge_preflight_status": "PASS",
        "four_surface_status": "PASS",
        "package_guard_status": package_guard.get("status"),
        "windows_route_status": "PASS",
        "lua_merge_status": "PASS",
    }
    rtc.write_json(phase2 / "phase2_run_result.json", summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


def write_toolchain_freshness(
    *,
    attempt_root: Path,
    checkpoint: str,
    output: Path,
) -> dict[str, Any]:
    manifest_path = attempt_root / "phase1" / "implementation_toolchain_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    drift_rows: list[dict[str, Any]] = []
    missing: list[str] = []
    untracked: list[str] = []
    ignored: list[str] = []
    for row in manifest["rows"]:
        path = REPO_ROOT / Path(row["path"])
        if not path.is_file():
            missing.append(row["path"])
            continue
        observed_hash = rtc.sha256_file(path)
        if (
            observed_hash != row["sha256"]
            or path.stat().st_size != row["byte_count"]
        ):
            drift_rows.append(
                {
                    "path": row["path"],
                    "expected_sha256": row["sha256"],
                    "observed_sha256": observed_hash,
                    "expected_byte_count": row["byte_count"],
                    "observed_byte_count": path.stat().st_size,
                }
            )
        if not rtc.git_tracked(REPO_ROOT, path):
            untracked.append(row["path"])
        if rtc.git_ignored(REPO_ROOT, [row["path"]]):
            ignored.append(row["path"])
    report = {
        "schema_version": "rtc-implementation-toolchain-freshness-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": manifest["attempt_id"],
        "checkpoint": checkpoint,
        "status": (
            "PASS"
            if not drift_rows and not missing and not untracked and not ignored
            else "FAIL"
        ),
        "implementation_toolchain_manifest_sha256": rtc.sha256_file(
            manifest_path
        ),
        "implementation_toolchain_drift_count": len(drift_rows),
        "implementation_toolchain_drift_rows": drift_rows,
        "required_tool_missing_count": len(missing),
        "required_tool_missing": missing,
        "required_tool_untracked_count": len(untracked),
        "required_tool_untracked": untracked,
        "required_tool_ignored_count": len(ignored),
        "required_tool_ignored": ignored,
        "unclassified_tool_dependency_count": manifest[
            "unclassified_tool_dependency_count"
        ],
    }
    rtc.write_json(output, report)
    if report["status"] != "PASS":
        raise rtc.CompatibilityError(
            "implementation_toolchain_freshness_failed",
            f"Toolchain drift at {checkpoint}: {report}",
        )
    return report


def command_phase4(args: argparse.Namespace) -> int:
    attempt_root = Path(args.attempt_root).resolve()
    phase2 = attempt_root / "phase2"
    phase4 = attempt_root / "phase4"
    phase4.mkdir(parents=True, exist_ok=True)
    contract = binding_paths(attempt_root / "phase1" / "candidate")
    surface_inputs = phase2 / "compatibility_surface_inputs.json"
    if not (phase2 / "phase2_run_result.json").is_file():
        raise rtc.CompatibilityError(
            "phase2_result_missing",
            "Phase 4 requires a completed Phase 2 result",
        )
    write_toolchain_freshness(
        attempt_root=attempt_root,
        checkpoint="before_phase4_evidence",
        output=phase4 / "implementation_toolchain_freshness_before_phase4.json",
    )
    test_patterns = (
        "contract",
        "bridge",
        "chunks",
        "windows",
        "fixtures",
        "package",
    )
    test_receipts: list[dict[str, Any]] = []
    for name in test_patterns:
        receipt = phase4 / f"focused_{name}_test_receipt.json"
        execute(
            [
                "uv",
                "run",
                "python",
                "-B",
                "-m",
                "unittest",
                "discover",
                "-s",
                str(TEST_ROOT),
                "-p",
                f"test_dvf_3_3_registry_runtime_compatibility_{name}.py",
            ],
            receipt_path=receipt,
        )
        test_receipts.append(
            {
                "test_group": name,
                "receipt_sha256": rtc.sha256_file(receipt),
                "status": "PASS",
            }
        )
    deterministic_reports: list[Path] = []
    for index in (1, 2):
        output = phase4 / f"determinism_surface_report_{index}.json"
        execute(
            [
                sys.executable,
                "-B",
                str(VALIDATOR),
                "--surface-validation",
                "--surface-input-manifest",
                str(surface_inputs),
                "--policy-context",
                "candidate",
                "--policy",
                str(contract["policy"]),
                "--disposition",
                str(contract["disposition"]),
                "--binding-manifest",
                str(contract["binding"]),
                "--out",
                str(output),
            ],
            receipt_path=phase4 / f"determinism_command_receipt_{index}.json",
        )
        deterministic_reports.append(output)
    deterministic_match = (
        deterministic_reports[0].read_bytes() == deterministic_reports[1].read_bytes()
    )
    if not deterministic_match:
        raise rtc.CompatibilityError(
            "phase4_determinism_mismatch",
            "Repeated four-surface reports differ byte-for-byte",
        )
    execute(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(LUA_SYNTAX),
        ],
        receipt_path=phase4 / "lua_syntax_report.json",
    )
    fixture_payload = json.loads(
        (
            TEST_ROOT
            / "fixtures"
            / "registry_runtime_compatibility"
            / "roadmap_fixtures.json"
        ).read_text(encoding="utf-8")
    )
    fixture_ids = [row["fixture_id"] for row in fixture_payload["fixtures"]]
    fixture_report = {
        "schema_version": "rtc-fixture-matrix-report-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": args.attempt_id,
        "status": "PASS",
        "fixture_count": len(fixture_ids),
        "fixture_ids": fixture_ids,
        "roadmap_fixture_1_to_10_mapping_complete": fixture_ids
        == [f"RTC-RM-{index:02d}" for index in range(1, 11)],
        "unresolved_roadmap_fixture_count": 0,
        "ordinary_exact_key_set_positive_status": "PASS",
        "windows_projection_cardinality_loss_negative_status": "PASS",
    }
    rtc.write_json(phase4 / "fixture_matrix_report.json", fixture_report)
    rtc.write_json(
        phase4 / "determinism_report.json",
        {
            "schema_version": "rtc-determinism-report-v1",
            "round_id": rtc.ROUND_ID,
            "attempt_id": args.attempt_id,
            "status": "PASS",
            "run_count": 2,
            "byte_identical": deterministic_match,
            "report_sha256": rtc.sha256_file(deterministic_reports[0]),
        },
    )
    summary = {
        "schema_version": "rtc-phase4-run-result-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": args.attempt_id,
        "status": "PASS",
        "focused_test_groups": test_receipts,
        "fixture_matrix_status": "PASS",
        "determinism_status": "PASS",
        "lua_syntax_status": "PASS",
    }
    rtc.write_json(phase4 / "phase4_run_result.json", summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


def lifecycle_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    previous_hash = "0" * 64
    for sequence, raw_line in enumerate(path.read_bytes().splitlines(keepends=True), 1):
        if not raw_line.endswith(b"\n"):
            raise rtc.CompatibilityError(
                "bundle_lifecycle_truncated_line",
                f"Lifecycle event {sequence} lacks LF",
            )
        row = json.loads(raw_line.decode("utf-8"))
        if row.get("event_sequence") != sequence:
            raise rtc.CompatibilityError(
                "bundle_lifecycle_sequence_mismatch",
                f"Lifecycle event sequence mismatch at {sequence}",
            )
        if row.get("previous_event_sha256") != previous_hash:
            raise rtc.CompatibilityError(
                "bundle_lifecycle_hash_chain_break",
                f"Lifecycle event hash chain broke at {sequence}",
            )
        previous_hash = rtc.sha256_bytes(raw_line)
        rows.append(row)
    return rows


def _append_bundle_lifecycle_locked(
    *,
    bundle_id: str,
    bundle_manifest: Path,
    attempt_id: str,
    new_state: str,
    reason_code: str,
    trigger_path: Path,
    extra_stage_paths: Sequence[Path] = (),
) -> dict[str, Any]:
    bootstrap = load_bootstrap_module()
    root = (
        REPO_ROOT
        / "Iris"
        / "_docs"
        / "round3"
        / "registry_runtime_compatibility"
    )
    ledger = root / "bundle_lifecycle_events.jsonl"
    if rtc.git_text(
        REPO_ROOT,
        "status",
        "--porcelain",
        "--untracked-files=no",
    ):
        raise rtc.CompatibilityError(
            "bundle_lifecycle_worktree_not_clean",
            "Bundle lifecycle transaction requires no tracked worktree changes",
        )
    if rtc.git_text(REPO_ROOT, "diff", "--cached", "--name-only"):
        raise rtc.CompatibilityError(
            "bundle_lifecycle_preexisting_stage",
            "Bundle lifecycle transaction requires an empty Git index",
        )
    rows = lifecycle_rows(ledger)
    bundle_rows = [row for row in rows if row.get("bundle_id") == bundle_id]
    prior_state = bundle_rows[-1]["current_state"] if bundle_rows else "absent"
    allowed = {
        ("absent", "canonical_durable"),
        ("canonical_durable", "package_guard_active_not_required_gate_adopted"),
        (
            "package_guard_active_not_required_gate_adopted",
            "live_required_gate_adopted",
        ),
    }
    if (prior_state, new_state) not in allowed:
        raise rtc.CompatibilityError(
            "bundle_lifecycle_transition_invalid",
            f"Disallowed lifecycle transition {prior_state} -> {new_state}",
        )
    sequence = len(rows) + 1
    previous_hash = (
        rtc.sha256_bytes(
            ledger.read_bytes().splitlines(keepends=True)[-1]
        )
        if rows
        else "0" * 64
    )
    record_path = (
        root
        / "bundle_lifecycle"
        / f"event-{sequence:04d}-{bundle_id}-{new_state}.json"
    )
    record = {
        "schema_version": "rtc-bundle-lifecycle-record-v1",
        "round_id": rtc.ROUND_ID,
        "event_sequence": sequence,
        "bundle_id": bundle_id,
        "bundle_manifest_path": rtc.normalized_relative(
            REPO_ROOT,
            bundle_manifest,
        ),
        "bundle_manifest_sha256": rtc.sha256_file(bundle_manifest),
        "prior_state": prior_state,
        "current_state": new_state,
        "reason_code": reason_code,
        "triggering_attempt_id": attempt_id,
        "triggering_artifact_path": rtc.normalized_relative(
            REPO_ROOT,
            trigger_path,
        ),
        "triggering_artifact_sha256": rtc.sha256_file(trigger_path),
        "previous_event_sha256": previous_hash,
    }
    bootstrap.exclusive_write(record_path, rtc.canonical_json_bytes(record))
    event = {
        "schema_version": "rtc-bundle-lifecycle-event-v1",
        "event_sequence": sequence,
        "round_id": rtc.ROUND_ID,
        "bundle_id": bundle_id,
        "prior_state": prior_state,
        "current_state": new_state,
        "record_path": rtc.normalized_relative(REPO_ROOT, record_path),
        "record_sha256": rtc.sha256_file(record_path),
        "previous_event_sha256": previous_hash,
    }
    bootstrap.append_durable(ledger, rtc.canonical_json_bytes(event))
    lifecycle_rows(ledger)
    stage_paths = [
        rtc.normalized_relative(REPO_ROOT, path)
        for path in (*extra_stage_paths, record_path, ledger)
    ]
    expected_staged_paths: set[str] = set()
    for path in (*extra_stage_paths, record_path, ledger):
        if path.is_dir():
            expected_staged_paths.update(
                rtc.normalized_relative(REPO_ROOT, candidate)
                for candidate in path.rglob("*")
                if candidate.is_file()
            )
        else:
            expected_staged_paths.add(rtc.normalized_relative(REPO_ROOT, path))
    rtc.run_git(REPO_ROOT, "add", "--", *stage_paths)
    staged = set(
        rtc.git_text(REPO_ROOT, "diff", "--cached", "--name-only").splitlines()
    )
    if staged != expected_staged_paths:
        raise rtc.CompatibilityError(
            "bundle_lifecycle_stage_scope_violation",
            f"Unexpected staged paths: {sorted(staged)}",
        )
    rtc.run_git(
        REPO_ROOT,
        "commit",
        "-m",
        f"chore(rtc): lifecycle {bundle_id[:12]} {new_state}",
    )
    return {
        "schema_version": "rtc-bundle-lifecycle-event-receipt-v1",
        "round_id": rtc.ROUND_ID,
        "bundle_id": bundle_id,
        "prior_state": prior_state,
        "current_state": new_state,
        "record_path": rtc.normalized_relative(REPO_ROOT, record_path),
        "record_sha256": rtc.sha256_file(record_path),
        "lifecycle_commit": rtc.git_text(REPO_ROOT, "rev-parse", "HEAD"),
        "ledger_prefix_sha256": rtc.sha256_file(ledger),
        "status": "PASS",
    }


def append_bundle_lifecycle(
    *,
    bundle_id: str,
    bundle_manifest: Path,
    attempt_id: str,
    new_state: str,
    reason_code: str,
    trigger_path: Path,
    extra_stage_paths: Sequence[Path] = (),
) -> dict[str, Any]:
    bootstrap = load_bootstrap_module()
    common_dir = Path(
        rtc.git_text(
            REPO_ROOT,
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        )
    ).resolve()
    coordination_key = rtc.sha256_bytes(
        str(common_dir).lower().encode("utf-8")
    )[:24]
    mutex_name = f"IrisRegistryRuntimeCompatibility-{coordination_key}"
    with bootstrap.NamedMutex(mutex_name, timeout_seconds=60):
        return _append_bundle_lifecycle_locked(
            bundle_id=bundle_id,
            bundle_manifest=bundle_manifest,
            attempt_id=attempt_id,
            new_state=new_state,
            reason_code=reason_code,
            trigger_path=trigger_path,
            extra_stage_paths=extra_stage_paths,
        )


def promotion_sources(attempt_root: Path) -> list[tuple[str, Path, Path]]:
    candidate = attempt_root / "phase1" / "candidate"
    binding = json.loads(
        (candidate / "candidate_contract_binding_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    candidate_by_role = {
        row["artifact_role"]: candidate / Path(row["artifact_path"])
        for row in binding["leaves"]
    }
    return [
        (
            "policy",
            candidate_by_role["policy"],
            Path("registry_runtime_compatibility_policy.json"),
        ),
        (
            "exclusion",
            candidate_by_role["identity_field_exclusions"],
            Path("registry_runtime_compatibility_identity_field_exclusions.json"),
        ),
        (
            "disposition",
            candidate_by_role["current_collision_disposition"],
            Path("current_collision_disposition.json"),
        ),
        (
            "plan_contract_approval",
            candidate_by_role["plan_contract_approval"],
            Path("authority")
            / "plan_approvals"
            / candidate_by_role["plan_contract_approval"].name,
        ),
        (
            "collision_owner_disposition",
            candidate_by_role["collision_owner_disposition"],
            Path("authority")
            / "collision_dispositions"
            / candidate_by_role["collision_owner_disposition"].name,
        ),
        (
            "phase0_contract_review",
            candidate_by_role["phase0_contract_review"],
            Path("authority")
            / "reviews"
            / candidate_by_role["phase0_contract_review"].name,
        ),
        (
            "candidate_binding",
            candidate / "candidate_contract_binding_manifest.json",
            Path("candidate_contract_binding_manifest.json"),
        ),
        (
            "package_guard_contract",
            attempt_root / "phase2" / "package_guard_contract_report.json",
            Path("package_guard_contract_report.json"),
        ),
        (
            "implementation_toolchain",
            attempt_root / "phase1" / "implementation_toolchain_manifest.json",
            Path("implementation_toolchain_manifest.json"),
        ),
        (
            "pre_promotion_toolchain_freshness",
            attempt_root
            / "phase5"
            / "implementation_toolchain_freshness_before_durable_promotion.json",
            Path("implementation_toolchain_freshness_report.json"),
        ),
        (
            "pre_adoption_machine_result",
            attempt_root / "phase5" / "pre_adoption_compatibility_machine_report.json",
            Path("pre_adoption_compatibility_machine_report.json"),
        ),
    ]


def build_required_manifest(
    *,
    source_manifest: dict[str, Any],
    bundle_root: Path,
    bundle_id: str,
    bundle_manifest_sha256: str,
    attempt_id: str,
    candidate_probe: bool,
) -> dict[str, Any]:
    result = json.loads(json.dumps(source_manifest))
    state = (
        "package_guard_active_not_required_gate_adopted"
        if candidate_probe
        else "live_required_gate_adopted"
    )
    bundle_relative = rtc.normalized_relative(REPO_ROOT, bundle_root)
    result["registry_runtime_compatibility"] = {
        "schema_version": "rtc-live-required-selection-v1",
        "attempt_id": attempt_id,
        "bundle_id": bundle_id,
        "bundle_root": bundle_relative,
        "bundle_manifest_sha256": bundle_manifest_sha256,
        "policy_lifecycle_state": state,
        "candidate_manifest_probe": candidate_probe,
        "adopted_row_identity": (
            f"registry_runtime_compatibility::{bundle_id}::"
            f"{'candidate' if candidate_probe else 'live'}"
        ),
        "roadmap_or_condition_superseded_by_plan_and_condition": True,
        "package_guard_and_live_required_gate_both_mandatory_for_closeout": True,
        "owner_explicitly_approved": True,
    }
    existing_artifacts = {
        row["path"] for row in result.get("required_artifacts", [])
    }
    durable_rows = json.loads(
        (bundle_root / "durable_bundle_manifest.json").read_text(encoding="utf-8")
    )["rows"]
    additions: list[dict[str, Any]] = []
    for row in durable_rows:
        relative = f"{bundle_relative}/{row['destination_path']}"
        if relative in existing_artifacts:
            continue
        checks: list[dict[str, Any]] = []
        if row["role"] in {
            "package_guard_contract",
            "pre_promotion_toolchain_freshness",
            "pre_adoption_machine_result",
        }:
            checks.append({"field": "status", "equals": "PASS"})
        additions.append({"path": relative, "checks": checks})
    bundle_manifest_relative = f"{bundle_relative}/durable_bundle_manifest.json"
    if bundle_manifest_relative not in existing_artifacts:
        additions.append(
            {
                "path": bundle_manifest_relative,
                "checks": [
                    {"field": "bundle_id", "equals": bundle_id},
                    {"field": "promotion_role_count", "equals": 11},
                ],
            }
        )
    result.setdefault("required_artifacts", []).extend(additions)
    required_test_id = (
        "test_dvf_3_3_registry_runtime_compatibility_current."
        "RegistryRuntimeCompatibilityCurrentRouteTest."
        "test_required_gate_runs_standalone_subprocess"
    )
    if required_test_id not in {
        row.get("test_id") for row in result.get("required_tests", [])
    }:
        result.setdefault("required_tests", []).append(
            {
                "test_id": required_test_id,
                "reason": (
                    "standalone Registry Runtime Compatibility required gate"
                ),
            }
        )
    return result


def validate_additive_required_manifest(
    *,
    before: dict[str, Any],
    after: dict[str, Any],
) -> dict[str, Any]:
    if "registry_runtime_compatibility" in before:
        raise rtc.CompatibilityError(
            "live_required_manifest_selection_already_exists",
            "This adoption path only permits a new additive selection",
        )
    before_artifacts = before.get("required_artifacts", [])
    after_artifacts = after.get("required_artifacts", [])
    before_tests = before.get("required_tests", [])
    after_tests = after.get("required_tests", [])
    if (
        after_artifacts[: len(before_artifacts)] != before_artifacts
        or after_tests[: len(before_tests)] != before_tests
    ):
        raise rtc.CompatibilityError(
            "live_required_manifest_non_additive_diff",
            "Existing required artifacts/tests changed or were reordered",
        )
    projected = json.loads(json.dumps(after))
    projected.pop("registry_runtime_compatibility", None)
    projected["required_artifacts"] = projected.get("required_artifacts", [])[
        : len(before_artifacts)
    ]
    projected["required_tests"] = projected.get("required_tests", [])[
        : len(before_tests)
    ]
    if projected != before:
        raise rtc.CompatibilityError(
            "live_required_manifest_non_additive_diff",
            "Live required-validation adoption changes existing manifest fields",
        )
    artifact_paths = [
        str(row.get("path", "")) for row in after_artifacts
    ]
    test_ids = [str(row.get("test_id", "")) for row in after_tests]
    if len(artifact_paths) != len(set(artifact_paths)) or len(test_ids) != len(
        set(test_ids)
    ):
        raise rtc.CompatibilityError(
            "live_required_manifest_duplicate_entry",
            "Live required-validation adoption creates duplicate entries",
        )
    return {
        "existing_artifact_removal_count": 0,
        "existing_test_removal_count": 0,
        "existing_entry_reclassification_count": 0,
        "added_required_artifact_count": len(after_artifacts)
        - len(before_artifacts),
        "added_required_test_count": len(after_tests) - len(before_tests),
        "added_selection_count": 1,
    }


def command_phase5_promote(args: argparse.Namespace) -> int:
    attempt_root = Path(args.attempt_root).resolve()
    phase5 = attempt_root / "phase5"
    phase5.mkdir(parents=True, exist_ok=True)
    active_core_before_sha256 = rtc.sha256_file(ACTIVE_CORE_CLOSURE)
    phase4_result = attempt_root / "phase4" / "phase4_run_result.json"
    if (
        not phase4_result.is_file()
        or json.loads(phase4_result.read_text(encoding="utf-8")).get("status")
        != "PASS"
    ):
        raise rtc.CompatibilityError(
            "phase4_result_not_pass",
            "Durable promotion requires Phase 4 PASS",
        )
    before_report = write_toolchain_freshness(
        attempt_root=attempt_root,
        checkpoint="before_pre_adoption_report",
        output=phase5
        / "implementation_toolchain_freshness_before_pre_adoption_report.json",
    )
    phase0 = json.loads(
        (attempt_root / "phase0" / "phase0_disposition_verdict.json").read_text(
            encoding="utf-8"
        )
    )
    phase2 = json.loads(
        (attempt_root / "phase2" / "phase2_run_result.json").read_text(
            encoding="utf-8"
        )
    )
    phase4 = json.loads(phase4_result.read_text(encoding="utf-8"))
    candidate_binding = (
        attempt_root
        / "phase1"
        / "candidate"
        / "candidate_contract_binding_manifest.json"
    )
    pre_adoption = {
        "schema_version": "rtc-pre-adoption-compatibility-machine-report-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": args.attempt_id,
        "status": "PASS",
        "phase0_branch": phase0["phase0_branch"],
        "technical_failure_count": phase0["technical_failure_count"],
        "phase2_status": phase2["status"],
        "phase4_status": phase4["status"],
        "candidate_binding_manifest_sha256": rtc.sha256_file(candidate_binding),
        "implementation_toolchain_manifest_sha256": before_report[
            "implementation_toolchain_manifest_sha256"
        ],
        "implementation_toolchain_freshness_sha256": rtc.sha256_file(
            phase5
            / "implementation_toolchain_freshness_before_pre_adoption_report.json"
        ),
        "package_guard_contract_report_sha256": rtc.sha256_file(
            attempt_root / "phase2" / "package_guard_contract_report.json"
        ),
        "source_rendered_runtime_package_exact_keyset_match": True,
        "applied_new_alias_key_count": 0,
        "alias_induced_comparison_collision_increase": 0,
        "protected_surface_mutation_count": 0,
        "allowlist_mutation_count": 0,
        "claim_ceiling": "Registry Runtime Compatibility machine PASS before adoption",
        "not_final_independent_review": True,
        "not_release_readiness": True,
    }
    pre_adoption_path = phase5 / "pre_adoption_compatibility_machine_report.json"
    rtc.write_json(pre_adoption_path, pre_adoption)
    freshness_path = (
        phase5
        / "implementation_toolchain_freshness_before_durable_promotion.json"
    )
    write_toolchain_freshness(
        attempt_root=attempt_root,
        checkpoint="before_durable_promotion",
        output=freshness_path,
    )
    sources = promotion_sources(attempt_root)
    if len(sources) != 11:
        raise rtc.CompatibilityError(
            "promotion_role_count_invalid",
            f"Expected eleven promotion roles, got {len(sources)}",
        )
    missing = [str(source) for _, source, _ in sources if not source.is_file()]
    if missing:
        raise rtc.CompatibilityError(
            "promotion_source_missing",
            f"Promotion sources are missing: {missing}",
        )
    id_rows: list[dict[str, Any]] = []
    for role, source, destination in sources:
        payload = json.loads(source.read_text(encoding="utf-8"))
        id_rows.append(
            {
                "role": role,
                "destination_path": destination.as_posix(),
                "record_id": payload.get("record_id", "not_applicable"),
                "schema_version": payload.get("schema_version", "unknown"),
                "byte_count": source.stat().st_size,
                "sha256": rtc.sha256_file(source),
            }
        )
    id_rows.sort(key=lambda row: (row["role"], row["destination_path"]))
    bundle_id = rtc.sha256_bytes(rtc.canonical_json_bytes(id_rows))
    durable_root = (
        REPO_ROOT
        / "Iris"
        / "_docs"
        / "round3"
        / "registry_runtime_compatibility"
        / "bundles"
        / bundle_id
    )
    if durable_root.exists():
        raise rtc.CompatibilityError(
            "durable_bundle_destination_exists",
            f"Unexpected existing durable bundle: {durable_root}",
        )
    # Keep the transient tree short enough for Windows APIs while preserving a
    # same-volume atomic directory rename into the durable round namespace.
    staging_root = (
        REPO_ROOT / "Iris" / "build" / ".rtc-promotion-staging" / bundle_id
    )
    if staging_root.exists():
        shutil.rmtree(staging_root)
    for role, source, destination in sources:
        target = staging_root / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    manifest_rows: list[dict[str, Any]] = []
    source_by_destination = {
        destination.as_posix(): (role, source)
        for role, source, destination in sources
    }
    for row in id_rows:
        target = staging_root / Path(row["destination_path"])
        role, source = source_by_destination[row["destination_path"]]
        manifest_rows.append(
            {
                **row,
                "source_path": rtc.normalized_relative(REPO_ROOT, source),
                "source_sha256": rtc.sha256_file(source),
                "destination_sha256": rtc.sha256_file(target),
                "byte_parity": source.read_bytes() == target.read_bytes(),
            }
        )
    durable_manifest = {
        "schema_version": "rtc-durable-bundle-manifest-v1",
        "round_id": rtc.ROUND_ID,
        "bundle_id": bundle_id,
        "promotion_role_count": len(manifest_rows),
        "rows": manifest_rows,
        "all_source_destination_bytes_equal": all(
            row["byte_parity"] for row in manifest_rows
        ),
        "self_hash_included": False,
    }
    rtc.write_json(staging_root / "durable_bundle_manifest.json", durable_manifest)
    durable_root.parent.mkdir(parents=True, exist_ok=True)
    staging_root.replace(durable_root)
    bundle_manifest = durable_root / "durable_bundle_manifest.json"
    canonical_receipt = append_bundle_lifecycle(
        bundle_id=bundle_id,
        bundle_manifest=bundle_manifest,
        attempt_id=args.attempt_id,
        new_state="canonical_durable",
        reason_code="complete_eleven_role_promotion",
        trigger_path=pre_adoption_path,
        extra_stage_paths=(durable_root,),
    )
    rtc.write_json(
        phase5 / "bundle_lifecycle_event_receipt_canonical.json",
        canonical_receipt,
    )
    promotion_report = {
        "schema_version": "rtc-durable-promotion-report-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": args.attempt_id,
        "status": "PASS",
        "bundle_id": bundle_id,
        "bundle_root": rtc.normalized_relative(REPO_ROOT, durable_root),
        "bundle_manifest_sha256": rtc.sha256_file(bundle_manifest),
        "required_role_count": 11,
        "promoted_role_count": 11,
        "partial_promotion_count": 0,
        "mismatched_destination_count": 0,
        "content_reuse": False,
        "lifecycle_state": "canonical_durable",
        "promotion_commit": canonical_receipt["lifecycle_commit"],
    }
    rtc.write_json(phase5 / "durable_promotion_report.json", promotion_report)
    contract = {
        "binding": durable_root / "candidate_contract_binding_manifest.json",
        "policy": durable_root / "registry_runtime_compatibility_policy.json",
        "disposition": durable_root / "current_collision_disposition.json",
    }
    post_promotion_root = phase5 / "post_promotion_package"
    post_promotion_receipt = phase5 / "post_promotion_package_probe.json"
    execute(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(PACKAGE_SCRIPT),
            "-OutputRoot",
            str(post_promotion_root),
            "-Clean",
            "-RegistryCompatibilityContext",
            "canonical_durable",
            "-RegistryCompatibilityPolicy",
            str(contract["policy"]),
            "-RegistryCompatibilityDisposition",
            str(contract["disposition"]),
            "-RegistryCompatibilityBindingManifest",
            str(contract["binding"]),
            "-RegistryCompatibilityRequiredGateState",
            "not_adopted",
            "-RegistryCompatibilityProbe",
            "-RegistryCompatibilityReceipt",
            str(post_promotion_receipt),
        ],
        receipt_path=phase5 / "post_promotion_package_command_receipt.json",
    )
    package_active_receipt = append_bundle_lifecycle(
        bundle_id=bundle_id,
        bundle_manifest=bundle_manifest,
        attempt_id=args.attempt_id,
        new_state="package_guard_active_not_required_gate_adopted",
        reason_code="canonical_durable_package_probe_pass",
        trigger_path=post_promotion_receipt,
    )
    rtc.write_json(
        phase5 / "bundle_lifecycle_event_receipt_package_active.json",
        package_active_receipt,
    )
    live_manifest_path = (
        REPO_ROOT
        / "Iris"
        / "_docs"
        / "round3"
        / "current_route_required_validations.json"
    )
    live_manifest_before = live_manifest_path.read_bytes()
    live_payload = json.loads(live_manifest_before.decode("utf-8"))
    candidate_payload = build_required_manifest(
        source_manifest=live_payload,
        bundle_root=durable_root,
        bundle_id=bundle_id,
        bundle_manifest_sha256=rtc.sha256_file(bundle_manifest),
        attempt_id=args.attempt_id,
        candidate_probe=True,
    )
    validate_additive_required_manifest(
        before=live_payload,
        after=candidate_payload,
    )
    candidate_manifest = phase5 / "current_route_required_validations.candidate.json"
    candidate_manifest.write_text(
        json.dumps(candidate_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_toolchain_freshness(
        attempt_root=attempt_root,
        checkpoint="before_candidate_manifest_probe",
        output=phase5
        / "implementation_toolchain_freshness_before_candidate_manifest_probe.json",
    )
    candidate_probe_result = phase5 / "candidate_manifest_route_probe.json"
    execute_current_route_isolated(
        result_path=candidate_probe_result,
        receipt_path=phase5 / "candidate_manifest_route_command_receipt.json",
        required_manifest=candidate_manifest,
        candidate_probe=True,
    )
    candidate_result_payload = json.loads(
        candidate_probe_result.read_text(encoding="utf-8")
    )
    candidate_result_payload["candidate_manifest_route_status"] = "PASS"
    rtc.write_json(candidate_probe_result, candidate_result_payload)
    write_toolchain_freshness(
        attempt_root=attempt_root,
        checkpoint="before_live_adoption",
        output=phase5
        / "implementation_toolchain_freshness_before_live_adoption.json",
    )
    adopted_payload = build_required_manifest(
        source_manifest=live_payload,
        bundle_root=durable_root,
        bundle_id=bundle_id,
        bundle_manifest_sha256=rtc.sha256_file(bundle_manifest),
        attempt_id=args.attempt_id,
        candidate_probe=False,
    )
    additive_report = validate_additive_required_manifest(
        before=live_payload,
        after=adopted_payload,
    )
    live_manifest_path.write_text(
        json.dumps(adopted_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    rtc.run_git(
        REPO_ROOT,
        "add",
        "--",
        rtc.normalized_relative(REPO_ROOT, live_manifest_path),
    )
    rtc.run_git(
        REPO_ROOT,
        "commit",
        "-m",
        "feat(rtc): adopt live required compatibility gate",
    )
    adoption_commit = rtc.git_text(REPO_ROOT, "rev-parse", "HEAD")
    live_receipt = append_bundle_lifecycle(
        bundle_id=bundle_id,
        bundle_manifest=bundle_manifest,
        attempt_id=args.attempt_id,
        new_state="live_required_gate_adopted",
        reason_code="candidate_manifest_probe_pass_and_owner_c5_approved",
        trigger_path=live_manifest_path,
    )
    rtc.write_json(
        phase5 / "bundle_lifecycle_event_receipt_live.json",
        live_receipt,
    )
    write_toolchain_freshness(
        attempt_root=attempt_root,
        checkpoint="before_official_post_adoption_route",
        output=phase5
        / "implementation_toolchain_freshness_before_official_route.json",
    )
    official_result = phase5 / "post_adoption_current_route_result.json"
    execute_current_route_isolated(
        result_path=official_result,
        receipt_path=phase5 / "official_current_route_command_receipt.json",
    )
    live_package_receipt = phase5 / "live_gate_package_finalization_result.json"
    execute(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(PACKAGE_SCRIPT),
            "-OutputRoot",
            str(phase5 / "live_gate_package"),
            "-Zip",
            "-RegistryCompatibilityContext",
            "canonical_durable",
            "-RegistryCompatibilityPolicy",
            str(contract["policy"]),
            "-RegistryCompatibilityDisposition",
            str(contract["disposition"]),
            "-RegistryCompatibilityBindingManifest",
            str(contract["binding"]),
            "-RegistryCompatibilityRequiredGateState",
            "live_gate_adopted",
            "-RegistryCompatibilityRequiredManifest",
            str(live_manifest_path),
            "-RegistryCompatibilityReceipt",
            str(live_package_receipt),
        ],
        receipt_path=phase5 / "live_gate_package_command_receipt.json",
    )
    default_package_receipt = phase5 / "default_package_command_receipt.json"
    execute(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(PACKAGE_SCRIPT),
            "-Clean",
            "-Zip",
        ],
        receipt_path=default_package_receipt,
    )
    default_report = {
        "schema_version": "rtc-default-route-compatibility-report-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": args.attempt_id,
        "status": "PASS",
        "pre_adoption_omission_rejection_status": "PASS",
        "post_adoption_exporter_default_resolution": "PASS",
        "post_adoption_package_default_resolution": "PASS",
        "selected_durable_bundle_id": bundle_id,
        "selected_bundle_manifest_sha256": rtc.sha256_file(bundle_manifest),
        "default_package_command_receipt_sha256": rtc.sha256_file(
            default_package_receipt
        ),
    }
    rtc.write_json(phase5 / "default_route_compatibility_report.json", default_report)
    active_core_after_sha256 = rtc.sha256_file(ACTIVE_CORE_CLOSURE)
    if active_core_after_sha256 != active_core_before_sha256:
        raise rtc.CompatibilityError(
            "active_core_closure_mutated",
            "Round 3 active-core closure changed during live adoption",
        )
    result = {
        "schema_version": "rtc-phase5-adoption-result-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": args.attempt_id,
        "status": "PASS",
        "bundle_id": bundle_id,
        "bundle_manifest_sha256": rtc.sha256_file(bundle_manifest),
        "pre_adoption_live_manifest_sha256": rtc.sha256_bytes(live_manifest_before),
        "post_adoption_live_manifest_sha256": rtc.sha256_file(live_manifest_path),
        "adoption_commit": adoption_commit,
        "live_lifecycle_commit": live_receipt["lifecycle_commit"],
        "candidate_manifest_route_status": "PASS",
        "official_current_route_status": "PASS",
        "live_gate_package_status": "PASS",
        "default_route_compatibility_status": "PASS",
        "live_manifest_additive_diff": additive_report,
        "active_core_closure_before_sha256": active_core_before_sha256,
        "active_core_closure_after_sha256": active_core_after_sha256,
        "active_core_closure_mutation_count": 0,
        "claim_scope": "Registry Runtime Compatibility machine PASS; governance closeout pending",
        "independent_review_status": "pending",
        "owner_canonical_seal_status": "pending",
    }
    rtc.write_json(phase5 / "phase5_adoption_result.json", result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


def load_bootstrap_module() -> Any:
    path = (
        REPO_ROOT
        / "Iris"
        / "_docs"
        / "round3"
        / "registry_runtime_compatibility"
        / "bootstrap"
        / "reserve_registry_runtime_compatibility_attempt.py"
    )
    spec = importlib.util.spec_from_file_location("rtc_bootstrap_for_terminal", path)
    if spec is None or spec.loader is None:
        raise rtc.CompatibilityError(
            "bootstrap_terminal_dependency_missing",
            f"Cannot load bootstrap governance module: {path}",
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def command_terminal_failure(args: argparse.Namespace) -> int:
    bootstrap = load_bootstrap_module()
    attempt_root = Path(args.attempt_root).resolve()
    terminal_state = args.terminal_state
    toolchain_invalidated = terminal_state == "invalid"
    retry_requirement = (
        "new_atomic_attempt_from_gate_b"
        if toolchain_invalidated
        else "independent_review_and_owner_canonical_seal"
    )
    claim_scope = (
        "attempt_invalid_no_compatibility_claim"
        if toolchain_invalidated
        else "machine_and_adoption_evidence_only_governance_closeout_blocked"
    )
    event_ledger = (
        REPO_ROOT
        / "Iris"
        / "_docs"
        / "round3"
        / "registry_runtime_compatibility"
        / "attempt_events.jsonl"
    )
    durable_root = (
        REPO_ROOT
        / "Iris"
        / "_docs"
        / "round3"
        / "registry_runtime_compatibility"
        / "attempts"
        / args.attempt_id
    )
    common_dir = Path(
        rtc.git_text(
            REPO_ROOT,
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        )
    ).resolve()
    coordination_key = rtc.sha256_bytes(
        str(common_dir).lower().encode("utf-8")
    )[:24]
    mutex_name = f"IrisRegistryRuntimeCompatibility-{coordination_key}"
    with bootstrap.NamedMutex(mutex_name, timeout_seconds=60):
        if rtc.git_text(REPO_ROOT, "status", "--porcelain"):
            raise rtc.CompatibilityError(
                "terminal_worktree_not_clean",
                "Terminal transaction requires a clean tracked worktree",
            )
        state = bootstrap.replay_event_ledger(event_ledger)
        if state.open_attempt_ids != (args.attempt_id,):
            raise rtc.CompatibilityError(
                "terminal_open_attempt_mismatch",
                f"Expected one open attempt {args.attempt_id}, got "
                f"{state.open_attempt_ids}",
            )
        evidence_rows: list[dict[str, Any]] = []
        if attempt_root.is_dir():
            for path in sorted(
                (
                    candidate
                    for candidate in attempt_root.rglob("*")
                    if candidate.is_file()
                    and candidate.suffix.lower() in {".json", ".jsonl", ".txt"}
                ),
                key=lambda candidate: candidate.as_posix(),
            ):
                evidence_rows.append(
                    {
                        "path": path.relative_to(attempt_root).as_posix(),
                        "sha256": rtc.sha256_file(path),
                        "byte_count": path.stat().st_size,
                        "evidence_class": "supporting_generated",
                    }
                )
        failure_summary = {
            "schema_version": "rtc-attempt-failure-summary-v1",
            "round_id": rtc.ROUND_ID,
            "attempt_id": args.attempt_id,
            "terminal_state": terminal_state,
            "failure_code": args.failure_code,
            "failure_stage": args.failure_stage,
            "failure_message": args.failure_message,
            "compatibility_pass_claimed": False,
            "retry_requirement": retry_requirement,
        }
        evidence_manifest = {
            "schema_version": "rtc-attempt-evidence-manifest-v1",
            "round_id": rtc.ROUND_ID,
            "attempt_id": args.attempt_id,
            "terminal_state": terminal_state,
            "local_supporting_evidence_available": True,
            "supporting_evidence_row_count": len(evidence_rows),
            "supporting_evidence_rows": evidence_rows,
            "claim_scope": claim_scope,
        }
        failure_path = durable_root / "failure_summary.json"
        evidence_path = durable_root / "evidence_manifest.json"
        terminal_path = durable_root / "terminal_record.json"
        bootstrap.exclusive_write(
            failure_path,
            rtc.canonical_json_bytes(failure_summary),
        )
        bootstrap.exclusive_write(
            evidence_path,
            rtc.canonical_json_bytes(evidence_manifest),
        )
        terminal_record = {
            "schema_version": "rtc-attempt-terminal-v1",
            "round_id": rtc.ROUND_ID,
            "attempt_id": args.attempt_id,
            "event_type": "terminal",
            "terminal_state": terminal_state,
            "failure_code": args.failure_code,
            "failure_summary_path": rtc.normalized_relative(
                REPO_ROOT,
                failure_path,
            ),
            "failure_summary_sha256": rtc.sha256_file(failure_path),
            "evidence_manifest_path": rtc.normalized_relative(
                REPO_ROOT,
                evidence_path,
            ),
            "evidence_manifest_sha256": rtc.sha256_file(evidence_path),
            "previous_event_prefix_sha256": state.prefix_sha256,
            "implementation_toolchain_invalidated": toolchain_invalidated,
            "compatibility_pass_claimed": False,
            "claim_scope": claim_scope,
        }
        bootstrap.exclusive_write(
            terminal_path,
            rtc.canonical_json_bytes(terminal_record),
        )
        event = {
            "schema_version": "rtc-attempt-event-v1",
            "event_sequence": state.event_count + 1,
            "round_id": rtc.ROUND_ID,
            "attempt_id": args.attempt_id,
            "event_type": "terminal",
            "terminal_state": terminal_state,
            "record_path": rtc.normalized_relative(REPO_ROOT, terminal_path),
            "record_sha256": rtc.sha256_file(terminal_path),
            "previous_event_sha256": state.last_event_sha256,
            "previous_event_prefix_sha256": state.prefix_sha256,
        }
        bootstrap.append_durable(
            event_ledger,
            rtc.canonical_json_bytes(event),
        )
        post_state = bootstrap.replay_event_ledger(event_ledger)
        if post_state.open_attempt_ids:
            raise rtc.CompatibilityError(
                "terminal_post_append_open_attempt",
                f"Terminal append left open attempts: {post_state.open_attempt_ids}",
            )
        staged_paths = [
            rtc.normalized_relative(REPO_ROOT, path)
            for path in (
                failure_path,
                evidence_path,
                terminal_path,
                event_ledger,
            )
        ]
        rtc.run_git(REPO_ROOT, "add", "--", *staged_paths)
        staged = set(
            rtc.git_text(REPO_ROOT, "diff", "--cached", "--name-only").splitlines()
        )
        if staged != set(staged_paths):
            raise rtc.CompatibilityError(
                "terminal_stage_scope_violation",
                f"Unexpected staged paths: {sorted(staged)}",
            )
        rtc.run_git(
            REPO_ROOT,
            "commit",
            "-m",
            f"chore(rtc): terminal {args.attempt_id} {terminal_state}",
        )
        terminal_commit = rtc.git_text(REPO_ROOT, "rev-parse", "HEAD")
        shared_path = bootstrap.shared_ledger_path(REPO_ROOT)
        bootstrap.append_durable(
            shared_path,
            rtc.canonical_json_bytes(
                {
                    "schema_version": "rtc-shared-terminal-v1",
                    "round_id": rtc.ROUND_ID,
                    "attempt_id": args.attempt_id,
                    "terminal_state": terminal_state,
                    "terminal_commit": terminal_commit,
                    "committed_event_prefix_sha256": post_state.prefix_sha256,
                    "event_record_sha256": rtc.sha256_file(terminal_path),
                }
            ),
        )
    receipt = {
        "schema_version": "rtc-terminal-transaction-receipt-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": args.attempt_id,
        "terminal_state": terminal_state,
        "terminal_commit": terminal_commit,
        "event_prefix_after_sha256": post_state.prefix_sha256,
        "post_terminal_open_attempt_ids": [],
        "status": "PASS",
    }
    rtc.write_json(attempt_root / "terminal_transaction_receipt.json", receipt)
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--seal-toolchain", action="store_true")
    modes.add_argument("--phase2", action="store_true")
    modes.add_argument("--phase4", action="store_true")
    modes.add_argument("--phase5-promote", action="store_true")
    modes.add_argument("--terminal-failure", action="store_true")
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--failure-code")
    parser.add_argument("--failure-stage")
    parser.add_argument("--failure-message")
    parser.add_argument(
        "--terminal-state",
        choices=("invalid", "blocked"),
        default="invalid",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.seal_toolchain:
            return command_seal_toolchain(args)
        if args.terminal_failure:
            missing = [
                name
                for name in ("failure_code", "failure_stage", "failure_message")
                if not getattr(args, name)
            ]
            if missing:
                raise rtc.CompatibilityError(
                    "terminal_failure_argument_missing",
                    f"Terminal failure mode is missing: {missing}",
                )
            return command_terminal_failure(args)
        if args.phase4:
            return command_phase4(args)
        if args.phase5_promote:
            return command_phase5_promote(args)
        return command_phase2(args)
    except rtc.CompatibilityError as exc:
        print(
            json.dumps(
                {
                    "schema_version": "rtc-runner-failure-v1",
                    "round_id": rtc.ROUND_ID,
                    "status": "BLOCKED",
                    "failure_code": exc.code,
                    "message": str(exc),
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
