from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import dvf_3_3_registry_runtime_compatibility as rtc


class RegistryRuntimeCompatibilityFixtureTest(unittest.TestCase):
    def test_roadmap_fixture_ids_one_through_ten_are_exact(self) -> None:
        fixture_path = (
            V2_ROOT
            / "tests"
            / "fixtures"
            / "registry_runtime_compatibility"
            / "roadmap_fixtures.json"
        )
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        ids = [row["fixture_id"] for row in payload["fixtures"]]
        self.assertEqual(ids, [f"RTC-RM-{index:02d}" for index in range(1, 11)])
        self.assertEqual(len(set(ids)), 10)

    def test_ascii_lower_is_locale_independent_and_rejects_non_ascii(self) -> None:
        self.assertEqual(rtc.ascii_lower_v1("Base.LemonGrass"), "base.lemongrass")
        with self.assertRaisesRegex(
            rtc.CompatibilityError,
            "ascii_lower_v1 rejects non-ASCII",
        ):
            rtc.ascii_lower_v1("Base.İtem")

    def test_collision_roles_do_not_collapse_exact_keys(self) -> None:
        records = [
            rtc.SurfaceRecord(
                surface="fixture",
                ordinal=index,
                decoded_key=key,
                raw_token_text=json.dumps(key),
                raw_token_bytes_sha256=rtc.sha256_bytes(key.encode()),
                payload={},
                source_path="fixture",
            )
            for index, key in enumerate(
                ("Base.LemonGrass", "Base.Lemongrass"),
                start=1,
            )
        ]
        groups = rtc.collision_groups(records)
        self.assertEqual(groups[0]["member_count"], 2)
        self.assertEqual(len({row.decoded_key for row in records}), 2)


if __name__ == "__main__":
    unittest.main()
