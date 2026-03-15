from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
BUILD_DIR = TESTS_DIR.parent / "tools" / "build"
sys.path.insert(0, str(BUILD_DIR))

from build_phase3_hold_queue import (  # noqa: E402
    HotspotValidationError,
    build_phase3_hold_queue,
    validate_hotspot_clusters,
)
from generate_acquisition_master import load_json, load_jsonl  # noqa: E402


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def write_json_file(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)


def make_queue_row(
    *,
    fulltype: str,
    bucket_id: str,
    candidate_state: str,
    candidate_reason_code: str,
    approval_state: str,
    approval_reason_code: str,
    candidate_compose_profile: str | None = None,
    phase3_notes: str | None = None,
    approval_notes: str | None = None,
) -> dict:
    return {
        "fulltype": fulltype,
        "bucket_id": bucket_id,
        "source_overlay": "candidate_state_phase3.review.jsonl",
        "candidate_state": candidate_state,
        "candidate_reason_code": candidate_reason_code,
        "candidate_compose_profile": candidate_compose_profile,
        "phase3_notes": phase3_notes,
        "approval_state": approval_state,
        "approval_reason_code": approval_reason_code,
        "approval_notes": approval_notes,
        "phase3_decision_version": "phase3-candidate-state-v1",
        "queue_version": "phase3-sync-queue-v1",
    }


def make_hotspot_cluster(
    *,
    cluster_id: str = "HOTSPOT_TEST",
    source_bucket: str = "Consumable.3-E",
    candidate_state: str = "MANUAL_OVERRIDE_CANDIDATE",
    candidate_reason_code: str = "LAYER_COLLISION",
    approval_reason_code: str = "MANUAL_REVIEW_REQUIRED",
    hotspot_type: str = "manual_concentration_3_of_3",
    cluster_status: str = "OPEN",
    fulltypes: list[str] | None = None,
) -> dict:
    return {
        "cluster_id": cluster_id,
        "source_bucket": source_bucket,
        "candidate_state": candidate_state,
        "candidate_reason_code": candidate_reason_code,
        "approval_reason_code": approval_reason_code,
        "hotspot_type": hotspot_type,
        "cluster_status": cluster_status,
        "cluster_note_template": f"cluster={cluster_id}",
        "policy_patch_required": False,
        "fulltypes": fulltypes or [],
    }


CONSUMABLE_3E_HOLD_ROWS = [
    make_queue_row(
        fulltype="Base.Comfrey",
        bucket_id="Consumable.3-E",
        candidate_state="MANUAL_OVERRIDE_CANDIDATE",
        candidate_reason_code="LAYER_COLLISION",
        approval_state="HOLD",
        approval_reason_code="MANUAL_REVIEW_REQUIRED",
        phase3_notes="채집 collision.",
    ),
    make_queue_row(
        fulltype="Base.Lemongrass",
        bucket_id="Consumable.3-E",
        candidate_state="MANUAL_OVERRIDE_CANDIDATE",
        candidate_reason_code="LAYER_COLLISION",
        approval_state="HOLD",
        approval_reason_code="MANUAL_REVIEW_REQUIRED",
        phase3_notes="채집 collision.",
    ),
    make_queue_row(
        fulltype="Base.Plantain",
        bucket_id="Consumable.3-E",
        candidate_state="MANUAL_OVERRIDE_CANDIDATE",
        candidate_reason_code="LAYER_COLLISION",
        approval_state="HOLD",
        approval_reason_code="MANUAL_REVIEW_REQUIRED",
        phase3_notes="채집 collision.",
    ),
]


