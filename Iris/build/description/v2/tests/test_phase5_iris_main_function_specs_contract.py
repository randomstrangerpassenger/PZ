from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
IRIS_MAIN = REPO / "Iris/media/lua/client/Iris/IrisMain.lua"


class Phase5IrisMainFunctionSpecsContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = IRIS_MAIN.read_text(encoding="utf-8")
        cls.specs = cls.source.split("local INIT_MODULES = {", 1)[1].split(
            "\n}\n\nlocal DEV_TESTHARNESS_MODULE", 1
        )[0]

    def test_init_module_specs_do_not_use_string_dispatch_keys(self) -> None:
        self.assertNotIn("loadMethod =", self.specs)
        self.assertNotIn("invokeMethod =", self.specs)
        self.assertNotIn("spec.loadMethod", self.source)
        self.assertNotIn("spec.invokeMethod", self.source)

    def test_init_modules_preserve_boot_order(self) -> None:
        modules = re.findall(r'loadModule\("([^"]+)"\)', self.specs)
        self.assertEqual(
            modules,
            [
                "Iris/IrisAPI",
                "Iris/UI/Tooltip/IrisAltTooltip",
                "Iris/Compat/IrisContextMenuTextureCompat",
                "Iris/Compat/IrisBulletReloadCompat",
                "Iris/UI/Wiki/IrisContextMenu",
                "Iris/UI/Browser/IrisBrowserData",
                "Iris/UI/Browser/IrisMapIcon",
            ],
        )
        for eager_static_module in (
            "Iris/Data/IrisRecipeIndex",
            "Iris/Data/IrisMoveablesIndex",
            "Iris/Data/IrisFixingIndex",
            "Iris/Data/IrisClassifications",
        ):
            self.assertNotIn(eager_static_module, self.specs)

    def test_init_modules_use_function_fields(self) -> None:
        rows = [line.strip() for line in self.specs.splitlines() if line.strip().startswith("{")]
        self.assertEqual(len(rows), 7)
        self.assertTrue(all("load = loadModule(" in row for row in rows))
        browser_data = next(row for row in rows if 'label = "IrisBrowserData"' in row)
        self.assertIn('ready = "BrowserData demand-build boundary ready"', browser_data)
        self.assertNotIn("invoke =", browser_data)
        self.assertNotIn("local function buildBrowserData", self.source)

    def test_run_module_spec_calls_function_fields_directly(self) -> None:
        body = self.source.split("local function runModuleSpec(spec)", 1)[1].split(
            "\nend\n\nlocal function runStartupTests", 1
        )[0]
        self.assertIn("local moduleOk, moduleResult = spec.load()", body)
        self.assertIn("spec.onLoaded(moduleResult)", body)
        self.assertIn("return spec.invoke(moduleResult)", body)


if __name__ == "__main__":
    unittest.main()
