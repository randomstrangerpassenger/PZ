from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
from typing import Any, Iterable

from .acceptance_context import (
    PROTECTED_SNAPSHOT_IDENTITY_ALGORITHM_ID,
    REPO_ROOT,
    SEALED_PREREQUISITE_RAW_SHA256,
    TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID,
)
from .inputs import PublicTextInputError, load_json_bytes as load_public_text_json_bytes


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise FoundationContractError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result


def git_head() -> str:
    return run_git("rev-parse", "HEAD").stdout.strip()


def is_tracked(path: Path) -> bool:
    return (
        run_git(
            "ls-files",
            "--error-unmatch",
            "--",
            repo_relative(path),
            check=False,
        ).returncode
        == 0
    )


def is_ignored(path: Path) -> bool:
    result = run_git(
        "check-ignore", "--no-index", "-v", "--", repo_relative(path), check=False
    )
    if result.returncode != 0:
        return False
    matched_rule = result.stdout.split("\t", 1)[0].rsplit(":", 1)[-1]
    return not matched_rule.startswith("!")


def has_unstaged_delta(path: Path) -> bool:
    return bool(
        run_git("diff", "--name-only", "--", repo_relative(path)).stdout.strip()
    )


class FoundationContractError(RuntimeError):
    pass


class ExternalInputRequired(FoundationContractError):
    def __init__(self, *, input_kind: str, path: Path, details: dict[str, Any]):
        super().__init__(f"external input required: {input_kind}: {repo_relative(path)}")
        self.input_kind = input_kind
        self.path = path
        self.details = details


