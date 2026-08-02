from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = next(parent for parent in Path(__file__).resolve().parents if (parent / ".git").exists())
sys.path.insert(0, str(REPO / "Iris" / "test"))
from core_refactor_evidence import load_bound_evidence, require_case_fixtures  # noqa: E402


class DescriptionSinglePathAcceptanceTest(unittest.TestCase):
    def test_pz_acceptance_preserves_characterized_outputs(self) -> None:
        before = load_bound_evidence(REPO, "Iris/_docs/refactor/core_refactor/phase1_pre_refactor_pz_baseline.jsonl")
        after = load_bound_evidence(REPO, "Iris/_docs/refactor/core_refactor/phase2_description_acceptance.jsonl")
        require_case_fixtures(after, {
            "description_acceptance.base_hammer": "Base.Hammer",
            "description_acceptance.base_pan": "Base.Pan",
            "description_acceptance.base_whiskeyfull": "Base.WhiskeyFull",
            "description_acceptance.nil_fallback": "nil_input",
        })
        before_by_fixture = {row["fixture_id"]: row for row in before if row["axis"] == "description"}
        after_by_fixture = {row["fixture_id"]: row for row in after if row["axis"] == "description_single_path"}
        self.assertEqual(set(before_by_fixture), set(after_by_fixture))
        for fixture_id, before_row in before_by_fixture.items():
            after_row = after_by_fixture[fixture_id]
            self.assertEqual("post_refactor_acceptance", after_row["time_axis"])
            self.assertEqual("pass", after_row["status"])
            self.assertEqual(before_row["observed"], after_row["observed"])


if __name__ == "__main__":
    unittest.main()
