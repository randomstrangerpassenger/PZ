from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.dvf_3_3_food_semantic.candidate_writer import (
    assert_candidate_sink,
    build_candidate_bytes,
)
from tools.build.dvf_3_3_food_semantic.contracts import FoodSemanticError
from tools.build.dvf_3_3_food_semantic.contracts import (
    iter_jsonl_with_raw,
    load_json,
)
from tools.build.dvf_3_3_food_semantic.curation_workflow import (
    apply_events_idempotently,
    build_batch_rows,
    validate_curated_rows,
)
from tools.build.dvf_3_3_food_semantic.schema_feasibility import AXES


FIXTURES = json.loads(
    (
        Path(__file__).parent
        / "fixtures/dvf_3_3_food_semantic_contract_fixtures.json"
    ).read_text(encoding="utf-8")
)


class FoodSemanticCurationWriterTest(unittest.TestCase):
    def test_writer_preserves_non_target_bytes(self) -> None:
        staging = V2_ROOT / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=staging) as temp_dir:
            facts_path = Path(temp_dir) / "facts.jsonl"
            first_raw = b'{ "item_id" : "Base.Before", "kept" : true } \n'
            target_raw = b'{"item_id":"Base.Target","identity_hint":"food"}\n'
            last_raw = b'{"item_id":"Base.After","n":1}\r\n'
            facts_path.write_bytes(first_raw + target_raw + last_raw)
            automatic = [dict(FIXTURES["writer_automatic_row"])]

            candidate, stats = build_candidate_bytes(
                facts_path,
                target_members={"Base.Target"},
                automatic_rows=automatic,
                authority_bearing=False,
            )
            self.assertTrue(candidate.startswith(first_raw))
            self.assertTrue(candidate.endswith(last_raw))
            self.assertEqual(stats["non_target_count"], 2)
            self.assertEqual(stats["changed_target_count"], 1)
            self.assertEqual(stats["non_target_row_byte_mismatch_count"], 0)

            reordered, reordered_stats = build_candidate_bytes(
                facts_path,
                target_members={"Base.Target"},
                automatic_rows=list(reversed(automatic)),
                authority_bearing=False,
            )
            self.assertEqual(candidate, reordered)
            self.assertEqual(stats, reordered_stats)

            with self.assertRaises(FoodSemanticError):
                build_candidate_bytes(
                    facts_path,
                    target_members={"Base.Target"},
                    automatic_rows=automatic,
                    authority_bearing=True,
                )

    def test_curation_batch_and_approval_contracts(self) -> None:
        queue = [
            {"item_identity": "Base.A"},
            {"item_identity": "Base.B"},
            {"item_identity": "Base.C"},
        ]
        first = build_batch_rows(queue, schema_sha256="a" * 64, batch_size=2)
        second = build_batch_rows(queue, schema_sha256="a" * 64, batch_size=2)
        self.assertEqual(first, second)
        self.assertEqual(sum(row["member_count"] for row in first), len(queue))

        events = [
            {
                "event_id": "event-1",
                "proposition_id": "prop-1",
                "event": "queued",
            }
        ]
        states, duplicates = apply_events_idempotently(events + events)
        self.assertEqual(states, {"prop-1": "queued"})
        self.assertEqual(duplicates, 1)

        schema = {"axes": AXES}
        report = validate_curated_rows(
            FIXTURES["curated_negative_rows"], schema
        )
        self.assertGreater(report["curated_approval_missing_count"], 0)
        self.assertGreater(report["curated_schema_violation_count"], 0)

    def test_live_writer_sink_is_rejected(self) -> None:
        attempt_root = (
            REPO_ROOT
            / "Iris/build/description/v2/staging/"
            "dvf_3_3_food_semantic_facts_authority/attempts/test-fixture"
        )
        with self.assertRaises(FoodSemanticError):
            assert_candidate_sink(
                REPO_ROOT,
                attempt_root,
                REPO_ROOT
                / "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
            )

    def test_successful_attempt_candidate_scope(self) -> None:
        attempts = (
            V2_ROOT
            / "staging/dvf_3_3_food_semantic_facts_authority/attempts"
        )
        successful = [
            path
            for path in attempts.iterdir()
            if (
                path / "implementation_execution_summary.json"
            ).is_file()
            and load_json(path / "implementation_execution_summary.json")[
                "status"
            ]
            == "PASS"
        ]
        self.assertTrue(successful)
        attempt = sorted(successful)[-1]
        coverage = load_json(
            attempt / "phase9_coverage/coverage_reconciliation_report.json"
        )
        self.assertEqual(coverage["implementation_route_count"], 317)
        self.assertEqual(coverage["unrouted_target_count"], 0)
        self.assertEqual(coverage["double_route_count"], 0)

        target = load_json(
            attempt / "phase1_census/target_food_universe_manifest.json"
        )
        current_path = V2_ROOT / "data/dvf_3_3_facts.jsonl"
        candidate_path = (
            attempt / "phase10_candidate/candidate_successor_facts.jsonl"
        )
        current_rows = list(iter_jsonl_with_raw(current_path))
        candidate_rows = list(iter_jsonl_with_raw(candidate_path))
        self.assertEqual(len(current_rows), len(candidate_rows))
        targets = set(target["members"])
        for (current, current_raw), (candidate, candidate_raw) in zip(
            current_rows, candidate_rows, strict=True
        ):
            self.assertEqual(current["item_id"], candidate["item_id"])
            if current["item_id"] not in targets:
                self.assertEqual(current_raw, candidate_raw)


if __name__ == "__main__":
    unittest.main()
