from __future__ import annotations

import re
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
IRIS_MOD_ROOT = V2_ROOT.parents[2]
RUNTIME_ROOT = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris"


class Phase5ArrayUtilContractTest(unittest.TestCase):
    def test_array_util_contains_is_single_membership_helper(self) -> None:
        array_text = (RUNTIME_ROOT / "Util" / "Array.lua").read_text(encoding="utf-8")

        self.assertIn("local Array = {}", array_text)
        self.assertIn("function Array.contains(values, value)", array_text)
        self.assertIn("if not values then", array_text)
        self.assertIn("return false", array_text)
        self.assertIn("for _, candidate in ipairs(values) do", array_text)
        self.assertIn("if candidate == value then", array_text)
        self.assertIn("return Array", array_text)

    def test_static_data_keeps_array_contains_as_compatibility_alias(self) -> None:
        static_data_text = (RUNTIME_ROOT / "API" / "StaticData.lua").read_text(encoding="utf-8")

        self.assertIn('local Array = require("Iris/Util/Array")', static_data_text)
        match = re.search(
            r"function StaticData\.arrayContains\(values, value\)(.*?)end",
            static_data_text,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        body = match.group(1)
        self.assertIn("return Array.contains(values, value)", body)
        self.assertNotIn("ipairs", body)

    def test_api_membership_consumers_use_array_util_directly(self) -> None:
        tags_text = (RUNTIME_ROOT / "API" / "Tags.lua").read_text(encoding="utf-8")
        use_cases_text = (RUNTIME_ROOT / "API" / "UseCases.lua").read_text(encoding="utf-8")

        for text in (tags_text, use_cases_text):
            self.assertIn('local Array = require("Iris/Util/Array")', text)
            self.assertNotIn("StaticData.arrayContains(", text)

        self.assertIn("return Array.contains(rawTags(fullType), tag)", tags_text)
        self.assertIn('return Array.contains(rawArray("contextOutcomes", fullType), outcome)', use_cases_text)
        self.assertIn(
            'return Array.contains(rawArray("capabilities", fullType), capability)',
            use_cases_text,
        )
        self.assertIn("return Array.copy(rawTags(fullType))", tags_text)
        self.assertIn('return Array.copy(rawArray("contextOutcomes", fullType))', use_cases_text)

    def test_moveables_tag_membership_uses_array_util(self) -> None:
        moveables_text = (RUNTIME_ROOT / "Data" / "IrisMoveablesIndex.lua").read_text(encoding="utf-8")

        self.assertIn('local Array = require("Iris/Util/Array")', moveables_text)
        self.assertIn("return Array.contains(allowedTags, tag)", moveables_text)

        match = re.search(
            r"function IrisMoveablesIndex\.tagIn\(fullType, allowedTags\)(.*?)end",
            moveables_text,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        self.assertNotIn("ipairs(allowedTags)", match.group(1))


if __name__ == "__main__":
    unittest.main()
