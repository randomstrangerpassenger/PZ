from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration"
SCRIPT = REPO / "Iris/build/description/v2/tools/build/dvf_3_3_vnext_delta_guard_current_route_integration.py"
RUNNER = REPO / "Iris/_docs/round3/round3_run_contract_tests.py"
REQUIRED_MANIFEST = REPO / "Iris/_docs/round3/current_route_required_validations.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class DvfVnextDeltaGuardCurrentRouteIntegrationTest(unittest.TestCase):
    live_manifest_before: dict | None = None
    live_manifest_after: dict | None = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.live_manifest_before = load_json(REQUIRED_MANIFEST) if REQUIRED_MANIFEST.exists() else None
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        cls.live_manifest_after = load_json(REQUIRED_MANIFEST) if REQUIRED_MANIFEST.exists() else None

    def test_final_report_preserves_claim_boundary(self) -> None:
        report = load_json(ROOT / "phase7/final_current_route_guard_integration_report.json")

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["claim"], "current route guard integrated")
        self.assertTrue(report["current_route_guard_integrated"])
        self.assertFalse(report["cutover_input_usable"])
        self.assertTrue(report["approved_manifest_index_only"])
        self.assertFalse(report["current_core_closure_expanded"])
        self.assertFalse(report["tooling_allowlist_expanded"])
        self.assertFalse(report["runtime_surface_mutated"])
        self.assertEqual(report["counts"]["total"], 2125)
        self.assertEqual(report["counts"]["approved"], 2017)
        self.assertEqual(report["counts"]["rejected"], 108)
        self.assertIn("no_release_readiness", report["non_claims"])
        self.assertIn("no_current_cutover", report["non_claims"])

    def test_guard_coverage_matrix_keeps_single_status_aware_definition(self) -> None:
        matrix = load_json(ROOT / "phase2/guard_coverage_matrix.json")

        self.assertEqual(matrix["status"], "PASS")
        self.assertEqual(matrix["primary_forbidden_condition_count"], 8)
        primary_rows = [row for row in matrix["rows"] if row.get("condition_role") != "subordinate_reference"]
        self.assertEqual(len(primary_rows), 8)
        self.assertTrue(all(row["definition_source_count"] == 1 for row in primary_rows))
        self.assertTrue(all(row["surface_owner_status"] == "sealed" for row in primary_rows))

        stale_rows = [row for row in matrix["rows"] if row["guard_id"] == "stale_dvf_bridge_package_intrusion"]
        self.assertEqual(len(stale_rows), 1)
        self.assertEqual(stale_rows[0]["surface_owner_status"], "implemented_review_pending")
        self.assertEqual(stale_rows[0]["shared_contract_role"], "referenced_subordinate_package_guard_evidence")
        self.assertEqual(
            stale_rows[0]["dual_definition_verdict"],
            "no_competing_definition_but_not_independently_sealed",
        )

    def test_required_validation_manifest_is_fail_closed_and_runner_visible(self) -> None:
        phase_manifest = load_json(ROOT / "phase4/current_route_required_validations.json")
        report = load_json(ROOT / "phase4/current_route_guard_integration_report.json")
        required_ids = {row["test_id"] for row in phase_manifest["required_tests"]}

        self.assertEqual(self.live_manifest_after, self.live_manifest_before)
        self.assertFalse(report["required_validation_manifest_written"])
        self.assertFalse(report["live_required_validation_manifest_mutated"])
        self.assertTrue(phase_manifest["required"])
        self.assertGreaterEqual(len(required_ids), 10)
        self.assertIn(
            "test_dvf_3_3_vnext_delta_disposition_guard_seal.DvfVnextDeltaDispositionGuardSealTest.test_final_contract_separates_guard_completion_from_cutover_usability",
            required_ids,
        )
        self.assertIn(
            "test_package_layer3_chunks_only_contract.PackageLayer3ChunksOnlyContractTest.test_package_script_fails_loud_on_stale_dvf_bridge_surface",
            required_ids,
        )

        list_result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(RUNNER),
                "--class",
                "current",
                "--required-validations",
                str(ROOT / "phase4/current_route_required_validations.json"),
                "--enforce-current-build-closure",
                "--list",
            ],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(list_result.returncode, 0, list_result.stderr)
        self.assertIn(
            "test_dvf_3_3_vnext_delta_guard_current_route_integration.DvfVnextDeltaGuardCurrentRouteIntegrationTest.test_final_report_preserves_claim_boundary",
            list_result.stdout,
        )

        tmp = REPO / "Iris/build/description/v2/tests/_tmp_delta_guard_current_route_manifest"
        if tmp.exists():
            shutil.rmtree(tmp)
        tmp.mkdir(parents=True)
        try:
            bad_manifest = tmp / "current_route_required_validations.bad.json"
            bad_manifest.write_text(
                json.dumps(
                    {
                        "schema_version": "round3-current-route-required-validations-v1",
                        "required": True,
                        "required_tests": [],
                        "required_artifacts": [],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            bad_result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(RUNNER),
                    "--class",
                    "current",
                    "--required-validations",
                    str(bad_manifest),
                    "--list",
                ],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(bad_result.returncode, 2)
            self.assertIn("has no required tests", bad_result.stderr)
        finally:
            if tmp.exists():
                shutil.rmtree(tmp)

    def test_package_export_compose_routes_share_criteria_by_equivalence(self) -> None:
        criteria = load_json(ROOT / "phase2/forbidden_scan_criteria.json")
        report = load_json(ROOT / "phase5/package_export_compose_guard_report.json")
        drift = load_json(ROOT / "phase5/shared_criteria_drift_report.json")
        compose = load_json(ROOT / "phase5/compose_build_rendered_boundary_report.json")

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["criteria_sha256"], criteria["criteria_sha256"])
        self.assertEqual(drift["status"], "PASS")
        self.assertFalse(drift["advisory_only"])
        self.assertEqual(drift["criteria_mismatch_count"], 0)
        self.assertEqual(report["routes"]["package"]["status"], "PASS")
        self.assertEqual(report["routes"]["export"]["status"], "PASS")
        self.assertEqual(report["routes"]["compose"]["status"], "PASS")
        self.assertEqual(compose["status"], "PASS")
        self.assertEqual(compose["compose_route_guard_target"], "compose_layer3_text.py::build_rendered()")
        self.assertTrue(compose["build_rendered_boundary_bound"])

    def test_parent_handoff_keeps_cutover_and_release_out_of_scope(self) -> None:
        handoff = load_json(ROOT / "phase7/parent_problem_handoff_report.json")
        closeout = (REPO / "docs/dvf_3_3_vnext_delta_guard_current_route_integration_closeout.md").read_text(
            encoding="utf-8"
        )

        self.assertEqual(handoff["status"], "PASS")
        self.assertIn("rejected_or_unapproved_delta_inclusion", handoff["forbidden_next_inputs"])
        self.assertIn("separate cutover scope approval", handoff["prerequisites"])
        self.assertIn("no_current_authority_baseline_manifest_created", handoff["non_claims"])
        self.assertIn("COMMON-RELEASE-NONDECISION", closeout)
        self.assertIn("COMMON-RUNTIME-SURFACE-NONMUTATION", closeout)
        self.assertIn("does not claim successor baseline identity final seal", closeout)


if __name__ == "__main__":
    unittest.main()
