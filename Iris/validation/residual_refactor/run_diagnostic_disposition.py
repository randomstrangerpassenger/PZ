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
SUCCESSOR_OUTPUT_POLICY = Path(
    "Iris/validation/clean_checkout/contracts/repository_runtime_lightweighting_output_policy.json"
)


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


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def path_descriptor(path: Path, repository_root: Path, *, role: str) -> dict[str, Any]:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(repository_root.resolve()).as_posix()
    except ValueError:
        return {
            "kind": "external_absolute",
            "role": role,
            "path": resolved.as_posix(),
            "exists": resolved.exists(),
            "sha256": sha256_file(resolved),
        }
    return {
        "kind": "repository_relative",
        "role": role,
        "path": relative,
        "exists": resolved.exists(),
        "sha256": sha256_file(resolved),
    }


def write_bytes_new(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if path.exists() or temporary.exists():
        raise FileExistsError(f"diagnostic output already exists: {path}")
    temporary.write_bytes(payload)
    try:
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def require_external_new_sink(path: Path, repository_root: Path, *, role: str) -> Path:
    lexical = Path(os.path.abspath(os.fspath(path)))
    repository = repository_root.resolve()
    cursor = lexical.parent
    while True:
        attributes = int(getattr(cursor.lstat(), "st_file_attributes", 0))
        if cursor.is_symlink() or bool(attributes & 0x400):
            raise ValueError(f"{role} has a symlink/reparse ancestor: {cursor}")
        parent = cursor.parent
        if parent == cursor:
            break
        cursor = parent
    resolved = lexical.resolve(strict=False)
    if resolved == repository or repository in resolved.parents:
        raise ValueError(f"{role} must be outside the source checkout: {resolved}")
    if lexical.exists() or resolved.exists():
        raise FileExistsError(f"{role} already exists: {lexical}")
    if not lexical.parent.is_dir() or not resolved.parent.is_dir():
        raise ValueError(f"{role} parent must be a pre-allocated directory: {lexical.parent}")
    return resolved


def successor_policy_adoption(repository_root: Path) -> tuple[bool, str, Path, dict[str, Any] | None]:
    policy_path = (repository_root.resolve() / SUCCESSOR_OUTPUT_POLICY).resolve()
    if not policy_path.is_file():
        return False, "planned_change_not_adopted", policy_path, None
    try:
        policy = load_json(policy_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return False, "successor_policy_unreadable", policy_path, None
    adopted = bool(
        policy.get("schema_version") == "iris_repository_runtime_lightweighting_output_policy_v1"
        and policy.get("approval", {}).get("approved") is True
        and policy.get("dangling_reference_allowed") is False
        and policy.get("external_subroots") == ["objects", "phases", "logs", "package"]
    )
    return adopted, ("adopted" if adopted else "planned_change_not_adopted"), policy_path, policy


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
    raw_out = repository_root / args.raw_out if not args.raw_out.is_absolute() else args.raw_out
    dispositions_path = (
        (repository_root / args.dispositions).resolve()
        if not args.dispositions.is_absolute()
        else args.dispositions.resolve()
    )
    output = repository_root / args.out if not args.out.is_absolute() else args.out
    raw_out = require_external_new_sink(raw_out, repository_root, role="diagnostic_raw_output")
    output = require_external_new_sink(output, repository_root, role="diagnostic_disposition_output")
    if (
        raw_out.parent == output.parent
        or raw_out.parent in output.parent.parents
        or output.parent in raw_out.parent.parents
    ):
        raise ValueError("diagnostic raw and disposition outputs require disjoint external subroots")
    output_existed_before = False
    policy_adopted, policy_disposition, policy_path, _policy = successor_policy_adoption(repository_root)
    if not policy_adopted:
        blocked = {
            "schema_version": "iris-residual-diagnostic-disposition-v1",
            "validation_status": "blocked",
            "execution_status": "not_run",
            "finding_status": "not_run",
            "blocking": True,
            "raw_exit_code": None,
            "disposition": policy_disposition,
            "raw_report_path": path_descriptor(
                raw_out, repository_root, role="diagnostic_raw_output"
            ),
            "output_path": {
                **path_descriptor(
                    output, repository_root, role="diagnostic_disposition_output"
                ),
                "exists_before_write": False,
                "write_disposition": "create_new",
            },
            "successor_output_policy": path_descriptor(
                policy_path, repository_root, role="successor_output_policy"
            ),
        }
        blocked_bytes = (json.dumps(blocked, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        )
        write_bytes_new(output, blocked_bytes)
        print(
            json.dumps(
                {
                    "validation_status": "blocked",
                    "blocking": True,
                    "disposition": policy_disposition,
                    "output_path": output.as_posix(),
                    "output_sha256": hashlib.sha256(blocked_bytes).hexdigest(),
                },
                sort_keys=True,
            )
        )
        return 2

    native_command = [
        sys.executable,
        "-B",
        str(runner),
        "--class",
        "diagnostic",
        "--out",
        str(raw_out),
    ]
    completed = subprocess.run(
        native_command,
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
            "command": {
                "executable": path_descriptor(
                    Path(sys.executable), repository_root, role="pinned_python_executable"
                ),
                "argv": [
                    {"kind": "literal", "value": "-B"},
                    {
                        "kind": "path",
                        "value": path_descriptor(
                            runner, repository_root, role="diagnostic_route_runner"
                        ),
                    },
                    {"kind": "literal", "value": "--class"},
                    {"kind": "literal", "value": "diagnostic"},
                    {"kind": "literal", "value": "--out"},
                    {
                        "kind": "path",
                        "value": path_descriptor(
                            raw_out, repository_root, role="diagnostic_raw_output"
                        ),
                    },
                ],
                "working_directory": path_descriptor(
                    repository_root, repository_root, role="source_checkout"
                ),
            },
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "raw_report_path": path_descriptor(
                raw_out, repository_root, role="diagnostic_raw_output"
            ),
            "dispositions_path": path_descriptor(
                dispositions_path,
                repository_root,
                role="owner_disposition_source",
            ),
            "output_path": {
                **path_descriptor(
                    output, repository_root, role="diagnostic_disposition_output"
                ),
                "exists_before_write": output_existed_before,
                "write_disposition": "create_new",
                "identity_binding": "sha256_emitted_after_atomic_write_on_command_stdout",
            },
            "successor_output_policy": path_descriptor(
                policy_path, repository_root, role="successor_output_policy"
            ),
        }
    )
    output_bytes = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    write_bytes_new(output, output_bytes)
    output_sha256 = hashlib.sha256(output_bytes).hexdigest()
    print(
        json.dumps(
            {
                "validation_status": report["validation_status"],
                "raw_exit_code": completed.returncode,
                "blocking": report["blocking"],
                "output_path": output.as_posix(),
                "output_sha256": output_sha256,
            },
            sort_keys=True,
        )
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
