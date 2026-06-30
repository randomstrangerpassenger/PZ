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
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal"
RUNNER = TOOLS / "run_dvf_3_3_required_artifact_disposition_seal.py"
VALIDATOR = TOOLS / "validate_dvf_3_3_required_artifact_disposition_seal.py"

sys.path.insert(0, str(TOOLS))

from dvf_3_3_required_artifact_disposition_seal_common import (  # noqa: E402
    ALLOWED_AXIS,
    ALLOWED_AXIS_DISPOSITION,
    ALLOWED_PASSABILITY,
    ALLOWED_PRESERVATION_RESULT,
    AUTO_SEAL_RULE_ID,
    negative_fixture_matrix,
    validate_rows,
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


class DvfRequiredArtifactDispositionSealTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tempdir = tempfile.TemporaryDirectory(prefix="dvf_required_artifact_disposition_")
        temp_root = Path(cls._tempdir.name)
        cls.root = temp_root / "evidence"
        cls.doc_root = temp_root / "docs"
        cls.runner_env = os.environ.copy()
        cls.runner_env["DVF_REQUIRED_ARTIFACT_DISPOSITION_EVIDENCE_ROOT"] = str(cls.root)
        cls.runner_env["DVF_REQUIRED_ARTIFACT_DISPOSITION_DOC_ROOT"] = str(cls.doc_root)
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--mode", "census"],
            cwd=REPO,
            env=cls.runner_env,
            text=True,
            capture_output=True,
            check=False,
        )
        final = cls.root / "phase6_closeout_claim_boundary/final_required_artifact_disposition_report.json"
        if not final.exists():
            raise AssertionError(
                "required artifact disposition seal generation did not create a final report\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )
        payload = load_json(final)
        census_skip_terminal = (
            payload.get("terminal_state") == "validation_failed"
            and payload.get("current_route_validation_state") == "SKIPPED"
        )
        if result.returncode != 0 and not census_skip_terminal:
            raise AssertionError(
                "required artifact disposition seal census generation failed unexpectedly\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    @classmethod
    def tearDownClass(cls) -> None:
        tempdir = getattr(cls, "_tempdir", None)
        if tempdir is not None:
            tempdir.cleanup()

    def test_live_manifest_denominator_and_ignored_coverage_are_separate(self) -> None:
        denominator = load_json(self.root / "phase0_readpoint_freeze/required_artifact_denominator.json")
        summary = load_json(self.root / "phase0_readpoint_freeze/required_artifact_vcs_summary.json")
        problem = load_json(self.root / "phase0_readpoint_freeze/problem_closure_denominator.json")
        ignored = load_json(self.root / "phase0_readpoint_freeze/ignored_diagnostic_coverage_denominator.json")

        self.assertEqual(denominator["status"], "PASS")
        self.assertEqual(denominator["required_artifact_count"], summary["vcs_tuple_count"])
        self.assertEqual(
            ignored["ignored_diagnostic_coverage_denominator_count"],
            len(set(ignored["paths"])),
        )
        self.assertEqual(problem["problem_closure_denominator_count"], len(set(problem["paths"])))
        self.assertTrue(summary["roadmap_premise_reconciliation"]["ignored_19_compared_to_ignore_rule_match_required"])
        self.assertTrue(summary["roadmap_premise_reconciliation"]["effectively_ignored_reported_as_separate_blocker_axis"])

    def test_schema_is_source_of_truth_and_rows_keep_fields_separate(self) -> None:
        schema = load_json(self.root / "phase1_policy_schema/disposition_schema.json")
        rows = load_jsonl(self.root / "phase6_closeout_claim_boundary/disposition_ledger.jsonl")

        self.assertEqual(schema["axis"], ALLOWED_AXIS)
        self.assertEqual(schema["axis_disposition"], ALLOWED_AXIS_DISPOSITION)
        self.assertEqual(schema["preservation_result"], ALLOWED_PRESERVATION_RESULT)
        self.assertEqual(schema["passability"], ALLOWED_PASSABILITY)
        self.assertTrue(schema["preservation_results_are_not_axis_dispositions"])
        self.assertTrue(rows)
        for row in rows:
            self.assertIn(row["axis"], schema["axis"])
            self.assertIn(row["axis_disposition"], schema["axis_disposition"])
            self.assertIn(row["preservation_result"], schema["preservation_result"])
            self.assertIn(row["passability"], schema["passability"])
            self.assertNotIn(row["axis_disposition"], schema["preservation_result"])

    def test_owner_rule_gate_controls_negative_exception_auto_disposition(self) -> None:
        owner_rule = load_json(self.root / "phase1_policy_schema/auto_seal_rule_ratification_validation_report.json")
        auto_report = load_json(self.root / "phase3_ignored_disposition/negative_exception_auto_disposition_report.json")
        final = load_json(self.root / "phase6_closeout_claim_boundary/final_required_artifact_disposition_report.json")
        rows = load_jsonl(self.root / "phase3_ignored_disposition/ignored_required_artifact_disposition_ledger.jsonl")
        candidates = [row for row in rows if row.get("auto_seal_rule_id") == AUTO_SEAL_RULE_ID]

        self.assertEqual(auto_report["negative_exception_candidate_count"], len(candidates))
        if owner_rule["owner_rule_ratification_binding_status"] == "PASS":
            self.assertEqual(final["auto_seal_rule_ratification_status"], "ratified")
            self.assertEqual(auto_report["negative_exception_auto_disposition_count"], len(candidates))
        else:
            self.assertIn(
                final["required_artifact_disposition_problem_status"],
                {"OWNER_PENDING", "SOLVED_WITH_MACHINE_BLOCKERS"},
            )
            self.assertIn(final["terminal_state"], {"owner_pending", "complete_with_blockers"})
            self.assertTrue(final["machine_pass_blocked"])
            self.assertEqual(auto_report["negative_exception_auto_disposition_count"], 0)
            self.assertTrue(all(row["passability"] == "owner_pending" for row in candidates))

    def test_negative_fixtures_and_validator_fail_closed(self) -> None:
        schema = load_json(self.root / "phase1_policy_schema/disposition_schema.json")
        matrix = load_json(self.root / "phase5_fail_closed_validation/negative_fixture_matrix.json")
        self.assertEqual(matrix["status"], "PASS")
        self.assertEqual(negative_fixture_matrix(schema)["status"], "PASS")

        bad_row = {
            "row_id": "unit-bad",
            "axis": "ignored",
            "axis_disposition": "diagnostic_only_preserved_by_tracking",
            "preservation_result": "tracked_original_preservation",
            "passability": "passable",
            "vcs_tuple": {
                "tracked": True,
                "untracked": False,
                "dirty": True,
                "ignore_rule_match": True,
                "ignore_rule_is_negative_exception": True,
                "ignore_active": False,
                "effectively_ignored": False,
            },
        }
        self.assertTrue(validate_rows([bad_row], schema=schema, owner_rule_binding_status="PASS"))

        result = subprocess.run(
            [sys.executable, "-B", str(VALIDATOR)],
            cwd=REPO,
            env=self.runner_env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_rejects_tampered_owner_input_vcs_preservation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dvf_required_artifact_disposition_tamper_") as temp:
            temp_root = Path(temp)
            tampered_evidence = temp_root / "evidence"
            tampered_docs = temp_root / "docs"
            shutil.copytree(self.root, tampered_evidence)
            shutil.copytree(self.doc_root, tampered_docs)
            owner_report = tampered_evidence / "phase6_closeout_claim_boundary/owner_input_record_vcs_preservation_report.json"
            payload = load_json(owner_report)
            payload["status"] = "FAIL"
            payload["owner_input_record_vcs_preservation_status"] = "FAIL"
            owner_report.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            env = os.environ.copy()
            env["DVF_REQUIRED_ARTIFACT_DISPOSITION_EVIDENCE_ROOT"] = str(tampered_evidence)
            env["DVF_REQUIRED_ARTIFACT_DISPOSITION_DOC_ROOT"] = str(tampered_docs)
            result = subprocess.run(
                [sys.executable, "-B", str(VALIDATOR)],
                cwd=REPO,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("FAIL", result.stdout + result.stderr)

    def test_parent_packet_is_hash_bound_and_non_authoritative(self) -> None:
        final = load_json(self.root / "phase6_closeout_claim_boundary/final_required_artifact_disposition_report.json")
        packet = load_json(self.root / "phase6_closeout_claim_boundary/parent_closure_input_packet.json")
        compatibility = load_json(self.root / "phase6_closeout_claim_boundary/parent_compatibility_contract.json")
        mapping = load_json(self.root / "phase6_closeout_claim_boundary/parent_terminal_state_mapping.json")

        self.assertEqual(packet["parent_round_id"], "dvf_3_3_current_route_authority_required_evidence_integrity_closure")
        self.assertEqual(packet["predecessor_round_id"], "dvf_3_3_required_artifact_disposition_seal")
        self.assertTrue(packet["parent_rerun_required"])
        self.assertTrue(packet["does_not_claim_parent_machine_pass"])
        for field in [
            "current_route_manifest_sha256",
            "required_artifact_denominator_sha256",
            "final_recensus_report_sha256",
            "disposition_ledger_sha256",
        ]:
            self.assertEqual(packet[field], compatibility[field])
        self.assertFalse(mapping["parent_machine_pass_claimed"])
        self.assertIn(final["terminal_state"], mapping["mappings"])
        self.assertIn("no_release_readiness", final["non_claims"])
        self.assertIn("no_runtime_chunk_replacement", final["non_claims"])


if __name__ == "__main__":
    unittest.main()
