#!/usr/bin/env python
"""Collect unittest test-case identities for Iris Round 3 evidence."""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path
from types import ModuleType
from typing import Iterable


def _iter_cases(suite: unittest.TestSuite) -> Iterable[unittest.TestCase]:
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _iter_cases(item)
        else:
            yield item


def _module_source(module_name: str, start: Path) -> str | None:
    module: ModuleType | None = sys.modules.get(module_name)
    file_name = getattr(module, "__file__", None) if module is not None else None
    if file_name:
        return str(Path(file_name).resolve())

    leaf = module_name.rsplit(".", 1)[-1]
    candidate = start / f"{leaf}.py"
    if candidate.exists():
        return str(candidate.resolve())
    return None


def collect_identities(start: Path, pattern: str, top_level: Path | None = None) -> dict:
    start = start.resolve()
    loader = unittest.TestLoader()
    if top_level is None:
        suite = loader.discover(str(start), pattern=pattern)
    else:
        suite = loader.discover(str(start), pattern=pattern, top_level_dir=str(top_level.resolve()))

    rows = []
    for case in _iter_cases(suite):
        test_id = case.id()
        cls = case.__class__
        module_name = cls.__module__
        class_name = cls.__qualname__
        method_name = getattr(case, "_testMethodName", None)
        collect_error = module_name == "unittest.loader" and class_name == "_FailedTest"
        if collect_error:
            failed_name = test_id.rsplit(".", 1)[-1]
            source_file = str((start / f"{failed_name}.py").resolve())
        else:
            source_file = _module_source(module_name, start)
        rows.append(
            {
                "test_id": test_id,
                "source_file": source_file,
                "module": module_name,
                "class": class_name,
                "method": method_name,
                "collect_error": collect_error,
                "status": "non_collectable" if collect_error else "collected",
            }
        )

    rows.sort(key=lambda row: row["test_id"])
    collect_error_count = sum(1 for row in rows if row["collect_error"])
    return {
        "schema_version": "round3-test-identities-v1",
        "collector": "unittest.TestLoader.discover",
        "start": str(start),
        "pattern": pattern,
        "top_level": str(top_level.resolve()) if top_level else None,
        "failed_test_policy": {
            "include_failed_tests": True,
            "cross_check_rule": "identity_count == tests_run when _FailedTest entries are included",
        },
        "identity_count": len(rows),
        "collect_error_count": collect_error_count,
        "identities": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="Iris/build/description/v2/tests")
    parser.add_argument("--pattern", default="test_*.py")
    parser.add_argument("--top-level")
    parser.add_argument("--out")
    args = parser.parse_args()

    payload = collect_identities(
        Path(args.start),
        args.pattern,
        Path(args.top_level) if args.top_level else None,
    )
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
