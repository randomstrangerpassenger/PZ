from __future__ import annotations

import json
import tempfile
from pathlib import Path

from Iris.validation.baseline.qualification_contracts import path_preflight, read_json, sha256_file, validate_registry
from Iris.validation.baseline.collect_baseline_qualification import (
    _classify_observed_failure,
    _windows_powershell_environment,
    forensic_evidence_capture_pass,
)
from Iris.validation.baseline.validate_baseline_qualification import execute_negative_matrix, synthetic_gate


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]


def test_registry_has_complete_negative_coverage() -> None:
    report = validate_registry(read_json(ROOT / "contracts/admission_precondition_registry.json"), read_json(ROOT / "contracts/admission_negative_fixture_registry.json"))
    assert report["status"] == "PASS"
    assert report["uncovered_precondition_count"] == 0
    assert report["orphan_negative_case_count"] == 0


def test_registry_executes_each_negative_and_never_calls_mutator(tmp_path: Path) -> None:
    report = execute_negative_matrix(
        read_json(ROOT / "contracts/admission_precondition_registry.json"),
        read_json(ROOT / "contracts/admission_negative_fixture_registry.json"),
        tmp_path,
    )
    assert report["status"] == "PASS"
    assert report["known_bad_s_base_rejected"] is True
    assert report["known_bad_s_base_exact_checkout_exercised"] is True
    assert report["qualification_over_budget_preflight_before_clone_proven"] is True
    assert report["mutator_called_on_rejected_case_count"] == 0
    assert report["executable_negative_case_count"] >= report["admission_precondition_count"]
    path_case = next(
        row
        for row in report["cases"]
        if row["fixture_id"] == "qualification_one_character_over_budget_before_clone"
    )
    assert path_case["materialized_path_length"] == path_case["qualified_materialized_path_limit"] + 1
    assert path_case["checkout_work_result_mutation_count"] == 0


def test_registry_rejects_orphan_fixture_reference() -> None:
    preconditions = {"preconditions": [{"precondition_id": "p"}]}
    fixtures = {
        "fixtures": [
            {
                "fixture_id": "f",
                "invalidates": ["gone"],
                "mutation": {"field": "gone", "value": False},
                "expected_rejection_code": "precondition_gone_failed",
            }
        ]
    }
    report = validate_registry(preconditions, fixtures)
    assert report["status"] == "FAIL"
    assert report["orphan_negative_case_count"] == 1


def test_synthetic_gate_never_calls_rejected_mutator() -> None:
    report = synthetic_gate({"admission_status": "rejected"})
    assert report["status"] == "REJECTED"
    assert report["mutator_call_count"] == 0


