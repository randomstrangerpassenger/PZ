#!/usr/bin/env python
"""Run Round 3 contract test classes through unittest."""

from __future__ import annotations

import argparse
import ast
import importlib.abc
import json
import subprocess
import sys
import time
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
ROUND_DIR = REPO / "Iris" / "_docs" / "round3"
TEST_ROOT = REPO / "Iris" / "build" / "description" / "v2" / "tests"
V2_ROOT = REPO / "Iris" / "build" / "description" / "v2"
DEFAULT_TAXONOMY = ROUND_DIR / "round3_test_taxonomy.json"
DEFAULT_CLOSURE = ROUND_DIR / "round3_active_core_closure.json"
DEFAULT_REQUIRED_VALIDATIONS = ROUND_DIR / "current_route_required_validations.json"
TOOLS_BUILD_ROOT = V2_ROOT / "tools" / "build"


class BuildClosureBlocker(importlib.abc.MetaPathFinder):
    def __init__(self, allowed_modules: set[str]) -> None:
        self.allowed_modules = allowed_modules

    def find_spec(self, fullname: str, path: object | None, target: object | None = None) -> object | None:
        prefix = "tools.build."
        if not fullname.startswith(prefix):
            return None
        module = fullname[len(prefix) :].split(".", 1)[0]
        if module and module not in self.allowed_modules:
            raise ImportError(f"Round 3 current closure blocks import of {fullname}")
        return None


