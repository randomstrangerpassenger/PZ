from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.layer3_current_authority_reconstruction import (  # noqa: E402
    decode_lua_string,
    parse_lua_chunk,
)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


class Layer3CurrentAuthorityReconstructionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = ROOT / "tests" / "_tmp_layer3_current_authority_reconstruction"
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    def test_decode_lua_decimal_utf8_string(self) -> None:
        self.assertEqual(decode_lua_string(r"\237\133\140\236\138\164\237\138\184\nok"), "테스트\nok")

    def test_parse_lua_chunk_extracts_runtime_fields(self) -> None:
        chunk = self.tmp_dir / "Chunk001.lua"
        write_text(
            chunk,
            '\n'.join(
                [
                    "return {",
                    '    ["Base.Sample"] = {',
                    '        ["publish_state"] = "exposed",',
                    '        ["source"] = "composed_v2_preview",',
                    '        ["text_ko"] = "\\236\\131\\152\\237\\148\\140",',
                    "    },",
                    "}",
                    "",
                ]
            ),
        )

        entries = parse_lua_chunk(chunk)

        self.assertEqual(
            entries,
            {
                "Base.Sample": {
                    "publish_state": "exposed",
                    "source": "composed_v2_preview",
                    "text_ko": "샘플",
                }
            },
        )


if __name__ == "__main__":
    unittest.main()
