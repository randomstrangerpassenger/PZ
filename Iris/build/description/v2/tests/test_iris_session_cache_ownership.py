from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
EVIDENCE = REPO / "Iris/_docs/refactor/codebase_optimization_followup"


class IrisSessionCacheOwnershipTest(unittest.TestCase):
    def test_cache_field_census_is_complete_and_session_candidate_free(self) -> None:
        receipt = json.loads((EVIDENCE / "cache_owner_census.json").read_text(encoding="utf-8"))
        expected = {
            "BrowserData.IrisAPI",
            "BrowserData.itemsByFullType",
            "BrowserData.rowsByFullType.row.item",
            "BrowserData.rowsByFullType.derivedScalars",
            "BrowserData.classificationIndex",
            "BrowserData.foldedVariantCaches",
            "BrowserData.searchSnapshot",
            "BrowserData.searchPrefixState",
            "StaticData.cache",
            "StaticData.failuresAndWarnings",
            "TooltipSummary.authorityModules",
            "TooltipSummary.summaryByFullType",
            "AltTooltip.IrisTooltipSummaryLocal",
            "AltTooltip.displayLineCache",
            "UseCaseLookup.indexMetadataSnapshot",
            "UseCaseLookup.chunkCache",
        }
        rows = receipt["fields"]
        self.assertEqual(expected, {row["id"] for row in rows})
        self.assertEqual(len(expected), len(rows))
        for row in rows:
            self.assertIn(row["category"], {
                "process_stable_static", "locale_dependent", "session_dependent_engine_object"
            })
            for key in ("owner", "construction_input", "invalidation_trigger", "evidence"):
                self.assertTrue(row[key], (row["id"], key))
        self.assertEqual(0, receipt["session_dependent_engine_object_candidates"])
        self.assertEqual("complete/no-op", receipt["change_2_disposition"])
        self.assertEqual(0, receipt["production_session_wiring_diff"])

        # The predecessor census stays historical. T3 retires these two Alt
        # caches without changing Summary's supported copy-on-read boundary.
        alt = (REPO / "Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua").read_text(encoding="utf-8")
        self.assertNotIn("local displayLineCache =", alt)
        self.assertNotIn("IrisTooltipSummaryLocal", alt)
        self.assertIn('require("Iris/Data/IrisTooltipStaticDataLookup")', alt)

    def test_no_production_session_reset_wiring_was_added(self) -> None:
        runtime = REPO / "Iris/media/lua/client/Iris"
        callers = []
        for path in runtime.rglob("*.lua"):
            text = path.read_text(encoding="utf-8")
            if "resetForReload(" in text and path.name not in {
                "IrisBrowserData.lua", "IrisBrowserLifecycle.lua"
            }:
                callers.append(path.relative_to(REPO).as_posix())
        self.assertEqual([], callers)
        main = (runtime / "IrisMain.lua").read_text(encoding="utf-8")
        self.assertNotIn("OnMainMenuEnter", main)

    def test_phase_0b_absence_only_defers_timing_branches(self) -> None:
        baseline = json.loads((EVIDENCE / "baseline_manifest.json").read_text(encoding="utf-8"))
        self.assertFalse(baseline["phase_0b"]["executed"])
        self.assertEqual("deferred_by_design", baseline["phase_0b"]["dependent_branches"])
        self.assertFalse(baseline["instrumentation"]["default_enabled"])


if __name__ == "__main__":
    unittest.main()
