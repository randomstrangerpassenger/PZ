from __future__ import annotations

import json
from pathlib import Path

import pytest

from Iris.validation.clean_checkout.iris_clean_checkout_validation_common import (
    CleanCheckoutError,
    canonical_compact_json_bytes,
    ensure_external_root,
    validate_external_environment,
    write_json_external,
)
from Iris.validation.clean_checkout.validate_iris_clean_checkout_validation import (
    validate_result_pair,
)


def _fake_repo(path: Path) -> Path:
    repo = path / "repo"
    (repo / ".git").mkdir(parents=True)
    return repo.resolve()


def test_external_root_rejects_checkout_descendant(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    with pytest.raises(CleanCheckoutError, match="outside the checkout"):
        ensure_external_root(repo, repo / "result")


def test_external_root_rejects_checkout_ancestor(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    with pytest.raises(CleanCheckoutError, match="must not contain"):
        ensure_external_root(repo, tmp_path)


def test_external_root_accepts_disjoint_sibling(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path / "checkout-parent")
    result = ensure_external_root(repo, tmp_path / "result")
    assert result == (tmp_path / "result").resolve()
    assert result.is_dir()


def test_external_writer_rejects_repository_path(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    with pytest.raises(CleanCheckoutError, match="repository-local"):
        write_json_external(repo, repo / "result.json", {"status": "PASS"})


def test_altered_environment_receipt_fails_before_execution(
    tmp_path: Path,
) -> None:
    receipt = tmp_path / "environment_receipt.json"
    receipt.write_bytes(
        canonical_compact_json_bytes(
            {
                "schema_version": (
                    "iris_clean_checkout_external_environment_receipt_v1"
                )
            }
        )
    )
    with pytest.raises(CleanCheckoutError, match="receipt hash differs"):
        validate_external_environment(
            Path(__file__),
            receipt,
            {
                "immutable_environment_receipt_path": str(receipt),
                "immutable_environment_receipt_sha256": "0" * 64,
                "interpreter_sha256": "0" * 64,
                "external_environment_root": str(tmp_path),
                "environment_content_manifest_sha256": "0" * 64,
                "package_set_sha256": "0" * 64,
            },
        )


def _canonical_result(status: str = "PASS") -> dict[str, object]:
    return {
        "schema_version": "iris-clean-checkout-canonical-result-v2",
        "status": status,
        "subject": {
            "commit": "1" * 40,
            "tree": "2" * 40,
        },
        "test_identity_count": 1,
        "test_inventory_sha256": "3" * 64,
    }


def test_result_pair_requires_byte_equivalent_payloads(
    tmp_path: Path,
) -> None:
    run_a = tmp_path / "run-a.json"
    run_b = tmp_path / "run-b.json"
    run_a.write_text(json.dumps(_canonical_result()), encoding="utf-8")
    run_b.write_text(
        json.dumps(_canonical_result("FAIL")),
        encoding="utf-8",
    )
    with pytest.raises(CleanCheckoutError, match="Run B is not PASS"):
        validate_result_pair(run_a, run_b)


def test_result_pair_accepts_equivalent_passes(tmp_path: Path) -> None:
    run_a = tmp_path / "run-a.json"
    run_b = tmp_path / "run-b.json"
    payload = json.dumps(_canonical_result())
    run_a.write_text(payload, encoding="utf-8")
    run_b.write_text(payload, encoding="utf-8")
    result = validate_result_pair(run_a, run_b)
    assert result["status"] == "PASS"
    assert result["canonical_results_equal"] is True
