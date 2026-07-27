from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.dvf_3_3_food_semantic.contracts import (
    load_json,
    load_jsonl,
)
from tools.build.dvf_3_3_food_semantic.curation_proposals import (
    record_exact_owner_batch_approvals,
    validate_batch_approvals,
)
from tools.build.dvf_3_3_food_semantic.curation_rework_resolution import (
    materialize_resolved_curation,
    write_rework_resolution_bundle,
)


ATTEMPT_ROOT = (
    V2_ROOT
    / "staging/dvf_3_3_food_semantic_facts_authority/"
    "attempts/attempt-0007"
)
PRIOR_AUTHORITY_ROOT = (
    ATTEMPT_ROOT
    / "post_implementation_authority/authority-execution-0001"
)
OWNER_DECISIONS = (
    V2_ROOT
    / "owner_inputs/dvf_3_3_food_semantic_facts_authority/"
    "owner_reserved_decisions.json"
)


class FoodSemanticCurationReworkResolutionTest(unittest.TestCase):
    def test_rework_resolution_is_narrow_pending_and_source_bound(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(dir=ATTEMPT_ROOT.parent) as temp_dir:
            proposal_root = Path(temp_dir) / "proposals"
            summary = write_rework_resolution_bundle(
                REPO_ROOT,
                ATTEMPT_ROOT,
                prior_authority_root=PRIOR_AUTHORITY_ROOT,
                output_root=proposal_root,
            )
            self.assertEqual(summary["validation_status"], "PASS")
            self.assertEqual(summary["target_count"], 2)
            self.assertEqual(summary["proposed_proposition_count"], 2)
            self.assertEqual(summary["needs_rework_count"], 0)
            self.assertFalse(summary["authority_effect"])
            proposals = load_jsonl(
                proposal_root
                / "curation_rework_resolution_proposals.jsonl"
            )
            self.assertEqual(
                [row["item_identity"] for row in proposals],
                ["Base.Comfrey", "Base.Plantain"],
            )
            self.assertTrue(
                all(
                    row["fact_axis"] == "ingredient_origin"
                    and row["fact_value"] == "plant"
                    and row["approval_status"]
                    == "pending_human_semantic_approval"
                    for row in proposals
                )
            )
            self.assertTrue(
                all(
                    row["reviewed_source_set"][1]["reviewed_fields"][
                        "categories"
                    ]
                    == ["MedicinalPlants"]
                    and row["reviewed_source_set"][0][
                        "reviewed_fields"
                    ]
                    == {"Type": "Normal"}
                    and row["reviewed_source_set"][2][
                        "reviewed_fields"
                    ]["category"]
                    == "Health"
                    for row in proposals
                )
            )
            validation = validate_batch_approvals(
                proposal_root,
                owner_decisions_path=OWNER_DECISIONS,
                require_all_approved=False,
            )
            self.assertEqual(validation["status"], "PENDING")
            self.assertEqual(validation["pending_batch_count"], 1)

    def test_approved_resolution_closes_rework_in_successor_execution(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(dir=ATTEMPT_ROOT.parent) as temp_dir:
            temp_root = Path(temp_dir)
            proposal_root = temp_root / "proposals"
            write_rework_resolution_bundle(
                REPO_ROOT,
                ATTEMPT_ROOT,
                prior_authority_root=PRIOR_AUTHORITY_ROOT,
                output_root=proposal_root,
            )
            receipt = record_exact_owner_batch_approvals(
                proposal_root,
                owner_decisions_path=OWNER_DECISIONS,
                approval_directive="fixture approval",
                approval_rationale=(
                    "Approve only the two exact plant-origin propositions."
                ),
                approval_time="2026-07-27T20:00:00+09:00",
            )
            self.assertEqual(receipt["approved_batch_count"], 1)
            self.assertEqual(receipt["approved_proposition_count"], 2)
            successor_root = temp_root / "authority-execution-0002"
            report = materialize_resolved_curation(
                proposal_root,
                prior_authority_root=PRIOR_AUTHORITY_ROOT,
                successor_authority_root=successor_root,
                owner_decisions_path=OWNER_DECISIONS,
            )
            self.assertEqual(report["status"], "PASS_COMPLETE")
            self.assertEqual(
                report["approved_curated_proposition_count"],
                238,
            )
            self.assertEqual(report["resolved_prior_rework_count"], 2)
            self.assertEqual(report["unresolved_rework_count"], 0)
            self.assertTrue(report["candidate_generation_authorized"])
            phase = successor_root / "phase8_curation"
            curated = load_jsonl(phase / "curated_fact_ledger.jsonl")
            approvals = load_jsonl(
                phase / "semantic_authority_approval_ledger.jsonl"
            )
            events = load_jsonl(phase / "curation_event_ledger.jsonl")
            self.assertEqual(len(curated), 238)
            self.assertEqual(len(approvals), 238)
            self.assertEqual(len(events), 718)
            self.assertEqual(
                load_jsonl(phase / "curation_rework_queue.jsonl"),
                [],
            )
            resolved = [
                row
                for row in curated
                if row["item_identity"]
                in {"Base.Comfrey", "Base.Plantain"}
            ]
            self.assertEqual(len(resolved), 2)
            self.assertTrue(
                all(
                    row["fact_field"] == "ingredient_origin"
                    and row["fact_value"] == "plant"
                    for row in resolved
                )
            )
            checkpoint = load_json(phase / "curation_checkpoint.json")
            self.assertEqual(checkpoint["accepted_count"], 238)
            self.assertEqual(checkpoint["rework_count"], 0)
            self.assertIsNone(checkpoint["next_canonical_cursor"])


if __name__ == "__main__":
    unittest.main()
