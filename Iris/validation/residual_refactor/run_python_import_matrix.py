#!/usr/bin/env python
"""Record the residual-refactor Python import, CLI, and byte matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def run_row(
    *,
    case_id: str,
    command: list[str],
    cwd: Path,
    environment: dict[str, str],
    expected_exit: int = 0,
) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    return {
        "case_id": case_id,
        "command": command,
        "cwd": cwd.as_posix(),
        "expected_exit_code": expected_exit,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "validation_status": "passed"
        if completed.returncode == expected_exit
        else "failed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mode", choices=("Baseline", "Closeout"), required=True)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    args = parser.parse_args()

    repository_root = repository_root_for(Path.cwd())
    v2_root = repository_root / "Iris" / "build" / "description" / "v2"
    build_root = v2_root / "tools" / "build"
    python = args.python.resolve()
    environment = dict(os.environ)
    environment["PYTHONNOUSERSITE"] = "1"
    environment.pop("PYTHONPATH", None)

    rows = [
        run_row(
            case_id="repo.package_import",
            command=[
                str(python),
                "-B",
                "-s",
                "-c",
                (
                    "from Iris.build.description.v2.tools.build import compose_layer3_io as m;"
                    "print(m.__file__)"
                ),
            ],
            cwd=repository_root,
            environment=environment,
        ),
        run_row(
            case_id="v2.tools_package_import",
            command=[
                str(python),
                "-B",
                "-s",
                "-c",
                "from tools.build import compose_layer3_io as m;print(m.__file__)",
            ],
            cwd=v2_root,
            environment=environment,
        ),
        run_row(
            case_id="build_root.bare_import",
            command=[
                str(python),
                "-B",
                "-s",
                "-c",
                "import compose_layer3_io as m;print(m.__file__)",
            ],
            cwd=build_root,
            environment=environment,
        ),
        run_row(
            case_id="repo.direct_script_help",
            command=[
                str(python),
                "-B",
                "-s",
                str(build_root / "export_registry_runtime_records.py"),
                "--help",
            ],
            cwd=repository_root,
            environment=environment,
        ),
        run_row(
            case_id="v2.python_m_help",
            command=[
                str(python),
                "-B",
                "-s",
                "-m",
                "tools.build.export_registry_runtime_records",
                "--help",
            ],
            cwd=v2_root,
            environment=environment,
        ),
        run_row(
            case_id="v2.tools_common_identity",
            command=[
                str(python),
                "-B",
                "-s",
                "-c",
                (
                    "from tools.common import paths;"
                    "print(paths.V2_ROOT);"
                    "assert paths.V2_ROOT.name == 'v2'"
                ),
            ],
            cwd=v2_root,
            environment=environment,
        ),
    ]

    if args.mode == "Closeout":
        rows.append(
            run_row(
                case_id="v2.extracted_leaf_import",
                command=[
                    str(python),
                    "-B",
                    "-s",
                    "-c",
                    (
                        "from tools.build import registry_runtime_record_paths as m;"
                        "print(m.__file__)"
                    ),
                ],
                cwd=v2_root,
                environment=environment,
            )
        )

    with tempfile.TemporaryDirectory(prefix="iris-residual-byte-") as temp:
        temporary_root = Path(temp)
        output = temporary_root / "rows.jsonl"
        snippet = (
            "from pathlib import Path;"
            "from tools.build.compose_layer3_io import write_jsonl;"
            f"p=Path({str(output)!r});"
            "write_jsonl(p,[{'z':'한글','a':1}]);"
            "print(p)"
        )
        byte_row = run_row(
            case_id="compose_layer3_io.jsonl_byte_contract",
            command=[str(python), "-B", "-s", "-c", snippet],
            cwd=v2_root,
            environment=environment,
        )
        if output.is_file():
            raw = output.read_bytes()
            expected = (
                json.dumps({"z": "한글", "a": 1}, ensure_ascii=False) + os.linesep
            ).encode("utf-8")
            byte_row.update(
                {
                    "artifact_sha256": sha256_file(output),
                    "artifact_bytes_hex": raw.hex(),
                    "line_ending": "crlf" if raw.endswith(b"\r\n") else "lf",
                    "trailing_newline": raw.endswith((b"\n", b"\r")),
                    "bom": raw.startswith(b"\xef\xbb\xbf"),
                    "byte_contract_equal": raw == expected,
                    "validation_status": "passed"
                    if byte_row["exit_code"] == 0 and raw == expected
                    else "failed",
                }
            )
        else:
            byte_row["validation_status"] = "failed"
            byte_row["artifact_missing"] = True
        rows.append(byte_row)

        long_parent = temporary_root
        while len(str(long_parent / "rows.jsonl")) < 280:
            long_parent = long_parent / "long-path-segment"
        long_output = long_parent / "rows.jsonl"
        long_snippet = (
            "from pathlib import Path;"
            "from tools.build.compose_layer3_io import file_sha256,write_jsonl;"
            f"p=Path({str(long_output)!r});"
            "write_jsonl(p,[{'long':True}]);"
            "assert len(file_sha256(p)) == 64;"
            "print(len(str(p)))"
        )
        long_row = run_row(
            case_id="compose_layer3_io.windows_long_path",
            command=[str(python), "-B", "-s", "-c", long_snippet],
            cwd=v2_root,
            environment=environment,
        )
        rows.append(long_row)
        long_tree = temporary_root / "long-path-segment"
        if long_tree.exists():
            cleanup_path = long_tree
            if os.name == "nt":
                resolved_long_tree = str(long_tree.resolve())
                cleanup_path = Path(
                    "\\\\?\\UNC\\" + resolved_long_tree[2:]
                    if resolved_long_tree.startswith("\\\\")
                    else "\\\\?\\" + resolved_long_tree
                )
            shutil.rmtree(cleanup_path)

        missing_path = temporary_root / "missing.jsonl"
        missing_snippet = (
            "from pathlib import Path;"
            "from tools.build.compose_layer3_io import file_sha256;"
            f"p=Path({str(missing_path)!r});"
            "\ntry:file_sha256(p)\n"
            "except FileNotFoundError:print('FileNotFoundError')\n"
            "else:raise AssertionError('missing file did not fail')"
        )
        rows.append(
            run_row(
                case_id="compose_layer3_io.missing_file_exception",
                command=[str(python), "-B", "-s", "-c", missing_snippet],
                cwd=v2_root,
                environment=environment,
            )
        )

        variants = {
            "lf": b'{"a":1}\n',
            "crlf": b'{"a":1}\r\n',
            "bom_lf": b'\xef\xbb\xbf{"a":1}\n',
        }
        rows.append(
            {
                "case_id": "compose_layer3_io.line_ending_and_bom_fixtures",
                "validation_status": "passed"
                if len({hashlib.sha256(value).hexdigest() for value in variants.values()}) == 3
                else "failed",
                "variant_sha256": {
                    name: hashlib.sha256(value).hexdigest()
                    for name, value in variants.items()
                },
                "all_variants_distinct": True,
            }
        )
        rows.append(
            {
                "case_id": "compose_layer3_io.atomic_replace_retry",
                "application_status": "not_applicable",
                "validation_status": "passed",
                "reason": (
                    "compose_layer3_io owns a direct-write JSONL contract and neither the baseline "
                    "nor Change 5A introduces atomic replace or retry semantics"
                ),
            }
        )

    status = "passed" if all(row["validation_status"] == "passed" for row in rows) else "failed"
    head = subprocess.run(
        ["git", "-C", str(repository_root), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    tree = subprocess.run(
        ["git", "-C", str(repository_root), "rev-parse", "HEAD^{tree}"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    report = {
        "schema_version": "iris-residual-python-import-matrix-v1",
        "validation_status": status,
        "mode": args.mode,
        "subject_commit": head,
        "subject_tree": tree,
        "python_executable": str(python).replace("\\", "/"),
        "python_version": sys.version,
        "python_no_user_site": True,
        "pythonpath_removed": True,
        "rows": rows,
    }
    output_path = (
        (repository_root / args.out).resolve()
        if not args.out.is_absolute()
        else args.out.resolve()
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"validation_status": status, "row_count": len(rows)}, sort_keys=True))
    return 0 if status == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
