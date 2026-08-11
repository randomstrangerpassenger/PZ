from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from _common import ContractError, canonical_bytes, read_json, require, sha256_file


MODE = "fresh-root-v1"
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


def validate_bundle(pointer_path: Path, archive_root: Path, fresh_root: Path) -> dict[str, Any]:
    pointer = load_object(pointer_path)
    require(pointer.get("schema_version") == "iris_test_precision_lightweighting_terminal_pointer_v1", "pointer schema mismatch")
    require(pointer.get("retrieval_mode") == MODE, "pointer retrieval mode mismatch")
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
    expected_tuple = (
        closure_id,
        str(pointer.get("terminal_subject_commit", "")),
        str(pointer.get("terminal_subject_tree", "")),
        str(pointer.get("pointer_git_blob_id", "")),
    )
    for label, value in (
        ("attestation", attestation), ("machine manifest", machine), ("review", review),
        ("owner seal", seal), ("bundle manifest", manifest), ("closeout receipt", receipt),
    ):
        require(artifact_tuple(value) == expected_tuple, f"{label} subject/pointer tuple mismatch")

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

    producer = pointer.get("terminal_evidence_retrieval_capability_identity")
    require(isinstance(producer, str) and producer.endswith(":" + MODE), "retrieval producer identity mismatch")
    return {
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Retrieve and validate the Iris terminal evidence DAG")
    parser.add_argument("--mode", choices=[MODE], required=True)
    parser.add_argument("--pointer", type=Path, required=True)
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--fresh-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "retrieval report is append-only")
    report = validate_bundle(args.pointer.resolve(), args.archive_root.resolve(), args.fresh_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(report))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContractError, json.JSONDecodeError, OSError) as error:
        raise SystemExit(f"terminal evidence validation failed: {error}") from error
