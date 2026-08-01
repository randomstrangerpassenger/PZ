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
            self.assertTrue(by_path[path]["declared_identity_matches"])

    def test_windows_candidate_anchor_preserves_named_identity_domain(self) -> None:
        repo = Path(__file__).resolve().parents[5]
        record = adoption.path_record(repo, adoption.CANDIDATE_PATH, adoption.CANDIDATE_SHA256)
        self.assertEqual("working_raw_bytes", record["declared_match_domain"])
        self.assertNotEqual(record["git_blob_sha256"], record["working"]["raw_sha256"])

    def test_current_source_pair_roles_are_coherent(self) -> None:
        repo = Path(__file__).resolve().parents[5]
        manifest = adoption.load_json_from_git(repo, adoption.INPUT_MANIFEST_PATH)
        self.assertEqual("successor_current_source_authority", manifest["authority_role"])
        self.assertEqual("current_source_authority", manifest["facts"]["role"])
        self.assertEqual(adoption.FACTS_SHA256, manifest["facts"]["sha256"])


if __name__ == "__main__":
    unittest.main()
