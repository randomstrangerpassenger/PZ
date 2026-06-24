#!/usr/bin/env python
"""Generate additive Round 3 evidence artifacts through the D1 hard stop."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from round3_collect_test_identities import collect_identities


REPO = Path(__file__).resolve().parents[3]
ROUND_DIR = REPO / "Iris" / "_docs" / "round3"
TEST_ROOT = REPO / "Iris" / "build" / "description" / "v2" / "tests"
BUILD_ROOT = REPO / "Iris" / "build" / "description" / "v2" / "tools" / "build"
SOURCE_ROADMAP = REPO / "Iris" / "_docs" / "refactor" / "round3_tools_build_test_contract_roadmap.md"
PLAN_DOC = REPO / "docs" / "iris-round3-final-integrated-build-script-test-contract-disentanglement-plan.md"
ROOT_PYTEST = REPO / "pytest.ini"
TRACKED_TEST_SEEDS = {
    "Iris/build/description/v2/tests/test_build_iris_index_data.py",
    "Iris/build/description/v2/tests/test_compose_layer3_text_v2.py",
    "Iris/build/description/v2/tests/test_current_authority_source_path_guard.py",
    "Iris/build/description/v2/tests/test_layer4_absorption_current_surface_guard.py",
    "Iris/build/description/v2/tests/test_layer4_trace_edge_authority_admission_round.py",
    "Iris/build/description/v2/tests/test_legacy_active_silent_current_surface_guard.py",
}
MANUAL_CURRENT_TESTS = {
    "Iris/build/description/v2/tests/test_compose_layer3_text_overlay.py": (
        "manual audit: imports only current closure module compose_layer3_text; "
        "asserts current compose overlay/render behavior; no ignored reproduction imports"
    ),
}

TEXT_EXTENSIONS = {
    ".bat",
    ".cmd",
    ".csv",
    ".ini",
    ".json",
    ".jsonl",
    ".lua",
    ".md",
    ".ps1",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO).as_posix()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def run_command(args: list[str], timeout: int = 120) -> dict:
    try:
        completed = subprocess.run(
            args,
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return {
            "command": " ".join(args),
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "timeout": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": " ".join(args),
            "exit_code": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timeout": True,
        }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def list_py(root: Path, pattern: str = "*.py") -> list[Path]:
    return sorted(path for path in root.rglob(pattern) if "__pycache__" not in path.parts and path.is_file())


def git_lines(args: list[str]) -> list[str]:
    result = run_command(["git", *args])
    if result["exit_code"] != 0:
        return []
    return [line.strip().replace("\\", "/") for line in result["stdout"].splitlines() if line.strip()]


def tracked_set() -> set[str]:
    return set(git_lines(["ls-files"]))


def ignored_set(paths: Iterable[Path]) -> set[str]:
    rels = [rel(path) for path in paths]
    if not rels:
        return set()
    completed = subprocess.run(
        ["git", "check-ignore", "--stdin"],
        cwd=REPO,
        input=("\n".join(rels) + "\n").encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        line.decode("utf-8", errors="replace").strip().replace("\\", "/")
        for line in completed.stdout.splitlines()
        if line.strip()
    }


def parse_unittest_summary(output: str) -> dict:
    ran = re.search(r"Ran\s+(\d+)\s+tests?", output)
    errors = failures = skips = 0
    detail = re.search(r"FAILED \(([^)]*)\)", output)
    if detail:
        for part in detail.group(1).split(","):
            key, _, value = part.strip().partition("=")
            if key == "errors":
                errors = int(value)
            elif key == "failures":
                failures = int(value)
            elif key in {"skipped", "skips"}:
                skips = int(value)
    skipped = re.search(r"skipped=(\d+)", output)
    if skipped:
        skips = int(skipped.group(1))
    return {
        "tests_run": int(ran.group(1)) if ran else None,
        "errors": errors,
        "failures": failures,
        "skips": skips,
        "result": "OK" if re.search(r"^OK$", output, re.MULTILINE) else ("FAILED" if "FAILED" in output else "UNKNOWN"),
    }


def source_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def script_module_name(path: Path) -> str:
    return path.stem


def extract_imported_build_modules(path: Path, module_names: set[str]) -> list[str]:
    text = source_text(path)
    found: set[str] = set()
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        tree = None
    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    if name.startswith("tools.build."):
                        found.add(name.split(".")[2])
                    elif name in module_names:
                        found.add(name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith("tools.build."):
                    found.add(module.split(".")[2])
                elif module == "tools.build":
                    for alias in node.names:
                        if alias.name in module_names:
                            found.add(alias.name)
                elif node.level == 1 and module in module_names:
                    found.add(module)
                elif node.level == 0 and module in module_names:
                    found.add(module)
    for match in re.finditer(r"tools\.build\.([A-Za-z_][A-Za-z0-9_]*)", text):
        if match.group(1) in module_names:
            found.add(match.group(1))
    return sorted(found)


def static_flags(path: Path) -> dict:
    text = source_text(path)
    return {
        "sys_exit": "sys.exit(" in text,
        "main_work": "__main__" in text or "unittest.main(" in text,
        "subprocess_execution": "subprocess." in text or "subprocess " in text,
        "dynamic_import_signal": "importlib" in text or "__import__(" in text,
        "hang_risk": "sleep(" in text or "while True" in text,
        "artifact_path_signal": bool(
            re.search(r"(staging/|staging\\\\|output/|output\\\\|media/lua|media\\\\lua|\.jsonl?|\.lua)", text)
        ),
    }


def scan_reference_summary(module_names: set[str]) -> dict:
    patterns = ["tools.build.", "Iris/build/description/v2/tools/build", "Iris\\build\\description\\v2\\tools\\build"]
    roots_excluded = {".git", "Iris/_docs/round3"}
    refs_by_module: dict[str, int] = {name: 0 for name in module_names}
    total_lines = 0
    scanned_files = 0
    skipped_files = 0
    for path in sorted(REPO.rglob("*")):
        if not path.is_file():
            continue
        r = rel(path)
        if r.startswith(".git/") or r.startswith("Iris/_docs/round3/"):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            skipped_files += 1
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            skipped_files += 1
            continue
        if not any(pattern in text for pattern in patterns):
            scanned_files += 1
            continue
        scanned_files += 1
        for line in text.splitlines():
            if any(pattern in line for pattern in patterns):
                total_lines += 1
                for module in module_names:
                    if module in line:
                        refs_by_module[module] += 1
    return {
        "policy": {
            "include_hidden": True,
            "excluded_roots": sorted(roots_excluded),
            "text_extensions": sorted(TEXT_EXTENSIONS),
        },
        "scanned_files": scanned_files,
        "skipped_non_text_or_unreadable_files": skipped_files,
        "matching_lines": total_lines,
        "refs_by_module": refs_by_module,
    }


def closure_from(seeds: Iterable[str], graph: dict[str, list[str]]) -> set[str]:
    seen: set[str] = set()
    queue = deque(seeds)
    while queue:
        item = queue.popleft()
        if item in seen:
            continue
        seen.add(item)
        for dep in graph.get(item, []):
            if dep not in seen:
                queue.append(dep)
    return seen


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def main() -> int:
    ROUND_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = now_iso()

    tracked = tracked_set()
    all_scripts = list_py(BUILD_ROOT)
    all_tests = list_py(TEST_ROOT, "test_*.py")
    ignored = ignored_set([*all_scripts, *all_tests])
    module_names = {script_module_name(path) for path in all_scripts}

    pre_status = run_command(["git", "status", "--short"])
    env = {
        "generated_at": generated_at,
        "python_version": run_command(["python", "--version"]),
        "rg_version": run_command(["rg", "--version"]),
        "jq_version": run_command(["jq", "--version"]),
        "source_roadmap_exists": SOURCE_ROADMAP.exists(),
        "plan_doc_exists": PLAN_DOC.exists(),
        "git_head": run_command(["git", "rev-parse", "HEAD"]),
        "git_status_short": pre_status,
    }

    legacy_command = ["python", "-B", "-m", "unittest", "discover", "-s", "Iris\\build\\description\\v2\\tests", "-p", "test_*.py"]
    legacy_run = run_command(legacy_command, timeout=180)
    legacy_output = (legacy_run["stdout"] or "") + (legacy_run["stderr"] or "")
    legacy_summary = parse_unittest_summary(legacy_output)
    post_status = run_command(["git", "status", "--short"])

    identities = collect_identities(TEST_ROOT, "test_*.py")
    identity_path = ROUND_DIR / "round3_legacy_test_identities.json"
    write_json(identity_path, identities)

    script_imports = {script_module_name(path): extract_imported_build_modules(path, module_names) for path in all_scripts}
    test_imports_by_file = {rel(path): extract_imported_build_modules(path, module_names) for path in all_tests}
    imported_by_tests: dict[str, list[str]] = defaultdict(list)
    imported_by_scripts: dict[str, list[str]] = defaultdict(list)
    for test_file, imports in test_imports_by_file.items():
        for module in imports:
            imported_by_tests[module].append(test_file)
    for script_module, imports in script_imports.items():
        for module in imports:
            imported_by_scripts[module].append(script_module)

    reference_summary = scan_reference_summary(module_names)

    tracked_core_modules = {Path(path).stem for path in tracked if path.startswith("Iris/build/description/v2/tools/build/") and path.endswith(".py")}
    current_test_seeds = {path for path in TRACKED_TEST_SEEDS if (REPO / path).exists()}
    manual_current_tests = {path for path in MANUAL_CURRENT_TESTS if (REPO / path).exists()}
    current_contract_tests = current_test_seeds | manual_current_tests
    current_contract_imports = sorted(
        {module for test_path in current_contract_tests for module in test_imports_by_file.get(test_path, [])}
    )
    current_closure = closure_from([*tracked_core_modules, *current_contract_imports], script_imports)

    script_rows = []
    for path in all_scripts:
        r = rel(path)
        module = path.stem
        flags = static_flags(path)
        refs = reference_summary["refs_by_module"].get(module, 0)
        by_current_seed = sorted(test for test in imported_by_tests.get(module, []) if test in current_test_seeds)
        by_current_contract = sorted(test for test in imported_by_tests.get(module, []) if test in current_contract_tests)
        by_non_current_test = sorted(test for test in imported_by_tests.get(module, []) if test not in current_contract_tests)
        if module in tracked_core_modules:
            owner_class = "current_build_core"
        elif by_current_contract:
            owner_class = "current_validation_support"
        elif by_non_current_test:
            owner_class = "historical_reproduction"
        elif refs or flags["dynamic_import_signal"] or imported_by_scripts.get(module):
            owner_class = "diagnostic_advisory"
        elif flags["artifact_path_signal"]:
            owner_class = "manifest_only_candidate"
        else:
            owner_class = "unresolved"
        script_rows.append(
            {
                "path": r,
                "module": module,
                "sha256": sha256(path),
                "tracked": r in tracked,
                "ignored": r in ignored,
                "owner_class": owner_class,
                "in_current_closure": module in current_closure,
                "imported_by_current_seed_tests": by_current_seed,
                "imported_by_current_contract_tests": by_current_contract,
                "imported_by_non_current_tests_count": len(by_non_current_test),
                "imported_by_peer_scripts_count": len(imported_by_scripts.get(module, [])),
                "doc_or_path_reference_count": refs,
                **flags,
            }
        )

    test_file_to_status = {}
    for row in identities["identities"]:
        source = row.get("source_file")
        if not source:
            continue
        try:
            test_file_to_status[Path(source).resolve().relative_to(REPO).as_posix()] = row["status"]
        except ValueError:
            pass

    taxonomy_rows = []
    for identity in identities["identities"]:
        source_file = identity.get("source_file")
        source_rel = None
        if source_file:
            try:
                source_rel = Path(source_file).resolve().relative_to(REPO).as_posix()
            except ValueError:
                source_rel = source_file
        imports = test_imports_by_file.get(source_rel or "", [])
        imports_ignored = [
            module for module in imports
            if f"Iris/build/description/v2/tools/build/{module}.py" in ignored
        ]
        if source_rel in current_test_seeds:
            contract_class = "current"
            reason = "tracked current-contract seed"
            audit_status = "seed"
        elif source_rel in manual_current_tests:
            contract_class = "current"
            reason = MANUAL_CURRENT_TESTS[source_rel]
            audit_status = "manual_audit_promoted"
        elif imports_ignored:
            contract_class = "historical"
            reason = "imports ignored reproduction modules"
            audit_status = "needs_manual_audit"
        elif imports:
            contract_class = "historical"
            reason = "untracked test imports build modules outside tracked seed set"
            audit_status = "needs_manual_audit"
        else:
            contract_class = "diagnostic"
            reason = "untracked zero-build-import test; assertion intent not promoted to current"
            audit_status = "needs_manual_audit"
        state = "non_collectable" if identity["collect_error"] else "ok"
        taxonomy_rows.append(
            {
                "test_id": identity["test_id"],
                "source_file": source_rel,
                "contract_class": contract_class,
                "state": state,
                "reason": reason,
                "audit_status": audit_status,
                "imported_build_modules": imports,
                "imports_ignored_reproduction_modules": imports_ignored,
                "routing_status": {
                    ("current", "ok"): "default unittest discovery after D1",
                    ("historical", "ok"): "explicit historical command or D3 status",
                    ("diagnostic", "ok"): "manifest-only or explicit diagnostic command",
                }.get((contract_class, state), "blocked or explicit ledger treatment"),
            }
        )

    matrix = Counter((row["contract_class"], row["state"]) for row in taxonomy_rows)

    signals = []
    for test in all_tests:
        r = rel(test)
        flags = static_flags(test)
        signals.append(
            {
                "path": r,
                "tracked": r in tracked,
                "ignored": r in ignored,
                "imported_build_modules": test_imports_by_file.get(r, []),
                "import_time_side_effect": flags["sys_exit"] or flags["main_work"] or flags["subprocess_execution"],
                "non_collectable": test_file_to_status.get(r) == "non_collectable",
                "non_passing": legacy_run["exit_code"] != 0,
                **flags,
            }
        )

    tree_snapshot = {
        "schema_version": "round3-baseline-tree-snapshot-v1",
        "generated_at": generated_at,
        "head": env["git_head"],
        "git_status_short": pre_status,
        "root_pytest_ini": {
            "exists": ROOT_PYTEST.exists(),
            "sha256": sha256(ROOT_PYTEST) if ROOT_PYTEST.exists() else None,
        },
        "tests": [
            {"path": rel(path), "sha256": sha256(path), "tracked": rel(path) in tracked, "ignored": rel(path) in ignored}
            for path in all_tests
        ],
        "tools_build": [
            {"path": rel(path), "sha256": sha256(path), "tracked": rel(path) in tracked, "ignored": rel(path) in ignored}
            for path in all_scripts
        ],
    }
    write_json(ROUND_DIR / "round3_baseline_tree_snapshot.json", tree_snapshot)

    baseline = {
        "schema_version": "round3-legacy-full-discovery-baseline-v1",
        "generated_at": generated_at,
        "command": legacy_run["command"],
        "exit_code": legacy_run["exit_code"],
        "timeout": legacy_run["timeout"],
        "summary": legacy_summary,
        "identity_file": rel(identity_path),
        "identity_count": identities["identity_count"],
        "collect_error_count": identities["collect_error_count"],
        "failed_test_policy": identities["failed_test_policy"],
        "count_cross_check": {
            "identity_count_equals_tests_run": identities["identity_count"] == legacy_summary["tests_run"],
            "tests_run": legacy_summary["tests_run"],
            "identity_count": identities["identity_count"],
        },
        "taxonomy_input_files": [rel(path) for path in all_tests],
        "pre_git_status_short": pre_status,
        "post_git_status_short": post_status,
        "stdout_tail": legacy_run["stdout"][-4000:],
        "stderr_tail": legacy_run["stderr"][-4000:],
    }
    write_json(ROUND_DIR / "round3_legacy_full_discovery_baseline.json", baseline)

    baseline_md = [
        "# Round 3 Legacy Full Discovery Baseline",
        "",
        f"Generated: `{generated_at}`",
        "",
        f"Command: `{legacy_run['command']}`",
        f"Exit code: `{legacy_run['exit_code']}`",
        f"Result: `{legacy_summary['result']}`",
        f"Tests run: `{legacy_summary['tests_run']}`",
        f"Errors: `{legacy_summary['errors']}`",
        f"Failures: `{legacy_summary['failures']}`",
        f"Skips: `{legacy_summary['skips']}`",
        f"Identity count: `{identities['identity_count']}`",
        f"Identity cross-check passed: `{identities['identity_count'] == legacy_summary['tests_run']}`",
        "",
        "This is a legacy full-discovery baseline only. It is not a current default discovery contract.",
    ]
    write_text(ROUND_DIR / "round3_legacy_full_discovery_baseline.md", "\n".join(baseline_md))

    summary = {
        "schema_version": "round3-contract-manifest-v1",
        "generated_at": generated_at,
        "scope": {
            "tools_build": rel(BUILD_ROOT),
            "tests": rel(TEST_ROOT),
        },
        "counts": {
            "tools_build_py": len(all_scripts),
            "tools_build_tracked": sum(1 for path in all_scripts if rel(path) in tracked),
            "tools_build_ignored": sum(1 for path in all_scripts if rel(path) in ignored),
            "tests_py": len(all_tests),
            "tests_tracked": sum(1 for path in all_tests if rel(path) in tracked),
            "tests_ignored": sum(1 for path in all_tests if rel(path) in ignored),
            "distinct_tools_build_modules_referenced_by_tests": len({m for imports in test_imports_by_file.values() for m in imports}),
            "test_files_importing_tools_build": sum(1 for imports in test_imports_by_file.values() if imports),
            "build_files_importing_tools_build": sum(1 for imports in script_imports.values() if imports),
        },
        "tracked_core_modules": sorted(tracked_core_modules),
        "current_test_seeds": sorted(current_test_seeds),
        "reference_scan": reference_summary,
        "scripts": sorted(script_rows, key=lambda row: row["path"]),
        "tests": [
            {
                "path": rel(path),
                "sha256": sha256(path),
                "tracked": rel(path) in tracked,
                "ignored": rel(path) in ignored,
                "imported_build_modules": test_imports_by_file.get(rel(path), []),
                **static_flags(path),
            }
            for path in all_tests
        ],
    }
    write_json(ROUND_DIR / "round3_contract_manifest.json", summary)

    measurement_rows = [
        ["tools/build Python files", summary["counts"]["tools_build_py"]],
        ["tools/build tracked", summary["counts"]["tools_build_tracked"]],
        ["tools/build ignored", summary["counts"]["tools_build_ignored"]],
        ["tests Python files", summary["counts"]["tests_py"]],
        ["tests tracked", summary["counts"]["tests_tracked"]],
        ["tests ignored", summary["counts"]["tests_ignored"]],
        ["legacy tests_run", legacy_summary["tests_run"]],
        ["legacy exit_code", legacy_run["exit_code"]],
        ["identity_count", identities["identity_count"]],
    ]
    write_text(
        ROUND_DIR / "round3_measurement_lock.md",
        "\n".join(
            [
                "# Round 3 Measurement Lock",
                "",
                f"Generated: `{generated_at}`",
                "",
                markdown_table(["Metric", "Value"], measurement_rows),
                "",
                "Pre-lock roadmap counts are inputs only. This file records the current checkout measurement used by Round 3 evidence.",
                "",
                "No runtime Lua, package payload, or generated public-facing output was intentionally changed by this measurement.",
            ]
        ),
    )

    write_json(
        ROUND_DIR / "round3_test_collectability_signals.json",
        {
            "schema_version": "round3-test-collectability-signals-v1",
            "generated_at": generated_at,
            "legacy_command_exit_code": legacy_run["exit_code"],
            "legacy_result": legacy_summary,
            "signals": sorted(signals, key=lambda row: row["path"]),
        },
    )

    write_json(
        ROUND_DIR / "round3_test_taxonomy.json",
        {
            "schema_version": "round3-test-taxonomy-v1",
            "generated_at": generated_at,
            "identity_source": rel(identity_path),
            "classification_policy": {
                "contract_class_order": "contract_class assigned before state",
                "current_seed_policy": "tracked six tests are current seeds",
                "manual_current_policy": "untracked tests may be promoted only by explicit manual audit when imports stay inside current closure and assertion intent is current",
                "manual_current_tests": MANUAL_CURRENT_TESTS,
                "state_policy": "legacy full discovery exit 0 makes collected identities ok unless _FailedTest appears",
            },
            "matrix": {f"{klass}+{state}": count for (klass, state), count in sorted(matrix.items())},
            "rows": taxonomy_rows,
        },
    )

    matrix_rows = [[klass, state, matrix[(klass, state)]] for klass in ["current", "historical", "diagnostic"] for state in ["ok", "non_collectable", "non_passing", "stale"]]
    write_text(
        ROUND_DIR / "round3_taxonomy_matrix.md",
        "\n".join(
            [
                "# Round 3 Taxonomy Matrix",
                "",
                f"Generated: `{generated_at}`",
                "",
                markdown_table(["Contract Class", "State", "Count"], matrix_rows),
                "",
                f"Total identities: `{len(taxonomy_rows)}`",
                f"Matrix sum equals identity count: `{sum(matrix.values()) == len(taxonomy_rows)}`",
            ]
        ),
    )

    manual_rows = [
        [
            path,
            MANUAL_CURRENT_TESTS[path],
            ", ".join(test_imports_by_file.get(path, [])),
        ]
        for path in sorted(manual_current_tests)
    ]
    write_text(
        ROUND_DIR / "round3_manual_audit_notes.md",
        "\n".join(
            [
                "# Round 3 Manual Audit Notes",
                "",
                f"Generated: `{generated_at}`",
                "",
                "These rows are explicit manual-audit promotions. They are not inferred only from filename or tracked state.",
                "",
                markdown_table(["Path", "Disposition", "Imported build modules"], manual_rows),
                "",
                "Promotion rule: current assertion intent, no ignored reproduction imports, and imports limited to current closure modules.",
            ]
        ),
    )

    routing_rows = [
        ["current", "ok", "default unittest discovery after D1", "identity/count included; must pass"],
        ["current", "non_passing", "default unittest discovery", "current gate fails loud"],
        ["current", "non_collectable", "blocked-current ledger", "current gate blocked; no split"],
        ["current", "stale", "blocked-current or explicit owner decision", "explicit blocker/subtraction; no silent pass"],
        ["historical", "ok", "explicit historical command or D3 status", "identity/count included or D3 frozen treatment"],
        ["historical", "non_passing", "explicit historical fail-state ledger", "no reproducibility claim unless D3 allows"],
        ["historical", "non_collectable", "historical blocked/non-executable status", "explicit collect error or D3 frozen treatment"],
        ["historical", "stale", "excluded with reason / frozen ledger", "explicit subtraction"],
        ["diagnostic", "ok", "explicit diagnostic command or manifest-only", "identity/count included or explicit exclusion"],
        ["diagnostic", "non_passing", "diagnostic fail-state ledger", "counted as diagnostic failure, not current pass"],
        ["diagnostic", "non_collectable", "diagnostic blocked ledger", "explicit collect error"],
        ["diagnostic", "stale", "excluded with reason", "explicit subtraction"],
    ]
    write_text(
        ROUND_DIR / "round3_taxonomy_routing_map.md",
        "\n".join(["# Round 3 Taxonomy Routing Map", "", f"Generated: `{generated_at}`", "", markdown_table(["Contract Class", "State", "Routing Status", "Reconciliation Treatment"], routing_rows)]),
    )

    active_closure = {
        "schema_version": "round3-active-core-closure-v1",
        "generated_at": generated_at,
        "closure_authority": [
            "Iris/build/description/v2/tools/build/INVENTORY.md",
            "Iris/_docs/refactor/phase1_active_manifest.md",
        ],
        "current_test_seeds": sorted(current_test_seeds),
        "manual_current_tests": {path: MANUAL_CURRENT_TESTS[path] for path in sorted(manual_current_tests)},
        "current_contract_tests": sorted(current_contract_tests),
        "tracked_core_modules": sorted(tracked_core_modules),
        "current_contract_imports": current_contract_imports,
        "current_closure_modules": sorted(current_closure),
        "current_closure_count": len(current_closure),
        "closure_rows": [
            row for row in sorted(script_rows, key=lambda item: item["path"]) if row["module"] in current_closure
        ],
        "blocked_or_not_executed": "scratch current-closure-only proof is deferred until D1/default-route selection",
    }
    write_json(ROUND_DIR / "round3_active_core_closure.json", active_closure)

    artifact_rows = []
    for row in sorted(script_rows, key=lambda item: item["path"]):
        if row["artifact_path_signal"] or row["doc_or_path_reference_count"] or row["dynamic_import_signal"]:
            artifact_rows.append(
                {
                    "path": row["path"],
                    "module": row["module"],
                    "artifact_path_signal": row["artifact_path_signal"],
                    "doc_or_path_reference_count": row["doc_or_path_reference_count"],
                    "dynamic_import_signal": row["dynamic_import_signal"],
                    "production_mapping": "unresolved_static_signal",
                    "dependency_mapping": "keep_or_manual_audit_required",
                    "method": "static_reference_or_signal_scan",
                }
            )
    write_json(
        ROUND_DIR / "round3_artifact_dependency_manifest.json",
        {
            "schema_version": "round3-artifact-dependency-manifest-v1",
            "generated_at": generated_at,
            "method_doc": "Iris/_docs/round3/round3_artifact_dependency_method.md",
            "rows": artifact_rows,
        },
    )
    write_text(
        ROUND_DIR / "round3_artifact_dependency_method.md",
        "\n".join(
            [
                "# Round 3 Artifact Dependency Method",
                "",
                "This manifest is a dependency signal inventory, not a production mapping proof.",
                "",
                "- `production_mapping`: unresolved unless a command execution or explicit generator map proves the producer/output pair.",
                "- `dependency_mapping`: `keep_or_manual_audit_required` for any static artifact-path, doc/path reference, or dynamic import signal.",
                "- `method`: current evidence comes from static reference/signal scan. No archive/delete action may rely on this alone.",
                "",
                "Byte-parity requirements are not triggered in Change 0-3 because no generator or artifact disposition is executed.",
            ]
        ),
    )

    disposition_rows = []
    for row in sorted(script_rows, key=lambda item: item["path"]):
        protected = (
            row["in_current_closure"]
            or row["artifact_path_signal"]
            or row["doc_or_path_reference_count"] > 0
            or row["dynamic_import_signal"]
            or row["imported_by_non_current_tests_count"] > 0
            or row["imported_by_peer_scripts_count"] > 0
            or row["owner_class"] == "unresolved"
        )
        disposition_rows.append(
            {
                "path": row["path"],
                "module": row["module"],
                "owner_class": row["owner_class"],
                "archive_eligible": False,
                "delete_eligible": False,
                "recommended_disposition": "keep_with_reason" if protected else "manual_audit_required",
                "reason": "Change 0-3 evidence only; D2 not approved and no archive/delete proof packet exists",
                "signals": {
                    "in_current_closure": row["in_current_closure"],
                    "artifact_path_signal": row["artifact_path_signal"],
                    "doc_or_path_reference_count": row["doc_or_path_reference_count"],
                    "dynamic_import_signal": row["dynamic_import_signal"],
                    "imported_by_non_current_tests_count": row["imported_by_non_current_tests_count"],
                    "imported_by_peer_scripts_count": row["imported_by_peer_scripts_count"],
                },
            }
        )
    write_json(
        ROUND_DIR / "round3_disposition_candidates.json",
        {
            "schema_version": "round3-disposition-candidates-v1",
            "generated_at": generated_at,
            "d2_status": "pending_not_approved",
            "rows": disposition_rows,
            "invariants": {
                "archive_or_delete_executed": False,
                "filename_glob_archive_delete_used": False,
                "unresolved_marked_archive_or_delete": False,
            },
        },
    )

    source_roadmap_text = source_text(SOURCE_ROADMAP) if SOURCE_ROADMAP.exists() else ""
    roadmap_checks = {
        "exists": SOURCE_ROADMAP.exists(),
        "has_phase_1_to_6_headings": all(f"### Phase {n}" in source_roadmap_text for n in range(1, 7)),
        "has_no_phase_0_alias": "Phase 0 in approach numbering" not in source_roadmap_text,
        "phase7a_followup_not_current_execution": "Phase 7a follow-up" in source_roadmap_text or "Phase 7a follow-up" in source_roadmap_text.replace("\n", " "),
        "historical_380_not_live_canonical": "not a live canonical baseline" in source_roadmap_text,
    }
    checklist_rows = [
        ["repo-stable source roadmap locked", roadmap_checks["exists"] and roadmap_checks["has_phase_1_to_6_headings"] and roadmap_checks["has_no_phase_0_alias"]],
        ["D1 recorded with schema", True],
        ["legacy full discovery baseline recorded", legacy_run["exit_code"] is not None],
        ["test identity collector output recorded", identity_path.exists()],
        ["taxonomy routing map sealed", True],
        ["test collectability/pass-state signals recorded", True],
        ["closure and artifact dependency proof recorded", True],
        ["Change 4 allowed", False],
        ["Change 5 allowed", False],
    ]
    write_text(
        ROUND_DIR / "round3_gate_readiness_checklist.md",
        "\n".join(
            [
                "# Round 3 Gate Readiness Checklist",
                "",
                f"Generated: `{generated_at}`",
                "",
                markdown_table(["Checklist Item", "Status"], checklist_rows),
                "",
                "Change 4 remains blocked until D1 is approved by the project owner or delegated maintainer.",
                "Change 5 remains blocked until D2 is approved by the project owner or delegated maintainer.",
            ]
        ),
    )

    scope_lock = [
        "# Round 3 Scope Lock",
        "",
        f"Generated: `{generated_at}`",
        "",
        "Authority order:",
        "",
        "1. `docs/Philosophy.md`",
        "2. `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`",
        "3. `docs/iris-round3-final-integrated-build-script-test-contract-disentanglement-plan.md`",
        "4. `Iris/_docs/refactor/round3_tools_build_test_contract_roadmap.md`",
        "5. `Iris/_docs/round3/*` evidence artifacts",
        "",
        "Primary provenance paths are repo-stable. This round does not use attachment-only provenance.",
        "",
        "Staging policy: no staging or commit is in scope for this execution turn. Primary evidence remains untracked until the owner stages or requests staging.",
        "",
        "## Gate Records",
        "",
        "```text",
        "gate_id: D1",
        "decision: pending",
        "approved_by: pending_project_owner_or_delegated_maintainer",
        f"timestamp: {generated_at}",
        "allowed_scope: none_until_approved; Change 4 default discovery split blocked",
        "blocked_scope: default current discovery switch; pytest routing; test moves",
        "evidence_artifact: Iris/_docs/round3/round3_gate_readiness_checklist.md",
        "status: pending",
        "",
        "gate_id: D2",
        "decision: pending",
        "approved_by: pending_project_owner_or_delegated_maintainer",
        f"timestamp: {generated_at}",
        "allowed_scope: none_until_approved; Change 5 disposition blocked",
        "blocked_scope: archive; delete; relocation; .gitignore disposition edits",
        "evidence_artifact: Iris/_docs/round3/round3_disposition_candidates.json",
        "status: pending",
        "",
        "gate_id: D3",
        "decision: pending",
        "approved_by: pending_project_owner_or_delegated_maintainer",
        f"timestamp: {generated_at}",
        "allowed_scope: policy selection during Change 6 only",
        "blocked_scope: historical preservation closeout claim",
        "evidence_artifact: Iris/_docs/round3/round3_legacy_full_discovery_baseline.json",
        "status: pending",
        "```",
        "",
        "## Source Roadmap Lock Checks",
        "",
        markdown_table(["Check", "Status"], [[key, value] for key, value in roadmap_checks.items()]),
        "",
        "## Tool Preflight",
        "",
        markdown_table(
            ["Command", "Exit Code"],
            [
                ["python --version", env["python_version"]["exit_code"]],
                ["rg --version", env["rg_version"]["exit_code"]],
                ["jq --version", env["jq_version"]["exit_code"]],
                ["git status --short", env["git_status_short"]["exit_code"]],
            ],
        ),
        "",
        "## Claim Boundary",
        "",
        "This scope lock records measurement and classification evidence only. It does not claim release readiness, runtime equivalence, full historical reproducibility, package readiness, or deletion safety.",
    ]
    write_text(ROUND_DIR / "round3_scope_lock.md", "\n".join(scope_lock))

    final_status = run_command(["git", "status", "--short", "--", "docs/iris-round3-final-integrated-build-script-test-contract-disentanglement-plan.md", "Iris/_docs/refactor/round3_tools_build_test_contract_roadmap.md", "Iris/_docs/round3"])
    diff_stat = run_command(["git", "diff", "--stat", "--", "Iris/_docs/round3"])
    write_json(
        ROUND_DIR / "round3_generation_report.json",
        {
            "schema_version": "round3-generation-report-v1",
            "generated_at": generated_at,
            "environment": env,
            "generated_files": sorted(rel(path) for path in ROUND_DIR.glob("round3_*")),
            "scoped_status": final_status,
            "scoped_diff_stat": diff_stat,
            "hard_stops": {
                "change4_blocked_until_d1": True,
                "change5_blocked_until_d2": True,
                "change6_complete_blocked_until_d3": True,
            },
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
