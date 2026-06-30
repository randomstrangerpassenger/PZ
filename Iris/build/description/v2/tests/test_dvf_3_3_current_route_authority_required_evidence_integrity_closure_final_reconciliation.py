from __future__ import annotations

import hashlib
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
RUNNER = TOOLS / (
    "run_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py"
)
VALIDATOR = TOOLS / (
    "validate_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py"
)
LIVE_MANIFEST = REPO / "Iris/_docs/round3/current_route_required_validations.json"
PARENT_PLAN = REPO / "docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md"
PREFLIGHT_REPORT = REPO / (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_required_artifact_surface_preflight_census/"
    "census_p8_closeout_no_mutation/final_preflight_census_report.json"
)

sys.path.insert(0, str(TOOLS))

from dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation import (  # noqa: E402
    derive_preflight_consumption_state,
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class DvfFinalReconciliationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tempdir = tempfile.TemporaryDirectory(prefix="dvf_final_reconciliation_")
        cls.root = Path(cls._tempdir.name) / "evidence"
        cls.env = os.environ.copy()
        cls.env["DVF_FINAL_RECONCILIATION_EVIDENCE_ROOT"] = str(cls.root)
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--mode", "census"],
            cwd=REPO,
            env=cls.env,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "final reconciliation census generation failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    @classmethod
    def tearDownClass(cls) -> None:
        tempdir = getattr(cls, "_tempdir", None)
        if tempdir is not None:
            tempdir.cleanup()

    def run_validator(self, evidence_root: Path) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["DVF_FINAL_RECONCILIATION_EVIDENCE_ROOT"] = str(evidence_root)
        return subprocess.run(
            [sys.executable, "-B", str(VALIDATOR)],
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

    def test_tooling_bootstrap_and_hash_binding_reports(self) -> None:
        bootstrap = load_json(self.root / "phase0/tooling_bootstrap_report.json")
        contract = load_json(self.root / "phase0/tooling_contract_report.json")
        closure = load_json(self.root / "phase1/closure_input_readpoint_report.json")
        denominator = load_json(self.root / "phase3/denominator_lifecycle_role_binding_report.json")

        self.assertEqual(bootstrap["status"], "PASS")
        self.assertTrue(bootstrap["common_module_exists"])
        self.assertTrue(bootstrap["runner_exists"])
        self.assertTrue(bootstrap["validator_exists"])
        self.assertTrue(bootstrap["focused_test_exists"])
        self.assertFalse(bootstrap["tooling_generation_delegated_to_separate_plan"])
        self.assertEqual(contract["second_authority_count"], 0)
        self.assertEqual(contract["required_set_definition_count"], 0)
        self.assertEqual(closure["live_manifest_sha256"], sha256(LIVE_MANIFEST))
        self.assertEqual(closure["parent_main_plan_sha256"], sha256(PARENT_PLAN))
        self.assertEqual(closure["preflight_report_sha256"], sha256(PREFLIGHT_REPORT))
        self.assertEqual(denominator["live_required_artifact_count"], 93)
        self.assertEqual(denominator["live_required_test_count"], 48)

    def test_preflight_split_and_disposition_supersession_are_explicit(self) -> None:
        preflight = load_json(self.root / "phase2/preflight_result_consumption_report.json")
        disposition = load_json(self.root / "phase2/disposition_result_consumption_report.json")

        self.assertEqual(preflight["artifact_semantic_verdict"], "blocked")
        self.assertEqual(preflight["artifact_disposition_state"], "owner_pending")
        self.assertEqual(preflight["preflight_consumption_state"], "consumed_with_disposition_supersession")
        self.assertEqual(preflight["preflight_blocked_token_silently_downgraded_count"], 0)
        self.assertEqual(
            preflight["preflight_blocked_token_resolved_by_disposition_count"],
            preflight["artifact_unresolved_owner_queue_count"],
        )
        self.assertEqual(disposition["terminal_state"], "ready")
        self.assertEqual(disposition["required_artifact_disposition_problem_status"], "SOLVED")
        self.assertEqual(disposition["disposition_consumption_state"], "consumed_ready_for_parent_rerun")
        self.assertTrue(disposition["parent_rerun_required"])
        self.assertFalse(disposition["parent_machine_pass_claimed"])

    def test_preflight_derivation_rejects_direct_ready_for_current_split(self) -> None:
        preflight = {"semantic_verdict": "blocked", "artifact_disposition_state": "owner_pending"}
        disposition = {"terminal_state": "ready", "required_artifact_disposition_problem_status": "SOLVED"}
        self.assertEqual(
            derive_preflight_consumption_state(preflight, disposition),
            "consumed_with_disposition_supersession",
        )

        unresolved = {"semantic_verdict": "blocked", "artifact_disposition_state": "owner_pending"}
        self.assertEqual(
            derive_preflight_consumption_state(unresolved, {"terminal_state": "owner_pending"}),
            "blocked_unresolved_preflight",
        )

    def test_parent_non_claim_and_manifest_adoption_contract(self) -> None:
        adoption = load_json(self.root / "phase4/required_manifest_adoption_report.json")
        parent_packet = load_json(self.root / "phase10/parent_intake_packet.json")
        top_doc = load_json(self.root / "phase6/top_doc_sync_state.json")

        self.assertEqual(adoption["required_manifest_adoption_state"], "no_live_change_required")
        self.assertEqual(adoption["removed_required_artifact_count"], 0)
        self.assertEqual(adoption["removed_required_test_count"], 0)
        self.assertFalse(adoption["self_reference_detected"])
        self.assertEqual(parent_packet["parent_consumption_authority"], "parent_main_plan_only")
        self.assertFalse(parent_packet["parent_recompute_substitution_allowed"])
        self.assertFalse(parent_packet["parent_machine_pass_claimed"])
        self.assertEqual(top_doc["top_doc_sync_state"], "draft_prepared_owner_application_pending")
        self.assertEqual(top_doc["top_doc_live_mutation_target_count"], 0)

    def test_validator_accepts_census_evidence_without_complete_current_route(self) -> None:
        result = self.run_validator(self.root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(self.root / "phase10/validation_report.json")
        self.assertEqual(report["status"], "PASS")

    def test_validator_rejects_missing_tooling_report(self) -> None:
        tampered = self.copy_evidence("tampered_missing_tooling")
        path = tampered / "phase0/tooling_bootstrap_report.json"
        payload = load_json(path)
        payload["runner_exists"] = False
        payload["status"] = "FAIL"
        write_json(path, payload)

        result = self.run_validator(tampered)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(tampered / "phase10/validation_report.json")
        self.assertIn("field_mismatch", {error["code"] for error in report["errors"]})

    def test_validator_rejects_second_authority_tamper(self) -> None:
        tampered = self.copy_evidence("tampered_second_authority")
        path = tampered / "phase0/tooling_contract_report.json"
        payload = load_json(path)
        payload["second_authority_count"] = 1
        payload["final_reconciliation_tool_second_authority_count"] = 1
        write_json(path, payload)

        result = self.run_validator(tampered)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(tampered / "phase10/validation_report.json")
        self.assertIn("hard_fail_matrix_mismatch", {error["code"] for error in report["errors"]})

    def test_validator_rejects_hash_binding_tamper(self) -> None:
        tampered = self.copy_evidence("tampered_hash_binding")
        path = tampered / "phase1/closure_input_readpoint_report.json"
        payload = load_json(path)
        payload["parent_main_plan_sha256"] = "0" * 64
        write_json(path, payload)

        result = self.run_validator(tampered)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(tampered / "phase10/validation_report.json")
        self.assertIn("hash_binding_mismatch", {error["code"] for error in report["errors"]})

    def test_validator_rejects_preflight_direct_ready_tamper(self) -> None:
        tampered = self.copy_evidence("tampered_preflight_ready")
        path = tampered / "phase2/preflight_result_consumption_report.json"
        payload = load_json(path)
        payload["preflight_consumption_state"] = "consumed_ready_direct"
        write_json(path, payload)

        result = self.run_validator(tampered)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(tampered / "phase10/validation_report.json")
        self.assertIn("field_mismatch", {error["code"] for error in report["errors"]})


if __name__ == "__main__":
    unittest.main()
