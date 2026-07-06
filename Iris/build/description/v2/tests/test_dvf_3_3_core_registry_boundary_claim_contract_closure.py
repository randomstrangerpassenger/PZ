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
ROUND_ID = "dvf_3_3_core_registry_boundary_claim_contract_closure"
RUNNER = TOOLS / f"run_{ROUND_ID}.py"
VALIDATOR = TOOLS / f"validate_{ROUND_ID}.py"

sys.path.insert(0, str(TOOLS))
import dvf_3_3_core_registry_boundary_claim_contract_closure as closure  # noqa: E402


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class DvfCoreRegistryBoundaryClaimContractClosureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tempdir = tempfile.TemporaryDirectory(prefix="dvf_core_registry_claim_")
        cls.root = Path(cls._tempdir.name) / "evidence"
        cls.env = os.environ.copy()
        cls.env["DVF_CORE_REGISTRY_BOUNDARY_CLAIM_CONTRACT_CLOSURE_ROOT"] = str(cls.root)
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--mode", "all"],
            cwd=REPO,
            env=cls.env,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "claim contract closure generation failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    @classmethod
    def tearDownClass(cls) -> None:
        tempdir = getattr(cls, "_tempdir", None)
        if tempdir is not None:
            tempdir.cleanup()

    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["DVF_CORE_REGISTRY_BOUNDARY_CLAIM_CONTRACT_CLOSURE_ROOT"] = str(root)
        return subprocess.run(
            [sys.executable, "-B", str(VALIDATOR), "--require-complete"],
            cwd=REPO,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def copy_evidence(self, name: str) -> Path:
        target = Path(self._tempdir.name) / name
        shutil.copytree(self.root, target)
        return target

    def test_final_report_keeps_claims_separated(self) -> None:
        final = load_json(self.root / "phase6/final_boundary_split_closure_report.json")

        self.assertTrue(final["claim_boundary_split_complete"])
        self.assertEqual(final["status"], "machine_pass_governance_only")
        self.assertEqual(final["predecessor_inventory_freshness_status"], "PASS")
        self.assertFalse(final["legacy_combined_route_pass_is_dvf_core_pass"])
        self.assertFalse(final["dvf_core_pass_runtime_compatible"])
        self.assertFalse(final["dvf_core_pass_package_safe"])
        self.assertFalse(final["dvf_core_pass_public_accepted"])
        self.assertFalse(final["dvf_core_pass_release_ready"])
        self.assertEqual(final["publish_boundary_pass_composition"], "conjunctive_all_components")
        self.assertFalse(final["partial_publish_boundary_bare_pass_allowed"])
        self.assertFalse(final["required_gate_adopted"])
        self.assertFalse(final["future_current_route_blocking_claimed"])
        self.assertEqual(final["protected_surface_changed_count"], 0)
        self.assertEqual(final["independent_review_gate_status"], "not_claimed")

    def test_machine_contract_binds_document_authority(self) -> None:
        contract = load_json(self.root / "phase2/claim_contract.json")
        binding = load_json(self.root / "phase2/document_machine_hash_binding.json")

        self.assertEqual(contract["claim_meaning_authority_path"], "docs/dvf_3_3_core_registry_boundary_claim_contract.md")
        self.assertEqual(binding["document_authority_sha256"], contract["claim_meaning_authority_sha256"])
        self.assertEqual(contract["dvf_pass_disposition"], "forbidden_standalone_current_claim")
        self.assertFalse(contract["dvf_pass_standalone_current_claim_allowed"])
        self.assertEqual(contract["active_exception_classes_source"], "disposition_derived")
        self.assertNotIn("legacy_alias_role_qualified", contract["active_exception_classes"])

    def test_claim_guard_records_scan_universe_and_negative_fixtures(self) -> None:
        scan = load_json(self.root / "phase3/forbidden_overclaim_scan_report.json")
        negative = load_json(self.root / "phase3/negative_fixture_report.json")
        guard = load_json(self.root / "phase3/claim_guard_execution_report.json")

        self.assertEqual(scan["status"], "PASS")
        self.assertGreater(scan["scan_universe_count"], 0)
        self.assertEqual(scan["scan_universe_deduplication_status"], "PASS")
        self.assertEqual(scan["forbidden_overclaim_count"], 0)
        self.assertEqual(negative["status"], "PASS")
        self.assertTrue(guard["partial_publish_boundary_pass_fixture_fails"])
        self.assertTrue(guard["default_disposition_legacy_alias_fixture_fails"])
        self.assertTrue(guard["legacy_alias_only_hash_bound_owner_record_fixture_passes"])

    def test_scanner_default_legacy_alias_fails_but_owner_branch_passes(self) -> None:
        text = "DVF PASS may be used as a legacy alias for current closure."
        _, default_violations = closure.scan_text(
            text,
            source_path="fixture/default.md",
            active_exceptions=closure.BASE_EXCEPTION_CLASSES,
        )
        _, owner_violations = closure.scan_text(
            text,
            source_path="fixture/owner.md",
            active_exceptions=closure.BASE_EXCEPTION_CLASSES + ["legacy_alias_role_qualified"],
        )

        self.assertEqual(default_violations[0]["violation_code"], "inactive_legacy_alias_role_qualified")
        self.assertEqual(owner_violations, [])

    def test_out_of_universe_path_is_counted_with_exclusion_reason(self) -> None:
        path = REPO / "Iris/build/description/v2/data/out_of_universe_fixture.json"
        self.assertEqual(closure.excluded_reason(path), "excluded_root")

    def test_validator_rejects_forbidden_overclaim_tamper(self) -> None:
        tampered = self.copy_evidence("tampered_overclaim")
        path = tampered / "phase3/forbidden_overclaim_scan_report.json"
        payload = load_json(path)
        payload["status"] = "FAIL"
        payload["forbidden_overclaim_count"] = 1
        payload["rows"] = [{"violation_code": "standalone_current_dvf_pass"}]
        write_json(path, payload)

        result = self.run_validator(tampered)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(tampered / "phase6/validation_report.require_complete.json")
        self.assertIn("forbidden_overclaim_detected", {error["code"] for error in report["errors"]})


if __name__ == "__main__":
    unittest.main()
