from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_cutover"
CURRENT_MANIFEST = REPO / "Iris/build/description/v2/data/dvf_3_3_input_manifest.json"
CURRENT_FACTS = REPO / "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
CURRENT_DECISIONS = REPO / "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl"
CURRENT_OVERLAY = REPO / "Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl"
CURRENT_RENDERED = REPO / "Iris/build/description/v2/output/dvf_3_3_rendered.json"
REQUIRED_MANIFEST = REPO / "Iris/_docs/round3/current_route_required_validations.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


class DvfVnextCurrentAuthorityCutoverTest(unittest.TestCase):
    def test_final_report_seals_cutover_without_release_claims(self) -> None:
        report = load_json(ROOT / "phase10/final_current_authority_cutover_report.json")
        claim = load_json(ROOT / "phase10/claim_boundary_report.json")

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["closeout_state"], "complete_current_authority_cutover_and_consumer_migration")
        self.assertEqual(report["entry_count"], 2105)
        self.assertEqual(report["runtime_entry_count"], 2105)
        self.assertIn("no_package_release_readiness", report["non_claims"])
        self.assertIn("no_manual_in_game_validation", report["non_claims"])
        self.assertEqual(claim["status"], "PASS")
        self.assertEqual(claim["forbidden_claim_hit_count"], 0)

    def test_current_source_and_rendered_are_2105_successor_authority(self) -> None:
        manifest = load_json(CURRENT_MANIFEST)
        rendered = load_json(CURRENT_RENDERED)
        source_report = load_json(ROOT / "phase2/source_promotion_report.json")
        rendered_report = load_json(ROOT / "phase3/rendered_regeneration_report.json")

        self.assertEqual(manifest["status"], "current_authority")
        self.assertEqual(manifest["authority_role"], "successor_current_source_authority")
        self.assertEqual(count_jsonl(CURRENT_FACTS), 2105)
        self.assertEqual(count_jsonl(CURRENT_DECISIONS), 2105)
        self.assertEqual(count_jsonl(CURRENT_OVERLAY), 2105)
        self.assertEqual(source_report["status"], "PASS")
        self.assertEqual(source_report["facts_count"], 2105)
        self.assertEqual(source_report["decisions_count"], 2105)
        self.assertEqual(rendered_report["status"], "PASS")
        self.assertEqual(rendered_report["rendered_entry_count"], 2105)
        self.assertTrue(rendered_report["explicit_overlay_path"])
        self.assertEqual(rendered["meta"]["overlay_path"].replace("\\", "/"), "Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl")
        self.assertEqual(len(rendered["entries"]), 2105)

    def test_live_runtime_chunks_are_single_successor_authority(self) -> None:
        report = load_json(ROOT / "phase4/runtime_atomic_replace_report.json")
        dual = load_json(ROOT / "phase4/old_new_dual_current_absence_report.json")

        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["live_runtime_replaced"])
        self.assertTrue(report["single_successor_authority"])
        self.assertEqual(report["entry_count"], 2105)
        self.assertEqual(report["chunk_count"], 11)
        self.assertFalse(report["monolith_runtime_authority"])
        self.assertEqual(dual["status"], "PASS")
        self.assertFalse(dual["old_chunk_dir_retained_as_live_authority"])

    def test_required_validation_manifest_points_to_cutover_evidence(self) -> None:
        manifest = load_json(REQUIRED_MANIFEST)
        paths = {row["path"] for row in manifest["required_artifacts"]}
        tests = {row["test_id"] for row in manifest["required_tests"]}
        consumer_report = load_json(ROOT / "phase5/manifest_driven_consumer_validation_report.json")

        self.assertIn("required_validation_gate_adopted", manifest["claim"])
        self.assertIn("axis-qualified", manifest["claim"])
        self.assertNotIn("current authority cutover and 2105 consumer migration sealed", manifest["claim"])
        self.assertIn("Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_cutover/phase10/final_current_authority_cutover_report.json", paths)
        self.assertIn("Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_cutover/phase4/runtime_atomic_replace_report.json", paths)
        self.assertIn(
            "test_dvf_3_3_vnext_current_authority_cutover.DvfVnextCurrentAuthorityCutoverTest.test_final_report_seals_cutover_without_release_claims",
            tests,
        )
        self.assertEqual(consumer_report["status"], "PASS")
        self.assertFalse(consumer_report["live_manifest_mutated_by_predecessor_scripts"])


if __name__ == "__main__":
    unittest.main()