class Phase3HoldQueueTests(unittest.TestCase):
    def test_build_phase3_hold_queue_writes_hold_only_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)
            sync_queue_path = tmp_dir / "phase3_sync_queue.jsonl"
            hold_queue_path = tmp_dir / "phase3_hold_queue_cumulative.jsonl"
            reason_summary_path = tmp_dir / "phase3_hold_reason_summary.json"
            backlog_path = tmp_dir / "phase3_hold_review_backlog.md"

            write_jsonl(
                sync_queue_path,
                [
                    make_queue_row(
                        fulltype="Base.Bandage",
                        bucket_id="Consumable.3-C",
                        candidate_state="PROMOTE_ACTIVE",
                        candidate_reason_code="LOCATION_SPECIFIC",
                        candidate_compose_profile="ACQ_ONLY_LOCATION",
                        approval_state="APPROVE_SYNC",
                        approval_reason_code="DIRECT_ACQUISITION_READY",
                    ),
                    make_queue_row(
                        fulltype="Base.DoctorBag",
                        bucket_id="Tool.1-L",
                        candidate_state="PROMOTE_ACTIVE",
                        candidate_reason_code="USE_CONTEXT_LINKED",
                        candidate_compose_profile="USE_PLUS_ACQ",
                        approval_state="HOLD",
                        approval_reason_code="CONTEXTUAL_PROMOTE_REVIEW",
                        approval_notes="Context-linked promote requires canon voice review.",
                    ),
                    make_queue_row(
                        fulltype="Base.Handbag",
                        bucket_id="Tool.1-L",
                        candidate_state="MANUAL_OVERRIDE_CANDIDATE",
                        candidate_reason_code="LAYER_COLLISION",
                        approval_state="HOLD",
                        approval_reason_code="MANUAL_REVIEW_REQUIRED",
                        phase3_notes="3-4 상호작용층과 겹친다.",
                        approval_notes="3-4 상호작용층과 겹친다.",
                    ),
                ],
            )

            result = build_phase3_hold_queue(
                sync_queue_path=sync_queue_path,
                hold_queue_out=hold_queue_path,
                reason_summary_out=reason_summary_path,
                backlog_out=backlog_path,
                queue_source_label="phase3_sync_queue.jsonl",
            )

            hold_rows = load_jsonl(hold_queue_path)
            summary = load_json(reason_summary_path)
            backlog = backlog_path.read_text(encoding="utf-8")

            self.assertEqual(2, len(hold_rows))
            self.assertEqual(2, summary["hold_row_total"])
            self.assertEqual(0, summary["known_batch_review_hold_row_total"])
            self.assertEqual(0, summary["known_hotspot_hold_row_total"])
            self.assertEqual(2, summary["general_hold_row_total"])
            self.assertEqual([], summary["known_batch_review_breakdown"])
            self.assertEqual([], summary["known_hotspot_breakdown"])
            self.assertEqual("phase3_sync_queue.jsonl", summary["queue_source"])
            self.assertEqual({"CONTEXTUAL_PROMOTE_REVIEW": 1, "MANUAL_REVIEW_REQUIRED": 1}, summary["approval_reason_breakdown"])
            self.assertEqual({"MANUAL_OVERRIDE_CANDIDATE": 1, "PROMOTE_ACTIVE": 1}, summary["candidate_state_breakdown"])
            self.assertIn("Batch Review Separation", backlog)
            self.assertIn("Phase 3 HOLD Review Backlog", backlog)
            self.assertIn("candidate_state", backlog)
            self.assertIn("Base.Handbag", backlog)
            self.assertEqual(2, len(result["hold_rows"]))

    def test_hotspot_cluster_classification(self) -> None:
        """Consumable.3-E 3건이 hotspot cluster로 올바르게 분류되는지 확인."""
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)
            sync_queue_path = tmp_dir / "phase3_sync_queue.jsonl"
            hold_queue_path = tmp_dir / "phase3_hold_queue_cumulative.jsonl"
            reason_summary_path = tmp_dir / "phase3_hold_reason_summary.json"
            backlog_path = tmp_dir / "phase3_hold_review_backlog.md"
            hotspot_path = tmp_dir / "phase3_approval_hotspot_clusters.json"

            write_jsonl(sync_queue_path, CONSUMABLE_3E_HOLD_ROWS)
            write_json_file(
                hotspot_path,
                [
                    make_hotspot_cluster(
                        cluster_id="HOTSPOT_CONSUMABLE_3E_FORAGING_COLLISION",
                        source_bucket="Consumable.3-E",
                        fulltypes=["Base.Comfrey", "Base.Lemongrass", "Base.Plantain"],
                    ),
                ],
            )

            result = build_phase3_hold_queue(
                sync_queue_path=sync_queue_path,
                hold_queue_out=hold_queue_path,
                reason_summary_out=reason_summary_path,
                backlog_out=backlog_path,
                hotspot_clusters_path=hotspot_path,
            )

            summary = result["summary"]
            self.assertEqual(3, summary["hold_row_total"])
            self.assertEqual(3, summary["known_hotspot_hold_row_total"])
            self.assertEqual(0, summary["known_batch_review_hold_row_total"])
            self.assertEqual(0, summary["general_hold_row_total"])
            self.assertEqual(1, len(summary["known_hotspot_breakdown"]))
            self.assertEqual("HOTSPOT_CONSUMABLE_3E_FORAGING_COLLISION", summary["known_hotspot_breakdown"][0]["cluster_id"])

    def test_hotspot_and_batch_review_separation(self) -> None:
        """batch review + hotspot + general이 3층으로 올바르게 분리되는지 확인."""
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)
            sync_queue_path = tmp_dir / "phase3_sync_queue.jsonl"
            hold_queue_path = tmp_dir / "phase3_hold_queue_cumulative.jsonl"
            reason_summary_path = tmp_dir / "phase3_hold_reason_summary.json"
            backlog_path = tmp_dir / "phase3_hold_review_backlog.md"
            hotspot_path = tmp_dir / "phase3_approval_hotspot_clusters.json"

            batch_row = make_queue_row(
                fulltype="Base.Bracelet_BangleLeftGold",
                bucket_id="Wearable.6-G",
                candidate_state="MANUAL_OVERRIDE_CANDIDATE",
                candidate_reason_code="LAYER_COLLISION",
                approval_state="HOLD",
                approval_reason_code="MANUAL_REVIEW_REQUIRED",
            )
            general_row = make_queue_row(
                fulltype="Base.DoctorBag",
                bucket_id="Tool.1-L",
                candidate_state="PROMOTE_ACTIVE",
                candidate_reason_code="USE_CONTEXT_LINKED",
                approval_state="HOLD",
                approval_reason_code="CONTEXTUAL_PROMOTE_REVIEW",
            )

            write_jsonl(sync_queue_path, CONSUMABLE_3E_HOLD_ROWS + [batch_row, general_row])
            write_json_file(
                hotspot_path,
                [
                    make_hotspot_cluster(
                        cluster_id="HOTSPOT_CONSUMABLE_3E_FORAGING_COLLISION",
                        source_bucket="Consumable.3-E",
                        fulltypes=["Base.Comfrey", "Base.Lemongrass", "Base.Plantain"],
                    ),
                ],
            )

            result = build_phase3_hold_queue(
                sync_queue_path=sync_queue_path,
                hold_queue_out=hold_queue_path,
                reason_summary_out=reason_summary_path,
                backlog_out=backlog_path,
                hotspot_clusters_path=hotspot_path,
            )

            summary = result["summary"]
            self.assertEqual(5, summary["hold_row_total"])
            self.assertEqual(1, summary["known_batch_review_hold_row_total"])
            self.assertEqual(3, summary["known_hotspot_hold_row_total"])
            self.assertEqual(1, summary["general_hold_row_total"])

            backlog = backlog_path.read_text(encoding="utf-8")
            self.assertIn("known batch review rows: `1`", backlog)
            self.assertIn("known hotspot rows: `3`", backlog)
            self.assertIn("general HOLD rows: `1`", backlog)

    def test_known_batch_review_preserved_with_hotspot(self) -> None:
        """batch review 33건 + hotspot 3건 + general 1건 = 총 37건 유지 확인."""
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)
            sync_queue_path = tmp_dir / "phase3_sync_queue.jsonl"
            hold_queue_path = tmp_dir / "phase3_hold_queue_cumulative.jsonl"
            reason_summary_path = tmp_dir / "phase3_hold_reason_summary.json"
            backlog_path = tmp_dir / "phase3_hold_review_backlog.md"
            hotspot_path = tmp_dir / "phase3_approval_hotspot_clusters.json"

            # 33 batch review rows (Wearable.6-G)
            batch_rows = [
                make_queue_row(
                    fulltype=f"Base.Ring_{i}",
                    bucket_id="Wearable.6-G",
                    candidate_state="MANUAL_OVERRIDE_CANDIDATE",
                    candidate_reason_code="LAYER_COLLISION",
                    approval_state="HOLD",
                    approval_reason_code="MANUAL_REVIEW_REQUIRED",
                )
                for i in range(33)
            ]
            # 1 general hold
            general_row = make_queue_row(
                fulltype="Base.Log",
                bucket_id="Resource.4-A",
                candidate_state="MANUAL_OVERRIDE_CANDIDATE",
                candidate_reason_code="LAYER_COLLISION",
                approval_state="HOLD",
                approval_reason_code="MANUAL_REVIEW_REQUIRED",
            )

            write_jsonl(sync_queue_path, batch_rows + CONSUMABLE_3E_HOLD_ROWS + [general_row])
            write_json_file(
                hotspot_path,
                [
                    make_hotspot_cluster(
                        cluster_id="HOTSPOT_CONSUMABLE_3E_FORAGING_COLLISION",
                        source_bucket="Consumable.3-E",
                        fulltypes=["Base.Comfrey", "Base.Lemongrass", "Base.Plantain"],
                    ),
                ],
            )

            result = build_phase3_hold_queue(
                sync_queue_path=sync_queue_path,
                hold_queue_out=hold_queue_path,
                reason_summary_out=reason_summary_path,
                backlog_out=backlog_path,
                hotspot_clusters_path=hotspot_path,
            )

            summary = result["summary"]
            total = 33 + 3 + 1
            self.assertEqual(total, summary["hold_row_total"])
            self.assertEqual(33, summary["known_batch_review_hold_row_total"])
            self.assertEqual(3, summary["known_hotspot_hold_row_total"])
            self.assertEqual(1, summary["general_hold_row_total"])
            self.assertEqual(total, summary["known_batch_review_hold_row_total"] + summary["known_hotspot_hold_row_total"] + summary["general_hold_row_total"])

    def test_candidate_state_counts_unchanged(self) -> None:
        """hotspot tier 추가 후에도 HOLD 총량과 APPROVE_SYNC가 불변인지 확인."""
        with tempfile.TemporaryDirectory() as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)
            sync_queue_path = tmp_dir / "phase3_sync_queue.jsonl"
            hold_queue_path = tmp_dir / "phase3_hold_queue_cumulative.jsonl"
            reason_summary_path = tmp_dir / "phase3_hold_reason_summary.json"
            backlog_path = tmp_dir / "phase3_hold_review_backlog.md"
            hotspot_path = tmp_dir / "phase3_approval_hotspot_clusters.json"

            approved_row = make_queue_row(
                fulltype="Base.Bandage",
                bucket_id="Consumable.3-C",
                candidate_state="PROMOTE_ACTIVE",
                candidate_reason_code="LOCATION_SPECIFIC",
                candidate_compose_profile="ACQ_ONLY_LOCATION",
                approval_state="APPROVE_SYNC",
                approval_reason_code="DIRECT_ACQUISITION_READY",
            )

            write_jsonl(sync_queue_path, [approved_row] + CONSUMABLE_3E_HOLD_ROWS)
            write_json_file(
                hotspot_path,
                [
                    make_hotspot_cluster(
                        cluster_id="HOTSPOT_CONSUMABLE_3E_FORAGING_COLLISION",
                        source_bucket="Consumable.3-E",
                        fulltypes=["Base.Comfrey", "Base.Lemongrass", "Base.Plantain"],
                    ),
                ],
            )

            result = build_phase3_hold_queue(
                sync_queue_path=sync_queue_path,
                hold_queue_out=hold_queue_path,
                reason_summary_out=reason_summary_path,
                backlog_out=backlog_path,
                hotspot_clusters_path=hotspot_path,
            )

            summary = result["summary"]
            self.assertEqual(4, summary["sync_queue_row_total"])
            self.assertEqual(3, summary["hold_row_total"])
            self.assertEqual(3, summary["candidate_state_breakdown"]["MANUAL_OVERRIDE_CANDIDATE"])
            self.assertEqual(3, len(result["hold_rows"]))

    def test_hotspot_json_duplicate_cluster_id_fails(self) -> None:
        """cluster_id 중복 시 HotspotValidationError가 발생하는지 확인."""
        clusters = [
            make_hotspot_cluster(cluster_id="SAME_ID", fulltypes=["Base.Comfrey"]),
            make_hotspot_cluster(cluster_id="SAME_ID", fulltypes=["Base.Lemongrass"]),
        ]
        hold_rows = [
            make_queue_row(
                fulltype="Base.Comfrey", bucket_id="Consumable.3-E",
                candidate_state="MANUAL_OVERRIDE_CANDIDATE", candidate_reason_code="LAYER_COLLISION",
                approval_state="HOLD", approval_reason_code="MANUAL_REVIEW_REQUIRED",
            ),
            make_queue_row(
                fulltype="Base.Lemongrass", bucket_id="Consumable.3-E",
                candidate_state="MANUAL_OVERRIDE_CANDIDATE", candidate_reason_code="LAYER_COLLISION",
                approval_state="HOLD", approval_reason_code="MANUAL_REVIEW_REQUIRED",
            ),
        ]
        with self.assertRaises(HotspotValidationError) as ctx:
            validate_hotspot_clusters(clusters, hold_rows)
        self.assertIn("Duplicate cluster_id", str(ctx.exception))

    def test_hotspot_json_cross_cluster_fulltype_fails(self) -> None:
        """같은 fulltype이 2개 cluster에 동시 소속되면 FAIL."""
        clusters = [
            make_hotspot_cluster(cluster_id="CLUSTER_A", fulltypes=["Base.Comfrey"]),
            make_hotspot_cluster(cluster_id="CLUSTER_B", fulltypes=["Base.Comfrey"]),
        ]
        hold_rows = [
            make_queue_row(
                fulltype="Base.Comfrey", bucket_id="Consumable.3-E",
                candidate_state="MANUAL_OVERRIDE_CANDIDATE", candidate_reason_code="LAYER_COLLISION",
                approval_state="HOLD", approval_reason_code="MANUAL_REVIEW_REQUIRED",
            ),
        ]
        with self.assertRaises(HotspotValidationError) as ctx:
            validate_hotspot_clusters(clusters, hold_rows)
        self.assertIn("belongs to multiple clusters", str(ctx.exception))

    def test_hotspot_json_row_mismatch_fails(self) -> None:
        """JSON의 candidate_state가 실제 row와 불일치하면 FAIL."""
        clusters = [
            make_hotspot_cluster(
                cluster_id="HOTSPOT_TEST",
                candidate_state="PROMOTE_ACTIVE",  # mismatch
                fulltypes=["Base.Comfrey"],
            ),
        ]
        hold_rows = [
            make_queue_row(
                fulltype="Base.Comfrey", bucket_id="Consumable.3-E",
                candidate_state="MANUAL_OVERRIDE_CANDIDATE", candidate_reason_code="LAYER_COLLISION",
                approval_state="HOLD", approval_reason_code="MANUAL_REVIEW_REQUIRED",
            ),
        ]
        with self.assertRaises(HotspotValidationError) as ctx:
            validate_hotspot_clusters(clusters, hold_rows)
        self.assertIn("candidate_state mismatch", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
