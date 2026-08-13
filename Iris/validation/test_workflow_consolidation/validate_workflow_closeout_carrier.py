from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    from ._common import ContractError, git, read_json, require, sha256_file, write_json
except ImportError:
    from _common import ContractError, git, read_json, require, sha256_file, write_json


ALLOWED_GOVERNANCE = {"docs/DECISIONS.md", "docs/ROADMAP.md"}
FORBIDDEN_PREFIXES = (
    "Iris/build/description/v2/tests/",
    "Iris/media/lua/",
    "Iris/_docs/round3/",
    "Iris/validation/test_workflow_consolidation/",
)


def carrier_changed_paths(repository: Path, terminal: str, carrier: str) -> list[str]:
    return sorted(
        line.replace("\\", "/")
        for line in git(repository, "diff", "--name-only", terminal, carrier).splitlines()
        if line
    )


def validate_carrier(
    repository: Path,
    terminal: str,
    pointer: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    carrier = git(repository, "rev-parse", "HEAD")
    parent_line = git(repository, "rev-list", "--parents", "-n", "1", carrier).split()
    single_parent = len(parent_line) == 2 and parent_line[1] == terminal
    entries = manifest.get("entries", [])
    allowed = {row.get("path") for row in entries if isinstance(row, dict)}
    manifest_path = "Iris/_docs/refactor/test_workflow_consolidation/workflow_closeout_carrier_manifest.json"
    pointer_path = "Iris/_docs/refactor/test_workflow_consolidation/terminal_evidence_pointer.json"
    allowed.update({manifest_path, pointer_path})
    changed = carrier_changed_paths(repository, terminal, carrier)
    forbidden = [path for path in changed if path.startswith(FORBIDDEN_PREFIXES)]
    forbidden = [path for path in forbidden if path not in {manifest_path, pointer_path} and path not in allowed]
    out_of_scope = [path for path in changed if path not in allowed and path not in ALLOWED_GOVERNANCE]
    non_self_reference = all(
        key not in pointer
        for key in ("carrier_commit", "carrier_tree", "carrier_manifest_sha256")
    )
    checks = {
        "single_parent_is_terminal": single_parent,
        "ancestry_distance_one": single_parent,
        "changed_paths_allowlisted": not out_of_scope,
        "no_code_test_config_or_authority_delta": not forbidden,
        "pointer_non_self_referential": non_self_reference,
        "manifest_schema_match": manifest.get("schema_version") == "iris_test_workflow_closeout_carrier_manifest_v1",
        "pointer_schema_match": pointer.get("schema_version") == "iris_test_workflow_terminal_evidence_pointer_v1",
    }
    return {
        "schema_version": "iris_test_workflow_closeout_carrier_validation_v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "terminal_commit": terminal,
        "carrier_commit": carrier,
        "checks": checks,
        "changed_paths": changed,
        "out_of_scope_paths": out_of_scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Iris workflow closeout carrier")
    parser.add_argument("--carrier-repository", type=Path, required=True)
    parser.add_argument("--terminal", required=True)
    parser.add_argument("--pointer", type=Path, required=True)
    parser.add_argument("--carrier-manifest", type=Path, required=True)
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--fresh-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate_carrier(
        args.carrier_repository.resolve(),
        args.terminal,
        read_json(args.pointer),
        read_json(args.carrier_manifest),
    )
    report["archive_root"] = str(args.archive_root.resolve())
    report["fresh_root"] = str(args.fresh_root.resolve())
    write_json(args.output, report)
    require(report["status"] == "PASS", "workflow closeout carrier validation failed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
