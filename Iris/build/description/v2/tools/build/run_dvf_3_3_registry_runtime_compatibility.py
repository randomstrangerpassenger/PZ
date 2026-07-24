#!/usr/bin/env python3
"""Orchestrate evidence-producing DVF 3.3 Registry Compatibility phases."""

from __future__ import annotations

import argparse
import ast
import json
import shutil
import subprocess
import sys
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
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        list(command),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--seal-toolchain", action="store_true")
    modes.add_argument("--phase2", action="store_true")
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--attempt-id", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.seal_toolchain:
            return command_seal_toolchain(args)
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
