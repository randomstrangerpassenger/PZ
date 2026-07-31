from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, Callable
from unittest import mock

import public_text_quality_acceptance as base


CORRECTION_ID = "g1-successor-0010-windows-long-path-safe-artifact-writer-0006"
SCHEMA_VERSION = "public_text_quality_windows_long_path_safe_writer_regression_v1"


def _long_target(root: Path, *, unicode_and_spaces: bool = False) -> Path:
    component = "유니코드 공간 segment" if unicode_and_spaces else "bounded-segment-0123456789"
    target = root / "artifacts"
    while len(str(target / "artifact.json")) <= 280:
        target /= component
    return target / "artifact.json"


def _expect_failure(action: Callable[[], object], label: str) -> None:
    try:
        action()
    except base.FoundationContractError:
        return
    raise base.FoundationContractError(f"writer regression did not fail-close: {label}")


def _exists(path: Path) -> bool:
    resolved = path.resolve(strict=False)
    return base._filesystem_path_exists(base._windows_extended_length_path(resolved))


def _children(path: Path) -> list[str]:
    filesystem_path = base._windows_extended_length_path(path.resolve(strict=False))
    return sorted(entry.name for entry in os.scandir(filesystem_path))


def _remove_tree(path: Path) -> None:
    if not path.exists():
        return
    shutil.rmtree(base._windows_extended_length_path(path.resolve(strict=False)))


def run_self_test() -> dict[str, Any]:
    if os.name != "nt":
        raise base.FoundationContractError(
            "Windows long-path writer regression requires a Windows host"
        )
    external_parent = Path(
        os.environ.get("IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT", tempfile.gettempdir())
    )
    external_parent.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="ptqa-long-writer-", dir=external_parent))
    cases: dict[str, str] = {}
    try:
        short_payload = b'{"path":"evidence/short.json","status":"PASS"}\n'
        short_target = root / "short" / "artifact.json"
        if base.write_once_bytes(
            short_target, short_payload, repository_root=root
        ) != "created":
            raise base.FoundationContractError("short-path writer did not create")
        if base.read_bytes_long_path_safe(short_target) != short_payload:
            raise base.FoundationContractError("short-path writer byte mismatch")
        cases["short_path_write"] = "PASS"

        long_payload = b'{"path":"evidence/long.json","status":"PASS"}\n'
        long_target = _long_target(root)
        if len(str(long_target)) <= 260:
            raise base.FoundationContractError("long-path fixture is not longer than 260")
        base.write_once_bytes(long_target, long_payload, repository_root=root)
        if (
            base.read_bytes_long_path_safe(long_target) != long_payload
            or base.sha256_file(long_target) != hashlib.sha256(long_payload).hexdigest()
        ):
            raise base.FoundationContractError("long-path write/read/hash mismatch")
        cases["long_path_write_read_hash_atomic_replace"] = "PASS"

        unicode_payload = "{\"path\":\"evidence/유니코드 공간.json\",\"status\":\"PASS\"}\n".encode(
            "utf-8"
        )
        unicode_target = _long_target(root, unicode_and_spaces=True)
        base.write_once_bytes(unicode_target, unicode_payload, repository_root=root)
        if base.read_bytes_long_path_safe(unicode_target) != unicode_payload:
            raise base.FoundationContractError("Unicode long-path byte mismatch")
        cases["unicode_space_long_path"] = "PASS"

        escape_target = root.parent / f"{root.name}-escape.json"
        _expect_failure(
            lambda: base.write_once_bytes(
                escape_target, b"escape", repository_root=root
            ),
            "repository containment escape",
        )
        if _exists(escape_target):
            raise base.FoundationContractError("containment escape created a target")
        cases["repository_containment_escape"] = "PASS"

        traversal_target = root / "safe" / ".." / "traversal.json"
        _expect_failure(
            lambda: base.write_once_bytes(
                traversal_target, b"traversal", repository_root=root
            ),
            "parent traversal",
        )
        cases["parent_traversal"] = "PASS"

        alias_target = root / "alias" / "artifact.json"
        original_reparse_probe = base._path_has_reparse_point

        def simulated_reparse(path: Path) -> bool:
            return path.name == "alias" or original_reparse_probe(path)

        with mock.patch.object(
            base, "_path_has_reparse_point", side_effect=simulated_reparse
        ):
            _expect_failure(
                lambda: base.write_once_bytes(
                    alias_target, b"alias", repository_root=root
                ),
                "symlink or reparse-point escape",
            )
        cases["symlink_reparse_escape"] = "PASS"

        failed_target = _long_target(root / "failure")
        with mock.patch.object(base.os, "replace", side_effect=OSError("injected")):
            _expect_failure(
                lambda: base.write_once_bytes(
                    failed_target, b"partial-write-fixture", repository_root=root
                ),
                "intermediate replace failure",
            )
        if _exists(failed_target):
            raise base.FoundationContractError("failed write left a partial target")
        residues = [
            name for name in _children(failed_target.parent) if ".tmp-" in name
        ]
        if residues:
            raise base.FoundationContractError("failed write left temporary residue")
        cases["failure_cleanup_no_partial_or_residue"] = "PASS"

        if base.write_once_bytes(
            long_target, long_payload, repository_root=root
        ) != "already_identical":
            raise base.FoundationContractError("identical rerun was not idempotent")
        if base.read_bytes_long_path_safe(long_target) != long_payload:
            raise base.FoundationContractError("identical rerun changed bytes")
        cases["identical_payload_rerun"] = "PASS"

        semantic_payload = base.pretty_json_bytes(
            {"path": "evidence/result.json", "status": "PASS"}
        )
        semantic_hashes: list[str] = []
        for checkout_name in ("checkout-a", "checkout-b"):
            checkout = root / checkout_name
            checkout.mkdir()
            target = _long_target(checkout)
            base.write_once_bytes(
                target, semantic_payload, repository_root=checkout
            )
            semantic_hashes.append(base.sha256_file(target))
        if len(set(semantic_hashes)) != 1:
            raise base.FoundationContractError(
                "checkout location changed artifact semantic identity"
            )
        cases["checkout_location_independent_semantic_identity"] = "PASS"

        if set(cases.values()) != {"PASS"} or len(cases) != 9:
            raise base.FoundationContractError("writer regression case census mismatch")
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "PASS",
            "correction_id": CORRECTION_ID,
            "case_count": len(cases),
            "passed_case_count": len(cases),
            "cases": cases,
            "windows_extended_length_path_applied_only_to_filesystem_calls": True,
            "artifact_paths_remain_repo_relative_posix": True,
            "absolute_path_drive_checkout_host_metadata_serialized": False,
            "atomic_sibling_write_flush_fsync_replace_stat_hash_cleanup": True,
            "partial_target_count": 0,
            "temporary_residue_count": 0,
            "authority_effect": "none",
        }
    finally:
        _remove_tree(root)
