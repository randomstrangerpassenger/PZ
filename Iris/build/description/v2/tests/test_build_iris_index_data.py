from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.build_iris_fixing_index_data import parse_fixers
from tools.build.build_iris_moveables_index_data import build_index as build_moveables_index
from tools.build.build_iris_recipe_index_data import build_index as build_recipe_index


class BuildIrisIndexDataTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = ROOT / "tests" / "_tmp_iris_index_data"
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    def test_recipe_index_builds_roles_and_allowed_get_item_types(self) -> None:
        recipe_index = {
            "version": "v-test",
            "recipes": {
                "slice": {
                    "recipe_name": "Slice",
                    "category": "Cooking",
                    "inputs": ["Base.Bread", "Knife"],
                    "keeps": ["Base.Pan"],
                },
                "toast": {
                    "recipe_name": "Toast",
                    "category": "Cooking",
                    "inputs": ["Base.Bread"],
                    "keeps": [],
                },
            },
        }
        dynamic_catalog = {
            "groups": {
                "CanOpener": {
                    "status": "resolved",
                    "matched_fulltypes": ["Base.TinOpener"],
                }
            }
        }

        data = build_recipe_index(recipe_index, dynamic_catalog)

        self.assertEqual(data["version"], "v-test")
        self.assertEqual(len(data["itemRoles"]["Base.Bread"]), 2)
        self.assertEqual(data["itemRoles"]["Base.Knife"][0]["role"], "input")
        self.assertEqual(data["itemRoles"]["Base.Pan"][0]["role"], "keep")
        self.assertEqual(data["getItemTypes"]["CanOpener"], ["Base.TinOpener"])

    def test_moveables_index_expands_tags_and_direct_items(self) -> None:
        script_root = self.tmp_dir / "scripts"
        script_root.mkdir()
        (script_root / "items.txt").write_text(
            "\n".join(
                [
                    "module Base",
                    "{",
                    "    item Hammer",
                    "    {",
                    "        Tags = Hammer,",
                    "    }",
                    "    item Crowbar",
                    "    {",
                    "        Tags = Crowbar,",
                    "    }",
                    "    item PipeWrench",
                    "    {",
                    "    }",
                    "}",
                ]
            ),
            encoding="utf-8",
        )
        moveables_lua = self.tmp_dir / "ISMoveableDefinitions.lua"
        moveables_lua.write_text(
            "\n".join(
                [
                    'local ItemTypeToTag = { ["Base.Hammer"] = "Hammer", ["Tag.Crowbar"] = "Crowbar" }',
                    'moveableDefinitions.addToolDefinition( "Hammer", {"Base.Hammer"}, Perks.Woodwork, 75, "Hammering", true );',
                    'moveableDefinitions.addToolDefinition( "Crowbar", {"Tag.Crowbar", "Crowbar"}, Perks.Woodwork, 150, "Hammering", true );',
                    'moveableDefinitions.addToolDefinition( "Wrench", {"Base.PipeWrench"}, nil, 100, "RepairWithWrench", true );',
                ]
            ),
            encoding="utf-8",
        )

        data = build_moveables_index(script_root, moveables_lua)

        self.assertIn("Base.Hammer", data["registered"])
        self.assertIn("Base.Crowbar", data["registered"])
        self.assertIn("Base.PipeWrench", data["registered"])
        self.assertEqual(data["tagMapping"]["Base.Hammer"], "Hammer")
        self.assertEqual(data["tagMapping"]["Base.Crowbar"], "Crowbar")
        self.assertEqual(data["tagMapping"]["Base.PipeWrench"], "Wrench")

    def test_fixing_index_extracts_first_fixer_item(self) -> None:
        fixing = self.tmp_dir / "fixing.txt"
        fixing.write_text(
            "\n".join(
                [
                    "module Base",
                    "{",
                    "    fixing Fix Axe",
                    "    {",
                    "        Fixer : Woodglue=2; Woodwork=2,",
                    "        Fixer : Base.DuctTape=2,",
                    "    }",
                    "}",
                ]
            ),
            encoding="utf-8",
        )

        fixers = parse_fixers([fixing])

        self.assertEqual(fixers, {"Base.Woodglue", "Base.DuctTape"})


if __name__ == "__main__":
    unittest.main()
