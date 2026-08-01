from __future__ import annotations

import sys
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parents[1] / "tools" / "build"
sys.path.insert(0, str(TOOLS))

import validated_naturalization_runtime_adoption as adoption


class ValidatedNaturalizationRuntimeAdoptionTest(unittest.TestCase):
    def test_declared_anchors_are_full_lowercase_sha256(self) -> None:
        self.assertTrue(adoption.ANCHORS)
        self.assertTrue(all(adoption.SHA256_RE.fullmatch(value) for value in adoption.ANCHORS.values()))

    def test_phase0_census_is_read_only_and_anchor_exact(self) -> None:
        repo = Path(__file__).resolve().parents[5]
        records = adoption.census(repo, adoption.PROTECTED_PATHS)
        by_path = {record["path"]: record for record in records}
        for path in adoption.ANCHORS:
            self.assertTrue(by_path[path]["git_tracked"])
            self.assertTrue(by_path[path]["declared_matches_git_blob_bytes"])

    def test_current_source_pair_roles_are_coherent(self) -> None:
        repo = Path(__file__).resolve().parents[5]
        manifest = adoption.load_json_from_git(repo, adoption.INPUT_MANIFEST_PATH)
        self.assertEqual("successor_current_source_authority", manifest["authority_role"])
        self.assertEqual("current_source_authority", manifest["facts"]["role"])
        self.assertEqual(adoption.FACTS_SHA256, manifest["facts"]["sha256"])


if __name__ == "__main__":
    unittest.main()
