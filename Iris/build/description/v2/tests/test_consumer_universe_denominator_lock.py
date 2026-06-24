from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/consumer_universe_denominator_lock"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class ConsumerUniverseDenominatorLockTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(TOOLS / "generate_consumer_universe_denominator_lock_artifacts.py")],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "consumer universe denominator lock generation failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_registry_locks_scalar_denominator_roles(self) -> None:
        registry = load_json(ROOT / "phase4/consumer_universe_denominator_registry.json")
        records = {row["denominator_id"]: row for row in registry["denominators"]}

        expected = {
            "DEN-AUDIT-RAW-OCCURRENCES": 198815,
            "DEN-AUDIT-ACCEPTED-CANDIDATES": 27869,
            "DEN-AUDIT-CORE-OCCURRENCES": 21174,
            "DEN-AUDIT-ADJACENT-SEED-OCCURRENCES": 6695,
            "DEN-AUDIT-EXECUTING-CONSUMERS": 1062,
            "DEN-AUDIT-CHANGE-REQUIRED": 311,
            "DEN-REBASELINE-CHANGE-NEEDED": 59,
            "DEN-REBASELINE-CONDITIONAL": 252,
            "DEN-NORMALIZED-APPLY-ELIGIBLE": 163,
            "DEN-READINESS-SANDBOX-MUTATION": 163,
            "DEN-NORMALIZED-NO-OP": 148,
            "DEN-NORMALIZED-MISSING-PATH": 125,
            "DEN-NORMALIZED-MISSING-APPLY-ELIGIBLE": 0,
            "DEN-AUDIT-CHANGE-FORBIDDEN": 27558,
            "DEN-RUNTIME-CURRENT-ENTRIES": 2105,
            "DEN-RUNTIME-ADOPTED-ROWS": 2084,
            "DEN-RUNTIME-UNADOPTED-ROWS": 21,
        }
        self.assertEqual(registry["denominator_count"], len(expected))
        for denominator_id, value in expected.items():
            self.assertIn(denominator_id, records)
            self.assertEqual(records[denominator_id]["value"], value)
            self.assertIsInstance(records[denominator_id]["value"], int)
            self.assertEqual(records[denominator_id]["authority_role"], "claim_boundary_governance_only")
            self.assertNotEqual(records[denominator_id]["source_granularity"], "unknown")

        self.assertIn("migrated_rows", records["DEN-AUDIT-CHANGE-REQUIRED"]["forbidden_claim_verbs"])
        self.assertIn("live_migration_completion", records["DEN-READINESS-SANDBOX-MUTATION"]["forbidden_claim_verbs"])
        self.assertIn("no_op_denominator", records["DEN-AUDIT-CHANGE-FORBIDDEN"]["forbidden_claim_verbs"])

    def test_relationships_separate_count_equality_from_row_identity(self) -> None:
        arithmetic = load_json(ROOT / "phase3/arithmetic_consistency_report.json")
        row_identity = load_json(ROOT / "phase3/row_identity_match_report.json")
        relation_graph = load_json(ROOT / "phase3/denominator_relation_graph.json")
        identity_rows = load_jsonl(ROOT / "phase3/cross_ledger_row_identity_mapping.jsonl")

        self.assertEqual(arithmetic["status"], "PASS")
        self.assertTrue(arithmetic["checks"]["59_plus_252_equals_311"])
        self.assertTrue(arithmetic["checks"]["163_plus_148_equals_311"])
        self.assertTrue(arithmetic["checks"]["2084_plus_21_equals_2105"])
        self.assertEqual(row_identity["status"], "PASS")
        self.assertEqual(row_identity["matched_count"], 163)
        self.assertFalse(row_identity["count_equal_only"])
        self.assertEqual(len(identity_rows), 163)
        self.assertTrue(all(row["identity_match_status"] == "MATCHED" for row in identity_rows))

        relation = {
            row["relation_id"]: row
            for row in relation_graph["relationships"]
        }["REL-NORMALIZED-APPLY-TO-READINESS-SANDBOX-MUTATION"]
        self.assertEqual(relation["status"], "LOCKED")
        self.assertEqual(relation["row_identity_match_status"], "MATCHED")

    def test_crosswalk_and_claim_guard_cover_inventory_only_counts(self) -> None:
        crosswalk_report = load_json(ROOT / "phase4/denominator_crosswalk_validation_report.json")
        inventory_only = load_json(ROOT / "phase4/inventory_only_guard_coverage_report.json")
        guard = load_json(ROOT / "phase5/claim_guard_test_report.json")
        negatives = load_jsonl(ROOT / "phase5/claim_guard_negative_fixtures.jsonl")

        self.assertEqual(crosswalk_report["status"], "PASS")
        self.assertEqual(crosswalk_report["crosswalk_row_count"], 311)
        self.assertEqual(crosswalk_report["matched_count"], 311)
        self.assertEqual(inventory_only["status"], "PASS")
        self.assertGreaterEqual(inventory_only["inventory_only_count"], 1)
        self.assertIn("DEN-AUDIT-RAW-OCCURRENCES", inventory_only["inventory_only_denominator_ids"])
        self.assertEqual(guard["status"], "PASS")
        self.assertTrue(all(row["observed_verdict"] == "REJECT" for row in negatives))

    def test_current_route_patch_records_live_required_gate_adoption(self) -> None:
        patch = load_json(ROOT / "phase6/current_route_required_validation_patch.json")
        validation = load_json(ROOT / "phase6/current_route_denominator_validation_report.json")
        sandbox = load_json(ROOT / "phase6/current_route_candidate_patch_sandbox_apply_restore_report.json")
        closure = load_json(ROOT / "phase6/current_route_closure_allowlist_regression_report.json")
        no_mutation = load_json(ROOT / "phase6/protected_surface_no_mutation_verdict.json")

        self.assertEqual(patch["status"], "adopted_required_gate")
        self.assertTrue(patch["patch_schema_valid"])
        self.assertTrue(patch["live_manifest_mutated"])
        self.assertTrue(patch["live_manifest_contains_required_artifact"])
        self.assertTrue(patch["live_manifest_contains_required_test"])
        self.assertEqual(validation["candidate_current_route_validation_status"], "patch_schema_validated")
        self.assertEqual(validation["required_gate_adoption_status"], "adopted_required_gate")
        self.assertTrue(validation["future_closeout_blocking_claim_allowed"])
        self.assertTrue(validation["live_manifest_contains_required_artifact"])
        self.assertTrue(validation["live_manifest_contains_required_test"])
        self.assertFalse(sandbox["sandbox_validation_run"])
        self.assertTrue(sandbox["live_manifest_mutated"])
        self.assertFalse(closure["this_round_tools_added_to_current_closure"])
        self.assertFalse(closure["this_round_tools_added_to_tooling_allowlist"])
        self.assertEqual(no_mutation["status"], "PASS")
        self.assertEqual(no_mutation["changed_count"], 0)

    def test_final_report_records_live_required_gate_adoption_without_canonical_seal(self) -> None:
        final = load_json(ROOT / "phase8/final_consumer_universe_denominator_lock_report.json")
        review = load_json(ROOT / "phase8/independent_review_status.json")
        closeout = (REPO / "docs/consumer_universe_denominator_lock_closeout.md").read_text(encoding="utf-8")

        self.assertEqual(final["machine_contract_status"], "PASS")
        self.assertEqual(final["governance_closeout_status"], "review_pending")
        self.assertTrue(final["complete_claim_allowed"])
        self.assertFalse(final["canonical_seal_allowed"])
        self.assertEqual(final["required_gate_adoption_status"], "adopted_required_gate")
        self.assertEqual(final["candidate_current_route_validation_status"], "patch_schema_validated")
        self.assertTrue(final["candidate_guard_claim_allowed"])
        self.assertTrue(final["future_closeout_blocking_claim_allowed"])
        self.assertTrue(final["live_manifest_mutated"])
        self.assertTrue(final["live_manifest_contains_required_artifact"])
        self.assertTrue(final["live_manifest_contains_required_test"])
        self.assertEqual(final["regenerate_twice_fingerprint_comparison"]["status"], "PASS")
        self.assertEqual(review["review_state"], "pending")
        self.assertFalse(review["materialized_by_this_round"])
        self.assertIn("Future closeout blocking is claimed only through the adopted current-route required gate", closeout)
        self.assertIn("not a canonical seal", closeout)


if __name__ == "__main__":
    unittest.main()
