from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair"
SCRIPT = REPO / "Iris/build/description/v2/tools/build/dvf_3_3_current_route_baseline_source_overlay_repair.py"
REQUIRED_VALIDATIONS = REPO / "Iris/_docs/round3/current_route_required_validations.json"
PRIMARY_PROBLEM7_PLAN = "docs/dvf_3_3_current_route_baseline_source_overlay_repair_problem7_plan.md"
PREDECESSOR_CONTRACT_PLAN = "docs/dvf_3_3_current_route_baseline_source_overlay_repair_plan.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class DvfCurrentRouteBaselineSourceOverlayRepairTest(unittest.TestCase):
    live_manifest_before: dict | None = None
    live_manifest_after: dict | None = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.live_manifest_before = load_json(REQUIRED_VALIDATIONS) if REQUIRED_VALIDATIONS.exists() else None
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        cls.live_manifest_after = load_json(REQUIRED_VALIDATIONS) if REQUIRED_VALIDATIONS.exists() else None

    def test_final_packet_is_sealed_after_independent_review(self) -> None:
        report = load_json(ROOT / "phase7/final_current_route_baseline_source_overlay_repair_predecessor_report.json")
        handoff = load_json(ROOT / "phase6/handoff_blocker_report.json")
        readiness = load_json(ROOT / "phase7/downstream_repair_readiness_status.json")

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["closeout_state"], "partial")
        self.assertTrue(report["bounded_repair_packet_complete"])
        self.assertEqual(report["remaining_repair_packet_blockers"], [])
        self.assertTrue(report["implementation_plan_ready"])
        self.assertTrue(report["sealed_contract_packet_emitted"])
        self.assertFalse(report["executable_handoff_emitted"])
        self.assertEqual(report["blockers"], [])
        self.assertTrue(report["checks"]["non_claude_independent_adversarial_review"])
        self.assertNotIn("live_materialization_reconnect_requires_separate_authorization", report["blockers"])
        self.assertTrue(handoff["execution_authorized"])
        self.assertFalse(handoff["requires_separate_authorization"])
        self.assertTrue(handoff["this_runner_forbidden_to_write"])
        self.assertTrue(handoff["implementation_plan_ready"])
        self.assertEqual(readiness["contract_packet_status"], "sealed")
        self.assertTrue(readiness["implementation_plan_ready"])
        self.assertTrue(readiness["bounded_repair_packet_complete"])
        self.assertEqual(readiness["remaining_work_for_repair_packet"], [])
        self.assertTrue((ROOT / "phase7/current_route_baseline_repair_contract_packet.sealed.md").exists())

    def test_plan_provenance_separates_problem7_primary_from_predecessor_contract(self) -> None:
        provenance = load_json(ROOT / "phase0/plan_input_provenance_reconciliation.json")
        fingerprints = load_json(ROOT / "phase1/fingerprint_manifest.json")
        report = load_json(ROOT / "phase7/final_current_route_baseline_source_overlay_repair_predecessor_report.json")

        self.assertEqual(provenance["schema_version"], "dvf-3-3-current-route-baseline-plan-provenance-v2")
        self.assertTrue(provenance["stable_plan_provenance_reconciled"])
        self.assertEqual(provenance["canonical_plan_role"], "primary_problem7_plan")
        self.assertEqual(provenance["canonical_plan_artifact_path"], PRIMARY_PROBLEM7_PLAN)
        self.assertEqual(provenance["predecessor_contract_plan_role"], "predecessor_contract_plan")
        self.assertEqual(provenance["predecessor_contract_plan_artifact_path"], PREDECESSOR_CONTRACT_PLAN)
        self.assertFalse(provenance["predecessor_contract_plan_execution_authority"])
        self.assertEqual(
            provenance["plan_path_relationship"],
            "primary_problem7_plan_is_canonical; predecessor_contract_plan_is_supporting_contract_only",
        )
        self.assertEqual(
            provenance["plan_roles"]["primary_problem7_plan"]["path"],
            PRIMARY_PROBLEM7_PLAN,
        )
        self.assertEqual(
            provenance["plan_roles"]["primary_problem7_plan"]["authority"],
            "canonical_problem_plan",
        )
        self.assertTrue(provenance["plan_roles"]["primary_problem7_plan"]["execution_authority"])
        self.assertEqual(
            provenance["plan_roles"]["predecessor_contract_plan"]["path"],
            PREDECESSOR_CONTRACT_PLAN,
        )
        self.assertEqual(
            provenance["plan_roles"]["predecessor_contract_plan"]["authority"],
            "predecessor_contract_only",
        )
        self.assertFalse(provenance["plan_roles"]["predecessor_contract_plan"]["execution_authority"])
        self.assertEqual(fingerprints["files"]["plan"], fingerprints["files"]["primary_problem7_plan"])
        self.assertNotEqual(fingerprints["files"]["primary_problem7_plan"], fingerprints["files"]["predecessor_contract_plan"])
        self.assertTrue(report["checks"]["stable_plan_provenance"])
        self.assertEqual(report["plan_roles"]["primary_problem7_plan"]["path"], PRIMARY_PROBLEM7_PLAN)
        self.assertEqual(report["plan_roles"]["predecessor_contract_plan"]["path"], PREDECESSOR_CONTRACT_PLAN)

    def test_live_vnext_successor_baseline_matches_manifest_after_authorized_reconnect(self) -> None:
        intake = load_json(ROOT / "phase1/current_route_failure_intake_report.json")
        drift = load_json(ROOT / "phase1/live_manifest_vs_actual_hash_drift_report.json")
        selected = load_json(ROOT / "phase2/selected_source_candidate_gate.json")
        disposition = (ROOT / "phase2/current_facts_6_disposition_lock.md").read_text(encoding="utf-8")

        self.assertEqual(intake["status"], "PASS")
        self.assertEqual(intake["facts"]["actual_count"], 2105)
        self.assertEqual(intake["decisions"]["actual_count"], 2105)
        self.assertEqual(intake["overlay"]["actual_count"], 2105)
        self.assertEqual(drift["drift_count"], 0)
        self.assertEqual(selected["status"], "PASS")
        self.assertEqual(selected["selected_source_candidate"], "live_vnext_successor_baseline_authority")
        self.assertEqual(selected["facts_count"], 2105)
        self.assertEqual(selected["decisions_count"], 2105)
        self.assertFalse(selected["source_reconnect_required"])
        self.assertTrue(selected["live_matches_manifest"])
        self.assertIn("superseded", disposition)

    def test_base_canopener_is_fixture_residue_with_selected_tinopener_alias(self) -> None:
        report = load_json(ROOT / "phase2/base_canopener_fixture_leak_report.json")
        rows = {row["item_id"]: row for row in report["focused_rows"]}

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["classification"], "fixture_leak_removed_by_authorized_reconnect")
        self.assertFalse(report["overlay_patch_needed"])
        self.assertEqual(report["alias_map"]["Base.CanOpener"], "Base.TinOpener")
        self.assertFalse(rows["Base.CanOpener"]["in_live_facts"])
        self.assertFalse(rows["Base.CanOpener"]["in_selected_source"])
        self.assertTrue(rows["Base.CanOpener"]["runtime_equivalent_in_runtime"])
        self.assertTrue(rows["Base.TinOpener"]["in_selected_source"])
        self.assertTrue(rows["Base.TinOpener"]["in_current_overlay"])

    def test_alias_normalized_identity_and_overlay_coverage_pass(self) -> None:
        identity = load_json(ROOT / "phase3/source_runtime_2105_cross_attestation_report.json")
        diffs = load_jsonl(ROOT / "phase3/source_runtime_row_identity_diff.jsonl")
        coverage = load_json(ROOT / "phase4/body_source_overlay_coverage_report.json")
        default_path = load_json(ROOT / "phase4/current_overlay_default_path_contract.json")
        guard = load_json(ROOT / "phase5/current_authority_overlay_input_guard_contract.json")

        self.assertEqual(identity["status"], "PASS")
        self.assertEqual(identity["source_count"], 2105)
        self.assertEqual(identity["rendered_count"], 2105)
        self.assertEqual(identity["runtime_count"], 2105)
        self.assertEqual(identity["normalized_missing_in_rendered_count"], 0)
        self.assertEqual(identity["normalized_extra_in_rendered_count"], 0)
        self.assertTrue(identity["rendered_runtime_key_parity"])
        self.assertEqual(diffs, [])
        self.assertEqual(coverage["status"], "PASS")
        self.assertEqual(coverage["adopted_row_count"], 2084)
        self.assertEqual(coverage["gap_count"], 0)
        self.assertFalse(default_path["current_route_silent_staging_fallback_allowed"])
        self.assertFalse(default_path["compose_default_constant_is_staging"])
        self.assertTrue(default_path["compose_default_constant_is_current_overlay"])
        self.assertEqual(guard["status"], "PASS")
        self.assertIn("overlay_path", guard["guarded_input_keys"])

    def test_diagnostic_runner_does_not_mutate_live_manifest_or_unscoped_targets(self) -> None:
        no_mutation = load_json(ROOT / "phase1/protected_surface_no_mutation_report.json")
        allowlist = load_json(ROOT / "phase6/exact_target_allowlist_draft.json")

        self.assertEqual(self.live_manifest_after, self.live_manifest_before)
        self.assertEqual(no_mutation["status"], "PASS")
        self.assertEqual(no_mutation["changed_count"], 0)
        self.assertTrue(allowlist["execution_authorized"])
        self.assertEqual(
            [target["path"] for target in allowlist["live_write_targets"]],
            [
                "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
                "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl",
            ],
        )

    def test_authorized_live_reconnect_report_exists_and_is_bounded(self) -> None:
        report = load_json(ROOT / "phase8_authorized_live_reconnect/authorized_live_source_reconnect_report.json")

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["allowlist_validation"]["status"], "PASS")
        self.assertEqual(report["authorized_scope"], "live_facts_decisions_only")
        self.assertEqual(
            report["live_write_targets"],
            [
                "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
                "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl",
            ],
        )
        self.assertEqual(
            sorted(report["allowlist_validation"]["authorized_target_paths"]),
            sorted(report["live_write_targets"]),
        )
        self.assertEqual(
            [row["snapshot_row_count"] for row in report["immutable_initial_prewrite_snapshots"]],
            [6, 6],
        )
        self.assertTrue(report["forbidden_targets_unchanged"])
        self.assertEqual(
            report["forbidden_live_targets_not_written"],
            [
                "Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl",
                "Iris/build/description/v2/output/dvf_3_3_rendered.json",
                "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks",
                "Iris/build/package/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks",
            ],
        )
        self.assertTrue(all(row["sha256_matches_manifest"] for row in report["postwrite_target_records"]))


if __name__ == "__main__":
    unittest.main()
