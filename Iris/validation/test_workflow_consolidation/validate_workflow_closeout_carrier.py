from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

try:
    from ._common import (
        ContractError,
        git,
        read_json,
        require,
        require_path_outside_repositories,
        resolve_within,
        sha256_file,
        write_json,
    )
except ImportError:
    from _common import (
        ContractError,
        git,
        read_json,
        require,
        require_path_outside_repositories,
        resolve_within,
        sha256_file,
        write_json,
    )


EVIDENCE_ROOT = "Iris/_docs/refactor/test_workflow_consolidation/"
MANIFEST_PATH = EVIDENCE_ROOT + "workflow_closeout_carrier_manifest.json"
POINTER_PATH = EVIDENCE_ROOT + "terminal_evidence_pointer.json"
ALLOWED_EVIDENCE_ROLES = {
    "terminal_comparison",
    "accepted_paired_measurement_summary",
    "accepted_session_schedule",
    "accepted_session_resource_estimate",
    "measurement_comparability_report",
    "cost_denominator_manifest",
    "terminal_validation_manifest",
    "terminal_source_policy_revalidation_report",
    "independent_review",
    "owner_seal",
}
REQUIRED_ARTIFACT_PATHS = {
    EVIDENCE_ROOT + f"{role}.json": role for role in ALLOWED_EVIDENCE_ROLES
}
REQUIRED_MANIFEST_ENTRIES = {
    **REQUIRED_ARTIFACT_PATHS,
    POINTER_PATH: "terminal_evidence_pointer",
}
ALLOWED_GOVERNANCE = {
    "docs/DECISIONS.md": "evidence_governance",
    "docs/ROADMAP.md": "evidence_governance",
}
REPLAY_FILES = (
    "terminal_validation_manifest.json",
    "accepted_paired_measurement_summary.json",
    "measurement_comparability_report.json",
    "independent_review.json",
    "owner_seal.json",
)
FORBIDDEN_PREFIXES = (
    "Iris/build/description/v2/tests/",
    "Iris/media/lua/",
    "Iris/_docs/round3/",
    "Iris/validation/",
)


def carrier_changed_paths(repository: Path, terminal: str, carrier: str) -> list[str]:
    return sorted(
        line.replace("\\", "/")
        for line in git(repository, "diff", "--name-only", terminal, carrier).splitlines()
        if line
    )


def _entry_map(entries: object) -> dict[str, dict[str, Any]] | None:
    if not isinstance(entries, list):
        return None
    rows: dict[str, dict[str, Any]] = {}
    for row in entries:
        if not isinstance(row, dict):
            return None
        path = row.get("path")
        if not isinstance(path, str) or not path or path in rows:
            return None
        rows[path] = row
    return rows


def _committed_blob_matches(
    repository: Path, carrier: str, path: str, expected_blob: object
) -> bool:
    if not isinstance(expected_blob, str) or not expected_blob:
        return False
    try:
        return git(repository, "rev-parse", f"{carrier}:{path}") == expected_blob
    except ContractError:
        return False


