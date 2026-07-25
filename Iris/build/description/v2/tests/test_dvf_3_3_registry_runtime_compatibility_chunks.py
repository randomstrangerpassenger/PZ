from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[5]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import dvf_3_3_registry_runtime_compatibility as rtc


class RegistryRuntimeCompatibilityChunkTest(unittest.TestCase):
    def test_lua_decimal_escape_decodes_before_identity_comparison(self) -> None:
        self.assertEqual(
            rtc.decode_lua_string(r'"Base.\076emonGrass"'),
            "Base.LemonGrass",
        )

    def test_json_escaped_key_retains_raw_token_and_decoded_identity(self) -> None:
        text = r'{"\u0042ase.LemonGrass":{"source":"fixture"}}'
        pairs, end = rtc.raw_json_object_pairs(text, 0)
        self.assertEqual(end, len(text))
        self.assertEqual(pairs[0][0], r'"\u0042ase.LemonGrass"')
        self.assertEqual(pairs[0][1], "Base.LemonGrass")

    def test_actual_lua_reconstruction_preserves_2105_exact_keys(self) -> None:
        harness = (
            V2_ROOT
            / "tests"
            / "fixtures"
            / "registry_runtime_compatibility"
            / "lua_merge_harness.lua"
        )
        client_root = REPO_ROOT / "Iris" / "media" / "lua" / "client"
        completed = subprocess.run(
            ["lua", str(harness), str(client_root), "2105"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["exact_key_count"], 2105)
        self.assertEqual(payload["collision_group_count"], 1)


if __name__ == "__main__":
    unittest.main()
