from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

REPO = next(parent for parent in Path(__file__).resolve().parents if (parent / ".git").exists())


class DetailViewModelAcceptanceTest(unittest.TestCase):
    def test_actual_standalone_en_ko_localized_payload_and_availability_parity(self) -> None:
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
        self.assertIn("localized_layer2=true", completed.stdout)
        self.assertIn("localized_layer3=true", completed.stdout)
        self.assertIn("availability_equal=true", completed.stdout)
        self.assertIn("labels_differ=true", completed.stdout)
        self.assertIn("nested_readonly=true", completed.stdout)
        self.assertIn("interaction_lookup_once_per_build=true", completed.stdout)

    def test_shared_model_and_scroll_source_guards(self) -> None:
        model_path = REPO / "Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua"
        model = model_path.read_text(encoding="utf-8")
        assembler = (model_path.parent / "IrisItemDetailModelAssembler.lua").read_text(encoding="utf-8")
        reader = (model_path.parent / "IrisItemFactReader.lua").read_text(encoding="utf-8")
        presentation = (model_path.parent / "IrisItemDetailPresentation.lua").read_text(encoding="utf-8")
        for field in (
            "fullType", "displayName", "moduleName", "itemType", "weight", "category",
            "subcategory", "tags", "food", "weapon", "literature", "moveable", "layer3",
            "connections", "useCases", "interactionState", "capabilities", "availability",
        ):
            self.assertIn(field, assembler)
        for forbidden in ("recommendation", "compareScore", "qualityScore", "priorityScore"):
            self.assertNotIn(f"{forbidden} =", assembler)
            self.assertNotIn(forbidden, presentation)
        self.assertIn("IrisItemDetailViewModel is read-only", assembler)
        self.assertIn("IrisItemDetailModelAssembler", model)
        self.assertIn('ObjectAccess.call(item, methodName)', reader)
        self.assertNotIn("ObjectAccess.call", assembler)
        self.assertIn("function Presentation.semanticSnapshot", presentation)
        self.assertIn("math.min(4", presentation)

        detail_path = REPO / "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua"
        detail = detail_path.read_text(encoding="utf-8")
        wheel = detail.split("function IrisBrowser:onDetailMouseWheel", 1)[1].split(
            "function IrisBrowser:onToggleRecipeSection", 1
        )[0]
        self.assertNotIn("showDetail", wheel)
        self.assertNotIn("rebuildDetailContent", wheel)
        self.assertIn("applyDetailScrollOffset", wheel)
        self.assertIn("DetailViewModel.fromItem(item)", detail)

        wiki = (REPO / "Iris/media/lua/client/Iris/UI/Wiki/IrisWikiPanel.lua").read_text(encoding="utf-8")
        sections = (REPO / "Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua").read_text(encoding="utf-8")
        collector = (REPO / "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionCollector.lua").read_text(encoding="utf-8")
        self.assertIn("DetailViewModel.ensure(item)", wiki)
        self.assertIn("DetailViewModel.ensure(item)", sections)
        self.assertIn("interactionState", collector)
        self.assertNotIn("model.connections", collector)
        self.assertNotIn("model.capabilities", collector)

    def test_fact_reader_states_and_tooltip_bound(self) -> None:
        lua = shutil.which("lua")
        self.assertIsNotNone(lua, "required standalone Lua executable is unavailable")
        completed = subprocess.run(
            [lua, str(REPO / "Iris/test/lua/detail_fact_reader_harness.lua"), str(REPO)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("IRIS_DETAIL_FACT_READER_PASS", completed.stdout)

if __name__ == "__main__":
    unittest.main()
