"""Cross-track regression fixture for Iris evidence pipelines."""
from __future__ import annotations

import hashlib
import subprocess
import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
IRIS_DIR = ROOT_DIR / "Iris"
OUTPUT_DIR = IRIS_DIR / "output"

RIGHTCLICK_OUTPUTS = [
    "evidence_candidates.v2.4.json",
    "evidence_decisions.v2.4.json",
    "field_registry.v2.4.json",
    "review_queue.v2.4.json",
    "uniqueness_overlay.v2.4.json",
    "property_based_items.v2.4.json",
]

RECIPE_OUTPUTS = [
    "recipe_index.v2.4.json",
    "recipes_by_fulltype.v2.4.json",
    "recipe_evidence_decisions.v2.4.json",
    "recipe_review_queue.v2.4.json",
    "dynamic_expr_catalog.v2.4.json",
    "dynamic_group_policy.v2.4.json",
    "requirements_by_fulltype.v2.4.json",
]


def file_hashes(filenames: list[str]) -> dict[str, str]:
    hashes = {}
    for filename in filenames:
        path = OUTPUT_DIR / filename
        if not path.exists():
            raise AssertionError(f"missing fixture output: {path}")
        hashes[filename] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


class EvidencePipelineCrossTrackTest(unittest.TestCase):
    maxDiff = None

    def run_pipeline(self, *args: str) -> None:
        result = subprocess.run(
            [sys.executable, "-B", *args],
            cwd=ROOT_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if result.returncode != 0:
            tail = result.stdout[-4000:]
            self.fail(f"pipeline failed ({args}):\n{tail}")

    def test_recipe_and_rightclick_outputs_do_not_cross_mutate(self) -> None:
        rightclick_before = file_hashes(RIGHTCLICK_OUTPUTS)
        self.run_pipeline(str(IRIS_DIR / "build" / "recipe_evidence_pipeline.py"))
        self.assertEqual(rightclick_before, file_hashes(RIGHTCLICK_OUTPUTS))

        recipe_before = file_hashes(RECIPE_OUTPUTS)
        self.run_pipeline(
            str(IRIS_DIR / "build" / "rightclick_evidence_pipeline.py"),
            "--v24",
        )
        self.assertEqual(recipe_before, file_hashes(RECIPE_OUTPUTS))


if __name__ == "__main__":
    unittest.main()
