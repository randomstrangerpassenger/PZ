from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
CODEC_ROOT = REPO / "Iris/validation/residual_refactor"
sys.path.insert(0, str(CODEC_ROOT))

from execute_artifact_lifecycle import durable_lifecycle_source  # noqa: E402
from promote_artifact_lifecycle_evidence import load_lifecycle_source  # noqa: E402
from repository_evidence_codec import (  # noqa: E402
    BASELINE_NAME,
    DELTA_NAME,
    DICTIONARY_NAME,
    NODES_NAME,
    build_v2_payloads,
    decode_v2_root,
    materialize_manifest,
)


V2_ROOT = (
    REPO
    / "Iris/_docs/refactor/repository_evidence_lightweighting/lifecycle_manifest_v2"
)
RUNTIME_ROOT = REPO / "Iris/_docs/refactor/repository_runtime_lightweighting"


class RepositoryEvidenceMigrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receipt = json.loads((V2_ROOT / "migration_receipt.json").read_text(encoding="utf-8"))
        cls.bundle = decode_v2_root(V2_ROOT)

    def test_adopted_v1_views_are_reconstructed_byte_identically(self) -> None:
        receipt = self.receipt
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(
            (len(self.bundle.baseline_rows), len(self.bundle.final_rows), self.bundle.shared_rows),
            (7512, 7515, 6737),
        )
        self.assertEqual(
            hashlib.sha256(self.bundle.baseline_bytes).hexdigest(),
            receipt["source_v1"]["baseline"]["sha256"],
        )
        self.assertEqual(len(self.bundle.baseline_bytes), receipt["source_v1"]["baseline"]["bytes"])
        self.assertEqual(
            hashlib.sha256(self.bundle.final_bytes).hexdigest(),
            receipt["source_v1"]["final"]["sha256"],
        )
        self.assertEqual(len(self.bundle.final_bytes), receipt["source_v1"]["final"]["bytes"])

    def test_v2_components_are_deterministic_and_smaller_than_the_v1_pair(self) -> None:
        rebuilt = build_v2_payloads(self.bundle.baseline_rows, self.bundle.final_rows)
        for name in (DICTIONARY_NAME, NODES_NAME, BASELINE_NAME, DELTA_NAME):
            self.assertEqual(rebuilt[name], (V2_ROOT / name).read_bytes())
        v2_bytes = sum(len(payload) for payload in rebuilt.values())
        v1_bytes = sum(row["bytes"] for row in self.receipt["source_v1"].values())
        self.assertLess(v2_bytes, v1_bytes)

    def test_promoter_and_executor_select_one_v2_representation(self) -> None:
        promoted_bytes, promoted_rows, promoted_representation = load_lifecycle_source(V2_ROOT, "final")
        self.assertEqual(promoted_representation, "v2")
        self.assertEqual(promoted_bytes, self.bundle.final_bytes)
        self.assertEqual(promoted_rows, self.bundle.final_rows)

        source, executed_bytes, executed_rows, executed_representation = durable_lifecycle_source(
            RUNTIME_ROOT / "baseline_inventory.json"
        )
        self.assertEqual(executed_representation, "v2")
        self.assertEqual(source, V2_ROOT.resolve())
        self.assertEqual(executed_bytes, self.bundle.baseline_bytes)
        self.assertEqual(executed_rows, self.bundle.baseline_rows)

    def test_report_inventory_no_change_disposition_is_sealed(self) -> None:
        disposition = self.receipt["inventory_reader_disposition"]
        self.assertEqual(disposition["status"], "sealed_no_change")
        self.assertEqual(disposition["ast_exact_string_hits"], [])
        self.assertEqual(disposition["lexical_exact_name_hits"], [])

    def test_codec_materializer_rejects_representation_mixing_by_construction(self) -> None:
        baseline_bytes, _, baseline_representation = materialize_manifest(V2_ROOT, "baseline")
        final_bytes, _, final_representation = materialize_manifest(V2_ROOT, "final")
        self.assertEqual((baseline_representation, final_representation), ("v2", "v2"))
        self.assertEqual((baseline_bytes, final_bytes), (self.bundle.baseline_bytes, self.bundle.final_bytes))


if __name__ == "__main__":
    unittest.main()

