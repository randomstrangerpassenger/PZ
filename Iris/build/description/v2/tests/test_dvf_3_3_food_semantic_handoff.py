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
    ACCEPTANCE_TEST_APPEND,
    ACCEPTANCE_TEST_PATH,
    CAUSE_PATH,
    POLICY_PATH,
    PRESERVATION_TEST_APPEND,
    PRESERVATION_TEST_PATH,
    RUNNER_APPEND,
    RUNNER_PATH,
    VALIDATOR_APPEND,
    VALIDATOR_PATH,
    _candidate_bytes,
)
from tools.build.dvf_3_3_food_semantic.contracts import load_json, sha256_file


class FoodSemanticHandoffTest(unittest.TestCase):
    def test_candidate_patch_is_bounded(self) -> None:
        specs = [
            (RUNNER_PATH, RUNNER_APPEND),
            (VALIDATOR_PATH, VALIDATOR_APPEND),
            (ACCEPTANCE_TEST_PATH, ACCEPTANCE_TEST_APPEND),
            (PRESERVATION_TEST_PATH, PRESERVATION_TEST_APPEND),
        ]
        for relative, append_text in specs:
            preimage = (REPO_ROOT / relative).read_bytes()
            candidate = _candidate_bytes(preimage, append_text)
            self.assertTrue(candidate.startswith(preimage))
            self.assertGreater(len(candidate), len(preimage))
            self.assertEqual(candidate[: len(preimage)], preimage)
        self.assertEqual(len({relative for relative, _ in specs}), 4)

    def test_threshold_is_derived_from_bound_inputs(self) -> None:
        policy = json.loads(
            (REPO_ROOT / POLICY_PATH).read_text(encoding="utf-8")
        )
        cause = json.loads((REPO_ROOT / CAUSE_PATH).read_text(encoding="utf-8"))
        ratio = policy["detectors"]["repeated_skeleton_concentration"]["ratio"]
        threshold = (
            int(cause["candidate_denominator"]) * int(ratio["numerator"])
            // int(ratio["denominator"])
        )
        self.assertEqual(cause["candidate_denominator"], 2084)
        self.assertEqual(threshold, 104)

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
            candidate = REPO_ROOT / row["candidate_path"]
            self.assertEqual(sha256_file(source), row["preimage_sha256"])
            self.assertEqual(sha256_file(candidate), row["replacement_sha256"])
            self.assertTrue(candidate.read_bytes().startswith(source.read_bytes()))
            self.assertEqual(row["existing_symbol_replacement_count"], 0)


if __name__ == "__main__":
    unittest.main()
