from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.dvf_3_3_food_semantic.naturalization_handoff import (
    ACCEPTANCE_TEST_PATH,
    PREDECESSOR_BASELINE_FIXTURE_PATH,
    PRESERVATION_TEST_PATH,
    RUNNER_PATH,
    VALIDATOR_PATH,
)
from tools.build.dvf_3_3_food_semantic.contracts import load_json, sha256_file


class FoodSemanticHandoffTest(unittest.TestCase):
    def test_candidate_patch_is_bounded(self) -> None:
        targets = [
            RUNNER_PATH,
            VALIDATOR_PATH,
            ACCEPTANCE_TEST_PATH,
            PRESERVATION_TEST_PATH,
        ]
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
        manifest = load_json(
            sorted(successful)[-1]
            / "phase12_phase2_handoff/naturalization_candidate_patch_manifest.json"
        )
        manifest_by_target = {
            row["target_path"]: row for row in manifest["files"]
        }
        for relative in targets:
            row = manifest_by_target[relative]
            source = REPO_ROOT / relative
            self.assertTrue(source.is_file())
            self.assertIsNone(row["candidate_path"])
            self.assertEqual(
                row["preimage_state"],
                "present_and_D16_symbols_adopted",
            )
            self.assertEqual(
                row["patch_kind"],
                "no_change_required_existing_D16_adoption",
            )
            self.assertEqual(sha256_file(source), row["preimage_sha256"])
            self.assertEqual(sha256_file(source), row["replacement_sha256"])
        self.assertEqual(len(set(targets)), 4)
        self.assertEqual(manifest["status"], "existing_D16_adoption_verified")
        self.assertEqual(manifest["existing_D16_adoption_file_count"], 4)
        self.assertFalse(manifest["D16_owner_authorization_consumed"])

    def test_predecessor_threshold_is_bound_without_authority_claim(self) -> None:
        cause = json.loads(
            (REPO_ROOT / PREDECESSOR_BASELINE_FIXTURE_PATH).read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(cause["candidate_denominator"], 2084)
        self.assertEqual(cause["maximum_repetition_count"], 104)
        self.assertFalse(cause["current_fact_semantic_authority_granted"])

    def test_successful_attempt_patch_manifest_is_exact(self) -> None:
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
        manifest = load_json(
            attempt
            / "phase12_phase2_handoff/naturalization_candidate_patch_manifest.json"
        )
        self.assertEqual(len(manifest["files"]), 4)
        self.assertEqual(manifest["candidate_patch_out_of_scope_symbol_count"], 0)
        for row in manifest["files"]:
            source = REPO_ROOT / row["target_path"]
            self.assertIsNone(row["candidate_path"])
            self.assertEqual(sha256_file(source), row["replacement_sha256"])
            self.assertEqual(sha256_file(source), row["preimage_sha256"])
            self.assertEqual(row["existing_symbol_replacement_count"], 0)
        self.assertFalse(manifest["D16_owner_authorization_consumed"])


if __name__ == "__main__":
    unittest.main()
