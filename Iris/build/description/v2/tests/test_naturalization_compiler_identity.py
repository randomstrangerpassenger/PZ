from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V2_ROOT.parents[3]
PREDECESSOR_TRANSITION = (
    REPO_ROOT
    / "Iris"
    / "validation"
    / "clean_checkout"
    / "evidence"
    / "g5_compiler_identity_successor_0003.json"
)
from iris_tooling.build import naturalization_compiler_identity as identity
from iris_tooling.build import public_text_quality_acceptance as consumer
from iris_tooling.build import run_dvf_3_3_korean_prose_naturalization as producer


class NaturalizationCompilerIdentityTest(unittest.TestCase):
    def synthetic_contents(self, raw: bytes) -> dict[str, bytes]:
        return {
            path: raw
            for path in identity.COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER
        }

    def test_producer_and_consumer_share_responsibility_complete_identity(self) -> None:
        self.assertIs(
            producer.build_compiler_identity,
            identity.build_compiler_identity,
        )
        self.assertIs(
            consumer.build_compiler_identity,
            identity.build_compiler_identity,
        )
        self.assertEqual(
            tuple(producer.COMPILER_IMPLEMENTATION_PATHS),
            identity.compiler_source_paths(producer.REPO_ROOT),
        )
        self.assertEqual(
            tuple(consumer.NATURALIZATION_COMPILER_IMPLEMENTATION_FILES),
            identity.compiler_source_paths(consumer.REPO_ROOT),
        )
        producer_evidence = producer.implementation_identity()
        consumer_evidence = consumer.build_compiler_identity(consumer.REPO_ROOT)
        self.assertEqual(producer_evidence, consumer_evidence)
        self.assertEqual(
            producer_evidence["algorithm_id"],
            identity.COMPILER_IDENTITY_ALGORITHM_ID,
        )
        self.assertEqual(
            producer_evidence["path_order"],
            list(identity.COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER),
        )
        self.assertEqual(
            len(producer_evidence["ordered_files"]),
            len(identity.COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER),
        )
        transition = json.loads(PREDECESSOR_TRANSITION.read_text(encoding="utf-8"))
        predecessor_evidence = {
            "algorithm_id": transition["algorithm_id"],
            "path_order": [
                row["path"]
                for row in transition["historical_gate_integration_basis"][
                    "ordered_files"
                ]
            ],
        }
        self.assertNotEqual(predecessor_evidence, producer_evidence)
        self.assertEqual(
            predecessor_evidence["algorithm_id"],
            producer_evidence["algorithm_id"],
        )
        self.assertEqual(len(predecessor_evidence["path_order"]), 9)
        current_paths = producer_evidence["path_order"]
        self.assertEqual(
            current_paths,
            list(identity.COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER),
        )
        self.assertIn(
            "Iris/tooling/src/iris_tooling/domains/public_text/naturalization_application.py",
            current_paths,
        )
        self.assertIn(
            "Iris/tooling/src/iris_tooling/domains/public_text/naturalization_transformation.py",
            current_paths,
        )
        self.assertIn(
            "Iris/tooling/src/iris_tooling/domains/public_text/inputs.py",
            current_paths,
        )

    def test_working_and_git_blob_line_endings_are_metamorphic(self) -> None:
        working = self.synthetic_contents(b"alpha\r\nbeta\rgamma\n")
        git_blob = self.synthetic_contents(b"alpha\nbeta\ngamma\n")
        working_evidence = identity.build_compiler_identity_from_bytes(working)
        blob_evidence = identity.build_compiler_identity_from_bytes(git_blob)
        self.assertEqual(
            working_evidence["ordered_files"],
            blob_evidence["ordered_files"],
        )
        self.assertEqual(
            working_evidence["aggregate_sha256"],
            blob_evidence["aggregate_sha256"],
        )

    def test_one_byte_semantic_source_change_is_stale(self) -> None:
        baseline_contents = self.synthetic_contents(b"alpha\nbeta\n")
        changed_contents = dict(baseline_contents)
        changed_path = identity.COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER[0]
        changed_contents[changed_path] = b"alpha\nBeta\n"
        baseline = identity.build_compiler_identity_from_bytes(baseline_contents)
        changed = identity.build_compiler_identity_from_bytes(changed_contents)
        self.assertNotEqual(
            baseline["ordered_files"][0]["canonical_sha256"],
            changed["ordered_files"][0]["canonical_sha256"],
        )
        self.assertNotEqual(
            baseline["aggregate_sha256"],
            changed["aggregate_sha256"],
        )
        self.assertFalse(
            identity.compiler_identity_matches_claim(
                baseline["aggregate_sha256"],
                changed,
            )
        )


if __name__ == "__main__":
    unittest.main()
