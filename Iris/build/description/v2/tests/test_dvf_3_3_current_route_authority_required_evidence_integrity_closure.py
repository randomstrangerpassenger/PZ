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
ROUND_ID = "dvf_3_3_current_route_authority_required_evidence_integrity_closure"
RUNNER = TOOLS / f"run_{ROUND_ID}.py"
VALIDATOR = TOOLS / f"validate_{ROUND_ID}.py"
DEFAULT_EVIDENCE_ROOT = REPO / "Iris/build/description/v2/staging" / ROUND_ID

sys.path.insert(0, str(TOOLS))
import dvf_3_3_current_route_authority_required_evidence_integrity_closure as closure  # noqa: E402


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class DvfCurrentRouteAuthorityRequiredEvidenceIntegrityClosureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tempdir = tempfile.TemporaryDirectory(prefix="dvf_parent_closure_")
        cls.root = Path(cls._tempdir.name) / "evidence"
        cls.env = os.environ.copy()
        cls.env["DVF_CURRENT_ROUTE_AUTHORITY_REQUIRED_EVIDENCE_INTEGRITY_CLOSURE_ROOT"] = str(cls.root)
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--mode", "scaffold"],
            cwd=REPO,
            env=cls.env,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "scaffold generation failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    @classmethod
    def tearDownClass(cls) -> None:
        tempdir = getattr(cls, "_tempdir", None)
        if tempdir is not None:
            tempdir.cleanup()

    def run_validator(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["DVF_CURRENT_ROUTE_AUTHORITY_REQUIRED_EVIDENCE_INTEGRITY_CLOSURE_ROOT"] = str(root)
        env["DVF_CURRENT_ROUTE_CLOSURE_SKIP_NESTED_FOCUSED"] = "1"
        return subprocess.run(
            [sys.executable, "-B", str(VALIDATOR), *args],
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

    def copy_complete_evidence(self, name: str) -> Path:
        final = DEFAULT_EVIDENCE_ROOT / "phase8/final_machine_report.json"
        if not final.exists():
            self.skipTest("complete parent evidence has not been generated in this checkout")
        target = Path(self._tempdir.name) / name
        shutil.copytree(DEFAULT_EVIDENCE_ROOT, target)
        return target

    def guard_errors(self, root: Path, callback) -> list[dict]:
        old_root = closure.EVIDENCE_ROOT
        try:
            closure.EVIDENCE_ROOT = root
            errors: list[dict] = []
            callback(errors)
            return errors
        finally:
            closure.EVIDENCE_ROOT = old_root

    def test_unsupported_mode_rejected(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--mode", "unsupported"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_scaffold_records_no_parent_machine_pass(self) -> None:
        scaffold = load_json(self.root / "phase_minus1/tooling_scaffold_report.json")
        matrix = load_json(self.root / "phase_minus1/ordered_command_matrix.json")

        self.assertEqual(scaffold["status"], "PASS")
        self.assertFalse(scaffold["parent_machine_pass_claimed"])
        self.assertTrue(scaffold["parent_recompute_required"])
        self.assertTrue(scaffold["phase0_entry_allowed"])
        self.assertEqual(scaffold["phase_minus1_role"], "pre-phase gate")
        self.assertEqual(scaffold["change_mapping_role"], "not_part_of_change_mapping")
        self.assertTrue(scaffold["phase_minus1_not_in_change_mapping"])
        self.assertEqual(scaffold["source_rendered_lua_bridge_runtime_package_mutation_count"], 0)
        self.assertEqual(
            matrix["command_sequence_id"],
            f"{ROUND_ID}_command_sequence_v1",
        )
        self.assertEqual(len(matrix["commands"]), 7)

    def test_scaffold_validator_accepts_isolated_root(self) -> None:
        result = self.run_validator(self.root, "--require-scaffold")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(self.root / "phase_minus1/validation_report.require_scaffold.json")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["error_count"], 0)

    def test_validator_rejects_scaffold_parent_pass_tamper(self) -> None:
        tampered = self.copy_evidence("tampered_parent_pass")
        path = tampered / "phase_minus1/tooling_scaffold_report.json"
        payload = load_json(path)
        payload["parent_machine_pass_claimed"] = True
        write_json(path, payload)

        result = self.run_validator(tampered, "--require-scaffold")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(tampered / "phase_minus1/validation_report.require_scaffold.json")
        self.assertIn("field_mismatch", {error["code"] for error in report["errors"]})

    def test_validator_rejects_command_order_tamper(self) -> None:
        tampered = self.copy_evidence("tampered_command_order")
        path = tampered / "phase_minus1/ordered_command_matrix.json"
        payload = load_json(path)
        payload["commands"][0]["command"] = "uv run python -B changed.py"
        write_json(path, payload)

        result = self.run_validator(tampered, "--require-scaffold")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(tampered / "phase_minus1/validation_report.require_scaffold.json")
        self.assertIn("command_order_violation", {error["code"] for error in report["errors"]})

    def test_complete_evidence_contract_when_present(self) -> None:
        final = DEFAULT_EVIDENCE_ROOT / "phase8/final_machine_report.json"
        if not final.exists():
            self.skipTest("complete parent evidence has not been generated in this checkout")
        payload = load_json(final)
        mapping = load_json(DEFAULT_EVIDENCE_ROOT / "phase_change_mapping_manifest.json")
        review = load_json(DEFAULT_EVIDENCE_ROOT / "phase8/primary_review_artifact_manifest.json")

        self.assertEqual(payload["status"], "machine_pass_governance_only")
        self.assertEqual(payload["top_doc_sync_state"], "owner_applied_and_validated")
        self.assertTrue(payload["top_doc_sync_pass_claimed"])
        self.assertTrue(payload["owner_applied_and_validated_claimed"])
        self.assertEqual(payload["top_doc_live_mutation_target_count"], 3)
        if payload["independent_review_gate"] == "PASS":
            self.assertEqual(payload["owner_seal_status"], "PASS")
            self.assertEqual(payload["canonical_seal_status"], "PASS")
            self.assertTrue(payload["canonical_seal_allowed"])
            self.assertEqual(payload["final_signoff_status"], "PASS")
        else:
            self.assertEqual(payload["independent_review_gate"], "BLOCKED")
            self.assertTrue(payload["canonical_review_pending"])
            self.assertTrue(payload["owner_seal_pending"])
            self.assertFalse(payload["canonical_seal_allowed"])
        self.assertFalse(payload["release_readiness_claimed"])
        self.assertFalse(payload["package_readiness_claimed"])
        self.assertEqual(mapping["literal_boundary_phrase"], "pre-phase gate / not part of change mapping")
        self.assertTrue(review["phase_change_mapping_manifest_included"])

    def test_complete_validator_recomputes_live_required_surface(self) -> None:
        tampered = self.copy_complete_evidence("tampered_vcs_surface")
        path = tampered / "phase5/vcs_required_surface_report.json"
        live_payload = load_json(path)
        payload = dict(live_payload)
        payload["required_artifact_count"] = 0
        write_json(path, payload)

        old_surface = closure.required_surface_report
        try:
            closure.required_surface_report = lambda: live_payload
            errors = self.guard_errors(tampered, closure.append_live_required_surface_errors)
        finally:
            closure.required_surface_report = old_surface
        self.assertIn("live_required_surface_recensus_mismatch", {error["code"] for error in errors})
        self.assertTrue((tampered / "phase8/live_vcs_required_surface_recensus_report.json").exists())

    def test_complete_validator_rejects_top_doc_not_claimed_without_omission(self) -> None:
        tampered = self.copy_complete_evidence("tampered_top_doc_not_claimed")
        final_path = tampered / "phase8/final_machine_report.json"
        final = load_json(final_path)
        final["top_doc_sync_state"] = "not_claimed"
        final.pop("omission_rationale_recorded", None)
        write_json(final_path, final)
        top_doc_path = tampered / "phase6/top_doc_sync_state.json"
        top_doc = load_json(top_doc_path)
        top_doc["top_doc_sync_state"] = "not_claimed"
        top_doc.pop("omission_rationale_recorded", None)
        write_json(top_doc_path, top_doc)

        errors = self.guard_errors(tampered, closure.append_no_overclaim_errors)
        self.assertIn("top_doc_state_violation", {error["code"] for error in errors})

    def test_complete_validator_rejects_command_matrix_binding_tamper(self) -> None:
        tampered = self.copy_complete_evidence("tampered_command_binding")
        path = tampered / "phase8/final_machine_report.json"
        payload = load_json(path)
        payload.pop("command_sequence_id", None)
        payload["command_matrix_bound"] = False
        write_json(path, payload)

        errors = self.guard_errors(tampered, closure.append_command_matrix_binding_errors)
        self.assertIn("command_matrix_binding_missing", {error["code"] for error in errors})

    def test_owner_reserved_tokens_cover_stable_codes(self) -> None:
        payload = load_json(DEFAULT_EVIDENCE_ROOT / "phase8/owner_reserved_interface_token_list.json")
        observed = {row["token"] for row in payload["rows"]}
        self.assertTrue(
            {
                "advisory_only",
                "parent_rerun_required",
                "parent_pass_substitution_forbidden",
                "predecessor_seal_ir_missing",
                "owner_reserved_interface_token",
                "command_order_violation",
            }.issubset(observed)
        )

    def test_negative_fixture_execution_report_records_observed_codes(self) -> None:
        payload = load_json(DEFAULT_EVIDENCE_ROOT / "phase3/negative_fixture_execution_report.json")
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["executed_fixture_count"], 6)
        for row in payload["fixtures"]:
            self.assertTrue(row["fixture_passed"], row)
            self.assertEqual(row["validator_exit_code"], 1, row)
            self.assertEqual(row["observed_code"], row["expected_code"], row)
            self.assertIn(row["expected_code"], row["observed_codes"], row)

    def test_hash_cycle_guard_detects_generated_evidence_hash_in_plan_text(self) -> None:
        complete = self.copy_complete_evidence("hash_cycle_guard")
        evidence_path = complete / "phase8/final_machine_report.json"
        digest = closure.normalized_sha(evidence_path)
        plan = Path(self._tempdir.name) / "synthetic_plan.md"
        plan.write_text(f"Generated evidence hash should not be here: {digest}\n", encoding="utf-8")

        old_root = closure.EVIDENCE_ROOT
        old_plan = closure.PLAN_DOC
        try:
            closure.EVIDENCE_ROOT = complete
            closure.PLAN_DOC = plan
            errors: list[dict] = []
            closure.append_hash_cycle_errors(errors)
        finally:
            closure.EVIDENCE_ROOT = old_root
            closure.PLAN_DOC = old_plan

        self.assertIn("hash_cycle_self_reference", {error["code"] for error in errors})


if __name__ == "__main__":
    unittest.main()
