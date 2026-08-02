from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
MODULE_PATH = REPO / "Iris/validation/residual_refactor/validate_evidence_roles.py"
SPEC = importlib.util.spec_from_file_location("iris_residual_evidence_roles", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
EVIDENCE = REPO / "Iris/_docs/refactor/residual_refactor"


class IrisResidualEvidenceRolesTest(unittest.TestCase):
    def test_role_schema_index_and_manual_classes_are_fail_closed(self) -> None:
        schema = json.loads((EVIDENCE / "evidence_role.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "iris-residual-evidence-role-v1")
        manual = json.loads(
            (EVIDENCE / "manual_runtime_validation.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(manual["properties"]["class_summaries"]["required"]),
            {"runtime_ui", "operator_contract"},
        )
        index = json.loads((EVIDENCE / "current_evidence_index.json").read_text(encoding="utf-8"))
        self.assertFalse(index["authority_claim"])
        self.assertTrue(index["index_projection"])

        with tempfile.TemporaryDirectory(prefix="iris-residual-role-") as temp:
            artifact = Path(temp) / "artifact.json"
            artifact.write_text("{}\n", encoding="utf-8")
            relative = artifact.resolve().relative_to(REPO.resolve()) if artifact.resolve().is_relative_to(REPO.resolve()) else None
            valid = {
                "schema_version": "iris-residual-evidence-role-v1",
                "role": "diagnostic",
                "created_at": "2026-08-03T00:00:00Z",
                "producer": "test",
                "producer_readpoint": "fixture",
                "command": ["python", "fixture"],
                "subject": {"commit": "0" * 40, "tree": "1" * 40, "overlay_sha256_or_null": None},
                "inputs": [],
                "outputs": [],
                "mutable": False,
                "supersedes": [],
                "authority_claim": False,
            }
            manifest_path = EVIDENCE / "fixture.evidence.json"
            errors = MODULE.validate_manifest(valid, path=manifest_path, repository_root=REPO)
            self.assertEqual(errors, [])
            invalid = dict(valid)
            invalid["authority_claim"] = True
            invalid["mutable"] = True
            codes = {
                row["code"]
                for row in MODULE.validate_manifest(invalid, path=manifest_path, repository_root=REPO)
            }
            self.assertIn("mutable_bundle_forbidden", codes)
            self.assertIn("diagnostic_authority_claim_forbidden", codes)


if __name__ == "__main__":
    unittest.main()
