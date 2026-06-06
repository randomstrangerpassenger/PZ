from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_legacy_active_silent_current_surface_guard import (
    ALLOWLIST_TOO_BROAD_ERROR_CODE,
    CURRENT_SURFACE_ERROR_CODE,
    DEFAULT_RUNTIME_STATE_ERROR_CODE,
    LEGACY_METRIC_RENDERED_ERROR_CODE,
    validate_repo,
)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


class LegacyActiveSilentCurrentSurfaceGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = ROOT / "tests" / "_tmp_legacy_active_silent_guard"
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    def manifest(self) -> dict:
        return {
            "round_root": "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round",
            "hard_fail_surfaces": [
                {
                    "id": "writer",
                    "path_globs": ["Iris/build/description/v2/data/**/*.jsonl"],
                    "occurrence_kinds": ["runtime_state_value", "source_value", "writer_output_label_value"],
                },
                {
                    "id": "operator",
                    "path_globs": ["Iris/build/description/v2/output/**/*.json"],
                    "occurrence_kinds": ["operator_label_value", "current_report_label_value", "writer_output_label_value"],
                },
                {
                    "id": "lua",
                    "path_globs": ["Iris/media/lua/client/Iris/Data/**/*.lua"],
                    "occurrence_kinds": ["source_value"],
                },
            ],
            "allow_surfaces": [
                {
                    "id": "docs",
                    "path_globs": ["docs/Iris/**"],
                    "occurrence_kinds": ["historical_quote", "plain_text", "diagnostic_alias", "legacy_metric_key"],
                    "reason": "historical docs",
                    "must_not_be_current_output": True,
                },
                {
                    "id": "staging",
                    "path_globs": ["Iris/build/description/v2/staging/**"],
                    "occurrence_kinds": ["historical_quote", "plain_text", "diagnostic_alias", "legacy_metric_key"],
                    "reason": "diagnostic staging",
                    "must_not_be_current_output": True,
                },
                {
                    "id": "legacy_metrics",
                    "path_globs": ["Iris/output/**/*.json"],
                    "occurrence_kinds": ["legacy_metric_key", "plain_text"],
                    "reason": "legacy metric keys",
                    "must_not_be_current_output": True,
                },
            ],
        }

    def test_positive_allowed_surfaces_and_non_label_words_pass(self) -> None:
        write_text(
            self.tmp_dir / "docs" / "Iris" / "history.md",
            "Historical active/silent text and a silent failure note stay quoted.\n",
        )
        write_text(
            self.tmp_dir / "Iris" / "output" / "layer3_stats.json",
            json.dumps({"active_count": 2084, "silent_count": 21}, indent=2),
        )
        write_text(
            self.tmp_dir / "Iris" / "build" / "description" / "v2" / "staging" / "round" / "report.json",
            json.dumps({"diagnostic_alias": "active/silent read-only legacy alias"}, indent=2),
        )
        write_text(
            self.tmp_dir / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "View.lua",
            "local activeView = true\n",
        )

        report = validate_repo(self.tmp_dir, self.manifest())

        self.assertEqual(report["status"], "pass")
        self.assertTrue(report["summary"]["gate_a_pass"])

    def test_runtime_state_legacy_value_is_owned_by_existing_guard_only(self) -> None:
        write_text(
            self.tmp_dir / "Iris" / "build" / "description" / "v2" / "data" / "decisions.jsonl",
            '{"item_id":"Base.Legacy","state":"active"}\n',
        )

        report = validate_repo(self.tmp_dir, self.manifest())
        codes = [error["code"] for error in report["errors"]]

        self.assertIn(DEFAULT_RUNTIME_STATE_ERROR_CODE, codes)
        self.assertNotIn(CURRENT_SURFACE_ERROR_CODE, codes)

    def test_lua_source_silent_current_surface_fails_with_new_guard(self) -> None:
        write_text(
            self.tmp_dir / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks" / "Chunk001.lua",
            'return { ["source"] = "silent" }\n',
        )

        report = validate_repo(self.tmp_dir, self.manifest())
        codes = [error["code"] for error in report["errors"]]

        self.assertIn(CURRENT_SURFACE_ERROR_CODE, codes)

    def test_generated_operator_current_label_fails_with_new_guard(self) -> None:
        write_text(
            self.tmp_dir / "Iris" / "build" / "description" / "v2" / "output" / "operator_report.json",
            json.dumps({"current_report_label": "active"}, indent=2),
        )

        report = validate_repo(self.tmp_dir, self.manifest())
        codes = [error["code"] for error in report["errors"]]

        self.assertIn(CURRENT_SURFACE_ERROR_CODE, codes)

    def test_legacy_metric_key_rendered_as_current_label_fails(self) -> None:
        write_text(
            self.tmp_dir / "Iris" / "output" / "layer3_stats.json",
            json.dumps({"label": "active_count"}, indent=2),
        )

        report = validate_repo(self.tmp_dir, self.manifest())
        codes = [error["code"] for error in report["errors"]]

        self.assertIn(LEGACY_METRIC_RENDERED_ERROR_CODE, codes)

    def test_too_broad_allowlist_rule_fails(self) -> None:
        manifest = self.manifest()
        manifest["allow_surfaces"].append(
            {
                "id": "bad",
                "path_globs": ["Iris/**"],
                "occurrence_kinds": ["plain_text"],
                "reason": "too broad",
                "must_not_be_current_output": True,
            }
        )

        report = validate_repo(self.tmp_dir, manifest)
        codes = [error["code"] for error in report["errors"]]

        self.assertIn(ALLOWLIST_TOO_BROAD_ERROR_CODE, codes)


if __name__ == "__main__":
    unittest.main()
