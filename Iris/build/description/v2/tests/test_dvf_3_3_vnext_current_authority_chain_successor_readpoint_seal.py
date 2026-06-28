from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal"
RUNNER = TOOLS / "run_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py"
VALIDATOR = TOOLS / "validate_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py"
INNER_CURRENT_ROUTE = os.environ.get("DVF_SUCCESSOR_READPOINT_INNER_CURRENT_ROUTE") == "1"

sys.path.insert(0, str(TOOLS))

from dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal import validate_artifacts  # noqa: E402


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class DvfVnextCurrentAuthorityChainSuccessorReadpointSealTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if INNER_CURRENT_ROUTE:
            return
        final_report = ROOT / "phase7/final_successor_readpoint_governance_seal_report.json"
        if final_report.exists():
            payload = load_json(final_report)
            required_fields = {
                "canonical_seal_blockers",
                "canonical_seal_blocker_count",
                "final_token_signoff_status",
                "canonical_audit_adoption_sequence_status",
            }
            if (
                payload.get("status") == "PASS"
                and payload.get("machine_contract_status") == "PASS"
                and required_fields.issubset(payload)
                and payload.get("canonical_seal_allowed") is True
            ):
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
                "successor readpoint seal runner failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_phase0_preflight_and_axis_contract_pass(self) -> None:
        preflight = load_json(ROOT / "phase0/preflight_current_checkout_readiness_report.json")
        contract = load_json(ROOT / "phase0/report_field_contract.json")
        axis = load_json(ROOT / "phase2/axis_exhaustiveness_report.json")
        non_supersession = load_json(ROOT / "phase2/axis_token_non_supersession_report.json")

        self.assertEqual(preflight["status"], "PASS")
        self.assertEqual(preflight["source"]["row_count"], 2105)
        self.assertEqual(preflight["rendered"]["entry_count"], 2105)
        self.assertEqual(preflight["runtime"]["entry_count"], 2105)
        self.assertEqual(contract["status"], "PASS")
        self.assertEqual(contract["round_id"], "dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal")
        self.assertEqual(axis["status"], "PASS")
        self.assertEqual(axis["unclassified_count"], 0)
        self.assertEqual(axis["ambiguous_count"], 0)
        self.assertTrue(non_supersession["this_round_maps_tokens_only"])
        self.assertFalse(non_supersession["sealed_token_supersession_claim"])

    def test_rowkey_and_package_binding_pass(self) -> None:
        uniqueness = load_json(ROOT / "phase3/source_item_id_uniqueness_report.json")
        equality = load_json(ROOT / "phase3/intra_source_keyset_equality_report.json")
        transform = load_json(ROOT / "phase3/key_transform_rule_report.json")
        rowkey = load_json(ROOT / "phase3/chain_rowkey_identity_report.json")
        package = load_json(ROOT / "phase3/package_peer_scan_canonical_minimum.json")

        self.assertEqual(uniqueness["status"], "PASS")
        self.assertEqual(uniqueness["duplicate_source_key_count"], 0)
        self.assertEqual(equality["status"], "PASS")
        self.assertEqual(equality["mismatch_count"], 0)
        self.assertEqual(transform["transform"], "identity")
        self.assertEqual(rowkey["status"], "PASS")
        self.assertEqual(rowkey["rowkey_identity_status"], "pass")
        self.assertEqual(package["status"], "PASS")
        self.assertFalse(package["package_zip_preservation_required_for_canonical"])

    def test_live_manifest_adoption_is_additive_and_governance_only(self) -> None:
        adoption = load_json(ROOT / "phase6/live_required_manifest_adoption_report.json")
        diff = load_json(ROOT / "phase6/manifest_additive_diff_report.json")
        closure = load_json(ROOT / "phase6/current_route_tooling_closure_impact_report.json")
        dependency = load_json(ROOT / "phase6/recursion_avoidance_validation_report.json")
        live = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")

        self.assertEqual(adoption["status"], "PASS")
        self.assertEqual(adoption["required_gate_adoption_status"], "adopted_required_gate")
        self.assertEqual(adoption["canonical_audit_adoption_sequence_status"], "already_adopted_revalidation")
        self.assertEqual(adoption["candidate_patch_sequence_evidence_level"], "already_adopted_revalidation")
        self.assertFalse(adoption["pre_live_manifest_mutation_sequence_proven"])
        self.assertEqual(adoption["removed_existing_entries"], 0)
        self.assertEqual(adoption["modified_existing_entries"], 0)
        self.assertFalse(adoption["source_rendered_lua_runtime_package_authority_mutated"])
        self.assertTrue(diff["already_adopted_revalidation"])
        self.assertEqual(diff["candidate_patch_sequence_evidence_level"], "already_adopted_revalidation")
        self.assertEqual(diff["removed_existing_entries"], 0)
        self.assertEqual(diff["modified_existing_entries"], 0)
        self.assertEqual(closure["active_core_count"], 12)
        self.assertFalse(closure["new_tooling_promoted_to_current_core"])
        self.assertEqual(dependency["self_referential_cycle_count"], 0)

        required_tests = {row["test_id"] for row in live["required_tests"]}
        for test_id in [
            (
                "test_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal."
                "DvfVnextCurrentAuthorityChainSuccessorReadpointSealTest."
                "test_phase0_preflight_and_axis_contract_pass"
            ),
            (
                "test_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal."
                "DvfVnextCurrentAuthorityChainSuccessorReadpointSealTest."
                "test_rowkey_and_package_binding_pass"
            ),
            (
                "test_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal."
                "DvfVnextCurrentAuthorityChainSuccessorReadpointSealTest."
                "test_live_manifest_adoption_is_additive_and_governance_only"
            ),
        ]:
            self.assertIn(test_id, required_tests)

    def test_final_packet_records_canonical_gate_status(self) -> None:
        if INNER_CURRENT_ROUTE:
            self.assertTrue((ROOT / "phase6/live_required_manifest_adoption_report.json").exists())
            return
        final = load_json(ROOT / "phase7/final_successor_readpoint_governance_seal_report.json")
        review = load_json(ROOT / "phase7/independent_review_artifact_hash_report.json")
        owner = load_json(ROOT / "phase7/owner_seal_record.json")
        signoff = load_json(ROOT / "phase7/final_token_signoff_record.json")

        self.assertEqual(final["status"], "PASS")
        self.assertEqual(final["machine_contract_status"], "PASS")
        self.assertEqual(final["closeout_state"], "successor_readpoint_governance_seal_complete")
        self.assertTrue(final["canonical_seal_allowed"])
        self.assertEqual(final["canonical_seal_status"], "canonical_seal_allowed")
        self.assertEqual(final["canonical_seal_blocker_count"], 0)
        self.assertEqual(final["canonical_seal_blockers"], [])
        self.assertEqual(final["vcs_preservation_proof_status"], "PASS")
        self.assertEqual(final["independent_review_status"], "PASS")
        self.assertEqual(final["owner_decision_status"], "approved")
        self.assertEqual(final["owner_seal_status"], "sealed")
        self.assertEqual(final["final_token_signoff_status"], "signed")
        self.assertEqual(review["canonical_external_review_state"], "passed")
        self.assertTrue(review["reviewer_identity_present"])
        self.assertFalse(review["owner_approval_substitutes_for_review"])
        self.assertEqual(owner["owner_decision_status"], "approved")
        self.assertEqual(owner["owner_seal_status"], "sealed")
        self.assertEqual(signoff["final_token_signoff_status"], "signed")
        self.assertIn("no_release_readiness", final["non_claims"])

    def test_validator_accepts_machine_governance_packet(self) -> None:
        if INNER_CURRENT_ROUTE:
            self.assertTrue((ROOT / "phase0/report_field_contract.json").exists())
            return
        report, ok = validate_artifacts(require_complete=True, write_report=False)
        self.assertTrue(ok, report["errors"])

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
