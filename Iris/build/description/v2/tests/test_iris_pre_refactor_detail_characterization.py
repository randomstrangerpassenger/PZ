from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = next(parent for parent in Path(__file__).resolve().parents if (parent / ".git").exists())
sys.path.insert(0, str(REPO / "Iris" / "test"))
from core_refactor_evidence import load_bound_evidence, require_cases  # noqa: E402


class PreRefactorDetailCharacterizationTest(unittest.TestCase):
    def test_detail_food_scroll_and_legacy_cases_are_bound(self) -> None:
        headless = load_bound_evidence(REPO, "Iris/_docs/refactor/core_refactor/phase1_pre_refactor_headless_baseline.jsonl")
        pz = load_bound_evidence(REPO, "Iris/_docs/refactor/core_refactor/phase1_pre_refactor_pz_baseline.jsonl")
        require_cases(
            headless,
            {"detail.food_raw_units": "Base.Apple", "legacy.capability_tooltip": "Base.Hammer"},
            "auxiliary_standalone_puc_lua_5_4",
        )
        require_cases(
            pz,
            {
                "detail.food_pz_units": "Base.Apple",
                "legacy.pz_surface": "Base.Hammer",
                "scroll_click.pz_pre_refactor": "Base.Hammer",
            },
            "project_zomboid_b41_41_78_20",
        )
        standalone_scroll = next(row for row in headless if row["case_id"] == "scroll_click.standalone_ceiling")
        self.assertFalse(standalone_scroll["baseline_denominator_included"])
        self.assertEqual("unvalidated_but_in_scope", standalone_scroll["status"])


if __name__ == "__main__":
    unittest.main()
