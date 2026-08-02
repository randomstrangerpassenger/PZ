#!/usr/bin/env python
"""Run Round 3 contract test classes through unittest."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.abc
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path, PurePosixPath


REPO = Path(__file__).resolve().parents[3]
ROUND_DIR = REPO / "Iris" / "_docs" / "round3"
TEST_ROOT = REPO / "Iris" / "build" / "description" / "v2" / "tests"
V2_ROOT = REPO / "Iris" / "build" / "description" / "v2"
DEFAULT_TAXONOMY = ROUND_DIR / "round3_test_taxonomy.json"
DEFAULT_CLOSURE = ROUND_DIR / "round3_active_core_closure.json"
DEFAULT_REQUIRED_VALIDATIONS = ROUND_DIR / "current_route_required_validations.json"
REQUIRED_VALIDATIONS_PROJECTION_ENV = (
    "IRIS_ROUND3_REQUIRED_VALIDATIONS_PROJECTION"
)
CLEAN_CHECKOUT_TEST_OUTPUT_ROOT_ENV = "IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT"
TOOLS_BUILD_ROOT = V2_ROOT / "tools" / "build"
HISTORICAL_REPRODUCTION_MANIFEST = (
    REPO
    / "Iris"
    / "_docs"
    / "refactor"
    / "core_refactor"
    / "historical_reproduction_corpus.json"
)
HISTORICAL_REPRODUCTION_ARCHIVE = (
    REPO
    / "Iris"
    / "_docs"
    / "refactor"
    / "core_refactor"
    / "historical_reproduction_corpus.zip"
)
PORTABLE_REPOSITORY_PATH = re.compile(r"^[A-Za-z0-9._/-]+$")
LOWERCASE_SHA256 = re.compile(r"^[0-9a-f]{64}$")
PINNED_REPRODUCTION_ROW_COUNT = 2409
PINNED_REPRODUCTION_ROUTE_TEST_COUNT = 201
PINNED_REPRODUCTION_BUILD_SUPPORT_COUNT = 498
PINNED_REPRODUCTION_TOOL_SUPPORT_COUNT = 0
PINNED_REPRODUCTION_ROUTE_FIXTURE_COUNT = 1710
PINNED_REPRODUCTION_ENTRY_PATHS_SHA256 = (
    "dac5e1b2eb41a619467452a507e52aa0971a19e0d75509976aa6bc1afbe6c509"
)
PINNED_REPRODUCTION_ROUTE_TEST_PATHS_SHA256 = (
    "795da92ab46bba97d369bbf9d8fd5629ce0e394fd33338617b5bcc5cfe3817b5"
)
PINNED_REPRODUCTION_ARCHIVE_SHA256 = (
    "7b32303162b925e18e56a4fb4ed0dce96b395afdd6cff8cae16a5163bcdcf9a9"
)
PINNED_REPRODUCTION_RAW_FIXTURE_PATHS = (
    "lua/shared/Translate/CS/Recipes_CS.txt",
    "lua/shared/Translate/DA/Recipes_DA.txt",
    "lua/shared/Translate/IT/Recipes_IT.txt",
    "lua/shared/Translate/KO/Recipes_KO.txt",
    "lua/shared/Translate/NL/Recipes_NL.txt",
    "lua/shared/Translate/PT/Recipes_PT.txt",
)


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
                if candidate.is_file() or (
                    literal_tools_path_added
                    and importlib.util.find_spec(imported) is None
                ):
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


def inspect_preimport_build_dependency_closure(
    test_ids: list[str], allowed_modules: set[str]
) -> dict:
    rows: list[dict] = []
    selected_tests: list[dict] = []
    violations: list[dict] = []
    for test_path in selected_test_module_paths(test_ids):
        selected_test = test_path.relative_to(REPO).as_posix()
        exists = test_path.is_file()
        tracked = git_path_is_tracked(test_path)
        ignored = git_path_is_ignored(test_path)
        selected_tests.append(
            {
                "selected_test": selected_test,
                "exists": exists,
                "tracked": tracked,
                "ignored": ignored,
            }
        )
        if not exists:
            violations.append(
                {
                    "code": "selected_test_module_missing",
                    "selected_test": selected_test,
                }
            )
            continue
        if not tracked:
            violations.append(
                {
                    "code": "selected_test_module_untracked",
                    "selected_test": selected_test,
                }
            )
        if ignored:
            violations.append(
                {
                    "code": "selected_test_module_ignored",
                    "selected_test": selected_test,
                }
            )
        for row in tools_build_import_candidates(test_path):
            target = row["resolved_path"]
            target_exists = target.is_file()
            target_tracked = target_exists and git_path_is_tracked(target)
            target_ignored = git_path_is_ignored(target)
            allowed = row["module"] in allowed_modules
            observed = {
                **{key: value for key, value in row.items() if key != "resolved_path"},
                "resolved_path": target.relative_to(REPO).as_posix(),
                "exists": target_exists,
                "tracked": target_tracked,
                "ignored": target_ignored,
                "allowed_by_current_closure": allowed,
            }
            rows.append(observed)
            violation_reason = None
            if not target_exists:
                violation_reason = "target_missing"
            elif not target_tracked:
                violation_reason = "target_untracked"
            elif target_ignored:
                violation_reason = "target_ignored"
            elif not allowed:
                violation_reason = "outside_preserved_closure"
            if violation_reason:
                violations.append(
                    {
                        "code": "unqualified_tools_build_import_bypass",
                        "reason": violation_reason,
                        **observed,
                    }
                )
    return {
        "status": "PASS" if not violations else "FAIL",
        "selected_test_count": len(selected_test_module_paths(test_ids)),
        "selected_tests": selected_tests,
        "tools_build_dependency_count": len(rows),
        "unqualified_tools_build_import_count": sum(
            row.get("code") == "unqualified_tools_build_import_bypass"
            for row in violations
        ),
        "selected_test_source_violation_count": sum(
            str(row.get("code", "")).startswith("selected_test_module_")
            for row in violations
        ),
        "violation_count": len(violations),
        "violations": violations,
        "dependencies": rows,
        "preimport_enforced": True,
        "test_execution_performed": False,
    }


def preimport_violation_message(violation: dict) -> str:
    fields = [
        str(violation.get("code", "preimport_build_dependency_violation")),
        f"selected_test={violation.get('selected_test')}",
    ]
    if violation.get("resolved_path") is not None:
        fields.append(f"resolved_target={violation['resolved_path']}")
    if violation.get("module") is not None:
        fields.append(f"module={violation['module']}")
    if violation.get("reason") is not None:
        fields.append(f"reason={violation['reason']}")
    return ": ".join((fields[0], " ".join(fields[1:])))


def enforce_preimport_build_dependency_closure(
    test_ids: list[str], allowed_modules: set[str]
) -> dict:
    report = inspect_preimport_build_dependency_closure(test_ids, allowed_modules)
    if report["violations"]:
        raise ImportError(preimport_violation_message(report["violations"][0]))
    return report


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
    validate_applicability_overrides(manifest)
    if not required_test_ids(manifest):
        raise ValueError(f"Current route required validation manifest has no required tests: {path}")
    return manifest


def validate_applicability_overrides(manifest: dict) -> None:
    overrides = manifest.get("applicability_overrides")
    if overrides is None:
        return
    if overrides.get("schema_version") != "round3-current-route-applicability-v1":
        raise ValueError("unsupported current-route applicability schema")
    basis_path = overrides.get("current_authority_basis_path")
    expected_sha = overrides.get("current_authority_sha256")
    if not isinstance(basis_path, str) or not isinstance(expected_sha, str):
        raise ValueError("current-route applicability authority binding is incomplete")
    resolved_basis = REPO / basis_path
    decoded_basis = (
        resolved_basis.read_text(encoding="utf-8").encode("utf-8")
        if resolved_basis.is_file()
        else b""
    )
    if (
        not resolved_basis.is_file()
        or hashlib.sha256(decoded_basis).hexdigest() != expected_sha
    ):
        raise ValueError("current-route applicability authority binding drift")
    historical = overrides.get("historical_optional_evidence", {})
    for kind, identity_field in (("tests", "test_id"), ("artifacts", None)):
        seen: set[str] = set()
        for row in historical.get(kind, []):
            identity = row.get(identity_field) if identity_field else (
                row.get("path") or row.get("path_prefix")
            )
            if (
                not isinstance(identity, str)
                or not isinstance(row.get("authority_basis_path"), str)
                or row.get("current_authority_sha256") != expected_sha
                or identity in seen
            ):
                raise ValueError(
                    "current-route historical applicability row is ambiguous"
                )
            seen.add(identity)


def required_test_ids(manifest: dict | None) -> list[str]:
    if not manifest:
        return []
    rows = manifest.get("required_tests", [])
    return sorted(
        {
            str(row["test_id"])
            for row in rows
            if row.get("test_id")
            and test_applicability(manifest, row)
            != "historical_optional_evidence"
        }
    )


def _override_rows(manifest: dict, kind: str) -> list[dict]:
    return list(
        manifest.get("applicability_overrides", {})
        .get("historical_optional_evidence", {})
        .get(kind, [])
    )


def test_applicability(manifest: dict, row: dict) -> str:
    direct = row.get("applicability")
    if direct:
        return str(direct)
    test_id = str(row.get("test_id", ""))
    if any(str(override.get("test_id")) == test_id for override in _override_rows(manifest, "tests")):
        return "historical_optional_evidence"
    return "current_product_required"


def artifact_applicability(manifest: dict, row: dict) -> str:
    direct = row.get("applicability")
    if direct:
        return str(direct)
    path = str(row.get("path", ""))
    for override in _override_rows(manifest, "artifacts"):
        exact = override.get("path")
        prefix = override.get("path_prefix")
        if (exact and str(exact) == path) or (prefix and path.startswith(str(prefix))):
            return "historical_optional_evidence"
    return "current_product_required"


def historical_optional_test_ids(manifest: dict | None) -> list[str]:
    if not manifest:
        return []
    return sorted(
        {
            str(row["test_id"])
            for row in manifest.get("required_tests", [])
            if row.get("test_id")
            and test_applicability(manifest, row)
            == "historical_optional_evidence"
        }
    )


def combined_test_ids(taxonomy_ids: list[str], manifest: dict | None) -> list[str]:
    historical = set(historical_optional_test_ids(manifest))
    return sorted(
        (set(taxonomy_ids) - historical).union(required_test_ids(manifest))
    )


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
        if artifact_applicability(manifest, row) == "historical_optional_evidence":
            continue
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
    historical_ids = historical_optional_test_ids(manifest)
    current_artifacts = [
        row
        for row in manifest.get("required_artifacts", [])
        if artifact_applicability(manifest, row) != "historical_optional_evidence"
    ]
    historical_artifacts = [
        row
        for row in manifest.get("required_artifacts", [])
        if artifact_applicability(manifest, row) == "historical_optional_evidence"
    ]
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
        "required_artifact_count": len(current_artifacts),
        "required_tests": required_ids,
        "historical_optional_evidence": {
            "test_count": len(historical_ids),
            "artifact_count": len(historical_artifacts),
            "tests": historical_ids,
            "artifacts": sorted(
                str(row.get("path", "")) for row in historical_artifacts
            ),
        },
        "applicability_authority": {
            "basis_path": manifest.get("applicability_overrides", {}).get(
                "current_authority_basis_path"
            ),
            "sha256": manifest.get("applicability_overrides", {}).get(
                "current_authority_sha256"
            ),
        },
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


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_repository_relative_path(value: object) -> PurePosixPath:
    if not isinstance(value, str) or not value or not value.isascii():
        raise ValueError("reproduction corpus path must be non-empty ASCII text")
    if not PORTABLE_REPOSITORY_PATH.fullmatch(value) or "\\" in value:
        raise ValueError(f"non-portable reproduction corpus path: {value}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"non-canonical reproduction corpus path: {value}")
    if path.as_posix() != value:
        raise ValueError(f"non-canonical reproduction corpus path: {value}")
    return path


def expected_reproduction_route_test_paths(taxonomy: dict) -> list[str]:
    paths = {row["source_file"] for row in taxonomy.get("rows", [])}
    return sorted(paths)


def reproduction_overlay_import_paths(overlay_root: Path) -> list[str]:
    overlay_v2 = overlay_root / "Iris" / "build" / "description" / "v2"
    return [
        str(overlay_v2 / "tests"),
        str(overlay_v2 / "tools" / "build"),
        str(overlay_v2 / "tools"),
        str(overlay_v2),
    ]


def materialize_historical_reproduction_overlay(
    overlay_root: Path, taxonomy: dict
) -> dict:
    manifest = load_json(HISTORICAL_REPRODUCTION_MANIFEST)
    if manifest.get("schema_version") != "iris-historical-reproduction-corpus-v1":
        raise ValueError("unsupported historical reproduction corpus schema")
    if manifest.get("raw_fixture_paths") != list(
        PINNED_REPRODUCTION_RAW_FIXTURE_PATHS
    ):
        raise ValueError("historical reproduction raw fixture set mismatch")

    rows = manifest.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("historical reproduction corpus rows must be non-empty")
    expected_count = manifest.get("row_count")
    if expected_count != len(rows):
        raise ValueError("historical reproduction corpus row count mismatch")
    if expected_count != PINNED_REPRODUCTION_ROW_COUNT:
        raise ValueError("historical reproduction pinned row count mismatch")

    paths = []
    route_test_paths = []
    build_support_paths = []
    tool_support_paths = []
    route_fixture_paths = []
    row_by_path = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("historical reproduction corpus row must be an object")
        path = canonical_repository_relative_path(row.get("path"))
        path_text = path.as_posix()
        if not path_text.startswith(
            (
                "Iris/build/description/v2/",
                "Iris/build/phase3_output/",
                "Iris/input/",
                "Iris/media/lua/",
                "lua/",
                "scripts/",
            )
        ):
            raise ValueError(f"reproduction corpus path is outside allowed roots: {path_text}")
        if path_text in row_by_path:
            raise ValueError(f"duplicate reproduction corpus path: {path_text}")
        if row.get("entry_kind") not in {
            "route_test",
            "build_support",
            "tool_support",
            "route_fixture",
        }:
            raise ValueError(f"invalid reproduction corpus entry kind: {path_text}")
        if row["entry_kind"] == "route_test":
            if not path_text.startswith("Iris/build/description/v2/tests/test_"):
                raise ValueError(f"invalid reproduction route-test path: {path_text}")
            route_test_paths.append(path_text)
        elif row["entry_kind"] == "build_support":
            if not path_text.startswith("Iris/build/description/v2/tools/build/"):
                raise ValueError(f"invalid reproduction build-support path: {path_text}")
            build_support_paths.append(path_text)
        elif row["entry_kind"] == "tool_support":
            if not path_text.startswith("Iris/build/description/v2/tools/"):
                raise ValueError(f"invalid reproduction tool-support path: {path_text}")
            tool_support_paths.append(path_text)
        else:
            if not path_text.startswith(
                (
                    "Iris/build/description/v2/data/",
                    "Iris/build/description/v2/output/",
                    "Iris/build/description/v2/staging/",
                    "Iris/build/description/v2/tools/style/",
                    "Iris/build/phase3_output/",
                    "Iris/input/",
                    "Iris/media/lua/",
                    "lua/",
                    "scripts/",
                )
            ):
                raise ValueError(f"invalid reproduction fixture path: {path_text}")
            route_fixture_paths.append(path_text)
        if not isinstance(row.get("sha256"), str) or not LOWERCASE_SHA256.fullmatch(
            row["sha256"]
        ):
            raise ValueError(f"invalid reproduction corpus entry hash: {path_text}")
        paths.append(path_text)
        row_by_path[path_text] = row

    if paths != sorted(paths):
        raise ValueError("historical reproduction corpus rows are not ordinal")
    path_identity = sha256_bytes("\n".join(paths).encode("utf-8"))
    if path_identity != manifest.get("expected_entry_paths_sha256"):
        raise ValueError("historical reproduction corpus entry-set hash mismatch")
    if path_identity != PINNED_REPRODUCTION_ENTRY_PATHS_SHA256:
        raise ValueError("historical reproduction pinned entry-set hash mismatch")
    expected_route_tests = expected_reproduction_route_test_paths(taxonomy)
    if route_test_paths != expected_route_tests:
        raise ValueError("historical reproduction route-test denominator mismatch")
    route_test_identity = sha256_bytes("\n".join(route_test_paths).encode("utf-8"))
    if route_test_identity != manifest.get("expected_route_test_paths_sha256"):
        raise ValueError("historical reproduction route-test hash mismatch")
    if route_test_identity != PINNED_REPRODUCTION_ROUTE_TEST_PATHS_SHA256:
        raise ValueError("historical reproduction pinned route-test hash mismatch")
    if manifest.get("route_test_count") != len(route_test_paths):
        raise ValueError("historical reproduction route-test count mismatch")
    if manifest.get("build_support_count") != len(build_support_paths):
        raise ValueError("historical reproduction build-support count mismatch")
    if manifest.get("tool_support_count") != len(tool_support_paths):
        raise ValueError("historical reproduction tool-support count mismatch")
    if manifest.get("route_fixture_count") != len(route_fixture_paths):
        raise ValueError("historical reproduction route-fixture count mismatch")
    if len(route_test_paths) != PINNED_REPRODUCTION_ROUTE_TEST_COUNT:
        raise ValueError("historical reproduction pinned route-test count mismatch")
    if len(build_support_paths) != PINNED_REPRODUCTION_BUILD_SUPPORT_COUNT:
        raise ValueError("historical reproduction pinned build-support count mismatch")
    if len(tool_support_paths) != PINNED_REPRODUCTION_TOOL_SUPPORT_COUNT:
        raise ValueError("historical reproduction pinned tool-support count mismatch")
    if len(route_fixture_paths) != PINNED_REPRODUCTION_ROUTE_FIXTURE_COUNT:
        raise ValueError("historical reproduction pinned route-fixture count mismatch")

    archive_relative = canonical_repository_relative_path(manifest.get("archive_path"))
    if archive_relative.as_posix() != HISTORICAL_REPRODUCTION_ARCHIVE.relative_to(
        REPO
    ).as_posix():
        raise ValueError("historical reproduction archive path mismatch")
    archive = HISTORICAL_REPRODUCTION_ARCHIVE
    archive_sha256 = sha256_bytes(archive.read_bytes())
    if archive_sha256 != manifest.get("archive_sha256"):
        raise ValueError("historical reproduction archive hash mismatch")
    if archive_sha256 != PINNED_REPRODUCTION_ARCHIVE_SHA256:
        raise ValueError("historical reproduction pinned archive hash mismatch")

    overlay_resolved = overlay_root.resolve()
    materialized_count = 0
    with zipfile.ZipFile(archive, "r") as corpus:
        archive_names = corpus.namelist()
        if archive_names != paths or len(set(archive_names)) != len(archive_names):
            raise ValueError("historical reproduction archive entry-set mismatch")
        for path_text in paths:
            payload = corpus.read(path_text)
            if sha256_bytes(payload) != row_by_path[path_text].get("sha256"):
                raise ValueError(
                    f"historical reproduction entry hash mismatch: {path_text}"
                )
            path = PurePosixPath(path_text)
            target = (overlay_root / Path(*path.parts)).resolve()
            try:
                target.relative_to(overlay_resolved)
            except ValueError as exc:
                raise ValueError(
                    f"historical reproduction target escapes overlay: {path_text}"
                ) from exc
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            materialized_count += 1

    return {
        "status": "materialized",
        "manifest_path": HISTORICAL_REPRODUCTION_MANIFEST.relative_to(REPO).as_posix(),
        "archive_path": archive_relative.as_posix(),
        "archive_sha256": archive_sha256,
        "row_count": materialized_count,
        "route_test_count": len(route_test_paths),
        "build_support_count": len(build_support_paths),
        "tool_support_count": len(tool_support_paths),
        "route_fixture_count": len(route_fixture_paths),
        "entry_paths_sha256": path_identity,
    }


def result_payload(
    *,
    contract_class: str,
    test_ids: list[str],
    result: unittest.TestResult,
    elapsed_seconds: float,
    closure_enforced: bool,
    required_validations: dict,
    historical_reproduction: dict,
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
        "historical_reproduction": historical_reproduction,
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
    parser.add_argument("--preimport-only", action="store_true")
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

    if args.preimport_only:
        if not args.enforce_current_build_closure or args.contract_class != "current":
            print(
                "--preimport-only requires --class current "
                "and --enforce-current-build-closure",
                file=sys.stderr,
            )
            return 2
        closure = load_json(Path(args.closure))
        allowed = set(closure["current_closure_modules"])
        allowed.update(closure.get("current_route_allowed_tooling_modules", []))
        report = inspect_preimport_build_dependency_closure(test_ids, allowed)
        if args.out:
            out_path = Path(args.out)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
                + "\n",
                encoding="utf-8",
            )
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0 if report["status"] == "PASS" else 2

    sys.path.insert(0, str(TEST_ROOT))
    sys.path.insert(0, str(V2_ROOT))

    historical_overlay_temp = None
    historical_overlay_paths: list[str] = []
    historical_reproduction = {"status": "not_applicable", "row_count": 0}
    if args.contract_class in {"historical", "diagnostic", "all"}:
        public_root = os.environ.get("PUBLIC")
        overlay_parent = (
            Path(public_root).resolve() / "IrisTest"
            if public_root
            else Path(tempfile.gettempdir()).resolve()
        )
        overlay_parent.mkdir(parents=True, exist_ok=True)
        historical_overlay_temp = tempfile.TemporaryDirectory(
            prefix="historical-overlay-",
            dir=overlay_parent,
        )
        overlay_root = Path(historical_overlay_temp.name)
        try:
            historical_reproduction = materialize_historical_reproduction_overlay(
                overlay_root, taxonomy
            )
        except (KeyError, OSError, TypeError, ValueError, zipfile.BadZipFile) as exc:
            historical_overlay_temp.cleanup()
            print(str(exc), file=sys.stderr)
            return 2
        historical_overlay_paths = reproduction_overlay_import_paths(overlay_root)
        for overlay_path in reversed(historical_overlay_paths):
            sys.path.insert(0, overlay_path)

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

    previous_projection = os.environ.get(
        REQUIRED_VALIDATIONS_PROJECTION_ENV
    )
    previous_test_output_root = os.environ.get(
        CLEAN_CHECKOUT_TEST_OUTPUT_ROOT_ENV
    )
    if args.contract_class == "current":
        os.environ[REQUIRED_VALIDATIONS_PROJECTION_ENV] = str(
            Path(args.required_validations).resolve()
        )
    if historical_overlay_temp is not None:
        os.environ[CLEAN_CHECKOUT_TEST_OUTPUT_ROOT_ENV] = str(overlay_root)
    try:
        result, elapsed = run_suite(test_ids, args.verbosity)
    finally:
        if previous_projection is None:
            os.environ.pop(REQUIRED_VALIDATIONS_PROJECTION_ENV, None)
        else:
            os.environ[REQUIRED_VALIDATIONS_PROJECTION_ENV] = (
                previous_projection
            )
        if previous_test_output_root is None:
            os.environ.pop(CLEAN_CHECKOUT_TEST_OUTPUT_ROOT_ENV, None)
        else:
            os.environ[CLEAN_CHECKOUT_TEST_OUTPUT_ROOT_ENV] = (
                previous_test_output_root
            )
        for overlay_path in historical_overlay_paths:
            if overlay_path in sys.path:
                sys.path.remove(overlay_path)
        if historical_overlay_temp is not None:
            historical_overlay_temp.cleanup()
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
        historical_reproduction=historical_reproduction,
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
