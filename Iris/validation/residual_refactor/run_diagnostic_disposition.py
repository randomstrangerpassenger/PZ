#!/usr/bin/env python
"""Run the public diagnostic route and apply exact owner dispositions."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


LOWER_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def repository_root_for(path: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"cannot resolve repository root: {result.stderr.strip()}")
    return Path(result.stdout.strip()).resolve()


def normalized_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").rstrip("/") + "/"


def normalize_traceback(
    text: str,
    *,
    repository_root: Path,
    overlay_roots: list[Path] | None = None,
    temporary_basenames: list[str] | None = None,
) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").replace("\\", "/")
    # Exception reprs escape Windows separators (``C:\\\\path``), while
    # traceback source lines do not.  Canonicalize both forms before replacing
    # repository/overlay prefixes so disposable checkout basenames cannot leak
    # into the fingerprint.
    normalized = re.sub(r"/+", "/", normalized)
    replacements: list[tuple[str, str]] = [(normalized_path(repository_root), "<REPO>/")]
    replacements.extend(
        (normalized_path(path), "<OVERLAY>/") for path in (overlay_roots or [])
    )
    replacements.sort(key=lambda item: len(item[0]), reverse=True)
    for prefix, replacement in replacements:
        normalized = re.sub(re.escape(prefix), replacement, normalized, flags=re.IGNORECASE)
    normalized = re.sub(
        r"(?i)(?:[A-Z]:)?(?:/[^/\r\n\"']+)+/historical-overlay-[^/\r\n\"']+/",
        "<OVERLAY>/",
        normalized,
    )
    for basename in sorted(set(temporary_basenames or []), key=len, reverse=True):
        if basename:
            normalized = normalized.replace(basename.replace("\\", "/"), "<TEMP>")
    return normalized


def traceback_fingerprint(
    text: str,
    *,
    repository_root: Path,
    overlay_roots: list[Path] | None = None,
    temporary_basenames: list[str] | None = None,
) -> str:
    normalized = normalize_traceback(
        text,
        repository_root=repository_root,
        overlay_roots=overlay_roots,
        temporary_basenames=temporary_basenames,
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def finding_rows(raw: dict[str, Any], repository_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for kind in ("failures", "errors"):
        for finding in raw.get(kind, []):
            test_id = str(finding.get("test_id", ""))
            trace = str(finding.get("traceback", ""))
            rows.append(
                {
                    "kind": kind[:-1],
                    "test_id": test_id,
                    "traceback_fingerprint": traceback_fingerprint(
                        trace, repository_root=repository_root
                    ),
                    "exception_type": (
                        trace.strip().splitlines()[-1].split(":", 1)[0]
                        if trace.strip()
                        else ""
                    ),
                }
            )
    return sorted(rows, key=lambda row: (row["test_id"], row["kind"]))


def disposition_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("test_id", "")),
        str(row.get("kind", "")),
        str(row.get("traceback_fingerprint", "")),
    )


def evaluate(
    *,
    raw_exit_code: int,
    raw_report: dict[str, Any] | None,
    dispositions: dict[str, Any],
    repository_root: Path,
) -> tuple[int, dict[str, Any]]:
    expected = dispositions.get("dispositions", [])
    expected_by_key = {disposition_key(row): row for row in expected}
    observed = finding_rows(raw_report or {}, repository_root) if raw_report else []
    observed_by_key = {disposition_key(row): row for row in observed}
    matched = sorted(set(expected_by_key).intersection(observed_by_key))
    unmatched = sorted(set(observed_by_key).difference(expected_by_key))
    stale = sorted(set(expected_by_key).difference(observed_by_key))

    schema_ok = bool(
        isinstance(raw_report, dict)
        and isinstance(raw_report.get("success"), bool)
        and isinstance(raw_report.get("failures", []), list)
        and isinstance(raw_report.get("errors", []), list)
    )
    raw_zero_consistent = raw_exit_code != 0 or bool(
        raw_report and raw_report.get("success") and not observed
    )
    raw_one_consistent = raw_exit_code != 1 or bool(
        raw_report and not raw_report.get("success") and observed
    )
    allowed_exit = raw_exit_code in {0, 1}
    all_dispositions_current = all(
        row.get("owner")
        and row.get("reason")
        and row.get("expiry_readpoint")
        and LOWER_SHA256.fullmatch(str(row.get("traceback_fingerprint", "")))
        for row in expected
    )
    passed = bool(
        schema_ok
        and allowed_exit
        and raw_zero_consistent
        and raw_one_consistent
        and not unmatched
        and not stale
        and all_dispositions_current
    )
    finding_status = (
        "passed"
        if raw_exit_code == 0 and not observed
        else "advisory_failed"
        if passed
        else "unexpected_failed"
    )
    report = {
        "schema_version": "iris-residual-diagnostic-disposition-v1",
        "validation_status": "passed" if passed else "failed",
        "execution_status": "passed" if schema_ok and allowed_exit else "failed",
        "finding_status": finding_status,
        "blocking": not passed,
        "raw_exit_code": raw_exit_code,
        "raw_report_schema_valid": schema_ok,
        "matched_test_ids": sorted({key[0] for key in matched}),
        "unmatched_test_ids": sorted({key[0] for key in unmatched}),
        "stale_disposition_test_ids": sorted({key[0] for key in stale}),
        "observed_findings": observed,
        "disposition_count": len(expected),
    }
    return (0 if passed else 2), report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--raw-out", type=Path, required=True)
    parser.add_argument("--dispositions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    repository_root = repository_root_for(Path.cwd())
    runner = (repository_root / args.runner).resolve() if not args.runner.is_absolute() else args.runner.resolve()
    raw_out = (repository_root / args.raw_out).resolve() if not args.raw_out.is_absolute() else args.raw_out.resolve()
    dispositions_path = (
        (repository_root / args.dispositions).resolve()
        if not args.dispositions.is_absolute()
        else args.dispositions.resolve()
    )
    output = (repository_root / args.out).resolve() if not args.out.is_absolute() else args.out.resolve()
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "-B",
        str(runner),
        "--class",
        "diagnostic",
        "--out",
        str(raw_out),
    ]
    completed = subprocess.run(
        command,
        cwd=repository_root,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONNOUSERSITE": "1"},
    )
    raw_report: dict[str, Any] | None = None
    if raw_out.is_file():
        try:
            raw_report = load_json(raw_out)
        except (OSError, ValueError, json.JSONDecodeError):
            raw_report = None
    dispositions = load_json(dispositions_path)
    exit_code, report = evaluate(
        raw_exit_code=completed.returncode,
        raw_report=raw_report,
        dispositions=dispositions,
        repository_root=repository_root,
    )
    report.update(
        {
            "command": command,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "raw_report_path": raw_out.relative_to(repository_root).as_posix(),
            "dispositions_path": dispositions_path.relative_to(repository_root).as_posix(),
        }
    )
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "validation_status": report["validation_status"],
                "raw_exit_code": completed.returncode,
                "blocking": report["blocking"],
            },
            sort_keys=True,
        )
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
