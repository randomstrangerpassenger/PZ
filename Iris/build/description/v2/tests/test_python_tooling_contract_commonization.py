from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import unittest
from collections import defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS_ROOT = REPO / "Iris/build/description/v2/tools/build"
CLOSURE = REPO / "Iris/_docs/round3/round3_active_core_closure.json"
RECEIPT = (
    REPO
    / "Iris/_docs/refactor/codebase_optimization/python_tooling_decision.json"
)
HELPER_NAMES = {"load_json", "write_json", "sha256_file"}
PROCESS_CALLEES = {
    "subprocess.run",
    "subprocess.Popen",
    "subprocess.check_call",
    "subprocess.check_output",
    "subprocess.call",
}


def dotted_name(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def function_fingerprint(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    # The dump includes arguments, defaults, calls, constants, exception
    # handling and write options, while excluding source position noise.
    contract = {
        "arguments": ast.dump(node.args, include_attributes=False),
        "body": [ast.dump(item, include_attributes=False) for item in node.body],
        "decorators": [
            ast.dump(item, include_attributes=False) for item in node.decorator_list
        ],
        "returns": ast.dump(node.returns, include_attributes=False)
        if node.returns
        else None,
    }
    return canonical_sha256(contract)


def build_inventory() -> dict:
    tracked_result = subprocess.run(
        [
            "git",
            "ls-files",
            "-z",
            "--",
            TOOLS_ROOT.relative_to(REPO).as_posix(),
        ],
        cwd=REPO,
        capture_output=True,
        check=False,
    )
    if tracked_result.returncode != 0:
        raise RuntimeError(
            "failed to enumerate tracked Python tooling: "
            + tracked_result.stderr.decode("utf-8", errors="replace")
        )
    files = sorted(
        REPO / value.decode("utf-8")
        for value in tracked_result.stdout.split(b"\0")
        if value and value.endswith(b".py")
    )
    closure = json.loads(CLOSURE.read_text(encoding="utf-8"))
    current_modules = set(closure.get("current_closure_modules", []))
    current_modules.update(closure.get("current_route_allowed_tooling_modules", []))
    process_sites: list[dict] = []
    helper_definitions: list[dict] = []

    for path in files:
        relative = path.relative_to(REPO).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        parent_function: dict[ast.AST, str | None] = {}

        class Visitor(ast.NodeVisitor):
            def __init__(self) -> None:
                self.function: str | None = None

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                previous = self.function
                self.function = node.name
                parent_function[node] = previous
                if node.name in HELPER_NAMES:
                    helper_definitions.append(
                        {
                            "path": relative,
                            "module": path.stem,
                            "name": node.name,
                            "line": node.lineno,
                            "fingerprint": function_fingerprint(node),
                            "current": path.stem in current_modules,
                        }
                    )
                self.generic_visit(node)
                self.function = previous

            visit_AsyncFunctionDef = visit_FunctionDef

            def visit_Call(self, node: ast.Call) -> None:
                callee = dotted_name(node.func)
                if callee in PROCESS_CALLEES:
                    process_sites.append(
                        {
                            "path": relative,
                            "module": path.stem,
                            "line": node.lineno,
                            "function": self.function,
                            "callee": callee,
                            "disposition": "retain_process_boundary",
                        }
                    )
                self.generic_visit(node)

        Visitor().visit(tree)

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in helper_definitions:
        grouped[(row["name"], row["fingerprint"])].append(row)
    exact_current_groups = []
    for (name, fingerprint), rows in sorted(grouped.items()):
        consumers = sorted(row["path"] for row in rows if row["current"])
        if len(consumers) >= 3:
            exact_current_groups.append(
                {
                    "name": name,
                    "fingerprint": fingerprint,
                    "current_producer_count": len(consumers),
                    "consumers": consumers,
                }
            )

    denominator = {
        "tool_files": [path.relative_to(REPO).as_posix() for path in files],
        "subprocess_sites": process_sites,
        "helper_definitions": helper_definitions,
        "exact_current_groups": exact_current_groups,
    }
    return {
        "denominator": denominator,
        "denominator_sha256": canonical_sha256(denominator),
        "counts": {
            "tool_files": len(files),
            "subprocess_sites": len(process_sites),
            "helper_definitions": len(helper_definitions),
            "load_json_definitions": sum(
                row["name"] == "load_json" for row in helper_definitions
            ),
            "write_json_definitions": sum(
                row["name"] == "write_json" for row in helper_definitions
            ),
            "sha256_file_definitions": sum(
                row["name"] == "sha256_file" for row in helper_definitions
            ),
            "exact_current_groups": len(exact_current_groups),
        },
    }


class PythonToolingContractCommonizationTest(unittest.TestCase):
    def test_inventory_and_decision_receipt(self) -> None:
        inventory = build_inventory()
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(
            "iris-python-tooling-contract-commonization-v1",
            receipt["schema_version"],
        )
        self.assertEqual(inventory["counts"], receipt["inventory_counts"])
        self.assertEqual(
            inventory["denominator_sha256"], receipt["denominator_sha256"]
        )
        self.assertEqual([], receipt["adopted_consumers"])
        self.assertEqual("complete/no-op", receipt["disposition"])
        self.assertEqual("not_applicable", receipt["adopted_parity_validation"])
        self.assertEqual([], inventory["denominator"]["exact_current_groups"])

    def test_adopted_consumers_preserve_cli_and_output_contract(self) -> None:
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        if not receipt["adopted_consumers"]:
            self.skipTest("not_applicable: decision receipt adopted zero consumers")
        self.fail("receipt declares adopted consumers without parity fixtures")


if __name__ == "__main__":
    unittest.main()
