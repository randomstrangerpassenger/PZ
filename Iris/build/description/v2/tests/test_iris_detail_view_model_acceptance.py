from __future__ import annotations

import shutil
import subprocess
import sys
import unittest
from pathlib import Path

REPO = next(parent for parent in Path(__file__).resolve().parents if (parent / ".git").exists())
sys.path.insert(0, str(REPO / "Iris" / "test"))
from core_refactor_evidence import load_bound_evidence, require_case_fixtures  # noqa: E402


class DetailViewModelAcceptanceTest(unittest.TestCase):
    def test_pz_raw_food_shared_model_and_incremental_scroll(self) -> None:
        before = load_bound_evidence(
            REPO, "Iris/_docs/refactor/core_refactor/phase1_pre_refactor_pz_baseline.jsonl"
        )
        after = load_bound_evidence(
            REPO, "Iris/_docs/refactor/core_refactor/phase4_detail_acceptance.jsonl"
        )
        require_case_fixtures(after, {
            "detail_acceptance.food_units": "Base.Apple",
            "detail_acceptance.browser_wiki_shared": "Base.Apple",
            "detail_acceptance.layer3_availability": "adopted_and_unadopted",
            "detail_acceptance.incremental_scroll": "Base.Hammer",
        })
        rows = {row["case_id"]: row for row in after}
        self.assertEqual(
            {
                "detail_acceptance.food_units",
                "detail_acceptance.browser_wiki_shared",
                "detail_acceptance.layer3_availability",
                "detail_acceptance.incremental_scroll",
            },
            rows.keys(),
        )
        self.assertTrue(all(row["owner_change"] == 5 for row in after))
        self.assertTrue(all(row["status"] == "pass" for row in after))
        self.assertTrue(all(row["time_axis"] == "post_refactor_acceptance" for row in after))

        before_rows = {row["case_id"]: row for row in before}
        old_food = before_rows["detail.food_pz_units"]["observed"]
        new_food = rows["detail_acceptance.food_units"]["observed"]
        for field in ("hunger", "thirst", "stress", "boredom", "core_renderer", "food_renderer"):
            self.assertEqual(old_food[field], new_food[field], field)
        self.assertTrue(new_food["item_wrapper_parity"])

        old_scroll = before_rows["scroll_click.pz_pre_refactor"]["observed"]
        new_scroll = rows["detail_acceptance.incremental_scroll"]["observed"]
        self.assertTrue(old_scroll["first_child_rebuilt"])
        self.assertTrue(new_scroll["child_identity_preserved"])
        self.assertTrue(new_scroll["repeated_identity_preserved"])
        self.assertTrue(new_scroll["model_identity_preserved"])
        self.assertGreaterEqual(new_scroll["click_target_count"], old_scroll["click_target_count"])
        self.assertGreater(new_scroll["scroll_after_first"], 0)
        self.assertLessEqual(new_scroll["scroll_after_second"], new_scroll["max_scroll"])

    def test_actual_standalone_en_ko_raw_and_availability_parity(self) -> None:
        lua = shutil.which("lua")
        self.assertIsNotNone(lua, "required standalone Lua executable is unavailable")
        completed = subprocess.run(
            [lua, str(REPO / "Iris/test/lua/detail_view_model_locale_harness.lua"), str(REPO)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("IRIS_DETAIL_LOCALE_PASS", completed.stdout)
        self.assertIn("raw_equal=true", completed.stdout)
        self.assertIn("availability_equal=true", completed.stdout)
        self.assertIn("ko_only_layer3_display=true", completed.stdout)
        self.assertIn("labels_differ=true", completed.stdout)
        self.assertIn("nested_readonly=true", completed.stdout)
        self.assertIn("interaction_lookup_once_per_build=true", completed.stdout)

    def test_shared_model_and_scroll_source_guards(self) -> None:
        model_path = REPO / "Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua"
        model = model_path.read_text(encoding="utf-8")
        for field in (
            "fullType", "displayName", "moduleName", "itemType", "weight", "category",
            "subcategory", "tags", "food", "weapon", "literature", "moveable", "layer3",
            "connections", "useCases", "interactionState", "capabilities", "availability",
        ):
            self.assertIn(field, model)
        for forbidden in ("recommendation", "compareScore", "qualityScore", "priorityScore"):
            self.assertNotIn(f"{forbidden} =", model)
        self.assertIn("IrisItemDetailViewModel is read-only", model)

        detail_path = REPO / "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua"
        detail = detail_path.read_text(encoding="utf-8")
        wheel = detail.split("function IrisBrowser:onDetailMouseWheel", 1)[1].split(
            "function IrisBrowser:onToggleRecipeSection", 1
        )[0]
        self.assertNotIn("showDetail", wheel)
        self.assertNotIn("rebuildDetailContent", wheel)
        self.assertIn("applyDetailScrollOffset", wheel)
        self.assertIn("DetailViewModel.fromItem(item)", detail)
        self.assertIn('local koPresentation = tostring(model.locale or "EN"):upper() == "KO"', detail)

        wiki = (REPO / "Iris/media/lua/client/Iris/UI/Wiki/IrisWikiPanel.lua").read_text(encoding="utf-8")
        sections = (REPO / "Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua").read_text(encoding="utf-8")
        collector = (REPO / "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionCollector.lua").read_text(encoding="utf-8")
        self.assertIn("DetailViewModel.ensure(item)", wiki)
        self.assertIn("DetailViewModel.ensure(item)", sections)
        self.assertIn("interactionState", collector)
        self.assertNotIn("model.connections", collector)
        self.assertNotIn("model.capabilities", collector)

if __name__ == "__main__":
    unittest.main()
