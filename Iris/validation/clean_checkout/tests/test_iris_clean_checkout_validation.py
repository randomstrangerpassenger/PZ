from __future__ import annotations

import json
from pathlib import Path

import pytest

from Iris.build.tools.common.io import repository_external_output_root
from Iris.validation.clean_checkout.iris_clean_checkout_validation_common import (
    CleanCheckoutError,
    canonical_compact_json_bytes,
    ensure_external_root,
    validate_external_environment,
    write_json_external,
)
from Iris.validation.clean_checkout.run_iris_clean_checkout_validation import (
    _classify_full_test_source,
    _full_required_source_roles,
    _ignored_status_snapshot,
    _normalized_test_id,
    _safe_checkout_target,
    _validate_explicit_required_dependencies,
    _validate_explicit_current_required_classifications,
    _validate_explicit_tool_dispositions,
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


def test_full_source_policy_classifies_only_declared_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "full_repository_gate.json"
    )
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    output_projection = contract["execution_workspace"][
        "standalone_output_projection"
    ]
    assert (
        output_projection["environment_variable"]
        == "IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT"
    )
    assert output_projection["pytest_projection"] is True
    assert output_projection["per_command_isolation"] is True
    assert output_projection["repository_output_write_count"] == 0
    repository_root = tmp_path / "repo"
    repository_root.mkdir()
    external_output = tmp_path / "external-output"
    monkeypatch.setenv(
        "IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT",
        str(external_output),
    )
    assert repository_external_output_root(
        environment_variable=(
            "IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT"
        ),
        default_root=repository_root / "Iris" / "output",
        repository_root=repository_root,
    ) == external_output.resolve()
    monkeypatch.setenv(
        "IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT",
        str(repository_root / "Iris" / "output"),
    )
    with pytest.raises(ValueError, match="outside the repository"):
        repository_external_output_root(
            environment_variable=(
                "IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT"
            ),
            default_root=repository_root / "Iris" / "output",
            repository_root=repository_root,
        )
    explicit_required_sources = {
        (
            "Iris/build/description/v2/tests/"
            "test_public_text_constituent_identity.py"
        ),
        (
            "Iris/build/description/v2/tests/"
            "test_dvf_3_3_korean_prose_compiler.py"
        ),
        (
            "Iris/build/description/v2/tests/"
            "test_naturalization_compiler_identity.py"
        ),
        (
            "Iris/build/description/v2/tests/"
            "test_iar_public_text_assessment.py"
        ),
    }
    explicit_paths = {
        row["path"]
        for row in contract["source_disposition_policy"][
            "explicit_current_required_sources"
        ]
    }
    assert explicit_required_sources <= explicit_paths
    roles = _full_required_source_roles(contract, {"rows": []})
    required_classifications = {
        path: _classify_full_test_source(path, roles)
        for path in explicit_required_sources
    }
    expected_classification = {
        "execution_role": "required_pytest",
        "authority_class": "required_tracked_source",
        "classification_basis": "explicit_current_required_source",
    }
    assert all(
        row == expected_classification
        for row in required_classifications.values()
    )
    _validate_explicit_current_required_classifications(
        contract,
        required_classifications,
    )
    direct_dependencies = _validate_explicit_required_dependencies(
        contract,
        {
            row["path"]
            for row in contract["required_test_dependency_policy"][
                "explicit_direct_dependencies"
            ]
        },
        explicit_required_sources,
    )
    iar_source = (
        "Iris/build/description/v2/tests/"
        "test_iar_public_text_assessment.py"
    )
    assert len(direct_dependencies) == 3
    assert {row["test_source"] for row in direct_dependencies} == {
        iar_source
    }
    assert {row["dependency_role"] for row in direct_dependencies} == {
        "generic_assessment_contract",
        "generic_assessment_runner",
        "generic_assessment_no_write_validator",
    }
    consumer_evidence = contract["consumer_integration_evidence_policy"][
        "explicit_evidence_roles"
    ]
    assert len(consumer_evidence) == 1
    assert consumer_evidence[0]["execution_role"] == "not_required"
    assert (
        consumer_evidence[0]["evidence_role"]
        == "consumer_integration_evidence"
    )
    assert consumer_evidence[0]["path"] not in {
        row["path"] for row in direct_dependencies
    }
    for demoted_source in explicit_required_sources:
        demoted = dict(required_classifications)
        demoted[demoted_source] = {
            "execution_role": "not_required",
            "authority_class": "historical_optional_evidence",
            "classification_basis": "historical heuristic",
        }
        with pytest.raises(
            CleanCheckoutError,
            match="classified as historical/optional",
        ):
            _validate_explicit_current_required_classifications(
                contract,
                demoted,
            )
    tool_paths = {
        row["path"]
        for row in contract["tool_disposition_policy"][
            "explicit_tool_roles"
        ]
    }
    tool_rows = _validate_explicit_tool_dispositions(
        contract,
        tool_paths,
        set(),
    )
    assert len(tool_rows) == 2
    with pytest.raises(
        CleanCheckoutError,
        match="required-test dependency",
    ):
        _validate_explicit_tool_dispositions(
            contract,
            tool_paths,
            {next(iter(tool_paths))},
        )
    historical = _classify_full_test_source(
        "Iris/build/description/v2/tests/test_old_authority.py",
        {},
    )
    assert historical["authority_class"] == "historical_optional_evidence"
    with pytest.raises(CleanCheckoutError, match="unclassified"):
        _classify_full_test_source("Iris/test/test_unknown.py", {})


def test_ignored_status_snapshot_excludes_nonignored_rows(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "Iris.validation.clean_checkout.run_iris_clean_checkout_validation."
        "_status_snapshot",
        lambda repo, include_ignored=True: (
            "1 .M N... tracked.py\n? local.py\n! ignored-output/\n"
        ),
    )
    assert _ignored_status_snapshot(tmp_path) == "! ignored-output/"


def test_full_node_identity_normalization() -> None:
    node_id = (
        "Iris/build/description/v2/tests/test_sample.py::"
        "SampleTest::test_value[param]"
    )
    assert _normalized_test_id(node_id) == (
        "test_sample.SampleTest.test_value"
    )


def test_full_materialization_target_rejects_parent_escape(
    tmp_path: Path,
) -> None:
    checkout = (tmp_path / "checkout").resolve()
    checkout.mkdir()
    with pytest.raises(CleanCheckoutError, match="unsafe"):
        _safe_checkout_target(checkout, "../outside.json")
