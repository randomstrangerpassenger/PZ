from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication"
SCRIPT = TOOLS / "run_dvf_3_3_terminal_disposition_adjudication.py"

sys.path.insert(0, str(TOOLS))

from dvf_3_3_terminal_disposition_adjudication_common import (  # noqa: E402
    default_independent_review_status,
    run_all,
    sha256_file,
    validate_all,
    validate_independent_review_status,
    validate_rollup_children,
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class TerminalDispositionAdjudicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--mode", "generate"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "terminal disposition generation failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_universe_binding_uses_executing_member_rows(self) -> None:
        manifest = load_json(ROOT / "phase1/terminal_consumer_universe_manifest.json")
        denominator = load_json(ROOT / "phase1/terminal_consumer_universe_denominator_report.json")
        decision = load_json(ROOT / "phase1/universe_unit_author_decision.json")

        self.assertEqual(manifest["member_count"], 1062)
        self.assertEqual(denominator["status"], "PASS")
        self.assertEqual(denominator["source_predicate_split"], {"conditional": 111, "no": 902, "yes": 49})
        self.assertEqual(decision["unit"], "executing_consumer_member_row")
        self.assertIn("2105", decision["substitute_denominators_rejected"])
        self.assertIn("311", decision["substitute_denominators_rejected"])
        self.assertIn("unique_file_path", decision["substitute_units_rejected"])

    def test_terminal_ledger_covers_all_members_with_positive_evidence(self) -> None:
        ledger = load_jsonl(ROOT / "phase3/terminal_disposition_ledger.jsonl")
        counts = load_json(ROOT / "phase3/terminal_disposition_counts.json")
        evidence = load_json(ROOT / "phase3/terminal_disposition_evidence_binding_report.json")

        self.assertEqual(len(ledger), 1062)
        self.assertEqual(counts["migrated_count"], 153)
        self.assertEqual(counts["no_op_count"], 268)
        self.assertEqual(counts["diagnostic_only_count"], 3)
        self.assertEqual(counts["historical_only_count"], 638)
        self.assertEqual(counts["blocked_count"], 0)
        self.assertEqual(counts["conditional_count"], 0)
        self.assertEqual(evidence["status"], "PASS")
        self.assertTrue(all(row["schema_version"] == "dvf-3-3-terminal-member-v1" for row in ledger))
        self.assertTrue(all(row["terminal_consumer_universe_id"] for row in ledger))
        self.assertTrue(all(row["used_identity_resolver"].endswith("resolve_member_identity_v1") for row in ledger))
        self.assertTrue(all(row["used_validation_core"].endswith("validate_terminal_records_v1") for row in ledger))
        self.assertTrue(all(row["projection_basis"] == "positive_member_row_evidence" for row in ledger))
        self.assertFalse(any(row["lack_of_migration_evidence_used_as_reason"] for row in ledger))

    def test_policy_preserves_vocabulary_and_reason_enums(self) -> None:
        schema = load_json(ROOT / "phase2/terminal_disposition_schema.json")
        crosswalk = load_json(ROOT / "phase2/audit_classification_terminal_crosswalk.json")
        ledger = load_jsonl(ROOT / "phase3/terminal_disposition_ledger.jsonl")

        self.assertEqual(schema["terminal_dispositions"], ["migrated", "no-op", "diagnostic-only", "historical-only"])
        self.assertIn("blocked", schema["non_terminal_states"])
        self.assertEqual(crosswalk["status"], "PASS")
        for row in ledger:
            if row["terminal_disposition"] == "migrated":
                self.assertEqual(row["migrated_evidence_class"], "prior_cutover_authority_role_migration_evidence")
                self.assertIsNone(row["terminal_reason_code"])
            else:
                self.assertIsNotNone(row["terminal_reason_code"])

    def test_residue_drain_down_keeps_predicate_axes_separate(self) -> None:
        zero = load_json(ROOT / "phase4/blocked_conditional_zero_verdict.json")
        reconciliation = load_json(ROOT / "phase4/predicate_vs_normalization_reconciliation_report.json")

        self.assertEqual(zero["status"], "PASS")
        self.assertEqual(zero["blocked_count"], 0)
        self.assertEqual(zero["conditional_count"], 0)
        self.assertTrue(reconciliation["global_predicate_axis"]["59_plus_252_equals_311"])
        self.assertTrue(reconciliation["normalization_axis"]["163_plus_148_equals_311"])
        self.assertTrue(reconciliation["bound_universe_axis"]["49_plus_111_plus_902_equals_1062"])
        self.assertFalse(reconciliation["axis_substitution_allowed"])

    def test_final_closeout_matches_independent_review_status(self) -> None:
        final = load_json(ROOT / "phase5/final_terminal_disposition_machine_report.json")
        closeout = load_json(ROOT / "phase6/final_terminal_disposition_closeout_report.json")
        review = load_json(ROOT / "phase6/independent_review_status.json")
        owner = load_json(ROOT / "phase6/owner_adoption_record.json")
        patch = load_json(ROOT / "phase5/current_route_required_validations.candidate_patch.json")
        no_mutation = load_json(ROOT / "phase5/protected_surface_no_mutation_verdict.json")
        closeout_text = (REPO / "docs/dvf_3_3_terminal_disposition_adjudication_closeout.md").read_text(encoding="utf-8")

        self.assertEqual(final["status"], "PASS")
        self.assertEqual(final["machine_contract_status"], "PASS")
        self.assertEqual(final["closeout_state"], "machine_complete_review_pending")
        self.assertFalse(final["canonical_complete"])
        self.assertIn(review["verdict"], {"review_pending", "review_pass"})
        if review["verdict"] == "review_pass":
            self.assertEqual(closeout["closeout_state"], "canonical_complete")
            self.assertTrue(closeout["canonical_complete"])
            self.assertTrue(review["canonical_complete_allowed"])
        else:
            self.assertEqual(closeout["closeout_state"], "machine_complete_review_pending")
            self.assertFalse(closeout["canonical_complete"])
            self.assertFalse(review["canonical_complete_allowed"])
        self.assertEqual(owner["owner_adoption_status"], "not_adopted")
        self.assertFalse(owner["owner_adoption_replaces_independent_review"])
        self.assertEqual(patch["adoption_status"], "not_adopted")
        self.assertFalse(patch["live_manifest_mutated"])
        self.assertEqual(no_mutation["status"], "PASS")
        self.assertEqual(no_mutation["changed_count"], 0)
        self.assertIn("no release readiness", closeout_text)
        self.assertIn("no source/rendered/runtime/package mutation", closeout_text)

    def test_independent_review_pass_with_hashes_is_valid(self) -> None:
        artifact = "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase3/terminal_disposition_counts.json"
        review = {
            "reviewed_artifacts": [artifact],
            "reviewed_hashes": {artifact: sha256_file(REPO / artifact)},
            "reviewer_identity_or_label": "independent-reviewer-fixture",
            "verdict": "review_pass",
            "timestamp": "2026-06-19T00:00:00+09:00",
            "claim_boundary_acknowledgement": True,
            "independent_review_status": "review_pass",
            "canonical_complete_allowed": True,
        }

        self.assertEqual(validate_independent_review_status(review), [])

    def test_independent_review_pass_requires_reviewer_hashes_and_claim_boundary(self) -> None:
        review = {
            "reviewed_artifacts": [],
            "reviewed_hashes": {},
            "reviewer_identity_or_label": "",
            "verdict": "review_pass",
            "timestamp": "2026-06-19T00:00:00+09:00",
            "claim_boundary_acknowledgement": False,
            "independent_review_status": "review_pass",
            "canonical_complete_allowed": False,
        }
        errors = validate_independent_review_status(review)
        codes = {error["code"] for error in errors}

        self.assertIn("review_pass_missing_reviewer", codes)
        self.assertIn("review_pass_missing_claim_boundary_acknowledgement", codes)
        self.assertIn("review_pass_canonical_not_allowed", codes)
        self.assertIn("review_pass_missing_reviewed_artifacts", codes)
        self.assertIn("review_pass_missing_reviewed_hashes", codes)

    def test_review_pass_promotion_workflow_validates(self) -> None:
        review_path = ROOT / "phase6/independent_review_status.json"
        original_review_text = review_path.read_text(encoding="utf-8")
        review_path.write_text(
            json.dumps(default_independent_review_status(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        run_all()
        validate_all(require_complete=True)
        run_all()
        artifacts = [
            "docs/dvf_3_3_terminal_disposition_adjudication_plan.md",
            "docs/dvf_3_3_terminal_disposition_adjudication_closeout.md",
            "docs/dvf_3_3_terminal_disposition_claim_boundary.md",
            "docs/dvf_3_3_terminal_disposition_policy.md",
            "docs/dvf_3_3_terminal_disposition_ledger_packet.md",
            "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase0/required_validation_commands.json",
            "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase1/terminal_consumer_universe_manifest.json",
            "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase1/terminal_consumer_universe_denominator_report.json",
            "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase3/terminal_disposition_counts.json",
            "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase3/terminal_disposition_ledger.jsonl",
            "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase5/final_terminal_disposition_machine_report.json",
            "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase5/terminal_disposition_validation_report.json",
            "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase6/independent_review_status.json",
            "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase6/independent_review_artifact_hash_report.json",
            "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase6/final_terminal_disposition_closeout_report.json",
            "Iris/build/description/v2/tools/build/dvf_3_3_terminal_disposition_adjudication_common.py",
            "Iris/build/description/v2/tests/test_terminal_disposition_adjudication.py",
            "uv.toml",
            ".gitignore",
        ]
        review = {
            "schema_version": "dvf-3-3-terminal-independent-review-status-v1",
            "generated_at": "2026-06-19T00:00:00+09:00",
            "reviewed_artifacts": artifacts,
            "reviewed_hashes": {artifact: sha256_file(REPO / artifact) for artifact in artifacts},
            "reviewer_identity_or_label": "independent-reviewer-fixture",
            "verdict": "review_pass",
            "timestamp": "2026-06-19T00:00:00+09:00",
            "claim_boundary_acknowledgement": True,
            "independent_review_status": "review_pass",
            "canonical_complete_allowed": True,
        }

        try:
            review_path.write_text(json.dumps(review, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            run_all()
            closeout = load_json(ROOT / "phase6/final_terminal_disposition_closeout_report.json")
            report, ok = validate_all(require_complete=True)

            self.assertEqual(closeout["closeout_state"], "canonical_complete")
            self.assertTrue(closeout["canonical_complete"])
            self.assertEqual(closeout["independent_review_status"], "review_pass")
            self.assertTrue(ok, report["errors"])
            hash_report = load_json(ROOT / "phase6/independent_review_artifact_hash_report.json")
            rewritten = {row["normalized_artifact"] for row in hash_report["rows"] if row["hash_relation"] == "promotion_rewritten"}
            self.assertEqual(hash_report["status"], "PASS")
            self.assertIn("docs/dvf_3_3_terminal_disposition_adjudication_closeout.md", rewritten)
            self.assertIn("docs/dvf_3_3_terminal_disposition_ledger_packet.md", rewritten)
            self.assertIn(
                "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase5/final_terminal_disposition_machine_report.json",
                rewritten,
            )
            self.assertIn(
                "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase6/final_terminal_disposition_closeout_report.json",
                rewritten,
            )
            self_referential = {
                row["normalized_artifact"]
                for row in hash_report["rows"]
                if row["hash_relation"] == "self_referential_attestation"
            }
            self.assertIn(
                "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase6/independent_review_artifact_hash_report.json",
                self_referential,
            )
            validation_rewritten = {
                row["normalized_artifact"]
                for row in hash_report["rows"]
                if row["hash_relation"] == "validation_rewritten_attestation"
            }
            self.assertIn(
                "Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase5/terminal_disposition_validation_report.json",
                validation_rewritten,
            )
            self.assertEqual(hash_report["validation_rewritten_attestation_count"], 1)
        finally:
            review_path.write_text(original_review_text, encoding="utf-8")
            run_all()

    def test_consumer_rollup_rejects_mixed_child_residue(self) -> None:
        ledger = load_jsonl(ROOT / "phase3/terminal_disposition_ledger.jsonl")
        children = [copy.deepcopy(ledger[0]), copy.deepcopy(ledger[1])]
        children[1]["terminal_disposition"] = "blocked"
        errors = validate_rollup_children(children)
        self.assertTrue(any(error["code"] == "rollup_child_residue_hidden" for error in errors))

    def test_consumer_rollup_rejects_blocked_child_occurrence(self) -> None:
        child = copy.deepcopy(load_jsonl(ROOT / "phase3/terminal_disposition_ledger.jsonl")[0])
        child["terminal_disposition"] = "blocked"
        errors = validate_rollup_children([child])
        self.assertTrue(any(error["code"] == "rollup_child_residue_hidden" for error in errors))

    def test_consumer_rollup_rejects_missing_child_positive_reason(self) -> None:
        child = next(row for row in load_jsonl(ROOT / "phase3/terminal_disposition_ledger.jsonl") if row["terminal_disposition"] == "no-op")
        child = copy.deepcopy(child)
        child["terminal_reason_code"] = None
        errors = validate_rollup_children([child])
        self.assertTrue(any(error["code"] == "rollup_child_missing_positive_reason" for error in errors))

    def test_consumer_rollup_rejects_hidden_child_occurrence_residue(self) -> None:
        child = copy.deepcopy(load_jsonl(ROOT / "phase3/terminal_disposition_ledger.jsonl")[0])
        child["hidden_by_rollup"] = True
        errors = validate_rollup_children([child])
        self.assertTrue(any(error["code"] == "hidden_child_occurrence_residue" for error in errors))


if __name__ == "__main__":
    unittest.main()