def validate_carrier(
    repository: Path,
    terminal: str,
    pointer: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    terminal_commit = git(repository, "rev-parse", terminal)
    carrier = git(repository, "rev-parse", "HEAD")
    parent_line = git(repository, "rev-list", "--parents", "-n", "1", carrier).split()
    single_parent = len(parent_line) == 2 and parent_line[1] == terminal_commit
    changed = carrier_changed_paths(repository, terminal_commit, carrier)
    entries = _entry_map(manifest.get("entries"))
    entries_valid = entries is not None
    entries = entries or {}
    allowed_paths = set(REQUIRED_ARTIFACT_PATHS) | set(ALLOWED_GOVERNANCE) | {
        MANIFEST_PATH,
        POINTER_PATH,
    }
    forbidden = [
        path
        for path in changed
        if path.startswith(FORBIDDEN_PREFIXES)
        and path not in REQUIRED_ARTIFACT_PATHS
        and path not in {MANIFEST_PATH, POINTER_PATH}
    ]
    out_of_scope = sorted(set(changed) - allowed_paths)
    required_present = (set(REQUIRED_MANIFEST_ENTRIES) | {MANIFEST_PATH}) <= set(
        changed
    )
    entries_match_schema = entries_valid and set(entries) == (
        set(REQUIRED_MANIFEST_ENTRIES)
        | set(ALLOWED_GOVERNANCE).intersection(changed)
    )
    entry_roles_match = entries_match_schema and all(
        row.get("role")
        == (REQUIRED_MANIFEST_ENTRIES | ALLOWED_GOVERNANCE)[path]
        for path, row in entries.items()
    )
    entry_blobs_match = entries_match_schema and all(
        _committed_blob_matches(repository, carrier, path, row.get("git_blob_id"))
        for path, row in entries.items()
    )
    non_self_reference = all(
        key not in pointer
        for key in ("carrier_commit", "carrier_tree", "carrier_manifest_sha256")
    )
    pointer_subject_bound = (
        pointer.get("terminal_subject_commit") == terminal_commit
        and pointer.get("terminal_subject_tree")
        == git(repository, "rev-parse", f"{terminal_commit}^{{tree}}")
        and pointer.get("retrieval_mode") == "fresh-root-terminal-replay-v1"
        and isinstance(pointer.get("external_retrieval_key"), str)
        and bool(pointer.get("external_retrieval_key"))
        and pointer.get("expected_terminal_filenames") == list(REPLAY_FILES)
    )
    checks = {
        "single_parent_is_terminal": single_parent,
        "ancestry_distance_one": single_parent,
        "changed_paths_match_closed_schema": not out_of_scope and required_present,
        "no_code_test_config_or_authority_delta": not forbidden,
        "manifest_entries_match_closed_path_role_schema": entries_match_schema
        and entry_roles_match,
        "manifest_entries_bind_committed_blobs": entry_blobs_match,
        "pointer_non_self_referential": non_self_reference,
        "pointer_binds_terminal_and_retrieval_contract": pointer_subject_bound,
        "manifest_schema_match": manifest.get("schema_version")
        == "iris_test_workflow_closeout_carrier_manifest_v1",
        "pointer_schema_match": pointer.get("schema_version")
        == "iris_test_workflow_terminal_evidence_pointer_v1",
    }
    return {
        "schema_version": "iris_test_workflow_closeout_carrier_validation_v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "terminal_commit": terminal_commit,
        "carrier_commit": carrier,
        "checks": checks,
        "changed_paths": changed,
        "out_of_scope_paths": out_of_scope,
        "forbidden_paths": forbidden,
    }


def retrieve_and_replay(
    repository: Path,
    terminal: str,
    pointer: dict[str, Any],
    archive_root: Path,
    fresh_root: Path,
) -> dict[str, Any]:
    terminal_commit = git(repository, "rev-parse", terminal)
    require(pointer.get("terminal_subject_commit") == terminal_commit, "pointer terminal commit mismatch")
    require(
        pointer.get("terminal_subject_tree")
        == git(repository, "rev-parse", f"{terminal_commit}^{{tree}}"),
        "pointer terminal tree mismatch",
    )
    require(archive_root.is_dir(), "durable archive root is missing")
    require(fresh_root.is_dir() and not any(fresh_root.iterdir()), "fresh root must exist and be empty")
    require(archive_root.resolve() != fresh_root.resolve(), "archive and fresh roots must be disjoint")
    require(
        archive_root.resolve() not in fresh_root.resolve().parents
        and fresh_root.resolve() not in archive_root.resolve().parents,
        "archive and fresh roots must not contain one another",
    )
    retrieval_key = pointer.get("external_retrieval_key")
    require(isinstance(retrieval_key, str) and retrieval_key, "external retrieval key is missing")
    bundle_root = resolve_within(archive_root, retrieval_key)
    require(bundle_root.is_dir(), "durable bundle is missing")
    expected_hashes = pointer.get("artifact_sha256")
    require(
        isinstance(expected_hashes, dict) and set(expected_hashes) == set(REPLAY_FILES),
        "pointer replay artifact identity is incomplete",
    )
    retrieved = fresh_root / "retrieved"
    retrieved.mkdir()
    terminal_checkout = fresh_root / "terminal-subject"
    git(
        repository,
        "worktree",
        "add",
        "--detach",
        str(terminal_checkout),
        terminal_commit,
    )
    require(
        git(terminal_checkout, "rev-parse", "HEAD") == terminal_commit,
        "fresh terminal checkout commit mismatch",
    )
    require(
        git(terminal_checkout, "rev-parse", "HEAD^{tree}")
        == pointer["terminal_subject_tree"],
        "fresh terminal checkout tree mismatch",
    )
    require(not git(terminal_checkout, "status", "--short"), "fresh terminal checkout is dirty")
    for name in REPLAY_FILES:
        source = resolve_within(bundle_root, name)
        require(source.is_file(), f"durable artifact is missing: {name}")
        require(sha256_file(source) == expected_hashes[name], f"durable artifact identity mismatch: {name}")
        destination = retrieved / name
        shutil.copyfile(source, destination)
        require(sha256_file(destination) == expected_hashes[name], f"retrieved artifact identity mismatch: {name}")
    artifacts = {name: read_json(retrieved / name) for name in REPLAY_FILES}
    require(
        all(artifact.get("terminal_subject_commit") == terminal_commit for artifact in artifacts.values()),
        "retrieved artifact terminal commit mismatch",
    )
    require(
        all(artifact.get("terminal_subject_tree") == pointer["terminal_subject_tree"] for artifact in artifacts.values()),
        "retrieved artifact terminal tree mismatch",
    )
    require(
        artifacts["terminal_validation_manifest.json"].get("status") == "PASS",
        "terminal validation replay is not PASS",
    )
    require(
        artifacts["accepted_paired_measurement_summary.json"].get("status") == "PASS",
        "accepted paired measurement replay is not PASS",
    )
    require(
        artifacts["measurement_comparability_report.json"].get("comparability_verdict")
        == "PASS",
        "measurement comparability replay is not PASS",
    )
    require(
        artifacts["independent_review.json"].get("verdict") == "PASS",
        "independent review replay is not PASS",
    )
    require(
        artifacts["independent_review.json"].get("findings_by_priority")
        == {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
        "independent review replay contains findings",
    )
    require(
        artifacts["owner_seal.json"].get("owner_seal") == "granted",
        "owner seal replay is not granted",
    )
    owner_seal = artifacts["owner_seal.json"]
    for name in REPLAY_FILES[:-1]:
        binding_key = name.removesuffix(".json") + "_sha256"
        require(
            owner_seal.get(binding_key) == expected_hashes[name],
            f"owner seal does not bind {name}",
        )
    return {
        "schema_version": "iris_test_workflow_terminal_retrieval_replay_v1",
        "status": "PASS",
        "terminal_subject_commit": terminal_commit,
        "terminal_subject_tree": pointer["terminal_subject_tree"],
        "fresh_root_retrieval_verified": True,
        "exact_terminal_subject_materialized_and_evidence_replayed": True,
        "retrieved_artifact_count": len(REPLAY_FILES),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Iris workflow closeout carrier")
    parser.add_argument("--carrier-repository", type=Path, required=True)
    parser.add_argument("--terminal", required=True)
    parser.add_argument("--pointer", type=Path, required=True)
    parser.add_argument("--carrier-manifest", type=Path, required=True)
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--fresh-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repository = args.carrier_repository.resolve()
    archive_root = require_path_outside_repositories(
        args.archive_root, [repository], label="archive root"
    )
    fresh_root = require_path_outside_repositories(
        args.fresh_root, [repository], label="fresh root"
    )
    output = require_path_outside_repositories(
        args.output, [repository], label="retrieval report"
    )
    require(not output.exists(), "retrieval report is append-only")
    pointer = read_json(args.pointer)
    report = validate_carrier(
        repository,
        args.terminal,
        pointer,
        read_json(args.carrier_manifest),
    )
    require(report["status"] == "PASS", "closeout carrier validation failed")
    report["retrieval_replay"] = retrieve_and_replay(
        repository,
        args.terminal,
        pointer,
        archive_root,
        fresh_root,
    )
    report["archive_root"] = str(archive_root)
    report["fresh_root"] = str(fresh_root)
    write_json(output, report)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
