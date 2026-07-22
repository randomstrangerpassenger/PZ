from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[5]
TOOLS_ROOT = REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tools" / "build"
RUNNER = TOOLS_ROOT / "run_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py"
VALIDATOR = TOOLS_ROOT / "validate_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py"
FIXTURE_ROOT = REPO_ROOT / "Iris" / "build" / "description" / "v2" / "tests" / "fixtures"
LIVE_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class DvfCompletionVocabularyExternalGateVocabularySplitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="dvf-completion-vocab-")
        cls.root = Path(cls.temp.name) / "fixture-check"
        cls.report_path = cls.root / "fixture_check_report.json"
        run = subprocess.run(
            [
                sys.executable,
                "-B",
                str(RUNNER),
                "--mode",
                "fixture-check",
                "--root",
                str(cls.root),
                "--fixture-root",
                str(FIXTURE_ROOT),
                "--report-path",
                str(cls.report_path),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        validate = subprocess.run(
            [
                sys.executable,
                "-B",
                str(VALIDATOR),
                "--mode",
                "fixture-check",
                "--fixture-root",
                str(FIXTURE_ROOT),
                "--report-path",
                str(cls.report_path),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if validate.returncode != 0:
            raise AssertionError(validate.stdout + validate.stderr)
        cls.report = read_json(cls.report_path)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_canonical_schema_and_negative_fixture_matrix(self) -> None:
        self.assertEqual(self.report["status"], "PASS")
        self.assertEqual(self.report["unexpected_pass_count"], 0)
        fixtures = {row["fixture"]: row for row in self.report["fixtures"]}
        for name in (
            "absence_maps_to_satisfied",
            "boolean_only_canonical_satisfied",
            "gate_pass_current",
            "historical_path_spoof_current_payload",
            "owner_pass_current",
            "owner_seal_missing_capture_metadata",
            "pass_with_notes_blocking",
            "string_path_canonical_satisfied",
        ):
            self.assertFalse(fixtures[name]["observed_pass"])
        self.assertTrue(fixtures["complete_current_canonical_satisfied"]["observed_pass"])
        self.assertTrue(fixtures["historical_legacy_pass_trace"]["observed_pass"])

    def test_live_manifest_adoption_is_additive_and_axis_qualified(self) -> None:
        manifest = read_json(LIVE_MANIFEST)
        test_ids = {row["test_id"] for row in manifest["required_tests"]}
        prefix = (
            "test_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split."
            "DvfCompletionVocabularyExternalGateVocabularySplitTest."
        )
        for method in (
            "test_canonical_schema_and_negative_fixture_matrix",
            "test_live_manifest_adoption_is_additive_and_axis_qualified",
            "test_final_report_blocks_canonical_external_review_without_external_artifacts",
        ):
            self.assertIn(prefix + method, test_ids)
        self.assertEqual(self.report["repository_write_count"], 0)

    def test_final_report_blocks_canonical_external_review_without_external_artifacts(self) -> None:
        self.assertEqual(self.report["stored_phase9_pass_read_count"], 0)
        self.assertEqual(self.report["current_route_invocation_count"], 0)
        self.assertEqual(self.report["canonical_completion_claim_count"], 0)
        self.assertTrue(self.report["freshness_nonce"])


if __name__ == "__main__":
    unittest.main()
