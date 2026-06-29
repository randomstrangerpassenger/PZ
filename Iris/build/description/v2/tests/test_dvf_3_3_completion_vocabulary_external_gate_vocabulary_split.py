from __future__ import annotations

import json
import hashlib
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split"
RUNNER = TOOLS / "run_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py"
VALIDATOR = TOOLS / "validate_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py"
NEGATIVE_FIXTURES = REPO / "Iris/build/description/v2/tests/fixtures/negative/completion_vocabulary_external_gate"
POSITIVE_FIXTURES = REPO / "Iris/build/description/v2/tests/fixtures/positive/completion_vocabulary_external_gate"
INNER_CURRENT_ROUTE = os.environ.get("DVF_COMPLETION_VOCAB_SPLIT_INNER_CURRENT_ROUTE") == "1"

sys.path.insert(0, str(TOOLS))
from dvf_3_3_completion_vocabulary_external_gate_vocabulary_split import (
    validate_governance_payload,
    validate_owner_seal_record,
    validate_review_bundle_manifest,
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def fixture_file_paths() -> list[Path]:
    return sorted(NEGATIVE_FIXTURES.glob("*.json")) + sorted(POSITIVE_FIXTURES.glob("*.json"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def forged_canonical_satisfied_payload(binding: dict) -> dict:
    return {
        "canonical_external_review_state": "satisfied",
        "canonical_seal_allowed": True,
        "decision_authority": "owner",
        "external_gate_state": "satisfied",
        "external_validation_bundle_result": "PASS",
        "external_validation_bundle_state": "present",
        "independent_review_artifact_binding": binding,
        "independent_review_artifact_present": True,
        "independent_review_state": "present",
        "independent_review_verdict": "PASS",
        "legacy_projection_consumed_for_current_gate": False,
        "machine_contract_validation": "PASS",
        "owner_decision": "approved",
        "owner_decision_basis": "fixture",
        "owner_decision_captured_by": "fixture",
        "owner_decision_readpoint": "fixture",
        "owner_decision_scope": "final_canonical_external_gate_seal",
        "owner_decision_source_kind": "owner_supplied",
        "owner_identity": "owner",
        "owner_seal_basis": "fixture",
        "owner_seal_captured_by": "fixture",
        "owner_seal_does_not_replace_review": True,
        "owner_seal_hash_binding": binding,
        "owner_seal_readpoint": "fixture",
        "owner_seal_scope": "final_canonical_external_gate_seal",
        "owner_seal_source_kind": "owner_supplied",
        "owner_seal_state": "sealed",
        "review_bundle_hash_sealed": True,
        "reviewed_artifact_list": [binding],
        "reviewed_validation_result_or_rerun_result": binding,
        "reviewed_validation_result_present": True,
        "reviewer_identity": "independent reviewer",
        "reviewer_identity_present": True,
        "reviewer_independence_declaration": "independent",
        "reviewer_independence_proven": True,
        "reviewer_independent_from_author": True,
        "reviewer_independent_from_executor": True,
        "reviewer_independent_from_roadmap_author": True,
        "reviewer_independent_from_self_record_generator": True,
        "reviewer_independent_from_upstream_governance_chain_artifact_author": True,
        "reviewer_role": "reviewer",
        "reviewer_role_present": True,
        "reviewer_scope": "final_canonical_external_gate_seal",
        "reviewer_scope_present": True,
        "self_generated_artifact_flag": False,
        "hash_sealed_review_bundle_reference": binding,
        "readpoint": "fixture",
        "review_timestamp": "2026-06-28T00:00:00Z",
    }


class DvfCompletionVocabularyExternalGateVocabularySplitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if INNER_CURRENT_ROUTE:
            return
        final_report = ROOT / "phase9/final_completion_vocabulary_external_gate_split_report.json"
        current_route = ROOT / "phase8/current_route_validation_result.json"
        matrix_report = ROOT / "phase7/negative_fixture_matrix_report.json"
        if final_report.exists() and current_route.exists() and matrix_report.exists():
            final = load_json(final_report)
            route = load_json(current_route)
            matrix = load_json(matrix_report)
            route_pass = route.get("status") == "PASS" or (
                route.get("success") is True and route.get("closure_enforced") is True
            )
            fixture_sources = {repo_rel(path) for path in fixture_file_paths()}
            matrix_fresh = matrix.get("fixture_file_count") == len(fixture_sources) and set(matrix.get("fixture_sources", [])) == fixture_sources
            final_complete = (
                final.get("status") == "PASS"
                and final.get("canonical_external_review_state") == "satisfied"
                and final.get("canonical_seal_allowed") is True
                and final.get("owner_seal_state") == "sealed"
                and final.get("token_rename_author_signoff_state") == "signed"
            )
            if final_complete and route_pass and matrix_fresh:
                return
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--mode", "machine-pass"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "completion vocabulary external gate split runner failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_canonical_schema_and_negative_fixture_matrix(self) -> None:
        schema = load_json(ROOT / "phase2/canonical_vocabulary_schema.json")
        absence = load_json(ROOT / "phase3/absence_mapping_schema_report.json")
        notes = load_json(ROOT / "phase2/pass_with_notes_note_schema.json")
        matrix = load_json(ROOT / "phase7/negative_fixture_matrix_report.json")

        self.assertEqual(schema["status"], "PASS")
        self.assertEqual(
            schema["pass_allowed_only_on"],
            [
                "machine_contract_validation",
                "external_validation_bundle_result",
                "independent_review_verdict",
            ],
        )
        self.assertIn("owner_decision", schema["bare_pass_forbidden_on"])
        self.assertFalse(absence["absence_maps_to_satisfied_allowed"])
        self.assertFalse(notes["blocking_note_allows_external_gate_satisfied"])
        self.assertEqual(matrix["status"], "PASS")
        self.assertEqual(matrix["unexpected_pass_count"], 0)
        fixture_files = fixture_file_paths()
        self.assertEqual(matrix["fixture_file_count"], len(fixture_files))
        self.assertEqual(set(matrix["fixture_sources"]), {repo_rel(path) for path in fixture_files})
        fixtures = {row["fixture"]: row for row in matrix["fixtures"]}
        self.assertFalse(fixtures["boolean_only_canonical_satisfied"]["observed_pass"])
        self.assertFalse(fixtures["historical_path_spoof_current_payload"]["observed_pass"])
        self.assertFalse(fixtures["owner_pass_current"]["observed_pass"])
        self.assertFalse(fixtures["owner_seal_missing_capture_metadata"]["observed_pass"])
        self.assertFalse(fixtures["gate_pass_current"]["observed_pass"])
        self.assertFalse(fixtures["absence_maps_to_satisfied"]["observed_pass"])
        self.assertFalse(fixtures["pass_with_notes_blocking"]["observed_pass"])
        self.assertFalse(fixtures["string_path_canonical_satisfied"]["observed_pass"])
        self.assertTrue(fixtures["complete_current_canonical_satisfied"]["observed_pass"])
        self.assertTrue(fixtures["historical_legacy_pass_trace"]["observed_pass"])

        complete = load_json(POSITIVE_FIXTURES / "complete_current_canonical_satisfied.json")
        self.assertEqual(validate_governance_payload(complete, repo_root=REPO), [])
        support = POSITIVE_FIXTURES / "support"
        review_payload = load_json(support / "independent_review_artifact.json")
        bundle_payload = load_json(support / "independent_review_bundle.json")
        bad_bundle = {
            **bundle_payload,
            "reviewed_artifact_list": [{"path": "missing/reviewed.json", "sha256": "0" * 64}],
            "reviewed_validation_result_or_rerun_result": {"path": "missing/result.json", "sha256": "0" * 64},
        }
        bundle_errors: list[dict] = []
        validate_review_bundle_manifest(
            bad_bundle,
            review_payload=review_payload,
            review_artifact_binding=complete["independent_review_artifact_binding"],
            errors=bundle_errors,
            repo_root=REPO,
        )
        bundle_error_codes = {error["code"] for error in bundle_errors}
        self.assertIn("hash_binding_target_missing", bundle_error_codes)
        self.assertIn("independent_review_bundle_reviewed_artifact_list_mismatch", bundle_error_codes)
        self.assertIn("independent_review_bundle_validation_result_mismatch", bundle_error_codes)
        owner_seal = load_json(support / "owner_seal_record.json")
        bad_owner_seal = {**owner_seal, "sealed_artifact_hashes": [{"path": "missing/sealed.json", "sha256": "0" * 64}]}
        owner_errors: list[dict] = []
        validate_owner_seal_record(
            bad_owner_seal,
            outer_payload=complete,
            errors=owner_errors,
            required_sealed_bindings=[
                complete["independent_review_artifact_binding"],
                review_payload["hash_sealed_review_bundle_reference"],
            ],
            repo_root=REPO,
        )
        owner_error_codes = {error["code"] for error in owner_errors}
        self.assertIn("hash_binding_target_missing", owner_error_codes)
        self.assertIn("owner_seal_record_missing_required_sealed_artifact", owner_error_codes)

        forged = load_json(NEGATIVE_FIXTURES / "boolean_only_canonical_satisfied.json")
        forged_errors = validate_governance_payload(forged)
        self.assertIn(
            "independent_review_concrete_artifact_fields_missing",
            {error["code"] for error in forged_errors},
        )
        spoof = load_json(NEGATIVE_FIXTURES / "historical_path_spoof_current_payload.json")
        spoof_errors = validate_governance_payload(spoof)
        self.assertIn("bare_pass_forbidden_on_governance_axis", {error["code"] for error in spoof_errors})
        string_forged = load_json(NEGATIVE_FIXTURES / "string_path_canonical_satisfied.json")
        string_forged_errors = validate_governance_payload(string_forged, repo_root=REPO)
        self.assertIn("hash_binding_must_be_object", {error["code"] for error in string_forged_errors})
        schema_file = ROOT / "phase2/canonical_vocabulary_schema.json"
        schema_binding = {"path": repo_rel(schema_file), "sha256": sha256_file(schema_file)}
        same_file_errors = validate_governance_payload(
            forged_canonical_satisfied_payload(schema_binding),
            repo_root=REPO,
        )
        same_file_error_codes = {error["code"] for error in same_file_errors}
        self.assertIn("independent_review_artifact_schema_invalid", same_file_error_codes)
        self.assertIn("owner_seal_record_schema_invalid", same_file_error_codes)
        absolute_binding = {"path": str(schema_file.resolve()), "sha256": sha256_file(schema_file)}
        absolute_errors = validate_governance_payload(
            forged_canonical_satisfied_payload(absolute_binding),
            repo_root=REPO,
        )
        self.assertIn("hash_binding_path_must_be_repo_relative", {error["code"] for error in absolute_errors})
        historical_path = POSITIVE_FIXTURES / "historical_legacy_pass_trace.json"
        historical = load_json(historical_path)
        self.assertTrue(validate_governance_payload(historical))
        self.assertEqual(
            validate_governance_payload(
                historical,
                artifact_path=historical_path,
                historical_artifact_paths=[historical_path],
                repo_root=REPO,
            ),
            [],
        )

    def test_live_manifest_adoption_is_additive_and_axis_qualified(self) -> None:
        adoption = load_json(ROOT / "phase8/required_validation_manifest_adoption_report.json")
        coexistence = load_json(ROOT / "phase8/legacy_manifest_dual_field_coexistence_report.json")
        cleanup = load_json(ROOT / "phase8/legacy_projection_cleanup_debt_report.json")
        live = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")

        self.assertEqual(adoption["status"], "PASS")
        self.assertEqual(adoption["required_gate_adoption_status"], "adopted_required_gate")
        self.assertEqual(adoption["removed_existing_entries"], 0)
        self.assertTrue(adoption["modified_existing_entries_are_current_round_completion_updates"])
        self.assertEqual(adoption["duplicate_entries"], 0)
        self.assertTrue(adoption["governance_only"])
        self.assertFalse(adoption["source_rendered_lua_runtime_package_authority_mutated"])
        self.assertEqual(coexistence["status"], "PASS")
        self.assertFalse(coexistence["legacy_checks_retired"])
        self.assertTrue(coexistence["canonical_checks_added"])
        self.assertTrue(cleanup["legacy_projection_cleanup_requires_separate_owner_approved_plan"])

        required_tests = {row["test_id"] for row in live["required_tests"]}
        for test_id in [
            (
                "test_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split."
                "DvfCompletionVocabularyExternalGateVocabularySplitTest."
                "test_canonical_schema_and_negative_fixture_matrix"
            ),
            (
                "test_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split."
                "DvfCompletionVocabularyExternalGateVocabularySplitTest."
                "test_live_manifest_adoption_is_additive_and_axis_qualified"
            ),
            (
                "test_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split."
                "DvfCompletionVocabularyExternalGateVocabularySplitTest."
                "test_final_report_blocks_canonical_external_review_without_external_artifacts"
            ),
        ]:
            self.assertIn(test_id, required_tests)

    def test_final_report_blocks_canonical_external_review_without_external_artifacts(self) -> None:
        final = load_json(ROOT / "phase9/final_completion_vocabulary_external_gate_split_report.json")
        review = load_json(ROOT / "phase4/review_independence_validation_report.json")
        owner = load_json(ROOT / "phase5/owner_review_substitution_guard_report.json")
        protected = load_json(ROOT / "phase7/protected_surface_no_mutation_report.json")
        claim = load_json(ROOT / "phase9/claim_boundary_scan_report.json")

        self.assertEqual(final["status"], "PASS")
        self.assertEqual(final["machine_contract_validation"], "PASS")
        self.assertFalse(final["legacy_projection_consumed_for_current_gate"])
        self.assertEqual(review["canonical_external_review_state"], "blocked")
        self.assertTrue(owner["owner_approval_does_not_replace_review"])
        self.assertEqual(protected["changed_count"], 0)
        self.assertEqual(claim["overclaim_count"], 0)

        if INNER_CURRENT_ROUTE:
            return

        token = load_json(ROOT / "phase9/token_rename_author_signoff_report.json")
        review_artifact = load_json(ROOT / "phase9/current_session_independent_review_artifact.json")
        owner_seal = load_json(ROOT / "phase9/current_session_owner_seal_record.json")

        self.assertEqual(final["external_validation_bundle_result"], "PASS")
        self.assertEqual(final["external_validation_bundle_state"], "present")
        self.assertEqual(final["independent_review_verdict"], "PASS")
        self.assertEqual(final["independent_review_state"], "present")
        self.assertEqual(final["owner_decision"], "approved")
        self.assertEqual(final["owner_seal_state"], "sealed")
        self.assertEqual(final["external_gate_state"], "satisfied")
        self.assertEqual(final["canonical_external_review_state"], "satisfied")
        self.assertTrue(final["canonical_seal_allowed"])
        self.assertEqual(final["closeout_state"], "canonical_complete_governance_only")
        self.assertTrue(final["canonical_complete_ledger_update_allowed"])
        self.assertEqual(final["token_rename_author_signoff_state"], "signed")
        self.assertEqual(token["token_rename_author_signoff_state"], "signed")
        self.assertFalse(token["canonical_closeout_blocked_without_signoff"])
        self.assertEqual(review_artifact["review_verdict"], "PASS")
        self.assertEqual(owner_seal["owner_seal_state"], "sealed")

        result = subprocess.run(
            [sys.executable, "-B", str(VALIDATOR), "--require-complete"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(ROOT / "phase9/validation_report.require_complete.json")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["error_count"], 0)


if __name__ == "__main__":
    unittest.main()
