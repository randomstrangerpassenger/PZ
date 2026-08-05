#!/usr/bin/env python
"""Promote verified external lifecycle evidence into the Git-visible durable sink."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from report_artifact_lifecycle import (
    LIFECYCLE_TRACKING_ADDITIONS,
    build_rows as lifecycle_build_rows,
    canonical_jsonl_bytes as lifecycle_jsonl_bytes,
    repository_identity as lifecycle_repository_identity,
    summary_for as lifecycle_summary_for,
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


def atomic_write_new(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise PromotionError(f"destination already exists: {path}")
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.exists():
        raise PromotionError(f"temporary destination already exists: {temporary}")
    temporary.write_bytes(payload)
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
    bindings = (("manifest", source_manifest), ("summary", source_summary))
    for key, source in bindings:
        binding = receipt.get(key, {})
        if os.path.normcase(str(Path(str(binding.get("path"))).resolve())) != os.path.normcase(str(source.resolve())):
            raise PromotionError(f"{key} source path differs from subject receipt")
        if sha256_file(source) != binding.get("sha256"):
            raise PromotionError(f"{key} source hash differs from subject receipt")
        if source.stat().st_size != binding.get("bytes"):
            raise PromotionError(f"{key} source length differs from subject receipt")
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


def promote_baseline(args: argparse.Namespace) -> None:
    repo, destination, external = validate_roots(args.repo, args.destination_root, args.receipt_out)
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
    manifest_rows = load_jsonl(args.source_manifest.resolve())
    actual_identity = lifecycle_repository_identity(repo)
    actual_rows, _ = lifecycle_build_rows(repo, include_missing_giants=True)
    actual_summary = lifecycle_summary_for(
        repo,
        "physical_capacity_subject",
        actual_identity,
        actual_rows,
    )
    if args.source_manifest.resolve().read_bytes() != lifecycle_jsonl_bytes(actual_rows):
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
    require_absent(
        [
            destination / "artifact_role_manifest.jsonl",
            destination / "baseline_inventory.json",
            destination / "baseline_promotion_receipt.json",
            external,
        ]
    )
    rows = [
        exact_copy_new(args.source_manifest.resolve(), destination / "artifact_role_manifest.jsonl"),
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
    if (
        baseline_promotion.get("schema_version") != "iris_repository_runtime_lightweighting_baseline_promotion_v1"
        or baseline_promotion.get("mode") != "baseline"
        or baseline_promotion.get("byte_identity_verified") is not True
    ):
        raise PromotionError("baseline promotion receipt is not authoritative")
    baseline_path = (destination / "baseline_inventory.json").resolve()
    baseline_manifest_path = (destination / "artifact_role_manifest.jsonl").resolve()
    if not baseline_path.is_file() or not baseline_manifest_path.is_file():
        raise PromotionError("durable baseline evidence is incomplete")
    promoted = {
        Path(str(row.get("destination_path", ""))).resolve(): row
        for row in baseline_promotion.get("promoted_files", [])
        if isinstance(row, dict)
    }
    for durable_path in (baseline_path, baseline_manifest_path):
        binding = promoted.get(durable_path)
        if (
            not binding
            or binding.get("destination_sha256") != sha256_file(durable_path)
            or int(binding.get("byte_length", -1)) != durable_path.stat().st_size
        ):
            raise PromotionError(f"durable baseline promotion binding mismatch: {durable_path.name}")
    baseline = load_object(baseline_path)
    manifest_rows = load_jsonl(args.source_manifest.resolve())
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
    if args.source_manifest.resolve().read_bytes() != lifecycle_jsonl_bytes(actual_rows):
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
        exact_copy_new(args.source_manifest.resolve(), destination / "final_artifact_role_manifest.jsonl"),
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
    {"baseline": promote_baseline, "archive": promote_archive, "terminal": promote_terminal}[args.mode](args)
    print(json.dumps({"status": "PASS", "mode": args.mode}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PromotionError, OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "FAIL", "error_type": type(error).__name__, "error": str(error)}, sort_keys=True), file=sys.stderr)
        raise SystemExit(2)
