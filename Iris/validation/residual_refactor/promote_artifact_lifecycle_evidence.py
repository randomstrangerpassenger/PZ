#!/usr/bin/env python
"""Promote verified external lifecycle evidence into the Git-visible durable sink."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, BinaryIO

from report_artifact_lifecycle import (
    LIFECYCLE_TRACKING_ADDITIONS,
    build_rows as lifecycle_build_rows,
    canonical_jsonl_bytes as lifecycle_jsonl_bytes,
    repository_identity as lifecycle_repository_identity,
    summary_for as lifecycle_summary_for,
)
from repository_evidence_codec import (
    RepositoryEvidenceCodecError,
    materialize_manifest,
    raw_sha256 as evidence_raw_sha256,
)


DURABLE_RELATIVE = Path("Iris/_docs/refactor/repository_runtime_lightweighting")
GIANT_RELATIVES = {
    "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/"
    "phase2_inventory/allowed_occurrence_inventory.json",
    "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/"
    "phase2_inventory/legacy_active_silent_occurrence_inventory.jsonl",
    "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/"
    "phase3_adjudication/occurrence_adjudication_report.json",
    "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/"
    "phase5_guard/current_surface_guard_report.json",
}
BASELINE_DURABLE_NAMES = (
    "artifact_role_manifest.jsonl",
    "baseline_inventory.json",
    "baseline_promotion_receipt.json",
)
BASELINE_PROMOTION_SCHEMAS = {
    "iris_repository_runtime_lightweighting_baseline_promotion_v1",
    "iris_repository_runtime_lightweighting_baseline_promotion_v2",
}
BASELINE_SUCCESSOR_LOCK_NAME = ".baseline-successor.lock"
BASELINE_SUCCESSOR_TEST_AUTHORITY = "artifact_lifecycle_promotion_fixture_v1"


class PromotionError(RuntimeError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PromotionError(f"expected JSON object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise PromotionError(f"expected JSON object at {path}:{line_number}")
            rows.append(value)
    return rows


def load_lifecycle_source(
    path: Path,
    view: str,
) -> tuple[bytes, list[dict[str, Any]], str]:
    try:
        return materialize_manifest(path.resolve(), view)  # type: ignore[arg-type]
    except RepositoryEvidenceCodecError as error:
        raise PromotionError(f"invalid lifecycle {view} representation: {path}") from error


def durable_baseline_lifecycle_source(destination: Path) -> tuple[Path, bytes, list[dict[str, Any]], str]:
    v1_path = destination / "artifact_role_manifest.jsonl"
    v2_root = (
        destination.parent
        / "repository_evidence_lightweighting"
        / "lifecycle_manifest_v2"
    )
    source = v1_path if v1_path.is_file() else v2_root
    payload, rows, representation = load_lifecycle_source(source, "baseline")
    return source.resolve(), payload, rows, representation


def atomic_write_new(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise PromotionError(f"destination already exists: {path}")
    temporary_prefix = path.name if path.name.startswith(".") else f".{path.name}"
    temporary = path.with_name(f"{temporary_prefix}.{os.getpid()}.tmp")
    if temporary.exists():
        raise PromotionError(f"temporary destination already exists: {temporary}")
    temporary.write_bytes(payload)
    if (
        path.name.startswith(".baseline-successor-")
        and path.name.endswith(".journal.json")
        and baseline_successor_test_injection("IRIS_BASELINE_SUCCESSOR_CRASH_AFTER_JOURNAL_TEMP") == "1"
    ):
        os._exit(83)
    try:
        os.link(temporary, path)
    except FileExistsError as error:
        raise PromotionError(f"destination already exists: {path}") from error
    finally:
        temporary.unlink(missing_ok=True)


def exact_copy_new(source: Path, destination: Path) -> dict[str, Any]:
    if not source.is_file():
        raise PromotionError(f"source is missing: {source}")
    source_hash = sha256_file(source)
    source_size = source.stat().st_size
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise PromotionError(f"destination already exists: {destination}")
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    if temporary.exists():
        raise PromotionError(f"temporary destination already exists: {temporary}")
    with source.open("rb") as input_handle, temporary.open("xb") as output_handle:
        shutil.copyfileobj(input_handle, output_handle, length=1024 * 1024)
    if sha256_file(temporary) != source_hash or temporary.stat().st_size != source_size:
        temporary.unlink(missing_ok=True)
        raise PromotionError(f"temporary promotion copy differs: {destination}")
    try:
        os.link(temporary, destination)
    except FileExistsError as error:
        raise PromotionError(f"destination already exists: {destination}") from error
    finally:
        temporary.unlink(missing_ok=True)
    if sha256_file(destination) != source_hash or destination.stat().st_size != source_size:
        raise PromotionError(f"promoted destination differs: {destination}")
    return {
        "source_path": source.as_posix(),
        "source_sha256": source_hash,
        "destination_path": destination.as_posix(),
        "destination_sha256": source_hash,
        "byte_length": source_size,
    }


def exact_payload_new(source: Path, payload: bytes, destination: Path, representation: str) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise PromotionError(f"destination already exists: {destination}")
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    if temporary.exists():
        raise PromotionError(f"temporary destination already exists: {temporary}")
    temporary.write_bytes(payload)
    source_hash = evidence_raw_sha256(payload)
    if sha256_file(temporary) != source_hash or temporary.stat().st_size != len(payload):
        temporary.unlink(missing_ok=True)
        raise PromotionError(f"temporary promotion materialization differs: {destination}")
    try:
        os.link(temporary, destination)
    except FileExistsError as error:
        raise PromotionError(f"destination already exists: {destination}") from error
    finally:
        temporary.unlink(missing_ok=True)
    return {
        "source_path": source.as_posix(),
        "source_representation": representation,
        "source_sha256": source_hash,
        "destination_path": destination.as_posix(),
        "destination_sha256": source_hash,
        "byte_length": len(payload),
    }


def git_head_identity(repo: Path) -> tuple[str, str]:
    completed = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD", "HEAD^{tree}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    lines = completed.stdout.splitlines()
    if completed.returncode != 0 or len(lines) != 2:
        raise PromotionError("promotion checkout HEAD/tree is unresolved")
    return lines[0], lines[1]


def git_head_file_identity(repo: Path, path: Path) -> dict[str, Any]:
    if not path.is_file() or is_reparse_or_symlink(path):
        raise PromotionError(f"canonical predecessor is not a regular non-reparse file: {path}")
    relative = path.resolve().relative_to(repo).as_posix()
    blob_id = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"HEAD:{relative}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    blob = subprocess.run(
        ["git", "-C", str(repo), "show", f"HEAD:{relative}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    working = path.read_bytes()
    if blob_id.returncode != 0 or blob.returncode != 0 or working != blob.stdout:
        raise PromotionError(f"canonical predecessor differs from HEAD: {relative}")
    return {
        "path": path.as_posix(),
        "repository_relative_path": relative,
        "sha256": hashlib.sha256(working).hexdigest(),
        "byte_length": len(working),
        "git_blob_id": blob_id.stdout.strip(),
    }


def valid_lower_hex(value: object, lengths: set[int]) -> bool:
    text = str(value)
    return len(text) in lengths and all(character in "0123456789abcdef" for character in text)


def absolute_repository_external_descriptor(value: object, repo: Path) -> Path:
    descriptor = Path(str(value))
    if not descriptor.is_absolute():
        raise PromotionError(f"path descriptor is not absolute: {value}")
    lexical = Path(os.path.abspath(descriptor))
    resolved = descriptor.resolve()
    for candidate in (lexical, resolved):
        try:
            candidate.relative_to(repo)
        except ValueError:
            continue
        raise PromotionError(f"path descriptor is not repository-external: {value}")
    return resolved


def validate_baseline_promotion_payload(
    repo: Path,
    destination: Path,
    promotion: dict[str, Any],
    *,
    historical_after_terminal_closeout: bool = False,
) -> None:
    schema = promotion.get("schema_version")
    if (
        schema not in BASELINE_PROMOTION_SCHEMAS
        or promotion.get("mode") != "baseline"
        or promotion.get("byte_identity_verified") is not True
    ):
        raise PromotionError("baseline promotion receipt is invalid")
    if schema == "iris_repository_runtime_lightweighting_baseline_promotion_v1":
        if "transaction" in promotion or "promotion_strategy" in promotion:
            raise PromotionError("baseline v1 receipt must retain create-new semantics")
        return
    repo = repo.resolve()
    destination = destination.resolve()
    transaction = promotion.get("transaction")
    physical_subject = promotion.get("physical_subject")
    if (
        promotion.get("promotion_strategy") != "successor_transaction"
        or not isinstance(transaction, dict)
        or not isinstance(physical_subject, dict)
        or not valid_lower_hex(physical_subject.get("run_identity"), {64})
        or not valid_lower_hex(physical_subject.get("commit"), {40, 64})
        or not valid_lower_hex(physical_subject.get("tree"), {40, 64})
        or not valid_lower_hex(transaction.get("transaction_id"), {32})
        or not valid_lower_hex(transaction.get("predecessor_commit"), {40, 64})
        or not valid_lower_hex(transaction.get("predecessor_tree"), {40, 64})
        or not valid_lower_hex(transaction.get("predecessor_receipt_sha256"), {64})
        or not valid_lower_hex(transaction.get("predecessor_receipt_git_blob_id"), {40, 64})
        or transaction.get("filesystem_group_atomicity_claimed") is not False
        or transaction.get("final_all_new_verified") is not True
        or transaction.get("recovery_policy")
        != "exclusive_lock_hash_addressed_journal_restore_all_predecessor_files_then_rerun"
        or promotion.get("destination_repository_relative_root") != DURABLE_RELATIVE.as_posix()
        or Path(str(physical_subject.get("physical_resolved_root", ""))).resolve() != repo
        or destination != (repo / DURABLE_RELATIVE).resolve()
    ):
        raise PromotionError("baseline successor transaction semantics are invalid")
    predecessor_commit = str(transaction["predecessor_commit"])
    predecessor_tree = str(transaction["predecessor_tree"])
    if (
        physical_subject.get("commit") != predecessor_commit
        or physical_subject.get("tree") != predecessor_tree
    ):
        raise PromotionError("baseline successor physical subject differs from predecessor HEAD")
    resolved_tree = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"{predecessor_commit}^{{tree}}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    ancestor = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", predecessor_commit, "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if resolved_tree.returncode != 0 or resolved_tree.stdout.strip() != predecessor_tree or ancestor.returncode != 0:
        raise PromotionError("baseline successor predecessor commit/tree is not in the current history")
    durable_baseline = load_object(destination / "baseline_inventory.json")
    if any(
        durable_baseline.get(key) != physical_subject.get(key)
        for key in ("physical_resolved_root", "commit", "tree", "run_identity")
    ):
        raise PromotionError("baseline successor physical subject differs from durable baseline")
    predecessor_rows = transaction.get("predecessor_files")
    if not isinstance(predecessor_rows, list) or len(predecessor_rows) != len(BASELINE_DURABLE_NAMES):
        raise PromotionError("baseline successor predecessor file set is invalid")
    predecessor_by_name: dict[str, dict[str, Any]] = {}
    for row in predecessor_rows:
        if not isinstance(row, dict):
            raise PromotionError("baseline successor predecessor row is invalid")
        relative = str(row.get("repository_relative_path", ""))
        name = Path(relative).name
        expected_predecessor_path = (repo / relative).resolve()
        absolute_predecessor_path = Path(str(row.get("path", "")))
        if (
            name in predecessor_by_name
            or relative != (DURABLE_RELATIVE / name).as_posix()
            or not absolute_predecessor_path.is_absolute()
            or absolute_predecessor_path.resolve() != expected_predecessor_path
        ):
            raise PromotionError("baseline successor predecessor path set is noncanonical")
        if (
            name not in BASELINE_DURABLE_NAMES
            or not valid_lower_hex(row.get("sha256"), {64})
            or not valid_lower_hex(row.get("git_blob_id"), {40, 64})
            or int(row.get("byte_length", -1)) < 0
        ):
            raise PromotionError(f"baseline successor predecessor identity is invalid: {name}")
        resolved_blob = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", f"{predecessor_commit}:{relative}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        blob_bytes = subprocess.run(
            ["git", "-C", str(repo), "show", f"{predecessor_commit}:{relative}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if (
            resolved_blob.returncode != 0
            or resolved_blob.stdout.strip() != row["git_blob_id"]
            or blob_bytes.returncode != 0
            or hashlib.sha256(blob_bytes.stdout).hexdigest() != row["sha256"]
            or len(blob_bytes.stdout) != row["byte_length"]
        ):
            raise PromotionError(f"baseline successor predecessor Git object differs: {name}")
        predecessor_by_name[name] = row
    if set(predecessor_by_name) != set(BASELINE_DURABLE_NAMES):
        raise PromotionError("baseline successor predecessor file names are incomplete")
    predecessor_receipt = predecessor_by_name["baseline_promotion_receipt.json"]
    if (
        predecessor_receipt["sha256"] != transaction["predecessor_receipt_sha256"]
        or predecessor_receipt["git_blob_id"] != transaction["predecessor_receipt_git_blob_id"]
    ):
        raise PromotionError("baseline successor predecessor receipt chain differs")
    store = transaction.get("predecessor_durable_store")
    if store != {"kind": "git_commit_blobs", "commit": predecessor_commit, "tree": predecessor_tree}:
        raise PromotionError("baseline successor predecessor durable store is invalid")
    promoted = promotion.get("promoted_files")
    new_generation = transaction.get("new_generation_files")
    if (
        not isinstance(promoted, list)
        or not isinstance(new_generation, list)
        or len(promoted) != 2
        or len(new_generation) != 2
        or any(not isinstance(row, dict) for row in promoted)
        or any(not isinstance(row, dict) for row in new_generation)
    ):
        raise PromotionError("baseline successor new generation bindings are invalid")
    promoted_by_name = {Path(str(row.get("destination_path", ""))).name: row for row in promoted}
    generation_by_name = {str(row.get("name", "")): row for row in new_generation}
    expected_new_names = set(BASELINE_DURABLE_NAMES[:2])
    if set(promoted_by_name) != expected_new_names or set(generation_by_name) != expected_new_names:
        raise PromotionError("baseline successor new generation path set is noncanonical")
    for name in expected_new_names:
        promoted_row = promoted_by_name[name]
        generation_row = generation_by_name[name]
        physical_destination = (repo / DURABLE_RELATIVE / name).resolve()
        promoted_source = absolute_repository_external_descriptor(
            promoted_row.get("source_path"),
            repo,
        )
        generation_source = absolute_repository_external_descriptor(
            generation_row.get("source_path"),
            repo,
        )
        if (
            generation_row.get("repository_relative_destination") != (DURABLE_RELATIVE / name).as_posix()
            or promoted_row.get("repository_relative_destination")
            != (DURABLE_RELATIVE / name).as_posix()
            or Path(str(promoted_row.get("destination_path", ""))).resolve()
            != physical_destination
            or promoted_source != generation_source
            or promoted_row.get("source_sha256") != generation_row.get("sha256")
            or promoted_row.get("destination_sha256") != generation_row.get("sha256")
            or int(promoted_row.get("byte_length", -1)) != generation_row.get("byte_length")
            or not valid_lower_hex(generation_row.get("sha256"), {64})
        ):
            raise PromotionError(f"baseline successor new generation binding differs: {name}")
        if promoted_source.exists():
            if (
                not promoted_source.is_file()
                or is_reparse_or_symlink(promoted_source)
                or sha256_file(promoted_source) != generation_row["sha256"]
                or promoted_source.stat().st_size != generation_row["byte_length"]
            ):
                raise PromotionError(f"baseline successor external source differs: {name}")
        elif not historical_after_terminal_closeout:
            raise PromotionError(
                f"baseline successor external source must remain through terminal closeout: {name}"
            )
    expected_transaction_seed = {
        "predecessor_commit": predecessor_commit,
        "predecessor_tree": predecessor_tree,
        "predecessor_receipt_sha256": transaction["predecessor_receipt_sha256"],
        "physical_run_identity": physical_subject["run_identity"],
        "sources": {
            name: {
                "sha256": generation_by_name[name]["sha256"],
                "byte_length": generation_by_name[name]["byte_length"],
            }
            for name in BASELINE_DURABLE_NAMES[:2]
        },
    }
    if (
        hashlib.sha256(canonical_json_bytes(expected_transaction_seed)).hexdigest()[:32]
        != transaction["transaction_id"]
    ):
        raise PromotionError("baseline successor transaction ID is not reproducible")
    generated_receipt = transaction.get("generated_receipt_output")
    staging = transaction.get("staging_verification")
    source_disposition = transaction.get("external_source_disposition")
    if (
        not isinstance(generated_receipt, dict)
        or generated_receipt.get("source_identity") != "generated:baseline-successor-receipt-v2"
        or generated_receipt.get("repository_relative_destination")
        != (DURABLE_RELATIVE / "baseline_promotion_receipt.json").as_posix()
        or generated_receipt.get("identity_rule")
        != "durable_and_external_bytes_must_be_identical_after_all_three_replacements"
        or generated_receipt.get("operator_receipt_disposition")
        != "retained_through_reviewed_promotion_commit_then_may_be_purged"
        or not isinstance(staging, dict)
        or staging.get("same_volume_stage_backup_and_destination") is not True
        or staging.get("all_staged_hashes_verified_before_replace") is not True
        or staging.get("ephemeral_paths_retained_in_durable_receipt") is not False
        or staging.get("ephemeral_paths_retained_in_recovery_journal_only") is not True
        or source_disposition
        != {
            "policy": "retained_through_terminal_closeout_then_may_be_purged",
            "existence_required_through_terminal_closeout": True,
            "historical_after_terminal_closeout_may_accept_absent": True,
        }
    ):
        raise PromotionError("baseline successor staging/final verification semantics are invalid")
    absolute_repository_external_descriptor(
        generated_receipt.get("external_destination_path"),
        repo,
    )


def resolve_repo(path: Path) -> Path:
    completed = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise PromotionError(completed.stderr.strip())
    return Path(completed.stdout.strip()).resolve()


def is_reparse_or_symlink(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        return bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400)
    except OSError:
        return False


def validate_roots(repo_arg: Path, destination_root: Path, receipt_out: Path) -> tuple[Path, Path, Path]:
    repo = resolve_repo(repo_arg.resolve())
    destination_lexical = Path(os.path.abspath(destination_root))
    expected_lexical = repo / DURABLE_RELATIVE
    if os.path.normcase(str(destination_lexical)) != os.path.normcase(str(expected_lexical)):
        raise PromotionError(f"destination root must be exact durable root: {expected_lexical}")
    current = destination_lexical
    while current != repo:
        if current.exists() and is_reparse_or_symlink(current):
            raise PromotionError(f"durable destination traverses a reparse/symlink path: {current}")
        if current.parent == current:
            raise PromotionError("durable destination is not beneath repository")
        current = current.parent
    destination = destination_lexical.resolve()
    expected = (repo / DURABLE_RELATIVE).resolve()
    if os.path.normcase(str(destination)) != os.path.normcase(str(expected)):
        raise PromotionError(f"destination root must be exact durable root: {expected}")
    external_receipt = receipt_out.resolve()
    try:
        external_receipt.relative_to(repo)
    except ValueError:
        pass
    else:
        raise PromotionError("operator receipt copy must be repository-external")
    return repo, destination, external_receipt


def require_external_input(repo: Path, path: Path, role: str) -> Path:
    lexical = Path(os.path.abspath(path))
    resolved = path.resolve()
    for candidate in (lexical, resolved):
        try:
            candidate.relative_to(repo)
        except ValueError:
            continue
        raise PromotionError(f"{role} must be repository-external: {candidate}")
    return resolved


def validate_subject_receipt(
    receipt_path: Path,
    source_manifest: Path,
    source_summary: Path,
    repo: Path,
) -> dict[str, Any]:
    receipt = load_object(receipt_path)
    for path, role in (
        (receipt_path, "subject receipt"),
        (source_manifest, "source manifest"),
        (source_summary, "source summary"),
    ):
        require_external_input(repo, path, role)
    if receipt.get("schema_version") != "iris_repository_runtime_lightweighting_subject_receipt_v1":
        raise PromotionError("subject receipt schema mismatch")
    if receipt.get("subject_kind") != "physical_capacity_subject":
        raise PromotionError("baseline requires physical_capacity_subject")
    if os.path.normcase(str(Path(str(receipt.get("physical_resolved_root"))).resolve())) != os.path.normcase(str(repo)):
        raise PromotionError("subject receipt repository mismatch")
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD", "HEAD^{tree}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if head.returncode != 0 or head.stdout.splitlines() != [receipt.get("commit"), receipt.get("tree")]:
        raise PromotionError("subject receipt commit/tree differs from promotion checkout")
    if source_manifest.is_file():
        manifest_identity_bytes = source_manifest.read_bytes()
    else:
        manifest_identity_bytes, _, _ = load_lifecycle_source(source_manifest, "baseline")
    bindings = (("manifest", source_manifest), ("summary", source_summary))
    for key, source in bindings:
        binding = receipt.get(key, {})
        if os.path.normcase(str(Path(str(binding.get("path"))).resolve())) != os.path.normcase(str(source.resolve())):
            raise PromotionError(f"{key} source path differs from subject receipt")
        payload_hash = evidence_raw_sha256(manifest_identity_bytes) if key == "manifest" else sha256_file(source)
        payload_bytes = len(manifest_identity_bytes) if key == "manifest" else source.stat().st_size
        if payload_hash != binding.get("sha256"):
            raise PromotionError(f"{key} source hash differs from subject receipt")
        if payload_bytes != binding.get("bytes"):
            raise PromotionError(f"{key} source length differs from subject receipt")
    _, _, manifest_representation = load_lifecycle_source(source_manifest, "baseline")
    if manifest_representation not in {"v1", "v2"}:
        raise PromotionError("unknown lifecycle manifest representation")
    return receipt


def finish_receipt(
    destination: Path,
    external_receipt: Path,
    name: str,
    payload: dict[str, Any],
) -> None:
    durable_path = destination / name
    encoded = canonical_json_bytes(payload)
    atomic_write_new(durable_path, encoded)
    atomic_write_new(external_receipt, encoded)
    if sha256_file(durable_path) != sha256_file(external_receipt):
        raise PromotionError("durable and operator receipt copies differ")


def require_absent(paths: list[Path]) -> None:
    existing = [path for path in paths if path.exists()]
    if existing:
        raise PromotionError(f"promotion destination already exists: {existing[0]}")


def validate_baseline_generation(args: argparse.Namespace, repo: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    subject = validate_subject_receipt(
        args.subject_receipt.resolve(),
        args.source_manifest.resolve(),
        args.source_summary.resolve(),
        repo,
    )
    summary = load_object(args.source_summary)
    if summary.get("subject_kind") != "physical_capacity_subject" or summary.get("run_identity") != subject.get("run_identity"):
        raise PromotionError("summary physical subject identity mismatch")
    if summary.get("unclassified_count") != 0 or summary.get("unreadable_count") != 0 or summary.get("consumer_scan_hold_count", 0) != 0 or summary.get("complete_accounting") is not True:
        raise PromotionError("summary accounting is incomplete")
    manifest_bytes, manifest_rows, _ = load_lifecycle_source(args.source_manifest.resolve(), "baseline")
    actual_identity = lifecycle_repository_identity(repo)
    actual_rows, _ = lifecycle_build_rows(repo, include_missing_giants=True)
    actual_summary = lifecycle_summary_for(
        repo,
        "physical_capacity_subject",
        actual_identity,
        actual_rows,
    )
    if manifest_bytes != lifecycle_jsonl_bytes(actual_rows):
        raise PromotionError("baseline manifest differs from a fresh physical checkout census")
    if summary != actual_summary:
        raise PromotionError("baseline summary differs from a fresh physical checkout census")
    giants = {
        str(row.get("path")): row
        for row in manifest_rows
        if str(row.get("path")) in GIANT_RELATIVES
    }
    if summary.get("ignored_giant_count") != 4 or set(giants) != GIANT_RELATIVES:
        raise PromotionError("baseline lacks the exact four physical ignored giant rows")
    for relative, row in giants.items():
        source = repo / relative
        if (
            row.get("path_access") != "readable"
            or row.get("vcs_state") != "ignored"
            or not source.is_file()
            or row.get("sha256") != sha256_file(source)
            or row.get("size_bytes") != source.stat().st_size
        ):
            raise PromotionError(f"baseline giant physical identity mismatch: {relative}")
    return subject, summary


def promote_baseline(args: argparse.Namespace) -> None:
    repo, destination, external = validate_roots(args.repo, args.destination_root, args.receipt_out)
    subject, _ = validate_baseline_generation(args, repo)
    require_absent(
        [
            destination / "artifact_role_manifest.jsonl",
            destination / "baseline_inventory.json",
            destination / "baseline_promotion_receipt.json",
            external,
        ]
    )
    manifest_bytes, _, representation = load_lifecycle_source(args.source_manifest.resolve(), "baseline")
    rows = [
        exact_payload_new(
            args.source_manifest.resolve(),
            manifest_bytes,
            destination / "artifact_role_manifest.jsonl",
            representation,
        ),
        exact_copy_new(args.source_summary.resolve(), destination / "baseline_inventory.json"),
    ]
    payload = {
        "schema_version": "iris_repository_runtime_lightweighting_baseline_promotion_v1",
        "mode": "baseline",
        "physical_subject": {
            "physical_resolved_root": subject["physical_resolved_root"],
            "commit": subject["commit"],
            "tree": subject["tree"],
            "run_identity": subject["run_identity"],
        },
        "promoted_files": rows,
        "destination_repository_relative_root": DURABLE_RELATIVE.as_posix(),
        "byte_identity_verified": True,
        "promotion_commit_binding": "pending_reviewed_commit",
    }
    finish_receipt(destination, external, "baseline_promotion_receipt.json", payload)


def transaction_path(destination: Path, transaction_id: str, role: str, name: str = "") -> Path:
    suffix = f".{name}" if name else ""
    return destination / f".baseline-successor-{transaction_id}.{role}{suffix}"


def write_json_replace(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(f"{path.name}.{os.getpid()}.replace")
    if os.path.lexists(temporary):
        raise PromotionError(f"journal replace temporary already exists: {temporary}")
    with temporary.open("xb") as handle:
        handle.write(canonical_json_bytes(payload))
    os.replace(temporary, path)


def acquire_transaction_lock(path: Path, *, create: bool) -> BinaryIO:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = path.open("x+b" if create else "r+b")
    except FileExistsError as error:
        raise PromotionError("another baseline successor transaction owns the exclusive lock") from error
    try:
        if path.stat().st_size == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as error:
        handle.close()
        raise PromotionError("another baseline successor transaction is currently active") from error
    return handle


def release_transaction_lock(handle: BinaryIO) -> None:
    try:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        handle.close()


def baseline_successor_test_injection(name: str) -> str:
    if os.environ.get("IRIS_BASELINE_SUCCESSOR_TEST_AUTHORITY") != BASELINE_SUCCESSOR_TEST_AUTHORITY:
        return ""
    return os.environ.get(name, "")


def copy_verified(source: Path, destination: Path, expected_sha256: str, expected_size: int) -> None:
    if destination.exists():
        raise PromotionError(f"transaction artifact already exists: {destination}")
    with source.open("rb") as input_handle, destination.open("xb") as output_handle:
        shutil.copyfileobj(input_handle, output_handle, length=1024 * 1024)
    if sha256_file(destination) != expected_sha256 or destination.stat().st_size != expected_size:
        raise PromotionError(f"transaction copy differs: {destination}")


def cleanup_transaction_artifacts(journal: dict[str, Any], *, remove_external: bool) -> None:
    for row in journal.get("files", []):
        for key in ("stage_path", "backup_path"):
            Path(str(row[key])).unlink(missing_ok=True)
        stage_path = Path(str(row["stage_path"]))
        for temporary in stage_path.parent.glob(f"{stage_path.name}.*.tmp"):
            temporary.unlink(missing_ok=True)
    external_stage = Path(str(journal["external_stage_path"]))
    for temporary in external_stage.parent.glob(f"{external_stage.name}.*.tmp"):
        temporary.unlink(missing_ok=True)
    journal_path = Path(str(journal["journal_path"]))
    for temporary in journal_path.parent.glob(f"{journal_path.name}.*.tmp"):
        temporary.unlink(missing_ok=True)
    for temporary in journal_path.parent.glob(f"{journal_path.name}.*.replace"):
        temporary.unlink(missing_ok=True)
    if remove_external:
        external = Path(str(journal["external_receipt_path"]))
        linked_stage = (
            external.exists()
            and external_stage.exists()
            and os.path.samefile(external, external_stage)
        )
        if external.exists() and (journal.get("external_published") is True or linked_stage):
            expected = journal.get("receipt_sha256")
            if isinstance(expected, str) and sha256_file(external) == expected:
                external.unlink()
            else:
                raise PromotionError("operator receipt cannot be safely removed during recovery")
    external_stage.unlink(missing_ok=True)
    journal_path.unlink(missing_ok=True)


def restore_predecessor_generation(journal: dict[str, Any]) -> None:
    errors: list[str] = []
    for row in journal.get("files", []):
        destination = Path(str(row["destination_path"]))
        backup = Path(str(row["backup_path"]))
        expected_hash = str(row["predecessor_sha256"])
        expected_size = int(row["predecessor_byte_length"])
        try:
            backup_valid = (
                backup.is_file()
                and not is_reparse_or_symlink(backup)
                and sha256_file(backup) == expected_hash
                and backup.stat().st_size == expected_size
            )
            destination_valid = (
                destination.is_file()
                and not is_reparse_or_symlink(destination)
                and sha256_file(destination) == expected_hash
                and destination.stat().st_size == expected_size
            )
            if backup_valid:
                restore_stage = destination.with_name(
                    f".baseline-successor-{journal['transaction_id']}.restore.{destination.name}"
                )
                restore_stage.unlink(missing_ok=True)
                copy_verified(backup, restore_stage, expected_hash, expected_size)
                os.replace(restore_stage, destination)
            elif not destination_valid:
                raise PromotionError(f"predecessor cannot be recovered: {destination}")
            if sha256_file(destination) != expected_hash or destination.stat().st_size != expected_size:
                raise PromotionError(f"recovered predecessor differs: {destination}")
        except (OSError, PromotionError) as error:
            errors.append(str(error))
    if errors:
        journal["state"] = "recovery_failed"
        journal["recovery_errors"] = errors
        write_json_replace(Path(str(journal["journal_path"])), journal)
        raise PromotionError("baseline successor recovery failed; journal and backups retained: " + "; ".join(errors))


def validate_recovery_journal(repo: Path, destination: Path, journal_path: Path, journal: dict[str, Any]) -> None:
    transaction_id = str(journal.get("transaction_id", ""))
    if len(transaction_id) != 32 or any(character not in "0123456789abcdef" for character in transaction_id):
        raise PromotionError("baseline successor journal transaction ID is invalid")
    expected_lock = destination / BASELINE_SUCCESSOR_LOCK_NAME
    if (
        journal.get("schema_version") != "iris_repository_runtime_lightweighting_baseline_successor_journal_v1"
        or Path(str(journal.get("repository_root", ""))).resolve() != repo
        or Path(str(journal.get("journal_path", ""))).resolve() != journal_path.resolve()
        or journal_path.resolve() != transaction_path(destination, transaction_id, "journal", "json").resolve()
        or Path(str(journal.get("lock_path", ""))).resolve() != expected_lock.resolve()
    ):
        raise PromotionError("baseline successor journal identity is invalid")
    rows = journal.get("files", [])
    if not isinstance(rows, list) or [row.get("name") for row in rows] != list(BASELINE_DURABLE_NAMES):
        raise PromotionError("baseline successor journal file set is invalid")
    for row in rows:
        name = str(row["name"])
        if (
            Path(str(row.get("destination_path", ""))).resolve() != (destination / name).resolve()
            or Path(str(row.get("stage_path", ""))).resolve()
            != transaction_path(destination, transaction_id, "stage", name).resolve()
            or Path(str(row.get("backup_path", ""))).resolve()
            != transaction_path(destination, transaction_id, "backup", name).resolve()
            or not isinstance(row.get("predecessor_sha256"), str)
            or len(str(row["predecessor_sha256"])) != 64
            or any(character not in "0123456789abcdef" for character in str(row["predecessor_sha256"]))
            or int(row.get("predecessor_byte_length", -1)) < 0
        ):
            raise PromotionError(f"baseline successor journal row is invalid: {name}")
    external = Path(str(journal.get("external_receipt_path", ""))).resolve()
    external_stage = Path(str(journal.get("external_stage_path", ""))).resolve()
    try:
        external.relative_to(repo)
    except ValueError:
        pass
    else:
        raise PromotionError("baseline successor recovery receipt is not repository-external")
    expected_external_stage = external.with_name(f".{external.name}.{transaction_id}.stage")
    if external_stage != expected_external_stage:
        raise PromotionError("baseline successor recovery receipt stage is invalid")
    command_intent = journal.get("command_intent")
    lock_owner = journal.get("lock_owner")
    if (
        not isinstance(command_intent, dict)
        or journal.get("command_intent_sha256")
        != hashlib.sha256(canonical_json_bytes(command_intent)).hexdigest()
        or not isinstance(lock_owner, dict)
        or not isinstance(lock_owner.get("pid"), int)
        or lock_owner.get("pid", 0) <= 0
        or lock_owner.get("process_identity")
        != f"pid-{lock_owner.get('pid')}-transaction-{transaction_id}"
    ):
        raise PromotionError("baseline successor recovery command intent is invalid")


def baseline_successor_input_identity(path: Path, role: str) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.is_file() or is_reparse_or_symlink(resolved):
        raise PromotionError(f"baseline successor {role} is not a regular non-reparse file: {resolved}")
    return {
        "path": resolved.as_posix(),
        "sha256": sha256_file(resolved),
        "byte_length": resolved.stat().st_size,
    }


def baseline_successor_command_intent(
    args: argparse.Namespace,
    repo: Path,
    destination: Path,
    external: Path,
) -> dict[str, Any]:
    predecessor = args.predecessor_promotion_receipt.resolve()
    expected_predecessor = (destination / "baseline_promotion_receipt.json").resolve()
    if predecessor != expected_predecessor:
        raise PromotionError("baseline successor command intent predecessor path is noncanonical")
    return {
        "schema_version": "iris_repository_runtime_lightweighting_baseline_successor_command_intent_v1",
        "mode": "baseline-successor",
        "repository_root": repo.as_posix(),
        "destination_root": destination.as_posix(),
        "receipt_out": external.as_posix(),
        "predecessor_promotion_receipt_path": predecessor.as_posix(),
        "inputs": {
            "source_manifest": baseline_successor_input_identity(args.source_manifest, "source manifest"),
            "source_summary": baseline_successor_input_identity(args.source_summary, "source summary"),
            "subject_receipt": baseline_successor_input_identity(args.subject_receipt, "subject receipt"),
        },
    }


def recover_interrupted_baseline_successor(
    args: argparse.Namespace,
    repo: Path,
    destination: Path,
    external: Path,
) -> bool:
    journals = sorted(destination.glob(".baseline-successor-*.journal.json"))
    lock = destination / BASELINE_SUCCESSOR_LOCK_NAME
    transaction_artifacts = sorted(destination.glob(".baseline-successor-*"))
    if len(journals) > 1:
        raise PromotionError("multiple baseline successor transactions are ambiguous")
    if not journals:
        if transaction_artifacts:
            journal_temporaries_only = all(
                re.fullmatch(
                    r"\.baseline-successor-[0-9a-f]{32}\.journal\.json\.\d+\.tmp",
                    path.name,
                )
                is not None
                for path in transaction_artifacts
            )
            if not journal_temporaries_only or not lock.is_file() or is_reparse_or_symlink(lock):
                raise PromotionError("baseline successor artifacts exist without a recoverable journal")
            stale_lock = acquire_transaction_lock(lock, create=False)
            try:
                for temporary in transaction_artifacts:
                    temporary.unlink()
            finally:
                release_transaction_lock(stale_lock)
            lock.unlink(missing_ok=True)
            return False
        if not os.path.lexists(lock):
            return False
        if not lock.is_file() or is_reparse_or_symlink(lock):
            raise PromotionError("baseline successor lock-only residue is noncanonical")
        stale_lock = acquire_transaction_lock(lock, create=False)
        release_transaction_lock(stale_lock)
        lock.unlink()
        return False
    if not lock.is_file() or is_reparse_or_symlink(lock):
        raise PromotionError("baseline successor journal exists without its exclusive lock")
    journal_path = journals[0]
    recovery_lock = acquire_transaction_lock(lock, create=False)
    remove_lock = False
    try:
        try:
            journal = load_object(journal_path)
        except (OSError, json.JSONDecodeError, PromotionError) as error:
            raise PromotionError(f"baseline successor journal is unreadable: {journal_path}") from error
        validate_recovery_journal(repo, destination, journal_path, journal)
        current_intent = baseline_successor_command_intent(args, repo, destination, external)
        if (
            journal.get("command_intent") != current_intent
            or journal.get("command_intent_sha256")
            != hashlib.sha256(canonical_json_bytes(current_intent)).hexdigest()
        ):
            raise PromotionError("baseline successor recovery command intent differs from the current invocation")
        if journal.get("state") not in {"preparing", "prepared", "applying", "recovery_failed", "committed"}:
            raise PromotionError("baseline successor journal state is invalid")
        transaction_id = str(journal["transaction_id"])
        allowed_artifacts = {journal_path.resolve()}
        for temporary in journal_path.parent.glob(f"{journal_path.name}.*.replace"):
            allowed_artifacts.add(temporary.resolve())
        for temporary in journal_path.parent.glob(f"{journal_path.name}.*.tmp"):
            allowed_artifacts.add(temporary.resolve())
        for row in journal["files"]:
            stage_path = Path(str(row["stage_path"]))
            allowed_artifacts.add(stage_path.resolve())
            allowed_artifacts.add(Path(str(row["backup_path"])).resolve())
            for temporary in stage_path.parent.glob(f"{stage_path.name}.*.tmp"):
                allowed_artifacts.add(temporary.resolve())
            allowed_artifacts.add(
                (destination / f".baseline-successor-{transaction_id}.restore.{row['name']}").resolve()
            )
        unexpected = [path for path in transaction_artifacts if path.resolve() not in allowed_artifacts]
        if unexpected:
            raise PromotionError(f"baseline successor recovery artifacts are ambiguous: {unexpected[0]}")
        if journal.get("state") == "committed":
            for row in journal["files"]:
                final = Path(str(row["destination_path"]))
                if (
                    not final.is_file()
                    or is_reparse_or_symlink(final)
                    or sha256_file(final) != row.get("new_sha256")
                    or final.stat().st_size != row.get("new_byte_length")
                ):
                    raise PromotionError("committed baseline successor transaction is incomplete")
            external = Path(str(journal["external_receipt_path"]))
            if (
                not external.is_file()
                or sha256_file(external) != journal.get("receipt_sha256")
                or external.read_bytes() != (destination / "baseline_promotion_receipt.json").read_bytes()
            ):
                raise PromotionError("committed baseline successor operator receipt is incomplete")
            validate_baseline_promotion_payload(
                repo,
                destination,
                load_object(destination / "baseline_promotion_receipt.json"),
            )
            cleanup_transaction_artifacts(journal, remove_external=False)
            remove_lock = True
            return True
        restore_predecessor_generation(journal)
        cleanup_transaction_artifacts(journal, remove_external=True)
        remove_lock = True
        raise PromotionError(
            f"recovered interrupted baseline successor transaction {transaction_id}; rerun with a fresh command"
        )
    finally:
        release_transaction_lock(recovery_lock)
        if remove_lock:
            lock.unlink(missing_ok=True)


def validate_predecessor_generation(
    repo: Path,
    destination: Path,
    predecessor_receipt_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], str, str]:
    expected_receipt = (destination / "baseline_promotion_receipt.json").resolve()
    if predecessor_receipt_path.resolve() != expected_receipt:
        raise PromotionError("predecessor promotion receipt must be the canonical durable receipt")
    predecessor = load_object(expected_receipt)
    validate_baseline_promotion_payload(repo, destination, predecessor)
    identities = [git_head_file_identity(repo, destination / name) for name in BASELINE_DURABLE_NAMES]
    promoted = predecessor.get("promoted_files", [])
    if not isinstance(promoted, list):
        raise PromotionError("predecessor promoted-file bindings are invalid")
    by_name: dict[str, dict[str, Any]] = {}
    for row in promoted:
        name = Path(str(row.get("destination_path", ""))).name
        if name in by_name:
            raise PromotionError(f"duplicate predecessor promoted-file binding: {name}")
        by_name[name] = row
    if set(by_name) != set(BASELINE_DURABLE_NAMES[:2]):
        raise PromotionError("predecessor promoted-file bindings are incomplete or noncanonical")
    for identity in identities[:2]:
        name = Path(str(identity["path"])).name
        binding = by_name.get(name)
        if (
            binding is None
            or Path(str(binding.get("destination_path", ""))).resolve() != (destination / name).resolve()
            or binding.get("destination_sha256") != identity["sha256"]
            or int(binding.get("byte_length", -1)) != identity["byte_length"]
        ):
            raise PromotionError(f"predecessor promoted-file binding differs from HEAD: {name}")
    head_commit, head_tree = git_head_identity(repo)
    return predecessor, identities, head_commit, head_tree


def promote_baseline_successor(args: argparse.Namespace) -> str | None:
    repo, destination, external = validate_roots(args.repo, args.destination_root, args.receipt_out)
    if recover_interrupted_baseline_successor(args, repo, destination, external):
        return "recovered_committed_transaction"
    if external.exists():
        raise PromotionError(f"operator receipt already exists: {external}")
    predecessor, predecessor_files, predecessor_commit, predecessor_tree = validate_predecessor_generation(
        repo,
        destination,
        args.predecessor_promotion_receipt.resolve(),
    )
    subject, _ = validate_baseline_generation(args, repo)
    source_paths = {
        "artifact_role_manifest.jsonl": args.source_manifest.resolve(),
        "baseline_inventory.json": args.source_summary.resolve(),
    }
    source_identities = {
        name: {"sha256": sha256_file(path), "byte_length": path.stat().st_size}
        for name, path in source_paths.items()
    }
    command_intent = baseline_successor_command_intent(args, repo, destination, external)
    transaction_seed = {
        "predecessor_commit": predecessor_commit,
        "predecessor_tree": predecessor_tree,
        "predecessor_receipt_sha256": sha256_file(destination / "baseline_promotion_receipt.json"),
        "physical_run_identity": subject["run_identity"],
        "sources": source_identities,
    }
    transaction_id = hashlib.sha256(canonical_json_bytes(transaction_seed)).hexdigest()[:32]
    lock_path = destination / BASELINE_SUCCESSOR_LOCK_NAME
    journal_path = transaction_path(destination, transaction_id, "journal", "json")
    external_stage = external.with_name(f".{external.name}.{transaction_id}.stage")
    if os.path.lexists(external_stage):
        raise PromotionError(f"operator receipt stage already exists: {external_stage}")
    if os.path.lexists(lock_path) or list(destination.glob(".baseline-successor-*")):
        raise PromotionError("another baseline successor transaction is active")

    predecessor_by_name = {Path(str(row["path"])).name: row for row in predecessor_files}
    file_rows: list[dict[str, Any]] = []
    for name in BASELINE_DURABLE_NAMES:
        predecessor_identity = predecessor_by_name[name]
        file_rows.append(
            {
                "name": name,
                "destination_path": (destination / name).as_posix(),
                "stage_path": transaction_path(destination, transaction_id, "stage", name).as_posix(),
                "backup_path": transaction_path(destination, transaction_id, "backup", name).as_posix(),
                "predecessor_sha256": predecessor_identity["sha256"],
                "predecessor_byte_length": predecessor_identity["byte_length"],
                "predecessor_git_blob_id": predecessor_identity["git_blob_id"],
            }
        )
    journal: dict[str, Any] = {
        "schema_version": "iris_repository_runtime_lightweighting_baseline_successor_journal_v1",
        "transaction_id": transaction_id,
        "state": "preparing",
        "repository_root": repo.as_posix(),
        "journal_path": journal_path.as_posix(),
        "lock_path": lock_path.as_posix(),
        "external_stage_path": external_stage.as_posix(),
        "external_receipt_path": external.as_posix(),
        "external_published": False,
        "lock_owner": {
            "pid": os.getpid(),
            "process_identity": f"pid-{os.getpid()}-transaction-{transaction_id}",
        },
        "command_intent": command_intent,
        "command_intent_sha256": hashlib.sha256(canonical_json_bytes(command_intent)).hexdigest(),
        "files": file_rows,
    }
    transaction_lock = acquire_transaction_lock(lock_path, create=True)
    committed = False
    try:
        if baseline_successor_test_injection("IRIS_BASELINE_SUCCESSOR_CRASH_AFTER_LOCK") == "1":
            os._exit(87)
        atomic_write_new(journal_path, canonical_json_bytes(journal))
        pause_path_value = baseline_successor_test_injection(
            "IRIS_BASELINE_SUCCESSOR_PAUSE_AFTER_JOURNAL"
        )
        if pause_path_value:
            pause_path = Path(pause_path_value).resolve()
            try:
                pause_path.relative_to(repo)
            except ValueError:
                pass
            else:
                raise PromotionError("baseline successor test pause path must be repository-external")
            release_path = pause_path.with_name(f"{pause_path.name}.release")
            atomic_write_new(pause_path, b"ready\n")
            deadline = time.monotonic() + 15.0
            while not release_path.is_file():
                if time.monotonic() >= deadline:
                    raise PromotionError("baseline successor test pause timed out")
                time.sleep(0.01)
            pause_path.unlink(missing_ok=True)
            release_path.unlink(missing_ok=True)
        crash_after_backup = int(
            baseline_successor_test_injection("IRIS_BASELINE_SUCCESSOR_CRASH_AFTER_BACKUP") or "0"
        )
        for backup_index, row in enumerate(file_rows, start=1):
            name = str(row["name"])
            destination_path = Path(str(row["destination_path"]))
            copy_verified(
                destination_path,
                Path(str(row["backup_path"])),
                str(row["predecessor_sha256"]),
                int(row["predecessor_byte_length"]),
            )
            if crash_after_backup == backup_index:
                os._exit(85)
            if name in source_paths:
                source = source_paths[name]
                source_hash = source_identities[name]["sha256"]
                source_size = source_identities[name]["byte_length"]
                row.update(
                    {
                        "source_path": source.as_posix(),
                        "source_sha256": source_hash,
                        "new_sha256": source_hash,
                        "new_byte_length": source_size,
                    }
                )
                copy_verified(source, Path(str(row["stage_path"])), source_hash, source_size)

        promoted_files = [
            {
                "source_path": source_paths[name].as_posix(),
                "source_sha256": source_identities[name]["sha256"],
                "destination_path": (destination / name).as_posix(),
                "repository_relative_destination": (DURABLE_RELATIVE / name).as_posix(),
                "destination_sha256": source_identities[name]["sha256"],
                "byte_length": source_identities[name]["byte_length"],
            }
            for name in ("artifact_role_manifest.jsonl", "baseline_inventory.json")
        ]
        receipt_payload = {
            "schema_version": "iris_repository_runtime_lightweighting_baseline_promotion_v2",
            "mode": "baseline",
            "promotion_strategy": "successor_transaction",
            "physical_subject": {
                "physical_resolved_root": subject["physical_resolved_root"],
                "commit": subject["commit"],
                "tree": subject["tree"],
                "run_identity": subject["run_identity"],
            },
            "promoted_files": promoted_files,
            "destination_repository_relative_root": DURABLE_RELATIVE.as_posix(),
            "byte_identity_verified": True,
            "promotion_commit_binding": "pending_reviewed_commit",
            "transaction": {
                "transaction_id": transaction_id,
                "predecessor_commit": predecessor_commit,
                "predecessor_tree": predecessor_tree,
                "predecessor_receipt_sha256": sha256_file(destination / "baseline_promotion_receipt.json"),
                "predecessor_receipt_git_blob_id": predecessor_by_name["baseline_promotion_receipt.json"]["git_blob_id"],
                "predecessor_files": predecessor_files,
                "new_generation_files": [
                    {
                        "name": row["name"],
                        "source_path": row.get("source_path"),
                        "repository_relative_destination": (
                            DURABLE_RELATIVE / str(row["name"])
                        ).as_posix(),
                        "sha256": row.get("new_sha256"),
                        "byte_length": row.get("new_byte_length"),
                    }
                    for row in file_rows[:2]
                ],
                "generated_receipt_output": {
                    "source_identity": "generated:baseline-successor-receipt-v2",
                    "repository_relative_destination": (
                        DURABLE_RELATIVE / "baseline_promotion_receipt.json"
                    ).as_posix(),
                    "external_destination_path": external.as_posix(),
                    "identity_rule": "durable_and_external_bytes_must_be_identical_after_all_three_replacements",
                    "operator_receipt_disposition": "retained_through_reviewed_promotion_commit_then_may_be_purged",
                },
                "external_source_disposition": {
                    "policy": "retained_through_terminal_closeout_then_may_be_purged",
                    "existence_required_through_terminal_closeout": True,
                    "historical_after_terminal_closeout_may_accept_absent": True,
                },
                "staging_verification": {
                    "same_volume_stage_backup_and_destination": True,
                    "all_staged_hashes_verified_before_replace": True,
                    "ephemeral_paths_retained_in_durable_receipt": False,
                    "ephemeral_paths_retained_in_recovery_journal_only": True,
                },
                "predecessor_durable_store": {
                    "kind": "git_commit_blobs",
                    "commit": predecessor_commit,
                    "tree": predecessor_tree,
                },
                "recovery_policy": "exclusive_lock_hash_addressed_journal_restore_all_predecessor_files_then_rerun",
                "filesystem_group_atomicity_claimed": False,
                "final_all_new_verified": True,
            },
        }
        receipt_bytes = canonical_json_bytes(receipt_payload)
        receipt_hash = hashlib.sha256(receipt_bytes).hexdigest()
        receipt_size = len(receipt_bytes)
        receipt_row = file_rows[2]
        receipt_row.update(
            {
                "source_path": "generated:baseline-successor-receipt-v2",
                "source_sha256": receipt_hash,
                "new_sha256": receipt_hash,
                "new_byte_length": receipt_size,
            }
        )
        atomic_write_new(Path(str(receipt_row["stage_path"])), receipt_bytes)
        atomic_write_new(external_stage, receipt_bytes)
        if sha256_file(Path(str(receipt_row["stage_path"]))) != receipt_hash or sha256_file(external_stage) != receipt_hash:
            raise PromotionError("staged successor receipt copies differ")
        journal["state"] = "prepared"
        journal["receipt_sha256"] = receipt_hash
        journal["files"] = file_rows
        write_json_replace(journal_path, journal)

        failure_after = int(
            baseline_successor_test_injection("IRIS_BASELINE_SUCCESSOR_FAIL_AFTER_REPLACE") or "0"
        )
        crash_after = int(
            baseline_successor_test_injection("IRIS_BASELINE_SUCCESSOR_CRASH_AFTER_REPLACE") or "0"
        )
        journal["state"] = "applying"
        write_json_replace(journal_path, journal)
        for index, row in enumerate(file_rows, start=1):
            os.replace(Path(str(row["stage_path"])), Path(str(row["destination_path"])))
            journal["replaced_count"] = index
            write_json_replace(journal_path, journal)
            if crash_after == index:
                os._exit(86)
            if failure_after == index:
                raise PromotionError(f"injected baseline successor failure after replace {index}")

        for row in file_rows:
            destination_path = Path(str(row["destination_path"]))
            if sha256_file(destination_path) != row["new_sha256"] or destination_path.stat().st_size != row["new_byte_length"]:
                raise PromotionError(f"successor destination differs: {destination_path}")
        if baseline_successor_test_injection("IRIS_BASELINE_SUCCESSOR_CREATE_EXTERNAL_COLLISION") == "1":
            atomic_write_new(external, b"test-owner-collision\n")
        try:
            os.link(external_stage, external)
        except FileExistsError as error:
            raise PromotionError(f"operator receipt appeared during transaction: {external}") from error
        if baseline_successor_test_injection("IRIS_BASELINE_SUCCESSOR_CRASH_AFTER_EXTERNAL_PUBLISH") == "1":
            os._exit(84)
        journal["external_published"] = True
        write_json_replace(journal_path, journal)
        if external.read_bytes() != (destination / "baseline_promotion_receipt.json").read_bytes():
            raise PromotionError("durable and operator successor receipt copies differ")
        external_stage.unlink()
        journal["state"] = "committed"
        write_json_replace(journal_path, journal)
        committed = True
        if baseline_successor_test_injection("IRIS_BASELINE_SUCCESSOR_FAIL_COMMITTED_CLEANUP") == "1":
            raise PromotionError("injected committed baseline successor cleanup failure")
        cleanup_transaction_artifacts(journal, remove_external=False)
    except Exception:
        if committed:
            raise
        try:
            restore_predecessor_generation(journal)
            cleanup_transaction_artifacts(journal, remove_external=True)
        except Exception:
            raise
        raise
    finally:
        release_transaction_lock(transaction_lock)
        if not journal_path.exists():
            lock_path.unlink(missing_ok=True)
    return None


def validate_chain(operation_path: Path, *paths: Path) -> list[dict[str, Any]]:
    operation = load_object(operation_path.resolve())
    if operation.get("schema_version") != "iris_repository_runtime_lightweighting_archive_operation_v1":
        raise PromotionError("archive operation manifest schema mismatch")
    expected_schemas = (
        "iris_repository_runtime_lightweighting_archive_receipt_v1",
        "iris_repository_runtime_lightweighting_archive_verify_receipt_v1",
        "iris_repository_runtime_lightweighting_restore_verify_receipt_v1",
    )
    rows: list[dict[str, Any]] = []
    prior_hash: str | None = None
    prior_path: Path | None = None
    for path, expected_schema in zip(paths, expected_schemas, strict=True):
        payload = load_object(path.resolve())
        if payload.get("schema_version") != expected_schema or payload.get("status") != "PASS":
            raise PromotionError(f"archive chain receipt is not expected PASS: {path}")
        if payload.get("operation_id") != operation.get("operation_id"):
            raise PromotionError(f"archive chain operation mismatch: {path}")
        if payload.get("physical_subject") != operation.get("physical_subject"):
            raise PromotionError(f"archive chain physical subject mismatch: {path}")
        if payload.get("operation_manifest_sha256") != sha256_file(operation_path.resolve()):
            raise PromotionError(f"archive chain operation-manifest binding mismatch: {path}")
        recorded_prior = payload.get("prior_receipt_sha256")
        if prior_hash is not None and recorded_prior != prior_hash:
            raise PromotionError(f"receipt chain mismatch: {path}")
        if prior_path is not None and Path(str(payload.get("prior_receipt_path", ""))).resolve() != prior_path:
            raise PromotionError(f"receipt chain prior path mismatch: {path}")
        prior_hash = sha256_file(path.resolve())
        prior_path = path.resolve()
        rows.append({"path": path.resolve().as_posix(), "sha256": prior_hash})
    archive, verify, restore = [load_object(path.resolve()) for path in paths]
    dry_path = Path(str(archive.get("prior_receipt_path", ""))).resolve()
    if not dry_path.is_file() or sha256_file(dry_path) != archive.get("prior_receipt_sha256"):
        raise PromotionError("archive receipt dry-run identity mismatch")
    dry = load_object(dry_path)
    if (
        dry.get("schema_version") != "iris_repository_runtime_lightweighting_archive_dry_run_receipt_v1"
        or dry.get("status") != "PASS"
        or dry.get("operation_id") != operation.get("operation_id")
        or dry.get("physical_subject") != operation.get("physical_subject")
        or dry.get("operation_manifest_sha256") != sha256_file(operation_path.resolve())
        or Path(str(dry.get("operation_manifest_path", ""))).resolve() != operation_path.resolve()
        or dry.get("selected_count") != len(operation.get("rows", []))
        or dry.get("selected_bytes") != sum(int(row.get("size_bytes", 0)) for row in operation.get("rows", []))
        or dry.get("source_modified") is not False
    ):
        raise PromotionError("archive dry-run receipt semantic validation failed")
    rows.insert(0, {"path": dry_path.as_posix(), "sha256": sha256_file(dry_path)})
    archive_path = Path(str(archive.get("archive_path", ""))).resolve()
    if not archive_path.is_file() or sha256_file(archive_path) != archive.get("archive_sha256"):
        raise PromotionError("archive object identity mismatch")
    if archive.get("object_reference_count") != len(operation.get("rows", [])) or archive.get("source_modified") is not False:
        raise PromotionError("archive receipt object/source disposition mismatch")
    if not isinstance(archive.get("prior_receipt_sha256"), str) or len(archive["prior_receipt_sha256"]) != 64:
        raise PromotionError("archive receipt lacks dry-run binding")
    if archive.get("ordinary_attempt_cleanup_excluded") is not True or archive.get("delete_eligible") is not False:
        raise PromotionError("archive retention disposition mismatch")
    if verify.get("full_manifest_verification") is not True or verify.get("verified_file_count") != len(operation.get("rows", [])):
        raise PromotionError("archive verify receipt is incomplete")
    if restore.get("all_sha256_verified") is not True or restore.get("restored_file_count") != len(operation.get("rows", [])):
        raise PromotionError("archive restore verification is incomplete")
    if restore.get("ordinary_attempt_cleanup_excluded") is not True or restore.get("delete_eligible") is not False:
        raise PromotionError("restore receipt retention disposition mismatch")
    if restore.get("archive_receipt_sha256") != sha256_file(paths[0].resolve()):
        raise PromotionError("restore receipt archive binding mismatch")
    if operation.get("zero_live_reference_count") != 0:
        raise PromotionError("archive operation still records live references")
    return rows


def promote_archive(args: argparse.Namespace) -> None:
    repo, destination, external = validate_roots(args.repo, args.destination_root, args.receipt_out)
    for path, role in (
        (args.source_operation_manifest, "source operation manifest"),
        (args.source_archive_receipt, "source archive receipt"),
        (args.source_verify_receipt, "source verify receipt"),
        (args.source_restore_receipt, "source restore receipt"),
    ):
        require_external_input(repo, path, role)
    chain = validate_chain(
        args.source_operation_manifest,
        args.source_archive_receipt,
        args.source_verify_receipt,
        args.source_restore_receipt,
    )
    require_external_input(repo, Path(chain[0]["path"]), "source dry-run receipt")
    operation = load_object(args.source_operation_manifest.resolve())
    require_absent(
        [
            destination / "archive_operation_manifest.json",
            destination / "archive_restore_receipt.json",
            destination / "archive_promotion_receipt.json",
            external,
        ]
    )
    rows = [
        exact_copy_new(args.source_operation_manifest.resolve(), destination / "archive_operation_manifest.json"),
        exact_copy_new(args.source_restore_receipt.resolve(), destination / "archive_restore_receipt.json"),
    ]
    payload = {
        "schema_version": "iris_repository_runtime_lightweighting_archive_promotion_v1",
        "mode": "archive",
        "physical_subject": operation.get("physical_subject"),
        "source_chain": chain,
        "promoted_files": rows,
        "byte_identity_verified": True,
        "promotion_commit_binding": "pending_reviewed_commit",
    }
    finish_receipt(destination, external, "archive_promotion_receipt.json", payload)


def promote_terminal(args: argparse.Namespace) -> None:
    repo, destination, external = validate_roots(args.repo, args.destination_root, args.receipt_out)
    for path, role in (
        (args.source_manifest, "source terminal manifest"),
        (args.source_summary, "source terminal summary"),
        (args.source_transition, "source tracking transition"),
    ):
        require_external_input(repo, path, role)
    baseline_promotion_path = args.baseline_promotion_receipt.resolve()
    expected_baseline_promotion = (destination / "baseline_promotion_receipt.json").resolve()
    if baseline_promotion_path != expected_baseline_promotion:
        raise PromotionError("terminal promotion requires the exact durable baseline promotion receipt")
    baseline_promotion = load_object(baseline_promotion_path)
    validate_baseline_promotion_payload(repo, destination, baseline_promotion)
    baseline_path = (destination / "baseline_inventory.json").resolve()
    baseline_manifest_path, baseline_manifest_bytes, _, _ = durable_baseline_lifecycle_source(
        destination
    )
    if not baseline_path.is_file():
        raise PromotionError("durable baseline evidence is incomplete")
    promoted = {
        Path(str(row.get("destination_path", ""))).resolve(): row
        for row in baseline_promotion.get("promoted_files", [])
        if isinstance(row, dict)
    }
    baseline_binding = promoted.get(baseline_path)
    if (
        not baseline_binding
        or baseline_binding.get("destination_sha256") != sha256_file(baseline_path)
        or int(baseline_binding.get("byte_length", -1)) != baseline_path.stat().st_size
    ):
        raise PromotionError("durable baseline promotion binding mismatch: baseline_inventory.json")
    manifest_binding = next(
        (
            row
            for row in baseline_promotion.get("promoted_files", [])
            if isinstance(row, dict)
            and Path(str(row.get("destination_path", ""))).name == "artifact_role_manifest.jsonl"
        ),
        None,
    )
    if (
        not manifest_binding
        or manifest_binding.get("destination_sha256") != evidence_raw_sha256(baseline_manifest_bytes)
        or int(manifest_binding.get("byte_length", -1)) != len(baseline_manifest_bytes)
    ):
        raise PromotionError("durable baseline promotion binding mismatch: artifact_role_manifest.jsonl")
    baseline = load_object(baseline_path)
    manifest_bytes, manifest_rows, representation = load_lifecycle_source(
        args.source_manifest.resolve(), "final"
    )
    summary = load_object(args.source_summary.resolve())
    transition = load_object(args.source_transition.resolve())
    actual_identity = lifecycle_repository_identity(repo)
    actual_rows, _ = lifecycle_build_rows(repo, include_missing_giants=True)
    actual_summary = lifecycle_summary_for(
        repo,
        "physical_capacity_subject",
        actual_identity,
        actual_rows,
    )
    if manifest_bytes != lifecycle_jsonl_bytes(actual_rows):
        raise PromotionError("terminal manifest differs from a fresh physical checkout census")
    if summary != actual_summary:
        raise PromotionError("terminal summary differs from a fresh physical checkout census")
    if (
        summary.get("schema_version") != "iris_repository_runtime_lightweighting_artifact_lifecycle_v1"
        or summary.get("subject_kind") != "physical_capacity_subject"
        or Path(str(summary.get("physical_resolved_root", ""))).resolve() != repo
        or summary.get("complete_accounting") is not True
        or summary.get("unclassified_count") != 0
        or summary.get("unreadable_count") != 0
        or summary.get("consumer_scan_hold_count") != 0
    ):
        raise PromotionError("terminal summary is not a complete physical-capacity census")
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD", "HEAD^{tree}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if head.returncode != 0 or head.stdout.splitlines() != [summary.get("commit"), summary.get("tree")]:
        raise PromotionError("terminal summary differs from the exact promotion checkout")
    manifest_paths = [str(row.get("path", "")) for row in manifest_rows]
    if len(manifest_paths) != len(set(manifest_paths)) or manifest_paths != sorted(manifest_paths):
        raise PromotionError("terminal manifest paths are duplicate or noncanonical")
    if summary.get("file_count") != len(manifest_rows) or summary.get("physical_bytes") != sum(
        int(row.get("size_bytes", 0)) for row in manifest_rows
    ):
        raise PromotionError("terminal manifest and summary physical accounting differ")
    if any(
        row.get("authority_role") == "unclassified"
        or row.get("path_access") == "unreadable"
        or row.get("consumer_scan_holds")
        for row in manifest_rows
    ):
        raise PromotionError("terminal manifest retains incomplete lifecycle rows")
    if (
        transition.get("schema_version") != "iris_repository_runtime_lightweighting_tracking_transition_v1"
        or transition.get("status") != "PASS"
        or transition.get("subject_kind") != "physical_capacity_subject"
        or Path(str(transition.get("physical_resolved_root", ""))).resolve() != repo
        or transition.get("baseline_run_identity") != baseline.get("run_identity")
        or transition.get("final_run_identity") != summary.get("run_identity")
        or transition.get("baseline_physical_bytes") != baseline.get("physical_bytes")
        or transition.get("final_physical_bytes") != summary.get("physical_bytes")
        or transition.get("physical_byte_delta")
        != int(summary.get("physical_bytes", 0)) - int(baseline.get("physical_bytes", 0))
        or transition.get("baseline_tracked_path_set_sha256") != baseline.get("tracked_path_set_sha256")
        or transition.get("final_tracked_path_set_sha256") != summary.get("tracked_path_set_sha256")
        or transition.get("unexpectedly_untracked_protected_count") != 0
        or transition.get("unapproved_newly_tracked_count") != 0
    ):
        raise PromotionError("terminal tracking transition semantic validation failed")
    baseline_tracked = {str(path) for path in baseline.get("tracked_paths", [])}
    final_tracked = {str(path) for path in summary.get("tracked_paths", [])}
    baseline_tracked_list = sorted(baseline_tracked)
    final_tracked_list = sorted(final_tracked)
    if baseline.get("tracked_path_set_sha256") != hashlib.sha256(
        canonical_json_bytes(baseline_tracked_list)
    ).hexdigest() or summary.get("tracked_path_set_sha256") != hashlib.sha256(
        canonical_json_bytes(final_tracked_list)
    ).hexdigest():
        raise PromotionError("terminal inventory tracked-path hash is not reproducible")
    producer_manifest_path = repo / DURABLE_RELATIVE / "producer_migration_manifest.json"
    producer_approved: set[str] = set()
    if producer_manifest_path.is_file():
        producer_manifest = load_object(producer_manifest_path)
        producer_approved = {
            str(path) for path in producer_manifest.get("approved_newly_tracked_paths", [])
        }
    added = sorted(final_tracked - baseline_tracked)
    removed = sorted(baseline_tracked - final_tracked)
    protected = {str(path) for path in baseline.get("protected_tracked_paths", [])}
    approved_additions = LIFECYCLE_TRACKING_ADDITIONS | producer_approved
    expected_transition = {
        "schema_version": "iris_repository_runtime_lightweighting_tracking_transition_v1",
        "status": "FAIL" if (set(added) - approved_additions or removed) else "PASS",
        "subject_kind": "physical_capacity_subject",
        "physical_resolved_root": repo.as_posix(),
        "baseline_run_identity": baseline.get("run_identity"),
        "final_run_identity": summary["run_identity"],
        "baseline_physical_bytes": baseline.get("physical_bytes"),
        "final_physical_bytes": summary["physical_bytes"],
        "physical_byte_delta": int(summary["physical_bytes"]) - int(baseline.get("physical_bytes", 0)),
        "baseline_tracked_path_set_sha256": baseline.get("tracked_path_set_sha256"),
        "final_tracked_path_set_sha256": summary["tracked_path_set_sha256"],
        "added_tracked_paths": added,
        "removed_tracked_paths": removed,
        "removed_tracked_count": len(removed),
        "approved_newly_tracked_paths": sorted(set(added).intersection(approved_additions)),
        "unexpectedly_untracked_protected_paths": sorted(protected.intersection(removed)),
        "unexpectedly_untracked_protected_count": len(protected.intersection(removed)),
        "unapproved_newly_tracked_paths": sorted(set(added) - approved_additions),
        "unapproved_newly_tracked_count": len(set(added) - approved_additions),
        "producer_migration_manifest": {
            "path": producer_manifest_path.relative_to(repo).as_posix(),
            "exists": producer_manifest_path.is_file(),
            "sha256": sha256_file(producer_manifest_path) if producer_manifest_path.is_file() else None,
        },
    }
    if transition != expected_transition:
        raise PromotionError("terminal tracking transition differs from fresh Git path-set recomputation")
    require_absent(
        [
            destination / "final_artifact_role_manifest.jsonl",
            destination / "final_inventory.json",
            destination / "tracking_set_transition.json",
            destination / "terminal_promotion_receipt.json",
            external,
        ]
    )
    rows = [
        exact_payload_new(
            args.source_manifest.resolve(),
            manifest_bytes,
            destination / "final_artifact_role_manifest.jsonl",
            representation,
        ),
        exact_copy_new(args.source_summary.resolve(), destination / "final_inventory.json"),
        exact_copy_new(args.source_transition.resolve(), destination / "tracking_set_transition.json"),
    ]
    payload = {
        "schema_version": "iris_repository_runtime_lightweighting_terminal_promotion_v1",
        "mode": "terminal",
        "baseline_promotion_receipt": {
            "path": baseline_promotion_path.as_posix(),
            "sha256": sha256_file(baseline_promotion_path),
        },
        "physical_subject": {
            "physical_resolved_root": summary["physical_resolved_root"],
            "commit": summary["commit"],
            "tree": summary["tree"],
            "run_identity": summary["run_identity"],
        },
        "promoted_files": rows,
        "byte_identity_verified": True,
        "semantic_validation": True,
        "promotion_commit_binding": "pending_reviewed_commit",
    }
    finish_receipt(destination, external, "terminal_promotion_receipt.json", payload)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="mode", required=True)
    baseline = sub.add_parser("baseline")
    baseline.add_argument("--repo", type=Path, required=True)
    baseline.add_argument("--source-manifest", type=Path, required=True)
    baseline.add_argument("--source-summary", type=Path, required=True)
    baseline.add_argument("--subject-receipt", type=Path, required=True)
    baseline.add_argument("--destination-root", type=Path, required=True)
    baseline.add_argument("--receipt-out", type=Path, required=True)
    baseline_successor = sub.add_parser("baseline-successor")
    baseline_successor.add_argument("--repo", type=Path, required=True)
    baseline_successor.add_argument("--source-manifest", type=Path, required=True)
    baseline_successor.add_argument("--source-summary", type=Path, required=True)
    baseline_successor.add_argument("--subject-receipt", type=Path, required=True)
    baseline_successor.add_argument("--predecessor-promotion-receipt", type=Path, required=True)
    baseline_successor.add_argument("--destination-root", type=Path, required=True)
    baseline_successor.add_argument("--receipt-out", type=Path, required=True)
    archive = sub.add_parser("archive")
    archive.add_argument("--repo", type=Path, required=True)
    archive.add_argument("--source-operation-manifest", type=Path, required=True)
    archive.add_argument("--source-archive-receipt", type=Path, required=True)
    archive.add_argument("--source-verify-receipt", type=Path, required=True)
    archive.add_argument("--source-restore-receipt", type=Path, required=True)
    archive.add_argument("--destination-root", type=Path, required=True)
    archive.add_argument("--receipt-out", type=Path, required=True)
    terminal = sub.add_parser("terminal")
    terminal.add_argument("--repo", type=Path, required=True)
    terminal.add_argument("--baseline-promotion-receipt", type=Path, required=True)
    terminal.add_argument("--source-manifest", type=Path, required=True)
    terminal.add_argument("--source-summary", type=Path, required=True)
    terminal.add_argument("--source-transition", type=Path, required=True)
    terminal.add_argument("--destination-root", type=Path, required=True)
    terminal.add_argument("--receipt-out", type=Path, required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    outcome = {
        "baseline": promote_baseline,
        "baseline-successor": promote_baseline_successor,
        "archive": promote_archive,
        "terminal": promote_terminal,
    }[args.mode](args)
    result = {"status": "PASS", "mode": args.mode}
    if outcome is not None:
        result["outcome"] = outcome
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PromotionError, OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "FAIL", "error_type": type(error).__name__, "error": str(error)}, sort_keys=True), file=sys.stderr)
        raise SystemExit(2)
