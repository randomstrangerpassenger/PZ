from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization"
TOOLS = REPO / "Iris/build/description/v2/tools/build"
NORMALIZATION_VALIDATOR = TOOLS / "validate_dvf_3_3_consumer_migration_input_normalization.py"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def load_negative_helper_probe() -> dict:
    result = subprocess.run(
        [sys.executable, "-B", str(NORMALIZATION_VALIDATOR), "--probe-negative-helpers"],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "negative helper subprocess probe failed"
            f"\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return json.loads(result.stdout)


class DvfConsumerMigrationInputNormalizationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        scripts = [
            "generate_dvf_3_3_consumer_migration_input_contract.py",
            "generate_dvf_3_3_consumer_migration_eligibility_matrix.py",
            "generate_dvf_3_3_missing_path_disposition_ledger.py",
            "validate_dvf_3_3_consumer_migration_anchor_relocation.py",
            "generate_dvf_3_3_authority_role_migration_rule_seed.py",
            "generate_dvf_3_3_downstream_command_surface_compatibility_manifest.py",
            "generate_dvf_3_3_consumer_migration_reconciled_input_manifest.py",
            "validate_dvf_3_3_consumer_migration_input_normalization.py",
        ]
        for script in scripts:
            result = subprocess.run(
                [sys.executable, "-B", str(TOOLS / script)],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode != 0:
                raise AssertionError(f"{script} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

    def test_phase0_freezes_source_membership_and_scope(self) -> None:
        fingerprint = load_json(ROOT / "phase0/source_matrix_fingerprint_report.json")
        membership = load_json(ROOT / "phase0/source_membership_reconciliation.json")
        scope = load_json(ROOT / "phase0/implementation_scope_boundary.json")

        self.assertEqual(fingerprint["status"], "PASS")
        self.assertEqual(membership["status"], "PASS")
        self.assertEqual(membership["audit_change_required_count"], 311)
        self.assertEqual(membership["execution_change_required_count"], 311)
        self.assertEqual(membership["audit_only_count"], 0)
        self.assertEqual(membership["execution_only_count"], 0)
        self.assertEqual(scope["implementation_allowed_scope"], "core_input_normalization_only")
        self.assertFalse(scope["consumer_migration_execution_allowed"])
        self.assertFalse(scope["current_cutover_allowed"])

    def test_phase1_terminal_disposition_contract(self) -> None:
        summary = load_json(ROOT / "phase1/eligibility_matrix_summary.json")
        row_ids = load_json(ROOT / "phase1/normalized_row_id_set_report.json")

        self.assertEqual(summary["status"], "PASS")
        self.assertEqual(summary["total_normalized_rows"], 311)
        self.assertEqual(summary["terminal_disposition_counts"], {"actual_apply_eligible": 163, "no_op": 148})
        self.assertEqual(summary["apply_eligible_count"], 163)
        self.assertEqual(summary["diff_countable_count"], 163)
        self.assertEqual(summary["blocked_row_count"], 0)
        self.assertEqual(row_ids["row_id_duplicate_count"], 0)

    def test_phase2_missing_paths_are_non_apply_and_not_diffs(self) -> None:
        summary = load_json(ROOT / "phase2/missing_path_disposition_summary.json")
        zero = load_json(ROOT / "phase2/missing_apply_eligible_zero_proof.json")
        preview = load_jsonl(ROOT / "phase2/missing_required_path_disposition_ledger.readiness_schema_preview.jsonl")

        self.assertEqual(summary["status"], "PASS")
        self.assertEqual(summary["missing_path_row_count"], 125)
        self.assertEqual(summary["known_missing_plan_path_rows"], 125)
        self.assertEqual(summary["missing_apply_eligible_row_count"], 0)
        self.assertEqual(zero["missing_diff_countable_row_count"], 0)
        self.assertEqual(len(preview), 125)
        self.assertTrue(all(row["readiness_missing_path_disposition"] == "no_op_non_apply" for row in preview))

    def test_phase3_anchor_relocation_is_fresh_and_non_ambiguous(self) -> None:
        report = load_json(ROOT / "phase3/anchor_relocation_validation_report.json")
        freshness = load_json(ROOT / "phase3/anchor_freshness_binding_report.json")

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["unresolved_count"], 0)
        self.assertEqual(report["ambiguous_count"], 0)
        self.assertEqual(report["anchor_relocation_counts"]["missing_path_non_apply"], 125)
        self.assertEqual(freshness["status"], "PASS")
        self.assertEqual(freshness["apply_eligible_rows_with_target_file_hash"], 163)
        self.assertEqual(freshness["apply_eligible_rows_with_bounded_context_hash"], 163)

    def test_phase4_rule_seed_is_authority_role_not_numeric_replacement(self) -> None:
        summary = load_json(ROOT / "phase4/authority_role_rule_seed_summary.json")
        coverage = load_json(ROOT / "phase4/rule_seed_coverage.json")
        rules = load_jsonl(ROOT / "phase4/authority_role_migration_rule_seed.jsonl")

        self.assertEqual(summary["status"], "PASS")
        self.assertEqual(summary["actual_apply_eligible_row_count"], 163)
        self.assertEqual(summary["rule_seed_row_count"], 163)
        self.assertEqual(summary["numeric_replacement_rule_count"], 0)
        self.assertEqual(coverage["missing_apply_eligible_rule_count"], 0)
        self.assertTrue(all(rule["operation_kind"] == "authority_role_migration" for rule in rules))
        self.assertTrue(all(rule["numeric_replacement_allowed"] is False for rule in rules))
        self.assertTrue(all(rule["normalization_rule_seed_only"] is True for rule in rules))

    def test_phase5_future_targets_are_target_only_and_source_bound(self) -> None:
        binding = load_json(ROOT / "phase5/compatibility_source_binding.json")
        command_contract = load_json(ROOT / "phase5/command_surface_mapping.for_current_cutover.target_contract.json")
        tool_contract = load_json(ROOT / "phase5/tool_contract_compatibility_manifest.target_contract.json")
        target_map = load_json(ROOT / "phase5/readiness_artifact_target_map.json")

        self.assertEqual(binding["status"], "PASS")
        self.assertTrue(all(row["mandatory_source_satisfied"] for row in binding["source_rows"]))
        for row in [command_contract["future_target"], tool_contract["future_target"], *target_map["target_rows"]]:
            self.assertEqual(row["path_kind"], "future_readiness_target")
            self.assertFalse(row["materialized_by_this_round"])
            self.assertTrue(row["target_only"])
            self.assertFalse(row["source_authority"])
            self.assertEqual(row["stale_future_target_behavior"], "fail_until_reconciled")
        self.assertTrue(all(row["capability_level_requirement_only"] for row in target_map["capability_level_rows"]))

    def test_phase6_and_final_report_keep_claim_axes_separate(self) -> None:
        manifest = load_json(ROOT / "phase6/consumer_migration_reconciled_input_manifest.json")
        final = load_json(ROOT / "phase8/final_normalization_contract_report.json")
        raw_guard = load_json(ROOT / "phase7/raw_input_direct_consumption_guard_report.json")
        no_mutation = load_json(ROOT / "phase7/protected_surface_no_mutation_verdict.json")

        self.assertEqual(manifest["verdict"], "PASS")
        self.assertTrue(manifest["handoff_usable"])
        self.assertEqual(manifest["handoff_usage_scope"], "downstream_tooling_readiness_input_only")
        self.assertEqual(manifest["actual_diff_ledger_path_kind"], "future_readiness_target")
        self.assertFalse(manifest["actual_diff_ledger_materialized_by_this_round"])
        self.assertFalse(manifest["actual_diff_ledger_source_authority"])
        self.assertEqual(final["machine_contract_status"], "PASS")
        self.assertEqual(final["governance_closeout_status"], "review_pending")
        self.assertFalse(final["complete_claim_allowed"])
        self.assertTrue(final["handoff_usable"])
        self.assertEqual(raw_guard["status"], "PASS")
        self.assertEqual(no_mutation["status"], "PASS")
        self.assertEqual(no_mutation["changed_count"], 0)

    def test_closeout_and_handoff_do_not_overclaim_execution(self) -> None:
        closeout = (REPO / "docs/dvf_3_3_vnext_consumer_migration_input_normalization_closeout.md").read_text(
            encoding="utf-8"
        )
        handoff = (REPO / "docs/dvf_3_3_vnext_consumer_migration_input_normalization_handoff_packet.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("does not claim consumer migration completion", closeout)
        self.assertIn("not migration execution or cutover authorization", handoff)
        self.assertIn("consumer_migration_reconciled_input_manifest.json", handoff)
        self.assertIn("Do not consume raw", handoff)

    def test_negative_helpers_keep_fail_loud_classifications(self) -> None:
        payload = load_negative_helper_probe()
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["terminal_disposition"], "blocked")
        self.assertEqual(payload["blocked_class"], "blocked_non_apply")
        self.assertEqual(payload["blocked_reason"], "unknown_terminal_disposition")

        ambiguous = payload["ambiguous_anchor"]
        self.assertEqual(ambiguous["result"], "ambiguous")

        deterministic = payload["deterministic_anchor"]
        self.assertEqual(deterministic["result"], "relocated_deterministically")
        self.assertEqual(deterministic["basis"], "nearest_tie_lowest_line_deterministic")


if __name__ == "__main__":
    unittest.main()
