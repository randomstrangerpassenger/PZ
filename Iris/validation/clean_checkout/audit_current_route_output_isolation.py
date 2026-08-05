#!/usr/bin/env python
"""Audit the exact current-route selected closure and source-checkout writes."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


class AuditError(RuntimeError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AuditError(f"expected JSON object: {path}")
    return value


def require_external(repo: Path, path: Path) -> Path:
    lexical = Path(os.path.abspath(path))
    try:
        lexical.relative_to(repo)
    except ValueError:
        pass
    else:
        raise AuditError(f"audit output lexical path must be repository-external: {lexical}")
    resolved = path.resolve()
    try:
        resolved.relative_to(repo)
    except ValueError:
        return resolved
    raise AuditError(f"audit output must be repository-external: {resolved}")


def call_name(node: ast.Call) -> str:
    value = node.func
    parts: list[str] = []
    while isinstance(value, ast.Attribute):
        parts.append(value.attr)
        value = value.value
    if isinstance(value, ast.Name):
        parts.append(value.id)
    return ".".join(reversed(parts))


def expression_provenance(node: ast.AST | None, variables: dict[str, str]) -> str:
    if node is None:
        return "unknown"
    if isinstance(node, ast.Name):
        if node.id in {"tmp_path", "tmpdir"}:
            return "bounded_temporary_contract"
        return variables.get(node.id, "unknown")
    source_tokens = {
        str(child.value)
        for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    }
    names = {
        child.id
        for child in ast.walk(node)
        if isinstance(child, ast.Name)
    }
    attributes = {
        child.attr
        for child in ast.walk(node)
        if isinstance(child, ast.Attribute)
    }
    if names.intersection({"tmp_path", "tmpdir"}) or attributes.intersection({"TemporaryDirectory", "NamedTemporaryFile"}):
        return "bounded_temporary_contract"
    if (
        "IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT" in source_tokens
        or names.intersection({"repository_external_output_root", "clean_checkout_test_paths"})
    ):
        return "external_test_output_contract"
    if any(isinstance(child, ast.Constant) and isinstance(child.value, str) for child in ast.walk(node)):
        return "literal_or_parameter_requires_dynamic_guard"
    return "dynamic_checkout_guard_required"


def expression_path_literal(node: ast.AST | None, variables: dict[str, str]) -> str | None:
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value.replace("\\", "/")
    if isinstance(node, ast.Name):
        return variables.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = expression_path_literal(node.left, variables)
        right = expression_path_literal(node.right, variables)
        if left and right:
            return f"{left.rstrip('/')}/{right.lstrip('/')}"
        return right
    if isinstance(node, ast.Call):
        name = call_name(node)
        if name in {"Path", "PurePath", "PurePosixPath", "PureWindowsPath"} and node.args:
            return expression_path_literal(node.args[0], variables)
        if isinstance(node.func, ast.Attribute):
            return expression_path_literal(node.func.value, variables)
    if isinstance(node, ast.Attribute):
        return expression_path_literal(node.value, variables)
    return None


def source_audit(repo: Path, relative: str, *, source_role: str) -> dict[str, Any]:
    path = (repo / relative).resolve()
    try:
        path.relative_to(repo)
    except ValueError as error:
        raise AuditError(f"taxonomy source escapes repository: {relative}") from error
    if not path.is_file():
        raise AuditError(f"taxonomy source is missing: {relative}")
    source = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=relative)
    imports: set[str] = set()
    import_requests: list[dict[str, Any]] = []
    unresolved_dynamic_imports: list[dict[str, Any]] = []
    write_sites: list[dict[str, Any]] = []
    variables: dict[str, str] = {}
    path_variables: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            provenance = expression_provenance(value, variables)
            path_literal = expression_path_literal(value, path_variables)
            for target in targets:
                if isinstance(target, ast.Name):
                    variables[target.id] = provenance
                    if path_literal:
                        path_variables[target.id] = path_literal
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
                import_requests.append(
                    {"kind": "import", "module": alias.name, "level": 0, "names": [], "line": node.lineno}
                )
        elif isinstance(node, ast.ImportFrom):
            display = ("." * node.level) + (node.module or "")
            imports.add(display)
            import_requests.append(
                {
                    "kind": "from",
                    "module": node.module or "",
                    "level": node.level,
                    "names": sorted(alias.name for alias in node.names if alias.name != "*"),
                    "line": node.lineno,
                }
            )
        elif isinstance(node, ast.Call):
            name = call_name(node)
            if name in {
                "importlib.util.spec_from_file_location",
                "runpy.run_path",
                "SourceFileLoader",
                "importlib.machinery.SourceFileLoader",
            }:
                path_argument_index = 1 if name.endswith("spec_from_file_location") or name.endswith("SourceFileLoader") else 0
                dynamic_path = (
                    expression_path_literal(node.args[path_argument_index], path_variables)
                    if len(node.args) > path_argument_index
                    else None
                )
                if dynamic_path and dynamic_path.lower().endswith(".py"):
                    import_requests.append(
                        {
                            "kind": "dynamic_path",
                            "module": "",
                            "path": dynamic_path,
                            "level": 0,
                            "names": [],
                            "line": node.lineno,
                        }
                    )
                else:
                    unresolved_dynamic_imports.append({"call": name, "line": node.lineno})
            if name in {"__import__", "importlib.import_module"}:
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    import_requests.append(
                        {
                            "kind": "dynamic_literal",
                            "module": node.args[0].value,
                            "level": 0,
                            "names": [],
                            "line": node.lineno,
                        }
                    )
                else:
                    unresolved_dynamic_imports.append({"call": name, "line": node.lineno})
            write_like = name.endswith(
                (
                    "write_text",
                    "write_bytes",
                    "mkdir",
                    "touch",
                    "unlink",
                    "replace",
                    "rename",
                    "rmtree",
                    "copy",
                    "copy2",
                    "copyfile",
                )
            ) or name in {"open", "Path.open", "os.open", "subprocess.run", "subprocess.Popen"}
            if write_like:
                if name in {"subprocess.run", "subprocess.Popen"}:
                    resolution = "dynamic_checkout_guard_required"
                elif isinstance(node.func, ast.Attribute):
                    resolution = expression_provenance(node.func.value, variables)
                elif node.args:
                    resolution = expression_provenance(node.args[0], variables)
                else:
                    resolution = "unresolved"
                if resolution in {"unknown", "literal_or_parameter_requires_dynamic_guard"}:
                    resolution = "dynamic_checkout_guard_required"
                write_sites.append(
                    {
                        "line": getattr(node, "lineno", None),
                        "call": name,
                        "resolved_sink": resolution,
                        "resolution_status": (
                            "unresolved"
                            if resolution == "unresolved"
                            else "dynamic_required"
                            if resolution == "dynamic_checkout_guard_required"
                            else "resolved"
                        ),
                    }
                )
    return {
        "source_file": relative,
        "source_role": source_role,
        "sha256": sha256_file(path),
        "imports": sorted(imports),
        "import_requests": sorted(
            import_requests,
            key=lambda row: (int(row["line"]), str(row["kind"]), int(row["level"]), str(row["module"])),
        ),
        "unresolved_dynamic_imports": unresolved_dynamic_imports,
        "write_sites": sorted(write_sites, key=lambda row: (int(row.get("line") or 0), str(row.get("call")))),
        "unresolved_write_site_count": sum(row["resolution_status"] == "unresolved" for row in write_sites),
        "dynamic_write_site_count": sum(row["resolution_status"] == "dynamic_required" for row in write_sites),
    }


def _module_candidates(base: Path, module: str) -> list[Path]:
    module_path = Path(*[part for part in module.split(".") if part])
    target = base / module_path
    return [target.with_suffix(".py"), target / "__init__.py"]


def resolve_local_import(
    repo: Path,
    source_relative: str,
    request: dict[str, Any],
) -> tuple[list[str], str]:
    module = str(request.get("module", ""))
    level = int(request.get("level", 0))
    names = [str(name) for name in request.get("names", [])]
    source_parent = (repo / source_relative).parent
    candidates: list[Path] = []
    if request.get("kind") == "dynamic_path":
        raw_path = Path(str(request.get("path", "")))
        candidates.append(raw_path if raw_path.is_absolute() else repo / raw_path)
        candidates.append(source_parent / raw_path)
    if level:
        base = source_parent
        for _ in range(level - 1):
            base = base.parent
        candidates.extend(_module_candidates(base, module))
        for name in names:
            joined = ".".join(part for part in (module, name) if part)
            candidates.extend(_module_candidates(base, joined))
    else:
        for base in (
            repo,
            source_parent,
            repo / "Iris/build/description/v2/tools/build",
            repo / "Iris/build/description/v2/tools",
        ):
            candidates.extend(_module_candidates(base, module))
            if request.get("kind") == "from":
                for name in names:
                    candidates.extend(_module_candidates(base, f"{module}.{name}"))
    resolved = {
        candidate.resolve().relative_to(repo).as_posix()
        for candidate in candidates
        if candidate.is_file()
    }
    if not resolved and module:
        tail = module.rsplit(".", 1)[-1]
        matches = {
            path.resolve().relative_to(repo).as_posix()
            for path in repo.rglob(f"{tail}.py")
            if not any(part in {".git", "__pycache__", ".pytest_cache", ".tmp", ".tmp_tests"} for part in path.parts)
        }
        if len(matches) == 1:
            resolved = matches
        elif len(matches) > 1:
            suffix = module.replace(".", "/") + ".py"
            exact_suffix = {path for path in matches if path.endswith(suffix)}
            if len(exact_suffix) == 1:
                resolved = exact_suffix
            else:
                return [], "ambiguous_local_import"
    if resolved:
        expanded = set(resolved)
        for relative in list(resolved):
            current = (repo / relative).parent
            while current != repo and repo in current.parents:
                initializer = current / "__init__.py"
                if initializer.is_file():
                    expanded.add(initializer.resolve().relative_to(repo).as_posix())
                current = current.parent
        return sorted(expanded), "local"
    if level:
        return [], "unresolved_relative_import"
    top_level = module.split(".", 1)[0]
    if top_level in sys.stdlib_module_names or top_level in {"pytest"}:
        return [], "external"
    return [], "external_or_unresolved"


def required_test_applicability(required: dict[str, Any], row: dict[str, Any]) -> str:
    direct = row.get("applicability")
    if direct:
        return str(direct)
    test_id = str(row.get("test_id", ""))
    optional_rows = (
        required.get("applicability_overrides", {})
        .get("historical_optional_evidence", {})
        .get("tests", [])
    )
    if any(str(optional.get("test_id", "")) == test_id for optional in optional_rows):
        return "historical_optional_evidence"
    return "current_product_required"


def build_inventory(repo: Path, taxonomy_path: Path, required_path: Path) -> dict[str, Any]:
    taxonomy = load_object(taxonomy_path)
    required = load_object(required_path)
    taxonomy_source_rows = taxonomy.get("rows", [])
    taxonomy_rows = {str(row.get("test_id")): row for row in taxonomy_source_rows}
    if len(taxonomy_rows) != len(taxonomy_source_rows):
        raise AuditError("taxonomy contains duplicate test IDs")
    required_source_rows = required.get("required_tests", [])
    all_required_ids = [str(row.get("test_id", "")) for row in required_source_rows]
    if not all_required_ids or len(set(all_required_ids)) != len(all_required_ids):
        raise AuditError("required validations are empty or contain duplicate IDs")
    historical_optional_ids = sorted(
        str(row.get("test_id", ""))
        for row in required_source_rows
        if required_test_applicability(required, row) == "historical_optional_evidence"
    )
    required_rows = [
        row
        for row in required_source_rows
        if required_test_applicability(required, row) != "historical_optional_evidence"
    ]
    if not required_rows:
        raise AuditError("required validations contain no current-product tests")
    selected: list[dict[str, Any]] = []
    sources: dict[str, dict[str, Any]] = {}
    declared_imports: dict[str, set[str]] = {}
    missing: list[str] = []
    for required_row in required_rows:
        test_id = str(required_row.get("test_id", ""))
        taxonomy_row = taxonomy_rows.get(test_id)
        if taxonomy_row is None:
            missing.append(test_id)
            continue
        source_file = str(taxonomy_row.get("source_file", ""))
        if not source_file:
            missing.append(test_id)
            continue
        if taxonomy_row.get("contract_class") != "current" or taxonomy_row.get("state") != "ok":
            raise AuditError(f"required validation is not current+ok: {test_id}")
        if source_file not in sources:
            sources[source_file] = source_audit(repo, source_file, source_role="selected_test_module")
            declared_imports[source_file] = set()
        declared_imports[source_file].update(str(name) for name in taxonomy_row.get("imported_build_modules", []))
        selected.append(
            {
                "test_id": test_id,
                "taxonomy_contract_class": taxonomy_row.get("contract_class"),
                "taxonomy_state": taxonomy_row.get("state"),
                "source_file": source_file,
                "source_sha256": sources[source_file]["sha256"],
                "required_role": required_row.get("role"),
            }
        )
    if missing:
        raise AuditError(f"required validation IDs lack taxonomy source rows: {missing}")
    route_runner_relative = "Iris/_docs/round3/round3_run_contract_tests.py"
    route_runner = repo / route_runner_relative
    if not route_runner.is_file():
        raise AuditError("current-route runner is missing")
    if route_runner_relative not in sources:
        sources[route_runner_relative] = source_audit(
            repo,
            route_runner_relative,
            source_role="current_route_runner",
        )
        declared_imports[route_runner_relative] = set()
    pending = list(sorted(sources))
    unresolved_imports: list[dict[str, Any]] = []
    while pending:
        source_file = pending.pop(0)
        source_row = sources[source_file]
        requests = list(source_row["import_requests"])
        requests.extend(
            {"kind": "declared_build", "module": module, "level": 0, "names": [], "line": None}
            for module in sorted(declared_imports.get(source_file, set()))
        )
        resolved_for_source: set[str] = set()
        external_for_source: set[str] = set()
        unresolved_for_source: list[dict[str, Any]] = []
        for request in requests:
            resolved_paths, disposition = resolve_local_import(repo, source_file, request)
            if disposition in {"unresolved_relative_import", "ambiguous_local_import"} or (
                request["kind"] == "declared_build" and not resolved_paths
            ):
                unresolved = {**request, "disposition": disposition}
                unresolved_for_source.append(unresolved)
                unresolved_imports.append({"source_file": source_file, **unresolved})
                continue
            if not resolved_paths:
                external_for_source.add(str(request.get("module", "")))
            for resolved in resolved_paths:
                resolved_for_source.add(resolved)
                if resolved in sources:
                    continue
                sources[resolved] = source_audit(repo, resolved, source_role="imported_local_module")
                declared_imports[resolved] = set()
                pending.append(resolved)
        for dynamic in source_row["unresolved_dynamic_imports"]:
            unresolved = {"source_file": source_file, "kind": "dynamic_nonliteral", **dynamic}
            unresolved_for_source.append(unresolved)
            unresolved_imports.append(unresolved)
        source_row["resolved_local_imports"] = sorted(resolved_for_source)
        source_row["external_imports"] = sorted(external_for_source)
        source_row["unresolved_imports"] = unresolved_for_source
    selected.sort(key=lambda row: str(row["test_id"]))
    source_rows = [sources[key] for key in sorted(sources)]
    source_census = [
        {"source_file": row["source_file"], "source_role": row["source_role"], "sha256": row["sha256"]} for row in source_rows
    ]
    payload = {
        "schema_version": "iris_repository_runtime_lightweighting_current_route_output_isolation_inventory_v1",
        "repository_root": repo.as_posix(),
        "taxonomy": {"path": taxonomy_path.resolve().as_posix(), "sha256": sha256_file(taxonomy_path)},
        "required_validations": {"path": required_path.resolve().as_posix(), "sha256": sha256_file(required_path)},
        "selected_test_count": len(selected),
        "historical_optional_test_count": len(historical_optional_ids),
        "historical_optional_test_ids": historical_optional_ids,
        "selected_source_count": sum(row["source_role"] == "selected_test_module" for row in source_rows),
        "closure_source_count": len(source_rows),
        "selected_test_source_count": sum(row["source_role"] == "selected_test_module" for row in source_rows),
        "selected_tests": selected,
        "sources": source_rows,
        "source_census_sha256": sha256_bytes(canonical_json_bytes(source_census)),
        "route_runner": {"path": route_runner.relative_to(repo).as_posix(), "sha256": sha256_file(route_runner)},
        "unresolved_write_site_count": sum(int(row["unresolved_write_site_count"]) for row in source_rows),
        "dynamic_write_site_count": sum(int(row["dynamic_write_site_count"]) for row in source_rows),
        "unresolved_import_count": len(unresolved_imports),
        "unresolved_imports": unresolved_imports,
    }
    if payload["unresolved_import_count"]:
        raise AuditError(f"current-route closure has unresolved local/dynamic imports: {unresolved_imports}")
    return payload


def atomic_write_new(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise AuditError(f"audit output already exists: {path}")
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(canonical_json_bytes(payload))
    try:
        os.link(temporary, path)
    except FileExistsError as error:
        raise AuditError(f"audit output already exists: {path}") from error
    finally:
        temporary.unlink(missing_ok=True)


def find_command_receipts(root: Path) -> dict[str, dict[str, Any]]:
    receipts: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*.json")):
        try:
            payload = load_object(path)
        except (OSError, ValueError, json.JSONDecodeError, AuditError):
            continue
        if payload.get("schema_version") != "iris_repository_runtime_lightweighting_command_receipt_v1":
            continue
        command_id = str(payload.get("command_id", ""))
        if command_id in receipts:
            raise AuditError(f"duplicate command receipt ID: {command_id}")
        receipts[command_id] = {
            "path": path.resolve().as_posix(),
            "sha256": sha256_file(path),
            "payload": payload,
        }
    return receipts


def route_passed(route: dict[str, Any]) -> bool:
    if route.get("success") is True:
        return True
    if route.get("status") in {"PASS", "passed"}:
        return True
    summary = route.get("summary", {})
    return (
        isinstance(summary, dict)
        and "failed" in summary
        and "errors" in summary
        and summary.get("failed") == 0
        and summary.get("errors") == 0
    )


def same_path(left: object, right: Path) -> bool:
    try:
        return os.path.normcase(str(Path(str(left)).resolve())) == os.path.normcase(str(right.resolve()))
    except (OSError, ValueError):
        return False


def git_identity(repo: Path) -> tuple[str, str]:
    completed = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD", "HEAD^{tree}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise AuditError("audit repository identity is unresolved")
    rows = completed.stdout.splitlines()
    if len(rows) != 2:
        raise AuditError("audit repository identity output is malformed")
    return rows[0], rows[1]


def resolve_argv_path(repo: Path, value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (repo / path).resolve()


def validate_dynamic_route_receipt(
    repo: Path,
    route_result: Path,
    receipt_row: dict[str, Any],
) -> dict[str, Any]:
    receipt_path = Path(receipt_row["path"])
    receipt = receipt_row["payload"]
    if receipt.get("schema_version") != "iris_repository_runtime_lightweighting_command_receipt_v1":
        raise AuditError("dynamic route command receipt schema mismatch")
    if receipt.get("terminal_status") != "pass" or receipt.get("native_exit_code") != 0 or receipt.get("semantic_exit_code") != 0:
        raise AuditError("dynamic current route command receipt is not an executed PASS")
    if not same_path(receipt.get("working_directory"), repo):
        raise AuditError("dynamic current route command ran in a different checkout")
    assertion = receipt.get("output_assertion") or {}
    delta = assertion.get("delta") or {}
    if assertion.get("kind") != "checkout_unchanged" or assertion.get("status") != "pass":
        raise AuditError("dynamic current route lacks checkout_unchanged PASS")
    for key in ("changed_count", "tracked_delta_count", "untracked_delta_count", "ignored_delta_count", "unreadable_count"):
        if int(delta.get(key, -1)) != 0:
            raise AuditError(f"dynamic current route checkout census is not zero: {key}")

    spec_binding = receipt.get("command_spec") or {}
    spec_path = Path(str(spec_binding.get("path", ""))).resolve()
    if not spec_path.is_file() or sha256_file(spec_path) != spec_binding.get("sha256"):
        raise AuditError("dynamic route command spec identity mismatch")
    spec = load_object(spec_path)
    if spec.get("schema_version") != "iris_repository_runtime_lightweighting_command_spec_v1":
        raise AuditError("dynamic route command spec schema mismatch")
    if not same_path(spec.get("command_receipt"), receipt_path):
        raise AuditError("dynamic route command spec points to another receipt")
    if spec.get("command_id") != receipt.get("command_id") or spec.get("output_assertion") != "checkout_unchanged" or not same_path(spec.get("working_directory"), repo):
        raise AuditError("dynamic route command spec execution boundary mismatch")
    if not same_path(spec.get("executable"), Path(str(receipt.get("executable", "")))):
        raise AuditError("dynamic route executable/spec binding mismatch")
    if spec.get("claim_id") != receipt.get("claim_id") or not same_path(spec.get("subject_receipt"), Path(str(receipt.get("subject_receipt", {}).get("path", "")))):
        raise AuditError("dynamic route command claim/subject binding mismatch")
    subject_binding = receipt.get("subject_receipt") or {}
    subject_path = Path(str(subject_binding.get("path", ""))).resolve()
    if not subject_path.is_file() or sha256_file(subject_path) != subject_binding.get("sha256"):
        raise AuditError("dynamic route subject receipt identity mismatch")
    subject = load_object(subject_path)
    head, tree = git_identity(repo)
    if subject.get("claim_id") != receipt.get("claim_id") or subject.get("commit") != head or subject.get("tree") != tree:
        raise AuditError("dynamic route subject differs from exact audit checkout")
    if subject_binding.get("execution_commit") != head or subject_binding.get("execution_tree") != tree:
        raise AuditError("dynamic route receipt lacks exact execution commit/tree")

    argv = receipt.get("decoded_argv")
    if not isinstance(argv, list) or argv != spec.get("argv"):
        raise AuditError("dynamic route argv/spec round trip mismatch")
    runner = repo / "Iris/_docs/round3/round3_run_contract_tests.py"
    if (
        not same_path(receipt.get("executable"), Path(sys.executable))
        or len(argv) != 7
        or argv[0] != "-B"
        or not same_path(resolve_argv_path(repo, str(argv[1])), runner)
        or argv[2:6]
        != ["--class", "current", "--enforce-current-build-closure", "--out"]
    ):
        raise AuditError("dynamic route argv is not the exact canonical current invocation")
    out_index = 5
    if not same_path(resolve_argv_path(repo, str(argv[out_index + 1])), route_result):
        raise AuditError("dynamic route argv writes a different result path")
    invoked = receipt.get("invoked_repository_files")
    if not isinstance(invoked, list):
        raise AuditError("dynamic route receipt lacks invoked repository implementation bindings")
    runner_rows = [row for row in invoked if same_path(row.get("actual_path"), runner)]
    if len(runner_rows) != 1:
        raise AuditError("dynamic route receipt does not bind the exact route runner implementation")
    runner_row = runner_rows[0]
    blob = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"{head}:{runner.relative_to(repo).as_posix()}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if (
        blob.returncode != 0
        or runner_row.get("execution_commit") != head
        or runner_row.get("git_blob_id") != blob.stdout.strip()
        or runner_row.get("working_sha256") != sha256_file(runner)
    ):
        raise AuditError("dynamic route runner implementation identity mismatch")
    successor = receipt.get("successor_policy") or {}
    successor_path = repo / "Iris/validation/clean_checkout/contracts/repository_runtime_lightweighting_output_policy.json"
    if not same_path(successor.get("path"), successor_path) or not successor_path.is_file() or successor.get("sha256") != sha256_file(successor_path):
        raise AuditError("dynamic route command lacks exact successor policy identity")
    return {
        "path": receipt_path.as_posix(),
        "sha256": receipt_row["sha256"],
        "claim_id": receipt["claim_id"],
        "subject_receipt": subject_binding,
        "command_spec": spec_binding,
        "working_directory": repo.as_posix(),
        "decoded_argv": argv,
        "output_assertion": assertion,
    }


def command_inventory(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    out = require_external(repo, args.out)
    taxonomy = (repo / args.taxonomy).resolve()
    required = (repo / args.required_validations).resolve()
    if taxonomy != (repo / "Iris/_docs/round3/round3_test_taxonomy.json").resolve() or required != (repo / "Iris/_docs/round3/current_route_required_validations.json").resolve():
        raise AuditError("inventory requires the exact current taxonomy and required-validation paths")
    payload = build_inventory(repo, taxonomy, required)
    atomic_write_new(out, payload)


def command_seal(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    out = require_external(repo, args.out)
    static_inventory_path = require_external(repo, args.static_inventory)
    route_result_path = require_external(repo, args.route_result)
    receipt_root = require_external(repo, args.command_receipt_root)
    inventory = load_object(static_inventory_path)
    route = load_object(route_result_path)
    if inventory.get("repository_root") != repo.as_posix():
        raise AuditError("static inventory repository mismatch")
    taxonomy = (repo / "Iris/_docs/round3/round3_test_taxonomy.json").resolve()
    required = (repo / "Iris/_docs/round3/current_route_required_validations.json").resolve()
    regenerated = build_inventory(repo, taxonomy, required)
    if static_inventory_path.read_bytes() != canonical_json_bytes(inventory) or regenerated != inventory:
        raise AuditError("static inventory is not the exact regenerated current-route closure")
    if inventory.get("unresolved_write_site_count") != 0 or inventory.get("unresolved_import_count") != 0:
        raise AuditError("static inventory has unresolved source analysis")
    if not route_passed(route):
        raise AuditError("dynamic current route did not pass")
    receipts = find_command_receipts(receipt_root)
    dynamic = [row for key, row in receipts.items() if key.endswith("route-audit-dynamic-current")]
    if len(dynamic) != 1:
        raise AuditError("dynamic current route command receipt is absent or not PASS")
    dynamic_binding = validate_dynamic_route_receipt(repo, route_result_path, dynamic[0])
    audit_commit, audit_tree = git_identity(repo)
    payload = {
        "schema_version": "iris_repository_runtime_lightweighting_current_route_output_isolation_receipt_v1",
        "status": "PASS",
        "repository_root": repo.as_posix(),
        "audit_subject": {"commit": audit_commit, "tree": audit_tree},
        "taxonomy_sha256": inventory["taxonomy"]["sha256"],
        "required_validations_sha256": inventory["required_validations"]["sha256"],
        "source_census_sha256": inventory["source_census_sha256"],
        "selected_test_count": inventory["selected_test_count"],
        "selected_source_count": inventory["selected_source_count"],
        "closure_source_count": inventory["closure_source_count"],
        "route_runner_sha256": inventory["route_runner"]["sha256"],
        "dynamic_write_site_count": inventory["dynamic_write_site_count"],
        "dynamic_write_sites_covered_by_checkout_census": True,
        "static_inventory": {"path": static_inventory_path.as_posix(), "sha256": sha256_file(static_inventory_path)},
        "route_result": {"path": route_result_path.as_posix(), "sha256": sha256_file(route_result_path)},
        "dynamic_route_command_receipt": dynamic_binding,
        "checkout_unchanged": True,
        "tracked_delta_count": 0,
        "untracked_delta_count": 0,
        "ignored_delta_count": 0,
        "unreadable_count": 0,
    }
    atomic_write_new(out, payload)


def command_verify(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    receipt_path = require_external(repo, args.receipt)
    receipt = load_object(receipt_path)
    if receipt.get("schema_version") != "iris_repository_runtime_lightweighting_current_route_output_isolation_receipt_v1" or receipt.get("status") != "PASS":
        raise AuditError("output-isolation receipt is not PASS")
    current_commit, current_tree = git_identity(repo)
    audit_subject = receipt.get("audit_subject", {})
    if audit_subject != {"commit": current_commit, "tree": current_tree}:
        raise AuditError("output-isolation audit subject differs from the current validation subject")
    audit_root = Path(str(receipt.get("repository_root", ""))).resolve()
    if not (audit_root / ".git").exists():
        raise AuditError("output-isolation audit checkout is unavailable")
    for parent, child in ((repo, audit_root), (audit_root, repo)):
        try:
            child.relative_to(parent)
        except ValueError:
            continue
        raise AuditError(
            "output-isolation audit and current validation checkouts must be separate and disjoint"
        )
    audit_commit, audit_tree = git_identity(audit_root)
    audit_status = subprocess.run(
        ["git", "-C", str(audit_root), "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    current_status = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if (
        (audit_commit, audit_tree) != (current_commit, current_tree)
        or audit_status.returncode != 0
        or audit_status.stdout
        or current_status.returncode != 0
        or current_status.stdout
    ):
        raise AuditError("output-isolation audit/current validation checkout is not the exact clean subject")
    taxonomy = (repo / args.taxonomy).resolve()
    required = (repo / args.required_validations).resolve()
    if taxonomy != (repo / "Iris/_docs/round3/round3_test_taxonomy.json").resolve() or required != (repo / "Iris/_docs/round3/current_route_required_validations.json").resolve():
        raise AuditError("verify requires the exact current taxonomy and required-validation paths")
    current = build_inventory(repo, taxonomy, required)
    static_binding = receipt.get("static_inventory", {})
    static_path = Path(str(static_binding.get("path", ""))).resolve()
    if not static_path.is_file() or sha256_file(static_path) != static_binding.get("sha256"):
        raise AuditError("output-isolation retained binding mismatch: static_inventory")
    retained_inventory = load_object(static_path)
    if (
        static_path.read_bytes() != canonical_json_bytes(retained_inventory)
        or retained_inventory.get("schema_version")
        != "iris_repository_runtime_lightweighting_current_route_output_isolation_inventory_v1"
        or retained_inventory.get("repository_root") != audit_root.as_posix()
        or retained_inventory.get("unresolved_write_site_count") != 0
        or retained_inventory.get("unresolved_import_count") != 0
    ):
        raise AuditError("retained output-isolation inventory is malformed or unresolved")
    expected = (
        receipt.get("taxonomy_sha256"), receipt.get("required_validations_sha256"),
        receipt.get("source_census_sha256"), receipt.get("selected_test_count"),
        receipt.get("selected_source_count"), receipt.get("closure_source_count"), receipt.get("route_runner_sha256"),
        receipt.get("dynamic_write_site_count"),
    )
    actual = (
        current["taxonomy"]["sha256"], current["required_validations"]["sha256"],
        current["source_census_sha256"], current["selected_test_count"],
        current["selected_source_count"], current["closure_source_count"], current["route_runner"]["sha256"],
        current["dynamic_write_site_count"],
    )
    retained = (
        retained_inventory.get("taxonomy", {}).get("sha256"),
        retained_inventory.get("required_validations", {}).get("sha256"),
        retained_inventory.get("source_census_sha256"),
        retained_inventory.get("selected_test_count"),
        retained_inventory.get("selected_source_count"),
        retained_inventory.get("closure_source_count"),
        retained_inventory.get("route_runner", {}).get("sha256"),
        retained_inventory.get("dynamic_write_site_count"),
    )
    if (
        actual != expected
        or retained != expected
        or receipt.get("dynamic_write_sites_covered_by_checkout_census") is not True
    ):
        raise AuditError("current-route closure identity changed; a new audit is required")
    for key in ("route_result",):
        binding = receipt.get(key, {})
        path = Path(str(binding.get("path", ""))).resolve()
        if not path.is_file() or sha256_file(path) != binding.get("sha256"):
            raise AuditError(f"output-isolation retained binding mismatch: {key}")
    dynamic = receipt.get("dynamic_route_command_receipt", {})
    for key in ("path",):
        path = Path(str(dynamic.get(key, ""))).resolve()
        if not path.is_file() or sha256_file(path) != dynamic.get("sha256"):
            raise AuditError("output-isolation dynamic command receipt binding mismatch")
    spec = dynamic.get("command_spec", {})
    spec_path = Path(str(spec.get("path", ""))).resolve()
    if not spec_path.is_file() or sha256_file(spec_path) != spec.get("sha256"):
        raise AuditError("output-isolation dynamic command spec binding mismatch")
    route_result_path = Path(str(receipt.get("route_result", {}).get("path", ""))).resolve()
    validate_dynamic_route_receipt(
        audit_root,
        route_result_path,
        {"path": dynamic.get("path"), "sha256": dynamic.get("sha256"), "payload": load_object(Path(str(dynamic.get("path", ""))).resolve())},
    )
    if receipt.get("checkout_unchanged") is not True or any(
        int(receipt.get(key, -1)) != 0
        for key in ("tracked_delta_count", "untracked_delta_count", "ignored_delta_count", "unreadable_count")
    ):
        raise AuditError("output-isolation receipt is not physically clean")
    print(json.dumps({"status": "PASS", "receipt_sha256": sha256_file(receipt_path)}, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    inventory = sub.add_parser("inventory")
    inventory.add_argument("--repo", type=Path, required=True)
    inventory.add_argument("--taxonomy", type=Path, required=True)
    inventory.add_argument("--required-validations", type=Path, required=True)
    inventory.add_argument("--out", type=Path, required=True)
    seal = sub.add_parser("seal")
    seal.add_argument("--repo", type=Path, required=True)
    seal.add_argument("--static-inventory", type=Path, required=True)
    seal.add_argument("--route-result", type=Path, required=True)
    seal.add_argument("--command-receipt-root", type=Path, required=True)
    seal.add_argument("--out", type=Path, required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--repo", type=Path, required=True)
    verify.add_argument("--taxonomy", type=Path, required=True)
    verify.add_argument("--required-validations", type=Path, required=True)
    verify.add_argument("--receipt", type=Path, required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    {"inventory": command_inventory, "seal": command_seal, "verify": command_verify}[args.command](args)
    if args.command != "verify":
        print(json.dumps({"status": "PASS", "command": args.command}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, OSError, ValueError, json.JSONDecodeError, SyntaxError) as error:
        print(json.dumps({"status": "FAIL", "error_type": type(error).__name__, "error": str(error)}, sort_keys=True), file=sys.stderr)
        raise SystemExit(2)
