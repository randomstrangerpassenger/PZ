"""Retrieve an archived closeout bundle and check its subject and hash links."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from source_metrics_io import ContractError, canonical_bytes, git, read_json, require, sha256_file


LEGACY_MODE = "fresh-root-v1"
CARRIER_MODE = "carrier-aware-v2"
MODES = (LEGACY_MODE, CARRIER_MODE)
REQUIRED_FILES = (
    "terminal_validation_attestation.json",
    "machine_validation_manifest.json",
    "independent_review.json",
    "owner_seal.json",
    "terminal_bundle_hash_manifest.json",
    "closeout_receipt.json",
)


def artifact_tuple(value: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(value.get("closure_id", "")),
        str(value.get("terminal_subject_commit", "")),
        str(value.get("terminal_subject_tree", "")),
        str(value.get("pointer_git_blob_id", "")),
    )


def load_object(path: Path) -> dict[str, Any]:
    value = read_json(path)
    require(isinstance(value, dict), f"{path.name} must be a JSON object")
    return value


def pointer_repository(pointer_path: Path) -> tuple[Path, str]:
    repo = next((parent for parent in (pointer_path.parent, *pointer_path.parents) if (parent / ".git").exists()), None)
    require(repo is not None, "tracked pointer repository root is unavailable")
    relative = pointer_path.relative_to(repo).as_posix()
    require(not git(repo, "status", "--short", "--", relative), "tracked pointer has a working-tree delta")
    return repo, relative


def resolve_pointer_subject(pointer_path: Path, pointer: dict[str, Any]) -> tuple[str, str, str, str]:
    mode = pointer.get("subject_binding_mode")
    if mode == "fixture_explicit":
        return (
            str(pointer.get("closure_id", "")),
            str(pointer.get("terminal_subject_commit", "")),
            str(pointer.get("terminal_subject_tree", "")),
            str(pointer.get("pointer_git_blob_id", "")),
        )
    require(mode == "commit_and_tree_containing_pointer", "pointer subject binding mode mismatch")
    repo, relative = pointer_repository(pointer_path)
    return (
        str(pointer.get("closure_id", "")),
        git(repo, "rev-parse", "HEAD"),
        git(repo, "rev-parse", "HEAD^{tree}"),
        git(repo, "rev-parse", f"HEAD:{relative}"),
    )


def validate_carrier(pointer_path: Path, pointer: dict[str, Any]) -> dict[str, str]:
    require(pointer.get("subject_binding_mode") == "carrier_parent_terminal", "carrier pointer subject binding mode mismatch")
    repo, relative = pointer_repository(pointer_path)
    carrier_commit = git(repo, "rev-parse", "HEAD")
    carrier_tree = git(repo, "rev-parse", "HEAD^{tree}")
    parents = git(repo, "show", "-s", "--format=%P", "HEAD").split()
    require(len(parents) == 1, "closeout carrier must have exactly one parent")
    terminal_commit = str(pointer.get("terminal_subject_commit", ""))
    terminal_tree = str(pointer.get("terminal_subject_tree", ""))
    require(parents[0] == terminal_commit, "closeout carrier parent is not the terminal subject")
    require(git(repo, "rev-parse", f"{terminal_commit}^{{tree}}") == terminal_tree, "terminal subject tree mismatch")
    require(git(repo, "rev-list", "--count", f"{terminal_commit}..{carrier_commit}") == "1", "closeout carrier ancestry distance is not one")

    manifest_relative = str(pointer.get("carrier_manifest_path", ""))
    require(manifest_relative, "carrier manifest path is missing")
    manifest_path = (repo / manifest_relative).resolve()
    try:
        manifest_path.relative_to(repo.resolve())
    except ValueError as error:
        raise ContractError("carrier manifest path escapes repository") from error
    require(manifest_path.is_file(), "carrier manifest is missing")
    require(not git(repo, "status", "--short", "--", manifest_relative), "carrier manifest has a working-tree delta")
    manifest = load_object(manifest_path)
    require(manifest.get("schema_version") == "iris_test_precision_lightweighting_closeout_carrier_manifest_v1", "carrier manifest schema mismatch")
    require(manifest.get("terminal_subject_commit") == terminal_commit, "carrier manifest terminal commit mismatch")
    require(manifest.get("terminal_subject_tree") == terminal_tree, "carrier manifest terminal tree mismatch")
    require(manifest.get("pointer_path") == relative, "carrier manifest pointer path mismatch")
    pointer_blob = git(repo, "rev-parse", f"HEAD:{relative}")
    require(manifest.get("pointer_git_blob_id") == pointer_blob, "carrier manifest pointer blob mismatch")
    approved = sorted([relative, manifest_relative])
    require(manifest.get("allowed_delta_paths") == approved, "carrier allowed-delta path set mismatch")
    changed = []
    for line in git(repo, "diff", "--name-status", terminal_commit, carrier_commit).splitlines():
        status, path = line.split("\t", 1)
        require(status == "A", "closeout carrier may only add evidence files")
        changed.append(path.replace("\\", "/"))
    require(sorted(changed) == approved, "closeout carrier contains an unapproved delta")
    return {
        "closure_id": str(pointer.get("closure_id", "")),
        "terminal_subject_commit": terminal_commit,
        "terminal_subject_tree": terminal_tree,
        "pointer_git_blob_id": pointer_blob,
        "carrier_commit": carrier_commit,
        "carrier_tree": carrier_tree,
    }


def validate_bundle(pointer_path: Path, archive_root: Path, fresh_root: Path) -> dict[str, Any]:
    pointer = load_object(pointer_path)
    mode = str(pointer.get("retrieval_mode", ""))
    require(mode in MODES, "pointer retrieval mode mismatch")
    expected_schema = (
        "iris_test_precision_lightweighting_terminal_pointer_v1"
        if mode == LEGACY_MODE
        else "iris_test_precision_lightweighting_terminal_pointer_v2"
    )
    require(pointer.get("schema_version") == expected_schema, "pointer schema mismatch")
    require(pointer.get("terminal_evidence_placement") == "external_bundle", "pointer placement mismatch")
    require(pointer.get("append_only") is True and pointer.get("deletion_prohibited") is True, "durability contract is incomplete")
    require(not pointer.get("machine_specific_absolute_archive_path"), "pointer must not contain an absolute archive path")
    require(fresh_root.is_dir(), "fresh root is missing")
    require(not any(fresh_root.iterdir()), "fresh root must be empty")
    require(archive_root.is_dir(), "durable archive root is missing")
    require(archive_root.resolve() != fresh_root.resolve(), "durable archive and fresh root must be disjoint")

    expected_files = pointer.get("expected_terminal_filenames")
    require(expected_files == list(REQUIRED_FILES), "pointer terminal filename set/order mismatch")
    closure_id = str(pointer.get("closure_id", ""))
    require(closure_id, "closure_id is missing")
    bundle_root = archive_root / str(pointer.get("external_retrieval_key", ""))
    require(bundle_root.is_dir(), "retrieved bundle is missing")

    retrieved = fresh_root / "retrieved"
    retrieved.mkdir()
    for name in REQUIRED_FILES:
        source = bundle_root / name
        require(source.is_file(), f"terminal artifact is missing: {name}")
        shutil.copyfile(source, retrieved / name)

    attestation = load_object(retrieved / REQUIRED_FILES[0])
    machine = load_object(retrieved / REQUIRED_FILES[1])
    review = load_object(retrieved / REQUIRED_FILES[2])
    seal = load_object(retrieved / REQUIRED_FILES[3])
    manifest = load_object(retrieved / REQUIRED_FILES[4])
    receipt = load_object(retrieved / REQUIRED_FILES[5])
    carrier = validate_carrier(pointer_path, pointer) if mode == CARRIER_MODE else None
    expected_tuple = (
        (
            carrier["closure_id"],
            carrier["terminal_subject_commit"],
            carrier["terminal_subject_tree"],
            carrier["pointer_git_blob_id"],
        )
        if carrier
        else resolve_pointer_subject(pointer_path, pointer)
    )
    for label, value in (
        ("attestation", attestation), ("machine manifest", machine), ("review", review),
        ("owner seal", seal), ("bundle manifest", manifest), ("closeout receipt", receipt),
    ):
        observed = artifact_tuple(value)
        if mode == CARRIER_MODE:
            require(observed[:3] == expected_tuple[:3], f"{label} terminal subject tuple mismatch")
        else:
            require(observed == expected_tuple, f"{label} subject/pointer tuple mismatch")

    attestation_hash = sha256_file(retrieved / REQUIRED_FILES[0])
    machine_hash = sha256_file(retrieved / REQUIRED_FILES[1])
    review_hash = sha256_file(retrieved / REQUIRED_FILES[2])
    seal_hash = sha256_file(retrieved / REQUIRED_FILES[3])
    manifest_hash = sha256_file(retrieved / REQUIRED_FILES[4])
    require(machine.get("terminal_validation_attestation_sha256") == attestation_hash, "machine manifest does not bind attestation")
    for row in machine.get("constituent_machine_evidence", []):
        path = bundle_root / str(row.get("path", ""))
        require(path.is_file() and sha256_file(path) == row.get("sha256"), "machine constituent identity mismatch")
    require(review.get("machine_validation_manifest_sha256") == machine_hash, "review does not bind machine manifest")
    require(review.get("verdict") == "PASS", "independent review verdict is not PASS")
    priorities = review.get("findings_by_priority")
    require(priorities == {"P0": 0, "P1": 0, "P2": 0, "P3": 0}, "independent review findings are nonzero")
    require(seal.get("owner_seal") == "granted", "owner seal is not granted")
    require(seal.get("machine_validation_manifest_sha256") == machine_hash, "owner seal machine binding mismatch")
    require(seal.get("independent_review_sha256") == review_hash, "owner seal review binding mismatch")
    hashes = manifest.get("artifact_sha256", {})
    require(hashes.get(REQUIRED_FILES[0]) == attestation_hash, "bundle manifest attestation hash mismatch")
    require(hashes.get(REQUIRED_FILES[1]) == machine_hash, "bundle manifest machine hash mismatch")
    require(hashes.get(REQUIRED_FILES[2]) == review_hash, "bundle manifest review hash mismatch")
    require(hashes.get(REQUIRED_FILES[3]) == seal_hash, "bundle manifest owner-seal hash mismatch")
    require(REQUIRED_FILES[4] not in hashes and REQUIRED_FILES[5] not in hashes, "bundle manifest contains a cyclic hash")
    require(receipt.get("terminal_bundle_hash_manifest_sha256") == manifest_hash, "closeout receipt manifest hash mismatch")
    require(receipt.get("closeout_state") in {"complete", "partial", "implemented_only", "blocked"}, "invalid closeout state")
    require(pointer.get("allocator_receipt_sha256") == manifest.get("allocator_receipt_sha256"), "allocator receipt binding mismatch")
    if mode == CARRIER_MODE:
        require(pointer.get("terminal_bundle_hash_manifest_sha256") == manifest_hash, "carrier pointer bundle manifest hash mismatch")
        require(pointer.get("owner_seal_sha256") == seal_hash, "carrier pointer owner seal hash mismatch")

    producer = pointer.get("terminal_evidence_retrieval_capability_identity")
    require(isinstance(producer, str) and producer.endswith(":" + mode), "retrieval producer identity mismatch")
    report = {
        "schema_version": "iris_test_precision_lightweighting_terminal_retrieval_report_v1",
        "status": "PASS",
        "closure_id": closure_id,
        "terminal_subject_commit": expected_tuple[1],
        "terminal_subject_tree": expected_tuple[2],
        "pointer_git_blob_id": expected_tuple[3],
        "producer": producer,
        "external_bundle_custody_bound": True,
        "external_bundle_durability_contract_bound": True,
        "machine_validation_manifest_valid": True,
        "external_bundle_retrieval_verified": True,
        "terminal_bundle_hash_manifest_valid": True,
        "closeout_receipt_valid": True,
    }
    if carrier:
        report.update({
            "retrieval_mode": CARRIER_MODE,
            "closeout_carrier_commit": carrier["carrier_commit"],
            "closeout_carrier_tree": carrier["carrier_tree"],
            "closeout_carrier_parent": carrier["terminal_subject_commit"],
            "closeout_carrier_ancestry_distance": 1,
            "closeout_carrier_allowed_evidence_delta_only": True,
        })
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Retrieve and validate the Iris terminal evidence DAG")
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--pointer", type=Path, required=True)
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--fresh-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "retrieval report is append-only")
    pointer = load_object(args.pointer.resolve())
    require(pointer.get("retrieval_mode") == args.mode, "CLI mode and pointer retrieval mode mismatch")
    report = validate_bundle(args.pointer.resolve(), args.archive_root.resolve(), args.fresh_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(report))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContractError, json.JSONDecodeError, OSError) as error:
        raise SystemExit(f"terminal evidence validation failed: {error}") from error
