from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal"
SCRIPT = TOOLS / "run_dvf_3_3_closeout_reentry_guard_seal.py"

sys.path.insert(0, str(TOOLS))

import dvf_3_3_closeout_reentry_guard_seal_common as common  # noqa: E402
from dvf_3_3_closeout_reentry_guard_seal_common import (  # noqa: E402
    EXPECTED_CURRENT_ROUTE_TEST_COUNT,
    FULL_CURRENT_ROUTE_CONTRACT_CLASS,
    FULL_CURRENT_ROUTE_SCHEMA_VERSION,
    classify_claim_text,
    classify_predecessor_context,
    validate_all,
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def runner_shaped_route_payload() -> dict:
    manifest = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")
    required_tests = [
        row["test_id"]
        for row in manifest["required_tests"]
        if row.get("required") is True
    ]
    return {
        "schema_version": FULL_CURRENT_ROUTE_SCHEMA_VERSION,
        "contract_class": FULL_CURRENT_ROUTE_CONTRACT_CLASS,
        "success": True,
        "test_count": EXPECTED_CURRENT_ROUTE_TEST_COUNT,
        "selected_identity_count": EXPECTED_CURRENT_ROUTE_TEST_COUNT,
        "closure_enforced": True,
        "errors": [],
        "failures": [],
        "skipped": [],
        "required_validations": {
            "success": True,
            "errors": [],
            "manifest_path": "Iris\\_docs\\round3\\current_route_required_validations.json",
            "required": True,
            "required_artifact_count": len(manifest["required_artifacts"]),
            "required_test_count": len(required_tests),
            "required_tests": required_tests,
        },
    }


class DvfCloseoutReentryGuardSealTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.run_generator()
        report, ok = validate_all(require_complete=True)
        if not ok:
            raise AssertionError(f"closeout/reentry guard validation failed: {report['errors']}")

    @classmethod
    def run_generator(cls) -> None:
        route_path = ROOT / "phase7/full_current_route_validation_result.json"
        if common.full_current_route_result_summary().get("runner_result_valid") is not True:
            route_path.parent.mkdir(parents=True, exist_ok=True)
            route_path.write_text(
                json.dumps(runner_shaped_route_payload(), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--mode", "generate"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "closeout/reentry guard generation failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_taxonomy_splits_allowed_and_forbidden_claim_classes(self) -> None:
        taxonomy = load_json(ROOT / "phase2/dvf_3_3_closeout_claim_taxonomy.json")
        report = load_json(ROOT / "phase2/completion_vocabulary_separation_report.json")

        allowed = {row["claim_class"] for row in taxonomy["allowed_claim_classes"]}
        forbidden = {row["claim_class"] for row in taxonomy["forbidden_overclaim_classes"]}

        self.assertEqual(taxonomy["status"], "PASS")
        self.assertFalse(taxonomy["standalone_complete_allowed"])
        self.assertIn("terminal_disposition_complete", allowed)
        self.assertIn("broad_consumer_completion", allowed)
        self.assertIn("cutover_subset_completion", allowed)
        self.assertIn("problem7_full_current_route_validation_pass", allowed)
        self.assertIn("release_readiness", forbidden)
        self.assertIn("runtime_authority_current_without_runtime_authority_input", forbidden)
        self.assertEqual(report["standalone_complete_claim_count"], 0)
        self.assertEqual(report["complete_suffix_violation_count"], 0)

    def test_claim_surface_scan_is_fail_closed_and_not_self_scanned(self) -> None:
        scan = load_json(ROOT / "phase1/claim_surface_scan_manifest.json")
        inventory = load_json(ROOT / "phase1/closeout_claim_surface_inventory.json")
        included = {path.replace("\\", "/") for path in scan["included_files"]}

        self.assertEqual(scan["status"], "PASS")
        self.assertEqual(inventory["status"], "PASS")
        self.assertEqual(scan["missing_required_surface_family_count"], 0)
        self.assertEqual(scan["blocked_claim_surface_count"], 0)
        self.assertEqual(scan["forbidden_overclaim_violation_count"], 0)
        self.assertEqual(scan["forbidden_predecessor_reentry_violation_count"], 0)
        self.assertEqual(inventory["blocked_claim_surface_count"], 0)
        self.assertFalse(
            any(
                path.startswith(
                    "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase1/"
                )
                for path in included
            )
        )

    def test_top_doc_publish_boundary_definitions_do_not_overclaim_readiness(self) -> None:
        allowed_rows = [
            (
                common.ARCHITECTURE_DOC,
                "Publish Boundary는 public text acceptance, semantic quality acceptance, package publication, release / Workshop readiness, manual QA를 별도 축으로 둔다.",
            ),
            (
                common.DECISIONS_DOC,
                "  * Publish Boundary 책임은 public text acceptance, semantic quality acceptance, package publication, release / Workshop readiness, manual QA다.",
            ),
            (
                common.ARCHITECTURE_DOC,
                "Public Text Quality / public acceptance / release readiness",
            ),
            (
                common.ROADMAP_DOC,
                "  * 후속 라우팅은 public acceptance / release readiness -> Publish Boundary Closure로 고정한다.",
            ),
        ]
        for path, line in allowed_rows:
            with self.subTest(path=path.name):
                row = common.classify_surface_line(path, line)
                self.assertIsNotNone(row)
                self.assertEqual(row["role"], "forbidden_overclaim_definition")
                self.assertTrue(row["definition_context"])
                self.assertEqual(row["classification"], "classified")

        blocked = common.classify_surface_line(
            common.ARCHITECTURE_DOC,
            "Release readiness is achieved by this closeout.",
        )
        self.assertIsNotNone(blocked)
        self.assertEqual(blocked["role"], "forbidden_overclaim_violation")
        self.assertFalse(blocked["definition_context"])
        self.assertEqual(blocked["classification"], "blocked")

    def test_predecessor_reentry_negative_fixtures_fail_closed(self) -> None:
        guard = load_json(ROOT / "phase3/predecessor_reentry_guard_report.json")
        raw = load_json(ROOT / "phase3/raw_predecessor_authority_read_report.json")
        debt = load_json(ROOT / "phase3/current_debt_reentry_report.json")
        dual = load_json(ROOT / "phase3/dual_reentry_authority_report.json")

        self.assertEqual(guard["status"], "PASS")
        self.assertEqual(guard["predecessor_reentry_violation_count"], 0)
        self.assertEqual(guard["current_hard_gate_predecessor_direct_use_count"], 0)
        self.assertEqual(guard["runtime_authority_predecessor_direct_use_count"], 0)
        self.assertEqual(guard["current_debt_predecessor_direct_use_count"], 0)
        self.assertTrue(all(row["status"] == "PASS" for row in guard["fixtures"]))
        self.assertEqual(raw["RAW_PREDECESSOR_AUTHORITY_READ"], 0)
        self.assertEqual(debt["CURRENT_DEBT_REENTRY"], 0)
        self.assertEqual(dual["dual_reentry_authority_count"], 0)

        self.assertIn("current_hard_gate_reentry", classify_predecessor_context("2105 is current hard gate"))
        self.assertIn("runtime_authority_reentry", classify_predecessor_context("2084 is runtime authority"))
        self.assertIn("current_debt_reentry", classify_predecessor_context("21 is current debt"))
        self.assertEqual(classify_predecessor_context("2105 is historical predecessor trace and must not become current debt"), [])

    def test_closeout_boundary_rejects_problem7_and_readiness_promotion(self) -> None:
        boundary = load_json(ROOT / "phase4/closeout_claim_boundary_guard_report.json")
        promotion = load_json(ROOT / "phase4/problem7_to_closeout_guard_promotion_guard_report.json")

        self.assertEqual(boundary["status"], "PASS")
        self.assertEqual(boundary["ambiguous_complete_claim_count"], 0)
        self.assertEqual(boundary["broad_cutover_collision_count"], 0)
        self.assertEqual(boundary["pre_apply_readiness_to_live_completion_promotion_count"], 0)
        self.assertEqual(boundary["problem7_pass_to_closeout_guard_completion_promotion_count"], 0)
        self.assertEqual(boundary["problem7_partial_flattened_to_complete_count"], 0)
        self.assertEqual(boundary["forbidden_overclaim_count"], 0)
        self.assertEqual(promotion["problem7_closeout_state"], "partial")
        self.assertEqual(promotion["problem7_pass_to_closeout_guard_completion_promotion_count"], 0)

        self.assertIn(
            "problem7_to_problem8_completion_promotion",
            classify_claim_text("Problem7 PASS makes Problem8 complete"),
        )
        self.assertIn(
            "live_migration_execution_complete_without_execution",
            classify_claim_text("pre-apply readiness means live migration execution complete"),
        )

    def test_manifest_adoption_is_governance_only_and_runner_visible(self) -> None:
        adoption = load_json(ROOT / "phase5/closeout_reentry_guard_manifest_adoption_report.json")
        live_manifest = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")

        self.assertEqual(adoption["status"], "PASS")
        self.assertEqual(adoption["required_gate_adoption_status"], "adopted_required_gate")
        self.assertTrue(adoption["live_manifest_contains_required_artifacts"])
        self.assertTrue(adoption["live_manifest_contains_required_tests"])
        self.assertEqual(adoption["dual_reentry_authority_count"], 0)
        self.assertFalse(adoption["governance_adopted_required_gate_is_runtime_adopted_row"])
        self.assertFalse(adoption["manifest_adoption_creates_runtime_mutation_claim"])

        required_paths = {row["path"] for row in live_manifest["required_artifacts"]}
        required_tests = {row["test_id"] for row in live_manifest["required_tests"]}
        self.assertIn("required_validation_gate_adopted", live_manifest["claim"])
        self.assertIn("axis-qualified", live_manifest["claim"])
        self.assertNotIn("current authority cutover and 2105 consumer migration sealed", live_manifest["claim"])
        self.assertIn(
            "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/final_closeout_reentry_guard_seal_report.json",
            required_paths,
        )
        self.assertIn(
            (
                "test_dvf_3_3_closeout_reentry_guard_seal."
                "DvfCloseoutReentryGuardSealTest.test_manifest_adoption_is_governance_only_and_runner_visible"
            ),
            required_tests,
        )

    def test_final_report_allows_canonical_seal_and_keeps_release_out_of_scope(self) -> None:
        final = load_json(ROOT / "phase7/final_closeout_reentry_guard_seal_report.json")
        no_mutation = load_json(ROOT / "phase7/final_no_mutation_report.json")
        commands = load_json(ROOT / "phase7/final_pinned_command_manifest.json")
        review_hash = load_json(ROOT / "phase7/independent_review_artifact_hash_report.json")
        live_manifest = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")
        claim_boundary = (REPO / "docs/dvf_3_3_closeout_reentry_claim_boundary.md").read_text(encoding="utf-8")
        review_paths = {row["path"] for row in review_hash["artifacts"]}
        required_paths = {row["path"] for row in live_manifest["required_artifacts"]}

        self.assertEqual(final["status"], "PASS")
        self.assertEqual(final["machine_contract_status"], "PASS")
        self.assertEqual(final["closeout_state"], "canonical_complete")
        self.assertTrue(final["canonical_seal_allowed"])
        self.assertEqual(final["independent_review_status"], "PASS")
        self.assertEqual(final["protected_source_rendered_lua_runtime_package_changed_count"], 0)
        self.assertIn("no_release_readiness", final["non_claims"])
        self.assertIn("no_public_text_acceptance", final["non_claims"])
        self.assertEqual(no_mutation["changed_count"], 0)
        self.assertEqual(commands["approved_successor_pinned_baseline"]["expected_test_count"], EXPECTED_CURRENT_ROUTE_TEST_COUNT)
        self.assertIn("axis-qualified", claim_boundary)
        self.assertIn("canonical seal is allowed", claim_boundary)
        self.assertEqual(review_hash["status"], "PASS")
        self.assertEqual(review_hash["independent_review_status"], "PASS")
        self.assertTrue(review_hash["canonical_seal_allowed"])
        self.assertEqual(review_hash["primary_review_artifact_missing_count"], 0)
        self.assertIn(
            "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/independent_review_artifact_hash_report.json",
            required_paths,
        )
        for path in {
            "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/final_closeout_reentry_guard_seal_report.json",
            "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/full_current_route_validation_result.json",
            "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/validation_report.all.json",
            "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase1/claim_surface_scan_manifest.json",
        }:
            self.assertIn(path, review_paths)

    def test_generate_final_report_reflects_claim_scan_failure(self) -> None:
        bad_surface = ROOT / "phase7/test_forbidden_claim_surface.md"
        bad_surface.write_text("release readiness achieved\n", encoding="utf-8")
        try:
            with mock.patch.object(common, "scan_surface_files", return_value=[bad_surface]):
                final = common.generate_artifacts()

            self.assertEqual(final["status"], "FAIL")
            self.assertEqual(final["machine_contract_status"], "FAIL")
            self.assertEqual(final["claim_surface_scan_state"], "FAIL")
            self.assertGreater(final["claim_surface_scan_blocked_claim_surface_count"], 0)
        finally:
            if bad_surface.exists():
                bad_surface.unlink()
            self.run_generator()

    def test_validator_requires_full_current_route_result_for_complete_contract(self) -> None:
        route_path = ROOT / "phase7/full_current_route_validation_result.json"
        backup = route_path.read_text(encoding="utf-8") if route_path.exists() else None
        try:
            if route_path.exists():
                route_path.unlink()
            missing_report, missing_ok = validate_all(require_complete=True)

            self.assertFalse(missing_ok)
            error_codes = {error["code"] for error in missing_report["errors"]}
            self.assertIn("full_current_route_validation_missing", error_codes)
            self.assertIn("full_current_route_validation_summary_stale", error_codes)

            route_path.write_text(
                json.dumps(
                    {
                        "success": True,
                        "test_count": EXPECTED_CURRENT_ROUTE_TEST_COUNT,
                        "closure_enforced": True,
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            generate_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "generate"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(generate_result.returncode, 0, generate_result.stdout + generate_result.stderr)
            final = load_json(ROOT / "phase7/final_closeout_reentry_guard_seal_report.json")
            self.assertEqual(final["machine_contract_status"], "FAIL")
            self.assertFalse(final["full_current_route_runner_result_valid"])

            malformed_report, malformed_ok = validate_all(require_complete=True)

            self.assertFalse(malformed_ok)
            self.assertIn(
                "full_current_route_runner_shape_invalid",
                {error["code"] for error in malformed_report["errors"]},
            )

            bad_required_payload = runner_shaped_route_payload()
            bad_required_payload["required_validations"]["required_test_count"] = 1
            bad_required_payload["required_validations"]["required_tests"] = ["synthetic.runner_shape_fixture"]
            route_path.write_text(
                json.dumps(bad_required_payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            bad_required_result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--mode", "generate"],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(
                bad_required_result.returncode,
                0,
                bad_required_result.stdout + bad_required_result.stderr,
            )
            bad_required_report, bad_required_ok = validate_all(require_complete=True)
            self.assertFalse(bad_required_ok)
            self.assertIn(
                "full_current_route_runner_shape_invalid",
                {error["code"] for error in bad_required_report["errors"]},
            )

            route_path.write_text(
                json.dumps(runner_shaped_route_payload(), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            self.run_generator()
            report, ok = validate_all(require_complete=True)
            self.assertTrue(ok, report["errors"])
        finally:
            if backup is None:
                if route_path.exists():
                    route_path.unlink()
            else:
                route_path.write_text(backup, encoding="utf-8")
            self.run_generator()


if __name__ == "__main__":
    unittest.main()