def git_path_is_tracked(path: Path) -> bool:
    relative = path.resolve().relative_to(REPO.resolve()).as_posix()
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", relative],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def git_path_is_ignored(path: Path) -> bool:
    relative = path.resolve().relative_to(REPO.resolve()).as_posix()
    result = subprocess.run(
        ["git", "check-ignore", "-q", "--", relative],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def selected_test_module_paths(test_ids: list[str]) -> list[Path]:
    paths = []
    for test_id in test_ids:
        module = test_id.split(".", 1)[0]
        path = TEST_ROOT / f"{module}.py"
        if path not in paths:
            paths.append(path)
    return paths


def tools_build_module_path(module: str) -> Path:
    if module == "__init__":
        return TOOLS_BUILD_ROOT / "__init__.py"
    module_file = TOOLS_BUILD_ROOT / f"{module}.py"
    package_init = TOOLS_BUILD_ROOT / module / "__init__.py"
    if package_init.is_file():
        return package_init
    return module_file


def tools_build_import_candidates(path: Path) -> list[dict]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    literal_tools_path_added = "sys.path" in source and (
        "tools/build" in source.replace("\\", "/")
        or "TOOLS" in source
        or "TOOLS_ROOT" in source
    )
    rows = []
    for node in ast.walk(tree):
        names: list[tuple[str, str]] = []
        if isinstance(node, ast.Import):
            names.extend((alias.name, "import") for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "tools.build":
                names.extend(
                    (f"{node.module}.{alias.name}", "from_import")
                    for alias in node.names
                )
            else:
                names.append((node.module, "from_import"))
        for imported, syntax in names:
            module = None
            if imported == "tools.build":
                module = "__init__"
            elif imported.startswith("tools.build."):
                module = imported[len("tools.build.") :].split(".", 1)[0]
            elif "." not in imported:
                candidate = tools_build_module_path(imported)
                if candidate.is_file():
                    module = imported
            if module:
                rows.append(
                    {
                        "selected_test": path.relative_to(REPO).as_posix(),
                        "module": module,
                        "syntax": syntax,
                        "line": getattr(node, "lineno", None),
                        "resolved_path": tools_build_module_path(module).resolve(),
                        "literal_tools_sys_path_present": literal_tools_path_added,
                    }
                )
    return rows


def enforce_preimport_build_dependency_closure(
    test_ids: list[str], allowed_modules: set[str]
) -> dict:
    rows = []
    violations = []
    for test_path in selected_test_module_paths(test_ids):
        if not test_path.is_file():
            violations.append(
                {
                    "code": "selected_test_module_missing",
                    "selected_test": test_path.relative_to(REPO).as_posix(),
                }
            )
            continue
        for row in tools_build_import_candidates(test_path):
            target = row.pop("resolved_path")
            exists = target.is_file()
            tracked = exists and git_path_is_tracked(target)
            ignored = exists and git_path_is_ignored(target)
            allowed = row["module"] in allowed_modules
            observed = {
                **row,
                "resolved_path": target.relative_to(REPO).as_posix(),
                "exists": exists,
                "tracked": tracked,
                "ignored": ignored,
                "allowed_by_current_closure": allowed,
            }
            rows.append(observed)
            if not exists or not tracked or ignored or not allowed:
                violations.append(
                    {
                        "code": "unqualified_tools_build_import_bypass",
                        **observed,
                    }
                )
    if violations:
        first = violations[0]
        raise ImportError(
            "unqualified_tools_build_import_bypass: "
            f"selected_test={first.get('selected_test')} "
            f"resolved_target={first.get('resolved_path')}"
        )
    return {
        "status": "PASS",
        "selected_test_count": len(selected_test_module_paths(test_ids)),
        "tools_build_dependency_count": len(rows),
        "unqualified_tools_build_import_count": 0,
        "dependencies": rows,
        "preimport_enforced": True,
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_test_ids(taxonomy: dict, contract_class: str, include_non_ok: bool) -> list[str]:
    rows = []
    for row in taxonomy["rows"]:
        if contract_class != "all" and row["contract_class"] != contract_class:
            continue
        if not include_non_ok and row["state"] != "ok":
            continue
        rows.append(row["test_id"])
    return sorted(set(rows))


def current_required_validation_manifest(path: Path, contract_class: str) -> dict | None:
    if contract_class != "current":
        return None
    if not path.exists():
        raise ValueError(f"Current route required validation manifest is missing: {path}")
    manifest = load_json(path)
    if manifest.get("schema_version") != "round3-current-route-required-validations-v1":
        raise ValueError(f"Unsupported current route required validation schema in {path}")
    if manifest.get("required") is not True:
        raise ValueError(f"Current route required validation manifest is not marked required: {path}")
    if not required_test_ids(manifest):
        raise ValueError(f"Current route required validation manifest has no required tests: {path}")
    return manifest


def required_test_ids(manifest: dict | None) -> list[str]:
    if not manifest:
        return []
    rows = manifest.get("required_tests", [])
    return sorted({str(row["test_id"]) for row in rows if row.get("test_id")})


def combined_test_ids(taxonomy_ids: list[str], manifest: dict | None) -> list[str]:
    return sorted(set(taxonomy_ids).union(required_test_ids(manifest)))


def object_field(payload: object, field_path: str) -> object:
    current = payload
    for part in field_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        return None
    return current


def artifact_check_errors(manifest: dict | None) -> list[dict]:
    if not manifest:
        return []
    errors: list[dict] = []
    for row in manifest.get("required_artifacts", []):
        artifact_path = REPO / row["path"]
        if not artifact_path.exists():
            errors.append({"code": "missing_required_artifact", "path": row["path"]})
            continue
        if not row.get("checks"):
            continue
        try:
            payload = load_json(artifact_path)
        except json.JSONDecodeError as exc:
            errors.append({"code": "invalid_required_artifact_json", "path": row["path"], "error": str(exc)})
            continue
        for check in row.get("checks", []):
            observed = object_field(payload, str(check["field"]))
            if "equals" in check and observed != check["equals"]:
                errors.append(
                    {
                        "code": "required_artifact_field_mismatch",
                        "path": row["path"],
                        "field": check["field"],
                        "expected": check["equals"],
                        "observed": observed,
                    }
                )
            if "one_of" in check and observed not in check["one_of"]:
                errors.append(
                    {
                        "code": "required_artifact_field_not_allowed",
                        "path": row["path"],
                        "field": check["field"],
                        "expected_one_of": check["one_of"],
                        "observed": observed,
                    }
                )
    return errors


def required_validation_payload(
    *,
    manifest: dict | None,
    selected_ids: list[str],
    result: unittest.TestResult,
) -> dict:
    if not manifest:
        return {
            "required": False,
            "success": True,
            "required_test_count": 0,
            "required_artifact_count": 0,
            "errors": [],
        }

    required_ids = required_test_ids(manifest)
    selected = set(selected_ids)
    missing = [test_id for test_id in required_ids if test_id not in selected]
    skipped = [
        test.id()
        for test, _reason in result.skipped
        if hasattr(test, "id") and test.id() in set(required_ids)
    ]
    failed = [
        test.id()
        for test, _traceback in [*result.errors, *result.failures]
        if hasattr(test, "id") and test.id() in set(required_ids)
    ]
    errors: list[dict] = []
    errors.extend({"code": "missing_required_test", "test_id": test_id} for test_id in missing)
    errors.extend({"code": "skipped_required_test", "test_id": test_id} for test_id in skipped)
    errors.extend({"code": "failed_required_test", "test_id": test_id} for test_id in failed)
    errors.extend(artifact_check_errors(manifest))
    return {
        "required": True,
        "manifest_path": str(DEFAULT_REQUIRED_VALIDATIONS.relative_to(REPO)),
        "success": not errors,
        "required_test_count": len(required_ids),
        "required_artifact_count": len(manifest.get("required_artifacts", [])),
        "required_tests": required_ids,
        "errors": errors,
    }


def run_suite(test_ids: list[str], verbosity: int) -> tuple[unittest.TestResult, float]:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for test_id in test_ids:
        suite.addTests(loader.loadTestsFromName(test_id))
    started = time.monotonic()
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    return result, time.monotonic() - started


def result_payload(
    *,
    contract_class: str,
    test_ids: list[str],
    result: unittest.TestResult,
    elapsed_seconds: float,
    closure_enforced: bool,
    required_validations: dict,
) -> dict:
    return {
        "schema_version": "round3-contract-test-run-v1",
        "contract_class": contract_class,
        "closure_enforced": closure_enforced,
        "test_count": result.testsRun,
        "selected_identity_count": len(test_ids),
        "success": result.wasSuccessful(),
        "errors": [
            {"test_id": str(test), "traceback": traceback}
            for test, traceback in result.errors
        ],
        "failures": [
            {"test_id": str(test), "traceback": traceback}
            for test, traceback in result.failures
        ],
        "skipped": [
            {"test_id": str(test), "reason": reason}
            for test, reason in result.skipped
        ],
        "required_validations": required_validations,
        "elapsed_seconds": round(elapsed_seconds, 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--class",
        dest="contract_class",
        choices=["current", "historical", "diagnostic", "all"],
        default="current",
    )
    parser.add_argument("--taxonomy", default=str(DEFAULT_TAXONOMY))
    parser.add_argument("--closure", default=str(DEFAULT_CLOSURE))
    parser.add_argument("--required-validations", default=str(DEFAULT_REQUIRED_VALIDATIONS))
    parser.add_argument("--include-non-ok", action="store_true")
    parser.add_argument("--enforce-current-build-closure", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--out")
    parser.add_argument("-v", "--verbosity", type=int, default=1)
    args = parser.parse_args()

    taxonomy = load_json(Path(args.taxonomy))
    try:
        required_manifest = current_required_validation_manifest(Path(args.required_validations), args.contract_class)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    taxonomy_test_ids = selected_test_ids(taxonomy, args.contract_class, args.include_non_ok)
    test_ids = combined_test_ids(taxonomy_test_ids, required_manifest)
    if args.list:
        for test_id in test_ids:
            print(test_id)
        return 0

    if not test_ids:
        print(f"No tests selected for contract class {args.contract_class}", file=sys.stderr)
        return 2

    sys.path.insert(0, str(TEST_ROOT))
    sys.path.insert(0, str(V2_ROOT))

    closure_enforced = False
    if args.enforce_current_build_closure:
        if args.contract_class != "current":
            print("--enforce-current-build-closure is only valid for --class current", file=sys.stderr)
            return 2
        closure = load_json(Path(args.closure))
        allowed = set(closure["current_closure_modules"])
        allowed.update(closure.get("current_route_allowed_tooling_modules", []))
        try:
            enforce_preimport_build_dependency_closure(test_ids, allowed)
        except (ImportError, OSError, SyntaxError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        sys.meta_path.insert(0, BuildClosureBlocker(allowed))
        closure_enforced = True

    result, elapsed = run_suite(test_ids, args.verbosity)
    required_payload = required_validation_payload(
        manifest=required_manifest,
        selected_ids=test_ids,
        result=result,
    )
    payload = result_payload(
        contract_class=args.contract_class,
        test_ids=test_ids,
        result=result,
        elapsed_seconds=elapsed,
        closure_enforced=closure_enforced,
        required_validations=required_payload,
    )
    success = result.wasSuccessful() and required_payload["success"]
    payload["success"] = success
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ["contract_class", "closure_enforced", "test_count", "success", "elapsed_seconds"]}, ensure_ascii=False))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
