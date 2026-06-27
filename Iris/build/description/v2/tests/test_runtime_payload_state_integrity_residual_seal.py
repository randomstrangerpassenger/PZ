from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
SCRIPT = REPO / "Iris/build/description/v2/tools/build/runtime_payload_state_integrity_residual_seal.py"
ROOT = REPO / "Iris/build/description/v2/staging/runtime_payload_state_integrity_residual_seal"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class RuntimePayloadStateIntegrityResidualSealTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--mode", "all", "--require-complete"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "runtime payload residual seal validation failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_final_report_allows_residual_seal_after_author_and_external_review(self) -> None:
        final = load_json(ROOT / "phase7/final_runtime_payload_residual_seal_report.json")
        adoption = load_json(ROOT / "phase8/current_route_governance_adoption_report.json")
        claim_boundary = (REPO / "docs/runtime_payload_state_integrity_residual_claim_boundary.md").read_text(encoding="utf-8")
        ledger = (REPO / "docs/runtime_payload_state_integrity_residual_ledger_packet.md").read_text(encoding="utf-8")

        self.assertEqual(final["status"], "PASS")
        self.assertEqual(final["machine_contract_status"], "PASS")
        self.assertTrue(final["canonical_residual_seal_allowed"])
        self.assertFalse(final["pending_author_selection"])
        self.assertFalse(final["blocked_external_gate"])
        self.assertTrue(final["author_seal_closing_decision_complete"])
        self.assertTrue(final["external_review_complete"])
        self.assertEqual(final["payload_shape_guard_status"], "PASS")
        self.assertEqual(final["guard_predicate_freeze_status"], "PASS")
        self.assertEqual(final["predecessor_residue_disposition"], "historical_only")
        self.assertEqual(final["residue_in_current_denominator_count"], 0)
        self.assertEqual(final["runtime_mutation_changed_count"], 0)
        self.assertIn("no_release_readiness", final["non_claims"])
        self.assertEqual(adoption["governance_adoption_status"], "not_required_traceable")
        self.assertFalse(adoption["live_manifest_mutated"])
        self.assertIn("complete_residual_seal_governance_only", claim_boundary)
        self.assertIn("complete_residual_seal_governance_only", ledger)
        self.assertIn("current runtime rows: 2105", ledger)

    def test_reverification_and_residue_confinement_match_existing_guard(self) -> None:
        guard = load_json(ROOT / "phase2/shape_guard_readpoint_reverification_report.json")
        forbidden = load_json(ROOT / "phase2/current_looking_forbidden_scan_report.json")
        disjoint = load_json(ROOT / "phase2/denominator_disjointness_report.json")
        residue = load_json(ROOT / "phase3/residual_historical_only_confinement_report.json")
        non_reentry = load_json(ROOT / "phase3/predecessor_residue_non_reentry_report.json")

        self.assertEqual(guard["status"], "PASS")
        self.assertEqual(guard["current_runtime_entry_count"], 2105)
        self.assertEqual(guard["current_runtime_unadopted_count"], 21)
        self.assertEqual(guard["current_like_publish_state_row_count"], 0)
        self.assertEqual(guard["current_like_forbidden_count"], 0)
        self.assertEqual(guard["current_like_unclassified_count"], 0)
        self.assertEqual(guard["predecessor_residue_count"], 2)
        self.assertEqual(guard["display_body_present_count"], 0)

        self.assertEqual(forbidden["status"], "PASS")
        self.assertEqual(forbidden["current_like_forbidden_count"], 0)
        self.assertEqual(forbidden["current_like_unclassified_count"], 0)
        self.assertEqual(disjoint["status"], "PASS")
        self.assertEqual(disjoint["residue_in_current_denominator_count"], 0)
        self.assertEqual(residue["status"], "PASS")
        self.assertTrue(residue["historical_only"])
        self.assertFalse(residue["cleanup_target"])
        self.assertEqual(non_reentry["status"], "PASS")
        self.assertTrue(non_reentry["current_like_denominator_intersection_empty"])

    def test_protected_manifest_and_hash_coverage_are_complete(self) -> None:
        protected = load_json(ROOT / "phase1/protected_surface_manifest.json")
        no_mutation = load_json(ROOT / "phase5/no_mutation_report.json")
        artifact_hash = load_json(ROOT / "phase5/artifact_hash_report.json")
        entries = protected["entries"]

        self.assertGreater(len(entries), 20)
        self.assertEqual(no_mutation["status"], "PASS")
        self.assertEqual(no_mutation["changed_count"], 0)
        self.assertEqual(no_mutation["source_rendered_bridge_runtime_package_changed_count"], 0)
        self.assertFalse(no_mutation["phase8_manifest_adoption_carveout_used"])
        self.assertFalse(any(entry["expected_mutation_allowed"] for entry in entries))
        self.assertTrue(all("pre_hash" in entry and "post_hash" in entry for entry in entries))
        self.assertTrue(
            all(
                entry.get("package_peer_source")
                for entry in entries
                if entry["path_source_kind"] == "package_peer_runtime_payload"
            )
        )

        self.assertEqual(artifact_hash["status"], "PASS")
        self.assertTrue(artifact_hash["guard_tool_hash_covered"])
        self.assertTrue(artifact_hash["guard_test_hash_covered"])
        self.assertTrue(artifact_hash["residual_tool_hash_covered"])
        self.assertTrue(artifact_hash["residual_test_hash_covered"])

    def test_author_and_external_review_gates_are_complete(self) -> None:
        options = load_json(ROOT / "phase4/author_reserved_selection_option_enumeration.json")
        decision = load_json(ROOT / "phase4/author_reserved_selection_decision_record.json")
        policy = load_json(ROOT / "phase4/policy_consistency_report.json")
        review = load_json(ROOT / "phase6/external_independent_review_report.json")
        review_gate = load_json(ROOT / "phase6/external_review_gate_report.json")
        author_doc = (REPO / "docs/runtime_payload_state_integrity_author_decision.md").read_text(encoding="utf-8")

        self.assertEqual(options["status"], "PASS")
        self.assertTrue(options["enumerable_option_space_present"])
        self.assertGreaterEqual(options["option_count"], 3)
        self.assertFalse(decision["decision_record_generated_by_executor"])
        self.assertTrue(decision["decision_value_not_generated_by_executor"])
        self.assertTrue(decision["decision_value_not_inferred_by_validator"])
        self.assertFalse(decision["pending_author_selection"])
        self.assertEqual(decision["selected_option_id"], "explicit_no_branch_mutation_required")
        self.assertTrue(decision["selected_option_is_seal_closing"])
        self.assertEqual(policy["status"], "PASS")
        self.assertTrue(policy["author_policy_confirmation_present"])
        self.assertTrue(policy["selected_option_metadata_consistent_with_decision"])
        self.assertEqual(review["status"], "PASS")
        self.assertTrue(review["canonical_residual_seal_allowed"])
        self.assertEqual(review["comparison_exempt_count"], 0)
        self.assertEqual(review_gate["status"], "PASS")
        self.assertEqual(review_gate["external_independent_review_status"], "PASS")
        self.assertFalse(review_gate["blocked_external_gate"])
        self.assertIn("seal_closing_author_decision_recorded", author_doc)

    def test_require_complete_rejects_missing_author_and_review_gates(self) -> None:
        author_path = ROOT / "phase4/author_reserved_selection_decision_record.json"
        review_path = ROOT / "phase6/external_independent_review_report.json"
        author_backup = author_path.read_text(encoding="utf-8")
        review_backup = review_path.read_text(encoding="utf-8")
        try:
            author_path.unlink()
            review_path.unlink()
            generate_missing_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "all"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(generate_missing_result.returncode, 0, generate_missing_result.stdout + generate_missing_result.stderr)

            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "validate", "--require-complete"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            report = load_json(ROOT / "phase7/validation_report.require_complete.json")
            error_codes = {error["code"] for error in report["errors"]}
            self.assertIn("canonical_residual_seal_not_allowed", error_codes)
            self.assertIn("author_seal_closing_decision_missing", error_codes)
            self.assertIn("external_independent_review_not_pass", error_codes)
        finally:
            author_path.write_text(author_backup, encoding="utf-8")
            review_path.write_text(review_backup, encoding="utf-8")
            restore_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "all", "--require-complete"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(restore_result.returncode, 0, restore_result.stdout + restore_result.stderr)

    def test_non_seal_closing_option_metadata_cannot_complete(self) -> None:
        author_path = ROOT / "phase4/author_reserved_selection_decision_record.json"
        author_backup = author_path.read_text(encoding="utf-8") if author_path.exists() else None
        try:
            author_decision = {
                "schema_version": "runtime-payload-residual-author-decision-record-v1",
                "status": "PASS",
                "decision_owner": "owner-fixture",
                "decision_owner_role": "project_author",
                "selected_option_id": "branch_b_contract_redefinition",
                "selected_option_is_seal_closing": True,
                "decision_source": "test_invalid_option_metadata_fixture",
                "decision_timestamp": "2026-06-27T00:00:00+00:00",
                "decision_readpoint": "test_invalid_option_metadata_fixture",
                "decision_record_generated_by_executor": False,
                "decision_value_not_generated_by_executor": True,
                "decision_value_not_inferred_by_validator": True,
                "pending_author_selection": False,
                "policy_confirmations": {
                    "current_compatible_unadopted_text_ko_forbidden": True,
                    "current_compatible_unadopted_publish_state_forbidden": True,
                    "unadopted_display_body_missing_or_explicit_nil": True,
                    "predecessor_residue_historical_only": True,
                },
            }
            write_json(author_path, author_decision)

            generate_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "generate"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(generate_result.returncode, 0, generate_result.stdout + generate_result.stderr)

            policy = load_json(ROOT / "phase4/policy_consistency_report.json")
            final = load_json(ROOT / "phase7/final_runtime_payload_residual_seal_report.json")
            self.assertEqual(policy["status"], "BLOCKED_PENDING_AUTHOR_SELECTION")
            self.assertTrue(policy["selected_option_in_enumerated_option_space"])
            self.assertFalse(policy["selected_option_metadata_seal_closing_if_author_selected"])
            self.assertFalse(policy["selected_option_metadata_consistent_with_decision"])
            self.assertFalse(final["author_seal_closing_decision_complete"])
            self.assertFalse(final["canonical_residual_seal_allowed"])

            validate_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "validate"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(validate_result.returncode, 0, validate_result.stdout + validate_result.stderr)
            report = load_json(ROOT / "phase7/validation_report.json")
            self.assertIn("author_gate_invalid", {error["code"] for error in report["errors"]})
        finally:
            if author_backup is None:
                if author_path.exists():
                    author_path.unlink()
            else:
                author_path.write_text(author_backup, encoding="utf-8")
            restore_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "all"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(restore_result.returncode, 0, restore_result.stdout + restore_result.stderr)

    def test_validate_rehashes_current_primary_review_artifacts(self) -> None:
        author_doc = REPO / "docs/runtime_payload_state_integrity_author_decision.md"
        original = author_doc.read_text(encoding="utf-8")
        try:
            author_doc.write_text(original + "\nvalidate drift fixture\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "validate"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            report = load_json(ROOT / "phase7/validation_report.json")
            self.assertIn("primary_review_artifact_hash_drift", {error["code"] for error in report["errors"]})
        finally:
            author_doc.write_text(original, encoding="utf-8")
            restore_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "all"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(restore_result.returncode, 0, restore_result.stdout + restore_result.stderr)

    def test_invalid_external_review_is_preserved_as_rejected(self) -> None:
        review_path = ROOT / "phase6/external_independent_review_report.json"
        review_backup = review_path.read_text(encoding="utf-8") if review_path.exists() else None
        try:
            artifact_hash = load_json(ROOT / "phase5/artifact_hash_report.json")
            invalid_review = {
                "schema_version": "runtime-payload-residual-external-independent-review-report-v1",
                "status": "PASS",
                "reviewer_identity": "self-reviewer-fixture",
                "reviewer_kind": "executor_chain_fixture",
                "review_independence_basis": "negative fixture intentionally remains in the executor authorship chain",
                "not_self_review": False,
                "not_same_authorship_chain": False,
                "same_authorship_chain_basis": "same authorship chain negative fixture",
                "reviewed_artifact_manifest_hash": artifact_hash["primary_review_artifact_manifest_hash"],
                "primary_review_artifact_count": artifact_hash["artifact_count"],
                "missing_count": 0,
                "hash_mismatch_count": 0,
                "comparison_exempt_count": 0,
                "comparison_exemptions": [],
                "review_verdict": "PASS",
                "canonical_residual_seal_allowed": True,
            }
            write_json(review_path, invalid_review)

            generate_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "all"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(generate_result.returncode, 0, generate_result.stdout + generate_result.stderr)

            preserved_review = load_json(review_path)
            gate = load_json(ROOT / "phase6/external_review_gate_report.json")
            independent_hash = load_json(ROOT / "phase6/independent_review_artifact_hash_report.json")
            final = load_json(ROOT / "phase7/final_runtime_payload_residual_seal_report.json")
            self.assertEqual(preserved_review["reviewer_identity"], "self-reviewer-fixture")
            self.assertFalse(preserved_review["not_self_review"])
            self.assertEqual(gate["status"], "BLOCKED_EXTERNAL_REVIEW")
            self.assertEqual(gate["external_independent_review_status"], "REJECTED")
            self.assertTrue(gate["external_review_rejected"])
            self.assertFalse(gate["external_review_missing"])
            self.assertEqual(gate["review_report_source"], "external_supplied_existing_record")
            self.assertEqual(gate["blocked_reason"], "external_independent_review_rejected")
            self.assertEqual(independent_hash["external_review_admissibility_state"], "REJECTED")
            self.assertTrue(independent_hash["external_review_rejected"])
            self.assertFalse(final["canonical_residual_seal_allowed"])

            validate_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "validate"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(validate_result.returncode, 0, validate_result.stdout + validate_result.stderr)
        finally:
            if review_backup is None:
                if review_path.exists():
                    review_path.unlink()
            else:
                review_path.write_text(review_backup, encoding="utf-8")
            restore_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "all"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(restore_result.returncode, 0, restore_result.stdout + restore_result.stderr)

    def test_validate_rejects_stale_external_review_classification_fields(self) -> None:
        gate_path = ROOT / "phase6/external_review_gate_report.json"
        independent_path = ROOT / "phase6/independent_review_artifact_hash_report.json"
        gate_backup = gate_path.read_text(encoding="utf-8")
        independent_backup = independent_path.read_text(encoding="utf-8")
        try:
            gate = load_json(gate_path)
            independent_hash = load_json(independent_path)
            gate["external_review_missing"] = False
            gate["external_review_rejected"] = True
            gate["blocked_reason"] = "stale_negative_fixture_reason"
            independent_hash["external_review_admissibility_state"] = "REJECTED"
            independent_hash["external_review_rejected"] = True
            independent_hash["external_review_missing"] = False
            write_json(gate_path, gate)
            write_json(independent_path, independent_hash)

            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "validate"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            report = load_json(ROOT / "phase7/validation_report.json")
            error_codes = {error["code"] for error in report["errors"]}
            self.assertIn("external_review_gate_classification_mismatch", error_codes)
            self.assertIn("independent_review_classification_mismatch", error_codes)
        finally:
            gate_path.write_text(gate_backup, encoding="utf-8")
            independent_path.write_text(independent_backup, encoding="utf-8")
            restore_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "all"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(restore_result.returncode, 0, restore_result.stdout + restore_result.stderr)

    def test_supplied_author_and_external_review_can_complete(self) -> None:
        author_path = ROOT / "phase4/author_reserved_selection_decision_record.json"
        review_path = ROOT / "phase6/external_independent_review_report.json"
        author_backup = author_path.read_text(encoding="utf-8") if author_path.exists() else None
        review_backup = review_path.read_text(encoding="utf-8") if review_path.exists() else None
        try:
            author_decision = {
                "schema_version": "runtime-payload-residual-author-decision-record-v1",
                "status": "PASS",
                "decision_owner": "owner-fixture",
                "decision_owner_role": "project_author",
                "selected_option_id": "explicit_no_branch_mutation_required",
                "selected_option_is_seal_closing": True,
                "decision_source": "test_supplied_author_decision_fixture",
                "decision_timestamp": "2026-06-27T00:00:00+00:00",
                "decision_readpoint": "test_complete_path_fixture",
                "decision_record_generated_by_executor": False,
                "decision_value_not_generated_by_executor": True,
                "decision_value_not_inferred_by_validator": True,
                "pending_author_selection": False,
                "policy_confirmations": {
                    "current_compatible_unadopted_text_ko_forbidden": True,
                    "current_compatible_unadopted_publish_state_forbidden": True,
                    "unadopted_display_body_missing_or_explicit_nil": True,
                    "predecessor_residue_historical_only": True,
                },
            }
            write_json(author_path, author_decision)

            generate_author_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "generate"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(generate_author_result.returncode, 0, generate_author_result.stdout + generate_author_result.stderr)

            artifact_hash = load_json(ROOT / "phase5/artifact_hash_report.json")
            external_review = {
                "schema_version": "runtime-payload-residual-external-independent-review-report-v1",
                "status": "PASS",
                "reviewer_identity": "external-reviewer-fixture",
                "reviewer_kind": "independent_fixture",
                "review_independence_basis": "test fixture outside executor decision path",
                "not_self_review": True,
                "not_same_authorship_chain": True,
                "same_authorship_chain_basis": "fixture asserts independent chain for validator path coverage",
                "reviewed_artifact_manifest_hash": artifact_hash["primary_review_artifact_manifest_hash"],
                "primary_review_artifact_count": artifact_hash["artifact_count"],
                "missing_count": 0,
                "hash_mismatch_count": 0,
                "comparison_exempt_count": 0,
                "comparison_exemptions": [],
                "review_verdict": "PASS",
                "canonical_residual_seal_allowed": True,
            }
            write_json(review_path, external_review)

            complete_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "all", "--require-complete"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(complete_result.returncode, 0, complete_result.stdout + complete_result.stderr)
            final = load_json(ROOT / "phase7/final_runtime_payload_residual_seal_report.json")
            self.assertEqual(final["status"], "PASS")
            self.assertTrue(final["canonical_residual_seal_allowed"])
            author_doc_path = REPO / "docs/runtime_payload_state_integrity_author_decision.md"
            author_doc = author_doc_path.read_text(encoding="utf-8")
            claim_doc = (REPO / "docs/runtime_payload_state_integrity_residual_claim_boundary.md").read_text(encoding="utf-8")
            ledger_doc = (REPO / "docs/runtime_payload_state_integrity_residual_ledger_packet.md").read_text(encoding="utf-8")
            self.assertIn("seal_closing_author_decision_recorded", author_doc)
            self.assertIn("complete_residual_seal_governance_only", claim_doc)
            self.assertIn("complete_residual_seal_governance_only", ledger_doc)

            try:
                author_doc_path.write_text(author_doc + "\ncomplete path artifact drift fixture\n", encoding="utf-8")
                drift_result = subprocess.run(
                    [sys.executable, "-B", str(SCRIPT), "--mode", "validate"],
                    cwd=REPO,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertNotEqual(drift_result.returncode, 0, drift_result.stdout + drift_result.stderr)
                drift_report = load_json(ROOT / "phase7/validation_report.json")
                gate_errors = [
                    error
                    for error in drift_report["errors"]
                    if error["code"] == "external_review_gate_classification_mismatch"
                ]
                self.assertTrue(gate_errors, drift_report)
                self.assertEqual(
                    gate_errors[0]["payload"]["expected"]["blocked_reason"],
                    "independent_review_artifact_hash_mismatch",
                )
            finally:
                author_doc_path.write_text(author_doc, encoding="utf-8")
        finally:
            if author_backup is None:
                if author_path.exists():
                    author_path.unlink()
            else:
                author_path.write_text(author_backup, encoding="utf-8")
            if review_backup is None:
                if review_path.exists():
                    review_path.unlink()
            else:
                review_path.write_text(review_backup, encoding="utf-8")
            restore_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "all", "--require-complete"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(restore_result.returncode, 0, restore_result.stdout + restore_result.stderr)
            restored_final = load_json(ROOT / "phase7/final_runtime_payload_residual_seal_report.json")
            restored_require_complete = load_json(ROOT / "phase7/validation_report.require_complete.json")
            self.assertEqual(restored_final["status"], "PASS")
            self.assertTrue(restored_final["canonical_residual_seal_allowed"])
            self.assertEqual(restored_require_complete["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
