from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = next(parent for parent in Path(__file__).resolve().parents if (parent / ".git").exists())
sys.path.insert(0, str(REPO / "Iris" / "test"))
from core_refactor_evidence import load_bound_evidence, require_cases  # noqa: E402


class PreRefactorBrowserCharacterizationTest(unittest.TestCase):
    def test_selection_build_and_search_cases_are_bound(self) -> None:
        headless = load_bound_evidence(REPO, "Iris/_docs/refactor/core_refactor/phase1_pre_refactor_headless_baseline.jsonl")
        pz = load_bound_evidence(REPO, "Iris/_docs/refactor/core_refactor/phase1_pre_refactor_pz_baseline.jsonl")
        require_cases(
            headless,
            {
                "selection.event_payload",
                "selection.selected_index",
                "selection.missing",
                "selection.out_of_range",
                "browser_build.missing_api",
                "browser_build.missing_tags",
                "browser_build.boolean_lifecycle",
                "search.current_results",
            },
            "auxiliary_standalone_puc_lua_5_4",
        )
        require_cases(pz, {"selection.pz_payloads", "browser_build.pz_lifecycle"}, "project_zomboid_b41_41_78_20")


if __name__ == "__main__":
    unittest.main()