def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise FoundationContractError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def load_json_strict(path: Path) -> Any:
    try:
        return load_public_text_json_bytes(
            read_bytes_long_path_safe(path), label=str(path)
        )
    except (OSError, PublicTextInputError) as exc:
        raise FoundationContractError(f"cannot load strict JSON {path}: {exc}") from exc


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def pretty_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_hash(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def windows_extended_length_path(path: Path) -> str:
    """Return a host-only filesystem spelling for an already resolved path."""
    value = str(path)
    if os.name != "nt":
        return value
    if value.startswith("\\\\?\\"):
        raise FoundationContractError(
            "callers must not supply an extended-length path alias"
        )
    if value.startswith("\\\\"):
        return "\\\\?\\UNC\\" + value[2:]
    if len(value) >= 3 and value[1:3] == ":\\":
        return "\\\\?\\" + value
    raise FoundationContractError(
        "Windows artifact path must resolve to a local drive or UNC absolute path"
    )


def _unvalidated_long_path_filesystem_path(path: Path) -> str:
    try:
        resolved = path.resolve(strict=False)
    except OSError as exc:
        raise FoundationContractError(f"cannot resolve filesystem path {path}: {exc}") from exc
    return windows_extended_length_path(resolved)


def read_bytes_long_path_safe(path: Path) -> bytes:
    """Read bytes without making the host path part of artifact identity."""
    filesystem_path = _unvalidated_long_path_filesystem_path(path)
    try:
        with open(filesystem_path, "rb") as stream:
            return stream.read()
    except OSError as exc:
        raise FoundationContractError(f"cannot read {path}: {exc}") from exc


def sha256_file(path: Path) -> str:
    try:
        return sha256_bytes(read_bytes_long_path_safe(path))
    except FoundationContractError as exc:
        raise FoundationContractError(f"cannot hash {path}: {exc}") from exc


def _path_has_reparse_point(path: Path) -> bool:
    try:
        metadata = os.lstat(windows_extended_length_path(path))
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise FoundationContractError(
            f"cannot inspect artifact path component {path}: {exc}"
        ) from exc
    attributes = getattr(metadata, "st_file_attributes", 0)
    return stat.S_ISLNK(metadata.st_mode) or bool(
        attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def validated_repository_artifact_target(
    path: Path, *, repository_root: Path
) -> Path:
    raw = str(path)
    if raw.startswith("\\\\?\\"):
        raise FoundationContractError(
            "extended-length aliases are internal filesystem details only"
        )
    if ".." in path.parts:
        raise FoundationContractError("artifact target contains parent traversal")
    try:
        root = Path(os.path.abspath(str(repository_root)))
        existing_ancestor = root
        while not existing_ancestor.exists():
            parent = existing_ancestor.parent
            if parent == existing_ancestor:
                raise FoundationContractError(
                    "artifact target has no resolvable existing ancestor"
                )
            existing_ancestor = parent
        resolved_ancestor = existing_ancestor.resolve(strict=True)
        if os.path.normcase(str(existing_ancestor)) != os.path.normcase(
            str(resolved_ancestor)
        ):
            raise FoundationContractError(
                "repository root descends from a path alias or symlink"
            )
        candidate = path if path.is_absolute() else root / path
        lexical = Path(os.path.abspath(str(candidate)))
        # ``Path.resolve(strict=False)`` still asks Windows to resolve the
        # nearest existing ancestor.  A valid write-once target commonly has
        # a not-yet-created parent, and that lookup raises WinError 2.  Keep
        # the candidate lexical here and inspect every existing component for
        # aliases below instead.
        resolved = lexical
    except OSError as exc:
        raise FoundationContractError(f"cannot resolve artifact target {path}: {exc}") from exc
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise FoundationContractError(
            "artifact target resolves outside the declared repository root"
        ) from exc
    if not relative.parts:
        raise FoundationContractError("artifact target cannot be the repository root")
    if os.path.normcase(str(lexical)) != os.path.normcase(str(resolved)):
        raise FoundationContractError(
            "artifact target path alias or symlink resolution is forbidden"
        )
    current = existing_ancestor
    relative_from_existing = root.relative_to(existing_ancestor)
    for component in (*relative_from_existing.parts, *relative.parts):
        current = current / component
        if _path_has_reparse_point(current):
            raise FoundationContractError(
                "artifact target contains a symlink or reparse-point component"
            )
    return resolved


def filesystem_path_exists(filesystem_path: str) -> bool:
    try:
        os.stat(filesystem_path)
    except FileNotFoundError:
        return False
    return True


def read_filesystem_bytes(filesystem_path: str) -> bytes:
    with open(filesystem_path, "rb") as stream:
        return stream.read()


def sha256_lf_normalized_text(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise FoundationContractError(
            f"cannot read UTF-8 text for normalized hash {path}: {exc}"
        ) from exc
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return sha256_bytes(normalized.encode("utf-8"))


def normalize_text_line_endings(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def build_text_constituent_identity_from_bytes(
    *,
    repo_relative_posix_path: str,
    declared_sha256: object,
    head_blob_id: str,
    head_blob_raw: bytes,
    working_raw: bytes,
    filtered_working_blob_id: str | None,
) -> dict[str, Any]:
    pure_path = PurePosixPath(repo_relative_posix_path)
    if (
        not repo_relative_posix_path
        or pure_path.is_absolute()
        or ".." in pure_path.parts
        or "\\" in repo_relative_posix_path
    ):
        raise FoundationContractError(
            "text constituent identity path must be repo-relative POSIX"
        )
    canonical_authority = normalize_text_line_endings(head_blob_raw)
    canonical_working = normalize_text_line_endings(working_raw)
    authority_raw_sha256 = sha256_bytes(head_blob_raw)
    canonical_authority_sha256 = sha256_bytes(canonical_authority)
    allowed_representation_hashes = {
        "git_blob_raw": authority_raw_sha256,
        "lf": canonical_authority_sha256,
        "crlf": sha256_bytes(canonical_authority.replace(b"\n", b"\r\n")),
        "lone_cr": sha256_bytes(canonical_authority.replace(b"\n", b"\r")),
    }
    declared_representation_kinds = sorted(
        kind
        for kind, digest in allowed_representation_hashes.items()
        if digest == declared_sha256
    )
    git_filtered_identity = (
        filtered_working_blob_id is not None
        and filtered_working_blob_id == head_blob_id
    )
    canonical_working_identity = canonical_working == canonical_authority
    declared_matches_head_authority = bool(declared_representation_kinds)
    working_matches_head_authority = (
        git_filtered_identity or canonical_working_identity
    )
    return {
        "algorithm_id": TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID,
        "path": repo_relative_posix_path,
        "authority_source": "HEAD_git_blob_raw",
        "head_git_blob_id": head_blob_id,
        "authority_git_blob_raw_sha256": authority_raw_sha256,
        "authority_lf_canonical_sha256": canonical_authority_sha256,
        "declared_sha256": declared_sha256,
        "declared_representation_kinds": declared_representation_kinds,
        "declared_matches_head_authority": declared_matches_head_authority,
        "working_lf_canonical_sha256": sha256_bytes(canonical_working),
        "git_filtered_working_identity": git_filtered_identity,
        "canonical_working_identity": canonical_working_identity,
        "working_matches_head_authority": working_matches_head_authority,
        "json_semantic_normalization_applied": False,
        "absolute_path_or_host_metadata_in_identity": False,
        "match": (
            declared_matches_head_authority
            and working_matches_head_authority
        ),
    }


def build_protected_snapshot_identity_from_bytes(
    *,
    repo_relative_posix_path: str,
    declared_sha256: object,
    head_blob_id: str,
    head_blob_raw: bytes,
    working_raw: bytes,
    filtered_working_blob_id: str | None,
    text_attribute: str,
) -> dict[str, Any]:
    pure_path = PurePosixPath(repo_relative_posix_path)
    if (
        not repo_relative_posix_path
        or pure_path.is_absolute()
        or ".." in pure_path.parts
        or "\\" in repo_relative_posix_path
    ):
        raise FoundationContractError(
            "protected snapshot identity path must be repo-relative POSIX"
        )
    authority_raw_sha256 = sha256_bytes(head_blob_raw)
    declared_matches_head_authority = (
        isinstance(declared_sha256, str)
        and declared_sha256 == authority_raw_sha256
    )
    try:
        head_blob_raw.decode("utf-8")
    except UnicodeDecodeError:
        head_is_utf8 = False
    else:
        head_is_utf8 = b"\x00" not in head_blob_raw
    identity_kind = (
        "text_lf_canonical"
        if head_is_utf8 and text_attribute != "unset"
        else "raw_bytes"
    )
    git_filtered_identity = (
        identity_kind == "text_lf_canonical"
        and filtered_working_blob_id is not None
        and filtered_working_blob_id == head_blob_id
    )
    canonical_working_identity = (
        identity_kind == "text_lf_canonical"
        and normalize_text_line_endings(working_raw)
        == normalize_text_line_endings(head_blob_raw)
    )
    raw_working_identity = working_raw == head_blob_raw
    working_matches_head_authority = (
        git_filtered_identity or canonical_working_identity
        if identity_kind == "text_lf_canonical"
        else raw_working_identity
    )
    return {
        "algorithm_id": PROTECTED_SNAPSHOT_IDENTITY_ALGORITHM_ID,
        "path": repo_relative_posix_path,
        "identity_kind": identity_kind,
        "text_attribute": text_attribute,
        "authority_source": "HEAD_git_blob_raw",
        "head_git_blob_id": head_blob_id,
        "authority_git_blob_raw_sha256": authority_raw_sha256,
        "declared_sha256": declared_sha256,
        "declared_matches_head_authority": declared_matches_head_authority,
        "working_raw_sha256": sha256_bytes(working_raw),
        "git_filtered_working_identity": git_filtered_identity,
        "canonical_working_identity": canonical_working_identity,
        "raw_working_identity": raw_working_identity,
        "working_matches_head_authority": working_matches_head_authority,
        "json_semantic_normalization_applied": False,
        "whitespace_normalization_applied": False,
        "absolute_path_or_host_metadata_in_identity": False,
        "match": (
            declared_matches_head_authority
            and working_matches_head_authority
        ),
    }


def build_protected_snapshot_present_row_from_bytes(
    *,
    repo_relative_posix_path: str,
    declared_sha256: object,
    head_blob_id: str,
    head_blob_raw: bytes,
    working_raw: bytes,
    filtered_working_blob_id: str | None,
    text_attribute: str,
) -> dict[str, Any]:
    identity = build_protected_snapshot_identity_from_bytes(
        repo_relative_posix_path=repo_relative_posix_path,
        declared_sha256=declared_sha256,
        head_blob_id=head_blob_id,
        head_blob_raw=head_blob_raw,
        working_raw=working_raw,
        filtered_working_blob_id=filtered_working_blob_id,
        text_attribute=text_attribute,
    )
    if identity["match"] is not True:
        raise FoundationContractError(
            "protected surface stale before Publish attempt: "
            f"{repo_relative_posix_path}"
        )
    return {
        "path": repo_relative_posix_path,
        "present": True,
        "sha256": identity["authority_git_blob_raw_sha256"],
    }


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def require_exact_keys(
    value: dict[str, Any],
    *,
    required: Iterable[str],
    optional: Iterable[str] = (),
    label: str,
) -> None:
    required_set = set(required)
    allowed_set = required_set | set(optional)
    actual_set = set(value)
    missing = sorted(required_set - actual_set)
    unknown = sorted(actual_set - allowed_set)
    if missing or unknown:
        raise FoundationContractError(
            f"{label} key mismatch: missing={missing}, unknown={unknown}"
        )


def require_true_predicates(value: Any, *, label: str) -> None:
    if not isinstance(value, dict) or not value:
        raise FoundationContractError(f"{label} must be a nonempty predicate object")
    failures = sorted(key for key, predicate in value.items() if predicate is not True)
    if failures:
        raise FoundationContractError(f"{label} contains non-PASS predicates: {failures}")


def artifact_record(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FoundationContractError(f"required prerequisite artifact missing: {path}")
    if not is_tracked(path):
        raise FoundationContractError(
            f"required prerequisite artifact is untracked: {repo_relative(path)}"
        )
    ignored_by_current_rules = is_ignored(path)
    expected_sha256 = SEALED_PREREQUISITE_RAW_SHA256.get(path)
    actual_sha256 = sha256_file(path)
    if expected_sha256 is not None and actual_sha256 != expected_sha256:
        raise FoundationContractError(
            f"sealed prerequisite artifact hash mismatch: {repo_relative(path)}"
        )
    head_blob = head_blob_record(path)
    if head_blob["git_blob_working_byte_identity"] is not True:
        raise FoundationContractError(
            f"prerequisite artifact differs from its HEAD Git blob: {repo_relative(path)}"
        )
    record = {
        "path": repo_relative(path),
        "raw_sha256": actual_sha256,
        "byte_count": path.stat().st_size,
        "tracked": True,
        "ignored_by_current_rules": ignored_by_current_rules,
        "tracked_file_ignore_effect": "none",
        **head_blob,
    }
    if expected_sha256 is not None:
        record.update(
            {
                "sealed_expected_raw_sha256": expected_sha256,
                "sealed_expected_raw_sha256_match": True,
            }
        )
    return record


def head_blob_record(path: Path) -> dict[str, Any]:
    relative = repo_relative(path)
    blob_id = run_git("rev-parse", f"HEAD:{relative}").stdout.strip()
    result = subprocess.run(
        ["git", "cat-file", "blob", blob_id],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise FoundationContractError(
            f"cannot read HEAD blob for {relative}: "
            f"{result.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return {
        "path": relative,
        "git_blob_id": blob_id,
        "git_blob_sha256": sha256_bytes(result.stdout),
        "working_sha256": sha256_file(path),
        "git_blob_working_byte_identity": result.stdout == path.read_bytes(),
    }


def commit_blob_record(path: Path, commit: str) -> dict[str, Any]:
    relative = repo_relative(path)
    blob_id = run_git("rev-parse", f"{commit}:{relative}").stdout.strip()
    result = subprocess.run(
        ["git", "cat-file", "blob", blob_id],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise FoundationContractError(
            f"cannot read {commit} blob for {relative}: "
            f"{result.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return {
        "path": relative,
        "commit": commit,
        "git_blob_id": blob_id,
        "git_blob_sha256": sha256_bytes(result.stdout),
    }


def head_filtered_blob_record(path: Path) -> dict[str, Any]:
    relative = repo_relative(path)
    head_blob_id = run_git("rev-parse", f"HEAD:{relative}").stdout.strip()
    filtered_working_blob_id = run_git("hash-object", "--", relative).stdout.strip()
    result = subprocess.run(
        ["git", "cat-file", "blob", head_blob_id],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise FoundationContractError(
            f"cannot read HEAD blob for filtered identity {relative}"
        )
    return {
        "path": relative,
        "git_blob_id": head_blob_id,
        "git_blob_sha256": sha256_bytes(result.stdout),
        "working_sha256_lf_normalized": sha256_lf_normalized_text(path),
        "git_filtered_working_blob_id": filtered_working_blob_id,
        "git_filtered_working_identity": filtered_working_blob_id == head_blob_id,
        "raw_working_byte_identity_required": False,
    }


def head_text_constituent_record(
    path: Path,
    declared_sha256: object,
) -> dict[str, Any]:
    relative = repo_relative(path)
    if not path.is_file():
        raise FoundationContractError(
            f"text constituent is missing: {relative}"
        )
    if not path.resolve().is_relative_to(REPO_ROOT.resolve()):
        raise FoundationContractError(
            f"text constituent escaped repository: {relative}"
        )
    if not is_tracked(path):
        raise FoundationContractError(
            f"text constituent is untracked: {relative}"
        )
    head_blob_id = run_git("rev-parse", f"HEAD:{relative}").stdout.strip()
    result = subprocess.run(
        ["git", "cat-file", "blob", head_blob_id],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise FoundationContractError(
            f"cannot read HEAD text constituent blob: {relative}"
        )
    filtered_working_blob_id = run_git(
        "hash-object", "--", relative
    ).stdout.strip()
    return build_text_constituent_identity_from_bytes(
        repo_relative_posix_path=relative,
        declared_sha256=declared_sha256,
        head_blob_id=head_blob_id,
        head_blob_raw=result.stdout,
        working_raw=path.read_bytes(),
        filtered_working_blob_id=filtered_working_blob_id,
    )

__all__ = (
    "ExternalInputRequired", "FoundationContractError", "artifact_record",
    "build_protected_snapshot_identity_from_bytes",
    "build_protected_snapshot_present_row_from_bytes",
    "build_text_constituent_identity_from_bytes", "canonical_hash",
    "canonical_json_bytes", "commit_blob_record", "filesystem_path_exists",
    "git_head", "has_unstaged_delta", "head_blob_record",
    "head_filtered_blob_record", "head_text_constituent_record", "is_ignored",
    "is_tracked", "load_json_strict", "normalize_text_line_endings",
    "pretty_json_bytes", "read_bytes_long_path_safe", "read_filesystem_bytes",
    "reject_duplicate_pairs", "repo_relative", "require_exact_keys",
    "require_true_predicates", "run_git", "sha256_bytes", "sha256_file",
    "sha256_lf_normalized_text", "validated_repository_artifact_target",
    "windows_extended_length_path",
)
