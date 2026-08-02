#!/usr/bin/env python
"""Write the residual manual-validation report without inventing runtime UI evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--subject-commit", required=True)
    parser.add_argument("--subject-tree", required=True)
    parser.add_argument("--tested-package-sha256", required=True)
    parser.add_argument("--operator-command-json", required=True)
    parser.add_argument("--operator-exit-code", type=int, required=True)
    parser.add_argument("--operator-evidence", type=Path, required=True)
    parser.add_argument("--operator-status", choices=("passed", "failed"), required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    repository_root = args.repository_root.resolve()
    command = json.loads(args.operator_command_json)
    evidence = (
        (repository_root / args.operator_evidence).resolve()
        if not args.operator_evidence.is_absolute()
        else args.operator_evidence.resolve()
    )
    runtime_cases = []
    blocked_reason = (
        "Project Zomboid interactive runtime, locale switching, screenshot capture, and a human "
        "runtime reviewer were unavailable during the unattended implementation window"
    )
    for case_id, expected in (
        ("runtime_ui.browser_determinism", "category order, search, folded count, representative, and recipe display match baseline"),
        ("runtime_ui.copy_on_read", "repeated Browser and Detail navigation cannot mutate frozen public data"),
        ("runtime_ui.wiki_units", "EN and KO food/core values preserve their percent-scaled and raw profiles"),
        ("runtime_ui.tooltip", "Alt Tooltip preserves 3/4-line success and 2-line failure branches after locale changes"),
        ("runtime_ui.logging", "debug-off play emits no debug-only work while warnings and errors remain visible"),
    ):
        runtime_cases.append(
            {
                "case_id": case_id,
                "case_class": "runtime_ui",
                "tested_package_sha256": args.tested_package_sha256,
                "project_zomboid_build": "not_observed",
                "iris_version": f"subject-{args.subject_commit[:12]}",
                "os": platform.platform(),
                "locale": "not_observed",
                "expected": expected,
                "observed": "not executed",
                "status": "blocked",
                "blocked_reason": blocked_reason,
            }
        )
    operator_case = {
        "case_id": "operator_contract.clean_checkout_full_gate",
        "case_class": "operator_contract",
        "os": platform.platform(),
        "shell": "PowerShell",
        "python_or_tool_version": sys.version,
        "command": command,
        "exit_code": args.operator_exit_code,
        "evidence": {
            "kind": "artifact",
            "path": evidence.relative_to(repository_root).as_posix(),
            "sha256": sha256_file(evidence),
        },
        "expected": {"exit_code": 0, "exact_committed_subject": True, "clean_checkout": True},
        "observed": {"exit_code": args.operator_exit_code, "status": args.operator_status},
        "status": args.operator_status,
    }
    payload = {
        "schema_version": "iris-residual-manual-runtime-validation-v1",
        "validation_status": "blocked" if args.operator_status == "passed" else "failed",
        "binding": {
            "subject_commit": args.subject_commit,
            "subject_tree": args.subject_tree,
            "reviewer": args.reviewer,
            "tested_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        },
        "class_summaries": {
            "runtime_ui": {"validation_status": "blocked", "case_count": len(runtime_cases)},
            "operator_contract": {"validation_status": args.operator_status, "case_count": 1},
        },
        "cases": [*runtime_cases, operator_case],
    }
    output = (repository_root / args.out).resolve() if not args.out.is_absolute() else args.out.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"validation_status": payload["validation_status"], "case_count": len(payload["cases"])}, sort_keys=True))
    return 0 if args.operator_status == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
