from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROUND_ID = "dvf_3_3_dvf_system_naming_realignment"
ROOT = REPO / "Iris/build/description/v2/staging" / ROUND_ID
RUNNER = TOOLS / f"run_{ROUND_ID}.py"
VALIDATOR = TOOLS / f"validate_{ROUND_ID}.py"
INNER = os.environ.get("DVF_SYSTEM_NAMING_REALIGNMENT_INNER_CURRENT_ROUTE") == "1"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class DvfSystemNamingRealignmentCurrentRouteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        final = ROOT / "phase6/final_naming_realignment_machine_report.json"
        if final.exists():
            return
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--mode", "all", "--skip-current-route"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "naming realignment artifact generation failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_required_gate_evidence_is_subprocess_generated_and_governance_only(self) -> None:
        final = load_json(ROOT / "phase6/final_naming_realignment_machine_report.json")
        design = load_json(ROOT / "phase5/import_closure_compatible_test_design_report.json")

        self.assertEqual(final["status"], "machine_pass_governance_only")
        self.assertEqual(final["dvf_system_naming_realignment_state"], "required_gate_adopted_complete")
        self.assertFalse(final["owner_required_decision_missing"])
        self.assertFalse(final["dvf_body_compiler_pass_achievement_claimed"])
        self.assertFalse(final["registry_authority_pass_claimed"])
        self.assertFalse(final["publish_boundary_pass_claimed"])
        self.assertEqual(final["protected_surface_changed_count"], 0)
        self.assertFalse(final["source_rendered_lua_runtime_package_mutation"])
        self.assertEqual(design["tools_build_package_import_attempt_count"], 0)
        self.assertTrue(design["bare_tool_module_import_used"])
        self.assertFalse(design["round3_active_core_closure_expansion_required"])

        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(VALIDATOR),
                "--require-complete",
                "--skip-route-requirements",
            ],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_forbidden_fixture_matrix_and_korean_cases_pass(self) -> None:
        negative = load_json(ROOT / "phase4/negative_fixture_matrix_report.json")
        korean = load_json(ROOT / "phase4/korean_mixed_language_fixture_report.json")
        positive = load_json(ROOT / "phase4/dvf_system_naming_realignment_pass_positive_fixture_report.json")

        self.assertEqual(negative["status"], "PASS")
        self.assertEqual(negative["forbidden_fixture_failure_count"], negative["negative_fixture_count"])
        self.assertEqual(korean["korean_mixed_language_fixture_status"], "PASS")
        self.assertEqual(positive["dvf_system_naming_realignment_pass_positive_fixture_status"], "PASS")

    def test_current_docs_resolve_retired_core_usage(self) -> None:
        usage = load_json(ROOT / "phase3/literal_vs_resolved_usage_report.json")
        scan = load_json(ROOT / "phase4/forbidden_claim_scan_report.json")

        self.assertEqual(usage["resolved_current_canonical_dvf_core_usage_count"], 0)
        self.assertTrue(usage["all_literal_dvf_core_occurrences_disposition_classified"])
        self.assertEqual(scan["forbidden_current_claim_count"], 0)
        self.assertEqual(scan["overclaim_scanner_class"], "lexical_token_level")

    def test_manifest_adoption_is_additive_when_selected(self) -> None:
        report = load_json(ROOT / "phase5/current_route_required_validation_patch.json")
        live = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")
        paths = {row["path"] for row in live["required_artifacts"]}
        tests = {row["test_id"] for row in live["required_tests"]}

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["removed_existing_entries"], 0)
        self.assertEqual(report["modified_existing_entries"], 0)
        self.assertEqual(report["predicate_meaning_change_count"], 0)
        self.assertIn(
            f"Iris/build/description/v2/staging/{ROUND_ID}/phase6/final_naming_realignment_machine_report.json",
            paths,
        )
        self.assertIn(
            "test_dvf_3_3_dvf_system_naming_realignment."
            "DvfSystemNamingRealignmentCurrentRouteTest."
            "test_required_gate_evidence_is_subprocess_generated_and_governance_only",
            tests,
        )


if __name__ == "__main__":
    unittest.main()
