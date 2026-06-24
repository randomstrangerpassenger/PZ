#!/usr/bin/env python
"""Fail if Round 3 current tests import historical/out-of-closure build modules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
ROUND_DIR = REPO / "Iris" / "_docs" / "round3"
DEFAULT_TAXONOMY = ROUND_DIR / "round3_test_taxonomy.json"
DEFAULT_CLOSURE = ROUND_DIR / "round3_active_core_closure.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_violations(taxonomy: dict, allowed_modules: set[str]) -> list[dict]:
    violations = []
    for row in taxonomy["rows"]:
        if row["contract_class"] != "current":
            continue
        out_of_closure = sorted(set(row["imported_build_modules"]) - allowed_modules)
        ignored_imports = sorted(row["imports_ignored_reproduction_modules"])
        if out_of_closure or ignored_imports:
            violations.append(
                {
                    "test_id": row["test_id"],
                    "source_file": row["source_file"],
                    "out_of_closure_modules": out_of_closure,
                    "ignored_reproduction_modules": ignored_imports,
                }
            )
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--taxonomy", default=str(DEFAULT_TAXONOMY))
    parser.add_argument("--closure", default=str(DEFAULT_CLOSURE))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()

    taxonomy = load_json(Path(args.taxonomy))
    closure = load_json(Path(args.closure))
    allowed = set(closure["current_closure_modules"])
    violations = find_violations(taxonomy, allowed)

    synthetic_detected = None
    if args.self_test:
        mutated = json.loads(json.dumps(taxonomy))
        mutated["rows"].append(
            {
                "test_id": "synthetic.CurrentBoundaryViolation.test_blocks_historical_import",
                "source_file": "synthetic/current_violation.py",
                "contract_class": "current",
                "state": "ok",
                "imported_build_modules": ["synthetic_historical_module"],
                "imports_ignored_reproduction_modules": ["synthetic_historical_module"],
            }
        )
        synthetic_detected = bool(find_violations(mutated, allowed))

    payload = {
        "schema_version": "round3-boundary-guard-v1",
        "allowed_current_closure_modules": sorted(allowed),
        "violation_count": len(violations),
        "violations": violations,
        "self_test_enabled": args.self_test,
        "synthetic_violation_detected": synthetic_detected,
        "success": len(violations) == 0 and (synthetic_detected is not False),
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
