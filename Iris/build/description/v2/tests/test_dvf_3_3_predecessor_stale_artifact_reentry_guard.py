from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_predecessor_stale_artifact_reentry_guard"
RUNNER = TOOLS / "run_dvf_3_3_predecessor_stale_artifact_reentry_guard.py"
VALIDATOR = TOOLS / "validate_dvf_3_3_predecessor_stale_artifact_reentry_guard.py"
INNER_CURRENT_ROUTE = os.environ.get("DVF_PREDECESSOR_STALE_INNER_CURRENT_ROUTE") == "1"

sys.path.insert(0, str(TOOLS))

from dvf_3_3_predecessor_stale_artifact_reentry_guard_common import (  # noqa: E402
    DISPOSITIONS,
    ROUND_REQUIRED_ARTIFACTS,
    ROUND_REQUIRED_TESTS,
    classify_claim_text,
    negative_fixture_rows,
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class DvfPredecessorStaleArtifactReentryGuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        final = ROOT / "phase6/final_predecessor_stale_artifact_reentry_guard_report.json"
        if final.exists():
            payload = load_json(final)
            if payload.get("machine_contract_status") == "PASS":
                return
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--mode", "generate"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "predecessor/stale artifact guard generation failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_preflight_denominator_and_taxonomy_pass(self) -> None:
        preflight = load_json(ROOT / "phase0/go_no_go_preflight_report.json")
        denominator = load_json(ROOT / "phase1/artifact_universe_denominator_lock.json")
        coverage = load_json(ROOT / "phase1/artifact_disposition_coverage_report.json")
        taxonomy = load_json(ROOT / "phase1/artifact_disposition_taxonomy.json")
        samples = load_json(ROOT / "phase1/docs_claim_scan_sample_adjudication_report.json")

        self.assertEqual(preflight["go_no_go_decision"], "GO")
        self.assertEqual(denominator["status"], "PASS")
        self.assertEqual(denominator["denominator_axis"], "predecessor_stale_artifact_universe")
        self.assertFalse(denominator["consumer_universe_denominator_id_reused"])
        self.assertFalse(denominator["consumer_universe_membership_reused"])
        self.assertFalse(denominator["consumer_universe_count_reused"])
        self.assertEqual(coverage["status"], "PASS")
        self.assertEqual(coverage["coverage_percent"], 100)
        self.assertEqual(coverage["unknown_blocked_count"], 0)
        self.assertEqual(coverage["bare_review_input_only_disposition_count"], 0)
        self.assertEqual(taxonomy["enum"], DISPOSITIONS)
        self.assertIn("review_input_only_non_authority", taxonomy["enum"])
        self.assertNotIn("review_input_only", taxonomy["enum"])
        self.assertEqual(samples["status"], "PASS")
        self.assertGreaterEqual(samples["sample_fixture_count"], 24)
        self.assertEqual(samples["false_positive_count"], 0)
        self.assertEqual(samples["false_negative_count"], 0)

    def test_negative_fixture_matrix_fails_closed(self) -> None:
        phase3 = load_json(ROOT / "phase3/adversarial_negative_fixture_contract.json")
        phase5 = load_json(ROOT / "phase5/negative_fixture_matrix_report.json")

        self.assertEqual(phase3["status"], "PASS")
        self.assertEqual(phase5["status"], "PASS")
        self.assertTrue(all(row["status"] == "PASS" for row in negative_fixture_rows()))
        fixture_ids = {row["fixture_id"] for row in phase5["fixtures"]}
        for fixture_id in {
            "renamed_legacy_bridge_payload",
            "stale_bridge_current_path",
            "old_bridge_package_path",
            "monolith_export",
            "nonstandard_monolith_filename",
            "rollback_snapshot_package_inclusion",
            "relocated_predecessor_fixture",
            "predecessor_fixture_required_manifest",
            "payload_marker_conflict",
            "role_metadata_conflict",
        }:
            self.assertIn(fixture_id, fixture_ids)

    def test_package_manifest_and_export_guards_pass(self) -> None:
        package_scan = load_json(ROOT / "phase3/package_forbidden_artifact_scan_report.json")
        package_route = load_json(ROOT / "phase5/package_route_validation_result.json")
        package_probe = load_json(ROOT / "phase5/package_probe_equivalence_report.json")
        predicates = load_json(ROOT / "phase5/package_predicate_extraction_report.json")
        export = load_json(ROOT / "phase3/export_route_guard_report.json")

        self.assertEqual(package_scan["status"], "PASS")
        self.assertEqual(package_scan["package_forbidden_hit_count"], 0)
        self.assertEqual(package_scan["package_zip_forbidden_hit_count"], 0)
        self.assertEqual(package_route["status"], "PASS")
        self.assertEqual(package_route["package_forbidden_hit_count"], 0)
        self.assertEqual(package_route["package_zip_forbidden_hit_count"], 0)
        self.assertEqual(package_probe["status"], "PASS")
        self.assertTrue(package_probe["output_root_isolated"])
        self.assertTrue(package_probe["same_forbidden_predicates_as_package_iris"])
        self.assertFalse(package_probe["live_package_payload_mutated"])
        self.assertEqual(package_probe["probe_vs_real_route_drift_count"], 0)
        self.assertEqual(predicates["status"], "PASS")
        self.assertEqual(predicates["extraction_coverage"], "complete")
        self.assertEqual(export["status"], "PASS")
        self.assertTrue(export["default_export_route_generates_chunk_authority"])
        self.assertFalse(export["default_export_route_generates_current_staging_monolith"])

    def test_required_manifest_claim_scan_and_adoption_are_governance_only(self) -> None:
        required = load_json(ROOT / "phase4/required_manifest_reentry_report.json")
        raw = load_json(ROOT / "phase4/raw_predecessor_direct_read_report.json")
        dual = load_json(ROOT / "phase4/no_dual_authority_read_report.json")
        claim = load_json(ROOT / "phase4/claim_surface_scan_report.json")
        adoption = load_json(ROOT / "phase4/manifest_adoption_report.json")
        live_manifest = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")

        self.assertEqual(required["status"], "PASS")
        self.assertEqual(required["required_manifest_predecessor_reentry_count"], 0)
        self.assertEqual(raw["raw_predecessor_direct_authority_read_count"], 0)
        self.assertEqual(dual["dual_authority_read_count"], 0)
        self.assertEqual(claim["docs_claim_violation_count"], 0)
        self.assertEqual(adoption["status"], "PASS")
        self.assertEqual(adoption["required_gate_adoption_status"], "adopted_required_gate")
        self.assertEqual(adoption["removed_existing_entries"], 0)
        self.assertEqual(adoption["modified_existing_entries"], 0)
        self.assertEqual(adoption["duplicate_entries"], 0)
        self.assertFalse(adoption["source_rendered_lua_runtime_package_authority_mutated"])

        required_paths = {row["path"] for row in live_manifest["required_artifacts"]}
        required_tests = {row["test_id"] for row in live_manifest["required_tests"]}
        for row in ROUND_REQUIRED_ARTIFACTS:
            self.assertIn(row["path"], required_paths)
        for test_id in ROUND_REQUIRED_TESTS:
            self.assertIn(test_id, required_tests)

        self.assertEqual(classify_claim_text("The stale bridge is current authority."), "blocked")
        self.assertEqual(classify_claim_text("Stale bridge cannot become current authority."), "allowed")
        self.assertEqual(classify_claim_text("레거시 bridge는 현재 권위가 아니다."), "allowed")

    def test_final_report_preserves_non_claims_and_review_boundary(self) -> None:
        final = load_json(ROOT / "phase6/final_predecessor_stale_artifact_reentry_guard_report.json")
        consistency = load_json(ROOT / "phase6/final_go_no_go_phase_consistency_report.json")
        review = load_json(ROOT / "phase6/independent_review_input.json")
        linkage = load_json(ROOT / "phase6/stale_bridge_ir_linkage_report.json")

        self.assertEqual(final["machine_contract_status"], "PASS")
        self.assertTrue(final["governance_guard_only"])
        self.assertEqual(final["preflight_go_no_go_decision"], "GO")
        self.assertEqual(final["go_no_go_phase_consistency_status"], "PASS")
        self.assertEqual(final["go_no_go_phase_drift_count"], 0)
        self.assertFalse(final["source_authority_mutated"])
        self.assertFalse(final["runtime_authority_mutated"])
        self.assertFalse(final["package_authority_mutated"])
        self.assertFalse(final["release_readiness_claimed"])
        self.assertFalse(final["canonical_seal_claimed"])
        self.assertEqual(final["independent_review_status"], "pending_or_external")
        self.assertEqual(final["review_input_disposition_name"], "review_input_only_non_authority")
        self.assertEqual(final["bare_review_input_only_disposition_count"], 0)
        self.assertFalse(final["manual_override_used"])
        self.assertEqual(final["owner_approved_disposition_override_count"], 0)
        self.assertIn("no_release_readiness", final["non_claims"])
        self.assertEqual(consistency["status"], "PASS")
        self.assertEqual(consistency["go_no_go_phase_drift_count"], 0)
        self.assertEqual(review["status"], "PASS")
        self.assertEqual(review["review_state"], "pending")
        self.assertTrue(review["machine_pass_does_not_satisfy_independent_review"])
        self.assertEqual(linkage["prior_stale_bridge_review_pending_disposition"], "separate_carry")
        self.assertFalse(linkage["closed_by_this_round"])

        if INNER_CURRENT_ROUTE:
            return
        result = subprocess.run(
            [sys.executable, "-B", str(VALIDATOR), "--require-complete"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
