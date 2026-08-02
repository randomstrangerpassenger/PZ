from __future__ import annotations

import shutil
import subprocess
import sys
import unittest
from pathlib import Path

REPO = next(parent for parent in Path(__file__).resolve().parents if (parent / ".git").exists())
sys.path.insert(0, str(REPO / "Iris" / "test"))
from core_refactor_evidence import load_bound_evidence, require_case_fixtures  # noqa: E402


class BrowserStateSelectionSearchAcceptanceTest(unittest.TestCase):
    def test_pz_acceptance_and_pre_refactor_relations(self) -> None:
        before = load_bound_evidence(
            REPO, "Iris/_docs/refactor/core_refactor/phase1_pre_refactor_pz_baseline.jsonl"
        )
        after = load_bound_evidence(
            REPO, "Iris/_docs/refactor/core_refactor/phase3_browser_acceptance.jsonl"
        )
        require_case_fixtures(after, {
            "browser_acceptance.pz_startup": "browser_open_startup",
            "browser_acceptance.state_machine": "uninitialized_building_ready",
            "browser_acceptance.required_retry": "missing_tags_then_browser_open",
            "browser_acceptance.optional_degraded": "missing_optional_index",
            "browser_acceptance.selection_matrix": "event_fallback_invalid",
            "browser_acceptance.search_pz": "hammer_casefold_repeat",
            "browser_acceptance.folded_count_pz": "tool_repeat",
        })
        rows = {row["case_id"]: row for row in after}
        required = {
            "browser_acceptance.pz_startup",
            "browser_acceptance.state_machine",
            "browser_acceptance.required_retry",
            "browser_acceptance.optional_degraded",
            "browser_acceptance.selection_matrix",
            "browser_acceptance.search_pz",
            "browser_acceptance.folded_count_pz",
        }
        self.assertEqual(required, rows.keys())
        self.assertTrue(all(row["owner_change"] == 4 for row in after))
        self.assertTrue(all(row["status"] == "pass" for row in after))
        self.assertTrue(all(row["time_axis"] == "post_refactor_acceptance" for row in after))

        before_by_id = {row["case_id"]: row for row in before}
        selection = rows["browser_acceptance.selection_matrix"]["observed"]
        self.assertEqual(before_by_id["selection.pz_payloads"]["observed"]["event"], selection["event"])
        self.assertEqual(before_by_id["selection.pz_payloads"]["observed"]["fallback"], selection["fallback"])
        self.assertEqual(
            before_by_id["browser_build.pz_lifecycle"]["observed"]["search_count"],
            rows["browser_acceptance.search_pz"]["observed"]["search_count"],
        )

    def test_actual_standalone_lua_state_and_cache_contracts(self) -> None:
        lua = shutil.which("lua")
        self.assertIsNotNone(lua, "required standalone Lua executable is unavailable")
        completed = subprocess.run(
            [lua, str(REPO / "Iris/test/lua/browser_state_acceptance_harness.lua"), str(REPO)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("IRIS_BROWSER_STANDALONE_PASS", completed.stdout)
        self.assertIn("normalized_getter_calls=0", completed.stdout)
        self.assertIn("optional_load_calls=2", completed.stdout)
        self.assertIn("folded_cache_entries=1", completed.stdout)

    def test_browserdata_compatibility_and_logging_source_guards(self) -> None:
        browser_root = REPO / "Iris/media/lua/client/Iris/UI/Browser"
        data_path = browser_root / "IrisBrowserData.lua"
        data_text = data_path.read_text(encoding="utf-8")
        self.assertEqual(1, data_text.count("IrisBrowserData._built ="))
        self.assertIn("function IrisBrowserData.getBuildState()", data_text)
        self.assertIn("function IrisBrowserData.isReady()", data_text)
        self.assertIn("function IrisBrowserData.ensureReady()", data_text)

        forbidden = []
        for path in browser_root.glob("*.lua"):
            if path == data_path:
                continue
            text = path.read_text(encoding="utf-8")
            if "IrisBrowserData._built" in text or "BrowserData._built" in text:
                forbidden.append(path.name)
        self.assertEqual([], forbidden)

        controller = (browser_root / "IrisBrowserListController.lua").read_text(encoding="utf-8")
        self.assertIn("resolveSelectedPayload", controller)
        self.assertNotIn("for k, v in pairs(item)", controller)
        self.assertNotIn("for k, v in pairs(itemData)", controller)

        query = (browser_root / "IrisBrowserQuery.lua").read_text(encoding="utf-8")
        self.assertIn("searchKeysByFullType", query)
        static_data = (REPO / "Iris/media/lua/client/Iris/API/StaticData.lua").read_text(encoding="utf-8")
        self.assertIn("function StaticData.getFailureReason(key)", static_data)
        self.assertIn("function StaticData.reset(key)", static_data)


if __name__ == "__main__":
    unittest.main()
