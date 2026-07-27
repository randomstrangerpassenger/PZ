from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.dvf_3_3_food_semantic.contracts import (
    FoodSemanticError,
    canonical_proposition_id,
    load_json,
    load_jsonl,
    relative_posix,
    sha256_file,
    write_json,
    write_jsonl,
)
from tools.build.dvf_3_3_food_semantic.curation_proposals import (
    record_exact_owner_batch_approvals,
    review_batch_proposal_hash,
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


def write_fixture_external_review(proposal_root: Path) -> Path:
    summary_path = proposal_root / "curation_proposal_summary.json"
    summary = load_json(summary_path)
    review_path = (
        proposal_root / "external_rework_resolution_review.pass.json"
    )
    write_json(
        review_path,
        {
            "schema_version": "test-fixture-v1",
            "verdict": "PASS",
            "reviewer_identity": "Codex Reviewer",
            "reviewer_is_implementation_author": False,
            "finding_counts": {
                "critical": 0,
                "important": 0,
                "minor": 0,
            },
            "semantic_scope_verdict": "PASS",
            "owner_approval_allowed": True,
            "materialization_after_exact_owner_approval_allowed": True,
            "authority_effect_before_owner_approval": False,
            "reviewed_proposal_summary_sha256": sha256_file(summary_path),
            "reviewed_proposal_ledger_sha256": summary[
                "proposal_ledger_sha256"
            ],
        },
        write_once=False,
    )
    return review_path


class FoodSemanticCurationReworkResolutionTest(unittest.TestCase):
    def test_public_review_batch_hash_contract_is_deterministic(
        self,
    ) -> None:
        batch_path = next(
            (
                V2_ROOT
                / "owner_inputs/dvf_3_3_food_semantic_facts_authority/"
                "curation_rework_resolution_0001/review_batches"
            ).glob("*.json")
        )
        batch = load_json(batch_path)
        first = review_batch_proposal_hash(batch)
        second = review_batch_proposal_hash(deepcopy(batch))
        self.assertEqual(first, second)
        approval_only = deepcopy(batch)
        approval_only["owner_approval"] = {"excluded": True}
        self.assertEqual(
            review_batch_proposal_hash(approval_only),
            first,
        )
        changed = deepcopy(batch)
        changed["members"][0]["fact_value"] = "animal"
        self.assertNotEqual(review_batch_proposal_hash(changed), first)

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
            write_fixture_external_review(proposal_root)
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

    def test_regeneration_preserves_exact_owner_approval_and_receipt(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(dir=ATTEMPT_ROOT.parent) as temp_dir:
            proposal_root = Path(temp_dir) / "proposals"
            write_rework_resolution_bundle(
                REPO_ROOT,
                ATTEMPT_ROOT,
                prior_authority_root=PRIOR_AUTHORITY_ROOT,
                output_root=proposal_root,
            )
            record_exact_owner_batch_approvals(
                proposal_root,
                owner_decisions_path=OWNER_DECISIONS,
                approval_directive="fixture approval",
                approval_rationale=(
                    "Approve only the two exact plant-origin propositions."
                ),
                approval_time="2026-07-27T20:00:00+09:00",
            )
            batch_path = next(
                (proposal_root / "review_batches").glob("*.json")
            )
            receipt_path = (
                proposal_root / "owner_curation_approval_receipt.json"
            )
            before_batch = batch_path.read_bytes()
            before_receipt = receipt_path.read_bytes()
            write_rework_resolution_bundle(
                REPO_ROOT,
                ATTEMPT_ROOT,
                prior_authority_root=PRIOR_AUTHORITY_ROOT,
                output_root=proposal_root,
            )
            self.assertEqual(batch_path.read_bytes(), before_batch)
            self.assertEqual(receipt_path.read_bytes(), before_receipt)
            validation = validate_batch_approvals(
                proposal_root,
                owner_decisions_path=OWNER_DECISIONS,
                require_all_approved=True,
            )
            self.assertEqual(validation["status"], "PASS")

    def test_regeneration_rejects_changed_approved_packet_before_writes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(dir=ATTEMPT_ROOT.parent) as temp_dir:
            proposal_root = Path(temp_dir) / "proposals"
            write_rework_resolution_bundle(
                REPO_ROOT,
                ATTEMPT_ROOT,
                prior_authority_root=PRIOR_AUTHORITY_ROOT,
                output_root=proposal_root,
            )
            record_exact_owner_batch_approvals(
                proposal_root,
                owner_decisions_path=OWNER_DECISIONS,
                approval_directive="fixture approval",
                approval_rationale=(
                    "Approve only the two exact plant-origin propositions."
                ),
                approval_time="2026-07-27T20:00:00+09:00",
            )
            proposal_path = (
                proposal_root
                / "curation_rework_resolution_proposals.jsonl"
            )
            batch_path = next(
                (proposal_root / "review_batches").glob("*.json")
            )
            batch = load_json(batch_path)
            batch["members"][0]["fact_value"] = "animal"
            write_json(batch_path, batch, write_once=False)
            before_proposal = proposal_path.read_bytes()
            before_batch = batch_path.read_bytes()
            with self.assertRaises(FoodSemanticError):
                write_rework_resolution_bundle(
                    REPO_ROOT,
                    ATTEMPT_ROOT,
                    prior_authority_root=PRIOR_AUTHORITY_ROOT,
                    output_root=proposal_root,
                )
            self.assertEqual(proposal_path.read_bytes(), before_proposal)
            self.assertEqual(batch_path.read_bytes(), before_batch)

    def test_regeneration_rejects_stale_receipt_before_writes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(dir=ATTEMPT_ROOT.parent) as temp_dir:
            proposal_root = Path(temp_dir) / "proposals"
            write_rework_resolution_bundle(
                REPO_ROOT,
                ATTEMPT_ROOT,
                prior_authority_root=PRIOR_AUTHORITY_ROOT,
                output_root=proposal_root,
            )
            record_exact_owner_batch_approvals(
                proposal_root,
                owner_decisions_path=OWNER_DECISIONS,
                approval_directive="fixture approval",
                approval_rationale=(
                    "Approve only the two exact plant-origin propositions."
                ),
                approval_time="2026-07-27T20:00:00+09:00",
            )
            proposal_path = (
                proposal_root
                / "curation_rework_resolution_proposals.jsonl"
            )
            batch_path = next(
                (proposal_root / "review_batches").glob("*.json")
            )
            receipt_path = (
                proposal_root / "owner_curation_approval_receipt.json"
            )
            before_proposal = proposal_path.read_bytes()
            before_receipt = receipt_path.read_bytes()
            batch_path.unlink()
            with self.assertRaises(FoodSemanticError):
                write_rework_resolution_bundle(
                    REPO_ROOT,
                    ATTEMPT_ROOT,
                    prior_authority_root=PRIOR_AUTHORITY_ROOT,
                    output_root=proposal_root,
                )
            self.assertEqual(proposal_path.read_bytes(), before_proposal)
            self.assertEqual(receipt_path.read_bytes(), before_receipt)
            self.assertFalse(batch_path.exists())

    def test_materialization_requires_exact_external_review_pass(
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
            record_exact_owner_batch_approvals(
                proposal_root,
                owner_decisions_path=OWNER_DECISIONS,
                approval_directive="fixture approval",
                approval_rationale=(
                    "Approve only the two exact plant-origin propositions."
                ),
                approval_time="2026-07-27T20:00:00+09:00",
            )
            successor_root = temp_root / "successor-authority"
            with self.assertRaises(FoodSemanticError):
                materialize_resolved_curation(
                    proposal_root,
                    prior_authority_root=PRIOR_AUTHORITY_ROOT,
                    successor_authority_root=successor_root,
                    owner_decisions_path=OWNER_DECISIONS,
                )
            self.assertFalse(
                (successor_root / "phase8_curation").exists()
            )

    def test_prior_authority_tamper_is_rejected_before_successor_write(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(dir=ATTEMPT_ROOT.parent) as temp_dir:
            temp_root = Path(temp_dir)
            prior_root = temp_root / "prior-authority"
            shutil.copytree(PRIOR_AUTHORITY_ROOT, prior_root)
            prior_receipt_path = (
                prior_root / "authority_execution_receipt.json"
            )
            prior_receipt = load_json(prior_receipt_path)
            prior_receipt["execution_root"] = relative_posix(
                prior_root,
                root=REPO_ROOT,
            )
            write_json(
                prior_receipt_path,
                prior_receipt,
                write_once=False,
            )
            proposal_root = temp_root / "proposals"
            write_rework_resolution_bundle(
                REPO_ROOT,
                ATTEMPT_ROOT,
                prior_authority_root=prior_root,
                output_root=proposal_root,
            )
            write_fixture_external_review(proposal_root)
            record_exact_owner_batch_approvals(
                proposal_root,
                owner_decisions_path=OWNER_DECISIONS,
                approval_directive="fixture approval",
                approval_rationale=(
                    "Approve only the two exact plant-origin propositions."
                ),
                approval_time="2026-07-27T20:00:00+09:00",
            )
            curated_path = (
                prior_root / "phase8_curation/curated_fact_ledger.jsonl"
            )
            prior_curated = load_jsonl(curated_path)
            write_jsonl(
                curated_path,
                prior_curated[:-1],
                write_once=False,
            )
            successor_root = temp_root / "successor-authority"
            with self.assertRaises(FoodSemanticError):
                materialize_resolved_curation(
                    proposal_root,
                    prior_authority_root=prior_root,
                    successor_authority_root=successor_root,
                    owner_decisions_path=OWNER_DECISIONS,
                )
            self.assertFalse(
                (successor_root / "phase8_curation").exists()
            )

    def test_semantic_scope_tamper_is_rejected_before_successor_write(
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
            write_fixture_external_review(proposal_root)
            record_exact_owner_batch_approvals(
                proposal_root,
                owner_decisions_path=OWNER_DECISIONS,
                approval_directive="fixture approval",
                approval_rationale=(
                    "Approve only the two exact plant-origin propositions."
                ),
                approval_time="2026-07-27T20:00:00+09:00",
            )
            proposal_path = (
                proposal_root
                / "curation_rework_resolution_proposals.jsonl"
            )
            proposals = load_jsonl(proposal_path)
            replacement_id = canonical_proposition_id(
                "Base.Comfrey",
                "culinary_role",
                "herb",
            )
            proposals[0]["fact_axis"] = "culinary_role"
            proposals[0]["fact_value"] = "herb"
            proposals[0]["proposition_id"] = replacement_id
            write_jsonl(proposal_path, proposals, write_once=False)
            summary_path = proposal_root / "curation_proposal_summary.json"
            summary = load_json(summary_path)
            summary["proposal_ledger_sha256"] = sha256_file(proposal_path)
            write_json(summary_path, summary, write_once=False)
            batch_path = next(
                (proposal_root / "review_batches").glob("*.json")
            )
            batch = load_json(batch_path)
            batch["members"][0] = proposals[0]
            batch["proposal_content_sha256"] = review_batch_proposal_hash(
                batch
            )
            batch["owner_approval"]["proposal_content_sha256"] = batch[
                "proposal_content_sha256"
            ]
            batch["owner_approval"]["approved_proposition_ids"] = sorted(
                row["proposition_id"] for row in batch["members"]
            )
            write_json(batch_path, batch, write_once=False)
            generic_validation = validate_batch_approvals(
                proposal_root,
                owner_decisions_path=OWNER_DECISIONS,
                require_all_approved=True,
            )
            self.assertEqual(generic_validation["status"], "PASS")
            successor_root = temp_root / "successor-authority"
            with self.assertRaises(FoodSemanticError):
                materialize_resolved_curation(
                    proposal_root,
                    prior_authority_root=PRIOR_AUTHORITY_ROOT,
                    successor_authority_root=successor_root,
                    owner_decisions_path=OWNER_DECISIONS,
                )
            self.assertFalse(
                (successor_root / "phase8_curation").exists()
            )


if __name__ == "__main__":
    unittest.main()