def test_forensic_capture_passes_for_complete_non_green_s_base_evidence(tmp_path: Path) -> None:
    denominator = {
        "schema_version": "round3-denominator-execution-receipt-v1",
        "status": "PASS",
        "ordered_node_ids_sha256": "a" * 64,
    }
    (tmp_path / "configured-current-collection.json").write_text(json.dumps(denominator), encoding="utf-8")
    (tmp_path / "configured-current.json").write_text(json.dumps(denominator), encoding="utf-8")
    (tmp_path / "exact-current.json").write_text(
        json.dumps({
            "schema_version": "round3-contract-test-run-v1",
            "success": False,
            "test_count": 1,
            "failures": [{"traceback": "actual exact trace"}],
            "errors": [],
        }),
        encoding="utf-8",
    )
    (tmp_path / "configured-current.junit.xml").write_text(
        '<testsuite><testcase classname="suite.Case" name="test_failure"><failure>actual trace</failure></testcase></testsuite>',
        encoding="utf-8",
    )
    rtc_raw = {
        "schema_version": "rtc-validator-failure-v1",
        "status": "BLOCKED",
        "failure_code": "implementation_toolchain_freshness_failed",
    }
    (tmp_path / "rtc-required-gate.json").write_text(json.dumps(rtc_raw), encoding="utf-8")
    rtc_observation = {
        "schema_version": "iris-baseline-admission-rtc-forensic-observation-v1",
        "status": "PASS",
        "subject": {
            "commit": "671c7b928ad5a1dbf26ea76949462fa8a7287903",
            "tree": "20bbbdb919fa97a44e03c1f1cb9ea0a6973fb1db",
        },
        "raw_required_gate_receipt_sha256": sha256_file(tmp_path / "rtc-required-gate.json"),
        "expected_failure_code": "implementation_toolchain_freshness_failed",
        "observed_failure_code": "implementation_toolchain_freshness_failed",
        "expected_observed_failure_code_match": True,
        "selected_bundle_member_count": 11,
        "selected_bundle_integrity_verified": True,
        "toolchain_manifest_integrity_verified": True,
        "all_hypotheses_evidence_derived": True,
        "hypotheses": {
            "H1_gate_reason_classification": {"finding": "supported"},
            "H2_stale_expected_governance_state": {"finding": "not_supported"},
            "H3_durable_materialization_defect": {"finding": "not_supported"},
            "H4_windows_path_observation_defect": {"finding": "not_supported"},
        },
    }
    (tmp_path / "rtc-required-gate-observation.json").write_text(
        json.dumps(rtc_observation), encoding="utf-8"
    )
    attempts = {}
    for name, code in (
        ("collection", 0), ("exact_current", 1), ("configured_current", 1),
        ("rtc_required_gate", 2),
    ):
        stdout = tmp_path / f"{name}.stdout.log"
        stderr = tmp_path / f"{name}.stderr.log"
        stdout.write_text("stdout", encoding="utf-8")
        stderr.write_text("stderr", encoding="utf-8")
        attempts[name] = {
            "native_exit_code": code,
            "stdout": stdout.name,
            "stdout_sha256": sha256_file(stdout),
            "stderr": stderr.name,
            "stderr_sha256": sha256_file(stderr),
        }
    ledger = {
        "nodes": [{"node_id": "suite.Case::test_failure"}],
        "unknown_failure_count": 0,
        "evidence_absent_unclassifiable_count": 0,
        "subject_finding_count": 0,
        "all_existing_nodes_have_evidence_bound_disposition": True,
        "primary_and_propagated_relation_complete": True,
    }
    required_paths = tuple(tmp_path / name for name in (
        "configured-current-collection.json", "exact-current.json",
        "configured-current.json", "configured-current.junit.xml",
        "rtc-required-gate.json", "rtc-required-gate-observation.json",
    ))
    assert forensic_evidence_capture_pass(
        result_root=tmp_path,
        attempts=attempts,
        required_paths=required_paths,
        ledger=ledger,
        status_before="",
        status_after="",
        ignored_before="",
        ignored_after="",
    )
    required_paths[0].unlink()
    assert not forensic_evidence_capture_pass(
        result_root=tmp_path,
        attempts=attempts,
        required_paths=required_paths,
        ledger=ledger,
        status_before="",
        status_after="",
        ignored_before="",
        ignored_after="",
    )


def test_forensic_trace_classifier_is_signature_bound_and_fail_closed() -> None:
    signatures = {
        "Get-FileHash is not recognized as the name of a cmdlet": "root-powershell-hash-autoload",
        "registry-authority-projection failed with [WinError 145]": "root-registry-projection-cleanup",
        "test_historical_reproduction_corpus_is_exact_and_fail_closed: No such file or directory":
            "root-historical-overlay-path-materialization",
        "AssertionError: missing fixture output: C:/external/legacy-output/a.json":
            "root-legacy-output-materialization",
    }
    for evidence, expected_root in signatures.items():
        classification = _classify_observed_failure(evidence)
        assert classification is not None
        assert classification["root_cause_id"] == expected_root
    assert _classify_observed_failure("AssertionError: unrelated candidate defect") is None


def test_full_gate_declares_dedicated_route_disposition() -> None:
    contract = json.loads((REPO / "Iris/validation/execution/contracts/repository_test_gate.json").read_text(encoding="utf-8"))
    rows = contract["source_disposition_policy"]["explicit_dedicated_route_sources"]
    assert {row["path"] for row in rows} == {
        "Iris/validation/baseline/tests/test_baseline_qualification.py",
        "Iris/validation/baseline/tests/test_reseal_output_isolation.py",
        "Iris/validation/baseline/tests/test_windows_path_contract.py",
    }
    assert {row["owner_decision"] for row in rows} == {"not_applicable_dedicated_route"}
    environment = _windows_powershell_environment({
        "ProgramFiles": r"C:\Program Files",
        "WINDIR": r"C:\Windows",
        "PSModulePath": r"C:\incompatible\PowerShell\Modules",
    })
    assert environment["PSModulePath"] == ";".join((
        r"C:\Program Files\WindowsPowerShell\Modules",
        r"C:\Windows\System32\WindowsPowerShell\v1.0\Modules",
    ))
