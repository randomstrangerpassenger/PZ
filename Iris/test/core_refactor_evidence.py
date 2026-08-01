from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_ROW_FIELDS = {
    "schema_version",
    "case_id",
    "axis",
    "fixture_id",
    "status",
    "expected",
    "observed",
    "time_axis",
    "owner_change",
    "baseline_denominator_included",
    "subject_commit",
    "subject_tree",
    "subject_worktree_patch_sha256_or_null",
    "producer_base_commit",
    "producer_base_tree",
    "producer_worktree_state",
    "producer_overlay_sha256_or_null",
    "lua_implementation",
    "lua_version",
    "lua_executable_path",
    "lua_version_output",
    "target_runtime_dialect",
    "execution_environment",
    "dialect_sensitive",
    "dialect_reasons",
    "evidence_role",
    "stubbed_dependencies",
}


def repository_root(test_file: str) -> Path:
    candidate = Path(test_file).resolve()
    for parent in candidate.parents:
        if (parent / ".git").exists() and (parent / "Iris").is_dir():
            return parent
    raise AssertionError(f"repository root not found from {test_file}")


def load_bound_evidence(repo: Path, relative_path: str) -> list[dict[str, Any]]:
    evidence_path = repo / relative_path
    binding_path = evidence_path.with_suffix(".binding.json")
    if not evidence_path.is_file():
        raise AssertionError(f"required evidence missing: {relative_path}")
    if not binding_path.is_file():
        raise AssertionError(f"required evidence binding missing: {binding_path}")
    evidence_bytes = evidence_path.read_bytes()
    digest = hashlib.sha256(evidence_bytes).hexdigest()
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    assert binding["schema_version"] == 1
    assert binding["evidence_schema_version"] == 1
    assert binding["evidence_path"] == relative_path.replace("\\", "/")
    assert binding["evidence_sha256"] == digest
    rows = [json.loads(line) for line in evidence_bytes.decode("utf-8").splitlines() if line]
    assert rows, f"empty evidence: {relative_path}"
    assert binding["row_count"] == len(rows)
    for row in rows:
        missing = REQUIRED_ROW_FIELDS - row.keys()
        assert not missing, f"{row.get('case_id')} missing fields: {sorted(missing)}"
        assert row["schema_version"] == 1
        assert row["subject_commit"] == binding["subject_commit"]
        assert row["subject_tree"] == binding["subject_tree"]
        assert row["producer_base_commit"] == binding["producer_base_commit"]
        assert row["producer_base_tree"] == binding["producer_base_tree"]
        assert row["time_axis"] == binding["time_axis"]
        assert row["execution_environment"] == binding["execution_environment"]
    return rows


def require_cases(rows: list[dict[str, Any]], case_ids: set[str], environment: str) -> None:
    assert rows and all(row["execution_environment"] == environment for row in rows)
    by_id = {row["case_id"]: row for row in rows}
    missing = case_ids - by_id.keys()
    assert not missing, f"missing evidence cases for {environment}: {sorted(missing)}"
    for case_id in case_ids:
        row = by_id[case_id]
        assert row["time_axis"] == "pre_refactor_characterization"
        assert row["baseline_denominator_included"] is True
        assert row["status"] == "pass", f"{case_id}: {row['status']}"

