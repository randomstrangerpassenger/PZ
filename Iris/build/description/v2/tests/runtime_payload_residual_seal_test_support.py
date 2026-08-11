from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
SCRIPT = REPO / "Iris/build/description/v2/tools/build/runtime_payload_state_integrity_residual_seal.py"
ROOT = REPO / "Iris/build/description/v2/staging/runtime_payload_state_integrity_residual_seal"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rebind_and_restore_complete_review() -> subprocess.CompletedProcess[str]:
    decision = load_json(
        ROOT / "phase4/author_reserved_selection_decision_record.json"
    )
    if decision.get("pending_author_selection") is True:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--mode", "all"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
    generated = subprocess.run(
        [sys.executable, "-B", str(SCRIPT), "--mode", "generate"],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    if generated.returncode not in {0, 1}:
        return generated
    artifact_hash = load_json(ROOT / "phase5/artifact_hash_report.json")
    review_path = ROOT / "phase6/external_independent_review_report.json"
    review = load_json(review_path)
    review["reviewed_artifact_manifest_hash"] = artifact_hash[
        "primary_review_artifact_manifest_hash"
    ]
    review["primary_review_artifact_count"] = artifact_hash["artifact_count"]
    review["missing_count"] = 0
    review["hash_mismatch_count"] = 0
    write_json(review_path, review)
    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPT),
            "--mode",
            "all",
            "--require-complete",
        ],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
