"""Native process execution and pytest result decoding."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from Iris.validation.execution.checkout_environment import CleanCheckoutError


def _load_pytest_result(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "schema_version": "iris-clean-checkout-pytest-result-v1",
            "mode": "unknown",
            "status": "FAIL",
            "pytest_version": None,
            "exit_status": None,
            "identity_rows": [],
            "collection_errors": [
                {
                    "node_id": "",
                    "message": "pytest result plugin did not write its result",
                }
            ],
            "counts": {},
        }
    return json.loads(path.read_text(encoding="utf-8"))


def _run_subprocess(
    command: list[str],
    *,
    cwd: Path,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _raise_process_failure(
    label: str,
    command: list[str],
    completed: subprocess.CompletedProcess[bytes],
) -> None:
    if completed.returncode == 0:
        return
    stdout = completed.stdout.decode("utf-8", errors="replace").strip()
    stderr = completed.stderr.decode("utf-8", errors="replace").strip()
    raise CleanCheckoutError(
        f"{label} failed ({completed.returncode}): {' '.join(command)}"
        f"\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
    )


def _normalized_test_id(node_id: str) -> str:
    parts = node_id.split("::")
    stem = Path(parts[0]).stem
    if len(parts) == 1:
        return stem
    leaf = parts[-1].split("[", 1)[0]
    if len(parts) >= 3:
        parent = parts[-2].split("[", 1)[0]
        return f"{stem}.{parent}.{leaf}"
    return f"{stem}.{leaf}"


def _status_counts(status: str) -> dict[str, int]:
    rows = status.splitlines()
    return {
        "status_row_count": len(rows),
        "tracked_change_count": sum(
            row.startswith(("1 ", "2 ", "u ")) for row in rows
        ),
        "untracked_path_count": sum(row.startswith("? ") for row in rows),
        "ignored_path_count": sum(row.startswith("! ") for row in rows),
    }
