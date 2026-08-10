#!/usr/bin/env python
"""Execute the ordered, receipt-bound artifact archive/delete lifecycle."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import stat
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

from promote_artifact_lifecycle_evidence import (
    PromotionError,
    validate_baseline_promotion_payload,
    validate_chain as validate_archive_chain,
)
from report_artifact_lifecycle import (
    SCOPED_ROOTS,
    LifecycleError,
    build_rows,
    git_path_set,
    load_lifecycle_reference_policy,
    reference_graph,
)
from repository_evidence_codec import (
    BASELINE_NAME as LIFECYCLE_V2_BASELINE_NAME,
    DELTA_NAME as LIFECYCLE_V2_DELTA_NAME,
    DICTIONARY_NAME as LIFECYCLE_V2_DICTIONARY_NAME,
    MIGRATION_RECEIPT_NAME as LIFECYCLE_V2_RECEIPT_NAME,
    NODES_NAME as LIFECYCLE_V2_NODES_NAME,
    RepositoryEvidenceCodecError,
    materialize_manifest,
    raw_sha256 as evidence_raw_sha256,
)


class LifecycleExecutionError(RuntimeError):
    pass


POST_VALIDATION_ALLOWED_ADDITIONS = {
    "Iris/_docs/refactor/repository_runtime_lightweighting/pre_delete_current_route_receipt.json",
    "Iris/_docs/refactor/repository_runtime_lightweighting/archive_operation_manifest.json",
    "Iris/_docs/refactor/repository_runtime_lightweighting/archive_restore_receipt.json",
    "Iris/_docs/refactor/repository_runtime_lightweighting/archive_promotion_receipt.json",
}
POST_VALIDATION_ALLOWED_MODIFICATIONS = {
    "Iris/_docs/refactor/repository_runtime_lightweighting/pre_delete_current_route_receipt.json",
    "Iris/_docs/refactor/repository_runtime_lightweighting/validation_checkpoint_manifest.json",
    "Iris/_docs/refactor/repository_runtime_lightweighting/protected_surface_successor_manifest.json",
}

CHECKPOINT_MANIFEST_RELATIVE = (
    "Iris/_docs/refactor/repository_runtime_lightweighting/validation_checkpoint_manifest.json"
)
PRE_DELETE_RECEIPT_RELATIVE = (
    "Iris/_docs/refactor/repository_runtime_lightweighting/pre_delete_current_route_receipt.json"
)
PROTECTED_SUCCESSOR_RELATIVE = (
    "Iris/_docs/refactor/repository_runtime_lightweighting/protected_surface_successor_manifest.json"
)
ENVIRONMENT_AUTHORITY_RELATIVE = (
    "Iris/validation/clean_checkout/authority/phase0_ratification_attempt_0002.json"
)
BASELINE_PROMOTION_SCHEMAS = {
    "iris_repository_runtime_lightweighting_baseline_promotion_v1",
    "iris_repository_runtime_lightweighting_baseline_promotion_v2",
}
LIFECYCLE_V2_DIRECTORY = "lifecycle_manifest_v2"
LIFECYCLE_V2_COMPONENTS = (
    LIFECYCLE_V2_DICTIONARY_NAME,
    LIFECYCLE_V2_NODES_NAME,
    LIFECYCLE_V2_BASELINE_NAME,
    LIFECYCLE_V2_DELTA_NAME,
    LIFECYCLE_V2_RECEIPT_NAME,
)


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_lf_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload.replace(b"\r\n", b"\n")).hexdigest()


def git_blob_bytes(repo: Path, revision: str, relative: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo), "show", f"{revision}:{relative}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise LifecycleExecutionError(
            f"Git blob is unavailable at {revision}:{relative}"
        )
    return completed.stdout


def git_blob_id(repo: Path, revision: str, relative: str) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"{revision}:{relative}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return value if value else None


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise LifecycleExecutionError(f"expected JSON object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise LifecycleExecutionError(f"expected object at {path}:{line_number}")
            rows.append(value)
    return rows


def durable_lifecycle_source(
    baseline_path: Path,
    view: str = "baseline",
) -> tuple[Path, bytes, list[dict[str, Any]], str]:
    v1_path = baseline_path.with_name(
        "artifact_role_manifest.jsonl"
        if view == "baseline"
        else "final_artifact_role_manifest.jsonl"
    )
    v2_root = (
        baseline_path.parent.parent
        / "repository_evidence_lightweighting"
        / LIFECYCLE_V2_DIRECTORY
    )
    source = v1_path if v1_path.is_file() else v2_root
    try:
        payload, rows, representation = materialize_manifest(source, view)  # type: ignore[arg-type]
    except RepositoryEvidenceCodecError as error:
        raise LifecycleExecutionError(
            f"durable lifecycle {view} representation is unavailable or invalid"
        ) from error
    return source.resolve(), payload, rows, representation


def valid_sha256(value: object) -> bool:
    text = str(value)
    return len(text) == 64 and all(character in "0123456789abcdef" for character in text)


def same_path(left: object, right: Path) -> bool:
    try:
        return os.path.normcase(str(Path(str(left)).resolve())) == os.path.normcase(str(right.resolve()))
    except (OSError, ValueError):
        return False


def route_passed(route: dict[str, Any]) -> bool:
    if route.get("success") is True or route.get("status") in {"PASS", "passed"}:
        return True
    summary = route.get("summary", {})
    return bool(
        isinstance(summary, dict)
        and summary.get("failed") == 0
        and summary.get("errors") == 0
    )


def atomic_write_new(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise LifecycleExecutionError(f"receipt/output already exists: {path}")
    payload = canonical_json_bytes(value)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.exists():
        raise LifecycleExecutionError(f"temporary output already exists: {temporary}")
    temporary.write_bytes(payload)
    try:
        os.link(temporary, path)
    except FileExistsError as error:
        raise LifecycleExecutionError(f"receipt/output already exists: {path}") from error
    finally:
        temporary.unlink(missing_ok=True)


def require_external(repo: Path, path: Path, role: str) -> Path:
    lexical = Path(os.path.abspath(path))
    try:
        lexical.relative_to(repo)
    except ValueError:
        pass
    else:
        raise LifecycleExecutionError(f"{role} lexical path must be repository-external: {lexical}")
    resolved = path.resolve()
    try:
        resolved.relative_to(repo)
    except ValueError:
        pass
    else:
        raise LifecycleExecutionError(f"{role} must be repository-external: {resolved}")
    try:
        repo.relative_to(resolved)
    except ValueError:
        pass
    else:
        raise LifecycleExecutionError(f"{role} must not contain repository: {resolved}")
    return resolved


def exact_repo_file(repo: Path, relative: str) -> Path:
    if any(character in relative for character in "*?[]"):
        raise LifecycleExecutionError(f"glob syntax is forbidden: {relative}")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or not pure.name:
        raise LifecycleExecutionError(f"unsafe repository path: {relative}")
    lexical_repo = Path(os.path.abspath(repo))
    target = Path(os.path.abspath(lexical_repo / Path(*pure.parts)))
    try:
        target.relative_to(lexical_repo)
    except ValueError as error:
        raise LifecycleExecutionError(f"path escapes repository: {relative}") from error
    current = target
    while True:
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            metadata = None
        if metadata is not None:
            reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
            file_attributes = getattr(metadata, "st_file_attributes", 0)
            if stat.S_ISLNK(metadata.st_mode) or (file_attributes & reparse_flag):
                raise LifecycleExecutionError(f"repository path traverses a symlink or reparse point: {relative}")
        if current == lexical_repo:
            break
        current = current.parent
    resolved_target = target.resolve(strict=False)
    resolved_repo = lexical_repo.resolve(strict=True)
    try:
        resolved_target.relative_to(resolved_repo)
    except ValueError as error:
        raise LifecycleExecutionError(f"resolved path escapes repository: {relative}") from error
    return target


def require_exact_regular_file(target: Path, row: dict[str, Any], phase: str) -> None:
    try:
        metadata = target.lstat()
    except FileNotFoundError as error:
        raise LifecycleExecutionError(f"{phase} target is not an exact regular file: {row['path']}") from error
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    file_attributes = getattr(metadata, "st_file_attributes", 0)
    if (
        not stat.S_ISREG(metadata.st_mode)
        or stat.S_ISLNK(metadata.st_mode)
        or (file_attributes & reparse_flag)
    ):
        raise LifecycleExecutionError(f"{phase} target is not an exact regular file: {row['path']}")
    if sha256_file(target) != row["sha256"] or metadata.st_size != row["size_bytes"]:
        raise LifecycleExecutionError(f"{phase} target changed: {row['path']}")


def operation_id(subject: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    payload = {
        "physical_subject": subject,
        "rows": [{"path": row["path"], "sha256": row["sha256"], "size_bytes": row["size_bytes"]} for row in rows],
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def operation_repo(operation: dict[str, Any]) -> Path:
    root = Path(str(operation.get("physical_subject", {}).get("physical_resolved_root", ""))).resolve()
    if not (root / ".git").exists():
        raise LifecycleExecutionError("operation physical subject is not a Git checkout")
    return root


def current_reference_policy(repo: Path) -> dict[str, Any]:
    try:
        return load_lifecycle_reference_policy(repo)
    except (LifecycleError, OSError, ValueError, json.JSONDecodeError) as error:
        raise LifecycleExecutionError(str(error)) from error


def validate_zero_live_reference_report(
    repo: Path,
    report: object,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(report, dict):
        raise LifecycleExecutionError("archive operation lacks a fresh reference report")
    report_rows = report.get("rows")
    expected_paths = sorted(str(row.get("path", "")) for row in rows)
    actual_paths = (
        sorted(str(row.get("path", "")) for row in report_rows if isinstance(row, dict))
        if isinstance(report_rows, list)
        else []
    )
    payload = dict(report)
    claimed_hash = payload.pop("report_sha256", None)
    if (
        report.get("schema_version")
        != "iris_repository_runtime_lightweighting_live_reference_report_v1"
        or report.get("physical_resolved_root") != repo.as_posix()
        or actual_paths != expected_paths
        or not isinstance(report_rows, list)
        or len(report_rows) != len(actual_paths)
        or len(actual_paths) != len(set(actual_paths))
        or report.get("live_reference_count") != 0
        or report.get("consumer_scan_hold_count") != 0
        or not isinstance(report.get("excluded_role_counts"), dict)
        or claimed_hash != hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    ):
        raise LifecycleExecutionError("fresh reference report identity/summary mismatch")
    policy = current_reference_policy(repo)
    if report.get("reference_policy") != policy["binding"]:
        raise LifecycleExecutionError("fresh reference report policy binding mismatch")
    disposed_rules = {
        rule["record_axis"]: rule for rule in policy["rules"]
    }
    operation_by_path = {str(row["path"]): row for row in rows}
    excluded_sources: dict[str, set[str]] = {
        rule["role"]: set() for rule in policy["rules"]
    }
    for row in report_rows:
        report_path = str(row.get("path", ""))
        consumer_axes = row.get("consumer_axes")
        if not isinstance(consumer_axes, dict):
            raise LifecycleExecutionError("fresh reference report consumer axes are malformed")
        for axis, sources in consumer_axes.items():
            if (
                not isinstance(axis, str)
                or not isinstance(sources, list)
                or not all(isinstance(source, str) for source in sources)
                or len(sources) != len(set(sources))
            ):
                raise LifecycleExecutionError("fresh reference report consumer axes are malformed")
            rule = disposed_rules.get(axis)
            if rule is None:
                continue
            operation_row = operation_by_path.get(report_path, {})
            if (
                report_path not in policy["target_paths"]
                or operation_row.get("producer") != policy["producer"]
            ):
                raise LifecycleExecutionError(
                    "fresh reference report disposition target scope mismatch"
                )
            if not all(
                any(fnmatch.fnmatchcase(source, pattern) for pattern in rule["path_globs"])
                for source in sources
            ):
                raise LifecycleExecutionError(
                    "fresh reference report disposed source is outside policy scope"
                )
            excluded_sources[rule["role"]].update(sources)
        if (
            row.get("direct_consumers")
            or row.get("transitive_consumers")
            or row.get("consumer_scan_holds")
            or row.get("zero_live_consumers") is not True
        ):
            raise LifecycleExecutionError(
                f"fresh reference report contains a live consumer: {row.get('path')}"
            )
    expected_excluded_role_counts = {
        role: len(sources) for role, sources in sorted(excluded_sources.items())
    }
    if report.get("excluded_role_counts") != expected_excluded_role_counts:
        raise LifecycleExecutionError("fresh reference report excluded-role summary mismatch")
    return policy["binding"]


def validate_operation(operation: dict[str, Any], repo: Path | None = None) -> Path:
    if operation.get("schema_version") != "iris_repository_runtime_lightweighting_archive_operation_v1":
        raise LifecycleExecutionError("archive operation schema mismatch")
    resolved_repo = operation_repo(operation)
    if repo is not None and resolved_repo != repo:
        raise LifecycleExecutionError("archive operation repository mismatch")
    rows = operation.get("rows")
    if not isinstance(rows, list) or not rows:
        raise LifecycleExecutionError("archive operation row set is empty or malformed")
    paths = [str(row.get("path", "")) for row in rows]
    if len(set(paths)) != len(paths):
        raise LifecycleExecutionError("archive operation contains duplicate paths")
    for row in rows:
        exact_repo_file(resolved_repo, str(row.get("path", "")))
        digest = str(row.get("sha256", ""))
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise LifecycleExecutionError(f"archive operation hash is invalid: {row.get('path')}")
        if not isinstance(row.get("size_bytes"), int) or int(row["size_bytes"]) < 0:
            raise LifecycleExecutionError(f"archive operation size is invalid: {row.get('path')}")
    if operation_id(operation.get("physical_subject", {}), rows) != operation.get("operation_id"):
        raise LifecycleExecutionError("archive operation ID mismatch")
    if operation.get("zero_live_reference_count") != 0:
        raise LifecycleExecutionError("archive operation zero-reference disposition mismatch")
    policy_binding = validate_zero_live_reference_report(
        resolved_repo,
        operation.get("zero_live_reference_report"),
        rows,
    )
    if operation.get("lifecycle_reference_policy") != policy_binding:
        raise LifecycleExecutionError("archive operation policy binding mismatch")
    return resolved_repo


def validate_step8_protected_successor(
    repo: Path,
    subject: dict[str, Any],
    receipt: dict[str, Any],
) -> None:
    protected_path = (repo / PROTECTED_SUCCESSOR_RELATIVE).resolve()
    if not protected_path.is_file():
        raise LifecycleExecutionError("STEP 8 protected successor manifest is unavailable")
    head_bytes = git_blob_bytes(repo, "HEAD", PROTECTED_SUCCESSOR_RELATIVE)
    if head_bytes != protected_path.read_bytes():
        raise LifecycleExecutionError("STEP 8 protected successor manifest is not bound to HEAD")
    prior_bytes = git_blob_bytes(
        repo,
        str(subject["commit"]),
        PROTECTED_SUCCESSOR_RELATIVE,
    )
    try:
        prior = json.loads(prior_bytes.decode("utf-8"))
        current = json.loads(head_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise LifecycleExecutionError("STEP 8 protected successor manifest is malformed") from error
    if not isinstance(prior, dict) or not isinstance(current, dict):
        raise LifecycleExecutionError("STEP 8 protected successor manifest is not an object")
    if (
        prior.get("schema_version")
        != "iris_repository_runtime_lightweighting_protected_surface_successor_v1"
        or current.get("schema_version") != prior.get("schema_version")
    ):
        raise LifecycleExecutionError("STEP 8 protected successor schema mismatch")
    prior_header = {key: value for key, value in prior.items() if key != "revisions"}
    current_header = {key: value for key, value in current.items() if key != "revisions"}
    prior_revisions = prior.get("revisions")
    current_revisions = current.get("revisions")
    if (
        prior_header != current_header
        or not isinstance(prior_revisions, list)
        or not isinstance(current_revisions, list)
        or len(current_revisions) != len(prior_revisions) + 1
        or current_revisions[:-1] != prior_revisions
    ):
        raise LifecycleExecutionError(
            "STEP 8 protected successor history is not an immutable single-revision append"
        )

    revision = current_revisions[-1]
    revision_id = receipt.get("protected_surface_revision_id")
    expected_revision_keys = {
        "revision_id",
        "track",
        "owner",
        "approved",
        "predecessor_commit",
        "reason",
        "approved_activation_deltas",
        "added_protected_rows",
    }
    if (
        not isinstance(revision, dict)
        or set(revision) != expected_revision_keys
        or not isinstance(revision_id, str)
        or not revision_id
        or revision.get("revision_id") != revision_id
        or revision.get("track") != "common"
        or revision.get("owner") != "repository_owner_user"
        or revision.get("approved") is not True
        or revision.get("predecessor_commit") != subject.get("commit")
        or not isinstance(revision.get("reason"), str)
        or not revision.get("reason")
        or revision.get("approved_activation_deltas") != []
    ):
        raise LifecycleExecutionError("STEP 8 protected successor revision authority mismatch")
    if any(
        isinstance(row, dict) and row.get("revision_id") == revision_id
        for row in prior_revisions
    ):
        raise LifecycleExecutionError("STEP 8 protected successor revision id is reused")

    expected_metadata = {
        PRE_DELETE_RECEIPT_RELATIVE: {
            "role": "common_track_pre_delete_current_route_evidence",
            "writer": "repository_runtime_lightweighting_step8_checkpoint_writer",
            "consumers": [
                "archive_operation",
                "delete_prerequisite_gate",
                "terminal_closeout",
                "repository_maintainers",
            ],
        },
        CHECKPOINT_MANIFEST_RELATIVE: {
            "role": "common_track_validation_checkpoint_manifest",
            "writer": "repository_runtime_lightweighting_step8_checkpoint_writer",
            "consumers": [
                "archive_operation",
                "delete_prerequisite_gate",
                "selected_track_validation",
                "terminal_closeout",
                "repository_maintainers",
            ],
        },
    }
    added_rows = revision.get("added_protected_rows")
    if not isinstance(added_rows, list) or len(added_rows) != len(expected_metadata):
        raise LifecycleExecutionError("STEP 8 protected successor row count mismatch")
    by_path = {
        str(row.get("path", "")): row
        for row in added_rows
        if isinstance(row, dict)
    }
    if set(by_path) != set(expected_metadata) or len(by_path) != len(added_rows):
        raise LifecycleExecutionError("STEP 8 protected successor path set mismatch")

    expected_row_keys = {
        "path",
        "before_git_blob_id",
        "before_sha256_lf",
        "expected_git_blob_id",
        "after_sha256_lf",
        "role",
        "writer",
        "consumers",
        "owner",
        "reason",
    }
    for relative, metadata in expected_metadata.items():
        row = by_path[relative]
        before_blob_id = git_blob_id(repo, str(subject["commit"]), relative)
        before_bytes = (
            git_blob_bytes(repo, str(subject["commit"]), relative)
            if before_blob_id is not None
            else None
        )
        after_blob_id = git_blob_id(repo, "HEAD", relative)
        if after_blob_id is None:
            raise LifecycleExecutionError(
                f"STEP 8 protected successor target is absent from HEAD: {relative}"
            )
        after_bytes = git_blob_bytes(repo, "HEAD", relative)
        if (
            set(row) != expected_row_keys
            or row.get("before_git_blob_id") != before_blob_id
            or row.get("before_sha256_lf")
            != (sha256_lf_bytes(before_bytes) if before_bytes is not None else None)
            or row.get("expected_git_blob_id") != after_blob_id
            or row.get("after_sha256_lf") != sha256_lf_bytes(after_bytes)
            or row.get("role") != metadata["role"]
            or row.get("writer") != metadata["writer"]
            or row.get("consumers") != metadata["consumers"]
            or row.get("owner") != "repository_owner_user"
            or not isinstance(row.get("reason"), str)
            or not row.get("reason")
        ):
            raise LifecycleExecutionError(
                f"STEP 8 protected successor row identity mismatch: {relative}"
            )


def validate_pre_delete_receipt(repo: Path, receipt_path: Path) -> dict[str, Any]:
    expected = (repo / PRE_DELETE_RECEIPT_RELATIVE).resolve()
    if receipt_path.resolve() != expected:
        raise LifecycleExecutionError("pre-delete receipt is not the exact durable path")
    receipt = load_object(expected)
    if (
        receipt.get("schema_version")
        != "iris_repository_runtime_lightweighting_pre_delete_current_route_receipt_v1"
        or receipt.get("status") != "PASS"
        or receipt.get("receipt_kind") != "pre_delete_current_route"
    ):
        raise LifecycleExecutionError("pre-delete current-route receipt schema/status mismatch")
    relative = expected.relative_to(repo).as_posix()
    blob = subprocess.run(
        ["git", "-C", str(repo), "show", f"HEAD:{relative}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if blob.returncode != 0 or hashlib.sha256(blob.stdout).hexdigest() != sha256_file(expected):
        raise LifecycleExecutionError("pre-delete current-route receipt is not bound to physical HEAD")
    subject = receipt.get("validated_subject", {})
    if (
        subject.get("subject_kind") != "common_pre_delete_validation_subject"
        or not str(subject.get("claim_id", ""))
        or not str(subject.get("commit", ""))
        or not str(subject.get("tree", ""))
        or not valid_sha256(subject.get("subject_receipt_sha256"))
        or not str(subject.get("subject_receipt_path", ""))
        or not str(subject.get("repository_root", ""))
    ):
        raise LifecycleExecutionError("pre-delete receipt lacks exact validation-subject identity")
    validation_root = require_external(
        repo,
        Path(str(subject["repository_root"])),
        "pre-delete validation checkout",
    )
    subject_receipt_path = require_external(
        repo,
        Path(str(subject["subject_receipt_path"])),
        "pre-delete validation subject receipt",
    )
    if not (validation_root / ".git").exists() or not subject_receipt_path.is_file():
        raise LifecycleExecutionError("pre-delete validation checkout/subject receipt is unavailable")
    if sha256_file(subject_receipt_path) != subject.get("subject_receipt_sha256"):
        raise LifecycleExecutionError("pre-delete validation subject receipt hash mismatch")
    subject_receipt = load_object(subject_receipt_path)
    if (
        subject_receipt.get("subject_kind") != subject.get("subject_kind")
        or subject_receipt.get("claim_id") != subject.get("claim_id")
        or subject_receipt.get("commit") != subject.get("commit")
        or subject_receipt.get("tree") != subject.get("tree")
        or not same_path(subject_receipt.get("repository_root"), validation_root)
    ):
        raise LifecycleExecutionError("pre-delete validation subject payload mismatch")
    subject_tree = subprocess.run(
        ["git", "-C", str(validation_root), "rev-parse", f"{subject['commit']}^{{tree}}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if subject_tree.returncode != 0 or subject_tree.stdout.strip() != subject.get("tree"):
        raise LifecycleExecutionError("pre-delete validation subject commit/tree is unresolved")
    validation_state = subprocess.run(
        [
            "git",
            "-C",
            str(validation_root),
            "rev-parse",
            "HEAD",
            "HEAD^{tree}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    validation_status = subprocess.run(
        ["git", "-C", str(validation_root), "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if (
        validation_state.returncode != 0
        or validation_state.stdout.splitlines() != [subject.get("commit"), subject.get("tree")]
        or validation_status.returncode != 0
        or validation_status.stdout
    ):
        raise LifecycleExecutionError("pre-delete validation checkout is not the exact clean subject")

    physical_subject_commit = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"{subject['commit']}^{{commit}}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    physical_subject_tree = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"{subject['commit']}^{{tree}}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    physical_ancestry = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", str(subject["commit"]), "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if (
        physical_subject_commit.returncode != 0
        or physical_subject_commit.stdout.strip() != subject.get("commit")
        or physical_subject_tree.returncode != 0
        or physical_subject_tree.stdout.strip() != subject.get("tree")
        or physical_ancestry.returncode != 0
    ):
        raise LifecycleExecutionError(
            "pre-delete validation subject is not an exact ancestor of the physical candidate"
        )
    for diff_args in (("diff", "--quiet", "HEAD", "--"), ("diff", "--cached", "--quiet", "HEAD", "--")):
        physical_worktree = subprocess.run(
            ["git", "-C", str(repo), *diff_args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if physical_worktree.returncode != 0:
            raise LifecycleExecutionError(
                "physical tracked implementation has uncommitted changes after validation"
            )

    checkpoint_path = (repo / CHECKPOINT_MANIFEST_RELATIVE).resolve()
    checkpoint_blob = subprocess.run(
        ["git", "-C", str(repo), "show", f"HEAD:{CHECKPOINT_MANIFEST_RELATIVE}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if (
        not checkpoint_path.is_file()
        or checkpoint_blob.returncode != 0
        or hashlib.sha256(checkpoint_blob.stdout).hexdigest() != sha256_file(checkpoint_path)
    ):
        raise LifecycleExecutionError("validation checkpoint manifest is not bound to physical HEAD")
    prior_checkpoint_blob = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "show",
            f"{subject['commit']}:{CHECKPOINT_MANIFEST_RELATIVE}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if prior_checkpoint_blob.returncode != 0:
        raise LifecycleExecutionError(
            "validated Common candidate lacks the prior checkpoint manifest"
        )
    try:
        prior_checkpoint = json.loads(prior_checkpoint_blob.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise LifecycleExecutionError("prior validation checkpoint manifest is malformed") from error
    checkpoint = load_object(checkpoint_path)
    if (
        not isinstance(prior_checkpoint, dict)
        or checkpoint.get("schema_version")
        != "iris_repository_runtime_lightweighting_validation_checkpoint_manifest_v1"
        or prior_checkpoint.get("schema_version") != checkpoint.get("schema_version")
    ):
        raise LifecycleExecutionError("validation checkpoint manifest schema mismatch")
    prior_rows = prior_checkpoint.get("checkpoints")
    checkpoint_rows = checkpoint.get("checkpoints")
    if (
        not isinstance(prior_rows, list)
        or not isinstance(checkpoint_rows, list)
        or len(checkpoint_rows) != len(prior_rows) + 1
        or checkpoint_rows[:-1] != prior_rows
    ):
        raise LifecycleExecutionError(
            "validation checkpoint history is not an immutable single-row append"
        )

    environment_authority = receipt.get("environment_authority", {})
    environment_authority_path = (validation_root / ENVIRONMENT_AUTHORITY_RELATIVE).resolve()
    if (
        not same_path(environment_authority.get("path"), environment_authority_path)
        or not environment_authority_path.is_file()
        or environment_authority.get("sha256") != sha256_file(environment_authority_path)
    ):
        raise LifecycleExecutionError("pre-delete environment authority identity mismatch")
    checkpoint_row = checkpoint_rows[-1]
    expected_checkpoint_row = {
        "checkpoint_id": "common_pre_delete",
        "subject_kind": subject["subject_kind"],
        "claim_id": subject["claim_id"],
        "commit": subject["commit"],
        "tree": subject["tree"],
        "clean_checkout_receipt": {
            "path": subject_receipt_path.as_posix(),
            "sha256": subject["subject_receipt_sha256"],
        },
        "required_receipt": {
            "path": PRE_DELETE_RECEIPT_RELATIVE,
            "sha256": sha256_file(expected),
        },
        "taxonomy": {
            "path": "Iris/_docs/round3/round3_test_taxonomy.json",
            "sha256": receipt.get("taxonomy", {}).get("sha256"),
        },
        "required_validations": {
            "path": "Iris/_docs/round3/current_route_required_validations.json",
            "sha256": receipt.get("required_validations", {}).get("sha256"),
        },
        "active_core_closure": {
            "path": "Iris/_docs/round3/round3_active_core_closure.json",
            "sha256": receipt.get("active_core_closure", {}).get("sha256"),
        },
        "environment_authority": {
            "path": ENVIRONMENT_AUTHORITY_RELATIVE,
            "sha256": environment_authority.get("sha256"),
        },
        "output_isolation_audit": {
            "path": receipt.get("output_isolation_audit", {}).get("path"),
            "sha256": receipt.get("output_isolation_audit", {}).get("sha256"),
        },
        "command_receipt_set_sha256": receipt.get("command_receipt_set_sha256"),
    }
    if not isinstance(checkpoint_row, dict) or checkpoint_row != expected_checkpoint_row:
        raise LifecycleExecutionError(
            "Common pre-delete checkpoint does not bind the exact validated candidate"
        )
    validate_step8_protected_successor(repo, subject, receipt)

    def changed_paths(diff_filter: str) -> set[str]:
        completed = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "diff",
                "--name-only",
                "-z",
                f"--diff-filter={diff_filter}",
                str(subject["commit"]),
                "HEAD",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if completed.returncode != 0:
            raise LifecycleExecutionError("physical candidate tracked delta is unresolved")
        return {
            token.decode("utf-8", errors="surrogateescape")
            for token in completed.stdout.split(b"\0")
            if token
        }

    added_paths = changed_paths("A")
    modified_paths = changed_paths("M")
    forbidden_transitions = changed_paths("CDRTUXB")
    if forbidden_transitions:
        raise LifecycleExecutionError(
            "physical candidate contains a forbidden tracked transition: "
            + ", ".join(sorted(forbidden_transitions))
        )
    receipt_added = PRE_DELETE_RECEIPT_RELATIVE in added_paths
    receipt_modified = PRE_DELETE_RECEIPT_RELATIVE in modified_paths
    if receipt_added == receipt_modified:
        raise LifecycleExecutionError(
            "pre-delete receipt must be exactly one approved add-or-refresh transition"
        )
    required_modifications = {
        CHECKPOINT_MANIFEST_RELATIVE,
        PROTECTED_SUCCESSOR_RELATIVE,
    }
    if receipt_modified:
        required_modifications.add(PRE_DELETE_RECEIPT_RELATIVE)
    forbidden_additions = added_paths - POST_VALIDATION_ALLOWED_ADDITIONS
    forbidden_modifications = modified_paths - POST_VALIDATION_ALLOWED_MODIFICATIONS
    if forbidden_additions or forbidden_modifications:
        changed_path = sorted(forbidden_additions | forbidden_modifications)[0]
        raise LifecycleExecutionError(
            f"physical tracked implementation differs from validated Common candidate: {changed_path}"
        )
    if modified_paths != required_modifications:
        raise LifecycleExecutionError(
            "physical post-validation modification set is not the exact STEP 8 seal"
        )
    for key, relative_input in (
        ("taxonomy", "Iris/_docs/round3/round3_test_taxonomy.json"),
        ("required_validations", "Iris/_docs/round3/current_route_required_validations.json"),
        ("active_core_closure", "Iris/_docs/round3/round3_active_core_closure.json"),
    ):
        binding = receipt.get(key, {})
        actual = (validation_root / relative_input).resolve()
        physical_equivalent = (repo / relative_input).resolve()
        if (
            Path(str(binding.get("path", ""))).resolve() != actual
            or not actual.is_file()
            or binding.get("sha256") != sha256_file(actual)
            or not physical_equivalent.is_file()
            or sha256_file(physical_equivalent) != sha256_file(actual)
        ):
            raise LifecycleExecutionError(f"pre-delete receipt input binding mismatch: {key}")
    audit_binding = receipt.get("output_isolation_audit", {})
    audit_receipt_path = require_external(
        repo,
        Path(str(audit_binding.get("path", ""))),
        "current-route output-isolation audit receipt",
    )
    if (
        not audit_receipt_path.is_file()
        or audit_binding.get("sha256") != sha256_file(audit_receipt_path)
    ):
        raise LifecycleExecutionError("pre-delete output-isolation audit identity mismatch")
    audit_receipt = load_object(audit_receipt_path)
    if (
        audit_receipt.get("schema_version")
        != "iris_repository_runtime_lightweighting_current_route_output_isolation_receipt_v1"
        or audit_receipt.get("status") != "PASS"
        or audit_receipt.get("audit_subject")
        != {"commit": subject.get("commit"), "tree": subject.get("tree")}
        or audit_receipt.get("taxonomy_sha256") != receipt.get("taxonomy", {}).get("sha256")
        or audit_receipt.get("required_validations_sha256")
        != receipt.get("required_validations", {}).get("sha256")
        or audit_receipt.get("checkout_unchanged") is not True
        or any(
            int(audit_receipt.get(key, -1)) != 0
            for key in (
                "tracked_delta_count",
                "untracked_delta_count",
                "ignored_delta_count",
                "unreadable_count",
            )
        )
    ):
        raise LifecycleExecutionError("pre-delete output-isolation audit is not an exact clean PASS")
    audit_root = require_external(
        repo,
        Path(str(audit_receipt.get("repository_root", ""))),
        "output-isolation audit checkout",
    )
    require_external(
        validation_root,
        audit_root,
        "separate output-isolation audit checkout",
    )
    if not (audit_root / ".git").exists():
        raise LifecycleExecutionError("output-isolation audit checkout is unavailable")
    command_rows = receipt.get("command_receipts")
    if not isinstance(command_rows, list) or not command_rows:
        raise LifecycleExecutionError("pre-delete receipt lacks command receipt set")
    canonical_command_set: list[dict[str, Any]] = []
    saw_current = False
    saw_isolation_audit = False
    for binding in command_rows:
        if not isinstance(binding, dict):
            raise LifecycleExecutionError("pre-delete command receipt binding is malformed")
        command_path = Path(str(binding.get("path", ""))).resolve()
        if not command_path.is_file() or binding.get("sha256") != sha256_file(command_path):
            raise LifecycleExecutionError("pre-delete command receipt identity mismatch")
        command = load_object(command_path)
        if (
            command.get("schema_version") != "iris_repository_runtime_lightweighting_command_receipt_v1"
            or command.get("terminal_status") != "pass"
            or command.get("native_exit_code") != 0
            or command.get("semantic_exit_code") != 0
            or command.get("claim_id") != subject.get("claim_id")
            or command.get("subject_receipt", {}).get("sha256") != subject.get("subject_receipt_sha256")
            or not same_path(command.get("subject_receipt", {}).get("path"), subject_receipt_path)
            or command.get("subject_receipt", {}).get("execution_commit") != subject.get("commit")
            or command.get("subject_receipt", {}).get("execution_tree") != subject.get("tree")
            or not same_path(command.get("working_directory"), validation_root)
            or not same_path(
                command.get("environment_authority", {}).get("path"),
                environment_authority_path,
            )
            or command.get("environment_authority", {}).get("sha256")
            != environment_authority.get("sha256")
        ):
            raise LifecycleExecutionError("pre-delete command receipt is not an exact subject-bound PASS")
        assertion = command.get("output_assertion", {})
        if assertion.get("kind") != "checkout_unchanged" or assertion.get("status") != "pass":
            raise LifecycleExecutionError("pre-delete command lacks checkout_unchanged PASS")
        delta = assertion.get("delta", {})
        if any(
            int(delta.get(key, -1)) != 0
            for key in (
                "changed_count",
                "tracked_delta_count",
                "untracked_delta_count",
                "ignored_delta_count",
                "unreadable_count",
            )
        ):
            raise LifecycleExecutionError("pre-delete command checkout census is not zero")
        command_id = str(command.get("command_id", ""))
        spec_binding = command.get("command_spec", {})
        spec_path = Path(str(spec_binding.get("path", ""))).resolve()
        if not spec_path.is_file() or spec_binding.get("sha256") != sha256_file(spec_path):
            raise LifecycleExecutionError("pre-delete command spec identity mismatch")
        spec = load_object(spec_path)
        argv = command.get("decoded_argv")
        if (
            spec.get("schema_version") != "iris_repository_runtime_lightweighting_command_spec_v1"
            or not same_path(spec.get("command_receipt"), command_path)
            or not same_path(spec.get("working_directory"), validation_root)
            or not same_path(spec.get("subject_receipt"), subject_receipt_path)
            or spec.get("claim_id") != subject.get("claim_id")
            or spec.get("command_id") != command_id
            or spec.get("output_assertion") != "checkout_unchanged"
            or not same_path(spec.get("executable"), Path(str(command.get("executable", ""))))
            or not isinstance(argv, list)
            or argv != spec.get("argv")
        ):
            raise LifecycleExecutionError("pre-delete command spec boundary mismatch")
        if command_id.endswith("pre-delete-current-route"):
            if saw_current:
                raise LifecycleExecutionError("pre-delete receipt contains duplicate current-route commands")
            runner = validation_root / "Iris/_docs/round3/round3_run_contract_tests.py"
            if (
                not same_path(command.get("executable"), Path(sys.executable))
                or len(argv) != 7
                or argv[0] != "-B"
                or not same_path(
                    Path(str(argv[1])) if Path(str(argv[1])).is_absolute() else validation_root / str(argv[1]),
                    runner,
                )
                or argv[2:6]
                != ["--class", "current", "--enforce-current-build-closure", "--out"]
            ):
                raise LifecycleExecutionError(
                    "pre-delete current-route argv is not the exact canonical invocation"
                )
            out_index = 5
            invoked = command.get("invoked_repository_files")
            runner_rows = [
                row for row in invoked if isinstance(row, dict) and same_path(row.get("actual_path"), runner)
            ] if isinstance(invoked, list) else []
            runner_blob = subprocess.run(
                ["git", "-C", str(validation_root), "rev-parse", f"{subject['commit']}:Iris/_docs/round3/round3_run_contract_tests.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if (
                len(runner_rows) != 1
                or runner_blob.returncode != 0
                or runner_rows[0].get("execution_commit") != subject.get("commit")
                or runner_rows[0].get("git_blob_id") != runner_blob.stdout.strip()
                or runner_rows[0].get("working_sha256") != sha256_file(runner)
            ):
                raise LifecycleExecutionError("pre-delete current-route runner implementation mismatch")
            route_binding = receipt.get("current_route_result", {})
            route_path = Path(str(route_binding.get("path", ""))).resolve()
            argv_out = Path(str(argv[out_index + 1]))
            argv_out = argv_out.resolve() if argv_out.is_absolute() else (validation_root / argv_out).resolve()
            if (
                route_path != argv_out
                or not route_path.is_file()
                or route_binding.get("sha256") != sha256_file(route_path)
                or not route_passed(load_object(route_path))
            ):
                raise LifecycleExecutionError("pre-delete current-route result identity/semantics mismatch")
            saw_current = True
        if command_id.endswith("verify-current-route-output-isolation"):
            if saw_isolation_audit:
                raise LifecycleExecutionError(
                    "pre-delete receipt contains duplicate output-isolation verification commands"
                )
            audit_script = (
                validation_root
                / "Iris/validation/clean_checkout/audit_current_route_output_isolation.py"
            )
            if (
                not same_path(command.get("executable"), Path(sys.executable))
                or len(argv) != 11
                or argv[0] != "-B"
                or argv[2:4] != ["verify", "--repo"]
                or not same_path(argv[4], validation_root)
                or argv[5:10]
                != [
                    "--taxonomy",
                    "Iris/_docs/round3/round3_test_taxonomy.json",
                    "--required-validations",
                    "Iris/_docs/round3/current_route_required_validations.json",
                    "--receipt",
                ]
                or not same_path(argv[10], audit_receipt_path)
                or not same_path(
                    Path(str(argv[1])) if len(argv) > 1 and Path(str(argv[1])).is_absolute()
                    else validation_root / str(argv[1] if len(argv) > 1 else ""),
                    audit_script,
                )
            ):
                raise LifecycleExecutionError(
                    "output-isolation verify argv is not the exact canonical invocation"
                )
            invoked = command.get("invoked_repository_files")
            audit_rows = [
                row
                for row in invoked
                if isinstance(row, dict) and same_path(row.get("actual_path"), audit_script)
            ] if isinstance(invoked, list) else []
            audit_blob = subprocess.run(
                [
                    "git",
                    "-C",
                    str(validation_root),
                    "rev-parse",
                    f"{subject['commit']}:Iris/validation/clean_checkout/audit_current_route_output_isolation.py",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if (
                len(audit_rows) != 1
                or audit_blob.returncode != 0
                or audit_rows[0].get("execution_commit") != subject.get("commit")
                or audit_rows[0].get("git_blob_id") != audit_blob.stdout.strip()
                or audit_rows[0].get("working_sha256") != sha256_file(audit_script)
            ):
                raise LifecycleExecutionError(
                    "output-isolation verifier implementation identity mismatch"
                )
            audit_environment = dict(os.environ)
            audit_environment["PYTHONDONTWRITEBYTECODE"] = "1"
            verified_audit = subprocess.run(
                [sys.executable, *map(str, argv)],
                cwd=validation_root,
                env=audit_environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if verified_audit.returncode != 0:
                raise LifecycleExecutionError(
                    "current-route output-isolation verifier rejected the retained audit: "
                    + verified_audit.stderr.strip()
                )
            saw_isolation_audit = True
        canonical_command_set.append(
            {"command_id": command_id, "path": command_path.as_posix(), "sha256": binding["sha256"]}
        )
    canonical_command_set.sort(key=lambda row: row["command_id"])
    expected_set_hash = hashlib.sha256(canonical_json_bytes(canonical_command_set)).hexdigest()
    if (
        receipt.get("command_receipt_set_sha256") != expected_set_hash
        or not saw_current
        or not saw_isolation_audit
    ):
        raise LifecycleExecutionError(
            "pre-delete receipt command set/current route/output-isolation mismatch"
        )
    if receipt.get("checkout_clean_before") is not True or receipt.get("checkout_clean_after") is not True:
        raise LifecycleExecutionError("pre-delete receipt lacks clean pre/post assertions")
    return receipt


def _git_changed_paths(
    repo: Path,
    before: str,
    after: str,
    diff_filter: str,
) -> set[str]:
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "diff",
            "--name-only",
            "-z",
            f"--diff-filter={diff_filter}",
            before,
            after,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise LifecycleExecutionError(
            "validated Common candidate tracked delta is unresolved"
        )
    return {
        token.decode("utf-8", errors="surrogateescape")
        for token in completed.stdout.split(b"\0")
        if token
    }


def _is_lifecycle_scoped(path: str) -> bool:
    return any(path == root or path.startswith(root.rstrip("/") + "/") for root in SCOPED_ROOTS)


def build_validated_candidate_delta_allowset(
    repo: Path,
    baseline: dict[str, Any],
    pre_delete: dict[str, Any],
) -> dict[str, Any]:
    baseline_commit = str(baseline.get("commit", ""))
    subject = pre_delete.get("validated_subject", {})
    subject_commit = str(subject.get("commit", ""))
    validation_root = Path(str(subject.get("repository_root", ""))).resolve()
    for commit, label in (
        (baseline_commit, "baseline"),
        (subject_commit, "validated Common candidate"),
    ):
        resolved = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", f"{commit}^{{commit}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if resolved.returncode != 0 or resolved.stdout.strip() != commit:
            raise LifecycleExecutionError(f"{label} commit is unresolved")
    for before, after, label in (
        (baseline_commit, subject_commit, "baseline-to-Common"),
        (subject_commit, "HEAD", "Common-to-physical"),
    ):
        ancestry = subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", before, after],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if ancestry.returncode != 0:
            raise LifecycleExecutionError(f"{label} candidate chronology is invalid")

    candidate_paths = _git_changed_paths(repo, baseline_commit, subject_commit, "AM")
    candidate_forbidden = _git_changed_paths(
        repo, baseline_commit, subject_commit, "CDRTUXB"
    )
    if candidate_forbidden:
        raise LifecycleExecutionError(
            "validated Common candidate contains a forbidden tracked transition: "
            + ", ".join(sorted(candidate_forbidden))
        )
    post_added = _git_changed_paths(repo, subject_commit, "HEAD", "A")
    post_modified = _git_changed_paths(repo, subject_commit, "HEAD", "M")
    post_forbidden = _git_changed_paths(repo, subject_commit, "HEAD", "CDRTUXB")
    if (
        post_forbidden
        or post_added - POST_VALIDATION_ALLOWED_ADDITIONS
        or post_modified - POST_VALIDATION_ALLOWED_MODIFICATIONS
    ):
        raise LifecycleExecutionError(
            "post-validation physical candidate transition exceeds durable evidence policy"
        )

    rows: list[dict[str, Any]] = []
    scoped_paths = {
        path
        for path in candidate_paths | post_added | post_modified
        if _is_lifecycle_scoped(path)
    }
    for path in sorted(scoped_paths):
        candidate_blob: str | None = None
        if path in candidate_paths:
            candidate_result = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", f"{subject_commit}:{path}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if candidate_result.returncode != 0:
                raise LifecycleExecutionError(
                    f"validated Common candidate path is unresolved: {path}"
                )
            candidate_blob = candidate_result.stdout.strip()
            validation_path = validation_root / path
            validation_blob = subprocess.run(
                [
                    "git",
                    "-C",
                    str(validation_root),
                    "hash-object",
                    f"--path={path}",
                    str(validation_path),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if (
                not validation_path.is_file()
                or validation_path.is_symlink()
                or validation_blob.returncode != 0
                or validation_blob.stdout.strip() != candidate_blob
            ):
                raise LifecycleExecutionError(
                    f"validated Common candidate path/blob binding mismatch: {path}"
                )

        head_blob = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", f"HEAD:{path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        physical_path = exact_repo_file(repo, path)
        working_blob = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "hash-object",
                f"--path={path}",
                str(physical_path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if (
            not physical_path.is_file()
            or physical_path.is_symlink()
            or head_blob.returncode != 0
            or working_blob.returncode != 0
            or working_blob.stdout.strip() != head_blob.stdout.strip()
        ):
            raise LifecycleExecutionError(
                f"physical candidate path/blob binding mismatch: {path}"
            )
        rows.append(
            {
                "path": path,
                "transition_phase": (
                    "validated_common_then_post_validation"
                    if path in candidate_paths and path in post_added | post_modified
                    else "validated_common_candidate"
                    if path in candidate_paths
                    else "post_validation_durable_evidence"
                ),
                "validated_candidate_git_blob_id": candidate_blob,
                "expected_physical_head_git_blob_id": head_blob.stdout.strip(),
                "sha256": sha256_file(physical_path),
                "size_bytes": physical_path.stat().st_size,
            }
        )
    return {
        "schema_version": "iris_repository_runtime_lightweighting_validated_candidate_delta_allowset_v1",
        "baseline_commit": baseline_commit,
        "validated_subject_commit": subject_commit,
        "physical_head_commit": subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        ).stdout.strip(),
        "rows": rows,
    }


def validate_baseline(repo: Path, baseline_path: Path, promotion_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    baseline = load_object(baseline_path)
    promotion = load_object(promotion_path)
    if baseline.get("subject_kind") != "physical_capacity_subject":
        raise LifecycleExecutionError("baseline is not a physical_capacity_subject")
    if Path(str(baseline.get("physical_resolved_root"))).resolve() != repo:
        raise LifecycleExecutionError("baseline physical root mismatch")
    if (
        promotion.get("schema_version") not in BASELINE_PROMOTION_SCHEMAS
        or promotion.get("mode") != "baseline"
        or promotion.get("byte_identity_verified") is not True
    ):
        raise LifecycleExecutionError("baseline promotion receipt is invalid")
    try:
        validate_baseline_promotion_payload(repo, baseline_path.parent, promotion)
    except PromotionError as error:
        raise LifecycleExecutionError("baseline promotion transaction is invalid") from error
    if baseline.get("unclassified_count") != 0 or baseline.get("unreadable_count") != 0 or baseline.get("consumer_scan_hold_count", 0) != 0 or baseline.get("complete_accounting") is not True:
        raise LifecycleExecutionError("baseline accounting is incomplete")
    manifest_path, manifest_bytes, manifest_rows, manifest_representation = durable_lifecycle_source(
        baseline_path
    )
    promoted_by_destination = {
        Path(str(row.get("destination_path"))).name: row for row in promotion.get("promoted_files", [])
    }
    baseline_binding = promoted_by_destination.get("baseline_inventory.json", {})
    manifest_binding = promoted_by_destination.get("artifact_role_manifest.jsonl", {})
    if baseline_binding.get("destination_sha256") != sha256_file(baseline_path):
        raise LifecycleExecutionError("promoted baseline hash mismatch")
    if manifest_binding.get("destination_sha256") != evidence_raw_sha256(manifest_bytes):
        raise LifecycleExecutionError("promoted manifest hash mismatch")
    durable_paths = [baseline_path, promotion_path]
    if manifest_representation == "v1":
        durable_paths.append(manifest_path)
    else:
        durable_paths.extend(manifest_path / name for name in LIFECYCLE_V2_COMPONENTS)
    for path in durable_paths:
        if not path.is_file():
            raise LifecycleExecutionError(f"durable lifecycle evidence is missing: {path}")
        try:
            relative = path.resolve().relative_to(repo).as_posix()
        except ValueError as error:
            raise LifecycleExecutionError("promoted baseline evidence is not repository-durable") from error
        blob = subprocess.run(
            ["git", "-C", str(repo), "show", f"HEAD:{relative}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if blob.returncode != 0 or hashlib.sha256(blob.stdout).hexdigest() != sha256_file(path):
            raise LifecycleExecutionError(f"promoted baseline evidence is not bound to HEAD: {relative}")
    return baseline, manifest_rows


def live_reference_report(repo: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    policy = current_reference_policy(repo)
    probes = [
        {
            "path": str(row["path"]),
            "path_access": "readable",
            "producer": row.get("producer"),
        }
        for row in rows
    ]
    graph = reference_graph(
        repo,
        probes,
        git_path_set(repo, "ls-files", "-z"),
        git_path_set(repo, "ls-files", "-z", "--others", "--exclude-standard"),
        lifecycle_policy=policy,
    )
    report_rows = []
    for row in sorted(rows, key=lambda item: str(item["path"])):
        reference = graph.get(str(row["path"]), {})
        report_rows.append(
            {
                "path": row["path"],
                "consumer_axes": reference.get("consumer_axes", {}),
                "direct_consumers": reference.get("direct_consumers", []),
                "transitive_consumers": reference.get("transitive_consumers", []),
                "consumer_scan_holds": reference.get("consumer_scan_holds", []),
                "zero_live_consumers": reference.get("zero_live_consumers", False),
            }
        )
    live_count = sum(
        len(row["direct_consumers"]) + len(row["transitive_consumers"])
        for row in report_rows
    )
    hold_count = sum(len(row["consumer_scan_holds"]) for row in report_rows)
    disposed_roles = {
        rule["record_axis"]: rule["role"] for rule in policy["rules"]
    }
    excluded_sources: dict[str, set[str]] = {
        role: set() for role in disposed_roles.values()
    }
    for row in report_rows:
        for axis, sources in row.get("consumer_axes", {}).items():
            role = disposed_roles.get(axis)
            if role is not None:
                excluded_sources[role].update(map(str, sources))
    payload = {
        "schema_version": "iris_repository_runtime_lightweighting_live_reference_report_v1",
        "physical_resolved_root": repo.as_posix(),
        "reference_policy": policy["binding"],
        "rows": report_rows,
        "live_reference_count": live_count,
        "consumer_scan_hold_count": hold_count,
        "excluded_role_counts": {
            role: len(paths) for role, paths in sorted(excluded_sources.items())
        },
    }
    payload["report_sha256"] = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    return payload


def command_dry_run(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    manifest_out = require_external(repo, args.manifest_out, "operation manifest")
    receipt_out = require_external(repo, args.receipt_out, "dry-run receipt")
    selection_path = require_external(repo, args.selection, "owner archive selection")
    if manifest_out == receipt_out or manifest_out.exists() or receipt_out.exists():
        raise LifecycleExecutionError("dry-run output paths must be distinct and unused")
    baseline, rows = validate_baseline(repo, args.baseline.resolve(), args.promotion_receipt.resolve())
    selection = load_object(selection_path)
    pre_delete_path = args.pre_delete_route_receipt.resolve()
    pre_delete = validate_pre_delete_receipt(repo, pre_delete_path)
    if selection.get("schema_version") != "iris_repository_runtime_lightweighting_exact_archive_selection_v1":
        raise LifecycleExecutionError("archive selection schema mismatch")
    if selection.get("owner") != "repository_owner_user" or selection.get("approved") is not True:
        raise LifecycleExecutionError("exact archive selection lacks owner approval")
    if selection.get("baseline_run_identity") != baseline.get("run_identity"):
        raise LifecycleExecutionError("selection baseline identity mismatch")
    if selection.get("physical_resolved_root") != repo.as_posix():
        raise LifecycleExecutionError("selection physical root mismatch")
    if selection.get("baseline_promotion_receipt_sha256") != sha256_file(args.promotion_receipt.resolve()) or selection.get("pre_delete_current_route_receipt_sha256") != sha256_file(args.pre_delete_route_receipt.resolve()):
        raise LifecycleExecutionError("selection evidence binding mismatch")
    by_path = {str(row["path"]): row for row in rows}
    selected: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for requested in selection.get("rows", []):
        path = str(requested.get("path", ""))
        if path in seen_paths:
            raise LifecycleExecutionError(f"selection contains duplicate path: {path}")
        seen_paths.add(path)
        row = by_path.get(path)
        if row is None:
            raise LifecycleExecutionError(f"selection path is outside promoted baseline: {path}")
        exact_repo_file(repo, path)
        if requested.get("sha256") != row.get("sha256"):
            raise LifecycleExecutionError(f"selection hash differs from baseline: {path}")
        for key in ("logical_artifact_id", "size_bytes"):
            if requested.get(key) != row.get(key):
                raise LifecycleExecutionError(f"selection {key} differs from baseline: {path}")
        if row.get("authority_role") in {"current_authority", "current_required_evidence"}:
            raise LifecycleExecutionError(f"current authority/required evidence cannot be archived: {path}")
        if row.get("path_access") != "readable" or not row.get("sha256"):
            raise LifecycleExecutionError(f"selection is not fully readable: {path}")
        selected.append(row)
    selected.sort(key=lambda row: str(row["path"]))
    if not selected:
        raise LifecycleExecutionError("exact archive selection is empty")
    subject = {
        "physical_resolved_root": baseline["physical_resolved_root"],
        "commit": baseline["commit"],
        "tree": baseline["tree"],
        "baseline_run_identity": baseline["run_identity"],
    }
    op_id = operation_id(subject, selected)
    current_references = live_reference_report(repo, selected)
    if current_references["live_reference_count"] != 0 or current_references["consumer_scan_hold_count"] != 0 or not all(row["zero_live_consumers"] for row in current_references["rows"]):
        raise LifecycleExecutionError("current reference graph does not prove zero live consumers")
    operation = {
        "schema_version": "iris_repository_runtime_lightweighting_archive_operation_v1",
        "operation_id": op_id,
        "physical_subject": subject,
        "selection_approval": {
            "path": selection_path.as_posix(),
            "sha256": sha256_file(selection_path),
            "owner": selection["owner"],
        },
        "pre_delete_current_route_receipt": {
            "path": pre_delete_path.as_posix(),
            "sha256": sha256_file(pre_delete_path),
        },
        "rows": [
            {
                "logical_artifact_id": row["logical_artifact_id"],
                "path": row["path"],
                "sha256": row["sha256"],
                "size_bytes": row["size_bytes"],
                "authority_role": row["authority_role"],
                "evidence_role": row["evidence_role"],
                "producer": row.get("producer"),
                "direct_consumers": row.get("direct_consumers", []),
                "transitive_consumers": row.get("transitive_consumers", []),
                "consumer_axes": row.get("consumer_axes", {}),
            }
            for row in selected
        ],
        "zero_live_reference_count": 0,
        "zero_live_reference_report": current_references,
        "lifecycle_reference_policy": current_references["reference_policy"],
        "archive_role": "archived",
        "ordinary_attempt_cleanup_excluded": True,
        "delete_eligible": False,
    }
    atomic_write_new(manifest_out, operation)
    receipt = {
        "schema_version": "iris_repository_runtime_lightweighting_archive_dry_run_receipt_v1",
        "status": "PASS",
        "operation_id": op_id,
        "physical_subject": subject,
        "operation_manifest_path": manifest_out.as_posix(),
        "operation_manifest_sha256": sha256_file(manifest_out),
        "selected_count": len(selected),
        "selected_bytes": sum(int(row["size_bytes"]) for row in selected),
        "source_modified": False,
    }
    atomic_write_new(receipt_out, receipt)


def validate_prior(
    operation: dict[str, Any],
    operation_path: Path,
    prior_path: Path,
    expected_schema: str,
) -> dict[str, Any]:
    prior = load_object(prior_path)
    if prior.get("schema_version") != expected_schema or prior.get("status") != "PASS":
        raise LifecycleExecutionError(f"prior receipt is not expected PASS: {prior_path}")
    if prior.get("operation_id") != operation.get("operation_id"):
        raise LifecycleExecutionError("prior receipt operation mismatch")
    if prior.get("physical_subject") != operation.get("physical_subject"):
        raise LifecycleExecutionError("prior receipt physical subject mismatch")
    if prior.get("operation_manifest_sha256") != sha256_file(operation_path):
        raise LifecycleExecutionError("prior receipt operation-manifest binding mismatch")
    if expected_schema == "iris_repository_runtime_lightweighting_archive_dry_run_receipt_v1":
        if (
            Path(str(prior.get("operation_manifest_path", ""))).resolve() != operation_path.resolve()
            or prior.get("selected_count") != len(operation.get("rows", []))
            or prior.get("selected_bytes")
            != sum(int(row["size_bytes"]) for row in operation.get("rows", []))
            or prior.get("source_modified") is not False
        ):
            raise LifecycleExecutionError("dry-run receipt semantic binding mismatch")
    return prior


def command_archive(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    operation_path = require_external(repo, args.operation_manifest, "archive operation manifest")
    prior_path = require_external(repo, args.prior_receipt, "archive dry-run receipt")
    operation = load_object(operation_path)
    validate_operation(operation, repo)
    validate_prior(
        operation,
        operation_path,
        prior_path,
        "iris_repository_runtime_lightweighting_archive_dry_run_receipt_v1",
    )
    archive_root = require_external(repo, args.archive_root, "cold archive root")
    receipt_out = require_external(repo, args.receipt_out, "archive receipt")
    if receipt_out.exists():
        raise LifecycleExecutionError(f"archive receipt already exists: {receipt_out}")
    if not archive_root.is_dir():
        raise LifecycleExecutionError("cold archive root must be a preallocated existing directory")
    archive_path = archive_root / f"{operation['operation_id']}.zip"
    if archive_path.exists():
        raise LifecycleExecutionError(f"archive already exists: {archive_path}")
    temporary_archive = archive_root / f".{operation['operation_id']}.{os.getpid()}.tmp"
    if temporary_archive.exists():
        raise LifecycleExecutionError(f"temporary archive already exists: {temporary_archive}")
    try:
        with zipfile.ZipFile(temporary_archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as bundle:
            for row in operation["rows"]:
                source = exact_repo_file(repo, str(row["path"]))
                if not source.is_file() or sha256_file(source) != row["sha256"] or source.stat().st_size != row["size_bytes"]:
                    raise LifecycleExecutionError(f"source changed before archive: {row['path']}")
                bundle.write(source, arcname=str(row["path"]))
            bundle.writestr("_iris_archive_operation_manifest.json", canonical_json_bytes(operation))
        os.link(temporary_archive, archive_path)
    except FileExistsError as error:
        raise LifecycleExecutionError(f"archive already exists: {archive_path}") from error
    finally:
        temporary_archive.unlink(missing_ok=True)
    receipt = {
        "schema_version": "iris_repository_runtime_lightweighting_archive_receipt_v1",
        "status": "PASS",
        "operation_id": operation["operation_id"],
        "physical_subject": operation["physical_subject"],
        "prior_receipt_sha256": sha256_file(prior_path),
        "prior_receipt_path": prior_path.as_posix(),
        "operation_manifest_sha256": sha256_file(operation_path),
        "archive_path": archive_path.as_posix(),
        "archive_sha256": sha256_file(archive_path),
        "archive_bytes": archive_path.stat().st_size,
        "retention_owner": "repository_owner_user",
        "durable_successor": "pending_archive_evidence_promotion",
        "object_reference_count": len(operation["rows"]),
        "ordinary_attempt_cleanup_excluded": True,
        "delete_eligible": False,
        "source_modified": False,
    }
    atomic_write_new(receipt_out, receipt)


def hash_zip_member(bundle: zipfile.ZipFile, name: str) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with bundle.open(name, "r") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            digest.update(chunk)
    return digest.hexdigest(), size


def command_verify(args: argparse.Namespace) -> None:
    operation = load_object(args.operation_manifest.resolve())
    repo = validate_operation(operation)
    operation_path = require_external(repo, args.operation_manifest, "archive operation manifest")
    prior_path = require_external(repo, args.prior_receipt, "archive receipt")
    receipt_out = require_external(repo, args.receipt_out, "archive verify receipt")
    prior = validate_prior(
        operation,
        operation_path,
        prior_path,
        "iris_repository_runtime_lightweighting_archive_receipt_v1",
    )
    archive = Path(str(prior["archive_path"])).resolve()
    if prior.get("operation_manifest_sha256") != sha256_file(operation_path):
        raise LifecycleExecutionError("archive receipt operation-manifest binding mismatch")
    if sha256_file(archive) != prior.get("archive_sha256"):
        raise LifecycleExecutionError("cold archive hash mismatch")
    with zipfile.ZipFile(archive, "r") as bundle:
        name_counts = Counter(bundle.namelist())
        expected = {str(row["path"]) for row in operation["rows"]} | {"_iris_archive_operation_manifest.json"}
        if set(name_counts) != expected or any(name_counts[name] != 1 for name in expected):
            raise LifecycleExecutionError("archive must contain exactly one of every expected member")
        embedded_manifest = bundle.read("_iris_archive_operation_manifest.json")
        expected_manifest = canonical_json_bytes(operation)
        if embedded_manifest != expected_manifest:
            raise LifecycleExecutionError("embedded archive operation manifest byte identity mismatch")
        for row in operation["rows"]:
            digest, size = hash_zip_member(bundle, str(row["path"]))
            if digest != row["sha256"] or size != row["size_bytes"]:
                raise LifecycleExecutionError(f"archive member mismatch: {row['path']}")
    receipt = {
        "schema_version": "iris_repository_runtime_lightweighting_archive_verify_receipt_v1",
        "status": "PASS",
        "operation_id": operation["operation_id"],
        "physical_subject": operation["physical_subject"],
        "prior_receipt_sha256": sha256_file(prior_path),
        "prior_receipt_path": prior_path.as_posix(),
        "operation_manifest_sha256": sha256_file(operation_path),
        "archive_path": archive.as_posix(),
        "archive_sha256": prior["archive_sha256"],
        "verified_file_count": len(operation["rows"]),
        "verified_member_count": len(operation["rows"]) + 1,
        "embedded_operation_manifest_sha256": hashlib.sha256(expected_manifest).hexdigest(),
        "exactly_one_of_each_expected_member": True,
        "full_manifest_verification": True,
    }
    atomic_write_new(receipt_out, receipt)


def command_restore_verify(args: argparse.Namespace) -> None:
    operation = load_object(args.operation_manifest.resolve())
    repo = validate_operation(operation)
    operation_path = require_external(repo, args.operation_manifest, "archive operation manifest")
    prior_path = require_external(repo, args.prior_receipt, "archive verify receipt")
    receipt_out = require_external(repo, args.receipt_out, "restore verify receipt")
    verify_receipt = validate_prior(
        operation,
        operation_path,
        prior_path,
        "iris_repository_runtime_lightweighting_archive_verify_receipt_v1",
    )
    archive_receipt_path = prior_path.with_name("archive_receipt.json")
    archive_receipt = load_object(archive_receipt_path)
    if sha256_file(archive_receipt_path) != verify_receipt.get("prior_receipt_sha256"):
        raise LifecycleExecutionError("restore verification archive receipt binding mismatch")
    if verify_receipt.get("operation_manifest_sha256") != sha256_file(operation_path):
        raise LifecycleExecutionError("verify receipt operation-manifest binding mismatch")
    archive = Path(str(archive_receipt["archive_path"])).resolve()
    if not archive.is_file() or sha256_file(archive) != archive_receipt.get("archive_sha256") or archive_receipt.get("archive_sha256") != verify_receipt.get("archive_sha256"):
        raise LifecycleExecutionError("restore verification archive object mismatch")
    restore_root = require_external(repo, args.restore_root, "restore root")
    if not restore_root.is_dir():
        raise LifecycleExecutionError("restore root must be a preallocated existing directory")
    if any(restore_root.iterdir()):
        raise LifecycleExecutionError("restore root must be empty")
    with zipfile.ZipFile(archive, "r") as bundle:
        for row in operation["rows"]:
            target = (restore_root / Path(*PurePosixPath(str(row["path"])).parts)).resolve()
            try:
                target.relative_to(restore_root)
            except ValueError as error:
                raise LifecycleExecutionError(f"restore target escapes root: {row['path']}") from error
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(str(row["path"]), "r") as source, target.open("xb") as output:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
            if sha256_file(target) != row["sha256"] or target.stat().st_size != row["size_bytes"]:
                raise LifecycleExecutionError(f"restored member mismatch: {row['path']}")
    receipt = {
        "schema_version": "iris_repository_runtime_lightweighting_restore_verify_receipt_v1",
        "status": "PASS",
        "operation_id": operation["operation_id"],
        "physical_subject": operation["physical_subject"],
        "prior_receipt_sha256": sha256_file(prior_path),
        "prior_receipt_path": prior_path.as_posix(),
        "operation_manifest_sha256": sha256_file(operation_path),
        "archive_receipt_sha256": sha256_file(archive_receipt_path),
        "archive_path": archive.as_posix(),
        "restore_root": restore_root.as_posix(),
        "restored_file_count": len(operation["rows"]),
        "all_sha256_verified": True,
        "retention_owner": "repository_owner_user",
        "durable_successor": "pending_archive_evidence_promotion",
        "object_reference_count": len(operation["rows"]),
        "ordinary_attempt_cleanup_excluded": True,
        "delete_eligible": False,
    }
    atomic_write_new(receipt_out, receipt)


def git_text(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise LifecycleExecutionError(completed.stderr.strip())
    return completed.stdout.strip()


def evaluate_delete_prerequisites(
    repo: Path,
    *,
    baseline_path: Path,
    operation_path: Path,
    archive_path: Path,
    promotion_path: Path,
    archive_evidence_commit: str,
    pre_delete_path: Path,
    approval_path: Path,
) -> dict[str, Any]:
    durable_root = (
        repo / "Iris/_docs/refactor/repository_runtime_lightweighting"
    ).resolve()
    expected_baseline = (durable_root / "baseline_inventory.json").resolve()
    expected_baseline_promotion = expected_baseline.with_name("baseline_promotion_receipt.json")
    if baseline_path.resolve() != expected_baseline or not expected_baseline_promotion.is_file():
        raise LifecycleExecutionError("delete gate requires the exact durable baseline/promotion paths")
    expected_operation = (durable_root / "archive_operation_manifest.json").resolve()
    expected_archive = (durable_root / "archive_restore_receipt.json").resolve()
    expected_archive_promotion = (durable_root / "archive_promotion_receipt.json").resolve()
    if (
        operation_path.resolve() != expected_operation
        or archive_path.resolve() != expected_archive
        or promotion_path.resolve() != expected_archive_promotion
    ):
        raise LifecycleExecutionError(
            "delete gate requires the exact durable archive evidence paths"
        )
    baseline, baseline_rows = validate_baseline(
        repo,
        expected_baseline,
        expected_baseline_promotion,
    )
    operation = load_object(operation_path)
    validate_operation(operation, repo)
    archive = load_object(archive_path)
    promotion = load_object(promotion_path)
    pre_delete = validate_pre_delete_receipt(repo, pre_delete_path)
    approval = load_object(approval_path)
    if Path(str(operation.get("physical_subject", {}).get("physical_resolved_root", ""))).resolve() != repo:
        raise LifecycleExecutionError("delete operation physical root mismatch")
    if operation.get("physical_subject", {}).get("baseline_run_identity") != baseline.get("run_identity"):
        raise LifecycleExecutionError("delete operation/baseline mismatch")
    baseline_by_path = {str(row.get("path", "")): row for row in baseline_rows}
    if len(baseline_by_path) != len(baseline_rows):
        raise LifecycleExecutionError("promoted baseline manifest contains duplicate paths")
    operation_rows = operation.get("rows", [])
    for operation_row in operation_rows:
        baseline_row = baseline_by_path.get(str(operation_row.get("path", "")))
        if baseline_row is None:
            raise LifecycleExecutionError("delete operation contains a path outside the promoted baseline")
        for key in (
            "logical_artifact_id",
            "path",
            "sha256",
            "size_bytes",
            "authority_role",
            "evidence_role",
            "producer",
            "direct_consumers",
            "transitive_consumers",
            "consumer_axes",
        ):
            if operation_row.get(key) != baseline_row.get(key):
                raise LifecycleExecutionError(
                    f"delete operation row differs from promoted baseline: {operation_row.get('path')}:{key}"
                )
        if (
            baseline_row.get("path_access") != "readable"
            or baseline_row.get("authority_role") in {"current_authority", "current_required_evidence"}
        ):
            raise LifecycleExecutionError(
                f"delete operation baseline row is not archive eligible: {operation_row.get('path')}"
            )
    selection_binding = operation.get("selection_approval", {})
    selection_path = require_external(
        repo,
        Path(str(selection_binding.get("path", ""))),
        "retained owner archive selection",
    )
    if not selection_path.is_file() or selection_binding.get("sha256") != sha256_file(selection_path):
        raise LifecycleExecutionError("delete operation owner-selection identity mismatch")
    selection = load_object(selection_path)
    if (
        selection.get("schema_version") != "iris_repository_runtime_lightweighting_exact_archive_selection_v1"
        or selection.get("owner") != "repository_owner_user"
        or selection.get("approved") is not True
        or selection_binding.get("owner") != selection.get("owner")
        or selection.get("physical_resolved_root") != repo.as_posix()
        or selection.get("baseline_run_identity") != baseline.get("run_identity")
        or selection.get("baseline_promotion_receipt_sha256")
        != sha256_file(expected_baseline_promotion)
        or selection.get("pre_delete_current_route_receipt_sha256") != sha256_file(pre_delete_path)
    ):
        raise LifecycleExecutionError("delete operation retained owner selection authority mismatch")
    selection_rows = selection.get("rows")
    if not isinstance(selection_rows, list) or len(selection_rows) != len(operation_rows):
        raise LifecycleExecutionError("delete operation retained owner selection row count mismatch")
    selected_by_path = {str(row.get("path", "")): row for row in selection_rows if isinstance(row, dict)}
    if len(selected_by_path) != len(selection_rows) or set(selected_by_path) != {
        str(row.get("path", "")) for row in operation_rows
    }:
        raise LifecycleExecutionError("delete operation retained owner selection path set mismatch")
    for operation_row in operation_rows:
        selected = selected_by_path[str(operation_row["path"])]
        for key in ("logical_artifact_id", "path", "sha256", "size_bytes"):
            if selected.get(key) != operation_row.get(key):
                raise LifecycleExecutionError(
                    f"delete operation retained owner selection row mismatch: {operation_row['path']}:{key}"
                )
    if archive.get("schema_version") != "iris_repository_runtime_lightweighting_restore_verify_receipt_v1" or archive.get("status") != "PASS" or archive.get("all_sha256_verified") is not True:
        raise LifecycleExecutionError("durable archive restore receipt is not PASS")
    if archive.get("operation_id") != operation.get("operation_id") or archive.get("physical_subject") != operation.get("physical_subject") or archive.get("operation_manifest_sha256") != sha256_file(operation_path):
        raise LifecycleExecutionError("durable archive restore receipt binding mismatch")
    if (
        promotion.get("schema_version") != "iris_repository_runtime_lightweighting_archive_promotion_v1"
        or promotion.get("mode") != "archive"
        or promotion.get("byte_identity_verified") is not True
    ):
        raise LifecycleExecutionError("archive promotion receipt is invalid")
    if promotion.get("physical_subject") != operation.get("physical_subject"):
        raise LifecycleExecutionError("archive promotion physical subject mismatch")
    promoted = {
        Path(str(row.get("destination_path", ""))).name: row
        for row in promotion.get("promoted_files", [])
    }
    if promoted.get("archive_operation_manifest.json", {}).get("destination_sha256") != sha256_file(operation_path):
        raise LifecycleExecutionError("archive promotion operation-manifest binding mismatch")
    if promoted.get("archive_restore_receipt.json", {}).get("destination_sha256") != sha256_file(archive_path):
        raise LifecycleExecutionError("archive promotion restore-receipt binding mismatch")
    source_chain = promotion.get("source_chain", [])
    if len(source_chain) != 4 or source_chain[-1].get("sha256") != sha256_file(archive_path):
        raise LifecycleExecutionError("archive promotion source chain mismatch")
    chain_paths: list[Path] = []
    for binding in source_chain:
        if not isinstance(binding, dict):
            raise LifecycleExecutionError("archive promotion source-chain row is malformed")
        path = Path(str(binding.get("path", ""))).resolve()
        if not path.is_file() or binding.get("sha256") != sha256_file(path):
            raise LifecycleExecutionError("archive promotion retained source-chain identity mismatch")
        chain_paths.append(path)
    source_operation_path = Path(
        str(promoted.get("archive_operation_manifest.json", {}).get("source_path", ""))
    ).resolve()
    if (
        not source_operation_path.is_file()
        or sha256_file(source_operation_path) != sha256_file(operation_path)
    ):
        raise LifecycleExecutionError("archive promotion retained source operation identity mismatch")
    try:
        revalidated_chain = validate_archive_chain(source_operation_path, *chain_paths[1:])
    except (PromotionError, OSError, ValueError, json.JSONDecodeError) as error:
        raise LifecycleExecutionError(f"archive promotion full source-chain revalidation failed: {error}") from error
    if revalidated_chain != [
        {"path": path.as_posix(), "sha256": sha256_file(path)} for path in chain_paths
    ]:
        raise LifecycleExecutionError("archive promotion full source-chain proof differs at delete time")
    operation_pre_delete = operation.get("pre_delete_current_route_receipt", {})
    if (
        Path(str(operation_pre_delete.get("path", ""))).resolve() != pre_delete_path.resolve()
        or operation_pre_delete.get("sha256") != sha256_file(pre_delete_path)
    ):
        raise LifecycleExecutionError("archive operation pre-delete receipt binding mismatch")
    if approval.get("schema_version") != "iris_repository_runtime_lightweighting_post_archive_delete_approval_v1":
        raise LifecycleExecutionError("post-archive delete approval schema mismatch")
    if approval.get("owner") != "repository_owner_user" or approval.get("approved") is not True:
        raise LifecycleExecutionError("post-archive exact delete lacks owner approval")
    if approval.get("archive_evidence_commit") != archive_evidence_commit:
        raise LifecycleExecutionError("delete approval commit mismatch")
    if approval.get("operation_id") != operation.get("operation_id"):
        raise LifecycleExecutionError("delete approval operation mismatch")
    expected_approval_bindings = {
        "archive_operation_manifest_sha256": sha256_file(operation_path),
        "archive_restore_receipt_sha256": sha256_file(archive_path),
        "archive_promotion_receipt_sha256": sha256_file(promotion_path),
        "pre_delete_current_route_receipt_sha256": sha256_file(pre_delete_path),
    }
    for key, expected in expected_approval_bindings.items():
        if approval.get(key) != expected:
            raise LifecycleExecutionError(f"delete approval evidence binding mismatch: {key}")
    approved_paths = sorted(str(path) for path in approval.get("exact_paths", []))
    operation_paths = sorted(str(row["path"]) for row in operation.get("rows", []))
    if approved_paths != operation_paths:
        raise LifecycleExecutionError("delete approval exact path set mismatch")
    commit = git_text(repo, "rev-parse", f"{archive_evidence_commit}^{{commit}}")
    archive_ancestry = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", commit, "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if archive_ancestry.returncode != 0:
        raise LifecycleExecutionError(
            "archive evidence commit is not an ancestor of physical HEAD"
        )
    for name, path in (
        ("archive_operation_manifest.json", operation_path),
        ("archive_restore_receipt.json", archive_path),
        ("archive_promotion_receipt.json", promotion_path),
    ):
        relative = path.relative_to(repo).as_posix()
        evidence_blob = subprocess.run(
            ["git", "-C", str(repo), "show", f"{commit}:{relative}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        head_blob = subprocess.run(
            ["git", "-C", str(repo), "show", f"HEAD:{relative}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        working_hash = sha256_file(path)
        if (
            evidence_blob.returncode != 0
            or head_blob.returncode != 0
            or hashlib.sha256(evidence_blob.stdout).hexdigest() != working_hash
            or hashlib.sha256(head_blob.stdout).hexdigest() != working_hash
        ):
            raise LifecycleExecutionError(f"archive evidence commit binding mismatch: {name}")
    if operation.get("zero_live_reference_count") != 0:
        raise LifecycleExecutionError("operation contains live references")
    references = live_reference_report(repo, operation.get("rows", []))
    if references["live_reference_count"] != 0 or references["consumer_scan_hold_count"] != 0 or not all(row["zero_live_consumers"] for row in references["rows"]):
        raise LifecycleExecutionError("final reference graph does not prove zero live consumers")
    if references.get("reference_policy") != operation.get("lifecycle_reference_policy"):
        raise LifecycleExecutionError("delete-time reference policy differs from archive operation")
    return {
        "operation_id": operation["operation_id"],
        "physical_subject": operation["physical_subject"],
        "archive_evidence_commit": commit,
        "zero_live_reference_report": references,
        "input_bindings": {
            "baseline": {"path": baseline_path.as_posix(), "sha256": sha256_file(baseline_path)},
            "operation_manifest": {"path": operation_path.as_posix(), "sha256": sha256_file(operation_path)},
            "archive_restore_receipt": {"path": archive_path.as_posix(), "sha256": sha256_file(archive_path)},
            "archive_promotion_receipt": {"path": promotion_path.as_posix(), "sha256": sha256_file(promotion_path)},
            "pre_delete_current_route_receipt": {"path": pre_delete_path.as_posix(), "sha256": sha256_file(pre_delete_path)},
            "owner_approval": {"path": approval_path.as_posix(), "sha256": sha256_file(approval_path)},
        },
    }


def command_validate_delete(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    facts = evaluate_delete_prerequisites(
        repo,
        baseline_path=args.baseline.resolve(),
        operation_path=args.operation_manifest.resolve(),
        archive_path=args.archive_receipt.resolve(),
        promotion_path=args.archive_promotion_receipt.resolve(),
        archive_evidence_commit=args.archive_evidence_commit,
        pre_delete_path=args.pre_delete_route_receipt.resolve(),
        approval_path=args.approval.resolve(),
    )
    receipt = {
        "schema_version": "iris_repository_runtime_lightweighting_delete_prerequisite_v1",
        "status": "PASS",
        **facts,
        "operation_manifest_sha256": facts["input_bindings"]["operation_manifest"]["sha256"],
        "archive_restore_receipt_sha256": facts["input_bindings"]["archive_restore_receipt"]["sha256"],
        "archive_promotion_receipt_sha256": facts["input_bindings"]["archive_promotion_receipt"]["sha256"],
        "pre_delete_current_route_receipt_sha256": facts["input_bindings"]["pre_delete_current_route_receipt"]["sha256"],
        "approval_sha256": facts["input_bindings"]["owner_approval"]["sha256"],
        "zero_live_reference_count": 0,
        "exact_leaf_count": len(load_object(args.operation_manifest.resolve())["rows"]),
    }
    atomic_write_new(require_external(repo, args.out, "delete prerequisite receipt"), receipt)


def command_delete(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    operation = load_object(args.operation_manifest.resolve())
    validate_operation(operation, repo)
    prerequisite = load_object(args.prerequisite_receipt.resolve())
    if prerequisite.get("schema_version") != "iris_repository_runtime_lightweighting_delete_prerequisite_v1" or prerequisite.get("status") != "PASS":
        raise LifecycleExecutionError("delete prerequisite receipt is not PASS")
    if prerequisite.get("operation_id") != operation.get("operation_id"):
        raise LifecycleExecutionError("delete prerequisite operation mismatch")
    if prerequisite.get("operation_manifest_sha256") != sha256_file(args.operation_manifest.resolve()):
        raise LifecycleExecutionError("operation manifest changed after prerequisite validation")
    if prerequisite.get("physical_subject") != operation.get("physical_subject"):
        raise LifecycleExecutionError("delete prerequisite physical subject mismatch")
    bindings = prerequisite.get("input_bindings", {})
    required_bindings = (
        "baseline",
        "operation_manifest",
        "archive_restore_receipt",
        "archive_promotion_receipt",
        "pre_delete_current_route_receipt",
        "owner_approval",
    )
    for key in required_bindings:
        binding = bindings.get(key, {})
        path = Path(str(binding.get("path", ""))).resolve()
        if not path.is_file() or sha256_file(path) != binding.get("sha256"):
            raise LifecycleExecutionError(f"delete prerequisite input binding mismatch: {key}")
    if Path(str(bindings["operation_manifest"]["path"])).resolve() != args.operation_manifest.resolve():
        raise LifecycleExecutionError("delete operation manifest path differs from prerequisite")
    facts = evaluate_delete_prerequisites(
        repo,
        baseline_path=Path(bindings["baseline"]["path"]).resolve(),
        operation_path=args.operation_manifest.resolve(),
        archive_path=Path(bindings["archive_restore_receipt"]["path"]).resolve(),
        promotion_path=Path(bindings["archive_promotion_receipt"]["path"]).resolve(),
        archive_evidence_commit=str(prerequisite["archive_evidence_commit"]),
        pre_delete_path=Path(bindings["pre_delete_current_route_receipt"]["path"]).resolve(),
        approval_path=Path(bindings["owner_approval"]["path"]).resolve(),
    )
    if facts["zero_live_reference_report"]["report_sha256"] != prerequisite.get("zero_live_reference_report", {}).get("report_sha256"):
        raise LifecycleExecutionError("delete-time reference graph differs from prerequisite")
    receipt_out = require_external(repo, args.receipt_out, "delete receipt")
    if receipt_out.exists():
        raise LifecycleExecutionError(f"delete receipt already exists: {receipt_out}")
    baseline_path = Path(str(bindings["baseline"]["path"])).resolve()
    baseline_manifest_path, baseline_manifest_bytes, _, baseline_manifest_representation = (
        durable_lifecycle_source(baseline_path)
    )
    baseline_sha256 = sha256_file(baseline_path)
    baseline_manifest_sha256 = evidence_raw_sha256(baseline_manifest_bytes)
    validated_candidate_delta_allowset = build_validated_candidate_delta_allowset(
        repo,
        load_object(baseline_path),
        load_object(Path(str(bindings["pre_delete_current_route_receipt"]["path"])).resolve()),
    )
    deleted: list[dict[str, Any]] = []
    for row in operation["rows"]:
        target = exact_repo_file(repo, str(row["path"]))
        require_exact_regular_file(target, row, "delete preflight")
    for row in operation["rows"]:
        target = exact_repo_file(repo, str(row["path"]))
        require_exact_regular_file(target, row, "delete immediate pre-unlink")
        target.unlink()
        if target.exists():
            raise LifecycleExecutionError(f"delete target still exists: {row['path']}")
        deleted.append({"path": row["path"], "sha256": row["sha256"], "size_bytes": row["size_bytes"]})
    receipt = {
        "schema_version": "iris_repository_runtime_lightweighting_delete_receipt_v1",
        "status": "PASS",
        "operation_id": operation["operation_id"],
        "physical_subject": operation["physical_subject"],
        "prior_receipt_sha256": sha256_file(args.prerequisite_receipt.resolve()),
        "operation_manifest_sha256": sha256_file(args.operation_manifest.resolve()),
        "baseline": {
            "path": baseline_path.as_posix(),
            "sha256": baseline_sha256,
        },
        "baseline_artifact_manifest": {
            "path": baseline_manifest_path.as_posix(),
            "representation": baseline_manifest_representation,
            "sha256": baseline_manifest_sha256,
        },
        "validated_candidate_delta_allowset": validated_candidate_delta_allowset,
        "deleted": deleted,
        "deleted_bytes": sum(int(row["size_bytes"]) for row in deleted),
        "recoverable_from_verified_cold_archive": True,
    }
    atomic_write_new(receipt_out, receipt)


def command_post_delete(args: argparse.Namespace) -> None:
    repo = args.repo.resolve()
    baseline = load_object(args.baseline.resolve())
    operation = load_object(args.operation_manifest.resolve())
    validate_operation(operation, repo)
    prior = load_object(args.prior_receipt.resolve())
    if prior.get("schema_version") != "iris_repository_runtime_lightweighting_delete_receipt_v1" or prior.get("status") != "PASS" or prior.get("operation_id") != operation.get("operation_id"):
        raise LifecycleExecutionError("delete receipt mismatch")
    if prior.get("operation_manifest_sha256") != sha256_file(args.operation_manifest.resolve()):
        raise LifecycleExecutionError("delete receipt operation-manifest binding mismatch")
    baseline_path = args.baseline.resolve()
    baseline_binding = prior.get("baseline", {})
    if Path(str(baseline_binding.get("path", ""))).resolve() != baseline_path or baseline_binding.get("sha256") != sha256_file(baseline_path):
        raise LifecycleExecutionError("delete receipt baseline binding mismatch")
    baseline_manifest, baseline_manifest_bytes, baseline_rows, baseline_manifest_representation = (
        durable_lifecycle_source(baseline_path)
    )
    manifest_binding = prior.get("baseline_artifact_manifest", {})
    if (
        Path(str(manifest_binding.get("path", ""))).resolve() != baseline_manifest
        or manifest_binding.get("sha256") != evidence_raw_sha256(baseline_manifest_bytes)
        or manifest_binding.get("representation", "v1") != baseline_manifest_representation
    ):
        raise LifecycleExecutionError("delete receipt baseline artifact-manifest binding mismatch")
    allowset = prior.get("validated_candidate_delta_allowset")
    if (
        not isinstance(allowset, dict)
        or allowset.get("schema_version")
        != "iris_repository_runtime_lightweighting_validated_candidate_delta_allowset_v1"
        or allowset.get("baseline_commit") != baseline.get("commit")
        or not isinstance(allowset.get("rows"), list)
    ):
        raise LifecycleExecutionError(
            "delete receipt validated-candidate delta allowset is malformed"
        )
    current_head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if (
        current_head.returncode != 0
        or current_head.stdout.strip() != allowset.get("physical_head_commit")
    ):
        raise LifecycleExecutionError(
            "physical HEAD changed after validated-candidate allowset capture"
        )
    durable_bindings: dict[str, dict[str, Any]] = {}
    for binding in allowset["rows"]:
        if (
            not isinstance(binding, dict)
            or not isinstance(binding.get("path"), str)
            or binding["path"] in durable_bindings
            or binding.get("transition_phase")
            not in {
                "validated_common_candidate",
                "post_validation_durable_evidence",
                "validated_common_then_post_validation",
            }
            or not valid_sha256(binding.get("sha256"))
            or not isinstance(binding.get("size_bytes"), int)
            or not str(binding.get("expected_physical_head_git_blob_id", ""))
        ):
            raise LifecycleExecutionError(
                "delete receipt validated-candidate delta allowset is malformed"
            )
        durable_bindings[binding["path"]] = binding
    unexpected_existing = [row["path"] for row in operation["rows"] if exact_repo_file(repo, str(row["path"])).exists()]
    if unexpected_existing:
        raise LifecycleExecutionError(f"deleted paths still exist: {unexpected_existing}")
    current_rows, _ = build_rows(repo)
    baseline_by_path = {str(row["path"]): row for row in baseline_rows}
    current_by_path = {str(row["path"]): row for row in current_rows}
    selected_paths = {str(row["path"]) for row in operation["rows"]}
    for path, binding in durable_bindings.items():
        current_row = current_by_path.get(path)
        current_path = exact_repo_file(repo, path)
        current_blob = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "hash-object",
                f"--path={path}",
                str(current_path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if (
            current_row is None
            or current_row.get("vcs_state") != "tracked"
            or binding.get("sha256") != current_row.get("sha256")
            or int(binding.get("size_bytes", -1)) != int(current_row.get("size_bytes", 0))
            or current_blob.returncode != 0
            or current_blob.stdout.strip()
            != binding.get("expected_physical_head_git_blob_id")
        ):
            raise LifecycleExecutionError(
                f"post-delete validated candidate binding mismatch: {path}"
            )
    unexpected: list[dict[str, Any]] = []
    approved_changed: list[dict[str, Any]] = []
    for path, baseline_row in baseline_by_path.items():
        if path in selected_paths:
            continue
        current_row = current_by_path.get(path)
        if current_row is None:
            materialized_children = {
                current_path
                for current_path in current_by_path
                if current_path.startswith(path.rstrip("/") + "/")
            }
            if (
                baseline_row.get("path_access") == "missing_referenced"
                and materialized_children
                and materialized_children.issubset(durable_bindings)
            ):
                continue
            unexpected.append({"path": path, "change": "unexpectedly_missing"})
        elif baseline_row.get("sha256") != current_row.get("sha256") or baseline_row.get("size_bytes") != current_row.get("size_bytes") or baseline_row.get("path_access") != current_row.get("path_access"):
            binding = durable_bindings.get(path, {})
            if path in durable_bindings and binding.get("sha256") == current_row.get("sha256") and int(binding.get("size_bytes", -1)) == int(current_row.get("size_bytes", 0)):
                approved_changed.append(
                    {
                        "path": path,
                        "before_sha256": baseline_row.get("sha256"),
                        "after_sha256": current_row.get("sha256"),
                        "before_size_bytes": baseline_row.get("size_bytes"),
                        "after_size_bytes": current_row.get("size_bytes"),
                        "byte_delta": int(current_row.get("size_bytes", 0)) - int(baseline_row.get("size_bytes", 0)),
                    }
                )
            else:
                unexpected.append({"path": path, "change": "unexpectedly_changed"})
    added_paths = sorted(set(current_by_path) - set(baseline_by_path))
    approved_added: list[dict[str, Any]] = []
    for path in added_paths:
        row = current_by_path[path]
        binding = durable_bindings.get(path, {})
        if path in durable_bindings and binding.get("sha256") == row.get("sha256") and int(binding.get("size_bytes", -1)) == int(row.get("size_bytes", 0)):
            approved_added.append({"path": path, "sha256": row.get("sha256"), "size_bytes": row.get("size_bytes")})
        else:
            unexpected.append({"path": path, "change": "unexpectedly_added"})
    if unexpected:
        raise LifecycleExecutionError(f"post-delete census found unexpected path delta: {unexpected[:5]}")
    current_bytes = sum(int(row.get("size_bytes", 0)) for row in current_rows)
    expected_deleted_bytes = sum(int(row["size_bytes"]) for row in operation["rows"])
    approved_added_bytes = sum(int(row["size_bytes"]) for row in approved_added)
    approved_changed_bytes = sum(int(row["byte_delta"]) for row in approved_changed)
    approved_durable_delta_bytes = approved_added_bytes + approved_changed_bytes
    if int(baseline["physical_bytes"]) + approved_durable_delta_bytes - current_bytes != expected_deleted_bytes:
        raise LifecycleExecutionError("post-delete physical byte delta differs from exact deletion")
    receipt = {
        "schema_version": "iris_repository_runtime_lightweighting_post_delete_census_v1",
        "status": "PASS",
        "operation_id": operation["operation_id"],
        "physical_subject": operation["physical_subject"],
        "baseline_physical_bytes": baseline["physical_bytes"],
        "final_physical_bytes": current_bytes,
        "physical_byte_delta": current_bytes - int(baseline["physical_bytes"]),
        "expected_deleted_bytes": expected_deleted_bytes,
        "approved_durable_addition_count": len(approved_added),
        "approved_durable_addition_bytes": approved_added_bytes,
        "approved_durable_additions": approved_added,
        "approved_durable_change_count": len(approved_changed),
        "approved_durable_change_bytes": approved_changed_bytes,
        "approved_durable_changes": approved_changed,
        "approved_durable_delta_bytes": approved_durable_delta_bytes,
        "validated_candidate_delta_allowset": {
            "baseline_commit": allowset["baseline_commit"],
            "validated_subject_commit": allowset.get("validated_subject_commit"),
            "physical_head_commit": allowset.get("physical_head_commit"),
            "bound_path_count": len(durable_bindings),
        },
        "deleted_path_count": len(operation["rows"]),
        "unexpected_existing_count": 0,
        "unexpected_path_delta_count": len(unexpected),
        "unexpected_path_deltas": unexpected,
        "prior_receipt_sha256": sha256_file(args.prior_receipt.resolve()),
    }
    atomic_write_new(require_external(repo, args.receipt_out, "post-delete receipt"), receipt)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    dry = sub.add_parser("dry-run")
    dry.add_argument("--repo", type=Path, required=True)
    dry.add_argument("--baseline", type=Path, required=True)
    dry.add_argument("--promotion-receipt", type=Path, required=True)
    dry.add_argument("--pre-delete-route-receipt", type=Path, required=True)
    dry.add_argument("--selection", type=Path, required=True)
    dry.add_argument("--manifest-out", type=Path, required=True)
    dry.add_argument("--receipt-out", type=Path, required=True)
    archive = sub.add_parser("archive")
    archive.add_argument("--repo", type=Path, required=True)
    archive.add_argument("--operation-manifest", type=Path, required=True)
    archive.add_argument("--prior-receipt", type=Path, required=True)
    archive.add_argument("--archive-root", type=Path, required=True)
    archive.add_argument("--receipt-out", type=Path, required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--operation-manifest", type=Path, required=True)
    verify.add_argument("--prior-receipt", type=Path, required=True)
    verify.add_argument("--receipt-out", type=Path, required=True)
    restore = sub.add_parser("restore-verify")
    restore.add_argument("--operation-manifest", type=Path, required=True)
    restore.add_argument("--prior-receipt", type=Path, required=True)
    restore.add_argument("--restore-root", type=Path, required=True)
    restore.add_argument("--receipt-out", type=Path, required=True)
    prereq = sub.add_parser("validate-delete-prerequisites")
    prereq.add_argument("--repo", type=Path, required=True)
    prereq.add_argument("--baseline", type=Path, required=True)
    prereq.add_argument("--operation-manifest", type=Path, required=True)
    prereq.add_argument("--archive-receipt", type=Path, required=True)
    prereq.add_argument("--archive-promotion-receipt", type=Path, required=True)
    prereq.add_argument("--archive-evidence-commit", required=True)
    prereq.add_argument("--pre-delete-route-receipt", type=Path, required=True)
    prereq.add_argument("--approval", type=Path, required=True)
    prereq.add_argument("--out", type=Path, required=True)
    delete = sub.add_parser("delete")
    delete.add_argument("--repo", type=Path, required=True)
    delete.add_argument("--operation-manifest", type=Path, required=True)
    delete.add_argument("--prerequisite-receipt", type=Path, required=True)
    delete.add_argument("--receipt-out", type=Path, required=True)
    post = sub.add_parser("post-delete-census")
    post.add_argument("--repo", type=Path, required=True)
    post.add_argument("--baseline", type=Path, required=True)
    post.add_argument("--operation-manifest", type=Path, required=True)
    post.add_argument("--prior-receipt", type=Path, required=True)
    post.add_argument("--receipt-out", type=Path, required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    handlers = {
        "dry-run": command_dry_run,
        "archive": command_archive,
        "verify": command_verify,
        "restore-verify": command_restore_verify,
        "validate-delete-prerequisites": command_validate_delete,
        "delete": command_delete,
        "post-delete-census": command_post_delete,
    }
    handlers[args.command](args)
    print(json.dumps({"status": "PASS", "command": args.command}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (LifecycleExecutionError, OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        print(json.dumps({"status": "FAIL", "error_type": type(error).__name__, "error": str(error)}, sort_keys=True), file=sys.stderr)
        raise SystemExit(2)
