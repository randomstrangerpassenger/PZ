from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
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


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def build_carrier_bundle(
    root: Path,
    *,
    carrier_spoof: bool = False,
    terminal_tree_spoof: bool = False,
) -> tuple[Path, Path]:
    repo = root / "repo"
    repo.mkdir()
    run_git(repo, "init", "-q")
    run_git(repo, "config", "user.name", "Iris Test")
    run_git(repo, "config", "user.email", "iris-test@example.invalid")
    (repo / "terminal.txt").write_text("terminal\n", encoding="utf-8")
    run_git(repo, "add", "terminal.txt")
    run_git(repo, "commit", "-q", "-m", "terminal")
    terminal_commit = run_git(repo, "rev-parse", "HEAD")
    terminal_tree = run_git(repo, "rev-parse", "HEAD^{tree}")
    subject = {
        "closure_id": "iris-test-lightweighting-carrier-fixture-1",
        "terminal_subject_commit": terminal_commit,
        "terminal_subject_tree": "f" * 40 if terminal_tree_spoof else terminal_tree,
    }

    archive = root / "archive"
    key = "carrier-fixture-allocation"
    bundle = archive / key
    bundle.mkdir(parents=True)
    allocator_hash = hashlib.sha256(b"carrier-allocator-receipt\n").hexdigest()
    attestation = {"schema_version": "attestation-v1", **subject, "status": "PASS"}
    write_json(bundle / REQUIRED_FILES[0], attestation)
    machine = {
        "schema_version": "machine-v1", **subject,
        "terminal_validation_attestation_sha256": sha256_file(bundle / REQUIRED_FILES[0]),
        "constituent_machine_evidence": [],
    }
    write_json(bundle / REQUIRED_FILES[1], machine)
    review = {
        "schema_version": "review-v1", **subject,
        "machine_validation_manifest_sha256": sha256_file(bundle / REQUIRED_FILES[1]),
        "verdict": "PASS", "findings_by_priority": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
    }
    write_json(bundle / REQUIRED_FILES[2], review)
    seal = {
        "schema_version": "seal-v1", **subject, "owner_seal": "granted",
        "machine_validation_manifest_sha256": sha256_file(bundle / REQUIRED_FILES[1]),
        "independent_review_sha256": sha256_file(bundle / REQUIRED_FILES[2]),
    }
    write_json(bundle / REQUIRED_FILES[3], seal)
    manifest = {
        "schema_version": "manifest-v1", **subject,
        "allocator_receipt_sha256": allocator_hash,
        "artifact_sha256": {name: sha256_file(bundle / name) for name in REQUIRED_FILES[:4]},
    }
    write_json(bundle / REQUIRED_FILES[4], manifest)
    receipt = {
        "schema_version": "receipt-v1", **subject, "closeout_state": "complete",
        "terminal_bundle_hash_manifest_sha256": sha256_file(bundle / REQUIRED_FILES[4]),
    }
    write_json(bundle / REQUIRED_FILES[5], receipt)

    pointer_relative = "Iris/_docs/refactor/test_precision_lightweighting/terminal_closeout_recovery/terminal_evidence_pointer.json"
    manifest_relative = "Iris/_docs/refactor/test_precision_lightweighting/terminal_closeout_recovery/closeout_carrier_manifest.json"
    pointer = repo / pointer_relative
    pointer_payload = {
        "schema_version": "iris_test_precision_lightweighting_terminal_pointer_v2",
        **subject,
        "subject_binding_mode": "carrier_parent_terminal",
        "retrieval_mode": "carrier-aware-v2",
        "terminal_evidence_placement": "external_bundle",
        "external_retrieval_key": key,
        "allocator_receipt_sha256": allocator_hash,
        "terminal_bundle_hash_manifest_sha256": sha256_file(bundle / REQUIRED_FILES[4]),
        "owner_seal_sha256": sha256_file(bundle / REQUIRED_FILES[3]),
        "append_only": True,
        "deletion_prohibited": True,
        "machine_specific_absolute_archive_path": None,
        "expected_terminal_filenames": list(REQUIRED_FILES),
        "carrier_manifest_path": manifest_relative,
        "terminal_evidence_retrieval_capability_identity": "fixture-git-blob:carrier-aware-v2",
    }
    write_json(pointer, pointer_payload)
    pointer_blob = run_git(repo, "hash-object", pointer_relative)
    carrier_manifest = repo / manifest_relative
    write_json(carrier_manifest, {
        "schema_version": "iris_test_precision_lightweighting_closeout_carrier_manifest_v1",
        **subject,
        "pointer_path": pointer_relative,
        "pointer_git_blob_id": pointer_blob,
        "allowed_delta_paths": sorted([pointer_relative, manifest_relative]),
    })
    if carrier_spoof:
        spoof = repo / "Iris/_docs/refactor/test_precision_lightweighting/terminal_closeout_recovery/unapproved.json"
        write_json(spoof, {"unapproved": True})
    run_git(repo, "add", "Iris/_docs/refactor/test_precision_lightweighting/terminal_closeout_recovery")
    run_git(repo, "commit", "-q", "-m", "carrier")
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


