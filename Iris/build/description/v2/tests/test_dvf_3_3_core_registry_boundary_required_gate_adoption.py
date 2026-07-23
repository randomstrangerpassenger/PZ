from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROUND_ID = "dvf_3_3_core_registry_boundary_required_gate_adoption"
ROOT = REPO / "Iris/build/description/v2/staging" / ROUND_ID
RUNNER = TOOLS / f"run_{ROUND_ID}.py"
VALIDATOR = TOOLS / f"validate_{ROUND_ID}.py"
INNER = (
    os.environ.get("DVF_REQUIRED_GATE_ADOPTION_INNER_CURRENT_ROUTE") == "1"
    or os.environ.get("DVF_REQUIRED_GATE_ADOPTION_INNER_FOCUSED") == "1"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_contract_probe() -> dict:
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(VALIDATOR),
            "--root",
            str(ROOT),
            "--probe-contract",
        ],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "required gate adoption contract probe failed\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return json.loads(result.stdout.strip().splitlines()[-1])


class DvfCoreRegistryBoundaryRequiredGateAdoptionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if INNER:
            return
        final = ROOT / "final_boundary_required_gate_adoption_report.json"
        if final.exists():
            payload = load_json(final)
            if payload.get("machine_required_gate_adoption_complete") is True:
                return
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--mode", "all"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "required gate adoption runner failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def copy_evidence(self, name: str) -> Path:
        tempdir = Path(tempfile.mkdtemp(prefix="dvf_required_gate_"))
        target = tempdir / name
        shutil.copytree(ROOT, target)
        self.addCleanup(lambda: shutil.rmtree(tempdir, ignore_errors=True))
        return target

    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["DVF_CORE_REGISTRY_BOUNDARY_REQUIRED_GATE_ADOPTION_ROOT"] = str(root)
        return subprocess.run(
            [sys.executable, "-B", str(VALIDATOR), "--root", str(root), "--require-complete"],
            cwd=REPO,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_live_rescan_enforces_claim_boundary(self) -> None:
        probe = load_contract_probe()
        report = probe["clean_scan"]
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["forbidden_overclaim_count"], 0)
        self.assertTrue(report["claim_scan_minimum_universe_satisfied"])

        bad = probe["injected_scan"]
        self.assertGreater(bad["forbidden_overclaim_count"], 0)
        self.assertIn("standalone_current_dvf_pass", {row["violation_code"] for row in bad["violations"]})

    def test_manifest_adoption_is_additive_and_governance_only(self) -> None:
        report = load_json(ROOT / "phase3/required_manifest_adoption_report.json")
        live = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")
        paths = {row["path"] for row in live["required_artifacts"]}
        tests = {row["test_id"] for row in live["required_tests"]}

        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["required_gate_adopted"])
        self.assertEqual(report["required_manifest_adoption_mode"], "additive_only")
        self.assertEqual(report["removed_required_artifact_count"], 0)
        self.assertEqual(report["removed_required_test_count"], 0)
        self.assertEqual(report["modified_existing_entries"], 0)
        self.assertEqual(report["predicate_meaning_change_count"], 0)
        self.assertFalse(report["source_rendered_lua_runtime_package_authority_mutated"])
        probe = load_contract_probe()
        for row in probe["round_required_artifacts"]:
            self.assertIn(row["path"], paths)
        for test_id in probe["round_required_tests"]:
            self.assertIn(test_id, tests)

    def test_bootstrap_and_pre_route_no_mutation_are_pass(self) -> None:
        mapping = load_json(ROOT / "phase1/field_host_phase_mapping.json")
        bootstrap = load_json(ROOT / "phase3/bootstrap_sufficiency_report.json")
        no_mutation = load_json(ROOT / "phase4/protected_surface_no_mutation_report.json")

        self.assertEqual(mapping["field_host_phase_mapping_status"], "PASS")
        self.assertEqual(mapping["manifest_required_route_result_field_count"], 0)
        self.assertFalse(mapping["final_no_mutation_summary_manifest_required_allowed"])
        self.assertEqual(bootstrap["status"], "PASS")
        self.assertTrue(bootstrap["all_manifest_required_artifacts_exist_before_post_adoption_route"])
        self.assertTrue(bootstrap["all_manifest_required_artifacts_have_final_values_before_post_adoption_route"])
        self.assertEqual(no_mutation["status"], "PASS")
        self.assertEqual(no_mutation["pre_route_protected_surface_changed_count"], 0)
        self.assertTrue(no_mutation["required_gate_artifacts_present"])

    def test_allowed_boundary_fixtures_include_korean(self) -> None:
        allowed = load_json(ROOT / "phase2/allowed_boundary_fixture_report.json")
        negative = load_json(ROOT / "phase2/negative_fixture_report.json")

        self.assertEqual(allowed["status"], "PASS")
        self.assertTrue(allowed["korean_fixture_coverage"])
        self.assertEqual(allowed["allowed_boundary_statement_false_positive_count"], 0)
        self.assertEqual(negative["status"], "PASS")
        self.assertEqual(negative["forbidden_fixture_failure_count"], 4)

    def test_final_report_preserves_two_pass_boundary_and_non_claims(self) -> None:
        if INNER:
            self.assertTrue((ROOT / "phase3/bootstrap_sufficiency_report.json").exists())
            return
        final = load_json(ROOT / "final_boundary_required_gate_adoption_report.json")
        update = load_json(ROOT / "phase6/post_final_report_update_contract.json")

        self.assertEqual(final["status"], "machine_pass_governance_only")
        self.assertTrue(final["machine_required_gate_adoption_complete"])
        self.assertTrue(final["post_final_current_route_rerun_success"])
        self.assertTrue(final["live_rescan_required_test_consumed"])
        self.assertTrue(final["post_final_live_rescan_required_test_consumed"])
        self.assertEqual(final["protected_surface_changed_count"], 0)
        self.assertFalse(final["source_rendered_lua_runtime_package_mutation"])
        self.assertFalse(final["canonical_seal_allowed"])
        self.assertFalse(final["release_readiness_claimed"])
        self.assertFalse(final["manual_qa_claimed"])
        self.assertEqual(update["post_final_report_update_contract_status"], "PASS")
        self.assertFalse(update["post_final_report_freeform_text_mutation_detected"])
        self.assertTrue(update["post_final_report_updated_field_set_matches_allowlist"])

    def test_validator_rejects_forbidden_overclaim_tamper(self) -> None:
        if INNER:
            self.assertTrue((ROOT / "phase2/claim_surface_scan_report.json").exists())
            return
        tampered = self.copy_evidence("tampered_overclaim")
        path = tampered / "phase2/claim_surface_scan_report.json"
        payload = load_json(path)
        payload["status"] = "FAIL"
        payload["forbidden_overclaim_count"] = 1
        payload["violations"] = [{"violation_code": "standalone_current_dvf_pass"}]
        write_json(path, payload)

        result = self.run_validator(tampered)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(tampered / "phase6/validation_report.require_complete.json")
        self.assertIn("field_mismatch", {error["code"] for error in report["errors"]})


if __name__ == "__main__":
    unittest.main()
