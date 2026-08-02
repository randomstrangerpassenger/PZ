from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = next(parent for parent in Path(__file__).resolve().parents if (parent / ".git").exists())
sys.path.insert(0, str(REPO / "Iris" / "test"))
from core_refactor_evidence import load_bound_evidence, require_cases  # noqa: E402


class PreRefactorDescriptionCharacterizationTest(unittest.TestCase):
    def test_description_cases_are_bound_in_both_runtimes(self) -> None:
        required = {
            "description.base_hammer": "Base.Hammer",
            "description.base_pan": "Base.Pan",
            "description.base_whiskeyfull": "Base.WhiskeyFull",
            "description.nil_fallback": "nil_input",
        }
        headless = load_bound_evidence(REPO, "Iris/_docs/refactor/core_refactor/phase1_pre_refactor_headless_baseline.jsonl")
        pz = load_bound_evidence(REPO, "Iris/_docs/refactor/core_refactor/phase1_pre_refactor_pz_baseline.jsonl")
        require_cases(headless, required, "auxiliary_standalone_puc_lua_5_4")
        require_cases(pz, required, "project_zomboid_b41_41_78_20")


if __name__ == "__main__":
    unittest.main()