def test_carrier_aware_v2_positive_bundle_produces_terminal_carrier_chain() -> None:
    with tempfile.TemporaryDirectory(prefix="iris-terminal-carrier-positive-") as value:
        root = Path(value)
        pointer, archive = build_carrier_bundle(root)
        fresh = root / "fresh"
        fresh.mkdir()
        report = validate_bundle(pointer, archive, fresh)
        assert report["status"] == "PASS"
        assert report["retrieval_mode"] == "carrier-aware-v2"
        assert report["closeout_carrier_parent"] == report["terminal_subject_commit"]
        assert report["closeout_carrier_ancestry_distance"] == 1
        assert report["closeout_carrier_allowed_evidence_delta_only"] is True


def test_carrier_aware_v2_missing_bundle_fails_closed() -> None:
    with tempfile.TemporaryDirectory(prefix="iris-terminal-carrier-missing-") as value:
        root = Path(value)
        pointer, archive = build_carrier_bundle(root)
        shutil.rmtree(archive / "carrier-fixture-allocation")
        fresh = root / "fresh"
        fresh.mkdir()
        with pytest.raises(ContractError, match="retrieved bundle is missing"):
            validate_bundle(pointer, archive, fresh)


def test_carrier_aware_v2_tampered_bundle_fails_closed() -> None:
    with tempfile.TemporaryDirectory(prefix="iris-terminal-carrier-tampered-") as value:
        root = Path(value)
        pointer, archive = build_carrier_bundle(root)
        review = archive / "carrier-fixture-allocation" / REQUIRED_FILES[2]
        payload = json.loads(review.read_text(encoding="utf-8"))
        payload["verdict"] = "FAIL"
        write_json(review, payload)
        fresh = root / "fresh"
        fresh.mkdir()
        with pytest.raises(ContractError, match="review verdict"):
            validate_bundle(pointer, archive, fresh)


def test_carrier_aware_v2_carrier_spoof_fails_closed() -> None:
    with tempfile.TemporaryDirectory(prefix="iris-terminal-carrier-spoof-") as value:
        root = Path(value)
        pointer, archive = build_carrier_bundle(root, carrier_spoof=True)
        fresh = root / "fresh"
        fresh.mkdir()
        with pytest.raises(ContractError, match="unapproved delta"):
            validate_bundle(pointer, archive, fresh)


def test_carrier_aware_v2_terminal_subject_spoof_fails_closed() -> None:
    with tempfile.TemporaryDirectory(prefix="iris-terminal-subject-spoof-") as value:
        root = Path(value)
        pointer, archive = build_carrier_bundle(root, terminal_tree_spoof=True)
        fresh = root / "fresh"
        fresh.mkdir()
        with pytest.raises(ContractError, match="terminal subject tree mismatch"):
            validate_bundle(pointer, archive, fresh)
