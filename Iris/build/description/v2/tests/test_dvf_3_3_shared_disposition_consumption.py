from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption"
SCRIPT = TOOLS / "run_dvf_3_3_shared_disposition_consumption.py"

sys.path.insert(0, str(TOOLS))

from dvf_3_3_shared_disposition_consumption_common import classify_consumption_record, validate_all  # noqa: E402


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class SharedDispositionConsumptionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--mode", "all"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "shared disposition consumption generation failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_phase1_census_is_bounded_and_covers_sealed_axis_tokens(self) -> None:
        predicate = load_json(ROOT / "phase1/bounded_census_predicate.json")
        token_set = load_json(ROOT / "phase1/sealed_axis_token_set.json")
        zero = load_json(ROOT / "phase1/zero_token_promotion_report.json")
        unclassified = load_json(ROOT / "phase1/unclassified_surface_report.json")
        census = load_jsonl(ROOT / "phase1/consumption_census_ledger.jsonl")

        self.assertEqual(predicate["status"], "PASS")
        self.assertFalse(predicate["raw_numeric_occurrence_is_authority"])
        self.assertEqual(token_set["status"], "PASS")
        self.assertEqual(token_set["token_count"], 20)
        self.assertTrue(
            {row["coverage_status"] for row in token_set["tokens"]}.issubset(
                {"COVERED", "COVERED_BY_SEALED_VALUE_TABLE"}
            )
        )
        self.assertIn("promoted_ratio", zero)
        self.assertIn("excluded_ratio", zero)
        self.assertEqual(unclassified["unclassified_surface_count"], 0)
        self.assertTrue(census)
        self.assertTrue(all(row["occurrence_kind"] == "role_bearing_disposition_occurrence" for row in census))

    def test_phase2_packet_preserves_terminal_split_and_sealed_sources(self) -> None:
        packet = load_json(ROOT / "phase2/shared_disposition_packet.json")
        sealed = load_json(ROOT / "phase2/sealed_report_set.json")
        forbidden = load_json(ROOT / "phase2/forbidden_direct_read_set.json")
        values = load_json(ROOT / "phase2/value_resolution_table.json")

        self.assertEqual(packet["status"], "candidate")
        self.assertEqual(packet["review_status"], "review_pass")
        self.assertEqual(packet["row_count"], 1062)
        self.assertEqual(packet["terminal_counts"]["migrated_count"], 153)
        self.assertEqual(packet["terminal_counts"]["no_op_count"], 268)
        self.assertEqual(packet["terminal_counts"]["diagnostic_only_count"], 3)
        self.assertEqual(packet["terminal_counts"]["historical_only_count"], 638)
        self.assertEqual(sealed["status"], "PASS")
        self.assertEqual(
            {row["path"] for row in sealed["sealed_value_sources"]}.intersection(
                {row["path"] for row in forbidden["forbidden_direct_reads"]}
            ),
            set(),
        )
        self.assertEqual(values["status"], "PASS")
        predecessor_rows = [row for row in values["rows"] if row["token"] in {"2105", "2084", "21"}]
        self.assertTrue(all(row["not_current_debt"] for row in predecessor_rows))

    def test_phase3_negative_fixtures_are_detected_without_leaking_into_current_scan(self) -> None:
        fixture_report = load_json(ROOT / "phase3/negative_fixture_containment_report.json")
        raw_report = load_json(ROOT / "phase3/raw_authority_read_report.json")
        divergence = load_json(ROOT / "phase3/divergence_report.json")

        self.assertEqual(fixture_report["status"], "PASS")
        self.assertEqual(fixture_report["leakage_count"], 0)
        self.assertTrue(all(row["status"] == "PASS" for row in fixture_report["fixtures"]))
        self.assertEqual(raw_report["RAW_AUTHORITY_READ"], 0)
        self.assertEqual(divergence["divergence_count"], 0)

        self.assertIn(
            "RAW_AUTHORITY_READ",
            classify_consumption_record(
                {
                    "path": "Iris/build/description/v2/staging/2105_baseline_consumption_audit/classified_ledger.jsonl",
                    "authority_role": "current_execution_authority",
                }
            ),
        )
        self.assertIn(
            "VALUE_DIVERGENCE",
            classify_consumption_record({"denominator_id": "DEN-AUDIT-EXECUTING-CONSUMERS", "value": 1063}),
        )
        self.assertIn("PREDECESSOR_REENTRY", classify_consumption_record({"token": "2105", "lifecycle_role": "current_debt"}))

    def test_phase4_and_phase5_record_live_required_gate_adoption(self) -> None:
        no_op = load_json(ROOT / "phase4/no_op_realignment_report.json")
        no_dual = load_json(ROOT / "phase4/no_dual_authority_read_report.json")
        protected = load_json(ROOT / "phase4/protected_surface_no_mutation_report.json")
        candidate = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.shared_disposition_candidate.json")
        live_manifest = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")
        closure = load_json(ROOT / "phase5/current_route_closure_allowlist_report.json")
        integration = load_json(ROOT / "phase5/current_route_integration_report.json")

        self.assertEqual(no_op["status"], "PASS")
        self.assertFalse(no_op["adapter_required"])
        self.assertEqual(no_dual["DUAL_AUTHORITY_READ"], 0)
        self.assertEqual(protected["changed_count"], 0)
        self.assertEqual(candidate["status"], "superseded_by_live_required_gate")
        self.assertTrue(candidate["live_manifest_contains_required_gate"])
        self.assertFalse(candidate["live_manifest_mutated"])
        self.assertTrue(
            any(
                row["path"]
                == "Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase7/final_shared_disposition_consumption_report.json"
                for row in live_manifest["required_artifacts"]
            )
        )
        self.assertTrue(
            any(
                row["test_id"]
                == (
                    "test_dvf_3_3_shared_disposition_consumption."
                    "SharedDispositionConsumptionTest.test_final_report_records_live_required_gate_adoption"
                )
                and row["required"]
                for row in live_manifest["required_tests"]
            )
        )
        self.assertEqual(closure["current_core_closure_count"], 12)
        self.assertLessEqual(closure["current_route_allowed_tooling_count"], 1)
        self.assertFalse(closure["new_shared_disposition_tooling_silently_promoted"])
        self.assertEqual(integration["adoption_state"], "adopted_required_gate")
        self.assertTrue(integration["live_manifest_contains_required_gate"])

    def test_docs_and_final_report_preserve_claim_boundary(self) -> None:
        forbidden = load_json(ROOT / "phase6/forbidden_claim_scan_report.json")
        final = load_json(ROOT / "phase7/final_shared_disposition_consumption_report.json")
        verdict = load_json(ROOT / "phase7/final_claim_boundary_verdict.json")
        policy = (REPO / "docs/dvf_3_3_shared_disposition_consumption_policy.md").read_text(encoding="utf-8")

        self.assertEqual(forbidden["forbidden_claim_count"], 0)
        self.assertEqual(final["status"], "PASS")
        self.assertEqual(final["closeout_state"], "complete_adopted")
        self.assertEqual(final["current_route_required_validation_adoption_state"], "adopted_required_gate")
        self.assertEqual(final["independent_review_status"], "review_pass")
        self.assertTrue(final["live_required_validation_manifest_mutated"])
        self.assertFalse(final["live_required_validation_manifest_mutated_by_generator"])
        self.assertTrue(final["live_required_validation_manifest_contains_required_gate"])
        self.assertIn("does_not_close_separate_closeout_reentry_guard_seal_problem", final["non_claims"])
        self.assertFalse(verdict["separate_closeout_reentry_guard_seal_closed"])
        self.assertTrue(verdict["live_required_validation_adopted"])
        self.assertIn("not live migration completion", policy)

    def test_final_report_records_live_required_gate_adoption(self) -> None:
        final = load_json(ROOT / "phase7/final_shared_disposition_consumption_report.json")
        adoption = load_json(ROOT / "phase7/adoption_decision_report.json")

        self.assertEqual(adoption["owner_adoption_status"], "adopted_required_gate")
        self.assertTrue(adoption["live_required_validation_manifest_contains_required_gate"])
        self.assertEqual(final["closeout_state"], "complete_adopted")
        self.assertEqual(final["owner_adoption_status"], "adopted_required_gate")

    def test_validator_accepts_complete_adopted_state(self) -> None:
        report, ok = validate_all(require_complete=True, write_report=False)

        self.assertTrue(ok, report["errors"])


if __name__ == "__main__":
    unittest.main()
