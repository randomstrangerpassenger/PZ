from __future__ import annotations

import importlib.util
import shutil
import subprocess
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
GENERATOR_PATH = REPO / "Iris/build/convert_descriptions_to_lua.py"
HARNESS = REPO / "Iris/test/lua/generated_lua_sparse_fields_harness.lua"


def load_generator():
    spec = importlib.util.spec_from_file_location("iris_sparse_generator", GENERATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GeneratedLuaSparseFieldsContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.generator = load_generator()
        cls.descriptions = cls.generator.load_json(cls.generator.DESCRIPTIONS_PATH)
        cls.nav = cls.generator.load_json(cls.generator.NAV_REGISTRY_PATH)
        cls.requirements = cls.generator.load_json(cls.generator.RECIPE_REQ_INDEX_PATH)

    def generate(self):
        return self.generator.convert_to_lua(
            self.descriptions,
            self.nav,
            self.requirements,
        )

    def test_sparse_fields_are_deterministic_and_tracked_outputs_are_current(self) -> None:
        first = self.generate()
        second = self.generate()
        self.assertEqual(first, second)

        facade, chunks, requirements, count, _line_count, errors = first
        self.assertEqual([], errors)
        self.assertEqual(1631, count)
        combined = "\n".join(content for _index, content, _count in chunks)
        self.assertNotIn("strength = nil", combined)
        self.assertNotIn("uniqueness = nil", combined)
        self.assertNotIn("category = nil", combined)
        self.assertIn(
            "if entry.debug_lines == nil then entry.debug_lines = {} end",
            facade,
        )

        source_entries = self.descriptions["fulltypes"]
        expected_debug_fields = sum(
            bool(entry.get("use_case_block", {}).get("debug_items", []))
            for entry in source_entries.values()
        )
        self.assertEqual(expected_debug_fields, combined.count("    debug_lines = {"))
        self.assertLess(expected_debug_fields, count)

        output_root = REPO / "Iris/media/lua/client/Iris/Data"
        self.assertEqual(
            facade,
            (output_root / "IrisUseCaseDescriptions.lua").read_text(encoding="utf-8"),
        )
        for index, content, _entry_count in chunks:
            self.assertEqual(
                content,
                (output_root / f"UseCaseDescriptions/Chunk{index:03d}.lua").read_text(
                    encoding="utf-8"
                ),
            )
        self.assertEqual(
            requirements,
            (output_root / "UseCaseDescriptions/RequirementsLookup.lua").read_text(
                encoding="utf-8"
            ),
        )
        self.assertEqual(
            self.generator.build_usecase_chunk_index(self.descriptions, chunks),
            (output_root / "UseCaseDescriptions/ChunkIndex.lua").read_text(
                encoding="utf-8"
            ),
        )
        self.assertEqual(
            self.generator.build_usecase_line_count_index(self.descriptions),
            (output_root / "UseCaseDescriptions/LineCountIndex.lua").read_text(
                encoding="utf-8"
            ),
        )

    def test_direct_facade_shape_alias_and_load_order_contract(self) -> None:
        lua = shutil.which("lua")
        self.assertIsNotNone(lua, "required standalone Lua executable is unavailable")
        completed = subprocess.run(
            [lua, str(HARNESS), str(REPO)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("IRIS_GENERATED_SPARSE_FIELDS_PASS", completed.stdout)
        self.assertIn("facade_entries=1631", completed.stdout)


if __name__ == "__main__":
    unittest.main()
