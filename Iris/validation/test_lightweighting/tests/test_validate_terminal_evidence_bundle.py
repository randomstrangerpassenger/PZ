from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from _common import ContractError, canonical_bytes, sha256_file
from validate_terminal_evidence_bundle import REQUIRED_FILES, validate_bundle


SUBJECT = {
    "closure_id": "iris-test-lightweighting-fixture-1",
    "terminal_subject_commit": "1" * 40,
    "terminal_subject_tree": "2" * 40,
    "pointer_git_blob_id": "3" * 40,
}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def build_bundle(root: Path) -> tuple[Path, Path]:
    archive = root / "archive"
    key = "fixture-allocation"
    bundle = archive / key
    bundle.mkdir(parents=True)
    allocator_hash = hashlib.sha256(b"allocator-receipt\n").hexdigest()
    pointer = root / "repo/Iris/_docs/refactor/test_precision_lightweighting/terminal_evidence_pointer.json"
    pointer_payload = {
        "schema_version": "iris_test_precision_lightweighting_terminal_pointer_v1",
        **SUBJECT,
        "subject_binding_mode": "fixture_explicit",
        "retrieval_mode": "fresh-root-v1",
        "terminal_evidence_placement": "external_bundle",
        "external_retrieval_key": key,
        "allocator_receipt_sha256": allocator_hash,
        "append_only": True,
        "deletion_prohibited": True,
        "machine_specific_absolute_archive_path": None,
        "expected_terminal_filenames": list(REQUIRED_FILES),
        "terminal_evidence_retrieval_capability_identity": "fixture-git-blob:fresh-root-v1",
    }
    write_json(pointer, pointer_payload)
    attestation = {"schema_version": "attestation-v1", **SUBJECT, "status": "PASS"}
    write_json(bundle / REQUIRED_FILES[0], attestation)
    machine = {
        "schema_version": "machine-v1", **SUBJECT,
        "terminal_validation_attestation_sha256": sha256_file(bundle / REQUIRED_FILES[0]),
        "constituent_machine_evidence": [],
    }
    write_json(bundle / REQUIRED_FILES[1], machine)
    review = {
        "schema_version": "review-v1", **SUBJECT,
        "machine_validation_manifest_sha256": sha256_file(bundle / REQUIRED_FILES[1]),
        "verdict": "PASS", "findings_by_priority": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
    }
    write_json(bundle / REQUIRED_FILES[2], review)
    seal = {
        "schema_version": "seal-v1", **SUBJECT, "owner_seal": "granted",
        "machine_validation_manifest_sha256": sha256_file(bundle / REQUIRED_FILES[1]),
        "independent_review_sha256": sha256_file(bundle / REQUIRED_FILES[2]),
    }
    write_json(bundle / REQUIRED_FILES[3], seal)
    manifest = {
        "schema_version": "manifest-v1", **SUBJECT,
        "allocator_receipt_sha256": allocator_hash,
        "artifact_sha256": {name: sha256_file(bundle / name) for name in REQUIRED_FILES[:4]},
    }
    write_json(bundle / REQUIRED_FILES[4], manifest)
    receipt = {
        "schema_version": "receipt-v1", **SUBJECT, "closeout_state": "complete",
        "terminal_bundle_hash_manifest_sha256": sha256_file(bundle / REQUIRED_FILES[4]),
    }
    write_json(bundle / REQUIRED_FILES[5], receipt)
    return pointer, archive


def test_fresh_root_positive_bundle_produces_all_complete_gate_values() -> None:
    with tempfile.TemporaryDirectory(prefix="iris-terminal-positive-") as value:
        root = Path(value)
        pointer, archive = build_bundle(root)
        fresh = root / "fresh"
        fresh.mkdir()
        report = validate_bundle(pointer, archive, fresh)
        assert report["status"] == "PASS"
        for key in (
            "machine_validation_manifest_valid", "external_bundle_retrieval_verified",
            "terminal_bundle_hash_manifest_valid", "closeout_receipt_valid",
        ):
            assert report[key] is True


def test_fresh_root_missing_bundle_fails_closed() -> None:
    with tempfile.TemporaryDirectory(prefix="iris-terminal-missing-") as value:
        root = Path(value)
        pointer, archive = build_bundle(root)
        shutil.rmtree(archive / "fixture-allocation")
        fresh = root / "fresh"
        fresh.mkdir()
        with pytest.raises(ContractError, match="retrieved bundle is missing"):
            validate_bundle(pointer, archive, fresh)


def test_fresh_root_tampered_review_fails_closed() -> None:
    with tempfile.TemporaryDirectory(prefix="iris-terminal-tamper-") as value:
        root = Path(value)
        pointer, archive = build_bundle(root)
        review = archive / "fixture-allocation" / REQUIRED_FILES[2]
        payload = json.loads(review.read_text(encoding="utf-8"))
        payload["verdict"] = "FAIL"
        write_json(review, payload)
        fresh = root / "fresh"
        fresh.mkdir()
        with pytest.raises(ContractError, match="review verdict"):
            validate_bundle(pointer, archive, fresh)
