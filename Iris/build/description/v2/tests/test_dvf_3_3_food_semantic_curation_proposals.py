from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.dvf_3_3_food_semantic.contracts import (
    FoodSemanticError,
    load_json,
    load_jsonl,
)
from tools.build.dvf_3_3_food_semantic.curation_proposals import (
    assert_curation_authority_sink,
    build_curation_proposals,
    build_review_batches,
    build_source_contexts,
    materialize_approved_curation,
    record_exact_owner_batch_approvals,
    source_context_diagnostics,
    validate_batch_approvals,
)


ATTEMPT_ROOT = (
    V2_ROOT
    / "staging/dvf_3_3_food_semantic_facts_authority/"
    "attempts/attempt-0007"
)
PROPOSAL_ROOT = (
    V2_ROOT
    / "owner_inputs/dvf_3_3_food_semantic_facts_authority/"
    "curation_proposals"
)
OWNER_DECISIONS = (
    V2_ROOT
    / "owner_inputs/dvf_3_3_food_semantic_facts_authority/"
    "owner_reserved_decisions.json"
)


def write_exact_batch_approvals(
    proposal_root: Path, *, blank_metadata: bool = False
) -> None:
    for path in sorted((proposal_root / "review_batches").glob("*.json")):
        batch = load_json(path)
        batch["owner_approval"] = {
            "approval_state": "approved",
            "approver_identity": (
                "   " if blank_metadata else "repository_owner"
            ),
            "approval_time": (
                "" if blank_metadata else "2026-07-27T00:00:00+09:00"
            ),
            "proposal_content_sha256": batch[
                "proposal_content_sha256"
            ],
            "approved_proposition_ids": [
                row["proposition_id"]
                for row in batch["members"]
                if row["disposition"] == "proposed"
            ],
            "accepted_needs_rework_items": [
                row["item_identity"]
                for row in batch["members"]
                if row["disposition"] == "needs_rework"
            ],
            "rationale": (
                "" if blank_metadata else "test exact bounded batch approval"
            ),
        }
        path.write_text(
            json.dumps(
                batch,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )


def copy_pending_proposal_bundle(target: Path) -> Path:
    shutil.copytree(PROPOSAL_ROOT, target)
    for path in sorted((target / "review_batches").glob("*.json")):
        batch = load_json(path)
        batch["owner_approval"] = None
        path.write_text(
            json.dumps(
                batch,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    receipt_path = target / "owner_curation_approval_receipt.json"
    receipt_path.unlink(missing_ok=True)
    return target


class FoodSemanticCurationProposalTest(unittest.TestCase):
    def test_source_contexts_cover_exact_queue_without_forbidden_consumption(
        self,
    ) -> None:
        contexts = build_source_contexts(REPO_ROOT, ATTEMPT_ROOT)
        report = source_context_diagnostics(contexts)
        self.assertEqual(report["target_count"], 238)
        self.assertEqual(report["missing_reviewed_context_count"], 0)
        self.assertEqual(report["forbidden_context_field_consumed_count"], 0)
        self.assertEqual(
            report["forbidden_context_operation_consumed_count"], 0
        )

    def test_proposals_are_bounded_and_fail_closed_on_non_food_sources(
        self,
    ) -> None:
        proposals, report = build_curation_proposals(
            REPO_ROOT, ATTEMPT_ROOT
        )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["proposal_row_count"], 238)
        self.assertEqual(report["proposed_proposition_count"], 236)
        self.assertEqual(report["needs_rework_count"], 2)
        self.assertEqual(
            report["needs_rework_items"],
            ["Base.Comfrey", "Base.Plantain"],
        )
        self.assertTrue(
            all(
                row["approval_status"]
                == "pending_human_semantic_approval"
                for row in proposals
            )
        )

    def test_review_batches_preserve_existing_D6_membership(self) -> None:
        proposals, _ = build_curation_proposals(REPO_ROOT, ATTEMPT_ROOT)
        batches = build_review_batches(
            ATTEMPT_ROOT,
            proposals,
            bundle_sha256="a" * 64,
        )
        self.assertEqual(len(batches), 10)
        self.assertEqual(
            sum(batch["batch"]["member_count"] for batch in batches), 238
        )
        self.assertLessEqual(
            max(batch["batch"]["member_count"] for batch in batches), 24
        )

    def test_unapproved_batches_cannot_materialize_authority(self) -> None:
        with tempfile.TemporaryDirectory(dir=ATTEMPT_ROOT.parent) as temp_dir:
            temp_root = Path(temp_dir)
            proposal_root = copy_pending_proposal_bundle(
                temp_root / "proposals"
            )
            report = validate_batch_approvals(
                proposal_root,
                owner_decisions_path=OWNER_DECISIONS,
                require_all_approved=False,
            )
            self.assertEqual(report["status"], "PENDING")
            self.assertEqual(report["pending_batch_count"], 10)
            self.assertEqual(report["approved_batch_count"], 0)
            with self.assertRaises(FoodSemanticError):
                materialize_approved_curation(
                    proposal_root,
                    temp_root / "authority",
                    owner_decisions_path=OWNER_DECISIONS,
                )

    def test_exact_batch_approvals_materialize_partial_append_only_state(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(dir=ATTEMPT_ROOT.parent) as temp_dir:
            temp_root = Path(temp_dir)
            proposal_root = copy_pending_proposal_bundle(
                temp_root / "proposals"
            )
            write_exact_batch_approvals(proposal_root)
            authority_root = temp_root / "authority"
            report = materialize_approved_curation(
                proposal_root,
                authority_root,
                owner_decisions_path=OWNER_DECISIONS,
            )
            self.assertEqual(report["status"], "PASS_WITH_REWORK")
            self.assertEqual(report["approved_curated_proposition_count"], 236)
            self.assertEqual(report["unresolved_rework_count"], 2)
            self.assertFalse(report["candidate_generation_authorized"])
            phase = authority_root / "phase8_curation"
            self.assertEqual(
                len(load_jsonl(phase / "curated_fact_ledger.jsonl")), 236
            )
            self.assertEqual(
                len(load_jsonl(phase / "curation_rework_queue.jsonl")), 2
            )
            self.assertEqual(
                len(load_jsonl(phase / "curation_event_ledger.jsonl")), 714
            )
            checkpoint = load_json(phase / "curation_checkpoint.json")
            self.assertEqual(checkpoint["accepted_count"], 236)
            self.assertEqual(checkpoint["rework_count"], 2)
            self.assertIsNotNone(checkpoint["next_canonical_cursor"])

    def test_owner_directive_records_exact_bounded_batch_approvals(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(dir=ATTEMPT_ROOT.parent) as temp_dir:
            temp_root = Path(temp_dir)
            proposal_root = copy_pending_proposal_bundle(
                temp_root / "proposals"
            )
            receipt = record_exact_owner_batch_approvals(
                proposal_root,
                owner_decisions_path=OWNER_DECISIONS,
                approval_directive="승인",
                approval_rationale=(
                    "Owner approves every exact proposition and accepts every "
                    "needs-rework disposition in each bounded D6 batch."
                ),
                approval_time="2026-07-27T19:00:00+09:00",
            )
            self.assertEqual(receipt["validation_status"], "PASS")
            self.assertEqual(receipt["approved_batch_count"], 10)
            self.assertEqual(receipt["approved_proposition_count"], 236)
            self.assertEqual(receipt["accepted_needs_rework_count"], 2)
            self.assertEqual(receipt["approval_directive"], "승인")
            validation = validate_batch_approvals(
                proposal_root,
                owner_decisions_path=OWNER_DECISIONS,
                require_all_approved=True,
            )
            self.assertEqual(validation["status"], "PASS")
            self.assertEqual(validation["approved_batch_count"], 10)
            self.assertTrue(
                (
                    proposal_root / "owner_curation_approval_receipt.json"
                ).is_file()
            )

    def test_blank_approval_metadata_cannot_materialize_authority(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(dir=ATTEMPT_ROOT.parent) as temp_dir:
            temp_root = Path(temp_dir)
            proposal_root = copy_pending_proposal_bundle(
                temp_root / "proposals"
            )
            write_exact_batch_approvals(
                proposal_root,
                blank_metadata=True,
            )
            validation = validate_batch_approvals(
                proposal_root,
                owner_decisions_path=OWNER_DECISIONS,
                require_all_approved=True,
            )
            self.assertEqual(validation["status"], "BLOCKED")
            self.assertEqual(validation["approved_batch_count"], 0)
            self.assertEqual(validation["invalid_batch_count"], 10)
            self.assertTrue(
                all(
                    "approver_identity_blank_or_invalid" in row["errors"]
                    and "approval_time_blank_or_invalid" in row["errors"]
                    and "approval_rationale_blank_or_invalid" in row["errors"]
                    for row in validation["batch_results"]
                )
            )
            authority_root = temp_root / "authority"
            with self.assertRaises(FoodSemanticError):
                materialize_approved_curation(
                    proposal_root,
                    authority_root,
                    owner_decisions_path=OWNER_DECISIONS,
                )
            self.assertFalse((authority_root / "phase8_curation").exists())

    def test_authority_sink_is_attempt_local_and_rejects_protected_root(
        self,
    ) -> None:
        protected_roots = [
            REPO_ROOT / "Iris/build/description/v2/data",
            REPO_ROOT / "Iris/build/description/v2/output",
            REPO_ROOT / "Iris/media/lua",
            REPO_ROOT / "Iris/Iris/media/lua",
            REPO_ROOT / "Iris/build/description/v2/package",
        ]
        for protected_root in protected_roots:
            with self.subTest(protected_root=protected_root):
                with self.assertRaises(FoodSemanticError):
                    assert_curation_authority_sink(protected_root)

        staging = V2_ROOT / "staging"
        with tempfile.TemporaryDirectory(dir=staging) as temp_dir:
            temp_root = Path(temp_dir)
            proposal_root = copy_pending_proposal_bundle(
                temp_root / "proposals"
            )
            write_exact_batch_approvals(proposal_root)
            authority_root = temp_root / "outside-attempt-authority"
            with self.assertRaises(FoodSemanticError):
                materialize_approved_curation(
                    proposal_root,
                    authority_root,
                    owner_decisions_path=OWNER_DECISIONS,
                )
            self.assertFalse((authority_root / "phase8_curation").exists())


if __name__ == "__main__":
    unittest.main()
