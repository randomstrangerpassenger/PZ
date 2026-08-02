from __future__ import annotations

import hashlib
import json
import re
import subprocess
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

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def _git(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, (
        f"git identity command failed: git {' '.join(arguments)}\n"
        f"{completed.stdout}{completed.stderr}"
    )
    return completed.stdout.strip()


def _verify_commit_tree(repo: Path, commit: Any, tree: Any, label: str) -> None:
    assert isinstance(commit, str) and COMMIT_PATTERN.fullmatch(commit), f"invalid {label} commit"
    assert isinstance(tree, str) and COMMIT_PATTERN.fullmatch(tree), f"invalid {label} tree"
    assert _git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}") == commit
    assert _git(repo, "show", "-s", "--format=%T", commit) == tree, f"{label} commit/tree mismatch"


def _verify_optional_sha256(value: Any, label: str) -> None:
    assert value is None or (isinstance(value, str) and SHA256_PATTERN.fullmatch(value)), (
        f"invalid {label} SHA-256"
    )


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
    _verify_commit_tree(repo, binding["subject_commit"], binding["subject_tree"], "subject")
    _verify_commit_tree(repo, binding["producer_base_commit"], binding["producer_base_tree"], "producer")
    _verify_optional_sha256(binding["subject_worktree_patch_sha256_or_null"], "subject patch")
    _verify_optional_sha256(binding["producer_overlay_sha256_or_null"], "producer overlay")
    if "producer_overlay_rows" in binding:
        overlay_rows = binding["producer_overlay_rows"]
        assert isinstance(overlay_rows, list) and all(isinstance(row, str) for row in overlay_rows)
        assert overlay_rows == sorted(overlay_rows), "producer overlay rows are not ordinal sorted"
        canonical_overlay = ("\n".join(overlay_rows) + "\n").encode() if overlay_rows else b""
        reconstructed = hashlib.sha256(canonical_overlay).hexdigest() if overlay_rows else None
        assert reconstructed == binding["producer_overlay_sha256_or_null"]
        if overlay_rows:
            assert binding["producer_worktree_state"] in {"tracked_overlay", "tracked_and_untracked_overlay"}
        else:
            assert binding["producer_worktree_state"] == "clean"
        assert isinstance(binding.get("producer_input_scope"), list) and binding["producer_input_scope"]
    rows = [json.loads(line) for line in evidence_bytes.decode("utf-8").splitlines() if line]
    assert rows, f"empty evidence: {relative_path}"
    assert binding["row_count"] == len(rows)
    case_ids: set[str] = set()
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
        assert row["subject_worktree_patch_sha256_or_null"] == binding["subject_worktree_patch_sha256_or_null"]
        assert row["producer_overlay_sha256_or_null"] == binding["producer_overlay_sha256_or_null"]
        if "producer_worktree_state" in binding:
            assert row["producer_worktree_state"] == binding["producer_worktree_state"]
        assert isinstance(row["fixture_id"], str) and row["fixture_id"], f"{row['case_id']} missing fixture identity"
        assert row["expected"] is not None, f"{row['case_id']} missing expected fixture contract"
        assert row["case_id"] not in case_ids, f"duplicate evidence case: {row['case_id']}"
        case_ids.add(row["case_id"])
        producer_state = row["producer_worktree_state"]
        assert producer_state in {"clean", "tracked_overlay", "tracked_and_untracked_overlay"}
        if producer_state == "clean":
            assert row["producer_overlay_sha256_or_null"] is None
        else:
            assert row["producer_overlay_sha256_or_null"] is not None
    return rows


def require_cases(rows: list[dict[str, Any]], fixtures_by_case: dict[str, str], environment: str) -> None:
    assert rows and all(row["execution_environment"] == environment for row in rows)
    by_id = {row["case_id"]: row for row in rows}
    missing = fixtures_by_case.keys() - by_id.keys()
    assert not missing, f"missing evidence cases for {environment}: {sorted(missing)}"
    for case_id, fixture_id in fixtures_by_case.items():
        row = by_id[case_id]
        assert row["fixture_id"] == fixture_id, f"{case_id}: fixture identity drift"
        assert row["time_axis"] == "pre_refactor_characterization"
        assert row["baseline_denominator_included"] is True
        assert row["status"] == "pass", f"{case_id}: {row['status']}"


def require_case_fixtures(rows: list[dict[str, Any]], fixtures_by_case: dict[str, str]) -> None:
    by_id = {row["case_id"]: row for row in rows}
    assert set(by_id) == set(fixtures_by_case), "evidence case denominator drift"
    for case_id, fixture_id in fixtures_by_case.items():
        assert by_id[case_id]["fixture_id"] == fixture_id, f"{case_id}: fixture identity drift"
