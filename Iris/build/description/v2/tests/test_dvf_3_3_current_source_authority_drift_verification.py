from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement"
RUNNER = TOOLS / "run_dvf_3_3_current_source_authority_drift_verification.py"
VALIDATOR = TOOLS / "validate_dvf_3_3_current_source_authority_drift_verification.py"
EXPECTED_REVIEW_ARTIFACTS = 49
EXPECTED_POST_MANIFEST_HASH_OBSERVATION_ARTIFACTS = {
    "phase6/primary_review_artifact_manifest.json",
    "phase6/validation_report.all.json",
    "phase6/validation_report.require_complete.json",
}
EXPECTED_SELF_HASH_PRESENCE_ONLY_ARTIFACTS = {
    "phase6/independent_review_artifact_hash_report.json",
}
EXPECTED_COMPARISON_EXEMPT_ARTIFACTS = EXPECTED_POST_MANIFEST_HASH_OBSERVATION_ARTIFACTS | EXPECTED_SELF_HASH_PRESENCE_ONLY_ARTIFACTS


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class DvfCurrentSourceAuthorityDriftVerificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--mode", "all"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "current source authority drift runner failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_source_chain_is_successor_2105_identity(self) -> None:
        report = load_json(ROOT / "phase1/source_chain_identity_report.json")
        matrix = load_json(ROOT / "phase1/source_hash_count_matrix.json")

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["authority_role"], "successor_current_source_authority")
        self.assertEqual(report["successor_universe_count"], 2105)
        self.assertTrue(report["successor_count_not_predecessor_recovery_target"])
        self.assertEqual(matrix["facts"]["actual_count"], 2105)
        self.assertEqual(matrix["decisions"]["actual_count"], 2105)
        self.assertEqual(matrix["overlay_support"]["actual_count"], 2105)
        self.assertTrue(matrix["checks"]["facts_match_manifest"])
        self.assertTrue(matrix["checks"]["decisions_match_manifest"])
        self.assertTrue(matrix["checks"]["overlay_match_manifest"])

    def test_direct_compose_uses_sandbox_current_equivalent_outputs(self) -> None:
        preflight = load_json(ROOT / "phase2/direct_compose_writer_sink_preflight_report.json")
        result = load_json(ROOT / "phase2/direct_current_compose_result.json")

        self.assertEqual(preflight["status"], "PASS")
        self.assertEqual(
            preflight["sandbox_output_root"],
            "Iris/build/description/v2/.tmp_tests/dvf_3_3_current_source_authority_drift_verification/direct_compose",
        )
        self.assertTrue(preflight["live_rendered_output_paths_blocked"])
        self.assertEqual(set(preflight["write_path_classifications"].values()), {"current-equivalent-fixture"})
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["entry_count"], 2105)
        self.assertTrue(result["checks"]["source_key_parity"])
        self.assertTrue(result["checks"]["entries_sha256_matches_live"])

    def test_overlay_regression_and_base_canopener_are_bounded(self) -> None:
        overlay = load_json(ROOT / "phase2/body_source_overlay_requirement_report.json")
        canopener = load_json(ROOT / "phase2/base_canopener_applicability_report.json")
        blocker = load_json(ROOT / "phase2/known_overlay_blocker_regression_report.json")

        self.assertEqual(overlay["status"], "PASS")
        self.assertEqual(overlay["adopted_row_count"], 2084)
        self.assertEqual(overlay["runtime_adopted_missing_overlay_count"], 0)
        self.assertEqual(canopener["status"], "PASS")
        self.assertEqual(canopener["classification"], "not_applicable_absent_from_selected_target")
        self.assertFalse(canopener["in_selected_successor_source"])
        self.assertEqual(blocker["known_missing_overlay_blocker_count"], 0)

    def test_content_derived_fixture_signature_does_not_reenter_current_paths(self) -> None:
        signature = load_json(ROOT / "phase4/content_derived_six_entry_signature.json")
        scan = load_json(ROOT / "phase4/current_looking_fixture_payload_scan.json")
        reentry = load_json(ROOT / "phase4/predecessor_reentry_guard_report.json")

        self.assertEqual(signature["status"], "PASS")
        self.assertEqual(signature["member_count"], 6)
        self.assertIn("Base.CanOpener", signature["members"])
        self.assertEqual(scan["status"], "PASS")
        self.assertEqual(scan["current_looking_six_entry_payload_count"], 0)
        self.assertEqual(reentry["status"], "PASS")
        self.assertEqual(reentry["predecessor_reentry_violation_count"], 0)

    def test_recovery_retirement_is_canonical_pass_after_review_and_owner_seal(self) -> None:
        retirement = load_json(ROOT / "phase5/recovery_scope_retirement_report.json")
        final = load_json(ROOT / "phase6/final_current_source_authority_drift_verification_report.json")
        review = load_json(ROOT / "phase6/independent_review_artifact_hash_report.json")

        self.assertEqual(retirement["status"], "PASS")
        self.assertEqual(retirement["prior_recovery_scope_status"], "future_drift_contingency")
        self.assertEqual(retirement["live_write_execution_authority_remaining_count"], 0)
        self.assertEqual(final["status"], "PASS")
        self.assertEqual(final["machine_contract_status"], "PASS")
        self.assertEqual(final["canonical_retirement_seal_status"], "PASS")
        self.assertTrue(final["canonical_retirement_seal_allowed"])
        self.assertEqual(final["independent_review_status"], "PASS")
        self.assertEqual(final["owner_seal_status"], "PASS")
        self.assertEqual(review["status"], "PASS")
        self.assertEqual(review["primary_review_artifact_missing_count"], 0)
        self.assertEqual(review["mismatch_count"], 0)
        self.assertEqual(review["independent_review_status"], "PASS")
        self.assertEqual(review["owner_seal_status"], "PASS")

    def test_primary_review_inventory_and_hash_report_cover_complete_packet(self) -> None:
        manifest = load_json(ROOT / "phase6/primary_review_artifact_manifest.json")
        review = load_json(ROOT / "phase6/independent_review_artifact_hash_report.json")
        paths = {row["root_relative_path"] for row in manifest["artifacts"]}
        review_paths = {row["root_relative_path"] for row in review["artifact_hashes"]}

        self.assertEqual(manifest["manifest_scope"], "complete_evidence_inventory")
        self.assertEqual(manifest["artifact_count"], EXPECTED_REVIEW_ARTIFACTS)
        self.assertEqual(manifest["inventory_file_count"], EXPECTED_REVIEW_ARTIFACTS)
        self.assertEqual(manifest["missing_count"], 0)
        self.assertTrue(EXPECTED_COMPARISON_EXEMPT_ARTIFACTS.issubset(paths))
        self.assertIn("phase5/current_route_required_validation_candidate.json", paths)
        self.assertEqual(paths, review_paths)
        self.assertEqual(review["primary_review_artifact_manifest_artifact_count"], EXPECTED_REVIEW_ARTIFACTS)
        self.assertEqual(review["primary_review_artifact_missing_count"], 0)
        self.assertEqual(review["mismatch_count"], 0)
        self.assertEqual(review["comparison_checked_count"], EXPECTED_REVIEW_ARTIFACTS - len(EXPECTED_COMPARISON_EXEMPT_ARTIFACTS))
        self.assertEqual(review["comparison_exempt_count"], len(EXPECTED_COMPARISON_EXEMPT_ARTIFACTS))
        for row in review["artifact_hashes"]:
            relative = row["root_relative_path"]
            if relative in EXPECTED_SELF_HASH_PRESENCE_ONLY_ARTIFACTS:
                self.assertEqual(row["hash_comparison_policy"], "self_hash_not_representable_presence_only")
                self.assertIsNone(row["expected_sha256"])
                self.assertIsNone(row["actual_sha256"])
                self.assertIsNone(row["sha256_matches"])
                self.assertEqual(row["hash_observation_status"], "self_hash_not_representable_after_write")
            elif relative in EXPECTED_POST_MANIFEST_HASH_OBSERVATION_ARTIFACTS:
                self.assertEqual(row["hash_comparison_policy"], "post_manifest_hash_observation_no_expected_comparison")
                self.assertIsNone(row["expected_sha256"])
                self.assertEqual(row["actual_sha256"], sha256_file(REPO / row["path"]))
                self.assertIsNone(row["sha256_matches"])
                self.assertEqual(row["hash_observation_status"], "post_manifest_hash_observed_without_expected_comparison")
            else:
                self.assertIsNotNone(row["expected_sha256"])
                self.assertIsNotNone(row["actual_sha256"])
                self.assertTrue(row["sha256_matches"])

    def test_validator_recalculates_manifest_expected_hashes(self) -> None:
        temp_parent = REPO / "Iris/build/description/v2/.tmp_tests/dvf_3_3_current_source_authority_drift_verification"
        temp_parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="review_hash_recalc_", dir=temp_parent) as temp_dir:
            temp_root = Path(temp_dir) / "evidence"
            shutil.copytree(ROOT, temp_root)
            target = temp_root / "phase1/source_chain_identity_report.json"
            target.write_text(target.read_text(encoding="utf-8") + "\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-B", str(VALIDATOR), "--root", str(temp_root)],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            report = load_json(temp_root / "phase6/validation_report.all.json")
            codes = {row["code"] for row in report["errors"]}
            self.assertIn("review_artifact_hash_mismatch_recalculated", codes)

    def test_final_json_non_claims_match_markdown_boundary(self) -> None:
        final = load_json(ROOT / "phase6/final_current_source_authority_drift_verification_report.json")
        non_claims = set(final["non_claims"])

        self.assertIn("no_rendered_live_regeneration", non_claims)
        self.assertIn("no_lua_bridge_export", non_claims)
        self.assertIn("no_runtime_chunk_replacement", non_claims)
        self.assertIn("no_live_required_validation_manifest_adoption", non_claims)

    def test_require_complete_validator_passes_after_review_and_owner_seal(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(VALIDATOR), "--require-complete"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        report = load_json(ROOT / "phase6/validation_report.require_complete.json")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["error_count"], 0)
        self.assertEqual(report["errors"], [])


if __name__ == "__main__":
    unittest.main()
